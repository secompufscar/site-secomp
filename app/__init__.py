from flask import Flask
from flask_script import Manager

app = Flask(__name__)

from app.controllers import routes

manager = Manager(app)

