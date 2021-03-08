from index import db, bcrypt
from datetime import datetime
from cryptography.hazmat.primitives.keywrap import aes_key_wrap_with_padding, aes_key_unwrap_with_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    eth_account = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True)
    api_pubkey = db.Column(db.String(255), unique=True)
    api_privkey = db.Column(db.String(255), unique=True)
    tasks = db.relationship("Task", back_populates='user',
                            cascade="all, delete-orphan")

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

    @staticmethod
    def encrypt_api_key(password, api_key):
        salt = b'sih4yoh9kiedahTeejaeyu1eoShoojaelohneex0duT4poe1'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        api_key_enc = aes_key_wrap_with_padding(key, api_key.encode())
        if api_key_enc:
            return base64.urlsafe_b64encode(api_key_enc).decode("utf-8")
        else:
            return None

    @staticmethod
    def dencrypt_api_key(password, api_key_enc):
        api_key_enc = base64.urlsafe_b64decode(api_key_enc)
        salt = b'sih4yoh9kiedahTeejaeyu1eoShoojaelohneex0duT4poe1'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        api_key = aes_key_unwrap_with_padding(key, api_key_enc)
        if api_key:
            return api_key.decode("utf-8")
        else:
            return None

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    pid = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    timeinterval = db.Column(db.Integer)
    # delta_min = db.Column(db.Float)
    # delta_max = db.Column(db.Float)
    target_delta = db.Column(db.Float)
    instrument = db.Column(db.String(255))
    is_running = db.Column(db.Boolean)
    curency = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
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
            'id': self.id,
            'perpetual': self.perpetual,
            'three_months': self.three_months,
            'six_months': self.six_months,
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
            'id': self.id,
            'perpetual': self.perpetual,
            'three_months': self.three_months,
            'six_months': self.six_months,
            'timestamp': self.timestamp,
        }


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return value.timestamp()
    # return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]
