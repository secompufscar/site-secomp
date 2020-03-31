from os import path, getenv

from flask import Flask, redirect, request, render_template, session, flash
from flask_babelex import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_qrcode import QRcode as QRCode


def create_app(config=None):
    """
    Project app factory
    """

    configs = {"development": ".development", "production": ".production", "default": ".default"}

    if config not in configs:
        config = getenv("FLASK_ENVIRONMENT", "development")

    config = "app.config" + configs[config]

    app = Flask(__name__)
    app.config.from_object(config)

    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(dsn=app.config["SENTRY_DSN"], integrations=[FlaskIntegration()])

    Bootstrap(app)
    QRCode(app)

    from app.models.models import db, Usuario
    from app.models.commands import populate

    app.app_context().push()
    db.init_app(app)

    from app.controllers.forms.forms import LoginForm

    @app.errorhandler(400)
    def bad_request(error):
        form_login = LoginForm(request.form)
        return render_template("400.html", form_login=form_login), 400

    @app.errorhandler(404)
    def page_not_found(error):
        form_login = LoginForm(request.form)
        return render_template("404.html", form_login=form_login), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        form_login = LoginForm(request.form)
        return render_template("500.html", form_login=form_login), 500

    migrate = Migrate(app, db)

    @app.cli.command()
    def create():
        """
        Creates database tables from sqlalchemy models
        """
        db.create_all()
        populate()
        db.session.commit()

    @app.cli.command()
    def drop():
        """
        Drops database tables
        """
        prompt = input("Erase current database? [y/n]")
        if prompt == "y":
            db.session.close_all()
            db.drop_all()
            db.session.commit()

    from app.controllers.functions.email import mail

    mail.init_app(app)

    from app.controllers.routes import admin, gerenciar, participantes, views, conteudo, api

    app.register_blueprint(gerenciar.gerenciar)
    app.register_blueprint(participantes.participantes)
    app.register_blueprint(views.views)
    app.register_blueprint(conteudo.conteudo)
    app.register_blueprint(api.api)

    upload_path = path.join(path.dirname(__file__), "static")
    adm = admin.init_app(app, upload_path)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(user_id):
        return db.session.query(Usuario).filter_by(id=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect("/login")

    @login_manager.needs_refresh_handler
    def refresh_callback():
        flash(u"Para proteção da sua conta, faça login novamente para poder acessar esta página.")
        return redirect("/confirm-login")

    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        if request.args.get("lang"):
            session["lang"] = request.args.get("lang")
        return "pt"

    return app
