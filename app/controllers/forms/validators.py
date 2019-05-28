import re

from wtforms.validators import ValidationError

from app.models.models import *

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

def transporte_ida_volta_selecionado():
    def _transporte_ida_volta_selecionado(form, field):
        if form.transporte_ida_volta.data is not True and field.data is not '':
            raise ValidationError("Selecione a opção de usar transporte de ida e volta")
    return _transporte_ida_volta_selecionado

def transporte_sanca_selecionado():
    def _transporte_sanca_selecionado(form, field):
        if form.transporte_sanca.data is not True and field.data is not '':
            raise ValidationError("Selecione a opção de usar transporte para São Carlos")
    return _transporte_sanca_selecionado

def hospedagem_selecionada():
    def _hospedagem_selecionada(form, field):
        if form.hospedagem.data is not True and field.data is not '':
            raise ValidationError("Selecione a opção de hospedagem")
    return _hospedagem_selecionada
