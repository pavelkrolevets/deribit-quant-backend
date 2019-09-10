from flask import request, render_template, jsonify, url_for, redirect, g, send_from_directory, flash
from .models import User, Chain
from index import app, db
from sqlalchemy.exc import IntegrityError
from .utils.auth import generate_token, requires_auth, verify_token
from werkzeug.utils import secure_filename
import os
from finance.finance import *
import json

# @app.route('/', methods=['GET'])
# def index():
#     return render_template('index.html')
#
#
# @app.route('/<path:path>', methods=['GET'])
# def any_root_path(path):
#     return render_template('index.html')

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

@app.route('/api/add_chain', methods=['POST'])
def add_chain():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        chain = Chain(
            chain_id=incoming["chain_id"],
        )
        user = User.query.filter_by(email=incoming["email"]).first_or_404()
        user.chains.append(chain)
        db.session.add(chain)
        db.session.commit()
        return jsonify(chain_added=True)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/get_chain_by_user', methods=['POST'])
def get_chain_by_user():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        # query all chains for a given user email
        result = Chain.query.filter(Chain.users_backref.any(email=incoming["email"])).all()
        chains = []
        for i in result:
            chains.append(i.chain_id)
            print(i.chain_id)
        return jsonify(chains=chains)
    else:
        return jsonify(token_is_valid=False), 403

@app.route('/api/get_user_by_chain', methods=['POST'])
def get_user_by_chain():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        # query all chains for a given user email
        result = User.query.filter(User.chains_backref.any(chain_id=incoming["chain_id"])).all()
        users = []
        for i in result:
            users.append(i.email)
            print(i.email)
        return jsonify(users=users)
    else:
        return jsonify(token_is_valid=False), 403

# @app.route('/api/upload_image', methods=['POST'])
# def upload_image():
#     incoming = request.get_json()
#     print(incoming)
#
#     # check if the post request has the file part
#     if 'file' not in request.files:
#         print('No file part')
#         return jsonify(file_upload=False), 403
#     file = request.files['file']
#     # if user does not select file, browser also
#     # submit an empty part without filename
#     if file.filename == '':
#         print('No selected file')
#         return jsonify(file_upload=False), 403
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         user = User.query.filter_by(email=request.files['email']).first_or_404()
#         image = Image(
#             url=filename,
#         )
#         user.images.append(image)
#         db.session.add(image)
#         db.session.commit()
#         return jsonify(file_upload=True)
#
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/compute_bsm', methods=['POST'])
def compute_bsm():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        option_values=[]
        data = incoming['data']
        if incoming['option_type']=='call':
            for item in data:
                item = json.loads(item)
                call = call_option(S0=item['S0'], K=item['K'], T=item['T'], r=item['r'], sigma=item['sigma'])
                option_values.append(call.value())
        if incoming['option_type']=='put':
            for item in data:
                put = put_option(S0=item.S0, K=item.K, T=item.T, r=item.r, sigma=item.sigma)
                option_values.append(put.value())

        return jsonify(option_values=option_values)
    else:
        return jsonify(token_is_valid=False), 403
