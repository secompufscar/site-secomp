from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from forms.constants import *

class CadastroForm(FlaskForm):

    primeiro_nome = StringField('Primeiro Nome', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=1, max=30)])
    sobrenome = StringField('Sobrenome', validators=[InputRequired(), Length(min=1, max=100)])
    email = StringField('Email', validators=[InputRequired(), Email(message=ERRO_EMAIL), Length(min=1, max=254)])
    senha = PasswordField('Senha', validators=[InputRequired(), EqualTo('confirmacao', message=ERRO_COMPARA_SENHAS), Length(min=8, max=20)])
    confirmacao = PasswordField('Confirmação de Senha', validators=[InputRequired(), Length(min=8, max=20)])
    curso = SelectField('Curso', choices=escolhas_curso, id= "curso")
    instituicao = SelectField('Instituição', choices=escolhas_instituicao, id= "instituicao", default="UFSCar")
    cidade = SelectField('Cidade', choices=escolhas_cidade, id= "cidade", default="São Carlos")
    data_nasc = DateField("Data de Nascimento", format="%d/%m/%Y", id="data_nasc")
