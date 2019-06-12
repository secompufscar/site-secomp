from random import SystemRandom

from flask import render_template, request, redirect, abort, url_for, Blueprint
from flask import jsonify
from app.controllers.functions.dictionaries import *

from app.controllers.functions.helpers import get_participantes_da_atividade_json
from app.controllers.functions.email import enviar_email_custon

import json

from app.models.models import *

api = Blueprint('api', __name__, static_folder='static',
                       template_folder='templates', url_prefix='/api')

@api.route('/')
def index():
    return "Welcome to SECOMP: API"

@api.route('/equipe')
def equipe():
    return "Esperando JSON da Equipe"
#    with open('./app/config/membros_org.json', 'r') as out:
#        return out

@api.route('/patrocinadores')
def patrocinadores():
    return  jsonify(get_patrocinadores())

@api.route('/img/<url>')
def retornaImg(url):
    return url #TODO (quando estiver no servidor) hospedagem de imagens

@api.route('/executa-email-custon',methods=['POST'])
def executa_email_custon():
    '''
    Rota para acesso remoto que executa o envio de emails
    '''
    permissoes = current_user.getPermissoes()
    if("ENVIAR_EMAIL" in permissoes or current_user.is_admin()):
        try:
            pkg = request.form

            assunto = pkg['assunto']
            titulo = pkg['titulo']
            template = pkg['template']
            temAnexo = pkg['temAnexo']
            anexoBase = pkg['anexoBase']
            anexoPasta= pkg['anexoPasta']
            complemento = int(pkg['complemento'])
            extencao = int(pkg['extencao'])
            selecionados = pkg['selecionados'].split(',')

            if extencao == 0:
                extencao = ""
            elif extencao == 1:
                extencao = ".pdf"

            enviar_email_custon(assunto, titulo, template, temAnexo, anexoBase, anexoPasta, complemento, selecionados, extencao)

            return jsonify('Sucesso')
        except Exception as e:
            print(e)
            return jsonify('Falha')
    else:
        print("NAO PODE")


@api.route('/pesquisa-usuario-por-atividade',methods=['POST'])
def pesquisa_usuario_por_atividade():
    '''
    Retorna os usuários que participaram de uma atividade
    '''
    permissoes = current_user.getPermissoes()
    if("ENVIAR_EMAIL" in permissoes or current_user.is_admin()):
        atividadeID = request.form['id']

        participantes = get_participantes_da_atividade_json(int(atividadeID))
        return jsonify(participantes)
