from random import SystemRandom

from flask import render_template, request, redirect, abort, url_for, Blueprint
from flask import jsonify
from app.controllers.functions.dictionaries import *

import json

from app.models.models import *

api = Blueprint('api', __name__, static_folder='static',
                       template_folder='templates', url_prefix='/api')

#@api.route('/')
def index():
    return "Welcome to SECOMP: API"

#@api.route('/equipe')
def equipe():
    return "Esperando JSON da Equipe"
#    with open('./app/config/membros_org.json', 'r') as out:
#        return out

#@api.route('/patrocinadores')
def patrocinadores():
    return  jsonify(get_patrocinadores())

#@api.route('/img/<url>')
def retornaImg(url):
    return url #TODO (quando estiver no servidor) hospedagem de imagens
