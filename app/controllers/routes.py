from flask import render_template, request, redirect, url_for, session
from flask_login import login_required, login_user, logout_user, current_user
from app import app
from app.controllers.forms import LoginForm, CadastroForm, ParticipanteForm
from app.controllers.functions import enviarEmailConfirmacao, email_confirmado, get_dicionario_usuario, get_dicionario_info_evento
from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import datetime
import os
from app.controllers.constants import dicionario_eventos, EDICAO_ATUAL
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
				return redirect(url_for('dashboard_usuario'))
	return render_template('login.html', form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
	user = current_user
	user.autenticado = False
	db.session.add(user)
	db.session.commit()
	logout_user()
	return redirect(url_for('login'))


@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

	form = CadastroForm(request.form)
	email = form.email.data
	salt = gensalt().decode('utf-8')
	token = serializer.dumps(email, salt=salt)

	if form.validate_on_submit():
		usuario = db.session.query(Usuario).filter_by(email=email).first()
		if usuario is not None:
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
			db.session.commit()
			enviarEmailConfirmacao(app, email, token)
			login_user(usuario, remember=True)
			return redirect(url_for('verificar_email'))
	return render_template('cadastro.html', form=form)

@app.route('/verificar-email')
@login_required
def verificar_email():
	if email_confirmado() == 	True:
		msg = 'Seu email foi verificado com sucesso!'
		status = True
	else:
		msg = 'Confirme o email de verificação que foi enviado ao endereço de email fornecido'
		status = False
	return render_template('confirma_email.html', resultado=msg, status=status)

@app.route('/cadastro-participante', methods=['POST', 'GET'])
@login_required
def cadastro_participante():
	if email_confirmado() == True:
		participante = db.session.query(Participante).filter_by(id_usuario=current_user.id, id_evento=id).first()
		if participante is None:
			form = ParticipanteForm(request.form)
			if form.validate_on_submit():
				agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				usuario = current_user
				participante = Participante(id_usuario=usuario.id, id_evento=1, pacote=form.kit.data,
				pagamento=False, camiseta=form.camiseta.data, data_inscricao=agora, credenciado=False,
				opcao_coffee=form.restricao_coffee.data)
				db.session.add(participante)
				db.session.flush()
				db.session.commit()
				return redirect(url_for('dashboard_usuario'))
			else:
				return render_template('cadastro_participante.html', form=form)
		else:
			return redirect(url_for('dashboard_usuario'))
	else:
		return redirect(url_for('verificar_email'))

@app.route('/dashboard-usuario')
@login_required
def dashboard_usuario():
	if email_confirmado() == True:
		participante = db.session.query(Participante).filter_by(id_usuario=current_user.id, id_evento=1).first()
		if participante is not None:
			inscricao=False
		else:
			inscricao=True
		return render_template('dashboard_usuario.html', eventos=dicionario_eventos, inscricao=inscricao,
		edicao_atual=EDICAO_ATUAL, info_usuario=get_dicionario_usuario(current_user))
	else:
		return redirect(url_for('verificar_email'))

@app.route('/dashboard-usuario/evento/<edicao>')
@login_required
def info_participante_evento(edicao):
	return render_template('info_participante.html', info_evento=get_dicionario_info_evento(edicao))
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
	return redirect(url_for('verificar_email'))
