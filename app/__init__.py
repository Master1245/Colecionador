from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
import os 

load_dotenv(find_dotenv())
DB_NUVEM = os.environ.get('DB_NUVEM')
DB_LOCAL = os.environ.get('DB_LOCAL')

app = Flask(__name__, template_folder='./templates')
# app.config['SQLALCHEMY_DATABASE_URI'] = DB_LOCAL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['JAWSDB_MARIA_URL']
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)

login_manager = LoginManager(app)
db = SQLAlchemy(app)