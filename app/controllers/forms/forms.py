from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, TextAreaField, HiddenField, IntegerField, FieldList
from wtforms.validators import InputRequired, Email, Length, EqualTo

from app.controllers.forms.options import *
from app.controllers.forms.validators import *
from app.controllers.functions.helpers import get_participantes, get_atividades


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Email(message=ERRO_EMAIL), Length(min=1, max=254)])
    senha = PasswordField('Senha', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=8, max=20, message=ERRO_TAMANHO_SENHA)])


class CadastroForm(FlaskForm):
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
    recaptcha = RecaptchaField()


class ParticipanteForm(FlaskForm):
    kit = BooleanField('Kit', id="kit")
    camiseta = SelectField('Camiseta', choices=get_opcoes_camisetas(
    ), id="camiseta", default="P Feminino", coerce=int)
    restricao_coffee = SelectField(
        'Restrição para o Coffee-Break', choices=opcoes_restricao, default="Nenhum", coerce=int, id="restricao_coffee")


class EditarUsuarioForm(FlaskForm):
    primeiro_nome = StringField('Primeiro Nome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=30)])
    sobrenome = StringField('Sobrenome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=100)])
    email = StringField('Email', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Email(message=ERRO_EMAIL), Length(min=1, max=254)])
    curso = SelectField('Curso', choices=get_opcoes_cursos(),
                        id='curso', coerce=int)
    instituicao = SelectField(
        'Instituição', choices=get_opcoes_instituicoes(), id='instituicao', coerce=int)
    cidade = SelectField(
        'Cidade', choices=get_opcoes_cidades(), id='cidade', coerce=int)
    data_nasc = DateField("Data de Nascimento",
                          format="%d/%m/%Y", id='data-nasc')
    senha = PasswordField('Senha', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=8, max=20, message=ERRO_TAMANHO_SENHA)])


class AlterarSenhaForm(FlaskForm):
    nova_senha = PasswordField('Senha', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), Length(
        min=8, max=20, message=ERRO_TAMANHO_SENHA), EqualTo('confirmacao', message=ERRO_COMPARA_SENHAS)])
    confirmacao = PasswordField('Confirmação de Senha', validators=[
                                InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=8, max=20)])


class AlterarSenhaPorEmailForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Email(message=ERRO_EMAIL), Length(min=1, max=254)])
    recaptcha = RecaptchaField()


class ContatoForm(FlaskForm):
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


class ComprovanteForm(FlaskForm):
    comprovante = FileField('Comprovante de Pagamento', validators=[
            FileRequired(message=ERRO_INPUT_REQUIRED),
            FileAllowed(['png', 'jpg', 'jpeg'], message=ERRO_EXTENSAO_INVALIDA)
        ])


class AlteraCamisetaForm(FlaskForm):
    participante = SelectField("Selecione o usuário", choices=get_participantes(), id="participante", coerce=int)
    camiseta = SelectField("Modelos", choices=get_opcoes_camisetas(), default="P Feminino", id="camiseta", coerce=int)


class VendaKitForm(FlaskForm):
    participante = SelectField("Inscrições na SECOMP 2019", choices=get_participantes(), id="participante", coerce=int)
    camiseta = SelectField("Modelos", choices=get_opcoes_camisetas(), default="P Feminino", id="camiseta", coerce=int)

class ListasParticipantes(FlaskForm):
    atividades = SelectField("Atividades", choices=get_atividades(), id="atividade", coerce=int)
    tipo = SelectField("Modelos", choices=[(0, 'Inscritos'), (1, 'Presentes')], id="tipo", coerce=int)


class CadastroMinistranteForm(FlaskForm):
    primeiro_nome = StringField('Primeiro Nome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=30), so_letras()], id="primeiro_nome")
    sobrenome = StringField('Sobrenome', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Length(min=1, max=100), so_letras()], id="sobrenome")
    email = StringField('Email', validators=[InputRequired(
        message=ERRO_INPUT_REQUIRED), Email(message=ERRO_EMAIL), Length(min=1, max=254), valida_email_ministrante()], id="email")
    senha = PasswordField('Senha', validators=[InputRequired(message=ERRO_INPUT_REQUIRED), EqualTo(
        'confirmacao', message=ERRO_COMPARA_SENHAS), Length(min=8, max=20, message=ERRO_TAMANHO_SENHA)], id="senha")
    confirmacao = PasswordField('Confirmação de Senha', validators=[
        InputRequired(message=ERRO_INPUT_REQUIRED), Length(min=8, max=20)])
    data_nascimento = DateField("Data de Nascimento",
                          format="%d/%m/%Y", id="data_nascimento")
    telefone = StringField('Telefone', validators=[InputRequired(), Length(min=8, max=14)], id='telefone')
    profissao = StringField('Profissão', validators=[InputRequired(), Length(min=1, max=64)], id='profissao')
    empresa_universidade = StringField('Empresa/Universidade', id='empresa_universidade',
        validators=[Length(max=64)])
    biografia = TextAreaField('Breve descrição biográfica, a ser utilizada na divulgação', validators=[InputRequired(),
        Length(min=1, max=1500)], id='biografia')
    foto = StringField('Foto', id='foto')
    tamanho_camiseta = SelectField('Tamanho de Camiseta', choices=get_opcoes_camisetas(), id='tamanho_camiseta', coerce=int)
    facebook = StringField('Facebook', id='facebook')
    twitter = StringField('Twitter', id='twitter')
    linkedin = StringField('Linkedin', id='linkedin')
    github = StringField('GitHub', id='github')
    codigo_url = ''
    recaptcha = RecaptchaField()

class CadastroInformacoesMinicurso(FlaskForm):
    titulo = StringField('Título do Minicurso', validators=[InputRequired(), Length(min=1,max=64)])
    area = SelectField('Área(s)', validators=[InputRequired()], choices=get_opcoes_area_atividade(), coerce=int)
    descricao = TextAreaField('Descrição', validators=[InputRequired(),
        Length(min=1,max=1024)])
    pre_requisitos = TextAreaField('Pré-requisitos recomendados aos participantes', validators=[InputRequired(),
        Length(max=300)])
    planejamento = TextAreaField('Descrição da estrutura do minicurso', validators=[InputRequired()])
    apresentacao_extra = StringField('Previa da apresentação', validators=[Length(max=128)])
    material = TextAreaField('Material', validators=[Length(max=128)])
    requisitos_hardware = TextAreaField('Requisitos de Hardware', validators=[InputRequired(), Length(max=128)])
    requisitos_software = TextAreaField('Requisitos de Software', validators=[InputRequired(), Length(max=128)])
    dicas_instalacao = TextAreaField('Dicas para instalação dos softwares necessários')
    observacoes = TextAreaField('Observações')

class CadastroInformacoesPalestra(FlaskForm):
    titulo = StringField('Título da Palestra', validators=[InputRequired(), Length(min=1,max=64)])
    area = SelectField('Área(s)', validators=[InputRequired()], choices=get_opcoes_area_atividade(), coerce=int)
    descricao = TextAreaField('Descrição', validators=[InputRequired(), Length(min=1,max=1024)])
    requisitos_tecnicos = TextAreaField('Requisitos de Hardware/Software')
    planejamento = TextAreaField('Planejamento', validators=[InputRequired()])
    apresentacao_extra = StringField('Apresentação Extra')
    material = TextAreaField('Descrição')
    perguntas = TextAreaField('Perguntas referentes à palestra', validators=[InputRequired()])
    observacoes = TextAreaField('Observações')

class CadastroFeiraDePesquisas(FlaskForm):
    titulo = StringField('Título da Pesquisa', validators=[InputRequired()])
    area = SelectField('Área(s)', validators=[InputRequired()], choices=get_opcoes_area_atividade(), coerce=int)
    descricao = TextAreaField('Descrição', validators=[InputRequired(), Length(min=1, max=1024)])
    necessidades = TextAreaField('Necessidades', validators=[InputRequired()])
    planejamento = TextAreaField('Planejamento', validators=[InputRequired()])
    observacoes = TextAreaField('Observações')

class CadastroAtividadeGenerica(FlaskForm):
    titulo = StringField('Título da Atividade', validators=[InputRequired()])
    area = SelectField('Área(s)', validators=[InputRequired()], choices=get_opcoes_area_atividade(), coerce=int)
    descricao = TextAreaField('Descrição', validators=[InputRequired(), Length(min=1, max=1024)])
    observacoes = TextAreaField('Observações')

#TODO fazer validator para campo opcoes_transporte_ida_volta ser obrigatorio caso transporte_ida_volta seja verdadeiro
#TODO fazer validator para campo opcoes_transporte_sanca ser obrigatorio caso transporte_sanca seja verdadeiro
#TODO fazer validator para campo necessidades_hospedagem ser obrigatorio caso hospedagem seja verdadeiro
class CadastroInformacoesLocomocaoEstadia(FlaskForm):
    cidade_origem = StringField('Cidade de Origem', validators=[InputRequired(), Length(min=1,max=64)])
    data_chegada_sanca = DateField('Data de Chegada em São Carlos', format='%d/%m/%Y', id='data_chegada_sanca',
        validators=[InputRequired()])
    data_partida_sanca = DateField('Data de Partida de São Carlos', format='%d/%m/%Y', id='data_partida_sanca',
        validators=[InputRequired()])
    transporte_ida_volta = BooleanField('Requer que a SECOMP UFSCar pague por seu transporte de ida e volta',
        id='transporte_ida_volta', validators=[InputRequired()])
    opcoes_transporte_ida_volta = SelectField('De qual modo este ocorrerá?', choices=get_opcoes_transporte(),
        id='opcoes_transporte_ida_volta', validators=[transporte_ida_volta_selecionado()], coerce=int)
    transporte_sanca = BooleanField('Requer que a SECOMP UFSCar se encarregue do seu transporte dentro de São Carlos?',
        validators=[InputRequired()], id='transporte_sanca')
    opcoes_transporte_sanca = SelectField('De qual modo este ocorrerá?', choices=get_opcoes_transporte(),
        id='opcoes_transporte_sanca', validators=[transporte_sanca_selecionado()], coerce=int)
    hospedagem = BooleanField('Requer que a SECOMP UFSCar arque com os custos de sua hospedagem?',
        validators=[InputRequired()], id='hospedagem')
    necessidades_hospedagem = TextAreaField('Quais são as necessidades básicas a serem atendidas pela estadia?',
        id='necessidades_hospedagem', validators=[Length(max=256), hospedagem_selecionada()])
    observacoes = TextAreaField('Deixe aqui alguma observação ou informação que julgar necessária', id='hospedagem',
        validators=[Length(max=256)])

class GerarUrlConteudoForm(FlaskForm):
    tipo_atividade = SelectField("Tipo da Atividade", choices=get_opcoes_tipo_atividade(), id="tipo_atividade", coerce=int, validators=[InputRequired()])

class ConfirmarAtividadeMinistranteForm(FlaskForm):
    vazio = ''
