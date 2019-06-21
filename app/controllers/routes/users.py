from os import path, makedirs

from bcrypt import gensalt
from flask import request, redirect, flash, Blueprint, current_app
from flask_login import login_required, login_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from passlib.hash import pbkdf2_sha256
from werkzeug import secure_filename

from app.controllers.forms.forms import *
from app.controllers.functions.dictionaries import *
from app.controllers.functions.email import *
from app.controllers.functions.helpers import *
from app.models.models import *

users = Blueprint('users', __name__, static_folder='static',
                  template_folder='templates', url_prefix='/participante')


@users.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    """
    Renderiza a página de cadastro do projeto
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    form = CadastroForm(request.form)
    email = form.email.data
    salt = gensalt().decode('utf-8')
    token = serializer.dumps(email, salt=salt)
    if form.validate_on_submit():
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hash = pbkdf2_sha256.encrypt(form.senha.data, rounds=10000, salt_size=15)
        usuario = Usuario(email=email, senha=hash, ultimo_login=agora,
                          data_cadastro=agora, primeiro_nome=form.primeiro_nome.data, sobrenome=form.sobrenome.data,
                          id_curso=verifica_outro_escolhido(form.curso, Curso(nome=str(form.outro_curso.data).strip())),
                          id_instituicao=verifica_outro_escolhido(form.instituicao,
                                                                  Instituicao(nome=form.outra_instituicao.data)),
                          id_cidade=verifica_outro_escolhido(form.cidade, Cidade(nome=form.outra_cidade.data)),
                          data_nascimento=form.data_nasc.data, token_email=token, autenticado=True, salt=salt)
        db.session.add(usuario)
        db.session.flush()
        db.session.commit()
        enviar_email_confirmacao(usuario, token)
        login_user(usuario, remember=True)
        return redirect(url_for('.verificar_email'))

    return render_template('users/cadastro.html', form=form)


@users.route('/verificar-email')
@login_required
def verificar_email():
    permissoes = current_user.getPermissoes()
    view_atividade = ''
    if "MINISTRANTE" in permissoes:
        ministrante = True
    else:
        ministrante = False
        codigo = ''
    if email_confirmado():
        msg = 'Seu email foi verificado com sucesso!'
        status = True
    else:
        msg = 'Confirme o email de verificação que foi enviado ao endereço de email fornecido'
        status = False
    return render_template('users/confirma_email.html', resultado=msg, status=status, ministrante=ministrante)


@users.route('/cadastro-participante', methods=['POST', 'GET'])
@login_required
def cadastro_participante():
    id_evento = db.session.query(Evento).filter_by(
        edicao=EDICAO_ATUAL).first().id
    if email_confirmado():
        participante = db.session.query(Participante).filter_by(
            id_usuario=current_user.id, id_evento=id_evento).first()
        if participante is None:
            form = ParticipanteForm(request.form)
            participante = db.session.query(Participante).filter_by(
                id_usuario=current_user.id, id_evento=id_evento).first()
            if form.validate_on_submit() and participante is None:
                agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                usuario = current_user
                participante = Participante(id_usuario=usuario.id, id_evento=id_evento, pacote=form.kit.data,
                                            pagamento=False, id_camiseta=form.camiseta.data, data_inscricao=agora, credenciado=False,
                                            opcao_coffee=form.restricao_coffee.data)
                db.session.add(participante)
                db.session.flush()
                db.session.commit()
                return redirect(url_for('.dashboard'))
            else:
                return render_template('users/cadastro_participante.html', form=form)
        else:
            return redirect(url_for('.dashboard'))
    else:
        return redirect(url_for('.verificar_email'))


@users.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    usuario = db.session.query(Usuario).filter_by(
        id=current_user.id).first()
    if email_confirmado():
        participante = db.session.query(Participante).filter_by(
            usuario=current_user).first()
        return render_template('users/dashboard_usuario.html', title='Dashboard', usuario=usuario,
                               participante=participante)
    else:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        salt = gensalt().decode('utf-8')
        token = serializer.dumps(current_user.email, salt=salt)
        usuario = current_user
        usuario.salt = salt
        usuario.token_email = token
        usuario.email_verificado = False
        db.session.add(usuario)
        db.session.commit()
        enviar_email_confirmacao(usuario.email, token)
        login_user(usuario, remember=True)
        return redirect(url_for('.verificar_email'))


@users.route('/enviar-comprovante', methods=['POST', 'GET'])
@login_required
def envio_comprovante():
    """
    Página de envio de comprovantes de pagamento
    """
    form = ComprovanteForm()
    if form.validate_on_submit():
        comprovante = form.comprovante.data
        filename = secure_filename(comprovante.filename)
        filename = f'{current_user.id}_{current_user.primeiro_nome}_{current_user.sobrenome}_{filename}'
        upload_path = path.join(current_app.config['UPLOAD_FOLDER'], 'comprovantes')
        if not path.exists(upload_path):
            makedirs(upload_path)
        comprovante.save(path.join(upload_path, filename))
        flash('Comprovante enviado com sucesso!')
        return redirect(url_for('.dashboard'))
    return render_template('users/enviar_comprovante.html', form=form)


@users.route('/verificacao/<token>')
def verificacao(token):
    """
    Página do link enviado para o usuário
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # Acha o usuário que possui o token
        user = db.session.query(Usuario).filter_by(token_email=token).first()
        salt = user.salt
        # Gera um email a partir do token do link e do salt do db
        email = serializer.loads(token, salt=salt, max_age=3600)
        user.email = email
        # Valida o email
        user.email_verificado = True
        db.session.add(user)
        db.session.commit()
    # Tempo definido no max_age
    except SignatureExpired:
        return render_template('users/cadastro.html', resultado='O link de ativação expirou.')
    except Exception as e:
        print(e)
        return render_template('users/cadastro.html', resultado='Falha na ativação.')
    return redirect(url_for('.verificar_email'))


@users.route('/inscricao-atividades')
@login_required
def inscricao_atividades():
    minicursos = db.session.query(Atividade).filter_by(
        tipo=TipoAtividade['minicurso'])
    workshops = db.session.query(Atividade).filter_by(
        tipo=TipoAtividade['workshop'])
    palestras = db.session.query(Atividade).filter_by(
        tipo=TipoAtividade['palestra'])
    return render_template('users/inscricao_atividades.html',
                           participante=db.session.query(Participante).filter_by(
                               usuario=current_user).first(), usuario=current_user, minicursos=minicursos, workshops=workshops, palestras=palestras)


@users.route('/inscricao-atividades/<filtro>')
@login_required
def inscricao_atividades_com_filtro(filtro):
    minicursos = db.session.query(Atividade).filter(
        Atividade.tipo.like(TipoAtividade['minicurso']), Atividade.titulo.like("%" + filtro + "%"))
    workshops = db.session.query(Atividade).filter(
        Atividade.tipo.like(TipoAtividade['workshop']), Atividade.titulo.like("%" + filtro + "%"))
    palestras = db.session.query(Atividade).filter(
        Atividade.tipo.like(TipoAtividade['palestra']), Atividade.titulo.like("%" + filtro + "%"))

    return render_template('users/inscricao_atividades.html',
                           participante=db.session.query(Participante).filter_by(
                               usuario=current_user).first(),
                           usuario=current_user, minicursos=minicursos, workshops=workshops, palestras=palestras)


@users.route('/inscrever-atividade/<id>')
@login_required
def inscrever(id):
    atv = db.session.query(Atividade).filter_by(id=id).first()
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

        return render_template('users/inscricao_atividades.html',
                               participante=db.session.query(Participante).filter_by(
                                   usuario=current_user).first(),
                               usuario=current_user, minicursos=minicursos, workshops=workshops, palestras=palestras,
                               acao="+")
    else:
        return "Não há vagas disponíveis!"


@users.route('/desinscrever-atividade/<id>')
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
            tipo=TipoAtividade['palestra'])
        return render_template('users/inscricao_atividades.html',
                               participante=db.session.query(Participante).filter_by(
                                   usuario=current_user).first(),
                               usuario=current_user, minicursos=minicursos, workshops=workshops, palestras=palestras,
                               acao="-")
    else:
        return "Não está inscrito nessa atividade!"


@users.route('/alterar-senha', methods=["POST", "GET"])
@login_required
def alterar_senha():
    form = AlterarSenhaForm(request.form)
    if email_confirmado():
        if form.validate_on_submit():
            usuario = db.session.query(Usuario).filter_by(
                email=current_user.email).first()
            enc = pbkdf2_sha256.encrypt(
                form.nova_senha.data, rounds=10000, salt_size=15)
            usuario.senha = enc
            db.session.add(usuario)
            db.session.commit()
            return redirect(url_for('.login'))
        else:
            return render_template('users/alterar_senha.html', form=form, action=request.base_url)
    else:
        flash('Confirme seu e-mail para alterar a senha!')
        return redirect(url_for('.dashboard'))


@users.route('/esqueci-senha', methods=["POST", "GET"])
def esqueci_senha():
    form = AlterarSenhaPorEmailForm(request.form)
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
            return render_template("users/esqueci_senha.html", status_envio_email=True, form=form)
        flash('Este e-mail não está cadastrado no site.')
    return render_template("users/esqueci_senha.html", status_envio_email=False, form=form)


@users.route('/confirmar-alteracao-senha/<token>', methods=["POST", "GET"])
def confirmar_alteracao_senha(token):
    form = AlterarSenhaForm(request.form)
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
        return redirect(url_for('.login'))
    return render_template("users/alterar_senha.html", form=form, action=request.base_url)
