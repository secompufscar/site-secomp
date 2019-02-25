import os

# FLASK
DEBUG = None

# FLASK WTF
SECRET_KEY = os.urandom(32)

# FLASK MAIL
MAIL_SERVER = 'smtp.zoho.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'noreply@secompufscar.com.br'
MAIL_PASSWORD= 'passmail'

# FLASK ADMIN
FLASK_ADMIN_SWATCH = 'darkly'

# SQLALCHEMY
SQLALCHEMY_DATABASE_URI = 'mysql://root:2968@localhost/db'
SQLALCHEMY_TRACK_MODIFICATIONS = True
