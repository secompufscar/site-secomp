from flask import Flask
from flask_script import Manager
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config.update(
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.zoho.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
	MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
	)



from app.controllers import routes

manager = Manager(app)
