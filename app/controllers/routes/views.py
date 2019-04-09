from flask import render_template, request, redirect, url_for

from app.controllers.forms.forms import *
from app.controllers.functions.email import enviar_email_DM
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


@app.route('/contato', methods=['POST', 'GET'])
def contatoDM():
    """
    Página de contato
    """
    form = ContatoForm(request.form)
    if form.validate_on_submit():
        nome = form.nome_completo.data
        email = form.email.data
        mensagem = form.mensagem.data
        enviar_email_DM(app, nome, email, mensagem)
        return render_template('contato.html', form=form, enviado=True)
    return render_template('contato.html', form=form)


@app.route('/constr')
def constr():
    return render_template('em_constr.html', title='Página em construção')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html', title='Sobre a Secomp')


@app.route('/equipe')
def equipe():
    import json
    with open('./config/membros_org.json', 'r') as read_file:
        data = json.load(read_file)
    return render_template('equipe.html', title='Equipe', data=data)


@app.route('/faq')
def faq():
    return render_template('faq.html', title='FAQ')


@app.errorhandler(404)
def not_found():
    return redirect(url_for('404'))


@app.errorhandler(403)
def unauthorized():
    return redirect(url_for('403'))
