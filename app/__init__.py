from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
import os 

load_dotenv(find_dotenv())
BD_NUVEM = os.environ.get('BD_NUVEM')

app = Flask(__name__, template_folder='../static/src' , static_folder='../static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1:3306/colecionador'
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=60)

login_manager = LoginManager(app)
db = SQLAlchemy(app)