import datetime

from flask import current_app
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from app.controllers.constants import *
from app.controllers.functions.helpers import get_score_evento, get_id_evento_atual, kit_pago
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
    except SQLAlchemyError:
        db.session.rollback()
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
        camisetas = db.session.query(Camiseta).filter(Camiseta.pagamento.efetuado == True,
                                                      Camiseta.pagamento.id_participante == participante.id).all()
        tamanhos = []
        for camiseta in camisetas:
            tamanhos.append(camiseta.tamanho)
        info = {
            "titulo": str(evento.edicao) + "ª SECOMP UFSCar",
            "data_inscricao": participante.data_inscricao,
            "presencas": atividades,
            "kit_pago": kit_pago(participante),
            "camisetas": tamanhos,
                "opcao_coffee": participante.opcao_coffee,
                "score_geral": get_score_evento(edicao)
        }
        return info
    except SQLAlchemyError:
        db.session.rollback()
        return None


def get_patrocinadores_ativos():
    try:
        info = []
        pats = db.session.query(Patrocinador).filter_by(ativo_site=True)
        for p in pats:
            aux = {
                "nome": p.nome_empresa,
                "cota": p.cota.nome,
                "site": p.link_website,
                "ordem_site": p.ordem_site,
                "logo": p.logo
            }
            info.append(aux)
        return info
    except Exception as e:
        print(e)
        return None


def get_atividades(edicao):
    try:
        atividades = db.session.query(Evento).filter_by(edicao=edicao).atividades
        ativ_json = []
        for a in atividades:
            ministrantes = []
            for m in a.ministrantes:
                ministrantes.append(m.ministrante.nome)
                ministrantes = []
                for m in a.ministrantes:
                    ministrantes.append(m.ministrante.nome)
            info = {
                "tipo": a.tipo.nome,
                "vagas_totais": a.vagas_totais,
                "vagas_disponiveis": a.vagas_disponiveis,
                "data_hora": a.data_hora,
                "local": a.local,
                "titulo": a.titulo,
                "descricao": a.descricao,
                "area": a.areas.nome,
                "observacoes": a.observacoes,
                "ministrantes": ministrantes
            }
            ativ_json.append(info)
        return ativ_json
    except SQLAlchemyError as err:
        db.session.rollback()
        return "Erro"


def get_url_tipo(tipo):
    if tipo == "Palestra":
        return "palestra"
    elif tipo == "Minicurso":
        return "minicurso"
    elif tipo == "Mesa Redonda":
        return "mesa-redonda"
    elif tipo == "Feira de Projetos":
        return "feira-projetos"
    elif tipo == "Roda de Conversa":
        return "roda-conversa"
    elif tipo == "Workshop":
        return "workshop"
    elif tipo == "Palestra Empresarial":
        return "palestra-empresarial"


def get_urls_conteudo(url_root):
    try:
        atividades = db.session.query(Atividade).join(TipoAtividade).filter(Atividade.id_evento==get_id_evento_atual(), TipoAtividade.nome != "Outro").all()
        info_urls = []
        emails = []
        for atividade in atividades:
            titulo = atividade.titulo

            if atividade.titulo is None or atividade.titulo == '':
                titulo = "-"
                emails = []
            for ministrante in atividade.ministrantes:
                relacao = db.session.query(RelacaoAtividadeMinistrante).filter_by(id_ministrante=ministrante.id, id_atividade=atividade.id).first()
                if relacao.confirmado == True:
                    confirmado = True
                else:
                    confirmado = False
                emails.append({"email": ministrante.usuario.email, "confirmado": confirmado })
                info = {
                        "id" : atividade.id,
                        "tipo" : atividade.tipo.nome,
                        "titulo_atividade": titulo,
                        "codigo_url" : atividade.url_codigo,
                        "url": str(url_root) + 'area-conteudo/cadastro-atividade/' + str(get_url_tipo(atividade.tipo.nome)) + '/' + str(atividade.url_codigo),
                        "emails": emails
                }
            info_urls.append(info)
        return info_urls
    except SQLAlchemyError:
        db.session.rollback()
        return None


def get_equipe(database=True):
    try:
        info_equipe = {}
        if database:
            diretorias = db.session.query(Diretoria).all()
            if len(diretorias) > 0:
                for diretoria in diretorias:
                    info_equipe[diretoria.nome] = {}
                    for membro in diretoria.membros:
                        info_equipe[diretoria.nome][membro.nome] = {'img': membro.foto}
        else:
            import json
            import os.path as op
            filename = op.join(current_app.root_path, 'config/membros_org.json')
            with open(filename, 'r') as info_file:
                info_equipe = json.load(info_file)
        return info_equipe
    except SQLAlchemyError:
        db.session.rollback()
        return None


def get_cronograma():
    try:
        segunda = db.session.query(Atividade).filter(Atividade.data_hora_inicio > '2019-09-09 00:00:00', Atividade.data_hora_fim < '2019-09-09 23:59:00' , Atividade.id_evento==get_id_evento_atual(), Atividade.titulo!=None, Atividade.ativo==True).order_by(Atividade.data_hora_inicio).all()
        terca = db.session.query(Atividade).filter(Atividade.data_hora_inicio > '2019-09-10 00:00:00', Atividade.data_hora_fim < '2019-09-10 23:59:00', Atividade.id_evento==get_id_evento_atual(), Atividade.titulo!=None, Atividade.ativo==True).order_by(Atividade.data_hora_inicio).all()
        quarta = db.session.query(Atividade).filter(Atividade.data_hora_inicio > '2019-09-11 00:00:00', Atividade.data_hora_fim < '2019-09-11 23:59:00', Atividade.id_evento==get_id_evento_atual(), Atividade.titulo!=None, Atividade.ativo==True).order_by(Atividade.data_hora_inicio).all()
        quinta = db.session.query(Atividade).filter(Atividade.data_hora_inicio > '2019-09-12 00:00:00', Atividade.data_hora_fim < '2019-09-12 23:59:00', Atividade.id_evento==get_id_evento_atual(), Atividade.titulo!=None, Atividade.ativo==True).order_by(Atividade.data_hora_inicio).all()
        sexta = db.session.query(Atividade).filter(Atividade.data_hora_inicio > '2019-09-13 00:00:00', Atividade.data_hora_fim < '2019-09-13 23:59:00', Atividade.id_evento==get_id_evento_atual(), Atividade.titulo!=None, Atividade.ativo==True).order_by(Atividade.data_hora_inicio).all()

        return {
            "SEG" : segunda,
            "TER": terca,
            "QUA": quarta,
            "QUI": quinta,
            "SEX": sexta
        }
    except SQLAlchemyError:
        db.session.rollback()
        return "Erro"
