from app.models.models import *

from os import path
from app.controllers.constants import EDICAO_ATUAL


def get_score_evento(edicao):
    return 10000


def get_usuarios_query():
    '''
    Retorna o objeto da query de usuários para ser usado em outra função
    '''
    try:
        query = db.session.query(Usuario)
        return query
    except Exception as e:
        print(e)
        return None


def get_participantes():
    try:
        query = db.session.query(Participante)
        participantes = []
        for p in query:
            info = (p.id, p.usuario.primeiro_nome + " " + p.usuario.sobrenome)
            participantes.append(info)
        return participantes
    except Exception as e:
        print(e)
        return None


def get_atividades():
    try:
        query = db.session.query(Atividade)
        ativ = []
        for a in query:
            info = (a.id, a.tipo + ' - ' + a.titulo)
            ativ.append(info)
        return ativ
    except Exception as e:
        print(e)
        return None


def get_participantes_da_atividade_json(id=0):
    '''
    Retorna uma lista de dicionários de usuários para ser usado na página de email cusmotizado
    '''
    query = None

    if (id == -1):
        query = db.session.query(Atividade)
    else:
        query = db.session.query(Atividade).filter_by(id=id)

    query = query.first()
    ativParticipantes = query.participantes

    participantes = [{'id': p.usuario.id, 'nome': f'{p.usuario.primeiro_nome} {p.usuario.sobrenome}', 'email': p.usuario.email} for p in ativParticipantes]

    return participantes



def get_participantes_sem_kit():
    try:
        query = db.session.query(Participante).filter_by(pacote=0)
        participantes = []
        for p in query:
            info = (p.id, p.usuario.primeiro_nome + " " + p.usuario.sobrenome)
            participantes.append(info)
        return participantes
    except Exception as e:
        print(e)
        return None


def cadastra_objeto_generico(objeto):
    try:
        db.session.add(objeto)
        db.session.flush()
        db.session.commit()
        return objeto

    except Exception as e:
        print(e)
        return None


def verifica_outro_escolhido(campo, objeto):
    if campo.data == 0:
        return cadastra_objeto_generico(objeto).id
    else:
        return campo.data


def get_path_anexo(anexoBase, anexoPasta, complemento, usuario, extencao):
    '''
    Retorna uma lista dos arquivos que serão anexados.
    '''

    # Tipo de modificação aplicada nos nomes dos anexos, novas motificações poder ser adicionadas aqui
    if complemento == 0: # Mesmo arquivo para todos
        return path.join(anexoPasta, (anexoBase + extencao))
    elif complemento == 1: # Nome CamelCase
        return path.join(anexoPasta, (anexoBase + usuario.primeiro_nome + usuario.sobrenome.replace(" ", "") + extencao))
    elif complemento == 2: # ID
        return path.join(anexoPasta, (anexoBase + usuario.id + extencao))
    else:
        return None

def valida_url_codigo(usuario, codigo):
    atividade = db.session.query(Atividade).filter_by(url_codigo=codigo).first()
    ministrante = db.session.query(Ministrante).filter_by(usuario=usuario).first()
    emails = []
    if atividade is None:
        return False, None, None
    for m in atividade.ministrantes:
        emails.append(m.usuario.email)
    if(usuario is None):
        if (atividade is not None):
            return True, atividade, emails
    else:
        if(ministrante is not None):
            if(atividade is not None and ministrante.usuario.email in emails):
                return True, atividade, emails
        else:
            if(atividade is not None and "CONTEUDO" in usuario.getPermissoes()):
                return True, atividade, emails
    return False, atividade, emails


def get_id_evento_atual():
    evento = db.session.query(Evento).filter_by(edicao=EDICAO_ATUAL).first()
    return evento.id

def confirmacao_atividade_ministrante(usuario):
    atividade = None
    if usuario.ministrante is not None:
        r = db.session.query(RelacaoAtividadeMinistrante).filter(RelacaoAtividadeMinistrante.id_ministrante == usuario.ministrante.id,
                                                                                                RelacaoAtividadeMinistrante.confirmado == None).all()
        for relacao in r:
            a = db.session.query(Atividade).get(relacao.id_atividade)
            if a is not None:
                atividade = a

    if atividade is not None:
        if atividade.tipo.nome == "Palestra":
            view = 'cadastro_palestra'
        elif atividade.tipo.nome == "Palestra Empresarial":
            view = 'cadastro_palestra_empresarial'
        elif atividade.tipo.nome == "Minicurso":
            view = 'cadastro_minicurso'
        elif atividade.tipo.nome == "Mesa Redonda":
            view = 'cadastro_mesa_redonda'
        elif atividade.tipo.nome == "Feira de Projetos":
            view = 'cadastro_feira_projetos'
        elif atividade.tipo.nome == "Roda de Conversa":
            view = 'cadastro_feira_projetos'
        elif atividade.tipo.nome == "Workshop":
            view = 'cadastro_workshop'
        return False, atividade, view
    else:
        return True, None, None

def get_tipos_atividade():
    minicurso = db.session.query(TipoAtividade).filter_by(nome='Minicurso').first()
    palestra = db.session.query(TipoAtividade).filter_by(nome='Palestra').first()
    mesa_redonda = db.session.query(TipoAtividade).filter_by(nome='Mesa Redonda').first()
    palestra_empresarial = db.session.query(TipoAtividade).filter_by(nome='Palestra Empresarial').first()
    feira_projetos = db.session.query(TipoAtividade).filter_by(nome='Feira de Projetos').first()
    workshop = db.session.query(TipoAtividade).filter_by(nome='Workshop').first()
    roda_conversa = db.session.query(TipoAtividade).filter_by(nome='Roda de Conversa').first()

    tipo_atividade = {
        'minicurso': minicurso,
        'palestra': palestra,
        'mesa_redonda': mesa_redonda,
        'palestra_empresarial': palestra_empresarial,
        'feira_projetos': feira_projetos,
        'workshop': workshop,
        'roda_conversa': roda_conversa
    }
    return tipo_atividade

def kit_pago(participante):
    pagamento = db.session.query(Pagamento).filter_by(efetuado=True, participante=participante, descricao='Kit').first()
    return pagamento is not None

def get_ranking_pontuacao():
    participantes = db.session.query(Participante).filter_by(id_evento=get_id_evento_atual()).order_by(Participante.pontuacao.desc()).limit(10).all()
    return participantes


def get_equipe():
    todos = db.session.query(MembroDeEquipe, Usuario, Diretoria, Cargo).join(Diretoria).join(Usuario).join(Cargo)

    coordenacao_geral = todos.filter(Diretoria.nome == 'Coordenação Geral').all()

    ti = todos.filter(Diretoria.nome == 'Tecnologia da Informação').all()
    dm = todos.filter(Diretoria.nome == 'Design & Marketing').all()
    conteudo = todos.filter(Diretoria.nome == 'Conteúdo').all()
    jf = todos.filter(Diretoria.nome == 'Jurídico-Financeiro').all()
    patrocinio = todos.filter(Diretoria.nome == 'Patrocínio').all()
    socio = todos.filter(Diretoria.nome == 'Sóciocultural').all()

    data = [('Coordenação Geral', coordenacao_geral),
            ('Tecnologia da Informação', ti),
            ('Design & Marketing', dm),
            ('Conteúdo', conteudo),
            ('Jurídico-Financeiro', jf),
            ('Patrocínio', patrocinio),
            ('Sociocultural', socio)]

    return data