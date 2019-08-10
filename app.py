from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e4c2b727a399acbc82f502fc15e79902'
app.config['SQLALCHEMY_DATABASE_URI'] = '***REMOVED***'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Citizen
import routes


