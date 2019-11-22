from app.models.models import *
import csv

with open('atividades.csv', 'wb') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['atividade'])
    atividades = db.session.query(Atividade).join(TipoAtividade, TipoAtividade.id == Atividade.id_tipo).filter(TipoAtividade.nome != "Outro").all()
    for atividade in atividades:
        print(atividade.titulo)
        filewriter.writerow([atividade.titulo])
