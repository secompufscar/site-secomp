import requests

from app.models.models import *
from app.controllers.constants import EDICAO_ATUAL

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

def get_score_evento(edicao):
    return 10000


def get_participantes():
    try:
        query = db.session.query(Participante)
        participantes = []
        for p in query:
            info = (p.id, p.usuario.primeiro_nome + " " + p.usuario.sobrenome + " <" + p.usuario.email + ">")
            participantes.append(info)
        return participantes
    except Exception as e:
        print(e)
        return None

def get_participantes_da_atividade_json(id):
    return 1



def get_atividades():
    try:
        query = db.session.query(Atividade).all()
        ativ = []
        for a in query:
            info = (a.id, a.tipo.nome + ' - ' + a.titulo)
            ativ.append(info)
        return ativ
    except Exception as e:
        print(e)
        return None

from datetime import datetime

def get_atividades_api():
    try:
        query = db.session.query(Atividade).filter(Atividade.titulo != None).all()
        ativ = []
        for a in query:
            ministrantes = []
            for m in a.ministrantes:
                ministrantes.append({
                    "id": m.id,
                    "id_usuario": m.id_usuario,
                    "cargo": m.profissao,
                    "instituicao": m.empresa_universidade,
                    "nome": m.usuario.primeiro_nome + " " + m.usuario.sobrenome,
                    "foto": m.foto,
                    "facebook": m.facebook,
                    "twitter": m.twitter,
                    "linkedin": m.linkedin,
                    "github": m.github,
                })
            info = {
                "id": a.id,
                "tipo": a.tipo.nome,
                "titulo": a.titulo,
                "local": a.local,
                "inicio": datetime.timestamp(a.data_hora_inicio),
                "fim": datetime.timestamp(a.data_hora_fim),
                "descricao": a.descricao,
                "ministrantes": ministrantes
            }
            ativ.append(info)
        return ativ
    except Exception as e:
        print(e)
        return None

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
    db.session.add(objeto)
    db.session.commit()
    return objeto


def verifica_outro_escolhido(campo, objeto):
    opcao_digitada = dict(campo.choices).get(campo.data)
    if opcao_digitada == 'Outro' or opcao_digitada == 'Outra':
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
        'palestra' : palestra,
        'mesa_redonda': mesa_redonda,
        'palestra_empresarial': palestra_empresarial,
        'feira_projetos': feira_projetos,
        'roda_conversa': roda_conversa,
        'workshop': workshop
    }
    return tipo_atividade

def kit_pago(participante):
    pagamento = db.session.query(Pagamento).filter_by(efetuado=True, participante=participante, descricao='Kit').first()
    return pagamento is not None

def get_preco_kit():
    return db.session.query(Evento).filter_by(edicao=EDICAO_ATUAL).first().preco_kit

def get_info_usuarios_envio_comprovante():
     pagamentos = db.session.query(Pagamento).join(Participante)\
     .filter(Participante.id_evento == get_id_evento_atual(), Pagamento.comprovante_enviado == True,
             Pagamento.metodo_pagamento == 'Comprovante', Pagamento.descricao == 'Kit', Pagamento.cancelado == False).all()
     return pagamentos

def esta_preenchido(data):
    if data == None:
        return False
    if data == '':
        return False
    if data == []:
        return False
    return True

def get_permissao_comprovante(participante, arquivo):
     pagamentos = db.session.query(Pagamento).filter(Pagamento.participante == participante, Pagamento.metodo_pagamento == 'Comprovante').all()
     for pagamento in pagamentos:
         if pagamento.arquivo_comprovante == arquivo:
             return True
     return False

def diretorio_publico(diretorio):
    return diretorio == "fotos_ministrantes" or diretorio == "logo_patrocinadores"

def get_nome_restricao(id_restricao):
    if id_restricao == 1:
        return "Nenhuma"
    elif id_restricao == 2:
        return "Vegetariano"
    elif id_restricao == 3:
        return "Vegano"
    elif id_restricao == 4:
        return "Diabético"
    else:
        return "";

def possui_permissao(usuario):
    permissoes = usuario.getPermissoes()
    if "ALTERAR_CAMISETAS" in permissoes or "CADASTRAR_PATROCINADOR" in permissoes or "VENDA_PRESENCIAL" in permissoes \
        or "SORTEAR" in permissoes or "SORTEAR" in permissoes or "GERAR_LISTAS" in permissoes \
        or "ENVIAR_EMAIL" in permissoes or "CONTEUDO" in permissoes or "GERENCIAR_COMPROVANTES" in permissoes:
        return True
    else:
        return False

def cadastro_wifi_visitante(data):
    username = current_app.config['SAGUI_USER']
    password = current_app.config['SAGUI_PASS']

    inicio_validade = '2019-09-09T00:00:00.000Z'
    fim_validade = '2019-09-13T23:59:59.999Z'
    justificativa = 'SECOMP'

    try:
        r = requests.post('https://sistemas.ufscar.br/sagui-api/api/login', json={'username': username, 'password': password})
        login_data = r.json()

        assert 'ROLE_VISITANTE_CADASTRAR_VISITANTE' in login_data['roles'], 'Usuário não tem as permissões necessárias!'

        headers = {'Authorization': f"{login_data['token_type']} {login_data['access_token']}"}
        r = requests.post('https://sistemas.ufscar.br/sagui-api/visitante', json=data, headers=headers)
        cadastro = r.json()

        id_visitante = cadastro['id']
        r = requests.post('https://sistemas.ufscar.br/sagui-api/visitante/%d/autorizar' % id_visitante,
                          json={'visitante': id_visitante,
                                'inicioValidade': inicio_validade,
                                'fimValidade': fim_validade,
                                'justificativa': justificativa},
                          headers=headers)
        autorizacao = r.json()

        requests.post('https://sistemas.ufscar.br/sagui-api/api/logout', headers=headers)
        return True
    except Exception as e:
        print(e)
        return False

def get_ranking_pontuacao():
    participantes = db.session.query(Participante).filter_by(id_evento=get_id_evento_atual()).order_by(Participante.pontuacao.desc()).limit(10).all()
    return participantes
