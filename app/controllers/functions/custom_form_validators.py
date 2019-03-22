from flask_wtf import FlaskForm
from wtforms.validators import ValidationError
from app.models.models import *
from flask_login import login_required, login_user, logout_user

def email_existe():
    mensagem = "Este email já está cadastrado!"
    def _email_existe(form, field):
        usuario = db.session.query(Usuario).filter_by(email=field.data).first()
        if usuario is not None:
            raise ValidationError(mensagem)
    return _email_existe
