#Variáveis usadas nas mensagens de erro no Formulário
ERRO_INPUT_REQUIRED = "Preencha esse campo"
ERRO_EMAIL = "Entre com um endereço de email válido"
ERRO_COMPARA_SENHAS = "Senhas devem ser iguais"
EDICAO_ATUAL = 10
#TODO Posteriormente criar uma função que seleciona os cursos e instituções no banco de dados
escolhas_curso = [
    ("Ciência da Computação", "Ciência da Computação"),
    ("Engenharia da Computação", "Engenharia da Computação")]

escolhas_instituicao = [
    ("UFSCar", "UFSCar"),
    ("USP", "USP")]

escolhas_cidade = [
    ("São Paulo", "São Paulo"),
    ("São Carlos", "São Carlos")]

escolhas_camiseta = [
    ("P Feminino", "P Feminino"),
    ("M Feminino", "M Feminino"),
    ("G Feminino", "G Feminino"),
    ("P Masculino", "P Masculino"),
    ("M Masculino", "M Masculino"),
    ("G Masculino", "G Masculino")]

escolhas_restricao = [
    (1, "Nenhum"),
    (2, "Vegetariano"),
    (3, "Vegano")]

URL_DEV = "https://0.0.0.0:5000"

dicionario_eventos = [
    {
        "titulo": "9ª SECOMP UFSCar",
        "edicao": 9,
        "participantes": 570,
        "url": "https://0.0.0.0:5000/dashboard-usuario/evento/9"
    },
    {
        "titulo": "10ª SECOMP UFSCar",
        "edicao": 10,
        "participantes": 100,
        "url": "https://0.0.0.0:5000/dashboard-usuario/evento/10"
    }
]
