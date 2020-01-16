from app.models.models import *
import csv

def gerar():

    csvData = [['nome', 'email']]

    participantes = db.session.query(Participante).all()

    for p in participantes:
        csvData.append([str(p.usuario.primeiro_nome) + ' ' + str(p.usuario.sobrenome), str(p.usuario.email)])
    with open('desafio.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    csvFile.close()
