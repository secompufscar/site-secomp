from flask import url_for, redirect
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import current_user
import locale
from datetime import datetime
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

from app.models.models import *


class AppIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated and current_user.is_admin():
            self._template_args['usuario'] = current_user
            return super(AppIndexView, self).index()
        return redirect(url_for('views.login'))


class AppModelView(ModelView):
    form_base_class = SecureForm
    can_view_details = True
    column_exclude_list = ['senha', 'token_email', 'token_alteracao_senha', 'salt_alteracao_senha', 'salt']

    def after_model_change(self, form, model, is_created):
        if is_created is not True:
            acao = 'modificado'
        else:
            acao = 'criado'
        hist = AdminModelHistory(id_usuario=current_user.id, acao=acao, nome_modelo=model.__class__.__name__, id_modelo=model.id,
                          data_hora_acao=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(hist)
        db.session.commit()

    def after_model_delete(self, model):
        hist = AdminModelHistory(id_usuario=current_user.id, acao='deletado', nome_modelo=model.__class__.__name__, id_modelo=model.id,
                          data_hora_acao=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(hist)
        db.session.commit()

    @classmethod
    def is_accessible(cls):
        return current_user.is_authenticated and current_user.is_admin()

    @classmethod
    def inaccessible_callback(cls, name, **kwargs):
        return redirect(url_for('views.login'))

class HistoryModelView(ModelView):
    can_edit = False
    can_create = False
    can_delete = False

class AppFileAdmin(FileAdmin):
    @classmethod
    def is_accessible(cls):
        return current_user.is_authenticated and current_user.is_admin()

    @classmethod
    def inaccessible_callback(cls, name, **kwargs):
        return redirect(url_for('views.login'))


def init_app(service, path):
    admin = Admin(service, index_view=AppIndexView(), template_mode='bootstrap3')
    admin.add_view(AppModelView(Usuario, db.session))
    admin.add_view(AppModelView(Evento, db.session))
    admin.add_view(AppModelView(Participante, db.session))
    admin.add_view(AppModelView(Presenca, db.session))
    admin.add_view(AppModelView(Ministrante, db.session))
    admin.add_view(AppModelView(DadosHospedagemTransporte, db.session))
    admin.add_view(AppModelView(RelacaoAtividadeMinistrante, db.session))
    admin.add_view(AppModelView(Atividade, db.session))
    admin.add_view(AppModelView(AreaAtividade, db.session))
    admin.add_view(AppModelView(TipoAtividade, db.session))
    admin.add_view(AppModelView(InfoPalestra, db.session))
    admin.add_view(AppModelView(InfoMinicurso, db.session))
    admin.add_view(AppModelView(InfoFeiraDeProjetos, db.session))
    admin.add_view(AppModelView(Patrocinador, db.session))
    admin.add_view(AppModelView(CotaPatrocinio, db.session))
    admin.add_view(AppModelView(Camiseta, db.session))
    admin.add_view(AppModelView(Permissao, db.session))
    admin.add_view(AppModelView(MembroDeEquipe, db.session))
    admin.add_view(AppModelView(Cargo, db.session))
    admin.add_view(AppModelView(Diretoria, db.session))
    admin.add_view(AppModelView(Curso, db.session))
    admin.add_view(AppModelView(Cidade, db.session))
    admin.add_view(AppModelView(Instituicao, db.session))
    admin.add_view(AppModelView(Pagamento, db.session))
    admin.add_view(AppModelView(CupomDesconto, db.session))
    admin.add_view(HistoryModelView(AdminModelHistory, db.session))
    admin.add_view(AppFileAdmin(path, '/static/', name='Arquivos Estáticos'))
    return admin
