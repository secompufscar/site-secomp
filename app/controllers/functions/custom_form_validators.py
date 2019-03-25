from flask_wtf import FlaskForm
from wtforms.validators import ValidationError
from app.models.models import *
from flask_login import login_required, login_user, logout_user
import re

def email_existe():
    mensagem = "Este email já está cadastrado!"
    def _email_existe(form, field):
        usuario = db.session.query(Usuario).filter_by(email=field.data).first()
        if usuario is not None:
            raise ValidationError(mensagem)
    return _email_existe

def so_letras():
    mensagem = "Entrada inválida (deve conter apenas letras)"
    def _so_letras(form, field):
        s = str(field.data)
        if re.search("[^a-zA-ZÁÂÃÀÇÉÊÍÓÔÕÚÜáâãàçéêíóôõúü\s]", s):
            raise ValidationError(mensagem)
    return _so_letras
