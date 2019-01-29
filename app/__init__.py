from flask import Flask
from flask_script import Server, Manager, prompt_bool
#from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager
import os

configs = {
    'development': '../config/development.py',
    'production': '../config/production.py',
    'default': '../config/default.py'
}

config_name = os.getenv('FLASK_CONFIGURATION', 'default')

app = Flask(__name__)
app.config.from_pyfile(configs[config_name])

from app.models.models import *

#db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

from app.controllers import routes

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(host='0.0.0.0', ssl_crt='ssl/server.crt', ssl_key='ssl/server.key'))

@manager.command
def create():
    "Creates database tables from sqlalchemy models"
    db.create_all()

@manager.command
def drop():
    "Drops database tables"
    if prompt_bool("Erase current database?"):
        db.drop_all()
