import datetime

from flask import url_for
from flask_login import current_user
from flask_mail import Mail, Message

from app.controllers.constants import *
from app.models.models import *


# Envia email para validação do email
def enviarEmailConfirmacao(app, email, token):

    mail = Mail(app)

    # Cria a msg, Assunto, De, Para
    msg = Message('Confirmação do Email',
                  sender=app.config['MAIL_USERNAME'], recipients=[email])
    # Str com o link da verificação + tokmethods=['POST', 'GET']
    link = url_for('verificacao', token=token, _external=True)
    msg.body = '{}'.format(link)

    try:
        mail.send(msg)  # Envia o email
    except Exception as e:  # Erros mais prováveis são devivo ao email_config, printa error em um arquivo
        try:
            log = open('logMailError.txt', 'a+')
            log.write('{} {} {}\n'.format(str(e), email,
                                          strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
            log.close()
        except:
            pass


def enviarEmailDM(app, nome, email, mensagem):
    mail = Mail(app)

    msg = Message('Mensagem de {}'.format(
        nome), sender=app.config['MAIL_USERNAME'], recipients=app.config['MAIL_DM'])
    msg.body = '{}\nEmail: {}\n\n{}'.format(nome, email, mensagem)

    try:
        mail.send(msg)  # Envia o email
    except Exception as e:  # Erros mais prováveis são devivo ao email_config, printa error em um arquivo
        try:
            log = open('logMailError.txt', 'a+')
            log.write('{} {} {} {} {}\n'.format(str(e), nome, email,
                                                mensagem, strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
            log.close()
        except:
            pass


def email_confirmado():
    usuario = current_user
    usuario = db.session.query(Usuario).filter_by(email=usuario.email).first()
    return usuario.email_verificado


def get_opcoes_cidades():
    cidades = db.session.query(Cidade).filter_by().all()
    info_cidades = []
    for cidade in cidades:
        info = (cidade.id, cidade.nome)
        info_cidades.append(info)
    return info_cidades


def get_opcoes_instituicoes():
    instituicoes = db.session.query(Instituicao).filter_by().all()
    info_instituicoes = []
    for instituicao in instituicoes:
        info = (instituicao.id, instituicao.nome)
        info_instituicoes.append(info)
    return info_instituicoes


def get_opcoes_cursos():
    cursos = db.session.query(Curso).filter_by().all()
    info_cursos = []
    for curso in cursos:
        info = (curso.id, curso.nome)
        info_cursos.append(info)
    return info_cursos


def get_opcoes_camisetas():
    camisetas = db.session.query(Camiseta).filter_by().order_by(
        Camiseta.ordem_site).all()
    info_camisetas = []
    for camiseta in camisetas:
        if camiseta.quantidade_restante > 0:
            info = (camiseta.id, camiseta.tamanho)
            info_camisetas.append(info)

    return info_camisetas


def get_dicionario_usuario(usuario):
    info = {
        "nome": usuario.primeiro_nome + ' ' + usuario.sobrenome,
        "email": usuario.email,
        "curso": usuario.curso,
        "instituicao": usuario.instituicao,
        "data_nasc": usuario.data_nascimento
    }
    return info

def get_score_evento(edicao):
    return 10000

# Função usada na dashboard do usuário


def get_dicionario_eventos_participante(base_url):
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
    evento = db.session.query(Evento).filter_by(edicao=EDICAO_ATUAL).first()
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

# Função usada na página de informações de um determinado evento


def get_dicionario_info_evento(edicao):
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
        "camiseta": participante.camiseta,
        "opcao_coffee": participante.opcao_coffee,
        "score_geral": get_score_evento(edicao)
    }
    return info
