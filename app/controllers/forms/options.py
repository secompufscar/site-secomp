from app.models.models import *
from app.controllers.functions.helpers import *

opcoes_restricao = [
    (1, "Nenhuma"),
    (2, "Vegetariano"),
    (3, "Vegano"),
    (4, "Diabético")
]

opcoes_falha = [
    (0, "Injeção"),
    (1, "Quebra de Autenticação"),
    (2, "Exposição de Dados Sensíveis"),
    (3, "Quebra de Controle de Acesso"),
    (4, "Configurações de Segurança Incorretas"),
    (5, "Cross-Site Scripting (XSS)"),
    (6, "Desserialização Insegura"),
    (7, "Utilização de Componentes Vulneráveis"),
    (8, "Outros")
]

opcoes_como_conheceu = [
    (0, "Pelo Departamento de Computação da UFSCar"),
    (1, "Através de amigos"),
    (2, "Pela nossa página do facebook"),
    (3, "Por cartazes espalhados em São Carlos"),
    (4, "Outro")
]


opcoes_transporte_ida_volta = [
    (0, 'Selecione uma opção'),
    (1, 'Carro próprio (combustível + pedágios, calculados pelo Jurídico Financeiro)'),
    (2, 'Passagem de Ônibus (compra a ser realizada pelo Jurídico Financeiro)'),
    (3, 'Carro alugado (apenas o valor do aluguel do carro)')
]


opcoes_transporte_sanca = [
    (0, 'Selecione uma opção'),
    (1, 'Carro próprio (combustível calculado pelo JF)'),
    (2, 'Uber/99 (valor gasto na viagem “local de partida → UFSCar”)'),
    (3, 'Membro da SECOMP UFSCar encarrega-se de buscar o convidado')
]


opcoes_avaliacao = [
    (1, 'Péssimo'),
    (2, 'Ruim'),
    (3, 'Regular'),
    (4, 'Bom'),
    (5, 'Ótimo')
]


def get_opcoes_cidades():
    try:
        cidades = db.session.query(Cidade).order_by("nome").all()
        info_cidades = []
        objeto_outro = False
        for cidade in cidades:
            if cidade.nome != 'Outra':
                info = (cidade.id, cidade.nome)
                info_cidades.append(info)
            else:
                objeto_outro = True
        if objeto_outro is False:
            info_cidades.append((0, "Outra"))
        return info_cidades
    except Exception as e:
        print(e)
        return None


def get_opcoes_instituicoes():
    try:
        instituicoes = db.session.query(Instituicao).order_by("nome").all()
        info_instituicoes = []
        objeto_outro = False
        for instituicao in instituicoes:
            if instituicao.nome != 'Outra':
                info = (instituicao.id, instituicao.nome)
                info_instituicoes.append(info)
            else:
                objeto_outro = True
        if objeto_outro is False:
            info_instituicoes.append((0, "Outra"))
        return info_instituicoes
    except Exception as e:
        print(e)
        return None


def get_opcoes_cursos():
    try:
        cursos = db.session.query(Curso).order_by("nome").all()
        info_cursos = []
        objeto_outro = False
        for curso in cursos:
            if curso.nome != 'Outro':
                info = (curso.id, curso.nome)
                info_cursos.append(info)
            else:
                objeto_outro = True
        if objeto_outro is False:
            info_cursos.append((0, "Outro"))
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
    atividades = None
    try:
        query = db.session.query(Atividade)

        atividades = [(a.id, a.titulo) for a in query]
        atividades.append((-1, 'Todas'))
    except:
        pass
    return atividades

def get_opcoes_tipo_atividade():
    try:
        tipos = db.session.query(TipoAtividade).order_by("nome").all()
        tipos_atividade = []
        for tipo in tipos:
            info_tipo = (tipo.id, tipo.nome)
            tipos_atividade.append(info_tipo)
        return tipos_atividade
    except Exception as e:
        return None

def get_usuarios_inscricao_pendente():
    try:
        usuarios = db.session.query(Usuario).all()
        usuarios_inscricao_pendente = []
        for usuario in usuarios:
            participante = db.session.query(Participante).filter(Participante.usuario == usuario, Participante.id_evento == get_id_evento_atual()).first()
            if participante is None and "MINISTRANTE" not in usuario.getPermissoes() and usuario.primeiro_nome is not None and usuario.sobrenome is not None:
                usuarios_inscricao_pendente.append((usuario.id, str(usuario.primeiro_nome) + ' ' + str(usuario.sobrenome) + ' <' + str(usuario.email) + '>'))
        return usuarios_inscricao_pendente
    except Exception as e:
        return None


