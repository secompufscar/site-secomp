from flask import url_for
from flask_login import login_required, login_user, logout_user, current_user
from app.models.models import *
from app.controllers.constants import *

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

def enviarEmailSenha(app, email, token): #Envia email para validação do email
	from flask_mail import Mail, Message

	mail = Mail(app)

	#Cria a msg, Assunto, De, Para
	msg = Message('Confirmação do Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
	#Str com o link da verificação + tokmethods=['POST', 'GET']
	link = url_for('confirmar_alteracao_senha', token=token, _external=True)
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
	try:
		usuario = current_user
		usuario = db.session.query(Usuario).filter_by(email=usuario.email).first()
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
		camisetas = db.session.query(Camiseta).filter_by().order_by(Camiseta.ordem_site).all()
		info_camisetas = []
		for camiseta in camisetas:
			if camiseta.quantidade_restante > 0:
				info = (camiseta.id, camiseta.tamanho)
				info_camisetas.append(info)

		return info_camisetas
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
			"data_nasc": "{0}/{1}/{2}".format(data[2], data[1], data[0]),
			"cidade": usuario.cidade.nome
		}
		return info
	except Exception as e:
		print(e)
		return None

def get_score_evento(edicao):
	return 10000

#Função usada na dashboard do usuário
def get_dicionario_eventos_participante(base_url):
	try:
		info_eventos = []
		agora = datetime.now()
		participantes = db.session.query(Participante).filter_by(id_usuario=current_user.id).all()
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
	except Exception as e:
		print(e)
		return None

#Função usada na página de informações de um determinado evento
def get_dicionario_info_evento(edicao):
	try:
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
			"camiseta": participante.camiseta.tamanho,
			"opcao_coffee": participante.opcao_coffee,
			"score_geral": get_score_evento(edicao)
		}
		return info
	except Exception as e:
		print(e)
		return None
