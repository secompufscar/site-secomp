from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
import os
from app import app

SENHA_DB = os.getenv("SENHA_DB")
IP_DB = os.getenv("IP_DB")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:%s@%s/db' % (SENHA_DB, IP_DB)
db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    participantes_associados = db.relationship('participante', backref='usuario', lazy=True)
    email = Column(String(45), unique=True, nullable=False)
    senha = Column(String(256), nullable=False)
    ultimo_login = Column(DateTime, nullable=False)
    data_cadastro = Column(DateTime, nullable=False)
    permissao = Column(Integer, nullable=False)
    primeiro_nome = Column(String(45), nullable=False)
    ult_nome = Column(String(45), nullable=False)
    curso = Column(String(45), nullable=False)
    cidade = Column(String(45), nullable=False)
    instituicao = Column(String(45), nullable=False)
    token_email = Column(String(90), nullable=False)
    data_nasc = Column(DateTime, nullable=False)
    autenticado = Column(Boolean, default=False)
    email_verificado = Column(Boolean, default=False)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.autenticado

    def is_anonymous(self):
        return False


class Participante(db.Model):
    __tablename__ = 'participante'
    id = Column(Integer, db.ForeignKey('usuario.id'), primary_key=True)
    edicao = Column(Integer, nullable=False)
    pacote = Column(Boolean, nullable=False)
    pagamento = Column(Boolean, nullable=False)
    camiseta = Column(String(3))
    data_inscricao = Column(DateTime, nullable=False)
    credenciado = Column(Boolean, nullable=False)

class Ministrante(db.Model):
    __tablename__ = 'ministrante'
    id = Column(Integer, db.ForeignKey('ministrante.id'), primary_key=True)
    pagar_gastos = Column(Boolean, nullable=False)
    data_chegada_sanca = Column(Date, nullable=False)
    data_saida_sanca = Column(Date, nullable=False)
    precisa_acomodacao = Column(Boolean, nullable=False)
    observacoes = Column(String(500))
    nome = Column(String(45), nullable=False)
    email = Column(String(45), nullable=False)
    tel = Column(String(45), nullable=False)
    profissao = Column(String(45), nullable=False)
    empresa_univ = Column(String(45), nullable=False)
    biografia = Column(String(1024), nullable=False)
    foto = Column(String(128), nullable=False)
    tamanho_cam = Column(String(5), nullable=False)
    facebook = Column(String(45))
    twitter = Column(String(45))
    linkedin = Column(String(45))
    github = Column(String(45))

relacao_atividade_participante = Table('relacao_atividade_participante',
                                       Column('id_atividade', Integer, ForeignKey('atividade.id'), primary_key=True),
                                       Column('id_participante', Integer, ForeignKey('participante.id'), primary_key=True))

class Atividade(db.Model):
    __tablename__ = 'atividades'
    id = Column(Integer, primary_key=True)
    vagas_totais = Column(Integer, nullable=False)
    vagas_disponiveis = Column(Integer, nullable=False)
    pre_requisitos = Column(String(512), nullable=False)
    pre_requisitos_recomendados = Column(String(512), nullable=False)
    ativo = Column(Boolean, nullable=False)
    tipo = Column(Integer, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    local = Column(String(45), nullable=False)
    titulo = Column(String(45), nullable=False)
    descricao = Column(String(1024), nullable=False)
    recursos_necessarios = Column(String(512), nullable=False)
    observacoes = Column(String(512), nullable=False)
    ministrante = db.relationship('ministrante', backref='ministrante', lazy=True)
    inscritos = db.relationship('participante', secondary=relacao_atividade_participante, lazy=True,
        backref=db.backref('atividades', lazy='subquery'))

if __name__ == "__main__":
    db.create_all()

