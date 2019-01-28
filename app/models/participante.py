from sqlalchemy import Column, Integer, Boolean, String, DateTime

from app import db


class Participante(db.Model):
    __tablename__ = 'participante'
    id = Column(Integer, db.ForeignKey('usuario.id'), primary_key=True)
    edicao = Column(Integer, nullable=False)
    pacote = Column(Boolean, nullable=False)
    pagamento = Column(Boolean, nullable=False)
    camiseta = Column(String(3))
    data_inscricao = Column(DateTime, nullable=False)
    credenciado = Column(Boolean, nullable=False)
