from app.models.models import *
import csv


def gerar(id_minicurso):

    csvData = [["nome", "e-mail"]]

    atv = db.session.query(Atividade).get(id_minicurso)
    for p in sorted(atv.participantes, key=lambda x: x.usuario.primeiro_nome, reverse=False):
        csvData.append([str(p.usuario.primeiro_nome) + " " + str(p.usuario.sobrenome), str(p.usuario.email)])

    with open("lista_participantes_minicurso" + str(id_minicurso) + ".csv", "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    csvFile.close()


def listar():
    atvs = db.session.query(Atividade).join(TipoAtividade).filter(TipoAtividade.nome == "Minicurso").all()
    for a in atvs:
        if a.titulo is not None:
            print(str(a.id) + " - " + str(a.titulo))
