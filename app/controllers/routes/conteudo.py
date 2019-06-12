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
    abort(404)

@conteudo.route('/gerar-url-cadastro', methods=['POST', 'GET'])
@login_required
def gerar_url_cadastro():
    permissoes = current_user.getPermissoes()
    if("CONTEUDO" in permissoes or current_user.is_admin()):
        return render_template("conteudo/gerar_url_cadastro.html", form=form, dict_urls=dict_urls)
    else:
        abort(403)

@conteudo.route('/cadastro-atividade/minicurso', methods=['POST', 'GET'])
@login_required
def cadastro_minicurso():
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        form = CadastroInformacoesMinicurso(request.form)
        return render_template('conteudo/cadastro_minicurso.html', form=form)
    abort(403)

@conteudo.route('/cadastro-atividade/palestra', methods=['POST', 'GET'])
@login_required
def cadastro_palestra():
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        form = CadastroInformacoesPalestra(request.form)
        return render_template('conteudo/cadastro_palestra.html', form=form)
    abort(403)

@conteudo.route('/cadastro-atividade/mesa-redonda', methods=['POST', 'GET'])
@login_required
def cadastro_mesa_redonda():
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        return render_template('conteudo/cadastro_mesa_redonda.html')
    abort(403)

@conteudo.route('/cadastro-atividade/feira-pesquisas', methods=['POST', 'GET'])
@login_required
def cadastro_feira_pesquisas():
    permissoes = current_user.getPermissoes()
    if("MINISTRANTE" in permissoes or "CONTEUDO" in permissoes or current_user.is_admin()):
        form = CadastroFeiraDePesquisas(request.form)
        return render_template('conteudo/cadastro_feira_pesquisas.html', form=form)
    abort(403)
