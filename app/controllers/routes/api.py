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

            # Atribuição e verificação dos dados
            assunto = pkg['assunto'].strip()
            if assunto == "":
                return jsonify('Falha. Sem assunto!')

            titulo = pkg['titulo'].strip()
            if titulo == "":
                return jsonify('Falha. Sem título!')

            template = pkg['template'].strip()
            if template == "":
                return jsonify('Falha. Sem template!')

            try:
                temAnexo = bool(pkg['temAnexo'])
            except Exception as e:
                print("Erro ao converter temAnexo para bool. {}".format(e))
                return jsonify('Falha. Erro ao converter temAnexo para bool!')

            anexoBase = pkg['anexoBase'].strip()
            if temAnexo and anexoBase == "":
                return jsonify('Falha')

            anexoPasta= pkg['anexoPasta']

            try:
                complemento = int(pkg['complemento'])
            except Exception as e:
                print("Erro ao converter complemento para int. {}".format(e))
                return jsonify('Falha. Erro ao converter complemento para int!')

            try:
                extencao = int(pkg['extencao'])
            except Exception as e:
                print("Erro ao converter extenção para int. {}".format(e))
                return jsonify('Falha. Erro ao converter extenção para int!')

            selecionados = pkg['selecionados'].split(',')
            if len(selecionados) == 0:
                return jsonify('Falha. Nínguem foi selecionado!')

            # Verificação da extenção, novas extenções adicionadas no dictExtencao devem ser suportadas aqui
            if extencao == 0:
                extencao = ""
            elif extencao == 1:
                extencao = ".pdf"
            else:
                return jsonify('Falha. Extenção não reconhecida!')

            # Retorna possíveis erros
            erros = enviar_email_custon(assunto, titulo, template, temAnexo, anexoBase, anexoPasta, complemento, selecionados, extencao)

            # Cuida dos erros, no caso de algum, retorna uma string com o email em que ocorreu o erro e o erro
            if len(erros) == 0:
                return jsonify('Sucesso')
            else:
                r = ""
                for e in erros:
                    r += ("Email: {email} {erro}").format(email=e[0]['email'], erro=str(e[1]))
                return jsonify('Falha. \n {}'.format(r))
        except Exception as e:
            print(e)
            return jsonify('Falha.')
    else:
        print("NAO PODE")


@api.route('/pesquisa-usuario-por-atividade',methods=['POST'])
def pesquisa_usuario_por_atividade():
    '''
    Retorna os usuários que participaram de uma atividade
    Pesquisa usando o id da atividade
    '''
    permissoes = current_user.getPermissoes()
    if("ENVIAR_EMAIL" in permissoes or current_user.is_admin()):
        atividadeID = request.form['id']

        participantes = get_participantes_da_atividade_json(int(atividadeID))
        return jsonify(participantes)
