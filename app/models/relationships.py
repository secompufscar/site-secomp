relacao_atividade_participante = db.Table('relacao_atividade_participante',
                                       Column('id', Integer, primary_key=True),
                                       Column('id_atividade', Integer, db.ForeignKey('atividade.id')),
                                       Column('id_participante', Integer, db.ForeignKey('participante.id'))

relacao_atividade_ministrante = db.Table('relacao_atividade_ministrante',
                                       Column('id', Integer, primary_key=True),
                                       Column('id_atividade', Integer, db.ForeignKey('atividade.id')),
                                       Column('id_ministrante', Integer, db.ForeignKey('ministrante.id')))