from app.models.models import *
from app.controllers.functions.email import *

def enviar():
    usuarios = db.session.query(Usuario).all()
    for usuario in usuarios:
        c = 0
        for p in usuario.participantes_associados:
            c = c + 1
        if c == 0 and usuario.ministrante is None:
            enviar_email_aviso_inscricao(usuario)
            print(usuario)
