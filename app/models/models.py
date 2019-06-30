from time import strftime, time, localtime
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date

db = SQLAlchemy()

relacao_atividade_area = db.Table('relacao_atividade_area',
                                    Column('id', Integer, primary_key=True),
                                    Column('id_atividade', Integer, db.ForeignKey('atividade.id')),
                                    Column('id_area', Integer, db.ForeignKey('area.id')))

relacao_patrocinador_evento = db.Table('relacao_patrocinador_evento',
                                       Column('id', Integer, primary_key=True),
                                       Column('id_patrocinador', Integer, db.ForeignKey('patrocinador.id')),
                                       Column('id_evento', Integer, db.ForeignKey('evento.id')))

relacao_permissao_usuario = db.Table('relacao_permissao_usuario',
                                     Column('id', Integer, primary_key=True),
                                     Column('id_usuario', Integer, db.ForeignKey('usuario.id')),
                                     Column('id_permissao', Integer, db.ForeignKey('permissao.id')))

relacao_atividade_participante = db.Table('relacao_atividade_participante',
                                       Column('id', Integer, primary_key=True),
                                       Column('id_atividade', Integer, db.ForeignKey('atividade.id')),
                                       Column('id_participante', Integer, db.ForeignKey('participante.id')))


relacao_atividade_patrocinador = db.Table('relacao_atividade_patrocinador',
                                       Column('id', Integer, primary_key=True),
                                       Column('id_atividade', Integer, db.ForeignKey('atividade.id')),
                                       Column('id_patrocinador', Integer, db.ForeignKey('patrocinador.id')))


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    email = Column(String(64), unique=True, nullable=False)
    senha = Column(String(256), nullable=True)
    primeiro_nome = Column(String(64), nullable=True)
    sobrenome = Column(String(64), nullable=True)
    id_curso = Column(Integer, db.ForeignKey('curso.id'), nullable=True)
    id_cidade = Column(Integer, db.ForeignKey('cidade.id'), nullable=True)
    id_instituicao = Column(Integer, db.ForeignKey('instituicao.id'), nullable=True)
    token_email = Column(String(90), nullable=True)
    data_nascimento = Column(Date, nullable=True)
    admin = Column(Boolean, default=False)
    autenticado = Column(Boolean, default=False)
    email_verificado = Column(Boolean, default=False)
    ultimo_login = Column(DateTime, default=strftime("%Y-%m-%d %H:%M:%S", localtime(time())))
    data_cadastro = Column(DateTime, default=strftime("%Y-%m-%d %H:%M:%S", localtime(time())))
    participantes_associados = db.relationship('Participante', back_populates='usuario', lazy=True)
    salt = Column(String(30), nullable=True)
    token_alteracao_senha = Column(String(90), nullable=True)
    salt_alteracao_senha = Column(String(30), nullable=True)
    permissoes_usuario = db.relationship('Permissao', secondary=relacao_permissao_usuario, lazy=True,
                                         back_populates='usuarios')
    membros_de_equipe = db.relationship('MembroDeEquipe', backref='usuario', lazy=True)
    ministrante = db.relationship('Ministrante', back_populates='usuario', lazy=True)

    @classmethod
    def is_active(cls):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.autenticado

    @classmethod
    def is_anonymous(cls):
        return False

    def is_admin(self):
        return self.admin

    def getPermissoes(self):
        permissoes = []
        for permissao in self.permissoes_usuario:
            permissoes.append(permissao.nome)
        return permissoes

    def __repr__(self):
        return self.primeiro_nome + " " + self.sobrenome + " <" + self.email + ">"


class Participante(db.Model):
    __tablename__ = 'participante'
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, db.ForeignKey('usuario.id'), primary_key=False)
    id_evento = Column(Integer, db.ForeignKey('evento.id'), nullable=False)
    pacote = Column(Boolean, nullable=False)
    pagamento = Column(Boolean, nullable=False)
    id_camiseta = Column(Integer, db.ForeignKey('camiseta.id'), primary_key=False)
    data_inscricao = Column(DateTime, default=strftime("%Y-%m-%d %H:%M:%S", localtime(time())))
    credenciado = Column(Boolean, nullable=False)
    opcao_coffee = Column(Integer, nullable=False)
    usuario = db.relationship('Usuario', back_populates='participantes_associados', lazy=True)
    presencas = db.relationship('Presenca', backref='participante')
    atividades = db.relationship('Atividade', secondary=relacao_atividade_participante, lazy=True,
                                 back_populates='participantes')

    def __repr__(self):
        return self.usuario.primeiro_nome + " " + self.usuario.sobrenome + " <" + self.usuario.email + ">"


class Ministrante(db.Model):
    __tablename__ = 'ministrante'
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, db.ForeignKey('usuario.id'), primary_key=False)
    telefone = Column(String(15), nullable=True)
    profissao = Column(String(64), nullable=True)
    empresa_universidade = Column(String(64))
    biografia = Column(String(1500), nullable=True)
    foto = Column(String(128))
    tamanho_camiseta = Column(Integer)
    facebook = Column(String(64))
    twitter = Column(String(64))
    linkedin = Column(String(64))
    github = Column(String(64))
    dados_hospedagem_transporte = db.relationship('DadosHospedagemTransporte', back_populates='ministrante', lazy=True)
    atividades = db.relationship('Atividade', secondary='relacao_atividade_ministrante', lazy=True,
                                back_populates='ministrantes')
    usuario = db.relationship('Usuario', back_populates='ministrante', lazy=True)

    def __repr__(self):
        return self.usuario.primeiro_nome + " " + self.usuario.sobrenome + " <" + self.usuario.email + ">"

class DadosHospedagemTransporte(db.Model):
    __tablename__ = 'dados_hospedagem_transporte'
    id = Column(Integer, primary_key=True)
    id_ministrante = Column(Integer, db.ForeignKey('ministrante.id'))
    id_evento = Column(Integer, db.ForeignKey('evento.id'))
    cidade_origem = Column(String(64), nullable=False)
    data_chegada_origem = Column(Date, nullable=False)
    data_chegada_partida = Column(Date, nullable=False)
    transporte_ida_volta = Column(Boolean, nullable=False)
    opcoes_transporte_ida_volta = Column(Integer)
    transporte_sanca = Column(Boolean, nullable=False)
    opcoes_transporte_sanca = Column(Integer)
    hospedagem = Column(Boolean, nullable=False)
    necessidades_hospedagem = Column(String(256))
    observacoes = Column(String(256))
    ministrante = db.relationship('Ministrante', back_populates='dados_hospedagem_transporte', lazy=True)


class AreaAtividade(db.Model):
    __tablename__ = 'area'
    id = Column(Integer, primary_key=True)
    nome = Column(String(48), nullable=False)
    atividades = db.relationship('Atividade', secondary=relacao_atividade_area, lazy=True,
                                    back_populates='areas')
    def __repr__(self):
        return self.nome + ' <' + str(self.id) + '>'

class TipoAtividade(db.Model):
    __tablename__ = 'tipo_atividade'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    def __repr__(self):
        return self.nome + ' <' + str(self.id) + '>'

class Atividade(db.Model):
    __tablename__ = 'atividade'
    id = Column(Integer, primary_key=True)
    id_evento = Column(Integer, db.ForeignKey('evento.id'))
    id_tipo = Column(Integer, db.ForeignKey('tipo_atividade.id'))
    vagas_totais = Column(Integer, nullable=True)
    vagas_disponiveis = Column(Integer, nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)
    data_hora = Column(DateTime, nullable=True)
    local = Column(String(64), nullable=True)
    titulo = Column(String(64), nullable=True)
    descricao = Column(String(1024), nullable=True)
    observacoes = Column(String(512))
    tipo = db.relationship('TipoAtividade', backref='atividades', lazy=True, uselist=False)
    url_codigo = Column(String(255))
    atividade_cadastrada = Column(Boolean, default=False)

    info_minicurso = db.relationship('InfoMinicurso', backref='atividade', lazy=True)
    info_palestra = db.relationship('InfoPalestra', backref='atividade', lazy=True)
    info_feira_de_projetos = db.relationship('InfoFeiraDeProjetos', backref='atividade', lazy=True)

    patrocinadores = db.relationship('Patrocinador', secondary=relacao_atividade_patrocinador, lazy=True,
                            back_populates='atividades')

    areas = db.relationship('AreaAtividade', secondary=relacao_atividade_area, lazy=True,
                            back_populates='atividades')
    ministrantes = db.relationship('Ministrante', secondary='relacao_atividade_ministrante', lazy=True,
                                   back_populates='atividades')
    participantes = db.relationship('Participante', secondary=relacao_atividade_participante, lazy=True,
                                    back_populates='atividades')
    presencas = db.relationship('Presenca', backref='atividade')


    def __repr__(self):
        if self.titulo != None:
            return self.titulo
        else:
            return 'Atividade <' + str(self.id) + '>'

class InfoMinicurso(db.Model):
    __tablename__ = 'info_minicurso'
    id = Column(Integer, primary_key=True)
    id_atividade = Column(Integer, db.ForeignKey('atividade.id'))
    pre_requisitos = Column(String(128))
    planejamento = Column(String(128))
    apresentacao_extra = Column(String(128))
    material = Column(String(128))
    requisitos_ide = Column(String(1024))
    requisitos_bibliotecas_pacotes = Column(String(1024))
    requisitos_dependencias = Column(String(1024))
    requisitos_sistema = Column(String(1024))
    requisitos_observacoes = Column(String(1024))
    requisitos_github = Column(String(1024))
    requisitos_hardware = Column(String(1024))
    dicas_instalacao = Column(String(1024))


class InfoPalestra(db.Model):
    __tablename__ = 'info_palestra'
    id = Column(Integer, primary_key=True)
    id_atividade = Column(Integer, db.ForeignKey('atividade.id'))
    planejamento = Column(String(128))
    apresentacao_extra = Column(String(128))
    material = Column(String(128))
    requisitos_tecnicos = Column(String(1024))
    perguntas = Column(String(1024))


class InfoFeiraDeProjetos(db.Model):
    __tablename__ = 'info_feira_de_projetos'
    id = Column(Integer, primary_key=True)
    id_atividade = Column(Integer, db.ForeignKey('atividade.id'))
    necessidades = Column(String(1024))
    planejamento = Column(String(1024))


class Evento(db.Model):
    __tablename__ = 'evento'
    id = Column(Integer, primary_key=True)
    edicao = Column(Integer, nullable=False)
    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime, nullable=False)
    inicio_inscricoes_evento = Column(DateTime, nullable=False)
    fim_inscricoes_evento = Column(DateTime, nullable=False)
    ano = Column(Integer, default=datetime.now().year)
    participantes = db.relationship('Participante', backref='evento', lazy=True)
    presencas = db.relationship('Presenca', backref='evento', lazy=True)
    atividades = db.relationship('Atividade', backref='evento', lazy=True)
    membros_equipe = db.relationship('MembroDeEquipe', backref='evento', lazy=True)
    patrocinadores = db.relationship('Patrocinador', secondary=relacao_patrocinador_evento, lazy=True,
                                     back_populates='eventos')
    camisetas = db.relationship('Camiseta', backref='evento', lazy=True)

    def __repr__(self):
        return str(self.edicao) + "ª Edição"


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

    def __repr__(self):
        return self.usuario.primeiro_nome + " " + self.usuario.sobrenome + "<" + self.usuario.email + ">"


class Cargo(db.Model):
    __tablename__ = 'cargo'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    membros = db.relationship('MembroDeEquipe', backref='cargo', lazy=True)

    def __repr__(self):
        return self.nome


class Diretoria(db.Model):
    __tablename__ = 'diretoria'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    ordem = Column(Integer, nullable=False)
    membros = db.relationship('MembroDeEquipe', backref='diretoria', lazy=True)

    def __repr__(self):
        return self.nome


class Patrocinador(db.Model):
    __tablename__ = 'patrocinador'
    id = Column(Integer, primary_key=True)
    nome_empresa = Column(String(100), nullable=False)
    logo = Column(String(100), nullable=False)
    ativo_site = Column(Boolean, nullable=False)
    id_cota = Column(Integer, db.ForeignKey('cota_patrocinio.id'), nullable=False)
    cota = db.relationship('CotaPatrocinio', backref='cota_patrocinio', lazy=True)
    ordem_site = Column(Integer, primary_key=True)
    link_website = Column(String(200), nullable=True)
    ultima_atualizacao_em = Column(DateTime, default=strftime("%Y-%m-%d %H:%M:%S", localtime(time())))
    eventos = db.relationship('Evento', secondary=relacao_patrocinador_evento, lazy=True,
                              back_populates='patrocinadores')
    atividades = db.relationship('Atividade', secondary=relacao_atividade_patrocinador, lazy=True,
                            back_populates='patrocinadores')

    def __repr__(self):
        return self.nome_empresa


class CotaPatrocinio(db.Model):
    __tablename__ = 'cota_patrocinio'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    patrocinadores = db.relationship('Patrocinador', backref='cota_patrocinio', lazy=True)


class Curso(db.Model):
    __tablename__ = 'curso'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    usuarios = db.relationship('Usuario', backref='curso', lazy=True)

    def __repr__(self):
        return self.nome


class Instituicao(db.Model):
    __tablename__ = 'instituicao'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    usuarios = db.relationship('Usuario', backref='instituicao', lazy=True)

    def __repr__(self):
        return self.nome


class Cidade(db.Model):
    __tablename__ = 'cidade'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    usuarios = db.relationship('Usuario', backref='cidade', lazy=True)

    def __repr__(self):
        return self.nome


class Camiseta(db.Model):
    __tablename__ = 'camiseta'
    id = Column(Integer, primary_key=True)
    id_evento = Column(Integer, db.ForeignKey('evento.id'), nullable=False)
    participantes = db.relationship('Participante', backref='camiseta', lazy=True)
    tamanho = Column(String(30), nullable=False)
    quantidade = Column(Integer, nullable=False)
    ordem_site = Column(Integer, nullable=False)
    quantidade_restante = Column(Integer, nullable=False)

    def __repr__(self):
        return self.nome


class Permissao(db.Model):
    __tablename__ = 'permissao'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    usuarios = db.relationship('Usuario', secondary=relacao_permissao_usuario, lazy=True,
                               back_populates='permissoes_usuario')

    def __repr__(self):
        return self.nome

class RelacaoAtividadeMinistrante(db.Model):
    __tablename__ = 'relacao_atividade_ministrante'
    id = Column('id', Integer, primary_key=True)
    id_atividade = Column('id_atividade', Integer, db.ForeignKey('atividade.id'))
    id_ministrante = Column('id_ministrante', Integer, db.ForeignKey('ministrante.id'))
    confirmado = Column('confirmado', Boolean, nullable=True)
    admin_atividade = Column('admin_atividade', Boolean, nullable=True)
