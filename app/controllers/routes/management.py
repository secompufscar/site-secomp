from random import SystemRandom

from flask import render_template, request, redirect, abort, url_for, Blueprint
from flask_login import login_required, current_user

from app.controllers.forms.forms import *
from app.models.models import *
from app.controllers.functions.dictionaries import *
from app.controllers.functions.helpers import *
from app.controllers.functions.email import *
from app.controllers.forms.validators import *

from secrets import token_urlsafe

from app.controllers.forms.options import *
import uuid

management = Blueprint('management', __name__, static_folder='static',
                       template_folder='templates', url_prefix='/gerenciar')


@management.route('/')
@login_required
def gerenciar():
    if possui_permissao(current_user) or current_user.is_admin():
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
        participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
        form_login = LoginForm(request.form)
        camisetas = db.session.query(Camiseta)
        return render_template('management/controle_camisetas.html', camisetas=camisetas, usuario=current_user, participante=participante, form_login=form_login)
    else:
        abort(403)


@management.route('/estoque-camisetas/<tamanho>')
@login_required
def estoque_camisetas_por_tamanho(tamanho):
    permissoes = current_user.getPermissoes()
    if("ALTERAR_CAMISETAS" in permissoes or current_user.is_admin()):
        participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
        form_login = LoginForm(request.form)
        camisetas = db.session.query(Camiseta).filter_by(tamanho=tamanho)
        return render_template('management/controle_camisetas.html', camisetas=camisetas, usuario=current_user, participante=participante, form_login=form_login)
    else:
        abort(403)


@management.route('/cadastro-patrocinador', methods=['POST', 'GET'])
@login_required
def cadastro_patrocinador():
    permissoes = current_user.getPermissoes()
    if("CADASTRAR_PATROCINADOR" in permissoes or current_user.is_admin()):
        participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
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
            return render_template('management/cadastro_patrocinador.html', usuario=current_user, participante=participante, form=form, form_login=form_login)
    else:
        abort(403)


@management.route('/venda-kits', methods=['POST', 'GET'])
@login_required
def vender_kits():
    permissoes = current_user.getPermissoes()
    meu_participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
    if("VENDA_PRESENCIAL" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        form = VendaKitForm(request.form)
        form.participante.choices = get_participantes()
        form.camiseta.choices = get_opcoes_camisetas()
        if form.validate_on_submit() and form.participante.data is not None:
            camiseta = db.session.query(Camiseta).filter_by(id=form.camiseta.data).first()
            participante = db.session.query(Participante).filter_by(id=form.participante.data).first()
            if camiseta.quantidade_restante > 0:
                valor = form.valor.data
                pagamento = Pagamento(id_participante=participante.id, descricao="Kit", valor=valor,
                efetuado=True, metodo_pagamento='Presencial')
                pagamento.id_camiseta = form.camiseta.data
                participante.pagamentos.append(pagamento)
                if camiseta.quantidade_restante > 0:
                    camiseta.quantidade_restante = camiseta.quantidade_restante - 1
                participante.opcao_coffee = form.restricao_coffee.data
                alerta = "Compra de " + participante.usuario.primeiro_nome + " " + participante.usuario.sobrenome \
                         + " realizada com sucesso! R$ " + str(valor) + ". Camiseta: " + camiseta.tamanho + \
                         " e restrição alimentar: " + get_nome_restricao(participante.opcao_coffee)
                db.session.add(camiseta)
                db.session.add(participante)
                db.session.commit()
                return render_template('management/venda_de_kits.html', alerta=alerta,
                                       form=form, form_login=form_login, usuario=current_user, participante=meu_participante)
            elif camiseta.quantidade_restante == 0:
                return render_template('management/venda_de_kits.html', alerta="Sem estoque para " + camiseta.tamanho,
                                       form=form, form_login=form_login, usuario=current_user, participante=meu_participante)
        return render_template('management/venda_de_kits.html', alerta="Preencha o formulário abaixo",
                               form=form, form_login=form_login, usuario=current_user, participante=meu_participante)
    else:
        abort(403)

@management.route('/sorteio')
@login_required
def sorteia_usuario():
    permissoes = current_user.getPermissoes()
    if("SORTEAR" in permissoes or current_user.is_admin()):
        participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
        form_login = LoginForm(request.form)
        return render_template('management/sortear_usuario.html', usuario=current_user, participante=participante, sorteando=False, form_login=form_login)
    else:
        abort(403)

@management.route('/sorteio/sortear', methods=["POST"])
@login_required
def sortear():
    permissoes = current_user.getPermissoes()
    if("SORTEAR" in permissoes or current_user.is_admin()):
        participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
        form_login = LoginForm(request.form)
        sorteado = db.session.query(Participante)
        sorteado = sorteado[SystemRandom().randint(1, sorteado.count()) - 1]
        return render_template('management/sortear_usuario.html', usuario=current_user, participante=participante, sorteado=sorteado, sorteando=True, form_login=form_login)
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
                antiga = db.session.query(Pagamento).filter_by(efetuado=True, cancelado=False, rejeitado=False, id_participante=participante.id).first()
                camiseta_antiga = db.session.query(Camiseta).filter_by(antiga.id_camiseta).first()
                camiseta_antiga.quantidade_restante = camiseta_antiga.quantidade_restante + 1
                camiseta.quantidade_restante = camiseta.quantidade_restante - 1
                participante.id_camiseta = camiseta.id
                db.session.add(camiseta_antiga)
                db.session.add(camiseta)
                db.session.add(participante)
                db.session.commit()
                return render_template('management/alterar_camisetas.html', participante=participante, camiseta=camiseta,
                                       sucesso='s', form=form, form_login=form_login, usuario=current_user)
            else:
                return render_template('management/alterar_camisetas.html', participante=participante, camiseta=camiseta,
                                       sucesso='n', form=form, form_login=form_login, usuario=current_user)
        return render_template('management/alterar_camisetas.html', form=form, form_login=form_login, usuario=current_user)
    else:
        abort(403)

@management.route('/listas', methods=["GET", "POST"])
@login_required
def listas():
    permissoes = current_user.getPermissoes()
    if("GERAR_LISTAS" in permissoes or current_user.is_admin()):
        participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
        form_login = LoginForm(request.form)
        form = ListasParticipantes(request.form)
        if(form.validate_on_submit()):
            if(form.tipo.data == 0):
                atividade = db.session.query(Atividade).get(form.atividades.data)
                lista = atividade.participantes
                return render_template('management/listas_participante.html',  atividade=atividade.titulo + ' - ' + atividade.tipo.nome,
                                        tipo='inscritos', lista=lista, form=form, form_login=form_login,
                                        usuario=current_user, participante=participante)
            elif(form.tipo.data == 1):
                atividade = db.session.query(Atividade).get(form.atividades.data)
                lista = atividade.presencas
                return render_template('management/listas_participante.html', atividade=atividade.titulo + ' - ' + atividade.tipo.nome,
                                        tipo='presentes', lista=lista, form=form, form_login=form_login,
                                        usuario=current_user, participante=participante)
        else:
            return render_template('management/listas_participante.html', form=form, form_login=form_login,
                                   usuario=current_user, participante=participante)
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
    if("CONTEUDO" in permissoes or "PATROCINIO" in permissoes or current_user.is_admin()):
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
                        atividade_removida.ministrantes.clear()
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
                            usuario = Usuario(email=email)
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
        return render_template("management/gerar_url_conteudo.html", form=form, dict_urls=get_urls_conteudo(request.url_root), form_login=form_login, url_root=request.url_root, usuario=current_user)
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

@management.route('/add-pontuacao', methods=["GET", "POST"])
@login_required
def add_pontuacao():
    permissoes = current_user.getPermissoes()
    if("CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        form = PontuacaoNaMaoForm(request.form)
        if form.validate_on_submit():
            nome_flag = "pontuacao_add_na_mao_" + str(len(db.session.query(Flag).all()))
            flag = Flag(codigo=nome_flag, pontos=form.pontuacao.data, ativa=False)
            db.session.add(flag)
            db.session.flush()
            db.session.commit()
            part = db.session.query(Participante).filter_by(id=int(form.participante.data)).first()
            part.pontuacao += flag.pontos
            part.flags_encontradas.append(flag)
            db.session.add(part)
            db.session.flush()
            db.session.commit()
            return render_template("management/add_pont.html", ult_day=True, form_login=form_login, form=form, sucesso=True, usuario=current_user)
        else:
            return render_template("management/add_pont.html", ult_day=True, form_login=form_login, form=form, usuario=current_user)
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

@management.route('/gerenciar-comprovantes', methods=['POST', 'GET'])
@login_required
def gerenciar_comprovantes():
    permissoes = current_user.getPermissoes()
    if("GERENCIAR_COMPROVANTES" in permissoes or current_user.is_admin()):
        participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
        form_login = LoginForm(request.form)
        form = GerenciarComprovantesForm(request.form)
        if form.validate_on_submit():
            if esta_preenchido(form.aprovar.data) and not esta_preenchido(form.desaprovar.data) and not esta_preenchido(form.rejeitar.data):
                pagamento = db.session.query(Pagamento).get(int(form.aprovar.data))
                if pagamento.efetuado is not True and pagamento.metodo_pagamento == 'Comprovante':
                    if pagamento.rejeitado is not True:
                        if pagamento.camiseta.quantidade_restante > 0:
                            pagamento.camiseta.quantidade_restante = pagamento.camiseta.quantidade_restante - 1
                        pagamento.efetuado = True
                        db.session.add(pagamento)
                        db.session.commit()
                        enviar_email_aviso_pagamento_kit_aprovado(pagamento.participante.usuario)

            elif esta_preenchido(form.desaprovar.data) and not esta_preenchido(form.aprovar.data) and not esta_preenchido(form.rejeitar.data) and not esta_preenchido(form.autorizar.data):
                pagamento = db.session.query(Pagamento).get(int(form.desaprovar.data))
                if pagamento.efetuado is not False and pagamento.metodo_pagamento == 'Comprovante':
                    if pagamento.rejeitado is not True:
                        pagamento.camiseta.quantidade_restante = pagamento.camiseta.quantidade_restante + 1
                        pagamento.efetuado = False
                        db.session.add(pagamento)
                        db.session.commit()

            elif esta_preenchido(form.rejeitar.data) and not esta_preenchido(form.aprovar.data) and not esta_preenchido(form.desaprovar.data)and not esta_preenchido(form.autorizar.data):
                pagamento = db.session.query(Pagamento).get(int(form.rejeitar.data))
                if pagamento.rejeitado is not True and pagamento.metodo_pagamento == 'Comprovante':
                    pagamento.camiseta.quantidade_restante = pagamento.camiseta.quantidade_restante + 1
                    pagamento.rejeitado = True
                    db.session.add(pagamento)
                    db.session.commit()
                    enviar_email_aviso_pagamento_kit_rejeitado(pagamento.participante.usuario)

            elif esta_preenchido(form.autorizar.data) and not esta_preenchido(form.rejeitar.data) and not esta_preenchido(form.aprovar.data) and not esta_preenchido(form.desaprovar.data):
                pagamento = db.session.query(Pagamento).get(int(form.autorizar.data))
                if pagamento.rejeitado is not False and pagamento.metodo_pagamento == 'Comprovante':
                    if pagamento.camiseta.quantidade_restante > 0:
                        pagamento.camiseta.quantidade_restante = pagamento.camiseta.quantidade_restante - 1
                    pagamento.rejeitado = False
                    db.session.add(pagamento)
                    db.session.commit()
        return render_template('management/gerenciar_comprovantes.html', form=form, participante=participante, usuario=current_user, form_login=form_login, pagamentos=get_info_usuarios_envio_comprovante())
    else:
        abort(403)

@management.route('/cadastro-presencial-participante', methods=['POST', 'GET'])
@login_required
def cadastro_presencial_participante():
    if "CREDENCIAMENTO" in current_user.getPermissoes() or "ADMIN" in current_user.getPermissoes() or current_user.is_admin():
        form_login = LoginForm(request.form)
        form = CadastroPresencialParticipanteForm(request.form)
        meu_participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
        form.usuario.choices = get_usuarios_inscricao_pendente()
        if form.validate_on_submit():
            agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            participante = Participante(id_usuario=form.usuario.data, id_evento=get_id_evento_atual(), data_inscricao=agora, credenciado=False, opcao_coffee=0,
                            uuid=str(uuid.uuid1()))
            db.session.add(participante)
            db.session.commit()
            if form.confirmar_email.data == 1:
                participante.usuario.email_verificado = True
                db.session.commit()
            alerta = "Participante " + str(participante.usuario.primeiro_nome) + ' ' + str(participante.usuario.sobrenome) + ' <' + str(participante.usuario.email) + '> inscrito com sucesso!'
            form.usuario.choices = get_usuarios_inscricao_pendente()
            return render_template('management/cadastro_participante_presencial.html', alerta=alerta,
                                   form=form, form_login=form_login, usuario=current_user, participante=meu_participante)
        return render_template('management/cadastro_participante_presencial.html', form=form, form_login=form_login,
                               usuario=current_user, participante=meu_participante, alerta=None)
    abort(403)

