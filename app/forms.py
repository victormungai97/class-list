'''Module that creates web form using FLASK-WTF'''
# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
#from wtforms_components import TimeField - creates HTML time input
# eg time = TimeField("time")
from app import app

class RegisterForm(FlaskForm):
  '''Form for registration'''
  # DataRequired validator checks field is not empty
  regno = StringField('regno',validators=[DataRequired()])
  name = TextField('name',validators=[DataRequired()])
  picture = FileField('picture',validators=[FileRequired(),
        FileAllowed(app.config['ALLOWED_EXTENSIONS'], "Images only!")
	  ])
