from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def get_user(user_id):
    return User.query.filter_by(id=user_id).first()

class User(db.Model, UserMixin):
    __tablename = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=True)
    password = db.Column(db.String(64), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.name

class Item(db.Model, UserMixin):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    hash = db.Column(db.String(200), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('item_types.id'))
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, name, description, user_id, type, hash):
        self.__name = name
        self.__description = description
        self.__user_id = user_id
        self.__type = type
        self.__hash = hash

    def __repr__(self):
        return '<Item %r>' % self.__name

class Item_type(db.Model, UserMixin):
    __tablename__ = 'item_types'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)

    def __init__(self, name):
        self.__name = name

    def __repr__(self):
        return '<Item_type %r>' % self.__name

class Colection(db.Model, UserMixin):
    __tablename__ = 'colections'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, name, description):
        self.__name = name
        self.__description = description

    def __repr__(self):
        return '<Colection %r>' % self.__name

class item_in_collection(db.Model, UserMixin):
    __tablename__ = 'item_in_collection'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    collection_id = db.Column(db.Integer, db.ForeignKey('colections.id'))

    def __init__(self, item_id, collection_id):
        self.__item_id = item_id
        self.__collection_id = collection_id

    def __repr__(self):
        return '<item_in_collection %r>' % self.__collection_id, " <item_id %r>", self.__item_id

class User_Collection(db.Model, UserMixin):
    __tablename__ = 'user_collection'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    collection_id = db.Column(db.Integer, db.ForeignKey('colections.id'))

    def __init__(self, user_id, collection_id):
        self.__user_id = user_id
        self.__collection_id = collection_id

    def __repr__(self):
        return '<user_collection %r>' % self.__collection_id, " <user_id %r>", self.__user_id