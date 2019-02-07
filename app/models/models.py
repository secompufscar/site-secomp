from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from app import app

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = Column(Integer, primary_key=True)
    participantes_associados = db.relationship('Participante', backref='usuario', lazy=True)
    email = Column(String(64), unique=True, nullable=False)
    senha = Column(String(256), nullable=False)
    ultimo_login = Column(DateTime, nullable=False)
    data_cadastro = Column(DateTime, nullable=False)
    permissao = Column(Integer, nullable=False)
    primeiro_nome = Column(String(64), nullable=False)
    ult_nome = Column(String(64), nullable=False)
    curso = Column(String(64), nullable=False)
    cidade = Column(String(64), nullable=False)
    instituicao = Column(String(64), nullable=False)
    token_email = Column(String(90), nullable=False)
    data_nasc = Column(DateTime, nullable=False)
    autenticado = Column(Boolean, default=False)
    email_verificado = Column(Boolean, default=False)
    salt = Column(String(30), nullable=False)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.autenticado

    def is_anonymous(self):
        return False


class Participante(db.Model):
    id = Column(Integer, db.ForeignKey('usuario.id'), primary_key=True)
    edicao = Column(Integer, nullable=False)
    pacote = Column(Boolean, nullable=False)
    pagamento = Column(Boolean, nullable=False)
    camiseta = Column(String(3))
    data_inscricao = Column(DateTime, nullable=False)
    credenciado = Column(Boolean, nullable=False)


class Ministrante(db.Model):
    id = Column(Integer, primary_key=True)
    pagar_gastos = Column(Boolean, nullable=False)
    data_chegada_sanca = Column(Date, nullable=False)
    data_saida_sanca = Column(Date, nullable=False)
    precisa_acomodacao = Column(Boolean, nullable=False)
    observacoes = Column(String(512))
    nome = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    tel = Column(String(64), nullable=False)
    profissao = Column(String(64), nullable=False)
    empresa_univ = Column(String(64), nullable=False)
    biografia = Column(String(1024), nullable=False)
    foto = Column(String(128), nullable=False)
    tamanho_cam = Column(String(8), nullable=False)
    facebook = Column(String(64))
    twitter = Column(String(64))
    linkedin = Column(String(64))
    github = Column(String(64))


relacao_atividade_participante = db.Table('relacao_atividade_participante',
				Column('id_atividade', Integer, db.ForeignKey('atividade.id'), primary_key=True),
                                Column('id_participante', Integer, db.ForeignKey('participante.id'), primary_key=True))


class Atividade(db.Model):
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
    ministrante = db.relationship('Ministrante', backref='ministrante', lazy=True)
    inscritos = db.relationship('Participante', secondary=relacao_atividade_participante, lazy=True,
	backref=db.backref('atividade', lazy='subquery'))
