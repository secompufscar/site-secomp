from flask import render_template, request, redirect, url_for, session
from app.models.usuario import Usuario
from app.controllers.forms import LoginForm
from app.controllers.functions import check_password
from flask_login import login_required, login_user, logout_user, current_user
from app import app


@app.route('/')
def index():
    return render_template('index.html', title='Página inicial')


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = Usuario.query.get(form.email.data)
        if user:
            if check_password(user.password, form.password.data):
                user.authenticated = True
                session.add(user)
                session.commit()
                login_user(user, remember=True)
                return redirect(url_for('index_usuario'))
    return render_template('login.html', form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.autenticado = False
    session.add(user)
    session.commit()
    logout_user()
    return redirect(url_for('index'))
