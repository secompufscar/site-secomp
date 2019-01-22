from flask import flash, render_template, request, redirect, url_for, session
from app.models.models import *
from app.controllers.forms import LoginForm, CadastroForm
from flask_login import LoginManager, login_manager, login_required, login_user, logout_user, current_user
from app import app
from passlib.hash import pbkdf2_sha256
import datetime
import os

SECRET_KEY = os.getenv('SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager(app)
@app.route('/')
def index():
    return render_template('index.html', title='Página inicial')

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        usuario = db.session.query(Usuario).filter_by(email=form.email.data).first()
        if usuario:
            if pbkdf2_sha256.verify(form.senha.data, usuario.senha):
                usuario.autenticado = True
                db.session.add(usuario)
                db.session.commit()
                login_user(usuario, remember=True)
                return redirect(url_for('index_usuario'))
        else:
            print(user)
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

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    form = CadastroForm(request.form)
    if form.validate_on_submit():
        usuario = db.session.query(Usuario).filter_by(email=form.email.data).first()
        if usuario != None:
            return "Este email já está sendo usado!"
        else:
            agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hash = pbkdf2_sha256.encrypt(form.senha.data, rounds=8000, salt_size=15)
            usuario = Usuario(email=form.email.data, senha=hash, ultimo_login=agora,
            data_cadastro=agora, permissao=0, primeiro_nome=form.primeiro_nome.data,
            ult_nome=form.sobrenome.data, curso=form.curso.data, instituicao=form.instituicao.data,
            cidade=form.cidade.data, data_nasc=form.data_nasc.data,
            token_email="asdfghjhtrgdfsda", autenticado=True)
            db.session.add(usuario)
            db.session.commit()
            login_user(usuario, remember=True)
            return redirect(url_for('index_usuario'))
    return render_template('cadastro.html', form=form)

@login_manager.user_loader
def user_loader(user_id):
        return Usuario.query.get(user_id)
