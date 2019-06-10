from random import SystemRandom

from flask import render_template, request, redirect, abort, url_for, Blueprint, jsonify
from flask_login import login_required, current_user

from app.controllers.forms.forms import *
from app.models.models import *
from app.controllers.functions.helpers import get_usuarios_query, get_atividades_json, get_participantes_da_atividade_json
from app.controllers.functions.email import enviar_email_custon


management = Blueprint('management', __name__, static_folder='static',
                       template_folder='templates', url_prefix='/gerenciar')


@management.route('/')
@login_required
def gerenciar():
    if current_user.is_admin():
        permissoes = db.session.query(Permissao).all()
        permissoes = {x.nome: x for x in permissoes}
        return render_template('management/gerenciar.html', usuario=current_user, permissoes=permissoes)
    else:
        abort(403)


@management.route('/estoque-camisetas')
@login_required
def estoque_camisetas():
    permissoes = current_user.getPermissoes()
    if("ALTERAR_CAMISETAS" in permissoes or current_user.is_admin()):
        camisetas = db.session.query(Camiseta)
        return render_template('management/controle_camisetas.html', camisetas=camisetas, usuario=current_user)
    else:
        abort(403)


@management.route('/estoque-camisetas/<tamanho>')
@login_required
def estoque_camisetas_por_tamanho(tamanho):
    permissoes = current_user.getPermissoes()
    if("ALTERAR_CAMISETAS" in permissoes or current_user.is_admin()):
        camisetas = db.session.query(Camiseta).filter_by(tamanho=tamanho)
        return render_template('management/controle_camisetas.html', camisetas=camisetas, usuario=current_user)
    else:
        abort(403)


@management.route('/cadastro-patrocinador', methods=['POST', 'GET'])
@login_required
def cadastro_patrocinador():
    permissoes = current_user.getPermissoes()
    if("CADASTRAR_PATROCINADOR" in permissoes or current_user.is_admin()):
        form = PatrocinadorForm(request.form)
        if form.validate_on_submit():
            patrocinador = Patrocinador(nome_empresa=form.nome_empresa.data, logo=form.logo.data,
                                        ativo_site=form.ativo_site.data, id_cota=form.id_cota.data,
                                        link_website=form.link_website.data)
            db.session.add(patrocinador)
            db.session.flush()
            db.session.commit()
            return redirect(url_for('.cadastro-patrocinador'))
        else:
            return render_template('management/cadastro_patrocinador.html', form=form)
    else:
        abort(403)


@management.route('/venda-kits', methods=['POST', 'GET'])
@login_required
def vender_kits():
    permissoes = current_user.getPermissoes()
    if("VENDA_PRESENCIAL" in permissoes or current_user.is_admin()):
        form = VendaKitForm(request.form)
        if form.validate_on_submit() and form.participante.data is not None:
            camiseta = db.session.query(Camiseta).filter_by(id=form.camiseta.data).first()
            participante = db.session.query(Participante).filter_by(id=form.participante.data).first()
            if participante.pagamento:
                return render_template('management/venda_de_kits.html', alerta="Kit já comprado!", form=form)
            elif camiseta.quantidade_restante > 0:
                participante.id_camiseta = form.camiseta.data
                participante.pacote = True
                participante.pagamento = True
                camiseta.quantidade_restante = camiseta.quantidade_restante - 1
                db.session.add(camiseta)
                db.session.add(participante)
                db.session.commit()
                return render_template('management/venda_de_kits.html', alerta="Compra realizada com sucesso!", form=form)
            elif camiseta.quantidade_restante == 0:
                return render_template('management/venda_de_kits.html', alerta="Sem estoque para " + camiseta.tamanho,
                                       form=form)
        return render_template('management/venda_de_kits.html', alerta="Preencha o formulário abaixo", form=form)
    else:
        abort(403)

@management.route('/sorteio')
@login_required
def sorteia_usuario():
    permissoes = current_user.getPermissoes()
    if("SORTEAR" in permissoes or current_user.is_admin()):
        return render_template('management/sortear_usuario.html', sorteando=False)
    else:
        abort(403)

@management.route('/sorteio/sortear', methods=["POST"])
@login_required
def sortear():
    permissoes = current_user.getPermissoes()
    if("SORTEAR" in permissoes or current_user.is_admin()):
        sorteado = db.session.query(Participante)
        sorteado = sorteado[SystemRandom().randint(1, sorteado.count()) - 1]
        return render_template('management/sortear_usuario.html', sorteado=sorteado, sorteando=True)
    else:
        abort(403)

@management.route('/alterar-camisetas', methods=["GET", "POST"])
@login_required
def alterar_camiseta():
    permissoes = current_user.getPermissoes()
    if("ALTERAR_CAMISETAS" in permissoes or current_user.is_admin()):
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
                return render_template('management/alterar_camisetas.html', participante=participante, camiseta=camiseta,
                                       sucesso='s', form=form)
            else:
                return render_template('management/alterar_camisetas.html', participante=participante, camiseta=camiseta,
                                       sucesso='n', form=form)
        return render_template('management/alterar_camisetas.html', form=form)
    else:
        abort(403)

@management.route('/listas', methods=["GET","POST"])
@login_required
def listas():
    permissoes = current_user.getPermissoes()
    if("GERAR_LISTAS" in permissoes or current_user.is_admin()):
        form = ListasParticipantes(request.form)
        if(form.validate_on_submit()):
            if(form.tipo.data == 0):
                lista = db.session.query(Atividade).filter_by(titulo=form.atividades.data).first().participantes
                return render_template('management/listas_participante.html', atividade=form.atividades.data, tipo='inscritos', lista=lista, form=form)
            elif(form.tipo.data == 1):
                lista = db.session.query(Atividade).filter_by(titulo=form.atividades.data).first().presencas
                return render_template('management/listas_participante.html', atividade=form.atividades.data, tipo='presentes', lista=lista, form=form)
        else:
            return render_template('management/listas_participante.html', form=form)
    else:
        abort(403)


@management.route('/pesquisa-usuario-email-custon',methods=['POST'])
def pesquisa_usuario_email_custon():
    atividadeID = request.form['id']

    participantes = get_participantes_da_atividade_json(int(atividadeID))
    return jsonify({'output': participantes})


@management.route('/atividades-json-email-custon',methods=['POST'])
def atividades_json_email_custon():
    atividades = get_atividades_json()
    return jsonify({'output': atividades})


@management.route("/email-custom", methods=["GET"])
def email_custom():
    form_login = LoginForm(request.form)

    return render_template('management/email_custom.html', form_login=form_login)


@management.route('/executa-email-custon',methods=['POST'])
def executa_email_custon():
    try:
        pkg = request.form

        assunto = pkg['assunto']
        titulo = pkg['titulo']
        template = pkg['template']
        temAnexo = pkg['temAnexo']
        anexo = pkg['anexo'].split(',')
        complemento = pkg['complemento']
        selecionados = pkg['selecionados'].split(',')
        extencao = pkg['extencao']

        enviar_email_custon(assunto, titulo, template, temAnexo, anexo, complemento, selecionados, extencao)

        return jsonify('Sucesso')
    except Exception as e:
        print(e)
        return jsonify('Falha')
