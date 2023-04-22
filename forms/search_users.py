from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchUsersForm(FlaskForm):
    query = StringField('Full URL/SteamID/SteamID64/Status', validators=[DataRequired()])
    submit = SubmitField('Search')
