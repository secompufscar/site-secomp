from flask import url_for, redirect
from flask_login import current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin

from app.models.models import *


class AppIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated and current_user.permissao > Permissao.USUARIO.value:
            self._template_args['usuario'] = current_user
            return super(AppIndexView, self).index()
        return redirect(url_for('index'))


class AppModelView(ModelView):
    form_base_class = SecureForm
    can_view_details = True
    column_exclude_list = ['senha', 'token_email', ]

    def is_accessible(self):
        return current_user.is_authenticated and current_user.permissao > Permissao.USUARIO.value
    
    @staticmethod
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


def init_admin(app, path):
    admin = Admin(app, index_view=AppIndexView(), template_mode='bootstrap3')
    admin.add_view(AppModelView(Usuario, db.session))
    admin.add_view(AppModelView(Participante, db.session))
    admin.add_view(AppModelView(Ministrante, db.session))
    admin.add_view(AppModelView(Atividade, db.session))
    admin.add_view(AppModelView(Camiseta, db.session))
    admin.add_view(FileAdmin(path, '/static/', name='Arquivos Estáticos'))
    return admin

