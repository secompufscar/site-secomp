from app.models.models import *


def populate():
    valores = {
        'cursos': ['Ciência da Computação', 'Engenharia da Computação'],
        'instituicoes': ['UFSCar', 'USP', 'UNESP', 'Unicamp'],
        'cidades': ['São Carlos', 'São Paulo', 'Campinas', 'Rio Claro'],
        'diretorias': ['Coordenação Geral', 'TI', 'Design & Marketing', 'Conteúdo',
                        'Jurídico-Financeira', 'Sociocultural'],
        'cargos': ['Membro', 'Diretora', 'Diretor', 'Voluntária', 'Voluntário'],
        'cotas': ['Diamante', 'Ouro', 'Prata', 'Apoio'],
        'permissoes': ['ADMIN', 'SORTEAR', 'GERAR_LISTAS', 'VENDA_PRESENCIAL',
                       'GERAR_CRACHAS', 'ALTERAR_CAMISETAS', 'NOTIFICACOES_APP',
                       'GERENCIAR_COMPROVANTES', 'MINISTRANTE', 'CONTEUDO',
                        'PATROCINIO'],
        'camisetas': ['P Feminino', 'M Feminino', 'G Feminino', 'GG Feminino',
                      'P Masculino', 'M Masculino', 'G Masculino', 'GG Masculino']
    }

    print('# Adicionando evento...')
    db.session.add(Evento(id=1, edicao=10, ano=2019,
                          data_hora_inicio='2019-09-09 08:30:00',
                          data_hora_fim='2019-09-13 18:30:00',
                          inicio_inscricoes_evento='2019-02-10 12:00:00',
                          fim_inscricoes_evento='2019-08-10 23:59:00'),
                          abertura_minicursos_1_etapa='2019-08-10 23:59:00',
                          fechamento_minicursos_1_etapa='2019-08-10 23:59:00',
                          abertura_minicursos_2_etapa='2019-08-10 23:59:00',
                          fechamento_minicursos_2_etapa='2019-08-10 23:59:00',
                          preco_kit=40.00)

    id = 1
    for curso in valores['cursos']:
        print(f'# Adicionando cursos [{id}/{len(valores["cursos"])}]')
        db.session.add(Curso(id=id, nome=curso))
        id += 1

    id = 1
    for instituicao in valores['instituicoes']:
        print(f'# Adicionando instituições [{id}/{len(valores["instituicoes"])}]')
        db.session.add(Instituicao(id=id, nome=instituicao))
        id += 1

    id = 1
    for cidade in valores['cidades']:
        print(f'# Adicionando cidades [{id}/{len(valores["cidades"])}]')
        db.session.add(Cidade(id=id, nome=cidade))
        id += 1

    id = 1
    for diretoria in valores['diretorias']:
        print(f'# Adicionando diretorias [{id}/{len(valores["diretorias"])}]')
        db.session.add(Diretoria(id=id, nome=diretoria, ordem=id))
        id += 1

    id = 1
    for cargo in valores['cargos']:
        print(f'# Adicionando cargos [{id}/{len(valores["cargos"])}]')
        db.session.add(Cargo(id=id, nome=cargo))
        id += 1

    id = 1
    for cota in valores['cotas']:
        print(f'# Adicionando cotas [{id}/{len(valores["cotas"])}]')
        db.session.add(CotaPatrocinio(id=id, nome=cota))
        id += 1

    id = 1
    for permissao in valores['permissoes']:
        print(f'# Adicionando permissões [{id}/{len(valores["permissoes"])}]')
        db.session.add(Permissao(id=id, nome=permissao))
        id += 1

    id = 1
    for camiseta in valores['camisetas']:
        print(f'# Adicionando camisetas [{id}/{len(valores["camisetas"])}]')
        db.session.add(Camiseta(id=id, id_evento=1, ordem_site=id,
                                tamanho=camiseta, quantidade=100, quantidade_restante=100))
        id += 1

    db.session.commit()
