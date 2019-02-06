from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from app import db
from app.models.relationships import *


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    email = Column(String(64), unique=True, nullable=False)
    senha = Column(String(256), nullable=False)
    ultimo_login = Column(DateTime, nullable=False)
    data_cadastro = Column(DateTime, nullable=False)
    permissao = Column(Integer, nullable=False)
    primeiro_nome = Column(String(64), nullable=False)
    sobrenome = Column(String(64), nullable=False)
    curso = Column(String(64), nullable=False)
    cidade = Column(String(64), nullable=False)
    instituicao = Column(String(64), nullable=False)
    token_email = Column(String(90), nullable=False)
    data_nasc = Column(DateTime, nullable=False)
    autenticado = Column(Boolean, default=False)
    email_verificado = Column(Boolean, default=False)
    salt = Column(String(30), nullable=False)
    participantes_associados = db.relationship('Participante', backref='usuario', lazy=True)

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
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, db.ForeignKey('usuario.id'))
    edicao = Column(Integer, nullable=False)
    pacote = Column(Boolean, nullable=False)
    pagamento = Column(Boolean, nullable=False)
    camiseta = Column(String(3))
    data_inscricao = Column(DateTime, nullable=False)
    credenciado = Column(Boolean, nullable=False)
    atividade = db.relationship('Atividade', secondary=relacao_atividade_participante, lazy=True,
        back_populates='participante')



class Ministrante(db.Model):
    __tablename__ = 'ministrante'
    id = Column(Integer, primary_key=True)
    nome_completo = Column(String(80), nullable=False)
    email = Column(String(64), nullable=False)
    telefone = Column(String(64), nullable=False)
    profissao = Column(String(64), nullable=False)
    empresa_universidade = Column(String(64), nullable=False)
    biografia = Column(String(1500), nullable=False)
    foto = Column(String(128))
    tamanho_camiseta = Column(String(8), nullable=False)
    facebook = Column(String(64))
    twitter = Column(String(64))
    linkedin = Column(String(64))
    github = Column(String(64))
    cidade_origem = Column(String(64))
    data_chegada_sanca = Column(Date, nullable=False)
    data_saida_sanca = Column(Date, nullable=False)
    transporte_ida_volta = Column(Boolean, nullable=False)
    hotel = Column(Boolean, nullable=False)
    transporte_sanca = Column(Boolean, nullable=False)
    observacoes = Column(String(512))

class Atividade(db.Model):
    __tablename__ = 'atividade'
    id = Column(Integer, primary_key=True)
    titulo = Column(String(64), nullable=False)
    area = Column(String(64), nullable=False)
    descricao = Column(String(1024), nullable=False)
    observacoes = Column(String(512))
    pre_requisitos = Column(String(512), nullable=False)
    planejamento = Column(String(1024))
    apresentacao_extra = Column(String(1024))
    material = Column(String(1024))
    requisitos_hardware = Column(String(512))
    requisitos_software = Column(String(512))
    dicas_instalacao = Column(String(1024))
    vagas_totais = Column(Integer, nullable=False)
    vagas_disponiveis = Column(Integer, nullable=False)
    ativo = Column(Boolean, nullable=False)
    tipo = Column(Integer, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    local = Column(String(64), nullable=False)
    ministrante = db.relationship('Ministrante', secondary=relacao_atividade_ministrante, lazy=True,
        back_populates='atividade')
    participante = db.relationship('Participante', secondary=relacao_atividade_participante, lazy=True,
        back_populates='atividade')

#if __name__ == "__main__":
#    db.create_all()

