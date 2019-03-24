import datetime

from app.models.models import *
from app.controllers.constants import *

def get_opcoes_cidades():
    try:
        cidades = db.session.query(Cidade).all()
        info_cidades = []
        for cidade in cidades:
            info = (cidade.id, cidade.nome)
            info_cidades.append(info)
        return info_cidades
    except Exception as e:
        print(e)
        return None


def get_opcoes_instituicoes():
    try:
        instituicoes = db.session.query(Instituicao).all()
        info_instituicoes = []
        for instituicao in instituicoes:
            info = (instituicao.id, instituicao.nome)
            info_instituicoes.append(info)
        return info_instituicoes
    except Exception as e:
        print(e)
        return None


def get_opcoes_cursos():
    try:
        cursos = db.session.query(Curso).all()
        info_cursos = []
        for curso in cursos:
            info = (curso.id, curso.nome)
            info_cursos.append(info)
        return info_cursos
    except Exception as e:
        print(e)
        return None

def get_opcoes_camisetas():
    try:
        camisetas = db.session.query(Camiseta).order_by(
            Camiseta.ordem_site).all()
        info_camisetas = []
        for camiseta in camisetas:
            if camiseta.quantidade_restante > 0:
                info = (camiseta.id, camiseta.tamanho)
                info_camisetas.append(info)

        return info_camisetas
    except Exception as e:
        print(e)
        return None

def get_opcoes_usuarios_permissao():
    try:
        usuarios = db.session.query(Usuario).order_by(
            Usuario.primeiro_nome).all()
        info_usuarios = []
        for usuario in usuarios:
            info = (usuario.id, str(usuario.primeiro_nome + ' ' + usuario.sobrenome + ' [' + usuario.email + ']'))
            info_usuarios.append(info)
        return info_usuarios
    except Exception as e:
        print(e)
        return None

def get_opcoes_permissoes():
    return [(0, "Super Admin"), (1, "JF")]
