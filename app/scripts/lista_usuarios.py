from app.models.models import *
import csv

def gerar():

    csvData = [['nome', 'e-mail']]

    usuarios = db.session.query(Usuario).order_by(Usuario.primeiro_nome).all()
    for usuario in usuarios:
        participante = db.session.query(Participante).join(Evento).filter(Participante.id_usuario == usuario.id, Evento.edicao == 10).first()
        if participante is None and "MINISTRANTE" not in usuario.getPermissoes() and usuario.primeiro_nome is not None and usuario.sobrenome is not None:
            csvData.append([str(usuario.primeiro_nome) + ' ' + str(usuario.sobrenome), str(usuario.email)])

    with open('lista_usuarios_sem_inscricao.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    csvFile.close()
