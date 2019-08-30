import re
from flask_login import current_user

from wtforms.validators import ValidationError, DataRequired, Optional

from app.models.models import *

import warnings
from collections import Iterable

from wtforms import FileField as _FileField
from werkzeug.datastructures import FileStorage
from wtforms.validators import DataRequired, StopValidation

# Mensagens de erro possíveis nos formulários
ERRO_INPUT_REQUIRED = "Preencha esse campo."
ERRO_EMAIL = "Entre com um endereço de email válido."
ERRO_COMPARA_SENHAS = "Senhas devem ser iguais."
ERRO_TAMANHO_SENHA = "A senha deve ter entre 8 e 20 caracteres."
ERRO_EXTENSAO_INVALIDA = "Tipo de arquivo inválido, tipos aceitos: .jpg, .png, .jpeg."
ERRO_CURSO_EXISTE = "Este curso já existe"
ERRO_INSTITUICAO_EXISTE = "Esta instituição já existe"
ERRO_CIDADE_EXISTE = "Esta cidade já existe"


def email_existe():
    def _email_existe(form, field):
        usuario = db.session.query(Usuario).filter_by(email=field.data).first()
        if usuario is not None:
            raise ValidationError("Este email já está cadastrado!")
    return _email_existe


def so_letras():
    def _so_letras(form, field):
        s = str(field.data)
        if re.search(r'[^a-zA-ZÁÂÃÀÇÉÊÍÓÔÕÚÜáâãàçéêíóôõúü\s]', s):
            raise ValidationError('Entrada inválida (deve conter apenas letras)')
    return _so_letras


def erro_curso_existe():
    def _erro_curso_existe(form, field):
        if len(field.data) > 0:
            cursos = db.session.query(Curso).filter(Curso.nome.op('regexp')(r'{}'.format(
                str(field.data)))).first()
            if cursos is not None:
                raise ValidationError(ERRO_CURSO_EXISTE)
    return _erro_curso_existe


def erro_instituicao_existe():
    def _erro_instituicao_existe(form, field):
        if len(field.data) > 0:
            instituicoes = db.session.query(Instituicao).filter(Instituicao.nome.op('regexp')(r'{}'.format(
                str(field.data)))).first()
            if instituicoes is not None:
                raise ValidationError(ERRO_INSTITUICAO_EXISTE)
    return _erro_instituicao_existe


def erro_cidade_existe():
    def _erro_cidade_existe(form, field):
        if len(field.data) > 0:
            cidades = db.session.query(Cidade).filter(Cidade.nome.op('regexp')(r'{}'.format(
                str(field.data)))).first()
            if cidades is not None:
                raise ValidationError(ERRO_CIDADE_EXISTE)
    return _erro_cidade_existe


def tem_valor():
    def _tem_valor(form, field):
        if field.data is '' and field.data is not '1':
            raise ValidationError("Preencha com algum valor")
    return _tem_valor

def valida_email_ministrante():
    def _valida_email_ministrante(form, field):
        atividade = db.session.query(Atividade).filter_by(url_codigo=form.codigo_url).first()
        usuario = db.session.query(Usuario).filter_by(email=field.data).first()
        emails = []
        for m in atividade.ministrantes:
            emails.append(m.usuario.email)
        if field.data not in emails:
            raise ValidationError("Entre com um email válido")
        else:
            if usuario.primeiro_nome is not None:
                raise ValidationError("Este email já está cadastrado!")
    return _valida_email_ministrante

def is_valid_email(email):
    if len(email) > 7:
        return bool(re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email))

def verifica_lista_emails(emails):
    if len(emails) == 0:
        return False
    for email in emails:
        if not is_valid_email(email):
            return False
    return True


class RequiredIf(DataRequired):
    """Validator which makes a field required if another field is set and has a truthy value.
    """
    field_flags = ('requiredif',)

    def __init__(self, message=None, *args, **kwargs):
        super(RequiredIf).__init__()
        self.message = message
        self.conditions = kwargs

    # field is requiring that name field in the form is data value in the form
    def __call__(self, form, field):
        for name, data in self.conditions.items():
            other_field = form[name]
            if other_field is None:
                raise ValidationError("Preencha o campo.")
            if other_field.data == data and not field.data:
                DataRequired.__call__(self, form, field)
            Optional()(form, field)

def valida_cupom_desconto():
    def _valida_cupom_desconto(form, field):
        cupom_desconto = db.session.query(CupomDesconto).filter_by(nome=form.cupom_desconto.data, usado=False).first()
        if not(cupom_desconto is not None and cupom_desconto.usado is False):
            raise ValidationError("Este cupom não é valido")
    return _valida_cupom_desconto

class ComprovanteRequired(DataRequired):

     def __call__(self, form, field):
        if form.forma_pagamento.data == 1:
            if not (isinstance(field.data, FileStorage) and field.data):
                if self.message is None:
                    message = field.gettext('This field is required.')
                else:
                    message = self.message

                raise StopValidation(message)
