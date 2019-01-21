from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


class LoginForm(FlaskForm):
    email = StringField('email')
    password = PasswordField('password')
    submit = SubmitField('submit')