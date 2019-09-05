from os import path, makedirs

from bcrypt import gensalt
from flask import request, redirect, flash, Blueprint, current_app
from flask_login import login_required, login_user, fresh_login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from passlib.hash import pbkdf2_sha256
from werkzeug import secure_filename

from app.controllers.forms.forms import *
from app.controllers.functions.dictionaries import *
from app.controllers.functions.email import *
from app.controllers.functions.helpers import *
from app.models.models import *
from sqlalchemy.orm import aliased
from app.controllers.functions.paypal import *
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
import uuid

limiter = Limiter(current_app, key_func=get_ipaddr)

users = Blueprint('users', __name__, static_folder='static',
                  template_folder='templates', url_prefix='/participante')


def email_verificado_required(func):
    def decorated_view(*args, **kwargs):
        if  not current_user.email_verificado:
            return redirect(url_for('users.verificar_email'))
        return func(*args, **kwargs)
    decorated_view.__name__ = func.__name__
    return decorated_view


@users.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    """
    Renderiza a página de cadastro do projeto
    """
    form_login = LoginForm(request.form)
    form = CadastroForm(request.form)
    form.curso.choices = get_opcoes_cursos()
    form.instituicao.choices = get_opcoes_instituicoes()
    form.cidade.choices = get_opcoes_cidades()
    if form.validate_on_submit():
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = form.email.data
        salt = gensalt().decode('utf-8')
        token = serializer.dumps(email, salt=salt)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hash = pbkdf2_sha256.encrypt(form.senha.data, rounds=10000, salt_size=15)
        usuario = Usuario(email=email, senha=hash, ultimo_login=agora,
                          data_cadastro=agora, primeiro_nome=form.primeiro_nome.data, sobrenome=form.sobrenome.data,
                          id_curso=verifica_outro_escolhido(form.curso, Curso(nome=(form.outro_curso.data))),
                          id_instituicao=verifica_outro_escolhido(form.instituicao,
                                                                  Instituicao(nome=form.outra_instituicao.data)),
                          id_cidade=verifica_outro_escolhido(form.cidade, Cidade(nome=form.outra_cidade.data)),
                          data_nascimento=form.data_nasc.data, token_email=token, autenticado=True, salt=salt)
        como_conheceu = ComoConheceu(usuario=usuario, opcao=form.como_conheceu.data, outro=form.outro_como_conheceu.data)
        db.session.add(usuario)
        db.session.add(como_conheceu)
        db.session.flush()
        db.session.commit()
        enviar_email_confirmacao(usuario, token)
        login_user(usuario, remember=True)
        return redirect(url_for('.verificar_email'))

    return render_template('users/cadastro.html', form=form, form_login=form_login)

@users.route('/verificar-email')
@login_required
def verificar_email():
    form_login = LoginForm(request.form)
    permissoes = current_user.getPermissoes()
    if "MINISTRANTE" in permissoes:
        ministrante = True
    else:
        ministrante = False
    if email_confirmado():
        msg = 'Seu email foi verificado com sucesso!'
        status = True
    else:
        msg = 'Confirme o email de verificação que te enviamos!'
        status = False
    return render_template('users/confirma_email.html', resultado=msg, status=status, ministrante=ministrante, form_login=form_login)

@login_required
@limiter.limit("40/year")
@limiter.limit("20/month")
@limiter.limit("20/day")
@limiter.limit("20/hour")
@limiter.limit("5/minute")
@users.route('/reenviar-email', methods=['POST', 'GET'])
@login_required
def reenviar_email():
    if current_user.email_verificado is not True:
        form_login = LoginForm(request.form)
        form = BaseRecaptchaForm(request.form)
        usuario = current_user
        if form.validate_on_submit():
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            email = current_user.email
            salt = gensalt().decode('utf-8')
            token = serializer.dumps(email, salt=salt)
            usuario.token_email = token
            usuario.salt = salt
            db.session.add(usuario)
            db.session.commit()
            enviar_email_confirmacao(usuario, token)
            return render_template('users/email_reenviado.html', form_login=form_login, usuario=usuario)
        return render_template('users/reenviar_email.html', form_login=form_login, usuario=usuario, form=form)
    else:
        return redirect(url_for('users.verificar_email'))


@users.route('/cadastro-participante', methods=['POST', 'GET'])
@login_required
def cadastro_participante():
    try:
        id_evento = db.session.query(Evento).filter_by(edicao=EDICAO_ATUAL).first().id
        if current_user.email_verificado:
            participante = db.session.query(Participante).filter_by(id_usuario=current_user.id, id_evento=id_evento).first()
            if participante is None:
                form = ParticipanteForm(request.form)
                participante = db.session.query(Participante).filter_by(id_usuario=current_user.id, id_evento=id_evento).first()
                if form.validate_on_submit() and participante is None:
                    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    participante = Participante(id_usuario=current_user.id, id_evento=id_evento, data_inscricao=agora, credenciado=False, opcao_coffee=0,
                                    uuid=str(uuid.uuid1()))
                    db.session.add(participante)
                    db.session.flush()
                    db.session.commit()
                    return redirect(url_for('.comprar_kit'))
                else:
                    return render_template('users/cadastro_participante.html', form=form, usuario=current_user)
            else:
                return redirect(url_for('.dashboard'))
        else:
            return redirect(url_for('.verificar_email'))
    except SQLAlchemyError:
        db.session.rollback()
        return redirect(url_for('.dashboard'))


@users.route('/alterar-dados-usuario', methods=['POST', 'GET'])
@login_required
def alterar_usuario():
    usuario = db.session.query(Usuario).filter_by(id=current_user.id).first()
    form = EdicaoUsuarioForm(request.form)
    if form.validate_on_submit() and request.method == 'POST':
        usuario.primeiro_nome = form.primeiro_nome.data
        usuario.sobrenome = form.sobrenome.data
        usuario.id_curso = verifica_outro_escolhido(form.curso, Curso(nome=(form.outro_curso.data)))
        usuario.id_instituicao = verifica_outro_escolhido(form.instituicao, Instituicao(nome=form.outra_instituicao.data))
        usuario.id_cidade = verifica_outro_escolhido(form.cidade, Cidade(nome=form.outra_cidade.data))
        usuario.data_nascimento = form.data_nasc.data
        db.session.flush()
        db.session.commit()
        return redirect(url_for('.dashboard'))
    else:
        form.primeiro_nome.data = usuario.primeiro_nome
        form.sobrenome.data = usuario.sobrenome
        form.curso.data = usuario.id_curso
        form.instituicao.data = usuario.id_instituicao
        form.cidade.data = usuario.id_cidade
        form.data_nasc.data = usuario.data_nascimento
        return render_template('users/alterar_usuario.html', usuario=current_user, form=form)


@users.route('/dashboard', methods=['POST', 'GET'])
@login_required
@email_verificado_required
def dashboard():
    if email_confirmado():
        participante = db.session.query(Participante).filter_by(
            usuario=current_user).first()
        return render_template('users/dashboard_usuario.html', title='Dashboard', usuario=current_user, participante=participante)
    else:
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('.verificar_email'))


@users.route('/wifi-visitante', methods=['POST', 'GET'])
@login_required
@email_verificado_required
def cadastro_wifi():
    if current_user.participante:
        form = WifiForm(request.form)
        if form.validate_on_submit():
            data = { 'cpf': form.cpf.data,
                     'nome': form.nome.data,
                     'email': form.email.data }
            res = cadastrar_wifi_visitante(data)
            if res:
                flash("Usuário cadastrado com sucesso na rede WIFI-VISITANTE!")
                current_user.wifi = True
                return redirect(url_for('.dashboard'))
            flash("Um ou mais campos não foram preenchidos corretamente.")
        return render_template('users/wifi_visitante.html', title='Cadastrar no WIFI-VISITANTE', form=form, cadastrado=current_user.participante.wifi)
    else:
        flash("Faça sua inscrição na SECOMP para poder se cadastrar no WIFI-VISITANTE!")
        return redirect(url_for('.cadastro_participante'))


@users.route('/dados', methods=['POST', 'GET'])
@login_required
def dados():
    usuario = db.session.query(Usuario).filter_by(
        id=current_user.id).first()
    return render_template('users/dados.html', title='Dados Pessoais', usuario=usuario,
                            participante = db.session.query(Participante).filter_by(usuario=current_user).first())


@users.route('/dados-participante', methods=['POST', 'GET'])
@login_required
def dados_participante():
    usuario = db.session.query(Usuario).filter_by(
        id=current_user.id).first()
    participante = db.session.query(Participante).filter_by(
        usuario=current_user).first()
    if participante is not None:
        restricao_alimentar = get_nome_restricao(participante.opcao_coffee)
    else:
        restricao_alimentar = ''
    ministrante = db.session.query(Ministrante).filter_by(
        usuario=current_user).first()
    return render_template('users/dados_participante.html', title='Dados de Participante', usuario=usuario,
                            participante=participante, ministrante=ministrante, restricao_alimentar=restricao_alimentar)

@login_required
@limiter.limit("500/year")
@limiter.limit("50/month")
@limiter.limit("20/day")
@limiter.limit("20/hour")
@limiter.limit("1/minute")
@users.route('/verificacao/<token>')
def verificacao(token):
    """
    Página do link enviado para o usuário
    """
    form_login = LoginForm(request.form)
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # Acha o usuário que possui o token
        user = db.session.query(Usuario).filter_by(token_email=token).first()
        salt = user.salt
        # Gera um email a partir do token do link e do salt do db
        email = serializer.loads(token, salt=salt, max_age=43200)
        user.email = email
        # Valida o email
        user.email_verificado = True
        db.session.add(user)
        db.session.commit()
    # Tempo definido no max_age
    except SignatureExpired:
        user = db.session.query(Usuario).filter_by(token_email=token).first()
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        salt = gensalt().decode('utf-8')
        user.salt = salt
        token = serializer.dumps(user.email, salt=salt)
        user.token_email = token
        db.session.add(user)
        db.session.commit()
        enviar_email_confirmacao(user, token)
        return redirect(url_for('.reenvio_confirmacao_email'))
    except Exception as e:
        print(e)
        return redirect(url_for('.erro_confirmacao_email'))
    return redirect(url_for('.verificar_email'))

@users.route('/reenvio-confirmacao-email')
def reenvio_confirmacao_email():
    form_login = LoginForm(request.form)
    return render_template('users/reenvio_confirmacao_email.html', form_login=form_login)

@users.route('/erro-confirmacao-email')
def erro_confirmacao_email():
    form_login = LoginForm(request.form)
    return render_template('users/erro_confirmacao_email.html', form_login=form_login)

@users.route('/inscricao-minicursos')
@login_required
@email_verificado_required
def inscricao_minicursos():
    agora = datetime.now()
    evento_atual = db.session.query(Evento).filter_by(edicao=EDICAO_ATUAL).first()
    participante = db.session.query(Participante).filter_by(usuario=current_user).first()
    if agora >= evento_atual.abertura_minicursos_1_etapa and agora <= evento_atual.fechamento_minicursos_1_etapa\
            or agora >= evento_atual.abertura_minicursos_2_etapa and agora <= evento_atual.fechamento_minicursos_2_etapa:
        tipo_atividade = get_tipos_atividade()
        minicursos = db.session.query(Atividade).filter_by(
            tipo=tipo_atividade['minicurso'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)
        return render_template('users/inscricao_minicursos.html',
                               participante=participante, usuario=current_user, minicursos=minicursos,
                               inscricao_liberada=1)
    else:
        return render_template('users/inscricao_minicursos.html',
                               participante=participante, usuario=current_user, inscricao_liberada=0)


#@users.route('/inscricao-workshops')
@login_required
@email_verificado_required
def inscricao_workshops():
    tipo_atividade = get_tipos_atividade()
    workshops = db.session.query(Atividade).filter_by(
        tipo=tipo_atividade['workshop'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)
    return render_template('users/inscricao_workshops.html',
                           participante=db.session.query(Participante).filter_by(
                               usuario=current_user).first(), usuario=current_user, workshops=workshops)


@users.route('/inscricao-minicursos/<filtro>')
@login_required
@email_verificado_required
def inscricao_minicursos_com_filtro(filtro):
    agora = datetime.now()
    evento_atual = db.session.query(Evento).filter_by(edicao=EDICAO_ATUAL).first()
    participante = db.session.query(Participante).filter_by(usuario=current_user).first()
    if agora >= evento_atual.abertura_minicursos_1_etapa and agora <= evento_atual.fechamento_minicursos_1_etapa:
        tipo_atividade = get_tipos_atividade()
        minicursos = db.session.query(Atividade).filter(
            Atividade.tipo == tipo_atividade['minicurso'], Atividade.titulo.like("%" + filtro + "%"),
            Atividade.id_evento == get_id_evento_atual(), Atividade.titulo!=None)

        return render_template('users/inscricao_minicursos.html',
                               participante=participante, usuario=current_user, minicursos=minicursos,
                               inscricao_liberada=1)
    else:
        return render_template('users/inscricao_minicursos.html',
                               participante=participante, usuario=current_user,
                               inscricao_liberada=0)


#@users.route('/inscricao-workshops/<filtro>')
@login_required
@email_verificado_required
def inscricao_workshops_com_filtro(filtro):
    tipo_atividade = get_tipos_atividade()
    workshops = db.session.query(Atividade).filter(
        Atividade.tipo == tipo_atividade['workshop'], Atividade.titulo.like("%" + filtro + "%"),
        Atividade.id_evento==get_id_evento_atual(), Atividade.titulo!=None)

    return render_template('users/inscricao_workshops.html',
                           participante=db.session.query(Participante).filter_by(
                               usuario=current_user).first(),
                           usuario=current_user, workshops=workshops)


@users.route('/inscrever-minicurso/<id>')
@login_required
@email_verificado_required
def inscrever_minicurso(id):
    tipo_atividade = get_tipos_atividade()
    atv = db.session.query(Atividade).filter_by(id=id).first()
    participante = db.session.query(Participante).filter_by(
        usuario=current_user).first()
    agora = datetime.now()
    evento_atual = db.session.query(Evento).filter_by(edicao=EDICAO_ATUAL).first()
    if atv.vagas_disponiveis > 0:
        if agora >= evento_atual.abertura_minicursos_1_etapa and agora <= evento_atual.fechamento_minicursos_1_etapa:
            if participante.minicurso_etapa_1 is None:
                participante.minicurso_etapa_1 = atv.id
                atv.participantes.append(db.session.query(
                    Participante).filter_by(usuario=current_user).first())
                atv.vagas_disponiveis = atv.vagas_disponiveis - 1
                db.session.flush()
                db.session.commit()
                minicursos = db.session.query(Atividade).filter_by(
                    tipo=tipo_atividade['minicurso'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)

                return render_template('users/inscricao_minicursos.html', participante=participante, usuario=current_user,
                                       minicursos=minicursos, acao="+", inscricao_liberada=1)
            else:
                minicursos = db.session.query(Atividade).filter_by(
                    tipo=tipo_atividade['minicurso'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)
                return render_template('users/inscricao_minicursos.html', participante=participante,
                                       usuario=current_user,
                                       minicursos=minicursos, acao="limite_excedido", inscricao_liberada=1)
        elif agora >= evento_atual.abertura_minicursos_2_etapa and agora <= evento_atual.fechamento_minicursos_2_etapa:
            if participante.minicurso_etapa_2 is None:
                participante.minicurso_etapa_2 = atv.id
                atv.participantes.append(db.session.query(
                    Participante).filter_by(usuario=current_user).first())
                atv.vagas_disponiveis = atv.vagas_disponiveis - 1
                db.session.flush()
                db.session.commit()
                minicursos = db.session.query(Atividade).filter_by(
                tipo=tipo_atividade['minicurso'], id_evento=get_id_evento_atual()).filter(Atividade.titulo!=None)

                return render_template('users/inscricao_minicursos.html', participante=participante, usuario=current_user,
                                        minicursos=minicursos, acao="+", inscricao_liberada=1)
            else:
                minicursos = db.session.query(Atividade).filter_by(
                    tipo=tipo_atividade['minicurso'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)
                return render_template('users/inscricao_minicursos.html', participante=participante,
                                       usuario=current_user,
                                       minicursos=minicursos, acao="limite_excedido",
                                       inscricao_liberada=1)
        else:
            minicursos = db.session.query(Atividade).filter_by(
                tipo=tipo_atividade['minicurso'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)
            return render_template('users/inscricao_minicursos.html', participante=participante,
                                   usuario=current_user,
                                   minicursos=minicursos, acao="inscricao_fechada",
                                   inscricao_liberada=0)
    else:
        minicursos = db.session.query(Atividade).filter_by(
            tipo=tipo_atividade['minicurso'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)
        return render_template('users/inscricao_minicursos.html', participante=participante,
                               usuario=current_user,
                               minicursos=minicursos, acao="vagas_esgotadas",
                               inscricao_liberada=1)


#@users.route('/inscrever-workshop/<id>')
@login_required
@email_verificado_required
def inscrever_workshop(id):
    tipo_atividade = get_tipos_atividade()
    atv = db.session.query(Atividade).filter_by(id=id).first()
    if atv.vagas_disponiveis > 0:
        atv.participantes.append(db.session.query(
            Participante).filter_by(usuario=current_user).first())
        atv.vagas_disponiveis = atv.vagas_disponiveis - 1
        db.session.flush()
        db.session.commit()
        workshops = db.session.query(Atividade).filter_by(
            tipo=tipo_atividade['workshop'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)

        return render_template('users/inscricao_workshops.html',
                               participante=db.session.query(Participante).filter_by(
                                   usuario=current_user).first(),
                               usuario=current_user, workshops=workshops, acao="+")
    else:
        return "Não há vagas disponíveis!"



@users.route('/desinscrever-minicurso/<id>')
@login_required
@email_verificado_required
def desinscrever_minicurso(id):
    tipo_atividade = get_tipos_atividade()
    atv = db.session.query(Atividade).filter_by(id=id).first()
    participante = db.session.query(Participante).filter_by(usuario=current_user).first()
    if participante in atv.participantes:
        if atv.id == participante.minicurso_etapa_1:
            participante.minicurso_etapa_1 = None
        elif atv.id == participante.minicurso_etapa_2:
            participante.minicurso_etapa_2 = None
        atv.participantes.remove(participante)
        atv.vagas_disponiveis = atv.vagas_disponiveis + 1
        db.session.flush()
        db.session.commit()
        minicursos = db.session.query(Atividade).filter_by(
            tipo=tipo_atividade['minicurso'], id_evento=get_id_evento_atual()).filter(Atividade.titulo!=None)
        return render_template('users/inscricao_minicursos.html',
                               participante=db.session.query(Participante).filter_by(
                                   usuario=current_user).first(),
                               usuario=current_user, minicursos=minicursos, acao="-", inscricao_liberada=1)
    else:
        minicursos = db.session.query(Atividade).filter_by(
            tipo=tipo_atividade['minicurso'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)
        return render_template('users/inscricao_minicursos.html',
                               participante=db.session.query(Participante).filter_by(
                                   usuario=current_user).first(),
                               usuario=current_user, minicursos=minicursos, acao="nao_inscrito",
                               inscricao_liberada=1)


#@users.route('/desinscrever-workshop/<id>')
@login_required
@email_verificado_required
def desinscrever_workshop(id):
    tipo_atividade = get_tipos_atividade()
    atv = db.session.query(Atividade).filter_by(id=id).first()
    if db.session.query(Participante).filter_by(usuario=current_user).first() in atv.participantes:
        atv.participantes.remove(db.session.query(
            Participante).filter_by(usuario=current_user).first())
        atv.vagas_disponiveis = atv.vagas_disponiveis + 1
        db.session.flush()
        db.session.commit()
        workshops = db.session.query(Atividade).filter_by(
            tipo=tipo_atividade['workshop'], id_evento=get_id_evento_atual()).filter(Atividade.titulo!=None)
        return render_template('users/inscricao_workshops.html',
                               participante=db.session.query(Participante).filter_by(
                                   usuario=current_user).first(),
                               usuario=current_user, workshops=workshops, acao="-")
    else:
        workshops = db.session.query(Atividade).filter_by(
            tipo=tipo_atividade['workshop'], id_evento=get_id_evento_atual()).filter(Atividade.titulo != None)
        return render_template('users/inscricao_workshops.html',
                               participante=db.session.query(Participante).filter_by(
                                   usuario=current_user).first(),
                               usuario=current_user, workshops=workshops, acao="nao_inscrito")


@users.route('/alterar-senha', methods=["POST", "GET"])
@fresh_login_required
@email_verificado_required
def alterar_senha():
    form_login = LoginForm(request.form)
    form = AlterarSenhaForm(request.form)
    if email_confirmado():
        participante = db.session.query(Participante).filter_by(usuario=current_user).first()
        if form.validate_on_submit():
            usuario = db.session.query(Usuario).filter_by(email=current_user.email).first()
            if pbkdf2_sha256.verify(form.senha_atual.data, usuario.senha):
                nova_senha = pbkdf2_sha256.encrypt(form.nova_senha.data, rounds=10000, salt_size=15)
                usuario.senha = nova_senha
                db.session.add(usuario)
                db.session.commit()
                # Envia e-mail informando ao usuário que a senha foi alterada
                info = {'assunto': 'Alteração de Senha',
                        'nome': current_user.primeiro_nome,
                        'email': current_user.email,
                        'titulo': 'ALTERAÇÃO DE SENHA',
                        'template': 'email/alteracao_senha.html',
                        'footer': 'TI X SECOMP UFSCar'}
                enviar_email_generico(info)
                flash('Senha alterada com sucesso!')
                return redirect(url_for('views.login'))
            else:
                flash('Senha atual incorreta!')
                return render_template('users/alterar_senha.html', form=form, action=request.base_url, form_login=form_login,
                                                                usuario=current_user, participante=participante)
        else:
            return render_template('users/alterar_senha.html', form=form, action=request.base_url, form_login=form_login,
                                    usuario=current_user, participante=participante)
    else:
        flash('Confirme seu e-mail para alterar a senha!')
        return redirect(url_for('.dashboard'))


@users.route('/esqueci-senha', methods=["POST", "GET"])
def esqueci_senha():
    form = AlterarSenhaPorEmailForm(request.form)
    form_login = LoginForm(request.form)
    if form.validate_on_submit():
        usuario = db.session.query(Usuario).filter_by(
            email=form.email.data).first()
        if usuario is not None:
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            salt = gensalt().decode('utf-8')
            token = serializer.dumps(usuario.email, salt=salt)
            usuario.token_alteracao_senha = token
            db.session.add(usuario)
            db.session.commit()
            enviar_email_senha(usuario, token)
            return render_template("users/esqueci_senha.html", status_envio_email=True, form=form, form_login=form_login)
        flash('Este e-mail não está cadastrado no site.')
    return render_template("users/esqueci_senha.html", status_envio_email=False, form=form, form_login=form_login)

@limiter.limit("500/year")
@limiter.limit("50/month")
@limiter.limit("20/day")
@limiter.limit("20/hour")
@limiter.limit("1/minute")
@users.route('/confirmar-alteracao-senha/<token>', methods=["POST", "GET"])
def confirmar_alteracao_senha(token):
    form = AlterarSenhaForm(request.form)
    form_login = LoginForm(request.form)
    if form.validate_on_submit():
        try:
            # Acha o usuário que possui o token
            usuario = db.session.query(Usuario).filter_by(
                token_alteracao_senha=token).first()
            hash = pbkdf2_sha256.encrypt(
                form.nova_senha.data, rounds=10000, salt_size=15)
            usuario.senha = hash
            db.session.add(usuario)
            db.session.commit()
            flash("A senha foi alterada com sucesso!")
        except SignatureExpired:
            flash("O link de confirmação expirou!")
        except Exception as e:
            print(e)
            flash("Falha na confirmação de link do email.")
        return redirect(url_for('views.login'))
    return render_template("users/alterar_senha.html", form=form, action=request.base_url, form_login=form_login, status_envio_email=True)

@users.route('/comprar-kit', methods=["POST", "GET"])
@login_required
@email_verificado_required
def comprar_kit():
    id_evento = db.session.query(Evento).filter_by(
        edicao=EDICAO_ATUAL).first().id
    if current_user.email_verificado is True:
        participante = db.session.query(Participante).filter_by(
            id_usuario=current_user.id, id_evento=id_evento).first()
        if participante is not None:
            form = ComprarKitForm()
            form.camiseta.choices = get_opcoes_camisetas()
            if form.validate_on_submit():
                if form.comprar.data == 1:
                    participante.opcao_coffee = form.restricao_coffee.data
                    db.session.add(participante)
                    db.session.flush()
                    db.session.commit()
                    if form.forma_pagamento.data == 2:
                        pagamento = db.session.query(Pagamento).join(Pagamento.participante).join(aliased(Participante.usuario),
                        Participante.usuario).join(aliased(Usuario), Usuario).filter(Usuario.email == current_user.email,\
                        Pagamento.descricao == "Kit", Pagamento.efetuado == False, Pagamento.rejeitado == False,
                        Pagamento.metodo_pagamento == 'PayPal', Pagamento.cancelado == False).first()
                        participante = db.session.query(Participante).filter_by(usuario=current_user).first()
                        if pagamento is None:
                            valor_pagamento = get_preco_kit()
                            if form.uso_cupom_desconto.data is True:
                                cupom_desconto = db.session.query(CupomDesconto).filter_by(nome=form.cupom_desconto.data, usado=False).first()
                                if cupom_desconto is not None:
                                    valor_pagamento = max(0.00, valor_pagamento - cupom_desconto.valor)
                                    payment = criar_pagamento("Kit", "Este pagamento corresponde ao kit da X SECOMP UFSCar", str(valor_pagamento), request.url_root)
                                    pagamento = Pagamento(id_participante = participante.id, payment_id=str(payment.id),\
                                    descricao="Kit", valor=valor_pagamento, efetuado=False, metodo_pagamento='PayPal',
                                    id_camiseta=form.camiseta.data)
                                    cupom_desconto.usado = True
                                    pagamento.cupom_desconto = cupom_desconto
                                    db.session.add(cupom_desconto)
                                    db.session.add(pagamento)
                                    db.session.commit()
                            else:
                                payment = criar_pagamento("Kit", "Este pagamento corresponde ao kit da X SECOMP UFSCar", str(valor_pagamento), request.url_root)
                                pagamento = Pagamento(id_participante = participante.id, payment_id=str(payment.id),\
                                descricao="Kit", valor=valor_pagamento, efetuado=False, metodo_pagamento='PayPal',
                                id_camiseta=form.camiseta.data)
                                db.session.add(pagamento)
                                db.session.commit()
                            if pagamento.camiseta.quantidade_restante > 0:
                                pagamento.camiseta.quantidade_restante = pagamento.camiseta.quantidade_restante - 1
                                db.session.add(pagamento)
                                db.session.commit()
                        else:
                            payment = encontrar_pagamento(pagamento.payment_id)
                        if payment is not None and pagamento.efetuado == False:
                            for link in payment.links:
                                if link.rel == "approval_url":
                                    approval_url = str(link.href)
                                    return redirect(approval_url)

                        return render_template('users/pagamento_kit_efetuado.html')
                    elif form.forma_pagamento.data == 1:
                        participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
                        comprovante = form.comprovante.data
                        filename = secure_filename(comprovante.filename)
                        agora = strftime("%Y%m%d%H%M%S", localtime(time()))
                        filename = f'{current_user.id}_{current_user.primeiro_nome}_{current_user.sobrenome}_{agora}_{filename}'
                        filename = filename.replace(' ', '')
                        file_name = secure_filename(comprovante.filename)
                        upload_path = path.join(current_app.config['UPLOAD_FOLDER'], 'comprovantes')
                        if not path.exists(upload_path):
                            makedirs(upload_path)
                        comprovante.save(path.join(upload_path, filename))
                        valor_pagamento = get_preco_kit()
                        if form.uso_cupom_desconto.data is True:
                            cupom_desconto = db.session.query(CupomDesconto).filter_by(nome=form.cupom_desconto.data, usado=False).first()
                            if cupom_desconto is not None:
                                valor_pagamento = max(0.00, valor_pagamento - cupom_desconto.valor)
                                pagamento = Pagamento(id_participante = participante.id,\
                                descricao="Kit", valor=valor_pagamento, efetuado=False, metodo_pagamento='Comprovante',
                                id_camiseta=form.camiseta.data, comprovante_enviado=True, arquivo_comprovante=filename)
                                cupom_desconto.usado = True
                                pagamento.cupom_desconto = cupom_desconto
                                db.session.add(cupom_desconto)
                                db.session.add(pagamento)
                                db.session.commit()
                        else:
                            pagamento = Pagamento(id_participante = participante.id,\
                            descricao="Kit", valor=valor_pagamento, efetuado=False, metodo_pagamento='Comprovante',
                            id_camiseta=form.camiseta.data, comprovante_enviado=True, arquivo_comprovante=filename)
                            db.session.add(pagamento)
                            db.session.commit()
                        if pagamento.camiseta.quantidade_restante > 0:
                            pagamento.camiseta.quantidade_restante = pagamento.camiseta.quantidade_restante - 1

                        db.session.add(pagamento)
                        db.session.add(participante)
                        db.session.commit()
                        flash('Comprovante enviado com sucesso!')
                        return redirect(url_for('.dashboard'))
            else:
                return render_template('users/comprar_kit.html', usuario=current_user, participante = db.session.query(
                                        Participante).filter_by(usuario=current_user).first(), form=form, valor="{:2.2f}".format(get_preco_kit()).replace('.', ','))
        else:
            return redirect(url_for('.dashboard'))
    else:
        return redirect(url_for('.verificar_email'))

@users.route('/executar-pagamento-kit', methods=["POST", "GET"])
@login_required
@email_verificado_required
def executar_pagamento_kit():
    form_login = LoginForm(request.form)
    payment_id = request.args.get('paymentId')
    pagamento = db.session.query(Pagamento).join(Pagamento.participante).join(aliased(Participante.usuario),
    Participante.usuario).join(aliased(Usuario), Usuario).filter(Usuario.email == current_user.email,\
    Pagamento.descricao == "Kit", Pagamento.payment_id == payment_id, Pagamento.efetuado == False,\
    Pagamento.rejeitado == False, Pagamento.metodo_pagamento == 'PayPal', Pagamento.cancelado == False).first()
    participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
    payer_id = request.args.get('PayerID')
    if pagamento is not None:
        if pagamento.efetuado is False:
            if payer_id is not None:
                payment = encontrar_pagamento(pagamento.payment_id)
                if payment.execute({"payer_id": payer_id}):
                    pagamento.payer_id, pagamento.efetuado = payer_id, True
                    pagamento.data_hora_pagamento = strftime("%Y-%m-%d %H:%M:%S", localtime(time()))
                    db.session.add(current_user)
                    db.session.add(participante)
                    db.session.add(pagamento)
                    db.session.commit()
                    enviar_email_aviso_sucesso_confirmacao_pagamento_paypal(pagamento.participante.usuario, pagamento)
                    return render_template('users/sucesso_pagamento_kit.html', usuario=current_user, participante=participante, form_login=form_login)
                else:
                    return render_template('users/erro_pagamento_kit.html', usuario=current_user, participante=participante, form_login=form_login)
                    print(payment.error)
        else:
            return render_template('users/pagamento_kit_efetuado.html', usuario=current_user, participante=participante, form_login=form_login)
    else:
        return redirect(url_for('.dashboard'))

@users.route('/cancelar-pagamento-kit', methods=["POST", "GET"])
@login_required
@email_verificado_required
def cancelar_pagamento_kit():
    return redirect(url_for('users.pagamentos'))

@users.route('/pagamentos', methods=["POST", "GET"])
@login_required
@email_verificado_required
def pagamentos():
    participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
    if participante is not None:
        form = CancelarPagamentoForm(request.form)
        pagamentos = db.session.query(Pagamento).filter(Pagamento.participante == participante)
        if form.validate_on_submit():
            pagamento = db.session.query(Pagamento).filter(Pagamento.id == int(form.cancelar.data), Pagamento.participante == participante,
                                                            Pagamento.cancelado == False, Pagamento.efetuado == False,  Pagamento.rejeitado == False).first()
            if pagamento is not None:
                pagamento.cancelado = True
                pagamento.camiseta.quantidade_restante = pagamento.camiseta.quantidade_restante + 1
                db.session.add(pagamento)
                db.session.commit()
        return render_template('users/pagamentos.html', usuario=current_user, participante=participante, pagamentos=pagamentos, form=form)
    else:
        return redirect(url_for('.cadastro_participante'))

@users.route('/presencas', methods=["POST", "GET"])
@login_required
@email_verificado_required
def presencas():
    participante = db.session.query(Participante).filter_by(usuario=current_user, id_evento=get_id_evento_atual()).first()
    if participante is not None:
        presencas = db.session.query(Presenca).filter(Presenca.id_participante == participante.id, Presenca.id_evento == get_id_evento_atual()).all()
        limites = {
            "SEG_INI": datetime.strptime('2019-09-09 00:00:00', '%Y-%m-%d %H:%M:%S'),
            "SEG_FIM": datetime.strptime('2019-09-09 23:59:59', '%Y-%m-%d %H:%M:%S'),
            "TER_INI": datetime.strptime('2019-09-10 00:00:00', '%Y-%m-%d %H:%M:%S'),
            "TER_FIM": datetime.strptime('2019-09-10 23:59:59', '%Y-%m-%d %H:%M:%S'),
            "QUA_INI": datetime.strptime('2019-09-11 00:00:00', '%Y-%m-%d %H:%M:%S'),
            "QUA_FIM": datetime.strptime('2019-09-11 23:59:59', '%Y-%m-%d %H:%M:%S'),
            "QUI_INI": datetime.strptime('2019-09-12 00:00:00', '%Y-%m-%d %H:%M:%S'),
            "QUI_FIM": datetime.strptime('2019-09-12 23:59:59', '%Y-%m-%d %H:%M:%S'),
            "SEX_INI": datetime.strptime('2019-09-13 00:00:00', '%Y-%m-%d %H:%M:%S'),
            "SEX_FIM": datetime.strptime('2019-09-13 23:59:59', '%Y-%m-%d %H:%M:%S')
        }
        return render_template('users/presencas.html', usuario=current_user, participante=participante, presencas=presencas, limites=limites)
    else:
        return redirect(url_for('.cadastro_participante'))
