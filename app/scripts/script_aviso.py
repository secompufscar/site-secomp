from app.models.models import *
from app.controllers.functions.email import *


def enviar():
    participantes = db.session.query(Participante).all()
    for p in participantes:
        try:
            enviar_email_aviso_tolerancia(p.usuario)
            print(p.usuario)
            print("True no try")
        except:
            print("False no try")
    print(str(len(participantes)))
