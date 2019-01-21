from flask import Flask, render_template, url_for
from forms.forms import *
from models.models import *
from passlib.hash import pbkdf2_sha256

@app.route('/')
def index():
    return render_template('index.html', title='Página inciial')

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    form = CadastroForm(csrf_enabled=False)
    if form.validate_on_submit():
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hash = pbkdf2_sha256.encrypt(form.senha.data, rounds=8000, salt_size=15)
        usuario = Usuario(email=form.email.data, senha=hash, ultimo_login=agora,
         data_cadastro=agora, permissao=0, primeiro_nome=form.primeiro_nome.data,
         ult_nome=form.sobrenome.data, curso=form.curso.data, instituicao=form.instituicao.data,
         cidade=form.cidade.data, data_nasc=form.data_nasc.data,
         token_email="asdfghjhtrgdfsda")
        db.session.add(usuario)
        db.session.commit()
        return "AAAAAAAH"
    return render_template('cadastro.html', form=form)
if __name__ == '__main__':
    #app.run()
    app.run(host='localhost', port=8000, debug=True)
