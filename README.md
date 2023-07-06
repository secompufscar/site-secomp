<h1 align="center">
📄<br>Site Secomp
</h1>

<p  align="center">
Site e principal sistema da Secomp
</p>

---

### Requisitos

-   [![git][git-logo]][git-url]
-   [![mysql][mysql-logo]][mysql-url]
-   [![python][python-logo]][python-url]

### Como rodar

1. Clone the repositório
    ```sh
    git clone https://github.com/secompufscar/site-secomp.git
    ```
2. Acesse a pasta clonada

    ```sh
    cd ./site-secomp
    ```

3. Instale as dependências

    ```sh
    pip install -r requirements.txt 
    ```

3. Crie um arquivo de configurações de desenvolvimento /app/config/development.py

    ```sh
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:password@localhost/secomp"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False
    ```

4. Execute o programa
    ```sh
    python run.py
    ```

<div align="center">
  <br/>
  <br/>
  <br/>
    <div>
      <h1>SECOMP UFSCAR</h1>
      <sub>Copyright © 2023 - <a href="https://github.com/secompufsca">secompufscar</sub></a>
    </div>
    <br/>
    <img src="https://avatars.githubusercontent.com/u/26929251?s=48&v=4" width="40" height="40"/>
</div>

[git-url]: https://git-scm.com/
[git-logo]: https://img.shields.io/badge/Git-f14e32?style=for-the-badge&logo=git&logoColor=white
[mysql-url]: https://www.mysql.com/
[mysql-logo]: https://img.shields.io/badge/Mysql-blue?style=for-the-badge&logo=mysql&logoColor=white
[python-url]: https://www.python.org/
[python-logo]: https://img.shields.io/badge/python-000000?style=for-the-badge&logo=python&logoColor=white