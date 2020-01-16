from app.models.models import *
import csv

def gerar():

    csvData = [['nome', 'quantidade_kits', 'camiseta']]

    participantes = db.session.query(Participante).join(Usuario).join(Pagamento).filter(Pagamento.efetuado == True).order_by(Usuario.primeiro_nome).all()
    for p in participantes:
        pagamentos = db.session.query(Pagamento).filter(Pagamento.efetuado == True, Pagamento.id_participante == p.id).all()
        c = 0
        camisetas = ''
        for pagamento in pagamentos:
            if c == 0:
                camisetas = pagamentos[0].camiseta.tamanho
            else:
                camisetas = camisetas + ', ' + pagamento.camiseta.tamanho
            c = c + 1
        csvData.append([str(p.usuario.primeiro_nome) + ' ' + str(p.usuario.sobrenome), str(len(pagamentos)), str(camisetas)])
    with open('kit_info.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    csvFile.close()
