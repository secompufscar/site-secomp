from app.models.models import *
import csv

def gerar():

    csvData = [['nome', 'e-mail']]

    participantes = db.session.query(Participante).join(Usuario).order_by(Usuario.primeiro_nome).all()
    for p in participantes:
        csvData.append([str(p.usuario.primeiro_nome) + ' ' + str(p.usuario.sobrenome), str(p.usuario.email)])
    with open('lista_participantes.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    csvFile.close()
