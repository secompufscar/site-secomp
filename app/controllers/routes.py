from os import path, makedirs

from bcrypt import gensalt
from flask import render_template, request, redirect, abort, flash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from passlib.hash import pbkdf2_sha256
from werkzeug import secure_filename

from app.controllers.forms import *
from app.controllers.functions import *
from app.models.models import *
from random import randint

@app.route('/')
def index():
    """
    Renderiza a página inicial do projeto
    """
    return render_template('index.html', title='Página inicial',
                           secomp_now=secomp_now[0], secomp=secomp[0],
                           secomp_email=secomp_email,
                           secompEdition=secomp_edition)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = db.session.query(Usuario).filter_by(
            email=form.email.data).first()
        if user:
            if pbkdf2_sha256.verify(form.senha.data, user.senha):
                user.autenticado = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('dashboard_usuario'))
    return render_template('login.html', form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """
    Renderiza a página de logout do projeto
    """
    user = current_user
    user.autenticado = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    """
    Renderiza a página de cadastro do projeto
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    form = CadastroForm(request.form)
    email = form.email.data
    salt = gensalt().decode('utf-8')
    token = serializer.dumps(email, salt=salt)

    if form.validate_on_submit():
        usuario = db.session.query(Usuario).filter_by(email=email).first()
        if usuario is not None:
            return render_template("cadastro.html", form=form, erro_email=True)
        else:
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hash = pbkdf2_sha256.encrypt(
                form.senha.data, rounds=10000, salt_size=15)
            usuario = Usuario(email=email, senha=hash, ultimo_login=agora,
                              data_cadastro=agora, permissao=0, primeiro_nome=form.primeiro_nome.data,
                              sobrenome=form.sobrenome.data, id_curso=verifica_outro_escolhido(form.curso,
                              Curso(nome=form.outro_curso.data)), id_instituicao=verifica_outro_escolhido(
                              form.instituicao, Instituicao(nome=form.outra_instituicao.data)),
                              id_cidade=verifica_outro_escolhido(form.cidade, Cidade(nome=form.outra_cidade.data)),
                              data_nascimento=form.data_nasc.data, token_email=token, autenticado=True, salt=salt)
            db.session.add(usuario)
            db.session.flush()
            db.session.commit()
            enviarEmailConfirmacao(app, email, token)
            login_user(usuario, remember=True)
            return redirect(url_for('verificar_email'))
    return render_template('cadastro.html', form=form, erro_email=False)


@app.route('/verificar-email')
@login_required
def verificar_email():
    if email_confirmado() == True:
        msg = 'Seu email foi verificado com sucesso!'
        status = True
    else:
        msg = 'Confirme o email de verificação que foi enviado ao endereço de email fornecido'
        status = False
    return render_template('confirma_email.html', resultado=msg, status=status)


@app.route('/cadastro-participante', methods=['POST', 'GET'])
@login_required
def cadastro_participante():
    id_evento = db.session.query(Evento).filter_by(
        edicao=EDICAO_ATUAL).first().id
    if email_confirmado() == True:
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
                return redirect(url_for('dashboard_usuario'))
            else:
                return render_template('cadastro_participante.html', form=form)
        else:
            return redirect(url_for('dashboard_usuario'))
    else:
        return redirect(url_for('verificar_email'))


@app.route('/dashboard-usuario', methods=['POST', 'GET'])
@login_required
def dashboard_usuario():
    if email_confirmado() == True:
        form = EditarUsuarioForm(request.form)
        if form.validate_on_submit():
            usuario = db.session.query(Usuario).filter_by(
                id=current_user.id).first()
            if pbkdf2_sha256.verify(form.senha.data, usuario.senha):
                usuario.primeiro_nome = form.primeiro_nome.data
                usuario.sobrenome = form.sobrenome.data
                usuario.data_nascimento = form.data_nasc.data
                usuario.id_curso = form.curso.data
                usuario.id_instituicao = form.instituicao.data
                usuario.id_cidade = form.cidade.data
                if usuario.email != form.email.data:
                    serializer = URLSafeTimedSerializer(
                        app.config['SECRET_KEY'])
                    salt = gensalt().decode('utf-8')
                    token = serializer.dumps(form.email.data, salt=salt)
                    usuario.salt = salt
                    usuario.token_email = token
                    usuario.email_verificado = False
                    db.session.add(usuario)
                    db.session.commit()
                    enviarEmailConfirmacao(app, form.email.data, token)
                    login_user(usuario, remember=True)
                    return redirect(url_for('verificar_email'))
                else:
                    db.session.add(usuario)
                    db.session.commit()
                    login_user(usuario, remember=True)
        form.primeiro_nome.default = current_user.primeiro_nome
        form.sobrenome.default = current_user.sobrenome
        form.email.default = current_user.email
        form.data_nasc.default = current_user.data_nascimento
        form.curso.default = current_user.curso.id
        form.instituicao.default = current_user.instituicao.id
        form.cidade.default = current_user.cidade.id
        form.process()

        return render_template('dashboard_usuario.html', eventos=get_dicionario_eventos_participante(request.base_url),
                               info_usuario=get_dicionario_usuario(current_user), form=form)
    else:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        salt = gensalt().decode('utf-8')
        token = serializer.dumps(current_user.email, salt=salt)
        usuario = current_user
        usuario.salt = salt
        usuario.token_email = token
        usuario.email_verificado = False
        db.session.add(usuario)
        db.session.commit()
        enviarEmailConfirmacao(app, usuario.email, token)
        login_user(usuario, remember=True)
        return redirect(url_for('verificar_email'))


@app.route('/dashboard-usuario/evento/<edicao>')
@login_required
def info_participante_evento(edicao):
    return render_template('info_participante.html', info_evento=get_dicionario_info_evento(edicao))


@app.route('/enviar-comprovante', methods=['POST', 'GET'])
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
        upload_path = path.join(app.config['UPLOAD_FOLDER'], 'comprovantes')
        if not path.exists(upload_path):
            makedirs(upload_path)
        comprovante.save(path.join(upload_path, filename))
        flash('Comprovante enviado com sucesso!')
        return redirect(url_for('dashboard_usuario'))
    return render_template('enviar_comprovante.html', form=form)


@app.route('/verificacao/<token>')
def verificacao(token):
    """
    Página do link enviado para o usuário
    """

    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
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
        return render_template('cadastro.html', resultado='O link de ativação expirou.')
    except Exception as e:
        print(e)
        return render_template('cadastro.html', resultado='Falha na ativação.')
    return redirect(url_for('verificar_email'))


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


@app.route('/alterar-senha', methods=["POST", "GET"])
@login_required
def alterar_senha():
    form = AlterarSenhaForm(request.form)
    if email_confirmado() == True:
        if form.validate_on_submit():
            usuario = db.session.query(Usuario).filter_by(
                email=current_user.email).first()
            enc = pbkdf2_sha256.encrypt(
                form.nova_senha.data, rounds=10000, salt_size=15)
            usuario.senha = enc
            db.session.add(usuario)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('alterar_senha.html', form=form, action=request.base_url)
    else:
        flash('Confirme seu e-mail para alterar a senha!')
        return redirect(url_for('dashboard_usuario'))


@app.route('/esqueci-senha', methods=["POST", "GET"])
def esqueci_senha():
    form = AlterarSenhaPorEmailForm(request.form)
    if form.validate_on_submit():
        usuario = db.session.query(Usuario).filter_by(
            email=form.email.data).first()
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        salt = gensalt().decode('utf-8')
        token = serializer.dumps(usuario.email, salt=salt)
        usuario.salt_alteracao_senha = salt
        usuario.token_alteracao_senha = token
        db.session.add(usuario)
        db.session.commit()
        enviarEmailSenha(app, usuario.email, token)
        return render_template("esqueci_senha.html", status_envio_email=True, form=form)
    return render_template("esqueci_senha.html", status_envio_email=False, form=form)


@app.route('/confirmar-alteracao-senha/<token>', methods=["POST", "GET"])
def confirmar_alteracao_senha(token):
    form = AlterarSenhaForm(request.form)
    if form.validate_on_submit():
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            # Acha o usuário que possui o token
            usuario = db.session.query(Usuario).filter_by(
                token_alteracao_senha=token).first()
            salt = usuario.salt_alteracao_senha
            # Gera um email a partir do token do link e do salt do db
            email = serializer.loads(token, salt=salt, max_age=3600)
            hash = pbkdf2_sha256.encrypt(
                form.nova_senha.data, rounds=10000, salt_size=15)
            usuario.senha = hash
            db.session.add(usuario)
            db.session.commit()
        except SignatureExpired:
            return "O link de confirmação expirou !"
        except Exception as e:
            print(e)
            return "Falha na confirmação de link do email"
        return redirect(url_for('login'))
    return render_template("alterar_senha.html", form=form, action=request.base_url)


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
        if(camiseta.quantidade_restante > 0):
            participante = db.session.query(Participante).filter_by(id=form.participante.data).first()
            participante.id_camiseta = form.camiseta.data
            participante.pacote = True
            participante.pagamento = True
            db.session.add(participante)
            db.session.commit()
            return render_template('venda_de_kits.html', alerta="Compra realizada com sucesso!", form=form)
        elif(camiseta.quantidade_restante == 0):
            return render_template('venda_de_kits.html', alerta="Sem estoque para " + camiseta.tamanho, form=form)
    return render_template('venda_de_kits.html', alerta="Preencha o formulário abaixo", form=form)

@app.route('/sortear')
@login_required
def sortear():
    return render_template('sortear_usuario.html', sorteando=False)

@app.route('/fazer-sorteio')
@login_required
def sorteando():
    # <Falta conferir permissões>
    sorteado = db.session.query(Participante)
    sorteado = sorteado[randint(1, sorteado.count()) - 1]
    return render_template('sortear_usuario.html', sorteado=sorteado, sorteando=True)

@app.route('/constr')
def constr():
    return render_template('em_constr.html', title='Página em construção')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html', title='Sobre a Secomp')
