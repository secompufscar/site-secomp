from sqlalchemy import db.Column, Integer, String, Boolean, DateTime
from app import db


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(Integer, primary_key=True)
    participantes_associados = db.relationship('participante', backref='usuario', lazy=True)
    email = db.Column(String(64), unique=True, nullable=False)
    senha = db.Column(String(256), nullable=False)
    ultimo_login = db.Column(DateTime, nullable=False)
    data_cadastro = db.Column(DateTime, nullable=False)
    permissao = db.Column(Integer, nullable=False)
    primeiro_nome = db.Column(String(64), nullable=False)
    ult_nome = db.Column(String(64), nullable=False)
    curso = db.Column(String(64), nullable=False)
    cidade = db.Column(String(64), nullable=False)
    instituicao = db.Column(String(64), nullable=False)
    token_email = db.Column(String(90), nullable=False)
    data_nasc = db.Column(DateTime, nullable=False)
    autenticado = db.Column(Boolean, default=False)
    email_verificado = db.Column(Boolean, default=False)

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
    id = db.Column(Integer, db.ForeignKey('usuario.id'), primary_key=True)
    edicao = db.Column(Integer, nullable=False)
    pacote = db.Column(Boolean, nullable=False)
    pagamento = db.Column(Boolean, nullable=False)
    camiseta = db.Column(String(3))
    data_inscricao = db.Column(DateTime, nullable=False)
    credenciado = db.Column(Boolean, nullable=False)


class Ministrante(db.Model):
    __tablename__ = 'ministrante'
    id = db.Column(Integer, db.ForeignKey('ministrante.id'), primary_key=True)
    pagar_gastos = db.Column(Boolean, nullable=False)
    data_chegada_sanca = db.Column(Date, nullable=False)
    data_saida_sanca = db.Column(Date, nullable=False)
    precisa_acomodacao = db.Column(Boolean, nullable=False)
    observacoes = db.Column(String(512))
    nome = db.Column(String(64), nullable=False)
    email = db.Column(String(64), nullable=False)
    tel = db.Column(String(64), nullable=False)
    profissao = db.Column(String(64), nullable=False)
    empresa_univ = db.Column(String(64), nullable=False)
    biografia = db.Column(String(1024), nullable=False)
    foto = db.Column(String(128), nullable=False)
    tamanho_cam = db.Column(String(8), nullable=False)
    facebook = db.Column(String(64))
    twitter = db.Column(String(64))
    linkedin = db.Column(String(64))
    github = db.Column(String(64))


class Atividade(db.Model):
    __tablename__ = 'atividade'
    id = db.Column(Integer, primary_key=True)
    vagas_totais = db.Column(Integer, nullable=False)
    vagas_disponiveis = db.Column(Integer, nullable=False)
    pre_requisitos = db.Column(String(512), nullable=False)
    pre_requisitos_recomendados = db.Column(String(512), nullable=False)
    ativo = db.Column(Boolean, nullable=False)
    tipo = db.Column(Integer, nullable=False)
    data_hora = db.Column(DateTime, nullable=False)
    local = db.Column(String(64), nullable=False)
    titulo = db.Column(String(64), nullable=False)
    descricao = db.Column(String(1024), nullable=False)
    recursos_necessarios = db.Column(String(512), nullable=False)
    observacoes = db.Column(String(512), nullable=False)
    ministrante = db.relationship('ministrante', backref='ministrante', lazy=True)
    inscritos = db.relationship('participante', secondary=relacao_atividade_participante, lazy=True,
        backref=db.backref('atividade', lazy='subquery'))


relacao_atividade_participante = db.Table('relacao_atividade_participante',
                                       db.Column('id_atividade', Integer, db.ForeignKey('atividade.id'), primary_key=True),
                                       db.Column('id_participante', Integer, db.ForeignKey('participante.id'), primary_key=True))

#if __name__ == "__main__":
#    db.create_all()

