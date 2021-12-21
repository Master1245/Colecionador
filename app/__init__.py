from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:99706855@localhost/flask_login'
app.config['SECRET_KEY'] = 'secret'


login_manager = LoginManager()
db = SQLAlchemy(app)