from random import SystemRandom

from flask import render_template, request, redirect, abort, url_for
from flask_login import login_required, current_user

from app.controllers.forms.forms import *
from app.models.models import *


@app.route('/gerenciar')
@login_required
def gerenciar():
    if current_user.is_admin():
        permissoes = db.query(Permissao).all()
        permissoes = {x.nome: x for x in permissoes}
        return render_template('gerenciar.html', usuario=current_user, permissoes=permissoes)
    else:
        abort(403)


@app.route('/gerenciar/estoque-camisetas')
@login_required
def estoque_camisetas():
    if current_user.is_admin():
        camisetas = db.session.query(Camiseta)
        return render_template('controle_camisetas.html', camisetas=camisetas, usuario=current_user)
    else:
        abort(403)


@app.route('/gerenciar/estoque-camisetas/<tamanho>')
@login_required
def estoque_camisetas_por_tamanho(tamanho):
    if current_user.is_admin():
        camisetas = db.session.query(Camiseta).filter_by(tamanho=tamanho)
        return render_template('controle_camisetas.html', camisetas=camisetas, usuario=current_user)
    else:
        abort(403)


@app.route('/gerenciar/cadastro-patrocinador', methods=['POST', 'GET'])
@login_required
def cadastro_patrocinador():
    form = PatrocinadorForm(request.form)
    if form.validate_on_submit():
        patrocinador = Patrocinador(nome_empresa=form.nome_empresa.data, logo=form.logo.data,
                                    ativo_site=form.ativo_site.data, id_cota=form.id_cota.data,
                                    link_website=form.link_website.data)
        db.session.add(patrocinador)
        db.session.flush()
        db.session.commit()
        return redirect(url_for('cadastro-patrocinador'))
    else:
        return render_template('cadastro_patrocinador.html', form=form)


@app.route('/gerenciar/venda-kits', methods=['POST', 'GET'])
@login_required
def vender_kits():
    # TODO: conferir permissões
    form = VendaKitForm(request.form)
    if form.validate_on_submit() and form.participante.data is not None:
        camiseta = db.session.query(Camiseta).filter_by(id=form.camiseta.data).first()
        participante = db.session.query(Participante).filter_by(id=form.participante.data).first()
        if participante.pagamento:
            return render_template('venda_de_kits.html', alerta="Kit já comprado!", form=form)
        elif camiseta.quantidade_restante > 0:
            participante.id_camiseta = form.camiseta.data
            participante.pacote = True
            participante.pagamento = True
            camiseta.quantidade_restante = camiseta.quantidade_restante - 1
            db.session.add(camiseta)
            db.session.add(participante)
            db.session.commit()
            return render_template('venda_de_kits.html', alerta="Compra realizada com sucesso!", form=form)
        elif camiseta.quantidade_restante == 0:
            return render_template('venda_de_kits.html', alerta="Sem estoque para " + camiseta.tamanho, form=form)
    return render_template('venda_de_kits.html', alerta="Preencha o formulário abaixo", form=form)


@app.route('/gerenciar/sorteio')
@login_required
def sorteia_usuario():
    return render_template('sortear_usuario.html', sorteando=False)


@app.route('/gerenciar/sorteio/sortear')
@login_required
def sortear():
    # TODO: conferir permissões
    sorteado = db.session.query(Participante)
    sorteado = sorteado[SystemRandom().randint(1, sorteado.count()) - 1]
    return render_template('sortear_usuario.html', sorteado=sorteado, sorteando=True)


@app.route('/gerenciar/alterar-camisetas', methods=["GET", "POST"])
@login_required
def alterar_camiseta():
    # TODO: conferir permissões
    form = AlteraCamisetaForm(request.form)
    if form.validate_on_submit() and form.participante.data is not None:
        participante = db.session.query(Participante).filter_by(id=form.participante.data).first()
        camiseta = db.session.query(Camiseta).filter_by(id=form.camiseta.data).first()
        if camiseta.quantidade_restante > 0:
            camiseta_antiga = db.session.query(Camiseta).filter_by(id=participante.id_camiseta).first()
            camiseta_antiga.quantidade_restante = camiseta_antiga.quantidade_restante + 1
            camiseta.quantidade_restante = camiseta.quantidade_restante - 1
            participante.id_camiseta = camiseta.id
            db.session.add(camiseta_antiga)
            db.session.add(camiseta)
            db.session.add(participante)
            db.session.commit()
            return render_template('alterar_camisetas.html', participante=participante, camiseta=camiseta,
                                   sucesso='s', form=form)
        else:
            return render_template('alterar_camisetas.html', participante=participante, camiseta=camiseta,
                                   sucesso='n', form=form)
    return render_template('alterar_camisetas.html', form=form)
