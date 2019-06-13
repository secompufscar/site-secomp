from app.models.models import *


def get_score_evento(edicao):
    return 10000


def get_usuarios_query():
    '''
    Retorna o objeto da query de usuários para ser usado em outra função
    '''
    try:
        query = db.session.query(Usuario)
        return query
    except Exception as e:
        print(e)
        return None


def get_participantes():
    try:
        query = db.session.query(Participante)
        participantes = []
        for p in query:
            info = (p.id, p.usuario.primeiro_nome + " " + p.usuario.sobrenome)
            participantes.append(info)
        return participantes
    except Exception as e:
        print(e)
        return None



def get_atividades():
    try:
        query = db.session.query(Atividade)
        ativ = []
        for a in query:
            info = (a.id, a.tipo + ' - ' + a.titulo)
            ativ.append(info)
        return ativ
    except Exception as e:
        print(e)
        return None

def get_participantes_da_atividade_json(id):
    '''
    Retorna uma lista de dicionários de usuários para ser usado na página de email cusmotizado
    '''
    query = None

    if (id == 0): 
        query = db.session.query(Atividade)
    else:
        query = db.session.query(Atividade).filter_by(id=id)
    
    query = query.first()
    ativParticipantes =  query.participantes

    participantes = []

    for p in ativParticipantes:
        usuario = p.usuario
        participante = {'id':usuario.id, 'nome':(usuario.primeiro_nome + " " + usuario.sobrenome), 'email':usuario.email}
        participantes.append(participante)

    return participantes



def get_participantes_sem_kit():
    try:
        query = db.session.query(Participante).filter_by(pacote=0)
        participantes = []
        for p in query:
            info = (p.id, p.usuario.primeiro_nome + " " + p.usuario.sobrenome)
            participantes.append(info)
        return participantes
    except Exception as e:
        print(e)
        return None


def cadastra_objeto_generico(objeto):
    try:
        db.session.add(objeto)
        db.session.flush()
        db.session.commit()
        return objeto

    except Exception as e:
        print(e)
        return None


def verifica_outro_escolhido(campo, objeto):
    if campo.data == 0:
        return cadastra_objeto_generico(objeto).id
    else:
        return campo.data


def get_path_anexo(anexoBase, anexoPasta, complemento, usuario, extencao):
    '''
    Retorna uma lista dos arquivos que serão anexados.
    '''
    # Tipo de modificação aplicada nos nomes dos anexos, novas motificações poder ser adicionadas aqui
    if complemento == 0: # Mesmo arquivo para todos
        return (anexoPasta + anexoBase + extencao)
    elif complemento == 1: # Nome CamelCase
        return (anexoPasta + anexoBase + usuario.primeiro_nome + usuario.sobrenome.replace(" ", "") + extencao)
    elif complemento == 2: # ID
        return (anexoPasta + anexoBase + usuario.id + extencao)
    else:
        return None