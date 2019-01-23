from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
import os

config = {
    "development": 'config.default',
    'production': 'config.production',
    'default': 'config.default'
}

config_name = os.getenv('FLASK_CONFIGURATION', 'default')

app = Flask(__name__)
app.config.from_object(config[config_name])
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.controllers import routes

manager = Manager(app)
manager.add_command('db', MigrateCommand)
