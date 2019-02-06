from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from app.controllers.constants import *

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message=ERRO_EMAIL), Length(min=1, max=254)])
    senha = PasswordField('Senha', validators=[InputRequired(), Length(min=8, max=20)])

class CadastroForm(FlaskForm):
    primeiro_nome = StringField('Primeiro Nome', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=1, max=30)])
    sobrenome = StringField('Sobrenome', validators=[InputRequired(), Length(min=1, max=100)])
    email = StringField('Email', validators=[InputRequired(), Email(message=ERRO_EMAIL), Length(min=1, max=254)])
    senha = PasswordField('Senha', validators=[InputRequired(), EqualTo('confirmacao', message=ERRO_COMPARA_SENHAS), Length(min=8, max=20)])
    confirmacao = PasswordField('Confirmação de Senha', validators=[InputRequired(), Length(min=8, max=20)])
    curso = SelectField('Curso', choices=escolhas_curso, id= "curso")
    instituicao = SelectField('Instituição', choices=escolhas_instituicao, id= "instituicao", default="UFSCar")
    cidade = SelectField('Cidade', choices=escolhas_cidade, id= "cidade", default="São Carlos")
    data_nasc = DateField('Data de Nascimento', format='%d/%m/%Y', id="data_nasc")

class CadastroInformacoesPessoais(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=1, max=80)])
    email = StringField('Email', validators=[InputRequired(), Email(message=ERRO_EMAIL), Length(min=1, max=254)])
    telefone = StringField('Telefone', validators=[InputRequired(), Length(min=1, max=11)])
    profissao = StringField('Profissão', validators=[InputRequired(), Length(min=1, max=64)])
    empresa_universidade = StringField('Empresa/Universidade')
    biografia = StringField('Biografia', validators=[InputRequired(), Length(min=1, max=1500)])
    foto = StringField('Foto')
    tamanho_camiseta = SelectField('Tamanho de Camiseta', choices=escolhas_camiseta, id="tamanho_camiseta")
    facebook = StringField('Facebook')
    twitter = StringField('Twitter')
    linkedin = StringField('Linkedin')
    github = StringField('GitHub')

class CadastroInformacoesMinicurso(FlaskForm):
    titulo = StringField('Título', validators=[InputRequired(), Length(min=1,max=64)])
    area = SelectField('Área', validators=[InputRequired()])
    descricao = StringField('Descrição', validators=[InputRequired(), Length(min=1,max=1024)])
    pre_requisitos = StringField('Pré-requisitos do participante')
    planejamento = StringField('Planejamento de como será')
    apresentacao_extra = StringField('Apresentação Extra')
    material = StringField('Descrição')
    requisitos_hardware = StringField('Requisitos de Hardware')
    requisitos_software = StringField('Requisitos de Software')
    dicas_instalacao = StringField('Dicas para instalação dos softwares necessários')
    observacoes = StringField('Observações')

class CadastroInformacoesPalestra(FlaskForm):
    titulo = StringField('Título', validators=[InputRequired(), Length(min=1,max=64)])
    area = SelectField('Área', validators=[InputRequired()])
    descricao = StringField('Descrição', validators=[InputRequired(), Length(min=1,max=1024)])
    requisitos_hardware = StringField('Requisitos de Hardware')
    planejamento = StringField('Planejamento de como será')
    apresentacao_extra = StringField('Apresentação Extra')
    material = StringField('Descrição')
    observacoes = StringField('Observações')

class CadastroInformaçõesLocomoçõesEstadia(FlaskForm):
    cidade_origem = StringField('Título', validators=[InputRequired(), Length(min=1,max=64)])
    data_chegada_sanca = DateField('Data de Chegada em São Carlos', format='%d/%m/%Y', id="data_chegada_sanca")
    data_partida_sanca = DateField('Data de Partida de São Carlos', format='%d/%m/%Y', id="data_partida_sanca")
    transporte_ida_volta = BooleanField('Requer que a SECOMP UFSCar pague por seu transporte de ida e volta')
    hotel = BooleanField('Requer que a SECOMP UFSCar pague por seu hotel?')
    transporte_sanca = BooleanField('Requer que a SECOMP UFSCar se encarregue do seu transporte dentro de São Carlos?')
    observacoes = StringField('Observações')

class CadastroAtividadeForm(FlaskForm):
   titulo = StringField('Título da Atividade', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=1, max=64)])
