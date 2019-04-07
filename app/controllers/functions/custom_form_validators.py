from wtforms.validators import ValidationError
from app.models.models import *
from flask_login import login_required, login_user, logout_user
from app.controllers.constants import *
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

def erro_curso_existe():
    def _erro_curso_existe(form, field):
        if len(field.data) > 0:
            cursos = db.session.query(Curso).filter(Curso.nome.op('regexp')(r"{}".format(str(field.data)))).first()
            if cursos is not None:
                raise ValidationError(ERRO_CURSO_EXISTE)

    return _erro_curso_existe


def erro_instituicao_existe():

    def _erro_instituicao_existe(form, field):
        if len(field.data) > 0:
            instituicoes = db.session.query(Instituicao).filter(Instituicao.nome.op('regexp')(r"{}".format(str(field.data)))).first()
            if instituicoes is not None:
                raise ValidationError(ERRO_INSTITUICAO_EXISTE)

    return _erro_instituicao_existe


def erro_cidade_existe():

    def _erro_cidade_existe(form, field):
        if len(field.data) > 0:
            cidades = db.session.query(Cidade).filter(Cidade.nome.op('regexp')(r"{}".format(str(field.data)))).first()
            if cidades is not None:
                raise ValidationError(ERRO_CIDADE_EXISTE)

    return _erro_cidade_existe
