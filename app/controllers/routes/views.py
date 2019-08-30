import os

from datetime import datetime
from passlib.hash import pbkdf2_sha256
from werkzeug import secure_filename

from flask import render_template, request, Blueprint, url_for, redirect, current_app, send_from_directory, abort, flash
from flask_login import login_required, login_user, logout_user, current_user, confirm_login
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr

from app.controllers.forms.forms import *
from app.controllers.forms.options import opcoes_falha
from app.controllers.functions.email import enviar_email_dm, enviar_email_generico
from app.controllers.functions.helpers import *
from app.controllers.constants import *
from app.controllers.functions.dictionaries import *

limiter = Limiter(current_app, key_func=get_ipaddr)
views = Blueprint('views', __name__, static_folder='static', template_folder='templates')


@views.route('/', methods=["GET", "POST"])
def index():
    """
    Renderiza a página inicial do projeto
    """

    form_login = LoginForm(request.form)
    return render_template('views/index.html', title='Página inicial',
                           secomp_now=secomp_now[0], secomp=secomp[0],
                           secomp_email=secomp_email,
                           secompEdition=secomp_edition,
                           form_login=form_login)


@views.route('/contato', methods=['POST', 'GET'])
def contato_dm():
    """
    Página de contato
    """
    form = ContatoForm(request.form)
    form_login = LoginForm(request.form)
    if form.validate_on_submit():
        nome = form.nome_completo.data
        email = form.email.data
        mensagem = form.mensagem.data
        enviar_email_dm(nome, email, mensagem)
        return render_template('views/contato.html', form=form, enviado=True, form_login=form_login)
    return render_template('views/contato.html', form=form, form_login=form_login)


@views.route('/bug-report', methods=['POST', 'GET'])
def bug_report():
    """
    Página de envio do bug report
    """
    form_login = LoginForm(request.form)
    form = BugReportForm()

    if form.validate_on_submit():
        info = {
            "assunto": 'SECOMP - Bug Report',  # assunto do email
            "email": 'ti@secompufscar.com.br',  # email destino
            "nome": form.autor.data,  # nome do autor
            "titulo": form.titulo.data,
            "descricao": form.descricao.data,
            "impacto": form.impacto.data,
            "template": 'email/report.html',  # path do template (raiz dentro do diretório 'templates')
            "footer": 'TI X SECOMP UFSCar'
        }

        if form.falha.data == 8:
            info['falha'] = form.outra_falha.data
        else:
            info['falha'] = opcoes_falha[form.falha.data][1]

        if form.contato.data:
            info['contato'] = form.contato.data

        anexos = []
        if form.anexo.data:
            blobs = request.files.getlist('anexo')
            for blob in blobs:
                filename = secure_filename(blob.filename)
                filename = f'{info["titulo"]}_{filename}'
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reports')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                abs_path = os.path.join(upload_path, filename)
                anexos.append(abs_path)
                blob.save(abs_path)

        enviar_email_generico(info=info, anexo=anexos)
        flash("Seu report foi enviado!")
        return render_template('views/bug_report.html', form=form, form_login=form_login)
    return render_template('views/bug_report.html', form=form, form_login=form_login)


@views.route('/constr', methods=["GET", "POST"])
def constr():
    form_login = LoginForm(request.form)
    return render_template('views/em_constr.html', title='Página em construção', form_login=form_login)


@views.route('/sobre', methods=["GET", "POST"])
def sobre():
    form_login = LoginForm(request.form)
    return render_template('views/sobre.html', title='Sobre a Secomp', form_login=form_login)


@views.route('/cronograma', methods=["GET", "POST"])
def cronograma():
    form_login = LoginForm(request.form)
    return render_template('views/cronograma.html', title='Cronograma', form_login=form_login, info_cronograma=get_cronograma())

@views.route('/equipe', methods=["GET", "POST"])
def equipe():
    form_login = LoginForm(request.form)
    return render_template('views/equipe.html', title='Equipe', form_login=form_login, info_equipe=get_equipe(database=False))

@views.route('/faq', methods=["GET", "POST"])
def faq():
    form_login = LoginForm(request.form)
    return render_template('views/faq.html', title='FAQ', form_login=form_login)


@views.route('/ctf', methods=["GET", "POST"])
def ctf():
    '''
    form_login = LoginForm(request.form)
    return render_template('views/ctf.html', title='CTF', form_login=form_login)
    '''
    return redirect(url_for('views.index'))

@views.route('/gamejam', methods=["GET", "POST"])
def gamejam():
    form_login = LoginForm(request.form)
    return render_template('views/gamejam.html', title='CTF', form_login=form_login)

@views.route('/desafio', methods=["GET", "POST"])
def desafio():
    form_login = LoginForm(request.form)
    return render_template('views/desafio.html', title='CTF', form_login=form_login)

@limiter.limit("50/day")
@views.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        user = db.session.query(Usuario).filter_by(
            email=form.email.data).first()
        if user:
            atividade_confirmada, atividade, view_atividade = confirmacao_atividade_ministrante(user)
            if user.senha is not None and pbkdf2_sha256.verify(form.senha.data, user.senha):
                user.autenticado = True
                user.ultimo_login = datetime.now()
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                if atividade_confirmada == False:
                    return redirect(url_for('conteudo.dados_hospedagem_transporte'))
                return redirect(url_for('users.dashboard'))
        return render_template('views/login.html', form_login=form, form=form, erro=True)
    return render_template('views/login.html', form_login=form, form=form)


@limiter.limit("50/day")
@views.route("/confirm-login", methods=["GET", "POST"])
def relogin():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = db.session.query(Usuario).filter_by(email=form.email.data).first()
        if user:
            if user.senha is not None and pbkdf2_sha256.verify(form.senha.data, user.senha):
                user.autenticado = True
                user.ultimo_login = datetime.now()
                db.session.add(user)
                db.session.commit()
                confirm_login()
                return redirect(url_for('users.dashboard'))
        return render_template('views/login.html', form_login=form, form=form, erro=True)
    return render_template('views/login.html', form_login=form, form=form)

@views.route("/logout", methods=["GET"])
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
    return redirect(url_for('views.login'))

@views.route("/senhas", methods=["GET"])
def senhas():
    return render_template('views/requisito_50.html')

@views.route("/patrocinadores", methods=["GET"])
def patrocinadores():
    '''
    Renderiza página referente aos patrocinadores da edição atual
    '''
    '''
    form = LoginForm(request.form)
    patrocinadores = db.session.query(Patrocinador).filter_by(ativo_site=True).order_by(Patrocinador.id_cota)
    return render_template('views/patrocinadores.html', patrocinadores=patrocinadores, form_login=form, edicao=EDICAO_ATUAL)
    '''
    return redirect(url_for('views.index'))

@views.route("/pontuacao", methods=["GET"])
def pontuacao_compcases():
    '''
    Renderiza página referente a pontuação geral do COMPCases
    '''
    form = LoginForm(request.form)
    participantes = get_ranking_pontuacao()
    participante_logado = None
    try:
        participante_logado = participante = db.session.query(Participante).filter_by(
            usuario=current_user).first()
    except:
        pass
    return render_template('views/pontuacao_compcases.html', participantes=participantes, participante_logado=participante_logado, form_login=form)

@views.route("/protected/<path:filename>", methods=["GET"])
@login_required
def protected(filename):
    if "CONTEUDO" in current_user.getPermissoes() or "PATROCINIO" in current_user.getPermissoes() or "MINISTRANTE" in current_user.getPermissoes() or "ADMIN" in current_user.getPermissoes():
        dir, filename = filename.rsplit('/', 1)
        filename = secure_filename(filename)
        caminho = os.path.join(current_app.root_path, 'protected', dir)
        if os.path.exists(caminho):
            return send_from_directory(caminho, filename)
        abort(404)
    abort(403)

@views.route("/uploads/<path:filename>", methods=["GET"])
@login_required
def uploads(filename):
    participante = db.session.query(Participante).filter(Participante.id_usuario == current_user.id, Participante.id_evento == get_id_evento_atual()).first()
    dir, filename = filename.rsplit('/', 1)
    dir = dir.replace(' ', '')
    if "CONTEUDO" in current_user.getPermissoes() or "PATROCINIO" in current_user.getPermissoes() or "ADMIN" in current_user.getPermissoes() or "GERENCIAR_COMPROVANTES" in current_user.getPermissoes() or get_permissao_comprovante(participante, filename) or diretorio_publico(dir):
        filename = secure_filename(filename)
        caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], dir)
        if os.path.exists(caminho):
            return send_from_directory(caminho, filename)
        abort(404)
    abort(403)
