from flask import render_template, request, redirect, abort, url_for, Blueprint
from flask_login import login_required, login_user, logout_user, current_user

from app.controllers.forms import *
from app.controllers.functions import *
from app.models.models import *
from os import path, makedirs

admin_area_routes = Blueprint('admin_area_routes', __name__, template_folder='templates')
@app.route('/area-administrativa/estoque-camisetas')
@login_required
def estoque_camisetas():
    if (current_user.permissao > 0):
        camisetas = db.session.query(Camiseta)
        return render_template('controle_camisetas.html', camisetas=camisetas, usuario=current_user)
    else:
        abort(403)


@app.route('/area-administrativa/estoque-camisetas/<tamanho>')
@login_required
def estoque_camisetas_por_tamanho(tamanho):
    if (current_user.permissao > 0):
        camisetas = db.session.query(Camiseta).filter_by(tamanho=tamanho)
        return render_template('controle_camisetas.html', camisetas=camisetas, usuario=current_user)
    else:
        abort(403)


@app.route('/area-administrativa/cadastro-patrocinio', methods=['POST', 'GET'])
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

@app.route('/area-administrativa/venda-kits', methods=['POST', 'GET'])
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

@app.route('/area-administrativa/fazer-sorteio')
@login_required
def sortear():
    return render_template('sortear_usuario.html', sorteando=False)

@app.route('/area-administrativa/fazer-sorteio/do')
@login_required
def sorteando():
    # <Falta conferir permissões>
    sorteado = db.session.query(Participante)
    sorteado = sorteado[randint(1, sorteado.count()) - 1]
    return render_template('sortear_usuario.html', sorteado=sorteado, sorteando=True)

@app.route('/area-administrativa/alterar-camiseta', methods=["GET","POST"])
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
