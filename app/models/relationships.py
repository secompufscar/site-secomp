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
