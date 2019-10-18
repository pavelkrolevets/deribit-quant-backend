from flask import request, jsonify, g
from .models import User, Task
from index import app, db
from sqlalchemy.exc import IntegrityError
from .utils.auth import generate_token, requires_auth, verify_token
from finance.option_bsm import *
import json
from delta_hedger.tasks import start_delta_hedge
from celery.result import AsyncResult
from delta_hedger.celery_app import celery_app
from finance.pnl import *
from finance.vola import *

celery_app.conf.broker_url = 'redis://localhost:6379/0'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@app.route("/api/user", methods=["GET"])
@requires_auth
def get_user():
    return jsonify(result=g.current_user)


@app.route("/api/create_user", methods=["POST"])
def create_user():
    incoming = request.get_json()
    user = User(
        email=incoming["email"],
        password=incoming["password"]
    )
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(message="User with that email already exists"), 409

    new_user = User.query.filter_by(email=incoming["email"]).first()

    return jsonify(
        id=user.id,
        token=generate_token(new_user)
    )


@app.route("/api/get_token", methods=["POST"])
def get_token():
    incoming = request.get_json()
    user = User.get_user_with_email_and_password(incoming["email"], incoming["password"])
    if user:
        return jsonify(token=generate_token(user))

    return jsonify(error=True), 403


@app.route("/api/is_token_valid", methods=["POST"])
def is_token_valid():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        return jsonify(token_is_valid=True)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/search', methods=['POST'])
def search():
    incoming = request.get_json()
    user = User.query.filter_by(email=incoming["email"]).first_or_404()
    return jsonify(
        id=user.id,
        account=user.eth_account
    )

@app.route('/api/update_ethaccount', methods=['POST'])
def update_eth_account():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        user.eth_account = incoming["eth_account"]
        db.session.commit()
        return jsonify(eth_account_updated=True)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/search_user', methods=['POST'])
def search_user():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        return jsonify(
            eth_account=user.eth_account,
            status=200
        )
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/compute_bsm', methods=['POST'])
def compute_bsm():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        option_values=[]
        data = incoming['data']
        if incoming['option_type']=='call' and incoming['direction']=='buy':
            for item in data:
                item = json.loads(item)
                call = call_option(S0=item['S0'], K=item['K'], T=item['T'], r=item['r'], sigma=item['sigma'])
                option_values.append(call.value()-incoming['trade_price'])
        if incoming['option_type'] == 'call' and incoming['direction'] == 'sell':
            for item in data:
                item = json.loads(item)
                call = call_option(S0=item['S0'], K=item['K'], T=item['T'], r=item['r'], sigma=item['sigma'])
                option_values.append(-call.value()+incoming['trade_price'])
        if incoming['option_type']=='put' and incoming['direction']=='buy':
            for item in data:
                put = put_option(S0=item.S0, K=item.K, T=item.T, r=item.r, sigma=item.sigma)
                option_values.append(put.value()-incoming['trade_price'])

        if incoming['option_type']=='put' and incoming['direction']=='sell':
            for item in data:
                put = put_option(S0=item.S0, K=item.K, T=item.T, r=item.r, sigma=item.sigma)
                option_values.append(-put.value()+incoming['trade_price'])

        return jsonify(option_values=option_values)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/start_delta_hedger', methods=['POST'])
def start_delta_hedger():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        delta_hedge_task = start_delta_hedge.delay(float(incoming["interval_min"]),
                                                   float(incoming["interval_max"]),
                                                   float(incoming["time_period"]),
                                                   incoming["instrument"],
                                                   user.api_pubkey,
                                                   user.api_privkey)
        task = Task(
            pid=delta_hedge_task.task_id,
            timeinterval=float(incoming["time_period"]),
            delta_min = float(incoming["interval_min"]),
            delta_max = float(incoming["interval_max"]),
            instrument = incoming["instrument"]
        )
        user.tasks.append(task)
        db.session.add(task)
        db.session.commit()
        return jsonify(deltahedger_started=True)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/get_tasks', methods=['POST'])
def get_tasks():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        tasks = user.tasks
        id=[]
        pid=[]
        timestamp=[]
        timeinterval=[]
        delta_min=[]
        delta_max=[]
        instrument=[]
        for item in tasks:
            id.append(item.id),
            pid.append(item.pid),
            timestamp.append(item.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            timeinterval.append(item.timeinterval)
            delta_min.append(item.delta_min)
            delta_max.append(item.delta_max)
            instrument.append(item.instrument)
        result = [{"id": i, "pid": p, "timestamp": t, "timeinterval": ti, "delta_min":dmin, "delta_max":dmax, "instrument": instr} for i, p, t, ti, dmin, dmax, instr in zip(id, pid, timestamp, timeinterval, delta_min, delta_max, instrument)]
        return json.dumps(result)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/kill_task', methods=['POST'])
def kill_task():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        pid = incoming["pid"]
        res = AsyncResult(pid, app=celery_app)
        print(res.state)

        try:
            celery_app.control.revoke(pid, terminate=True, signal='SIGKILL')
        except Exception:
            return jsonify(task_stopped=False)

        res = celery_app.AsyncResult(pid)
        print(res.state)

        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        task = Task.query.filter_by(pid=pid).first_or_404()
        user.tasks.remove(task)
        db.session.commit()

        return jsonify(task_stopped=True)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/get_task_state', methods=['POST'])
def get_task_state():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        pid = incoming["pid"]
        res = celery_app.AsyncResult(pid)
        print(res.state)

        return jsonify(task_state=res.state)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/update_api_keys', methods=['POST'])
def update_api_keys():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        user.api_pubkey = incoming["api_pubkey"]
        user.api_privkey = incoming["api_privkey"]
        db.session.commit()
        return jsonify(api_keys_updated=True)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/get_api_keys', methods=['POST'])
def get_api_keys():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        return jsonify(
            api_pubkey=user.api_pubkey,
            api_privkey=user.api_privkey
        )
    else:
        return jsonify(token_is_valid=False), 403


@app.route('/api/compute_pnl', methods=['POST'])
def compute_pnl():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        pnl, pnl_at_exp = compute_global_pnl(user.api_pubkey, user.api_privkey,
                                             int(incoming["range_min"]),
                                             int(incoming["range_max"]),
                                             int(incoming["step"]),
                                             float(incoming["risk_free"]),
                                             float(incoming["vola"]))
        return jsonify(pnl=pnl,
                       pnl_at_exp=pnl_at_exp)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/get_hist_vola', methods=['POST'])
def get_hist_vola():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        hist_vola = getHistVola(int(incoming["window"]), incoming["timeframe"], incoming["instrument"])
        return jsonify(hist_vola=hist_vola)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/analaize_positions', methods=['POST'])
def analaize_positions():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        pnl, pnl_at_exp = analize_positions(user.api_pubkey, user.api_privkey,
                                            incoming["positions"],
                                             int(incoming["range_min"]),
                                             int(incoming["range_max"]),
                                             int(incoming["step"]),
                                             float(incoming["risk_free"]),
                                             float(incoming["vola"]))
        return jsonify(pnl=pnl,
                       pnl_at_exp=pnl_at_exp)
    else:
        return jsonify(token_is_valid=False), 403
