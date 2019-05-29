from os import path, makedirs
import hashlib
from bcrypt import gensalt, hashpw
from flask import request, redirect, flash, Blueprint, current_app, abort
from flask_login import login_required, login_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from passlib.hash import pbkdf2_sha256
import string
import random
from app.controllers.forms.forms import *
from app.controllers.functions.email import *
from app.models.models import *
from app.controllers.functions.dictionaries import *

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


@conteudo.route('/cadastro-ministrante/<codigo>', methods=['POST', 'GET'])
def cadastro_ministrante(codigo):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    url = db.session.query(URLConteudo).filter_by(codigo=str(codigo), valido=True).first()
    if(url is not None and url.codigo == codigo and url.numero_cadastros != 0):
        form = CadastroMinistranteForm(request.form)
        if form.validate_on_submit():
            email = form.email.data
            salt = gensalt().decode('utf-8')
            token = serializer.dumps(email, salt=salt)
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hash = pbkdf2_sha256.encrypt(form.senha.data, rounds=10000, salt_size=15)
            usuario = Usuario(email=email, senha=hash, ultimo_login=agora,
                            data_cadastro=agora, primeiro_nome=form.primeiro_nome.data, sobrenome=form.sobrenome.data,
                            data_nascimento=form.data_nascimento.data, token_email=token, autenticado=True, salt=salt)
            ministrante = Ministrante(telefone=form.telefone.data, profissao=form.profissao.data,
                                    empresa_universidade=form.empresa_universidade.data, biografia=form.biografia.data,
                                    foto=form.foto.data, tamanho_camiseta=form.tamanho_camiseta.data, facebook=form.facebook.data,
                                    twitter=form.twitter.data, linkedin=form.linkedin.data, github=form.github.data,
                                    usuario=usuario)
            url.numero_cadastros = url.numero_cadastros - 1
            db.session.add(usuario)
            db.session.add(ministrante)
            db.session.add(url)
            db.session.flush()
            db.session.commit()
            enviar_email_confirmacao(usuario, token)
            login_user(usuario, remember=True)
            return redirect(url_for('users.verificar_email'))
        print(form.errors)
        return render_template("conteudo/cadastro_ministrante.html", form=form, codigo=codigo)
    abort(404)

@conteudo.route('/gerar-url-cadastro', methods=['POST', 'GET'])
@login_required
def gerar_url_cadastro():
    permissoes = current_user.getPermissoes()
    if("CONTEUDO" in permissoes or current_user.is_admin()):
        form = GerarURLCadastroForm(request.form)
        url_em_uso = db.session.query(URLConteudo).filter_by(ultimo_gerado=True, valido=True).first()
        dict_urls = get_dicionario_urls_cadastro_ministrante(request.url_root + 'area-conteudo/cadastro-ministrante/')
        if form.validate_on_submit() or url_em_uso  is None:
            codigo = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(200))
            url_conteudo = URLConteudo(codigo=codigo, ultimo_gerado=True, valido=True,
                                       numero_cadastros=form.numero_cadastros.data, descricao=form.descricao.data)
            db.session.add(url_conteudo)
            if  url_em_uso is not None and url_em_uso.numero_cadastros == 0:
                db.session.delete(url_em_uso)
            db.session.commit()
            dict_urls = get_dicionario_urls_cadastro_ministrante(request.url_root + 'area-conteudo/cadastro-ministrante/')
            return render_template("conteudo/gerar_url_cadastro.html", form=form, dict_urls=dict_urls)
        return render_template("conteudo/gerar_url_cadastro.html", form=form, dict_urls=dict_urls)
    else:
        abort(403)
