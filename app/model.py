from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import smtplib, ssl

@login_manager.user_loader
def get_user(user_id):
    return User.query.filter_by(id=user_id).first()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    Token_reset = db.Column(db.String(256), nullable=True)


    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.Token_reset = None

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.name

    def SendMail(token, destinario):
        message = 'Subject: {}\n\n"TOKEN :"{}'.format("Utilize o token para reset da senha ",token)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
            server.login("colecionadorrrr@gmail.com", 'lnkmvovyvehewufa')
            server.sendmail(from_addr='colecionadorrrr@gmail.com', to_addrs=destinario, msg=message)
            server.quit()

class Item(db.Model, UserMixin):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    hash = db.Column(db.String(200), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('item_types.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, name, description, type, hash):
        self.name = name
        self.description = description
        self.type_id = type
        self.hash = hash

    def getitens(self):
        return self.name, self.description, self.type, self.hash

class Item_type(db.Model, UserMixin):
    __tablename__ = 'item_types'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Item_type %r>' % self.name

class Colection(db.Model, UserMixin):
    __tablename__ = 'colections'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, )
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description

class item_in_collection(db.Model, UserMixin):
    __tablename__ = 'item_in_collection'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('colections.id'), nullable=False)

    def __init__(self, item_id, collection_id):
        self.item_id = item_id
        self.collection_id = collection_id

class User_Collection(db.Model, UserMixin):
    __tablename__ = 'user_collection'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('colections.id', ondelete='CASCADE'), nullable=False)


    def __init__(self, user_id, collection_id):
        self.user_id = user_id
        self.collection_id = collection_id