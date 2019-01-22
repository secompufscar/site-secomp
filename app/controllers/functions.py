def check_password(x, y):
    #Esperar criptografia para programar a função que verificará a integridade da senha
    return True

def enviarEmailConfirmacao(app, email, token): #Envia email para validação do email
	from flask_mail import Mail, Message
	
	mail = Mail(app)
	
	#Cria a msg, Assunto, De, Para
	msg = Message('Confirmação do Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
	#Str com o link da verificação + token
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