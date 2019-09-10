from index import db, bcrypt
from flask import send_from_directory
from datetime import datetime

chain_association = db.Table('chain_association', db.Model.metadata,
    db.Column('chain_id', db.Integer, db.ForeignKey('chain.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    eth_account = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True)
    chains = db.relationship("Chain", secondary=chain_association, backref=db.backref('users_backref'))
    images = db.relationship("Image", backref='user_images')

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

class Chain(db.Model):
    __tablename__ = 'chain'
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship("User", secondary=chain_association, backref=db.backref('chains_backref'))
    chain_id = db.Column(db.String(255))

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

