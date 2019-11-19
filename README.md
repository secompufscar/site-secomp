# X SECOMP

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b51e0e662bf840bfab9bcacb087cd670)](https://app.codacy.com/app/g4briel.4lves/site-secomp?utm_source=github.com&utm_medium=referral&utm_content=secompufscar/site-secomp&utm_campaign=Badge_Grade_Settings)

> Este é o repositório do código fonte usado no site da [Semana
> da Computação da UFSCar](https://secompufscar.com.br/).

## Dependências
Antes de rodar o servidor, instalar as seguintes dependências:
### Debian Based
- `sudo apt install mysql-server zlib1g-dev libffi-dev python3-dev python3-venv`
### Arch Based
- `sudo pacman -S mariadb zlib libffi`
### Pip
- `pip install -r requirements.txt`

## Configuração
Antes de iniciar o servidor é necessário configurar as variáveis de ambiente a seguir:
- `FLASK_CONFIGURATION` nome do arquivo de configuração `.py` usado em `app/config/`
- `FLASK_APP` path para o construtor do objeto `Flask()`, setar para `app:create_app()`
