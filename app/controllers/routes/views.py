from flask import render_template, request, Blueprint, url_for, redirect, current_app, send_from_directory, abort
from flask_login import login_required, login_user, logout_user, current_user
from passlib.hash import pbkdf2_sha256
import os
from app.controllers.forms.forms import *
from app.controllers.functions.email import enviar_email_dm, enviar_email_generico
from app.controllers.functions.helpers import *
from app.controllers.constants import *
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr

limiter = Limiter(current_app, key_func=get_ipaddr)
views = Blueprint('views', __name__, static_folder='static', template_folder='templates')


@views.route('/', methods=["GET", "POST"])
def index():
    """
    Renderiza a página inicial do projeto
    """
    '''
    form_login = LoginForm(request.form)
    return render_template('views/index.html', title='Página inicial',
                           secomp_now=secomp_now[0], secomp=secomp[0],
                           secomp_email=secomp_email,
                           secompEdition=secomp_edition,
                           form_login=form_login)
    '''
    return redirect(url_for('views.login'))

#@views.route('/contato', methods=['POST', 'GET'])
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
    form = BugReportForm(request.form)

    if form.validate_on_submit():
        content = {
            "assunto": 'SECOMP - Bug Report',  # assunto do email
            "email": 'ti@secompufscar.com.br',  # email destino
            "nome": form.autor.data,  # nome do autor
            "titulo": form.titulo.data,
            "falha": form.falha.data,
            "resumo": form.resumo.data,
            "descricao": form.descricao.data,
            "impacto": form.impacto.data,
            "template": 'email/report.html',  # path do template (raiz dentro do diretório 'templates')
            "footer": 'TI X SECOMP UFSCar'
        }
        if form.contato.data:
            content['contato'] = form.contato.data
        enviar_email_generico(info=content)
        return render_template('views/bug-report.html', form=form, form_login=form_login, enviado=True)
    return render_template('views/bug-report.html', form=form, form_login=form_login)


@views.route('/constr', methods=["GET", "POST"])
def constr():
    form_login = LoginForm(request.form)
    return render_template('views/em_constr.html', title='Página em construção', form_login=form_login)


#@views.route('/sobre', methods=["GET", "POST"])
def sobre():
    form_login = LoginForm(request.form)
    return render_template('views/sobre.html', title='Sobre a Secomp', form_login=form_login)


#@views.route('/cronograma', methods=["GET", "POST"])
def cronograma():
    form_login = LoginForm(request.form)
    return render_template('views/cronograma.html', title='Cronograma', form_login=form_login)


#@views.route('/equipe', methods=["GET", "POST"])
def equipe():
    import json
    import os.path as op
    import app.config as conf
    form_login = LoginForm(request.form)
    filename = op.join(op.dirname(conf.__file__), 'membros_org.json')
    with open(filename, 'r') as read_file:
        data = json.load(read_file)
    return render_template('views/equipe.html', title='Equipe', data=data, form_login=form_login)


#@views.route('/faq', methods=["GET", "POST"])
def faq():
    form_login = LoginForm(request.form)
    return render_template('views/faq.html', title='FAQ', form_login=form_login)


#@views.route('/ctf', methods=["GET", "POST"])
def ctf():
    form_login = LoginForm(request.form)
    return render_template('views/ctf.html', title='CTF', form_login=form_login)

#@views.route('/teste', methods=["GET","POST"])
def teste():
    form_login = LoginForm(request.form)
    return render_template('teste.html', title='Teste', form_login=form_login)

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
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                if atividade_confirmada == False:
                    return redirect(url_for('conteudo.dados_hospedagem_transporte'))
                return redirect(url_for('views.constr'))
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

#@views.route("/senhas", methods=["GET"])
def senhas():
    return render_template('views/requisito_50.html')

#@views.route("/patrocinadores", methods=["GET"])
def patrocinadores():
    patrocinadores = db.session.query(Patrocinador)
    return render_template('views/patrocinadores.html', patrocinadores=patrocinadores)

@views.route("/protected/<path:filename>", methods=["GET"])
@login_required
def protected(filename):
    if "CONTEUDO" in current_user.getPermissoes() or "PATROCINIO" in current_user.getPermissoes() or "MINISTRANTE" in current_user.getPermissoes() or "ADMIN" in current_user.getPermissoes():
        return send_from_directory(
            os.path.join(current_app.root_path, 'protected'),
            filename
        )
    abort(404)
