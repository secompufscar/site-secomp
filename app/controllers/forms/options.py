from app.models.models import *

opcoes_restricao = [
    (1, "Nenhum"),
    (2, "Vegetariano"),
    (3, "Vegano")
]

opcoes_transporte_ida_volta = [
    (1, 'Carro próprio (combustível + pedágios, calculados pelo Jurídico Financeiro)'),
    (2, 'Passagem de Ônibus (compra a ser realizada pelo Jurídico Financeiro)'),
    (3, 'Carro alugado (apenas o valor do aluguel do carro)')
]

opcoes_transporte_sanca = [
    (1, 'Carro próprio (combustível calculado pelo JF)'),
    (2, 'Uber/99 (valor gasto na viagem “local de partida → UFSCar”)'),
    (3, 'Membro da SECOMP UFSCar encarrega-se de buscar o convidado')
]

opcoes_como_conheceu = [
        (0, "Pelo Departamento de Computação da UFSCar"),
        (1, "Através de amigos"),
        (2, "Pela nossa página do facebook"),
        (3, "Por cartazes espalhados em São Carlos"),
        (4, "Outro")
]

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


def get_opcoes_cotas_patrocinadores():
    try:
        cotas_data = db.session.query(CotaPatrocinio).filter_by().order_by(
            CotaPatrocinio.nome).all()
        cotas = []

        for cota in cotas_data:
            info_cota = (cota.id, cota.nome)
            cotas.append(info_cota)

        return cotas
    except Exception as e:
        return None


def get_opcoes_area_atividade():
    try:
        areas_data = db.session.query(AreaAtividade).all()
        areas = []
        for area in areas_data:
            info_area = (area.id, area.nome)
            areas.append(info_area)
        return areas
    except Exception as e:
        return None

# Opções de complemento do envio customizado de emails
def get_opcoes_ecustom_complemento():
    return [(0, 'Mesmo arquivo para todos'), (1, 'Nome do usuário, CamelCase'), (2, 'ID do usuário')]

# Opções de extensão do envio customizado de emails
def get_opcoes_ecustom_extensao():
    return [(0, 'Sem extensão'), (1, '.pdf')]

def get_opcoes_ecustom_atividade():
    # Cria uma lista de atividades para ser usado na página
    query = db.session.query(Atividade)

    atividades = [(a.id, a.titulo) for a in query]
    atividades.append((-1, 'Todas'))

    return atividades

def get_opcoes_tipo_atividade():
    try:
        tipos = db.session.query(TipoAtividade).all()
        tipos_atividade = []
        for tipo in tipos:
            info_tipo = (tipo.id, tipo.nome)
            tipos_atividade.append(info_tipo)
        return tipos_atividade
    except Exception as e:
        return None

def get_opcoes_transporte_ida_volta():
    return [(0, 'Selecione uma opção'),
            (1, 'Carro próprio (combustível + pedágios, calculados pelo Jurídico Financeiro)'),
            (2, 'Passagem de Ônibus (compra a ser realizada pelo Jurídico Financeiro)'),
            (3, 'Carro alugado (apenas o valor do aluguel do carro)')]

def get_opcoes_transporte_sanca():
    return [(0, 'Selecione uma opção'),
            (1, 'Carro próprio (combustível calculado pelo JF)'),
            (2, 'Uber/99 (valor gasto na viagem “local de partida → UFSCar”)'),
            (3, 'Membro da SECOMP UFSCar encarrega-se de buscar o convidado')]

