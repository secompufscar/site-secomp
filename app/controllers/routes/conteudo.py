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

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(current_app, key_func=get_remote_address)


conteudo = Blueprint('conteudo', __name__, static_folder='static',
                  template_folder='templates', url_prefix='/area-conteudo')

@conteudo.route('/', methods=['POST', 'GET'])
@login_required
def index():
    permissoes = current_user.getPermissoes()
    if("CONTEUDO" in permissoes or current_user.is_admin()):
        return render_template('conteudo/index.html')
    else:
        abort(403)

@limiter.limit("20/day")
@conteudo.route('/cadastro-ministrante/<codigo>', methods=['POST', 'GET'])
def cadastro_ministrante(codigo):
    permitido, atividade, emails = valida_url_codigo(None, codigo)
    if(permitido == True):
        form = CadastroMinistranteForm(request.form)
        form.codigo_url = codigo
        if(form.validate_on_submit() and form.email.data in emails):
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            email = form.email.data
            salt = gensalt().decode('utf-8')
            token = serializer.dumps(email, salt=salt)
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hash = pbkdf2_sha256.encrypt(form.senha.data, rounds=10000, salt_size=15)
            permissao_ministrante = db.session.query(Permissao).filter_by(nome="MINISTRANTE").first()

            usuario = db.session.query(Usuario).filter_by(email=form.email.data).first()
            ministrante = usuario.ministrante[0]

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

            ministrante.id_usuario =  usuario.id
            ministrante.telefone = form.telefone.data
            ministrante.profissao = form.profissao.data
            ministrante.empresa_universidade = form.empresa_universidade.data
            ministrante.biografia = form.biografia.data
            ministrante.foto = form.foto.data
            ministrante.tamanho_camiseta = form.tamanho_camiseta.data
            ministrante.facebook = form.facebook.data
            ministrante.twitter = form.twitter.data
            ministrante.linkedin = form.linkedin.data
            ministrante.github = form.github.data

            db.session.add(ministrante)
            db.session.commit()


            enviar_email_confirmacao(usuario, token)
            login_user(usuario, remember=True)
            return redirect(url_for('users.verificar_email'))
        return render_template("conteudo/cadastro_ministrante.html", form=form, codigo=codigo)
    else:
        abort(404)


@limiter.limit("20/day")
@conteudo.route('/cadastro-atividade/minicurso/<codigo>', methods=['POST', 'GET'])
@login_required
def cadastro_minicurso(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        permitido, atividade, minstrante = valida_url_codigo(current_user, codigo)
        if permitido == True:
            if atividade.titulo == None:
                form = CadastroInformacoesMinicurso(request.form)
                if form.validate_on_submit():
                    info_minicurso = InfoMinicurso(pre_requisitos=form.pre_requisitos.data, planejamento=form.planejamento.data,
                                                    apresentacao_extra=form.apresentacao_extra.data, material=form.material.data,
                                                    requisitos_hardware=form.requisitos_hardware.data, requisitos_software=form.requisitos_software.data,
                                                    dicas_instalacao=form.dicas_instalacao.data)
                    r_atividade_ministrante = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
                    r_atividade_ministrante.confirmado = True
                    atividade.titulo = form.titulo.data
                    atividade.area.append(db.session.query(AreaAtividade).get(form.area.data))
                    atividade.descricao = form.descricao.data
                    atividade.observacoes = form.observacoes.data
                    atividade.info_minicurso.append(info_minicurso)
                    db.session.add(r_atividade_ministrante)
                    db.session.add(info_minicurso)
                    db.session.add(atividade)
                    db.session.commit()
                    return redirect(url_for('user.dashboard'))
                return render_template('conteudo/cadastro_minicurso.html', form=form, codigo=codigo)
            else:
                return redirect(url_for('confirmar_atividade', codigo=codigo))
    abort(403)

@limiter.limit("20/day")
@conteudo.route('/cadastro-atividade/palestra/<codigo>', methods=['POST', 'GET'])
@login_required
def cadastro_palestra(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        permitido, atividade, minstrante = valida_url_codigo(current_user, codigo)
        if permitido == True:
            if atividade.titulo == None:
                form = CadastroInformacoesPalestra(request.form)
                if form.validate_on_submit():
                    info_palestra = InfoPalestra(requisitos_tecnicos=form.requisitos_tecnicos.data, planejamento=form.planejamento.data,
                                                apresentacao_extra=form.apresentacao_extra.data, material=form.material.data,
                                                perguntas=form.perguntas.data)
                    r_atividade_ministrante = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
                    r_atividade_ministrante.confirmado = True
                    atividade.titulo = form.titulo.data
                    atividade.area.append(db.session.query(AreaAtividade).get(form.area.data))
                    atividade.descricao = form.descricao.data
                    atividade.observacoes = form.observacoes.data
                    atividade.info_minicurso.append(info_palestra)
                    db.session.add(r_atividade_ministrante)
                    db.session.add(info_palestra)
                    db.session.add(atividade)
                    db.session.commit()
                    return redirect(url_for('user.dashboard'))
                return render_template('conteudo/cadastro_palestra.html', form=form, codigo=codigo)
            else:
                return redirect(url_for('confirmar_atividade', codigo=codigo))
    abort(403)

@conteudo.route('/cadastro-atividade/mesa-redonda/<codigo>', methods=['POST', 'GET'])
@login_required
def cadastro_mesa_redonda(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        permitido, atividade, minstrante = valida_url_codigo(current_user, codigo)
        if(permitido == True):
            return render_template('conteudo/cadastro_mesa_redonda.html', codigo=codigo)
    abort(403)

@conteudo.route('/cadastro-atividade/feira-pesquisas/<codigo>', methods=['POST', 'GET'])
@login_required
def cadastro_feira_pesquisas(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        permitido, atividade, minstrante = valida_url_codigo(current_user, codigo)
        if(permitido == True):
            form = CadastroFeiraDePesquisas(request.form)
            return render_template('conteudo/cadastro_feira_pesquisas.html', form=form, codigo=codigo)
    abort(403)

@limiter.limit("20/day")
@conteudo.route('/confirmar-atividade/<codigo>', methods=['POST', 'GET'])
@login_required
def confirmar_atividade(codigo):
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        permitido, atividade, minstrante = valida_url_codigo(current_user, codigo)
        if permitido == True:
            if atividade.titulo != None:
                atividade_confirmada, dmatter, view_atividade = confirmacao_atividade_ministrante(current_user)
                if atividade_confirmada == False:
                    if form.validate_on_submit():
                        r_atividade_ministrante = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
                        r_atividade_ministrante.confirmado = True
                        db.session.add(r_atividade_ministrante)
                        db.session.commit()
                return redirect(url_for('user.dashboard'))
            else:
                return redirect(url_for('conteudo.' + view_atividade, codigo=codigo))
            return render_template('conteudo/cadastro_feira_pesquisas.html', codigo=codigo)
    abort(403)
