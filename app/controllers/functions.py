from flask import url_for
from flask_login import login_required, login_user, logout_user, current_user
from app.models.models import *
from app.controllers.constants import *
import datetime

def check_password(x, y):
	#Esperar criptografia para programar a função que verificará a integridade da senha
	return True

def enviarEmailConfirmacao(app, email, token): #Envia email para validação do email
	from flask_mail import Mail, Message

	mail = Mail(app)

	#Cria a msg, Assunto, De, Para
	msg = Message('Confirmação do Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
	#Str com o link da verificação + tokmethods=['POST', 'GET']
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

def get_score_evento(edicao):
	return 10000

def get_dicionario_eventos_participante():
	info_eventos = []
	agora = datetime.datetime.now()
	participantes = db.session.query(Participante).filter_by(id_usuario=current_user.id).all()
	ja_participa = False
	for participante in participantes:
		evento = participante.evento
		if evento.edicao != EDICAO_ATUAL:
			info = {
				"titulo": str(evento.edicao) + "ª SECOMP UFSCar",
				"edicao": evento.edicao,
				"participantes": len(evento.participantes),
				"url": "https://0.0.0.0:5000/dashboard-usuario/evento/" + str(evento.edicao),
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
		"url": "https://0.0.0.0:5000/dashboard-usuario/evento/" + str(evento.edicao),
		"inscricao": inscricao
	}
	info_eventos.append(info)
	return info_eventos

def get_dicionario_info_evento(edicao):
	evento = db.session.query(Evento).filter_by(edicao=edicao).first()
	participante = db.session.query(Participante).filter_by(id_evento=evento.id, id_usuario=current_user.id).first()
	presencas = participante.presencas
	atividades = []
	for presenca in presencas:
		atividades.append(presenca.atividades.titulo)

	info = {
		"titulo": str(evento.edicao) + "ª SECOMP UFSCar",
		"data_inscricao" : participante.data_inscricao,
		"presencas": atividades,
		"kit_pago": participante.pagamento,
		"camiseta": participante.camiseta,
		"opcao_coffee": participante.opcao_coffee,
		"score_geral": get_score_evento(edicao)
	}
	return info
