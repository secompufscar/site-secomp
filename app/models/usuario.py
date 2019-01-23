from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app import db


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    participantes_associados = db.relationship('Participante', backref='usuario', lazy=True)
    email = Column(String(45), unique=True, nullable=False)
    senha = Column(String(256), nullable=False)
    ultimo_login = Column(String(45), nullable=False)
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

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.autenticado

    def is_anonymous(self):
        return False
