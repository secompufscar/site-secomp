from flask import render_template, request, redirect, abort, url_for, Blueprint
from flask_login import login_required, login_user, logout_user, current_user

from app.controllers.forms import *
from app.controllers.functions import *
from app.models.models import *

routes = Blueprint('routes', __name__, template_folder='templates')
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
        enviarEmailDM(app, nome, email, mensagem)
        return render_template('contato.html', form=form, enviado=True)
    return render_template('contato.html', form=form)


@app.route('/inscricao-atividades')
@login_required
def inscricao_atividades():
    minicursos = db.session.query(Atividade).filter_by(
        tipo=TipoAtividade['minicurso'])
    workshops = db.session.query(Atividade).filter_by(
        tipo=TipoAtividade['workshop'])
    palestras = db.session.query(Atividade).filter_by(
        tipo=TipoAtividade['palestra'])
    return render_template('inscricao_atividades.html',
                           participante=db.session.query(Participante).filter_by(
                               usuario=current_user).first(),
                           usuario=current_user, minicursos=minicursos, workshops=workshops, palestras=palestras)


@app.route('/inscricao-atividades/<filtro>')
@login_required
def inscricao_atividades_com_filtro(filtro):
    minicursos = db.session.query(Atividade).filter(
        Atividade.tipo.like(TipoAtividade['minicurso']), Atividade.titulo.like("%" + filtro + "%"))
    workshops = db.session.query(Atividade).filter(
        Atividade.tipo.like(TipoAtividade['workshop']), Atividade.titulo.like("%" + filtro + "%"))
    palestras = db.session.query(Atividade).filter(
        Atividade.tipo.like(TipoAtividade['palestra']), Atividade.titulo.like("%" + filtro + "%"))

    return render_template('inscricao_atividades.html',
                           participante=db.session.query(Participante).filter_by(
                               usuario=current_user).first(),
                           usuario=current_user, minicursos=minicursos, workshops=workshops, palestras=palestras)


@app.route('/inscrever-atividade/<id>')
@login_required
def inscrever(id):
    atv = db.session.query(Atividade).filter_by(id=id)[0]
    if atv.vagas_disponiveis > 0:
        atv.participantes.append(db.session.query(
            Participante).filter_by(usuario=current_user).first())
        atv.vagas_disponiveis = atv.vagas_disponiveis - 1
        db.session.flush()
        db.session.commit()
        minicursos = db.session.query(Atividade).filter_by(
            tipo=TipoAtividade['minicurso'])
        workshops = db.session.query(Atividade).filter_by(
            tipo=TipoAtividade['workshop'])
        palestras = db.session.query(Atividade).filter_by(
            tipo=TipoAtividade['palestra'])

        return render_template('inscricao_atividades.html',
                               participante=db.session.query(Participante).filter_by(
                                   usuario=current_user).first(),
                               usuario=current_user, minicursos=minicursos, workshops=workshops, palestras=palestras,
                               acao="+")
    else:
        return "Não há vagas disponíveis!"
    return id


@app.route('/desinscrever-atividade/<id>')
@login_required
def desinscrever(id):
    atv = db.session.query(Atividade).filter_by(id=id).first()
    if db.session.query(Participante).filter_by(usuario=current_user).first() in atv.participantes:
        atv.participantes.remove(db.session.query(
            Participante).filter_by(usuario=current_user).first())
        atv.vagas_disponiveis = atv.vagas_disponiveis + 1
        db.session.flush()
        db.session.commit()
        minicursos = db.session.query(Atividade).filter_by(
            tipo=TipoAtividade['minicurso'])
        workshops = db.session.query(Atividade).filter_by(
            tipo=TipoAtividade['workshop'])
        palestras = db.session.query(Atividade).filter_by(
            tipo=TipoAtividade['palestra')
        return render_template('inscricao_atividades.html',
                               participante=db.session.query(Participante).filter_by(
                                   usuario=current_user).first(),
                               usuario=current_user, minicursos=minicursos, workshops=workshops, palestras=palestras,
                               acao="-")
    else:
        return "Não está inscrito nessa atividade!"

@app.route('/estoque-camisetas')
@login_required
def estoque_camisetas():
    if (current_user.permissao > 0):
        camisetas = db.session.query(Camiseta)
        return render_template('controle_camisetas.html', camisetas=camisetas, usuario=current_user)
    else:
        abort(403)


@app.route('/estoque-camisetas/<tamanho>')
@login_required
def estoque_camisetas_por_tamanho(tamanho):
    if (current_user.permissao > 0):
        camisetas = db.session.query(Camiseta).filter_by(tamanho=tamanho)
        return render_template('controle_camisetas.html', camisetas=camisetas, usuario=current_user)
    else:
        abort(403)
