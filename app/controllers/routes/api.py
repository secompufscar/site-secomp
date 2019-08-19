from flask import render_template, request, redirect, abort, url_for, Blueprint
from flask import jsonify, current_app
from app.controllers.functions.dictionaries import *

from app.controllers.functions.helpers import get_participantes_da_atividade_json
from app.controllers.functions.email import enviar_email_custon

from app.controllers.forms.options import get_opcoes_ecustom_extensao

from app.models.models import *

api = Blueprint('api', __name__, static_folder='static',
                       template_folder='templates', url_prefix='/api')

#@api.route('/')
def index():
    return "Welcome to SECOMP: API"

#@api.route('/equipe')
def equipe():
    return "Esperando JSON da Equipe"
#    with open('./app/config/membros_org.json', 'r') as out:
#        return out

@api.route('/patrocinadores/<edicao>')
def patrocinadores(edicao):
    return jsonify(get_patrocinadores(edicao))


@api.route('/atividades/<edicao>')
def atividades(edicao):
    return jsonify(get_atividades(edicao))

#@api.route('/img/<url>')
def retornaImg(url):
    return url #TODO (quando estiver no servidor) hospedagem de imagens



@api.route('/ler-presenca', methods=['POST'])
def ler_presenca():
    '''
    Essa rota vai receber via POST o id de participante, o id da atividade e registrar a presença caso a key do aplicativo bata com a
    key do arquivo config/development.py, chamada de KEY_API_PRESENCA.
    '''
    data = request.get_json(force=True)
    id_participante = int(data['id_participante'])
    id_atividade = int(data['id_atividade'])
    key = data['key']
    if(key == current_app.config['KEY_API_PRESENCA']):
        try:
            participante = db.session.query(Participante).filter_by(id=id_participante).first()

            if (db.session.query(Presenca).filter_by(id_atividade=id_atividade,
                                                         id_participante=id_participante).first() != None):
                inscrito =  participante in db.session.query(Atividade).filter_by(id=id_atividade).participantes
                presenca = Presenca(data_hora_registro=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    id_atividade=id_atividade,
                                    id_participante=id_participante,
                                    id_evento=get_id_evento_atual(),
                                    inscrito=inscrito)
                db.session.add(presenca)
                db.session.flush()
                db.session.commit()
                info = {
                    "Participante" : participante.primeiro_nome + " " + participante.sobrenome,
                    "Status" : "SUCCESS"
                }
                return jsonify(info)
            else:
                info = {
                    "Participante": participante.primeiro_nome + " " + participante.sobrenome,
                    "Status": "JA_LIDO"
                }
                return jsonify(info)
        except:
            return jsonify("ERROR")
    else:
        return jsonify("INVALID KEY")


@api.route('/executa-email-custon', methods=['POST'])
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
                if (pkg['temAnexo'] == 'true'):
                    temAnexo = True
                elif (pkg['temAnexo'] == 'false'):
                    temAnexo = False
                else:
                    print("Erro ao converter temAnexo para bool.")
                    return jsonify('Falha. Erro ao converter temAnexo para bool!')

            except Exception as e:
                print("Erro ao converter temAnexo para bool. {}".format(e))
                return jsonify('Falha. Erro ao converter temAnexo para bool!')

            anexoBase = pkg['anexoBase'].strip()
            if temAnexo and anexoBase == "":
                return jsonify('Falha')

            anexoPasta = pkg['anexoPasta']

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
            extencaoDict = {key : value for (key, value) in get_opcoes_ecustom_extensao()}

            if extencao == 0:
                extencao = ""
            else:
                try:
                    extencao = extencaoDict[extencao]
                except Exception as e:
                    return jsonify('Falha. Extenção não reconhecida!\n{}'.format(str(e)))

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
            return jsonify('Falha. \n {}'.format(str(e)))
    else:
        print("NAO PODE")


@api.route('/pesquisa-usuario-por-atividade', methods=['POST'])
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

