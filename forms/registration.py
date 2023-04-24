from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired

"""Форма регистрации"""


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat the password', validators=[DataRequired()])
    submit = SubmitField('Sign up')
