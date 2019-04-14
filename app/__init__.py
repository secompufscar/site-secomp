from os import getenv, path

from flask import Flask, redirect, request, render_template, session
from flask_babelex import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Server, Manager, prompt_bool

configs = {
    'development': '../config/development.py',
    'production': '../config/production.py',
    'default': '../config/default.py'
}

config_name = getenv('FLASK_CONFIGURATION', 'development')

app = Flask(__name__)
app.config.from_pyfile(configs[config_name])

Bootstrap(app)


@app.errorhandler(400)
def bad_request():
    return render_template('400.html'), 400


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error():
    return render_template('500.html'), 500


from app.models.models import db, Usuario

migrate = Migrate(app, db)

from app.controllers.functions.email import mail

mail.init_app(app)

from app.controllers.routes import admin, management, users, views

app.register_blueprint(management.management)
app.register_blueprint(users.users)
app.register_blueprint(views.views)

upload_path = path.join(path.dirname(__file__), 'static')
adm = admin.init_app(app, upload_path)

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
    if prompt_bool("Erase current database?", default=True):
        db.session.close_all()
        db.drop_all()


babel = Babel(app)


@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return "pt"
