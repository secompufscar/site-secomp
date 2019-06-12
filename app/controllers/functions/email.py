from time import strftime, gmtime

from flask import url_for, render_template, current_app
from flask_login import current_user
from flask_mail import Mail, Message

from app.models.models import db, Usuario
from app.controllers.functions.helpers import get_usuarios_query, get_path_anexo

mail = Mail()

_teste = {
    "assunto": 'Teste',  # assunto do email
    "nome": 'Pessoa',  # nome do destinatário
        "titulo": "EMAIL TESTE",
    "email": 'ti@secompufscar.com.br',  # email destino
    "template": 'email/teste.html',  # path do template (raiz dentro do diretório 'templates')
    "footer": 'TI X SECOMP UFSCar'
}


def enviar_email_generico(info=None, anexo=None):
    """
    Função que envia um email genérico recebendo um dicionário, que deve ter dados obrigatórios
    (ver dicionario teste) mas pode ter dados a mais a serem passados para o template
    Por padrão a chamada da função sem argumentos enviará um email teste para o ti
    """
    if info is None:
        global _teste
        info = _teste
    msg = Message(info['assunto'], sender=('SECOMP UFSCar', str(current_app.config['MAIL_USERNAME'])),
                  recipients=[info['email']])

    print(info['template'])
    try:
        msg.html = render_template(info['template'], info=info)
        print(msg.html)

        # Parte que cuida dos anexos
        if not (anexo is None or anexo == []):
            for fileName in anexo:
                try:
                    fp = open(fileName, "r")

                    # Verifica a extenção do arquivo
                    if not fileName.find(".png") == -1:
                        msg.attach(fileName, "image/png", fp.read())
                    elif not fileName.find(".pdf") == -1:
                        msg.attach(fileName, "application/pdf", fp.read())
                    else:
                        msg.attach(fileName, "text/plain", fp.read())

                    fp.close()
                except Exception as e:
                    print(e)
                    return

    except Exception as e:
        print(e)
        return

    try:
        global mail
        print(msg)
        mail.send(msg)
    except Exception as e:  # Erros mais prováveis são devido ao email_config, printa error em um arquivo
        try:
            log = open('logMailError.txt', 'a+')
            log.write(f"{str(e)} {info['email']} {strftime('%a, %d %b %Y %H:%M:%S', gmtime())}\n")
            log.close()
        except Exception:
            return


def enviar_email_confirmacao(usuario, token):
    """
    Envia email para validação do email
    """
    # Cria a msg, Assunto, De, Para
    link = url_for('users.verificacao', token=token, _external=True)
    info = {"assunto": 'Confirmação de Email',
            "nome": usuario.primeiro_nome,
            "titulo": 'CONFIRMAÇÃO DE EMAIL',
            "email": usuario.email,
            "template": 'email/confirmacao_de_email.html',
            "link": str(link),
            "footer": 'TI X SECCOMP UFSCar'
            }
    enviar_email_generico(info)


def enviar_email_dm(nome, email, mensagem):
    msg = Message(f'Mensagem de {nome}',
                  sender=current_app.config['MAIL_USERNAME'], recipients=current_app.config['MAIL_DM'])
    msg.body = f'{nome}\nEmail: {email}\n\n{mensagem}'

    try:
        global mail
        mail.send(msg)  # Envia o email
    except Exception as e:  # Erros mais prováveis são devivo ao email_config, printa error em um arquivo
        try:
            log = open('logMailError.txt', 'a+')
            log.write(f'{str(e)} {email} {strftime("%a, %d %b %Y %H:%M:%S", gmtime())}\n')
            log.close()
        except Exception:
            return


def enviar_email_senha(usuario, token):
    """
    Envia email para alteração de senha
    """
    # Cria a Msg, Assunto, De, Para
    link = url_for('users.confirmar_alteracao_senha', token=token, _external=True)
    info = {
        "assunto": 'Alteração de Senha',
        "nome": usuario.primeiro_nome,
        "titulo": 'ALTERAÇÃO DE SENHA',
        "email": usuario.email,
        "template": 'email/alteracao_senha.html',
        "link": str(link),
        "footer": 'TI X SECOMP UFSCar'
    }
    enviar_email_generico(info)


def email_confirmado():
    try:
        usuario = current_user
        usuario = db.session.query(Usuario).filter_by(
            email=usuario.email).first()
        return usuario.email_verificado
    except Exception as e:
        print(e)
        return None


def enviar_email_custon(assunto, titulo, template, temAnexo, anexoBase, anexoPasta, complemento, selecionados, extencao):
    '''
    Envia um ou mais emails customizados
    Podendo ou não ter anexo
    '''
    usuarios = get_usuarios_query()

    for i in selecionados:
        usuario = usuarios.filter_by(id=i).first()

        info = {
            "assunto": assunto,
            "nome": usuario.primeiro_nome + " " + usuario.sobrenome,
            "titulo": titulo,
            "email": usuario.email,
            "template": "email/" + template,
            "footer": 'TI X SECOMP UFSCar'
        }

        if (temAnexo):
            files = []
            files.append(get_path_anexo(anexoBase, anexoPasta, complemento, usuario, extencao))
            enviar_email_generico(info, files)
        else:
            enviar_email_generico(info, None)
