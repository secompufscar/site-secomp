from flask import url_for, redirect
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import current_user, login_required

from app.models.models import *


class AppIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        print(current_user.is_anonymous)
        if (not current_user.is_anonymous) and current_user.autenticado and current_user.admin:
            self._template_args['usuario'] = current_user
            return super(AppIndexView, self).index()
        return redirect(url_for('views.index'))


class AppModelView(ModelView):
    form_base_class = SecureForm
    can_view_details = True
    column_exclude_list = ['senha', 'token_email', 'token_alteracao_senha', 'salt_alteracao_senha', 'salt']

    @classmethod
    def is_accessible(cls):
        return (not current_user.is_anonymous) and current_user.autenticado and current_user.admin

    @classmethod
    def inaccessible_callback(cls, name, **kwargs):
        return redirect(url_for('views.index'))


def init_app(service, path):
    admin = Admin(service, index_view=AppIndexView(), template_mode='bootstrap3')
    admin.add_view(AppModelView(Usuario, db.session))
    admin.add_view(AppModelView(Participante, db.session))
    admin.add_view(AppModelView(Ministrante, db.session))
    admin.add_view(AppModelView(Atividade, db.session))
    admin.add_view(AppModelView(Camiseta, db.session))
    admin.add_view(AppModelView(Permissao, db.session))
    admin.add_view(AppModelView(MembroDeEquipe, db.session))
    admin.add_view(AppModelView(AreaAtividade, db.session))
    admin.add_view(AppModelView(TipoAtividade, db.session))
    admin.add_view(AppModelView(Pagamento, db.session))
    admin.add_view(AppModelView(Evento, db.session))
    admin.add_view(FileAdmin(path, '/static/', name='Arquivos Estáticos'))
    return admin
