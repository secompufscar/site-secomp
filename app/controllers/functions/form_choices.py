import datetime

from app.models.models import *
from app.controllers.constants import *

def get_opcoes_cidades():
    try:
        cidades = db.session.query(Cidade).filter_by().all()
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
        instituicoes = db.session.query(Instituicao).filter_by().all()
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
        cursos = db.session.query(Curso).filter_by().all()
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
        camisetas = db.session.query(Camiseta).filter_by().order_by(
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
