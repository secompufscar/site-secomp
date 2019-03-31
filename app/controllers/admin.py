from flask import url_for, redirect
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app.controllers.forms import *
from flask import render_template, request, redirect, abort, url_for, Blueprint

from app.models.models import *


class AppIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated and current_user.permissao > Permissao.USUARIO.value:
            return super(AppIndexView, self).index()
        return redirect(url_for('index'))


class AppModelView(ModelView):
    can_view_details = True
    column_exclude_list = ['senha', 'token_email', 'token_alteracao_senha', 'salt_alteracao_senha', 'salt']
    def is_accessible(self):
        return current_user.is_authenticated and current_user.permissao > Permissao.USUARIO.value

def init_admin(app):
    admin = Admin(app, index_view=AppIndexView(), template_mode='bootstrap3')
    admin.add_view(AppModelView(Usuario, db.session))
    admin.add_view(AppModelView(Participante, db.session))
    admin.add_view(AppModelView(Ministrante, db.session))
    admin.add_view(AppModelView(Atividade, db.session))
    admin.add_view(AppModelView(Camiseta, db.session))
    admin.add_view(AppModelView(PermissaoUsuarios, db.session))
    admin.add_view(AppModelView(MembroDeEquipe, db.session))
    return admin
