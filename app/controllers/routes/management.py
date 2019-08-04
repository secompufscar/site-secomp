from random import SystemRandom

from flask import render_template, request, redirect, abort, url_for, Blueprint
from flask_login import login_required, current_user

from app.controllers.forms.forms import *
from app.models.models import *
from app.controllers.functions.dictionaries import *
from app.controllers.functions.helpers import *
from app.controllers.forms.validators import *

from secrets import token_urlsafe

from app.controllers.forms.options import get_opcoes_ecustom_atividade, get_opcoes_ecustom_extencao, get_opcoes_ecustom_complemento

management = Blueprint('management', __name__, static_folder='static',
                       template_folder='templates', url_prefix='/gerenciar')


@management.route('/')
@login_required
def gerenciar():
    if current_user.is_admin():
        form_login = LoginForm(request.form)
        permissoes = db.session.query(Permissao).all()
        permissoes = {x.nome: x for x in permissoes}
        return render_template('management/gerenciar.html', usuario=current_user, permissoes=permissoes, form_login=form_login)
    else:
        abort(403)


@management.route('/estoque-camisetas')
@login_required
def estoque_camisetas():
    permissoes = current_user.getPermissoes()
    if("ALTERAR_CAMISETAS" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        camisetas = db.session.query(Camiseta)
        return render_template('management/controle_camisetas.html', camisetas=camisetas, usuario=current_user, form_login=form_login)
    else:
        abort(403)


@management.route('/estoque-camisetas/<tamanho>')
@login_required
def estoque_camisetas_por_tamanho(tamanho):
    permissoes = current_user.getPermissoes()
    if("ALTERAR_CAMISETAS" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        camisetas = db.session.query(Camiseta).filter_by(tamanho=tamanho)
        return render_template('management/controle_camisetas.html', camisetas=camisetas, usuario=current_user, form_login=form_login)
    else:
        abort(403)


@management.route('/cadastro-patrocinador', methods=['POST', 'GET'])
@login_required
def cadastro_patrocinador():
    permissoes = current_user.getPermissoes()
    if("CADASTRAR_PATROCINADOR" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        form = PatrocinadorForm(request.form)
        if form.validate_on_submit():
            patrocinador = Patrocinador(nome_empresa=form.nome_empresa.data, logo=form.logo.data,
                                        ativo_site=form.ativo_site.data, id_cota=form.id_cota.data,
                                        link_website=form.link_website.data, form_login=form_login)
            db.session.add(patrocinador)
            db.session.flush()
            db.session.commit()
            return redirect(url_for('.cadastro-patrocinador'))
        else:
            return render_template('management/cadastro_patrocinador.html', form=form, form_login=form_login)
    else:
        abort(403)


@management.route('/venda-kits', methods=['POST', 'GET'])
@login_required
def vender_kits():
    permissoes = current_user.getPermissoes()
    if("VENDA_PRESENCIAL" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        form = VendaKitForm(request.form)
        if form.validate_on_submit() and form.participante.data is not None:
            camiseta = db.session.query(Camiseta).filter_by(id=form.camiseta.data).first()
            participante = db.session.query(Participante).filter_by(id=form.participante.data).first()
            if participante.pagamento:
                return render_template('management/venda_de_kits.html', alerta="Kit já comprado!", form=form, form_login=form_login)
            elif camiseta.quantidade_restante > 0:
                participante.id_camiseta = form.camiseta.data
                participante.pacote = True
                participante.pagamento = True
                camiseta.quantidade_restante = camiseta.quantidade_restante - 1
                db.session.add(camiseta)
                db.session.add(participante)
                db.session.commit()
                return render_template('management/venda_de_kits.html', alerta="Compra realizada com sucesso!",
                                       form=form, form_login=form_login)
            elif camiseta.quantidade_restante == 0:
                return render_template('management/venda_de_kits.html', alerta="Sem estoque para " + camiseta.tamanho,
                                       form=form, form_login=form_login)
        return render_template('management/venda_de_kits.html', alerta="Preencha o formulário abaixo", form=form, form_login=form_login)
    else:
        abort(403)

@management.route('/sorteio')
@login_required
def sorteia_usuario():
    permissoes = current_user.getPermissoes()
    if("SORTEAR" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        return render_template('management/sortear_usuario.html', sorteando=False, form_login=form_login)
    else:
        abort(403)

@management.route('/sorteio/sortear', methods=["POST"])
@login_required
def sortear():
    permissoes = current_user.getPermissoes()
    if("SORTEAR" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        sorteado = db.session.query(Participante)
        sorteado = sorteado[SystemRandom().randint(1, sorteado.count()) - 1]
        return render_template('management/sortear_usuario.html', sorteado=sorteado, sorteando=True, form_login=form_login)
    else:
        abort(403)

@management.route('/alterar-camisetas', methods=["GET", "POST"])
@login_required
def alterar_camiseta():
    permissoes = current_user.getPermissoes()
    if("ALTERAR_CAMISETAS" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
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
                                       sucesso='s', form=form, form_login=form_login)
            else:
                return render_template('management/alterar_camisetas.html', participante=participante, camiseta=camiseta,
                                       sucesso='n', form=form, form_login=form_login)
        return render_template('management/alterar_camisetas.html', form=form)
    else:
        abort(403)

@management.route('/listas', methods=["GET", "POST"])
@login_required
def listas():
    permissoes = current_user.getPermissoes()
    if("GERAR_LISTAS" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        form = ListasParticipantes(request.form)
        if(form.validate_on_submit()):
            if(form.tipo.data == 0):
                lista = db.session.query(Atividade).filter_by(titulo=form.atividades.data).first().participantes
                return render_template('management/listas_participante.html', atividade=form.atividades.data,
                                        tipo='inscritos', lista=lista, form=form, form_login=form_login)
            elif(form.tipo.data == 1):
                lista = db.session.query(Atividade).filter_by(titulo=form.atividades.data).first().presencas
                return render_template('management/listas_participante.html', atividade=form.atividades.data,
                                        tipo='presentes', lista=lista, form=form, form_login=form_login)
        else:
            return render_template('management/listas_participante.html', form=form, form_login=form_login)
    else:
        abort(403)

@management.route("/email-custom", methods=["GET"])
@login_required
def email_custom():
    '''
    Página para envio de email
    '''
    permissoes = current_user.getPermissoes()
    if("ENVIAR_EMAIL" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        form = EmailCuston(request.form)

        return render_template('management/email_custom.html', form=form, form_login=form_login)
    else:
        abort(403)

@management.route('/gerar-url-conteudo', methods=['POST', 'GET'])
@login_required
def gerar_url_conteudo():
    permissoes = current_user.getPermissoes()
    if("CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        form = GerarUrlConteudoForm(request.form)
        emails = request.form.getlist('emails[]')
        if form.validate_on_submit():
            atividade_removida = request.form.getlist('removido')
            if len(atividade_removida) > 0:
                atividade_removida = db.session.query(Atividade).get(atividade_removida[0])
                if atividade_removida is not None:
                    for ministrante in atividade_removida.ministrantes:
                        if ministrante.usuario.senha is None:
                            db.session.delete(ministrante.usuario)
                            db.session.delete(ministrante)
                        db.session.delete(atividade_removida)
                        db.session.commit()
            if verifica_lista_emails(emails):
                codigo = token_urlsafe(150)
                tipo = db.session.query(TipoAtividade).filter_by(id=form.tipo_atividade.data).first()
                atividade = Atividade(url_codigo=codigo, id_evento=get_id_evento_atual(), id_tipo=tipo.id)
                if atividade is not None and tipo is not None:
                    atividade.tipo = tipo
                    for email in emails:
                        usuario = db.session.query(Usuario).filter_by(email=email).first()
                        if usuario is None:
                            usuario = Usuario(email=email, primeiro_nome='', sobrenome='')
                            ministrante = Ministrante(usuario=usuario)
                            usuario.ministrante = ministrante
                            db.session.add(usuario)
                            db.session.add(ministrante)
                        else:
                            ministrante = usuario.ministrante
                        db.session.commit()
                        atividade.ministrantes.append(ministrante)
                    db.session.add(atividade)
                    db.session.commit()
        return render_template("management/gerar_url_conteudo.html", form=form, dict_urls=get_urls_conteudo(), form_login=form_login)
    else:
        abort(403)

@management.route('/crd-flag', methods=["GET", "POST"])
@login_required
def cadastro_flags():
    permissoes = current_user.getPermissoes()
    if("CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        form = CadastrarFlagForm(request.form)
        if form.validate_on_submit():
            flag = Flag(codigo=form.flag.data, pontos=form.pontos.data)
            db.session.add(flag)
            db.session.flush()
            db.session.commit()
            flags = db.session.query(Flag).filter_by(ativa=True).all()
            return render_template("management/crd_flags.html", form_login=form_login, form=form, cadastrado=True, desativada=False, flags=flags, usuario=current_user)
        else:
            flags = db.session.query(Flag).filter_by(ativa=True).all()
            return render_template("management/crd_flags.html", form_login=form_login, form=form, cadastrado=False, desativada=False, flags=flags, usuario=current_user)
    else:
        abort(403)

@management.route('/crd-flag/desativar/<id>', methods=["GET", "POST"])
@login_required
def desativar_flag(id):
    permissoes = current_user.getPermissoes()
    if("CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        form = CadastrarFlagForm(request.form)
        flag = db.session.query(Flag).filter_by(id=id).first()
        flag.ativa = False
        db.session.flush()
        db.session.commit()
        flags = db.session.query(Flag).filter_by(ativa=True).all()
        return render_template("management/crd_flags.html", form_login=form_login, form=form, cadastrado=False,
                        desativada=True, flags=flags, usuario=current_user)
    else:
        abort(403)