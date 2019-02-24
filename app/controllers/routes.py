
from bcrypt import gensalt
from flask import render_template, request, redirect
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from passlib.hash import pbkdf2_sha256

from app.controllers.forms import LoginForm, CadastroForm
from app.controllers.functions import *
from app.controllers.functions import enviarEmailConfirmacao
from app.models.models import *


@app.route('/')
def index():
    """
    Renderiza a página inicial do projeto
    """
    return render_template('index.html', title='Página inicial',
                           secomp_now=secomp_now[0], secomp=secomp[0],
                           secomp_email=secomp_email,
                           secompEdition=secomp_edition)

@app.route('/dev')
def dev():
    return render_template('index.dev.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Renderiza a página de login do projeto
    """
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = db.session.query(Usuario).filter_by(
            email=form.email.data).first()
        if user:
            if pbkdf2_sha256.verify(form.senha.data, user.senha):
                user.autenticado = True
                user.ultimo_login = datetime.now()
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return "olá, {}".format(user.primeiro_nome)
                # return redirect(url_for('index_usuario'))
    return render_template('login.html', form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """
    Renderiza a página de logout do projeto
    """
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
    token = serializer.dumps(email, salt='confirmacao_email')
    salt = gensalt().decode('utf-8')

    if form.validate_on_submit():
        usuario = db.session.query(Usuario).filter_by(email=email).first()
        if usuario != None:
            return "Este email já está sendo usado!"
        else:
            agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hash = pbkdf2_sha256.encrypt(form.senha.data, rounds=10000, salt_size=15)
            usuario = Usuario(email=email, senha=hash, ultimo_login=agora,
                              data_cadastro=agora, permissao=0, primeiro_nome=form.primeiro_nome.data,
                              sobrenome=form.sobrenome.data, curso=form.curso.data, instituicao=form.instituicao.data,
                              id_cidade=form.cidade.data, data_nascimento=form.data_nasc.data,
                              token_email=token, autenticado=True, salt=salt)
            # TODO Quando pronto o modelo de evento implementar função get_id_edicao()
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
	id_evento = db.session.query(Evento).filter_by(edicao=EDICAO_ATUAL).first().id
	if email_confirmado() == True:
		participante = db.session.query(Participante).filter_by(id_usuario=current_user.id, id_evento=id_evento).first()
		if participante is None:
			form = ParticipanteForm(request.form)
			participante = db.session.query(Participante).filter_by(id_usuario=current_user.id, id_evento=id_evento).first()
			if form.validate_on_submit() and participante is None:
				agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				usuario = current_user
				participante = Participante(id_usuario=usuario.id, id_evento=id_evento, pacote=form.kit.data,
				pagamento=False, id_camiseta=form.camiseta.data, data_inscricao=agora, credenciado=False,
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
		return render_template('dashboard_usuario.html', eventos=get_dicionario_eventos_participante(request.base_url),
		info_usuario=get_dicionario_usuario(current_user))
	else:
		return redirect(url_for('verificar_email'))

@app.route('/dashboard-usuario/evento/<edicao>')
@login_required
def info_participante_evento(edicao):
	return render_template('info_participante.html', info_evento=get_dicionario_info_evento(edicao))


# Página do link enviado para o usuário
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


@app.route('/inscricao-atividades')
@login_required
def inscricao_atividades():
    minicursos = db.session.query(Atividade).filter_by(tipo=0)
    palestras = db.session.query(Atividade).filter_by(tipo=1)
    return render_template('inscricao_atividades.html',
                           participante=db.session.query(Participante).filter_by(usuario=current_user).first(),
                           usuario=current_user, minicursos=minicursos, palestras=palestras)


@app.route('/inscrever-atividade/<id>')
@login_required
def inscrever(id):
    atv = db.session.query(Atividade).filter_by(id=id).first()
    if atv.vagas_disponiveis > 0:
        atv.inscritos.append(db.session.query(Participante).filter_by(usuario=current_user).first())
        atv.vagas_disponiveis = atv.vagas_disponiveis - 1
        db.session.flush()
        db.session.commit()
        return redirect(url_for('inscricao_atividades'))
    else:
        return "Não há vagas disponíveis!"


@app.route('/desinscrever-atividade/<id>')
@login_required
def desinscrever(id):
    atv = db.session.query(Atividade).filter_by(id=id).first()
    if db.session.query(Participante).filter_by(usuario=current_user).first() in atv.inscritos:
        atv.inscritos.remove(db.session.query(Participante).filter_by(usuario=current_user).first())
        atv.vagas_disponiveis = atv.vagas_disponiveis + 1
        db.session.flush()
        db.session.commit()
        return redirect(url_for('inscricao_atividades'))
    else:
        return "Não está inscrito nessa atividade!"
