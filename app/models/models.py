from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from dotenv import load_dotenv
import os

load_dotenv()
SENHA = os.getenv("SENHA")
IP_DB = os.getenv("IP_DB")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:%s@%s/db' % (SENHA, IP_DB)
db = SQLAlchemy(app)

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

class Participante(db.Model):
    __tablename__ = 'participante'
    id = Column(Integer, db.ForeignKey('usuario.id'), primary_key=True)
    edicao = Column(Integer, nullable=False)
    pacote = Column(Boolean, nullable=False)
    pagamento = Column(Boolean, nullable=False)
    camiseta = Column(String(3))
    data_inscricao = Column(DateTime, nullable=False)
    credenciado = Column(Boolean, nullable=False)

#if __name__ == "__main__":
#	db.create_all()
