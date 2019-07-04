from app.models.models import *
from app.controllers.constants import EDICAO_ATUAL


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


def valida_url_codigo(usuario, codigo):
    atividade = db.session.query(Atividade).filter_by(url_codigo=codigo).first()
    ministrante = db.session.query(Ministrante).filter_by(usuario=usuario).first()
    emails = []
    if atividade is None:
        return False, None, None
    for m in atividade.ministrantes:
        emails.append(m.usuario.email)
    if(usuario is None):
        if (atividade is not None):
            return True, atividade, emails
        else:
            return False, atividade, emails
    else:
        if(atividade is not None and ministrante.usuario.email in emails):
            return True, atividade, emails
        else:
            return False, atividade, emails


def get_id_evento_atual():
    evento = db.session.query(Evento).filter_by(edicao=EDICAO_ATUAL).first()
    return evento.id

def confirmacao_atividade_ministrante(usuario):
    atividade = None
    if usuario.ministrante is not None:
        r = db.session.query(RelacaoAtividadeMinistrante).filter(RelacaoAtividadeMinistrante.id_ministrante == usuario.ministrante.id,
                                                                                                RelacaoAtividadeMinistrante.confirmado == None).first()
        if r is not None:
            atividade = db.session.query(Atividade).get(r.id_atividade)
    if atividade is not None:
        if atividade.tipo.nome == "Palestra":
            view = 'cadastro_palestra'
        elif atividade.tipo.nome == "Palestra Empresarial":
            view = 'cadastro_palestra_empresarial'
        elif atividade.tipo.nome == "Minicurso":
            view = 'cadastro_minicurso'
        elif atividade.tipo.nome == "Mesa Redonda":
            view = 'cadastro_mesa_redonda'
        elif atividade.tipo.nome == "Feira de Projetos":
            view = 'cadastro_feira_projetos'
        return False, atividade, view
    else:
        return True, None, None

def get_tipos_atividade():
    minicurso = db.session.query(TipoAtividade).filter_by(nome='Minicurso').first()
    palestra = db.session.query(TipoAtividade).filter_by(nome='Palestra').first()
    mesa_redonda = db.session.query(TipoAtividade).filter_by(nome='Mesa Redonda').first()
    palestra_empresarial = db.session.query(TipoAtividade).filter_by(nome='Palestra Empresarial').first()
    feira_projetos = db.session.query(TipoAtividade).filter_by(nome='Feira Projetos').first()
    workshop = db.session.query(TipoAtividade).filter_by(nome='Workshop').first()

    tipo_atividade = {
        'minicurso': minicurso,
        'palestra' : palestra,
        'mesa_redonda': mesa_redonda,
        'palestra_empresarial': palestra_empresarial,
        'feira_projetos': feira_projetos,
        'workshop': workshop
    }
    return tipo_atividade
