from flask import render_template, request, redirect, abort, url_for, Blueprint
from flask_login import login_required, login_user, logout_user, current_user

from app.controllers.forms import *
from app.controllers.functions import *
from app.models.models import *
from os import path, makedirs

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
        tipo=Atividades.MINICURSO.value)
    workshops = db.session.query(Atividade).filter_by(
        tipo=Atividades.WORKSHOP.value)
    palestras = db.session.query(Atividade).filter_by(
        tipo=Atividades.PALESTRA.value)
    return render_template('inscricao_atividades.html',
                           participante=db.session.query(Participante).filter_by(
                               usuario=current_user).first(),
                           usuario=current_user, minicursos=minicursos, workshops=workshops, palestras=palestras)


@app.route('/inscricao-atividades/<filtro>')
@login_required
def inscricao_atividades_com_filtro(filtro):
    minicursos = db.session.query(Atividade).filter(
        Atividade.tipo.like(Atividades.MINICURSO.value), Atividade.titulo.like("%" + filtro + "%"))
    workshops = db.session.query(Atividade).filter(
        Atividade.tipo.like(Atividades.WORKSHOP.value), Atividade.titulo.like("%" + filtro + "%"))
    palestras = db.session.query(Atividade).filter(
        Atividade.tipo.like(Atividades.PALESTRA.value), Atividade.titulo.like("%" + filtro + "%"))

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
            tipo=Atividades.MINICURSO.value)
        workshops = db.session.query(Atividade).filter_by(
            tipo=Atividades.WORKSHOP.value)
        palestras = db.session.query(Atividade).filter_by(
            tipo=Atividades.PALESTRA.value)

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
            tipo=Atividades.MINICURSO.value)
        workshops = db.session.query(Atividade).filter_by(
            tipo=Atividades.WORKSHOP.value)
        palestras = db.session.query(Atividade).filter_by(
            tipo=Atividades.PALESTRA.value)
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


@app.route('/cadastro-patrocinio', methods=['POST', 'GET'])
@login_required
def cadastro_patrocinio():
    form = PatrocinadorForm(request.form)

    if form.validate_on_submit():
        patrocinador = Patrocinador(nome_empresa=form.nome_empresa.data,
            logo=form.logo.data, ativo_site=form.ativo_site.data, id_cota=form.id_cota.data,
            link_website=form.link_website.data,
            ultima_atualizacao_em=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        db.session.add(patrocinador)
        db.session.flush()
        db.session.commit()
        return redirect(url_for('cadastro-patrocinio'))
    else:
        return render_template('cadastro_patrocinio.html', form=form)

@app.route('/venda-kits', methods=['POST', 'GET'])
@login_required
def vender_kits():
    #<Falta conferir permissões>
    form = VendaKitForm(request.form)
    if (form.validate_on_submit() and form.participante.data != None):
        camiseta = db.session.query(Camiseta).filter_by(id=form.camiseta.data).first()
        participante = db.session.query(Participante).filter_by(id=form.participante.data).first()
        if(participante.pagamento):
            return render_template('venda_de_kits.html', alerta="Kit já comprado!", form=form)
        elif(camiseta.quantidade_restante > 0):
            participante.id_camiseta = form.camiseta.data
            participante.pacote = True
            participante.pagamento = True
            camiseta.quantidade_restante = camiseta.quantidade_restante - 1
            db.session.add(camiseta)
            db.session.add(participante)
            db.session.commit()
            return render_template('venda_de_kits.html', alerta="Compra realizada com sucesso!", form=form)
        elif(camiseta.quantidade_restante == 0):
            return render_template('venda_de_kits.html', alerta="Sem estoque para " + camiseta.tamanho, form=form)
    return render_template('venda_de_kits.html', alerta="Preencha o formulário abaixo", form=form)

@app.route('/fazer-sorteio')
@login_required
def sortear():
    return render_template('sortear_usuario.html', sorteando=False)

@app.route('/fazer-sorteio/do')
@login_required
def sorteando():
    # <Falta conferir permissões>
    sorteado = db.session.query(Participante)
    sorteado = sorteado[randint(1, sorteado.count()) - 1]
    return render_template('sortear_usuario.html', sorteado=sorteado, sorteando=True)

@app.route('/alterar-camiseta', methods=["GET","POST"])
@login_required
def alterar_camiseta():
    # <Falta conferir permissões>
    form = AlteraCamisetaForm(request.form)
    if (form.validate_on_submit() and form.participante.data != None):
        participante = db.session.query(Participante).filter_by(id=form.participante.data).first()
        camiseta = db.session.query(Camiseta).filter_by(id=form.camiseta.data).first()
        if (camiseta.quantidade_restante > 0):
            camiseta_antiga = db.session.query(Camiseta).filter_by(id=participante.id_camiseta).first()
            camiseta_antiga.quantidade_restante = camiseta_antiga.quantidade_restante + 1
            camiseta.quantidade_restante = camiseta.quantidade_restante - 1
            participante.id_camiseta = camiseta.id
            db.session.add(camiseta_antiga)
            db.session.add(camiseta)
            db.session.add(participante)
            db.session.commit()
            return render_template('alterar_camiseta.html', participante=participante, camiseta=camiseta, sucesso='s', form=form)
        else:
            return render_template('alterar_camiseta.html', participante=participante, camiseta=camiseta, sucesso='n', form=form)
    return render_template('alterar_camiseta.html', form=form)

@app.route('/constr')
def constr():
    return render_template('em_constr.html', title='Página em construção')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html', title='Sobre a Secomp')
