import datetime

from flask_login import current_user

from app.controllers.constants import *
from app.controllers.functions.helpers import get_score_evento, get_id_evento_atual
from app.models.models import *


def get_dicionario_usuario(usuario):
    try:
        data = str(usuario.data_nascimento).split("-")
        info = {
            "primeiro_nome": usuario.primeiro_nome,
            "sobrenome": usuario.sobrenome,
            "email": usuario.email,
            "curso": usuario.curso.nome,
            "instituicao": usuario.instituicao.nome,
            "data_nasc": f"{data[2]}/{data[1]}/{data[0]}",
            "cidade": usuario.cidade.nome,
        }
        return info
    except Exception as e:
        print(e)
        return None


def get_dicionario_eventos_participante(base_url):
    '''Função usada na dashboard do usuário'''
    try:
        info_eventos = []
        agora = datetime.now()
        participantes = db.session.query(Participante).filter_by(
            id_usuario=current_user.id).all()
        ja_participa = False
        for participante in participantes:
            evento = participante.evento
            if evento.edicao != EDICAO_ATUAL:
                info = {
                    "titulo": str(evento.edicao) + "ª SECOMP UFSCar",
                    "edicao": evento.edicao,
                    "participantes": len(evento.participantes),
                    "url": base_url + "/evento/" + str(evento.edicao),
                    "inscricao": 0
                }
                info_eventos.append(info)
            else:
                ja_participa = True
        evento = db.session.query(Evento).filter_by(
            edicao=EDICAO_ATUAL).first()
        if ja_participa == False:
            if agora >= evento.inicio_inscricoes_evento and agora < evento.fim_inscricoes_evento:
                inscricao = 1
            else:
                inscricao = 2
        else:
            inscricao = 0
        info = {
            "titulo": str(evento.edicao) + "ª SECOMP UFSCar",
            "edicao": evento.edicao,
            "participantes": len(evento.participantes),
            "url": base_url + "/evento/" + str(evento.edicao),
            "inscricao": inscricao
        }
        info_eventos.append(info)
        return info_eventos
    except Exception as e:
        print(e)
        return None


def get_dicionario_info_evento(edicao):
    '''Função usada na página de informações de um determinado evento'''
    try:
        evento = db.session.query(Evento).filter_by(edicao=edicao).first()
        participante = db.session.query(Participante).filter_by(
            id_evento=evento.id, id_usuario=current_user.id).first()
        presencas = participante.presencas
        atividades = []
        for presenca in presencas:
            atividades.append(presenca.atividades.titulo)

        info = {
            "titulo": str(evento.edicao) + "ª SECOMP UFSCar",
            "data_inscricao": participante.data_inscricao,
            "presencas": atividades,
            "kit_pago": participante.pagamento,
            "camiseta": participante.camiseta.tamanho,
                "opcao_coffee": participante.opcao_coffee,
                "score_geral": get_score_evento(edicao)
        }
        return info
    except Exception as e:
        print(e)
        return None


def get_patrocinadores():
    try:
        patrocinadores = db.session.query(Patrocinador).filter_by(ativo_site=True)
        pat_json = []
        anoAtual = 2019
        for p in patrocinadores:
            #TODO: Verificar o ano do patrocinador
            info = {
                "nome": p.nome_empresa,
                "logo": "/img/"+p.logo,
                "cota": p.cota.nome,
                "ordem_site": p.ordem_site,
                "link": p.link_website
            }
            pat_json.append({p.id:info})
        return pat_json
    except Exception as e:
        return "Erro"

def get_urls_conteudo():
    atividades = db.session.query(Atividade).filter_by(id_evento=get_id_evento_atual()).all()
    info_urls = []
    for atividade in atividades:
        titulo = atividade.titulo

        if atividade.titulo is None or atividade.titulo == '':
            titulo = "-"
        emails = []
        for ministrante in atividade.ministrantes:
            emails.append(ministrante.usuario.email)
        info = {
                "id" : atividade.id,
                "tipo" : atividade.tipo[0].nome,
                "titulo_atividade": titulo,
                "codigo_url" : atividade.url_codigo,
                "emails": emails
        }
        info_urls.append(info)
    return info_urls
