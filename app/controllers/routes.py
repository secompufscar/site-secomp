import datetime

from bcrypt import gensalt
from flask import render_template, request, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from passlib.hash import pbkdf2_sha256

from app.controllers.constants import secomp_now, secomp, secomp_email, secomp_edition
from app.controllers.forms import LoginForm, CadastroForm
from app.controllers.functions import enviarEmailConfirmacao
from app.models.models import *


@app.route('/')
def index():
    """
    Renderiza a página inicial do projeto
    """
    return render_template('index.html', title='Página inicial', 
            secomp_now=secomp_now, secomp=secomp, 
            secomp_email=secomp_email, 
            secompEdition = secomp_edition)

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
                              cidade=form.cidade.data, data_nascimento=form.data_nasc.data,
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


# Página do link enviado para o usuário
@app.route('/verificacao/<token>')
def verificacao(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        # Gera um email a partir do token do link
        email = serializer.loads(token, salt='confirmacao_email', max_age=3600)
        # Acha o usuário que possui o email
        user = db.session.query(Usuario).filter_by(email=email).first()
        # Valida o email
        user.email_verificado = True
        db.session.add(user)
        db.session.commit()
    # Tempo definido no max_age
    except SignatureExpired:
        return 'O link de ativação expirou.'
        # return render_template('cadastro.html', resultado='O link de ativação expirou.')
    except Exception as e:
        return 'Falha na ativação.'
        # return render_template('cadastro.html', resultado='Falha na ativação.')
    return 'Email confirmado.'
    # return render_template('cadastro.html', resultado='Email confirmado.')


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
        minicursos = db.session.query(Atividade).filter_by(tipo=0)
        palestras = db.session.query(Atividade).filter_by(tipo=1)
        return render_template('inscricao_atividades.html',
                               participante=db.session.query(Participante).filter_by(usuario=current_user).first(),
                               usuario=current_user, minicursos=minicursos, palestras=palestras, acao="+")
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
        minicursos = db.session.query(Atividade).filter_by(tipo=0)
        palestras = db.session.query(Atividade).filter_by(tipo=1)
        return render_template('inscricao_atividades.html',
                               participante=db.session.query(Participante).filter_by(usuario=current_user).first(),
                               usuario=current_user, minicursos=minicursos, palestras=palestras, acao="-")
    else:
        return "Não está inscrito nessa atividade!"
