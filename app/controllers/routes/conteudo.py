from os import path, makedirs
import hashlib
from bcrypt import gensalt, hashpw
from flask import request, redirect, flash, Blueprint, current_app, abort
from flask_login import login_required, login_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from passlib.hash import pbkdf2_sha256
from app.controllers.forms.forms import *
from app.controllers.functions.email import *
from app.controllers.functions.helpers import *
from app.models.models import *
from flask_wtf import FlaskForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug import secure_filename
limiter = Limiter(current_app, key_func=get_remote_address)


conteudo = Blueprint('conteudo', __name__, static_folder='static',
                  template_folder='templates', url_prefix='/area-conteudo')

@limiter.limit("20/day")
@conteudo.route('/cadastro-ministrante/<codigo>', methods=['POST', 'GET'])
def cadastro_ministrante(codigo):
    form_login = LoginForm(request.form)
    r = valida_url_codigo(None, codigo)
    permitido, emails = r[0], r[2]
    if(permitido == True):
        form = CadastroMinistranteForm()
        form.codigo_url = codigo
        if form.validate_on_submit() and form.email.data in emails:
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            email = form.email.data
            salt = gensalt().decode('utf-8')
            token = serializer.dumps(email, salt=salt)
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hash = pbkdf2_sha256.encrypt(form.senha.data, rounds=10000, salt_size=15)
            permissao_ministrante = db.session.query(Permissao).filter_by(nome="MINISTRANTE").first()

            usuario = db.session.query(Usuario).filter_by(email=form.email.data).first()
            ministrante = usuario.ministrante

            if permissao_ministrante is not None:
                usuario.permissoes_usuario.append(permissao_ministrante)

            usuario.email = form.email.data
            usuario.senha = hash
            usuario.ultimo_login = agora
            usuario.data_cadastro = agora
            usuario.primeiro_nome = form.primeiro_nome.data
            usuario.sobrenome = form.sobrenome.data
            usuario.data_nascimento = form.data_nascimento.data
            usuario.token_email = token
            usuario.autenticado = True
            usuario.salt = salt

            db.session.add(usuario)
            db.session.commit()

            if form.foto.data:
                foto = form.foto.data
                filename = secure_filename(foto.filename)
                filename = f'{usuario.id}_{usuario.primeiro_nome}_{usuario.sobrenome}_{filename}'
                upload_path = path.join(current_app.config['UPLOAD_FOLDER'], 'fotos_ministrantes')
                if not path.exists(upload_path):
                    makedirs(upload_path)

            ministrante.id_usuario = usuario.id
            ministrante.telefone = form.telefone.data
            ministrante.profissao = form.profissao.data
            ministrante.empresa_universidade = form.empresa_universidade.data
            ministrante.biografia = form.biografia.data
            if form.foto.data:
                ministrante.foto = filename
            ministrante.tamanho_camiseta = form.tamanho_camiseta.data
            ministrante.facebook = form.facebook.data
            ministrante.twitter = form.twitter.data
            ministrante.linkedin = form.linkedin.data
            ministrante.github = form.github.data

            db.session.add(ministrante)
            db.session.commit()
            if form.foto.data:
                foto.save(path.join(upload_path, filename))
            enviar_email_confirmacao(usuario, token)
            login_user(usuario, remember=True)
            return redirect(url_for('users.verificar_email'))
        return render_template("conteudo/cadastro_ministrante.html", form=form, codigo=codigo, form_login=form_login)
    else:
        abort(404)

@limiter.limit("20/day")
@conteudo.route('/dados-hospedagem-transporte/', methods=['POST', 'GET'])
@login_required
def dados_hospedagem_transporte():
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        atividade_confirmada, atividade, view_atividade = confirmacao_atividade_ministrante(current_user)
        dados_hospedagem_transporte = db.session.query(DadosHospedagemTransporte).filter_by(id_evento=get_id_evento_atual(), id_ministrante=current_user.ministrante.id).first()
        if dados_hospedagem_transporte is not None and atividade_confirmada == False:
            return redirect(url_for('conteudo.' + view_atividade, codigo=atividade.url_codigo))
        form = CadastroInformacoesLocomocaoEstadia(request.form)
        if form.validate_on_submit():
            dados_hospedagem_transporte = DadosHospedagemTransporte(id_evento=get_id_evento_atual(), cidade_origem=form.cidade_origem.data,
            data_chegada_origem=form.data_chegada_sanca.data, data_chegada_partida=form.data_partida_sanca.data,
            transporte_ida_volta=form.transporte_ida_volta.data, opcoes_transporte_ida_volta=str(form.opcoes_transporte_ida_volta.data),
            transporte_sanca=form.transporte_sanca.data, opcoes_transporte_sanca=str(form.opcoes_transporte_sanca.data),
            hospedagem=form.hospedagem.data, necessidades_hospedagem=form.necessidades_hospedagem.data, observacoes=form.observacoes.data)
            current_user.ministrante.dados_hospedagem_transporte.append(dados_hospedagem_transporte)
            db.session.add(dados_hospedagem_transporte)
            db.session.add(current_user)
            db.session.commit()
            print(atividade.url_codigo)
            return redirect(url_for('conteudo.' + view_atividade, codigo=atividade.url_codigo))
        return render_template("conteudo/dados_hospedagem_transporte.html", form=form, form_login=form_login)
    abort(404)


@limiter.limit("20/day")
@conteudo.route('/cadastro-atividade/minicurso/<codigo>', methods=['POST', 'GET'])
@login_required
def cadastro_minicurso(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm()
        permitido, atividade, emails = valida_url_codigo(current_user, codigo)
        ministrante = current_user.ministrante
        if permitido == True:
            r_atividade_ministrante = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
            if r_atividade_ministrante.admin_atividade is not False:
                form = CadastroInformacoesMinicurso()
                if form.validate_on_submit():

                    ae_filename = None
                    m_filename = None

                    if form.apresentacao_extra.data:
                        apresentacao_extra = form.apresentacao_extra.data
                        ae_filename = secure_filename(apresentacao_extra.filename)
                        ae_filename = f'{current_user.id}_{current_user.primeiro_nome}_{current_user.sobrenome}_{ae_filename}'
                        ae_path = path.join(current_app.config['UPLOAD_FOLDER'], 'minicursos/apresentacoes_extra')
                        if not path.exists(ae_path):
                            makedirs(ae_path)

                    if form.material.data:
                        material = form.material.data
                        m_filename = secure_filename(material.filename)
                        m_filename = f'{current_user.id}_{current_user.primeiro_nome}_{current_user.sobrenome}_{m_filename}'
                        m_path = path.join(current_app.config['UPLOAD_FOLDER'], 'minicursos/materiais')
                        if not path.exists(m_path):
                            makedirs(m_path)

                    info_minicurso = InfoMinicurso(pre_requisitos=form.pre_requisitos.data, planejamento=form.planejamento.data,
                                                    apresentacao_extra=ae_filename, material=m_filename,
                                                    requisitos_hardware=form.requisitos_hardware.data, requisitos_ide=form.requisitos_ide.data,
                                                    requisitos_bibliotecas_pacotes=form.requisitos_bibliotecas_pacotes.data,
                                                    requisitos_dependencias=form.requisitos_dependencias.data, requisitos_sistema=form.requisitos_sistema.data,
                                                    requisitos_observacoes=form.requisitos_observacoes.data, requisitos_github=form.requisitos_github.data,
                                                    dicas_instalacao=form.dicas_instalacao.data)
                    for ministrante in atividade.ministrantes:
                        r = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
                        r.admin_atividade = False
                        db.session.add(r)
                        db.session.commit()
                    r_atividade_ministrante = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
                    r_atividade_ministrante.confirmado = True
                    r_atividade_ministrante.admin_atividade = True
                    atividade.titulo = form.titulo.data
                    for id in form.area.data:
                        atividade.areas.append(db.session.query(AreaAtividade).get(id))
                    atividade.descricao = form.descricao.data
                    atividade.observacoes = form.observacoes.data
                    atividade.info_minicurso.append(info_minicurso)
                    db.session.add(r_atividade_ministrante)
                    db.session.add(info_minicurso)
                    db.session.add(atividade)
                    db.session.commit()
                    if form.apresentacao_extra.data:
                        apresentacao_extra.save(path.join(ae_path, ae_filename))
                    if form.material.data:
                        material.save(path.join(m_path, m_filename))
                    return redirect(url_for('users.dashboard'))
                return render_template('conteudo/cadastro_minicurso.html', form=form, codigo=codigo, form_login=form_login)
            else:
                return redirect(url_for('conteudo.confirmar_atividade', codigo=codigo))
    abort(404)

@limiter.limit("20/day")
@conteudo.route('/cadastro-atividade/palestra/<codigo>', methods=['POST', 'GET'])
@login_required
def cadastro_palestra(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        permitido, atividade, emails = valida_url_codigo(current_user, codigo)
        ministrante = current_user.ministrante
        if permitido == True:
            r_atividade_ministrante = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
            if r_atividade_ministrante.admin_atividade is not False:
                form = CadastroInformacoesPalestra()
                if form.validate_on_submit():

                    m_filename = None

                    if form.material.data:
                        material = form.material.data
                        m_filename = secure_filename(material.filename)
                        m_filename = f'{current_user.id}_{current_user.primeiro_nome}_{current_user.sobrenome}_{m_filename}'
                        m_path = path.join(current_app.config['UPLOAD_FOLDER'], 'palestras/materiais')
                        if not path.exists(m_path):
                            makedirs(m_path)

                    info_palestra = InfoPalestra(requisitos_tecnicos=form.requisitos_tecnicos.data, planejamento=form.planejamento.data,
                                                apresentacao_extra=form.apresentacao_extra.data, material=m_filename,
                                                perguntas=form.perguntas.data)
                    for ministrante in atividade.ministrantes:
                        r = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
                        r.admin_atividade = False
                        db.session.add(r)
                        db.session.commit()
                    r_atividade_ministrante.confirmado = True
                    r_atividade_ministrante.admin_atividade = True
                    atividade.titulo = form.titulo.data
                    for id in form.area.data:
                        atividade.areas.append(db.session.query(AreaAtividade).get(id))
                    atividade.descricao = form.descricao.data
                    atividade.observacoes = form.observacoes.data
                    atividade.info_palestra.append(info_palestra)
                    db.session.add(r_atividade_ministrante)
                    db.session.add(info_palestra)
                    db.session.add(atividade)
                    db.session.commit()
                    if form.material.data:
                        material.save(path.join(m_path, m_filename))
                    return redirect(url_for('users.dashboard'))
                return render_template('conteudo/cadastro_palestra.html', form=form, codigo=codigo, form_login=form_login)
            else:
                return redirect(url_for('conteudo.confirmar_atividade', codigo=codigo))
    abort(404)

@conteudo.route('/cadastro-atividade/mesa-redonda/<codigo>', methods=['POST', 'GET'])
@login_required
def cadastro_mesa_redonda(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        permitido, atividade, emails = valida_url_codigo(current_user, codigo)
        form = CadastroAtividadeGenerica(request.form)
        if form.validate_on_submit():
            for ministrante in atividade.ministrantes:
                r = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
                r.admin_atividade = False
                db.session.add(r)
                db.session.commit()
            atividade.titulo = form.titulo.data
            for id in form.area.data:
                atividade.areas.append(db.session.query(AreaAtividade).get(id))
            atividade.descricao = form.descricao.data
            atividade.observacoes = form.observacoes.data
            db.session.add(atividade)
            db.session.commit()
            return redirect(url_for('users.dashboard'))
        return render_template('conteudo/cadastro_mesa_redonda.html', codigo=codigo, form=form, form_login=form_login)
    else:
        return redirect(url_for('conteudo.confirmar_atividade', codigo=codigo))
    abort(404)

@conteudo.route('/cadastro-atividade/feira-projetos/<codigo>', methods=['POST', 'GET'])
@login_required
def cadastro_feira_projetos(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        permitido, atividade, emails = valida_url_codigo(current_user, codigo)
        ministrante = current_user.ministrante
        if(permitido == True):
            r_atividade_ministrante = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
            if r_atividade_ministrante.admin_atividade is not False:
                form = CadastroFeiraDeProjetos(request.form)
                if form.validate_on_submit():
                    info_feira_de_projetos = InfoFeiraDeProjetos(necessidades=form.necessidades.data, planejamento=form.planejamento.data)
                    for ministrante in atividade.ministrantes:
                        r = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
                        r.admin_atividade = False
                        db.session.add(r)
                        db.session.commit()
                    r_atividade_ministrante.confirmado = True
                    r_atividade_ministrante.admin_atividade = True
                    atividade.titulo = form.titulo.data
                    for id in form.area.data:
                        atividade.areas.append(db.session.query(AreaAtividade).get(id))
                    atividade.descricao = form.descricao.data
                    atividade.observacoes = form.observacoes.data
                    atividade.info_feira_de_projetos.append(info_feira_de_projetos)
                    db.session.add(r_atividade_ministrante)
                    db.session.add(info_feira_de_projetos)
                    db.session.add(atividade)
                    db.session.commit()
                    return redirect(url_for('users.dashboard'))
                return render_template('conteudo/cadastro_feira_projetos.html', codigo=codigo, form=form, form_login=form_login)
            else:
                return redirect(url_for('conteudo.confirmar_atividade', codigo=codigo))
    abort(404)

@limiter.limit("20/day")
@conteudo.route('/confirmar-atividade/<codigo>', methods=['POST', 'GET'])
@login_required
def confirmar_atividade(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        form_login = LoginForm(request.form)
        permitido, atividade, emails = valida_url_codigo(current_user, codigo)
        ministrante = current_user.ministrante
        r_atividade_ministrante = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
        if permitido == True and r_atividade_ministrante.confirmado is not False:
            form = FlaskForm(request.form)
            if form.validate_on_submit():
                confirmar = request.form.getlist('confirmar')[0]
                r_atividade_ministrante.confirmado = bool(confirmar == '1')
                db.session.add(r_atividade_ministrante)
                db.session.commit()
                return redirect(url_for('users.dashboard'))
            return render_template('conteudo/confirmar_atividade.html', codigo=codigo, titulo_atividade=atividade.titulo, form=form, form_login=form_login)
    abort(404)
