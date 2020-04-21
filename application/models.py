from index import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    eth_account = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True)
    api_pubkey = db.Column(db.String(255), unique=True)
    api_privkey = db.Column(db.String(255), unique=True)
    tasks = db.relationship("Task", back_populates='user', cascade="all, delete-orphan")

    def __init__(self, email, password):
        self.email = email
        self.active = True
        self.password = User.hashed_password(password)

    @staticmethod
    def hashed_password(password):
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @staticmethod
    def get_user_with_email_and_password(email, password):
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return None

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    timeinterval = db.Column(db.Integer)
    delta_min = db.Column(db.Float)
    delta_max = db.Column(db.Float)
    instrument = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="tasks")

class BtcFutures(db.Model):
    __tablename__ = 'futures_contango_btc'
    id = db.Column(db.Integer, primary_key=True)
    perpetual = db.Column(db.Float)
    three_months = db.Column(db.Float)
    six_months = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id'         : self.id,
            'perpetual'  : self.perpetual,
            'three_months'  : self.three_months,
            'six_months'  : self.six_months,
            'timestamp': self.timestamp,
        }

class EthFutures(db.Model):
    __tablename__ = 'futures_contango_eth'
    id = db.Column(db.Integer, primary_key=True)
    perpetual = db.Column(db.Float)
    three_months = db.Column(db.Float)
    six_months = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id'         : self.id,
            'perpetual'  : self.perpetual,
            'three_months'  : self.three_months,
            'six_months'  : self.six_months,
            'timestamp': self.timestamp,
        }

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return  value.timestamp()
    # return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]
