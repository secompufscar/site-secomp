from os import getenv, path

from flask import Flask, redirect, request, session
from flask_babelex import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Server, Manager, prompt_bool

from app.controllers.routes import admin, management, users, views
from app.models.models import db, Usuario

configs = {
    'development': '../config/development.py',
    'production': '../config/production.py',
    'default': '../config/default.py'
}

config_name = getenv('FLASK_CONFIGURATION', 'development')

app = Flask(__name__)
app.config.from_pyfile(configs[config_name])

Bootstrap(app)
migrate = Migrate(app, db)
upload_path = path.join(path.dirname(__file__), 'static')
adm = admin.init_admin(app, upload_path)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    return db.session.query(Usuario).filter_by(id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(host='0.0.0.0'))


@manager.command
def create():
    """
    Creates database tables from sqlalchemy models
    """
    db.create_all()


@manager.command
def drop():
    """
    Drops database tables
    """
    if prompt_bool("Erase current database?"):
        db.drop_all()


babel = Babel(app)


@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return "pt"
