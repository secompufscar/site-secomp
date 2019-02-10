from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from datetime import datetime
from enum import Enum
from app import app

db = SQLAlchemy(app)

class Permissao(Enum):
    USUARIO = 0
    ADMIN = 1
    SUPER_ADMIN = 2


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    participantes_associados = db.relationship('Participante', backref='usuario', lazy=True)
    email = Column(String(64), unique=True, nullable=False)
    senha = Column(String(256), nullable=False)
    primeiro_nome = Column(String(64), nullable=False)
    ultimo_nome = Column(String(64), nullable=False)
    curso = Column(String(64), nullable=False)
    cidade = Column(String(64), nullable=False)
    instituicao = Column(String(64), nullable=False)
    data_nascimento = Column(DateTime, nullable=False)
    permissao = Column(Integer, nullable=False)
    autenticado = Column(Boolean, default=False)
    token_email = Column(String(90), nullable=False)
    email_verificado = Column(Boolean, default=False)
    ultimo_login = Column(DateTime, default=datetime.now())
    data_cadastro = Column(DateTime, nullable=False)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.autenticado

    def is_anonymous(self):
        return False
    

class Participante(db.Model):
    __tablename__ = 'participantes'
    id = Column(Integer, db.ForeignKey('usuario.id'), primary_key=True)
    edicao = Column(Integer, nullable=False)
    pacote = Column(Boolean, nullable=False)
    pagamento = Column(Boolean, nullable=False)
    camiseta = Column(String(3))
    data_inscricao = Column(DateTime, nullable=False)
    credenciado = Column(Boolean, nullable=False)
    atividades = db.relationship('Atividade', secondary='participante_em_atividade', lazy=True)


class Ministrante(db.Model):
    __tablename__ = "ministrantes"
    id = Column(Integer, primary_key=True)
    pagar_gastos = Column(Boolean, nullable=False)
    data_chegada_sanca = Column(Date, nullable=False)
    data_saida_sanca = Column(Date, nullable=False)
    precisa_acomodacao = Column(Boolean, nullable=False)
    observacoes = Column(String(512))
    nome = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    telefone = Column(String(64), nullable=False)
    profissao = Column(String(64), nullable=False)
    empresa_univ = Column(String(64), nullable=False)
    biografia = Column(String(1024), nullable=False)
    foto = Column(String(128), nullable=False)
    tamanho_cam = Column(String(8), nullable=False)
    facebook = Column(String(64))
    twitter = Column(String(64))
    linkedin = Column(String(64))
    github = Column(String(64))


class ParticipanteEmAtividade (db.Model):
    __tablename__ = 'participante_em_atividade'
    id_atividade = Column(Integer, db.ForeignKey('atividade.id'), primary_key=True)
    id_participante = Column(Integer, db.ForeignKey('participante.id'), primary_key=True)


class Atividade(db.Model):
    __tablename__ = 'atividades'
    id = Column(Integer, db.ForeignKey('ministrante.id'), primary_key=True)
    vagas_totais = Column(Integer, nullable=False)
    vagas_disponiveis = Column(Integer, nullable=False)
    pre_requisitos = Column(String(512), nullable=False)
    pre_requisitos_recomendados = Column(String(512), nullable=False)
    ativo = Column(Boolean, nullable=False)
    tipo = Column(Integer, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    local = Column(String(64), nullable=False)
    titulo = Column(String(64), nullable=False)
    descricao = Column(String(1024), nullable=False)
    recursos_necessarios = Column(String(512), nullable=False)
    observacoes = Column(String(512), nullable=False)
    ministrante = db.relationship('Ministrante', backref='atividade', lazy=True)
    inscritos = db.relationship('Participante', secondary='participante_em_atividade', lazy='subquery', 
	backref=db.backref('atividade', lazy=True))

