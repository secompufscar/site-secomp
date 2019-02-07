from flask import render_template, request, redirect, url_for, session
from flask_login import login_required, login_user, logout_user, current_user
from app import app
from app.controllers.forms import LoginForm, CadastroForm
from app.controllers.functions import enviarEmailConfirmacao
from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import datetime
import os
from app.models.models import *
from bcrypt import gensalt


@app.route('/')
def index():
	return render_template('index.html', title='Página inicial')


@app.route("/login", methods=["GET", "POST"])
def login():
	form = LoginForm(request.form)
	if form.validate_on_submit():
		user = db.session.query(Usuario).filter_by(email = form.email.data).first()
		if user:
			if pbkdf2_sha256.verify(form.senha.data, user.senha):
				user.autenticado = True
				db.session.add(user)
				db.session.commit()
				login_user(user, remember=True)
				return redirect(url_for('index_usuario'))
	return render_template('login.html', form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
	user = current_user
	user.autenticado = False
	db.session.add(user)
	db.session.commit()
	logout_user()
	return redirect(url_for('index'))


@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

	form = CadastroForm(request.form)
	email = form.email.data
	salt = gensalt().decode('utf-8')
	token = serializer.dumps(email, salt=salt)

	if form.validate_on_submit():
		usuario = db.session.query(Usuario).filter_by(email=email).first()
		if usuario != None:
			return "Este email já está sendo usado!"
		else:
			agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			hash = pbkdf2_sha256.encrypt(form.senha.data, rounds=10000, salt_size=15)
			usuario = Usuario(email=email, senha=hash, ultimo_login=agora,
							  data_cadastro=agora, permissao=0, primeiro_nome=form.primeiro_nome.data,
							  ult_nome=form.sobrenome.data, curso=form.curso.data, instituicao=form.instituicao.data,
							  cidade=form.cidade.data, data_nasc=form.data_nasc.data,
							  token_email=token, autenticado=True, salt=salt)
			#TODO Quando pronto o modelo de evento implementar função get_id_edicao()
			db.session.add(usuario)
			db.session.flush()
			participante = Participante(id=usuario.id, edicao=1, pacote=False, pagamento=False,
			camiseta=' ', data_inscricao=agora, credenciado=False)
			enviarEmailConfirmacao(app, email, token)
			db.session.add(participante)
			db.session.commit()
			login_user(usuario, remember=True)
			return redirect(url_for('index_usuario'))
	return render_template('cadastro.html', form=form)


@app.login_manager.user_loader
def user_loader(user_id):
		return Usuario.query.get(user_id)


#Página do link enviado para o usuário
@app.route('/verificacao/<token>')
def verificacao(token):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	try:
		#Acha o usuário que possui o token
		user = db.session.query(Usuario).filter_by(token_email = token).first()
		salt = user.salt

		#Gera um email a partir do token do link e do salt do db
		email = serializer.loads(token, salt=salt, max_age=3600)

		#Valida o email
		user.email_verificado = True
		db.session.add(user)
		db.session.commit()
	#Tempo definido no max_age
	except SignatureExpired:
		return render_template('cadastro.html', resultado='O link de ativação expirou.')
	except Exception as e:
		return render_template('cadastro.html', resultado='Falha na ativação.')
	return render_template('cadastro.html', resultado='Email confirmado.')
