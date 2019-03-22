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
