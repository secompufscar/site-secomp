from flask import render_template, request, redirect, abort, url_for, Blueprint
from flask import jsonify, current_app
from app.controllers.functions.dictionaries import *
from passlib.hash import pbkdf2_sha256

from app.controllers.functions.helpers import get_participantes_da_atividade_json, get_atividades_api
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


@api.route('/atividades', methods=['POST', 'GET'])
def atividades():
    return jsonify(get_atividades_api())

#@api.route('/img/<url>')
def retornaImg(url):
    return url #TODO (quando estiver no servidor) hospedagem de imagens

@api.route('/ler-presenca', methods=['POST'])
def ler_presenca():
    '''
    Essa rota vai receber via POST o uuid do participante, o id da atividade e registrar a presença caso a key do aplicativo bata com a
    key do arquivo config/development.py, chamada de KEY_API_PRESENCA.
    '''
    data = request.get_json(force=True)
    uuid = str(data['uuid_participante'])
    id_atividade = int(data['id_atividade'])
    force = bool(data['force_presenca'])
    key = data['key']
    if(key == current_app.config['KEY_API_PRESENCA']):
        try:
            participante = db.session.query(Participante).filter_by(uuid=uuid).first()
            if(db.session.query(Presenca).filter_by(id_participante=participante.id, id_atividade=164).first() != None or id_atividade == 164): #Verifica se está credenciado
                inscrito = participante in db.session.query(Atividade).filter_by(id=id_atividade).first().participantes
                if(id_atividade == 164 or inscrito or force):
                    if (db.session.query(Presenca).filter_by(id_atividade=id_atividade,
                                                                 id_participante=participante.id).first() == None):
                        presenca = Presenca(data_hora_registro=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            id_atividade=id_atividade,
                                            id_participante=participante.id,
                                            id_evento=get_id_evento_atual(),
                                            inscrito=inscrito)
                        db.session.add(presenca)
                        db.session.flush()
                        db.session.commit()
                        info = {
                            "Participante" : participante.usuario.primeiro_nome + " " + participante.usuario.sobrenome,
                            "Status" : "SUCCESS"
                        }
                        return jsonify(info)
                    else:
                        info = {
                            "Participante": participante.usuario.primeiro_nome + " " + participante.usuario.sobrenome,
                            "Status": "JA_LIDO"
                        }
                        return jsonify(info)
                else:
                    info = {
                        "Participante": participante.usuario.primeiro_nome + " " + participante.usuario.sobrenome,
                        "Status": "NÃO_INSCRITO"
                    }
                    return jsonify(info)
            else:
                info = {
                    "Participante": participante.usuario.primeiro_nome + " " + participante.usuario.sobrenome,
                    "Status": "NÃO_CREDENCIADO"
                }
                return jsonify(info)
        except Exception as e:
            print(e)
            return jsonify("ERROR")
    else:
        return jsonify("INVALID KEY")

@api.route('/verifica-inscricao', methods=['POST'])
def verifica_insc():
    '''
    Essa rota vai receber via POST o uuid do participante, o id da atividade e verificar se o participante está inscrito na mesma
    '''
    data = request.get_json(force=True)
    uuid = str(data['uuid_participante'])
    id_atividade = int(data['id_atividade'])
    key = data['key']
    if(key == current_app.config['KEY_API_PRESENCA']):
        try:
            participante = db.session.query(Participante).filter_by(uuid=uuid).first()
            inscrito = participante in db.session.query(Atividade).filter_by(id=id_atividade).first().participantes
            info = {
                "Participante": participante.usuario.primeiro_nome + " " + participante.usuario.sobrenome,
                "Inscrito": inscrito
            }
            return jsonify(info)
        except Exception as e:
            print(e)
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

@api.route('/verifica-kit', methods=['POST']) #Mudar nome da rota para consulta-dados-usuario
def verifica_kit():
    '''
    Essa rota vai receber via POST o uuid do participante, verificar se o participante está comprou o kit.
    '''
    data = request.get_json(force=True)
    uuid = str(data['uuid_participante'])
    key = data['key']
    if(key == current_app.config['KEY_API_PRESENCA']):
        try:
            participante = db.session.query(Participante).filter_by(uuid=uuid).first()
            pagamentos = db.session.query(Pagamento).filter_by(id_participante=participante.id, efetuado=True, rejeitado=False, cancelado=False).all()
            camisetas = []
            for p in pagamentos:
                camisetas.append(p.camiseta.tamanho)
            info = {
                "Participante": participante.usuario.primeiro_nome + " " + participante.usuario.sobrenome,
                "Kit": len(pagamentos) > 0,
                "Camiseta": camisetas
            }
            return jsonify(info)
        except Exception as e:
            print(e)
            return jsonify("ERROR")
    else:
        return jsonify("INVALID KEY")

@api.route('/dados-usuario', methods=['POST'])
def dados_usuario():
    '''
    Essa rota vai receber via POST o email do participante, a hash da senha, e retornar os dados do usuário para o aplicativo.
    '''
    data = request.get_json(force=True)
    email = str(data['email'])
    senha = str(data['password'])
    user = db.session.query(Usuario).filter_by(email=email).first()
    participante = db.session.query(Participante).filter_by(
        usuario=user).first()
    if user:
        if user.senha is not None and pbkdf2_sha256.verify(senha, user.senha):
            ativs = []
            for p in participante.presencas:
                ativ = db.session.query(Atividade).filter_by(id=p.id_atividade).all()
                for a in ativ:
                    ativs.append(a.titulo)
            camiseta = db.session.query(Pagamento).filter_by(id_participante=participante.id, efetuado=True, rejeitado=False, cancelado=False).all()
            camisetas = []
            for p in camiseta:
                camisetas.append(p.camiseta.tamanho)
            info = {
                "id_participante": participante.id,
                "primeiro_nome": participante.usuario.primeiro_nome,
                "sobrenome": participante.usuario.sobrenome,
                "camiseta": camisetas,
                "pontuacao": participante.pontuacao,
                "presencas": ativs,
                "uuid": participante.uuid
            }
            return jsonify(info)
        else:
            return jsonify("Erro: senha inválida.")
    return jsonify("Usuário inexistente.")
  
'''
@api.route('/hash-func', methods=['POST'])
def hash_func():
    
    Essa rota vai receber via POST a senha do usuário e retornar a HASH para o aplicativo.
    
    data = request.get_json(force=True)
    senha = str(data['password'])
    if senha:
        return jsonify(pbkdf2_sha256.encrypt(senha, rounds=10000, salt_size=15))
    else:
        return jsonify("NULL")
'''
    
@api.route('/patrocinadores', methods=['GET'])
def patroc_api():
    '''
    Devolve um JSON com os patrocinadores
    '''
    try:
        return jsonify(get_patrocinadores_ativos())
    except Exception as e:
        print(e)
        return None
