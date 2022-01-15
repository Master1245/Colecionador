from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
import os 

load_dotenv(find_dotenv())
BD_NUVEM = os.environ.get('BD_NUVEM')

app = Flask(__name__, template_folder='../static/templates' , static_folder='../static')

app.config['SQLALCHEMY_DATABASE_URI'] = BD_NUVEM
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)

login_manager = LoginManager(app)
db = SQLAlchemy(app)