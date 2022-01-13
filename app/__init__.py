from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta

app = Flask(__name__, template_folder='./templates')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:99706855@localhost/flask_login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://idexawu7uo5e90zg:iqpikux52el4bwu2@uyu7j8yohcwo35j3.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/uo2l4tehiflllwwl'
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)

login_manager = LoginManager(app)
db = SQLAlchemy(app)