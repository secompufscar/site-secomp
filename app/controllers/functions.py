from flask import url_for
from flask_login import login_required, login_user, logout_user, current_user
from app.models.models import *

def check_password(x, y):
	#Esperar criptografia para programar a função que verificará a integridade da senha
	return True

def enviarEmailConfirmacao(app, email, token): #Envia email para validação do email
	from flask_mail import Mail, Message

	mail = Mail(app)

	#Cria a msg, Assunto, De, Para
	msg = Message('Confirmação do Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
	#Str com o link da verificação + tokmethods=['POST', 'GET']en
	link = url_for('verificacao', token=token, _external=True)
	msg.body = '{}'.format(link)

	try:
		mail.send(msg) #Envia o email
	except Exception as e: #Erros mais prováveis são devivo ao email_config, printa error em um arquivo
		try:
			log = open('logMailError.txt', 'a+')
			log.write('{} {} {}\n'.format(str(e), email, strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
			log.close()
		except:
			pass
def email_confirmado():
	usuario = current_user
	usuario = db.session.query(Usuario).filter_by(email=usuario.email).first()
	return usuario.email_verificado

def get_dicionario_usuario(usuario):
	info = {
		"nome": usuario.primeiro_nome + ' ' + usuario.ult_nome,
		"email": usuario.email,
		"curso": usuario.curso,
		"instituicao": usuario.instituicao,
		"data_nasc": usuario.data_nasc
	}
	return info
