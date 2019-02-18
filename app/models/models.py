from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from app import app

db = SQLAlchemy(app)

relacao_atividade_participante = db.Table('relacao_atividade_participante',
Column('id', Integer, primary_key=True),
Column('id_atividade', Integer, db.ForeignKey('atividade.id')),
Column('id_participante', Integer, db.ForeignKey('participante.id')))

relacao_atividade_ministrante = db.Table('relacao_atividade_ministrante',
Column('id', Integer, primary_key=True),
Column('id_atividade', Integer, db.ForeignKey('atividade.id')),
Column('id_ministrante', Integer, db.ForeignKey('ministrante.id')))


relacao_patrocinador_evento = db.Table('relacao_patrocinador_evento',
Column('id', Integer, primary_key=True),
Column('id_patrocinador', Integer, db.ForeignKey('patrocinador.id')),
Column('id_evento', Integer, db.ForeignKey('evento.id')))

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    participantes = db.relationship('Participante', backref='usuario', lazy=True)
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
    data_nasc = Column(Date, nullable=False)
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
    __tablename__ = 'participante'
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, db.ForeignKey('usuario.id'), primary_key=False)
    id_evento = Column(Integer, db.ForeignKey('evento.id'), nullable=False)
    pacote = Column(Boolean, nullable=False)
    pagamento = Column(Boolean, nullable=False)
    camiseta = Column(String(20))
    data_inscricao = Column(DateTime, nullable=False)
    credenciado = Column(Boolean, nullable=False)
    opcao_coffee = Column(Integer, nullable=False)
    presencas = db.relationship('Presenca', backref='participante')
    atividades = db.relationship('Atividade', secondary=relacao_atividade_participante, lazy=True,
    back_populates='participantes')


class Ministrante(db.Model):
    __tablename__ = 'ministrante'
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
    atividades = db.relationship('Atividade', secondary=relacao_atividade_ministrante, lazy=True,
    back_populates='ministrantes')

class Atividade(db.Model):
    __tablename__ = 'atividade'
    id = Column(Integer, primary_key=True)
    id_ministrante = Column(Integer, db.ForeignKey('ministrante.id'))
    id_evento = Column(Integer, db.ForeignKey('evento.id'))
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
    ministrantes = db.relationship('Ministrante', secondary=relacao_atividade_ministrante, lazy=True,
    back_populates='atividades')

    participantes = db.relationship('Participante', secondary=relacao_atividade_participante, lazy=True,
    back_populates='atividades')

    presencas = db.relationship('Presenca', backref='atividade')

class Evento(db.Model):
    __tablename__ = 'evento'
    id = Column(Integer, primary_key=True)
    edicao = Column(Integer, nullable=False)
    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime, nullable=False)
    inicio_inscricoes_evento = Column(DateTime, nullable=False)
    fim_inscricoes_evento = Column(DateTime, nullable=False)
    ano = Column(Integer, nullable=False)
    participantes = db.relationship('Participante', backref='evento', lazy=True)
    presencas = db.relationship('Presenca', backref='evento', lazy=True)
    atividades = db.relationship('Atividade', backref='evento', lazy=True)
    membros_equipe = db.relationship('MembroDeEquipe', backref='evento', lazy=True)
    patrocinadores = db.relationship('Patrocinador', secondary=relacao_patrocinador_evento, lazy=True,
    back_populates='eventos')

class Presenca(db.Model):
    __tablename__ = 'presenca'
    id = Column(Integer, primary_key=True)
    data_hora_registro = Column(DateTime, nullable=False)
    id_atividade = Column(Integer, db.ForeignKey('atividade.id'), nullable=False)
    id_participante = Column(Integer, db.ForeignKey('participante.id'), nullable=False)
    id_evento = Column(Integer, db.ForeignKey('evento.id'), nullable=False)
    inscrito = Column(Boolean, nullable=False)

class MembroDeEquipe(db.Model):
    __tablename__ = 'membro_de_equipe'
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, db.ForeignKey('usuario.id'), nullable=False)
    foto = Column(String(100), nullable=True)
    email_secomp = Column(String(254), nullable=True)
    id_cargo = Column(Integer, db.ForeignKey('cargo.id'), nullable=False)
    id_diretoria = Column(Integer, db.ForeignKey('diretoria.id'), nullable=False)
    id_evento = Column(Integer, db.ForeignKey('evento.id'), nullable=False)

class Cargo(db.Model):
    __tablename__ = 'cargo'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    membros = db.relationship('MembroDeEquipe', backref='cargo', lazy=True)

class Diretoria(db.Model):
    __tablename__ = 'diretoria'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    ordem = Column(Integer, nullable=False)
    membros = db.relationship('MembroDeEquipe', backref='diretoria', lazy=True)

class Patrocinador(db.Model):
    __tablename__ = 'patrocinador'
    id = Column(Integer, primary_key=True)
    nome_empresa = Column(String(100), nullable=False)
    logo = Column(String(100), nullable=False)
    ativo_site = Column(Boolean, nullable=False)
    id_cota = Column(Integer, db.ForeignKey('cota_patrocinio.id'), nullable=False)
    ordem_site = Column(Integer, primary_key=True)
    link_website = Column(String(200), nullable=True)
    ultima_atualizacao_em = Column(DateTime, nullable=False)
    eventos = db.relationship('Evento', secondary=relacao_patrocinador_evento, lazy=True,
    back_populates='patrocinadores')

class CotaPatrocinio(db.Model):
    __tablename__ = 'cota_patrocinio'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    patrocinadores = db.relationship('Patrocinador', backref='cota_patrocinio', lazy=True)
