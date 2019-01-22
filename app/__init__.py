from flask import Flask
from flask_script import Manager

app = Flask(__name__)
app.config.update(
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	#MAIL_USERNAME = env
	#MAIL_PASSWORD = env
	)

from app.controllers import routes

manager = Manager(app)

