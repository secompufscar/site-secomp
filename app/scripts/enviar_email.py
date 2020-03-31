from app.models.models import *
from app.controllers.functions.email import *


def enviar():
    credenciados = db.session.query(Atividade).filter_by(titulo="Credenciamento").first().participantes
    for p in credenciados:
        enviar_email_feedback(p.usuario)
