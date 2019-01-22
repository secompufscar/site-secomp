from flask import Flask
from flask_script import Manager
from dotenv import load_dotenv

load_dotenv() 
app = Flask(__name__)

from app.controllers import routes

manager = Manager(app)

