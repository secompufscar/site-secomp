import datetime

from flask import url_for
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Mail, Message

from app.models.models import *
from app.controllers.constants import *


def enviarEmailConfirmacao(app, email, token):
    ''' Envia email para validação do email'''
    mail = Mail(app)
    # Cria a msg, Assunto, De, Para
    msg = Message('Confirmação do Email',
                   sender=app.config['MAIL_USERNAME'], recipients=[email])
    # Str com o link da verificação + tokmethods=['POST', 'GET']
    link = url_for('verificacao', token=token, _external=True)
    msg.body = f'{link}'

    try:
        mail.send(msg)  # Envia o email
    except Exception as e:  # Erros mais prováveis são devivo ao email_config, printa error em um arquivo
        try:
            log = open('logMailError.txt', 'a+')
            log.write(f'{str(e)} {email} {strftime("%a, %d %b %Y %H:%M:%S", gmtime())}\n')
            log.close()
        except:
            pass


def enviarEmailDM(app, nome, email, mensagem):
    mail = Mail(app)
    msg = Message(f'Mensagem de {nome}', 
            sender=app.config['MAIL_USERNAME'], recipients=app.config['MAIL_DM'])
    msg.body = f'{nome}\nEmail: {email}\n\n{mensagem}'

    try:
        mail.send(msg)  # Envia o email
    except Exception as e:  # Erros mais prováveis são devivo ao email_config, printa error em um arquivo
        try:
            log = open('logMailError.txt', 'a+')
            log.write(f'{str(e)} {email} {strftime("%a, %d %b %Y %H:%M:%S", gmtime())}\n')
            log.close()
        except:
            pass


def enviarEmailSenha(app, email, token):
    ''' Envia email para alteração de senha'''

    mail = Mail(app)

    # Cria a msg, Assunto, De, Para
    msg = Message('Confirmação de Alteração de Senha',
                  sender=app.config['MAIL_USERNAME'], recipients=[email])
    # Str com o link da verificação + tokmethods=['POST', 'GET']
    link = url_for('confirmar_alteracao_senha', token=token, _external=True)
    msg.body = f'{link}'

    try:
        mail.send(msg)  # Envia o email
    except Exception as e:  # Erros mais prováveis são devivo ao email_config, printa error em um arquivo
        try:
            log = open('logMailError.txt', 'a+')
            log.write(f'{str(e)} {email} {strftime("%a, %d %b %Y %H:%M:%S", gmtime())}\n')
            log.close()
        except:
            pass


def email_confirmado():
    try:
        usuario = current_user
        usuario = db.session.query(Usuario).filter_by(
            email=usuario.email).first()
        return usuario.email_verificado
    except Exception as e:
        print(e)
        return None


def get_opcoes_cidades():
    try:
        cidades = db.session.query(Cidade).filter_by().all()
        info_cidades = []
        for cidade in cidades:
            info = (cidade.id, cidade.nome)
            info_cidades.append(info)
        return info_cidades
    except Exception as e:
        print(e)
        return None


def get_opcoes_instituicoes():
    try:
        instituicoes = db.session.query(Instituicao).filter_by().all()
        info_instituicoes = []
        for instituicao in instituicoes:
            info = (instituicao.id, instituicao.nome)
            info_instituicoes.append(info)
        return info_instituicoes
    except Exception as e:
        print(e)
        return None


def get_opcoes_cursos():
    try:
        cursos = db.session.query(Curso).filter_by().all()
        info_cursos = []
        for curso in cursos:
            info = (curso.id, curso.nome)
            info_cursos.append(info)
        return info_cursos
    except Exception as e:
        print(e)
        return None


def get_opcoes_camisetas():
    try:
        camisetas = db.session.query(Camiseta).filter_by().order_by(
            Camiseta.ordem_site).all()
        info_camisetas = []
        for camiseta in camisetas:
            if camiseta.quantidade_restante > 0:
                info = (camiseta.id, camiseta.tamanho)
                info_camisetas.append(info)

        return info_camisetas
    except Exception as e:
        print(e)
        return None

def get_participantes():
    try:
        query = db.session.query(Participante)
        participantes = []
        for p in query:
            info = (p.id, p.usuario.nome + " " + p.usuario.sobrenome)
            participantes.append(info)
        return participantes
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


def get_score_evento(edicao):
    return 10000


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


def get_opcoes_cotas_patrocinadores():
    try:
        cotas_data = db.session.query(CotaPatrocinio).filter_by().order_by(
            CotaPatrocinio.nome).all()
        cotas = []

        for cota in cotas_data:
            info_cota = (cota.id, cota.nome)
            cotas.append(info_cota)

        return cotas
    except Exception as e:
        return None


def erro_curso_existe():

    def _erro_curso_existe(form, field):
        cursos = db.session.query(Curso).filter(Curso.nome.op('regexp')(r"^[a-zA-Zãêç\s]+$"))
        if cursos is not None:
            raise ValidationError(ERRO_CURSO_EXISTE)

    return _erro_curso_existe


def erro_instituicao_existe():

    def _erro_instituicao_existe(form, field):
        instituicoes = db.session.query(Instituicao).filter(Instituicao.nome.op('regexp')(r"^[a-zA-Zãêç\s]+$"))
        if instituicoes is not None:
            raise ValidationError(ERRO_INSTITUICAO_EXISTE)

    return _erro_instituicao_existe


def erro_cidade_existe():

    def _erro_cidade_existe(form, field):
        cidades = db.session.query(Cidade).filter(Cidade.nome.op('regexp')(r"^[a-zA-Zãêç\s]+$"))
        if cidades is not None:
            raise ValidationError(ERRO_CIDADE_EXISTE)

    return _erro_cidade_existe


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
