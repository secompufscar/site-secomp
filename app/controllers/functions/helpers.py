from app.models.models import *


def get_score_evento(edicao):
    return 10000


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

