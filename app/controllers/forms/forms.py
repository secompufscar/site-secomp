from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import InputRequired, Email, Length, EqualTo
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, TextAreaField, IntegerField, RadioField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Optional

from app.controllers.forms.options import *
from app.controllers.forms.validators import *
from app.controllers.functions.helpers import get_participantes, get_atividades


class BaseRecaptchaForm(FlaskForm):
    recaptcha = RecaptchaField(validators=[Recaptcha(message="Você deve completar a checagem de validação do recaptcha.")])


class LoginForm(BaseRecaptchaForm):
    email = StringField('Email', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Email(message=ERRO_EMAIL), Length(min=1, max=254)])
    senha = PasswordField('Senha', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=8, max=20, message=ERRO_TAMANHO_SENHA)])


class CadastroForm(BaseRecaptchaForm):
    primeiro_nome = StringField('Primeiro Nome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=30), so_letras()], id="primeiro_nome")
    sobrenome = StringField('Sobrenome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=100), so_letras()], id="sobrenome")
    email = StringField('Email', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Email(message=ERRO_EMAIL), Length(min=1, max=254), email_existe()], id="email")
    senha = PasswordField('Senha', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), EqualTo(
        'confirmacao', message=ERRO_COMPARA_SENHAS), Length(min=8, max=20, message=ERRO_TAMANHO_SENHA)], id="senha")
    confirmacao = PasswordField('Confirmação de Senha', validators=[
                            InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=8, max=20)])
    curso = SelectField('Curso', choices=get_opcoes_cursos(), validators=
    [InputRequired(message=ERRO_INPUT_REQUIRED)],
                        id="curso", coerce=int)
    outro_curso = StringField("Outro curso", id="outro_curso", validators=[erro_curso_existe(), so_letras()])
    instituicao = SelectField('Instituição', choices=get_opcoes_instituicoes(
    ), id="instituicao", default="UFSCar", coerce=int)
    outra_instituicao = StringField("Outra instituição", id="outra_instituicao", validators=[erro_instituicao_existe(), so_letras()])
    cidade = SelectField('Cidade', choices=get_opcoes_cidades(
    ), id="cidade", default="São Carlos", coerce=int)
    outra_cidade = StringField("Outra Cidade", id="outra_cidade", validators=[erro_cidade_existe(), so_letras()])
    data_nasc = DateField("Data de Nascimento",
                          format="%d/%m/%Y", id="data_nasc")
    como_conheceu = SelectField('Como você conheceu a SECOMP?', choices=opcoes_como_conheceu, coerce=int)
    outro_como_conheceu = StringField("Outro", id="outro_como_conheceu", validators=[Length(max=200)])


class EdicaoUsuarioForm(BaseRecaptchaForm):
    primeiro_nome = StringField('Primeiro Nome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=30), so_letras()], id="primeiro_nome")
    sobrenome = StringField('Sobrenome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=100), so_letras()], id="sobrenome")
    curso = SelectField('Curso', choices=get_opcoes_cursos(), validators=[InputRequired(message=ERRO_INPUT_REQUIRED)], id="curso", coerce=int)
    outro_curso = StringField("Outro curso", id="outro_curso", validators=[erro_curso_existe(), so_letras()])
    instituicao = SelectField('Instituição', choices=get_opcoes_instituicoes(
    ), id="instituicao", default="UFSCar", coerce=int)
    outra_instituicao = StringField("Outra instituição", id="outra_instituicao", validators=[erro_instituicao_existe(), so_letras()])
    cidade = SelectField('Cidade', choices=get_opcoes_cidades(
    ), id="cidade", default="São Carlos", coerce=int)
    outra_cidade = StringField("Outra Cidade", id="outra_cidade", validators=[erro_cidade_existe(), so_letras()])
    data_nasc = DateField("Data de Nascimento",
                          format="%d/%m/%Y", id="data_nasc")


class ParticipanteForm(FlaskForm):
    leu_termos = BooleanField('Li e concordo com os termos de uso', validators=[InputRequired(message=ERRO_INPUT_REQUIRED)], id="li_termos")


class ComprarKitForm(BaseRecaptchaForm):
    comprar = RadioField('Deseja comprar o kit da SECOMP UFSCar?', id='comprar', choices=[(1,'Sim'),(2,'Não')], coerce=int, default=2)
    camiseta = SelectField('Camiseta', choices=get_opcoes_camisetas(
    ), id="camiseta", default="P Feminino", coerce=int)
    restricao_coffee = SelectField(
        'Restrição para o Coffee-Break', choices=opcoes_restricao, default="Nenhum", coerce=int, id="restricao_coffee")
    forma_pagamento = RadioField('Forma de pagamento do kit', id='forma_pagamento', choices=[(1,'Transferência bancária'),(2,'PayPal')], coerce=int, default=2)
    uso_cupom_desconto = BooleanField('Deseja utilizar um cupom de desconto?', id='uso_cupom_desconto')
    cupom_desconto = StringField('Cupom de Desconto', id='cupom_desconto', validators=[Length(max=200), RequiredIf(uso_cupom_desconto=True), valida_cupom_desconto()], render_kw={'maxlength': 200})
    comprovante = FileField('Enviar comprovante de pagamento', id="comprovante", validators=[
            ComprovanteRequired(message=ERRO_INPUT_REQUIRED),
            FileAllowed(['png', 'jpg', 'jpeg'], message=ERRO_EXTENSAO_INVALIDA)
        ])


class AlterarSenhaForm(FlaskForm):
    senha_atual = PasswordField('Senha Atual', validators=[Length(min=0, max=20, message=ERRO_TAMANHO_SENHA)])
    nova_senha = PasswordField('Nova Senha', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=8, max=20, message=ERRO_TAMANHO_SENHA), EqualTo('confirmacao', message=ERRO_COMPARA_SENHAS)])
    confirmacao = PasswordField('Confirmação de Senha', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=8, max=20)])


class AlterarSenhaPorEmailForm(BaseRecaptchaForm):
    email = StringField('Email', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Email(message=ERRO_EMAIL), Length(min=1, max=254)])


class ContatoForm(BaseRecaptchaForm):
    nome_completo = StringField('Nome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=30)])
    email = StringField('Email', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=30)])
    mensagem = StringField('Mensagem', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=500)])


class PatrocinadorForm(FlaskForm):
    nome_empresa = StringField('Nome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=100)])
    logo = StringField('Logo', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=100)])
    ativo_site = BooleanField('Ativo', validators=[InputRequired()], id="ativo_site")
    id_cota = SelectField('Cota', choices=get_opcoes_cotas_patrocinadores(),
        id="cota", default="0", coerce=int)
    link_website = StringField('Site', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=200)])


class ComprovanteForm(BaseRecaptchaForm):
    comprovante = FileField('Comprovante de Pagamento', validators=[
            FileRequired(message=ERRO_INPUT_REQUIRED),
            FileAllowed(['png', 'jpg', 'jpeg'], message=ERRO_EXTENSAO_INVALIDA)
        ])


class AlteraCamisetaForm(FlaskForm):
    participante = SelectField("Selecione o usuário", choices=get_participantes(), id="participante", coerce=int)
    camiseta = SelectField("Modelos", choices=get_opcoes_camisetas(), default="P Feminino", id="camiseta", coerce=int)

class PontuacaoNaMaoForm(FlaskForm):
    participante = SelectField("Selecione o usuário", choices=get_participantes(), id="participante", coerce=int)
    pontuacao = IntegerField()

class VendaKitForm(FlaskForm):
    participante = SelectField("Inscrições na SECOMP 2019", choices=get_participantes(), id="participante", coerce=int)
    camiseta = SelectField("Modelos", choices=get_opcoes_camisetas(), default="P Feminino", id="camiseta", coerce=int)
    restricao_coffee = SelectField(
        'Restrição para o Coffee-Break', choices=opcoes_restricao, default="Nenhum", coerce=int, id="restricao_coffee")
    valor = StringField("Valor", validators=[InputRequired()])



class ListasParticipantes(FlaskForm):
    atividades = SelectField("Atividades", choices=get_atividades(), id="atividade", coerce=int)
    tipo = SelectField("Modelos", choices=[(0, 'Inscritos'), (1, 'Presentes')], id="tipo", coerce=int)


class CadastroMinistranteForm(FlaskForm):
    primeiro_nome = StringField('Primeiro Nome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=64), so_letras()], id="primeiro_nome", render_kw={'maxlength': 64})
    sobrenome = StringField('Sobrenome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=64), so_letras()], id="sobrenome", render_kw={'maxlength': 64})
    email = StringField('Email', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Email(message=ERRO_EMAIL), Length(min=1, max=254),
        valida_email_ministrante()], id="email")
    senha = PasswordField('Senha', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), EqualTo(
        'confirmacao', message=ERRO_COMPARA_SENHAS), Length(min=8, max=20, message=ERRO_TAMANHO_SENHA)], id="senha")
    confirmacao = PasswordField('Confirmação de Senha', validators=[
        InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=8, max=20)])
    data_nascimento = DateField("Data de Nascimento",
                          format="%d/%m/%Y", id="data_nascimento")
    telefone = StringField('Telefone', validators=[InputRequired(), Length(min=8, max=14)], id='telefone')
    profissao = StringField('Profissão', validators=[InputRequired(), Length(min=1, max=64)], id='profissao', render_kw={'maxlength': 64})
    empresa_universidade = StringField('Empresa/Universidade', id='empresa_universidade',
        validators=[Length(max=64)])
    biografia = TextAreaField('Breve descrição biográfica, a ser utilizada na divulgação', validators=[InputRequired(),
        Length(min=1, max=1500)], id='biografia', render_kw={'maxlength': 1500})
    foto = FileField('Foto', validators=[
            FileAllowed(['png', 'jpg', 'jpeg'], message=ERRO_EXTENSAO_INVALIDA)
        ])
    tamanho_camiseta = SelectField('Tamanho de Camiseta', choices=get_opcoes_camisetas(),
        id='tamanho_camiseta', coerce=int)
    facebook = StringField('Facebook', id='facebook')
    twitter = StringField('Twitter', id='twitter')
    linkedin = StringField('Linkedin', id='linkedin')
    github = StringField('GitHub', id='github')
    recaptcha = RecaptchaField()
    codigo_url = ''

class CadastroInformacoesMinicurso(FlaskForm):
    titulo = StringField('Título do Minicurso', validators=[InputRequired(), Length(min=1,max=256)], id='titulo', render_kw={'maxlength': 256})
    descricao = TextAreaField('Descrição', validators=[InputRequired(),
        Length(min=1,max=1024)], id='descricao', render_kw={'maxlength': 1024})
    pre_requisitos = TextAreaField('Pré-requisitos recomendados aos participantes', validators=[InputRequired(),
        Length(max=512)], id='pre_requisitos', render_kw={'maxlength': 512})
    planejamento = TextAreaField('Descrição da estrutura do minicurso', validators=[InputRequired(), Length(max=2056)], id='planejamento',
                                 render_kw={'maxlength': 2056})
    apresentacao_extra = FileField('Apresentação extra', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx','rar', 'zip', 'tar', 'z', 'gz', 'taz', 'tgz'],
                    message=ERRO_EXTENSAO_INVALIDA)
        ], id='apresentacao_extra')
    material = FileField('Material', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx','rar', 'zip', 'tar', 'z', 'gz', 'taz', 'tgz'],
                    message=ERRO_EXTENSAO_INVALIDA)
        ], id='material')
    requisitos_ide = TextAreaField('Existe alguma preferência de IDE (Ambiente Integral de Desenvolvimento) ou editor de texto para o minicurso?',
                                    validators=[InputRequired(), Length(max=1024)], id='requisitos_ide', render_kw={'maxlength': 1024})
    requisitos_bibliotecas_pacotes = TextAreaField('Caso existam, especifique todos os pacotes e/ou bibliotecas adicionais que serão utilizados no decorrer do minicurso',
                                                   validators=[InputRequired(), Length(max=1024)], id='requisitos_bibliotecas_pacotes', render_kw={'maxlength': 1024})
    requisitos_dependencias = TextAreaField('Especifique todos os programas e dependências que serão necessários no decorrer do minicurso',
                                                   validators=[InputRequired(), Length(max=1024)], id='requisitos_dependencias', render_kw={'maxlength': 1024})
    requisitos_sistema = TextAreaField('Caso exista, especifique alguma limitação no uso de algum sistema operacional para o minicurso',
                                                   validators=[Length(max=1024)], id='requisitos_sistema', render_kw={'maxlength': 1024})
    requisitos_observacoes = TextAreaField('Existe alguma observação em relação aos requisitos do minicurso?',
                                                   validators=[Length(max=1024)], id='requisitos_observacoes', render_kw={'maxlength': 1024})
    requisitos_github = StringField('No caso da existência de código disponível no GitHub ou em outros repositórios, forneça o link para este repositório ',
                                                   validators=[Length(max=1024)], id='requisitos_github', render_kw={'maxlength': 1024})
    requisitos_hardware = TextAreaField('Caso o minicurso envolva hardware, forneça os requisitos de hardware',
                                        validators=[Length(max=1024)], id='requisitos_hardware', render_kw={'maxlength': 1024})
    dicas_instalacao = TextAreaField('Dicas para instalação dos softwares necessários', id='dicas_instalacao', validators=[Length(max=1024)], render_kw={'maxlength': 1024})
    observacoes = TextAreaField('Observações em geral', id='observacoes', validators=[Length(max=512)], render_kw={'maxlength': 512})
    confirmacao = BooleanField('Li e concordo com Termo e Condições de Inscrição', validators=[InputRequired()])


class CadastroInformacoesPalestra(FlaskForm):
    titulo = StringField('Título da Palestra', validators=[InputRequired(), Length(min=1,max=256)], id='titulo', render_kw={'maxlength': 256})
    descricao = TextAreaField('Descrição', validators=[InputRequired(), Length(min=1,max=1024)], id='descricao', render_kw={'maxlength': 1024})
    requisitos_tecnicos = TextAreaField('Requisitos de Hardware/Software', id='requisitos_tecnicos', validators=[Length(max=1024)], render_kw={'maxlength': 1024})
    planejamento = TextAreaField('Planejamento', validators=[InputRequired(), Length(max=2056)], id='planejamento', render_kw={'maxlength': 2056})
    material = FileField('Material', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'rar', 'zip', 'tar', 'z', 'gz', 'taz', 'tgz'],
                    message=ERRO_EXTENSAO_INVALIDA)
        ], id='material')
    perguntas = TextAreaField('Perguntas referentes à palestra', validators=[InputRequired(), Length(max=1024)], id='perguntas', render_kw={'maxlength': 1024})
    observacoes = TextAreaField('Observações', id='observacoes', validators=[Length(max=512)], render_kw={'maxlength': 512})
    confirmacao = BooleanField('Li e concordo com Termo e Condições de Inscrição', validators=[InputRequired()], id='confirmacao')


class CadastroFeiraDeProjetos(FlaskForm):
    titulo = StringField('Título do Projeto', validators=[InputRequired(), Length(min=1,max=256)], id='titulo', render_kw={'maxlength': 256})
    descricao = TextAreaField('Descrição', validators=[InputRequired(), Length(min=1, max=1024)], id='descricao', render_kw={'maxlength': 1024})
    necessidades = TextAreaField('Necessidades', validators=[InputRequired(), Length(max=1024)], id='necessidades', render_kw={'maxlength': 1024})
    planejamento = TextAreaField('Planejamento', validators=[InputRequired(), Length(max=2056)], id='planejamento', render_kw={'maxlength': 2056})
    observacoes = TextAreaField('Observações', id='observacoes', validators=[Length(max=512)], render_kw={'maxlength': 512})
    confirmacao = BooleanField('Li e concordo com Termo e Condições de Inscrição', validators=[InputRequired()])


class CadastroAtividadeGenerica(FlaskForm):
    titulo = StringField('Título da Atividade', validators=[InputRequired(), Length(min=1,max=256)], id='titulo', render_kw={'maxlength': 256})
    descricao = TextAreaField('Descrição', validators=[InputRequired(), Length(min=1, max=1024)], id='descricao', render_kw={'maxlength': 1024})
    observacoes = TextAreaField('Observações', id='observacoes', validators=[Length(max=512)], render_kw={'maxlength': 512})
    confirmacao = BooleanField('Li e concordo com Termo e Condições de Inscrição', validators=[InputRequired()])


class CadastroInformacoesLocomocaoEstadia(FlaskForm):
    cidade_origem = StringField('Cidade de origem', validators=[InputRequired(), Length(min=1,max=64)], render_kw={'maxlength': 64})
    data_chegada_sanca = DateField('Data de chegada em São Carlos', format='%d/%m/%Y', id='data_chegada_sanca',
        validators=[InputRequired()])
    data_partida_sanca = DateField('Data de partida de São Carlos', format='%d/%m/%Y', id='data_partida_sanca',
        validators=[InputRequired()])
    transporte_ida_volta = BooleanField('Requer que a SECOMP UFSCar pague por seu transporte de ida e volta',
        id='transporte_ida_volta')
    opcoes_transporte_ida_volta = SelectField('De qual modo este ocorrerá?', choices=opcoes_transporte_ida_volta,
                                              id='opcoes_transporte_ida_volta', coerce=int, validators=[RequiredIf(transporte_ida_volta=True)])
    transporte_sanca = BooleanField('Requer que a SECOMP UFSCar se encarregue do seu transporte dentro de São Carlos?',
        id='transporte_sanca')
    opcoes_transporte_sanca = SelectField('De qual modo este ocorrerá?', choices=opcoes_transporte_sanca,
                                          id='opcoes_transporte_sanca', coerce=int, validators=[RequiredIf(transporte_sanca=True)])
    hospedagem = BooleanField('Requer que a SECOMP UFSCar arque com os custos de sua hospedagem?',
        id='hospedagem')
    necessidades_hospedagem = TextAreaField('Quais são as necessidades básicas a serem atendidas pela estadia?',
        id='necessidades_hospedagem', validators=[Length(max=256), RequiredIf(hospedagem=True)])
    observacoes = TextAreaField('Deixe aqui alguma observação ou informação que julgar necessária', id='hospedagem',
        validators=[Length(max=256)], render_kw={'maxlength': 256})


class BugReportForm(BaseRecaptchaForm):
    falha = SelectField('Tipo de Falha Encontrada:', validators=[InputRequired(message=ERRO_INPUT_REQUIRED)], id='falha',
            choices=opcoes_falha, coerce=int)
    outra_falha = StringField("Outra Falha:", validators=[Length(max=64)], id="outra_falha", render_kw={'maxlength': 64})
    autor = StringField('Autor:', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=1, max=64)],
            default='ex: Como você quer ser identificado?', render_kw={'maxlength': 64})
    contato = StringField('Caso queira ser contatado por nós, deixe aqui seu e-mail:', validators=[Optional(), Email(message=ERRO_EMAIL)], id='contato')
    titulo = StringField('Título:', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=1, max=64)], render_kw={'maxlength': 64})
    descricao = TextAreaField('Escreva aqui, de forma clara e precisa, a falha encontrada, com os passos necessários para reproduzi-la:',
            validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(max=1200)], id='descricao', render_kw={'maxlength': 1200})
    impacto = TextAreaField('Escreva aqui o impacto causado pela falha encontrada, caso seja explorada:', validators=[Length(max=300)], id='impacto',
            render_kw={'maxlength': 300})
    anexo = FileField('Caso você tenha um vídeo/imagem que ajude a ilustrar seu report ou uma versão em PDF do report, envie aqui:', validators=[Optional(),
        FileAllowed(['pdf', 'webm', 'mkv', 'gif', 'mp4', 'png', 'jpg', 'jpeg'], message=ERRO_EXTENSAO_INVALIDA)], id='anexo')


class EmailCustom(BaseRecaptchaForm):
    assunto = StringField('Assunto', id='text_assunto')
    titulo = StringField('Título', id='text_titulo')
    template = StringField('Template do Email', id='text_template_email')
    anexo = BooleanField('Anexo', id='cbox_tem_anexo')
    pastaAnexo = StringField('Nome da pasta', id='text_path_anexo')
    baseAnexo = StringField('Base do nome do anexo', id='text_base_anexo')
    complemento = SelectField('Complemento', id='list_complemento_anexo', choices=get_opcoes_ecustom_complemento())
    extencao = SelectField('Extenção', id='list_extencao_anexo', choices=get_opcoes_ecustom_extensao())
    atividades = SelectField('Atividades', id='list_atividades', choices= get_opcoes_ecustom_atividade())
    pesquisaResultado = StringField('Nome: ', id='text_pesquisa_em_resultado')
    todosresultado = BooleanField('Todos', id='cbox_todos_os_usuarios')
    pesquisaSelecionados = StringField('Nome: ', id='text_pesquisa_em_selecionados')


class GerarUrlConteudoForm(FlaskForm):
    tipo_atividade = SelectField("Tipo da Atividade", choices=get_opcoes_tipo_atividade(), id="tipo_atividade", coerce=int, validators=[InputRequired()])


class CadastrarFlagForm(FlaskForm):
    flag = StringField('Flag', validators=[InputRequired(), Length(min=1, max=64)])
    pontos = IntegerField('Pontos', validators=[InputRequired()])


class SubmeterFlagForm(BaseRecaptchaForm):
    flag = StringField('Flag', validators=[InputRequired(), Length(min=1, max=64)])


class GerenciarComprovantesForm(FlaskForm):
    aprovar = IntegerField()
    desaprovar = IntegerField()
    rejeitar = IntegerField()
    autorizar = IntegerField()


class CancelarPagamentoForm(FlaskForm):
    cancelar = IntegerField()


class WifiForm(BaseRecaptchaForm):
    cpf = StringField('CPF:', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=0,max=14)])
    nome = StringField('Nome Completo:', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=1,max=128)])
    email = StringField('Email:', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Email(message=ERRO_EMAIL), Length(min=1, max=128)])


class CadastroPresencialParticipanteForm(FlaskForm):
    usuario = SelectField("Selecione um usuário para o cadastro presencial", choices=get_usuarios_inscricao_pendente(), id="usuario", coerce=int)
    confirmar_email = RadioField('Deseja comprar o kit da SECOMP UFSCar?', id='comprar', choices=[(1,'Sim'),(2,'Não')], coerce=int, default=2)


class FeedbackForm(BaseRecaptchaForm):
    aspectos_gerais = SelectField('Avalie a atividade em aspectos gerais', id='aspectos_gerais', choices=opcoes_avaliacao, coerce=int,
                                  validators=[InputRequired(message=ERRO_INPUT_REQUIRED)])
    conteudo = SelectField('Avalie quanto a conteúdo da atividade', id='conteudo', choices=opcoes_avaliacao, validators=[InputRequired(message=ERRO_INPUT_REQUIRED)], coerce=int)
    conhecimentos_ministrante = SelectField('Avalie quanto ao nível de preparo e conhecimentos do ministrante', id='conhecimentos_ministrante',
                                            choices=opcoes_avaliacao, validators=[InputRequired(message=ERRO_INPUT_REQUIRED)], coerce=int)
    observacoes = StringField('Deixe comentários, se desejar', id='observacoes', validators=[Length(max=500)])


class SorteioForm(FlaskForm):
    atividades = SelectField(choices=get_atividades(), id="atividade", coerce=int)
