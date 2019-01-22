from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config.from_object('config.default')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.controllers import routes

manager = Manager(app)
manager.add_command('db', MigrateCommand)
