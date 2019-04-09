import re

from wtforms.validators import ValidationError

from app.controllers.constants import *
from app.models.models import *


def email_existe():
    def _email_existe(field):
        usuario = db.session.query(Usuario).filter_by(email=field.data).first()
        if usuario is not None:
            raise ValidationError("Este email já está cadastrado!")
    return _email_existe


def so_letras():
    def _so_letras(field):
        s = str(field.data)
        if re.search(r'[^a-zA-ZÁÂÃÀÇÉÊÍÓÔÕÚÜáâãàçéêíóôõúü\s]', s):
            raise ValidationError('Entrada inválida (deve conter apenas letras)')
    return _so_letras


def erro_curso_existe():
    def _erro_curso_existe(field):
        if len(field.data) > 0:
            cursos = db.session.query(Curso).filter(Curso.nome.op('regexp')(r'{}'.format(
                str(field.data)))).first()
            if cursos is not None:
                raise ValidationError(ERRO_CURSO_EXISTE)

    return _erro_curso_existe


def erro_instituicao_existe():
    def _erro_instituicao_existe(field):
        if len(field.data) > 0:
            instituicoes = db.session.query(Instituicao).filter(Instituicao.nome.op('regexp')(r'{}'.format(
                str(field.data)))).first()
            if instituicoes is not None:
                raise ValidationError(ERRO_INSTITUICAO_EXISTE)

    return _erro_instituicao_existe


def erro_cidade_existe():
    def _erro_cidade_existe(field):
        if len(field.data) > 0:
            cidades = db.session.query(Cidade).filter(Cidade.nome.op('regexp')(r'{}'.format(
                str(field.data)))).first()
            if cidades is not None:
                raise ValidationError(ERRO_CIDADE_EXISTE)

    return _erro_cidade_existe
