'''Module that creates web form using FLASK-WTF'''
# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.widgets import html_params, HTMLString
#from wtforms_components import TimeField - creates HTML time input
# eg time = TimeField("time")
from app import app

class RegisterForm(FlaskForm):
  '''Form for registration'''
  # DataRequired validator checks field is not empty
  regno = StringField('Reg No',validators=[DataRequired()])
  name = TextField('Name',validators=[DataRequired()])
  picture = FileField('Picture',validators=[FileRequired(),
        FileAllowed(app.config['ALLOWED_EXTENSIONS'], "Images only!")
	  ])
  submit = SubmitField('submit')
  
class ButtonWidget(object):
	"""
	Renders a button field
	"""
	input_type = 'button' # set type to button not submit
	html_params = staticmethod(html_params)
		
	def __call__(self, field, **kwargs):
		kwargs.setdefault('id',field.id)
		kwargs.setdefault('type',field.input_type)
		kwargs.setdefault('onclick',field.onclick)
		kwargs.setdefault('class',field.class_)
		if 'value' not in kwargs:
			kwargs['value'] = field._value()
			
		return HTMLString('<button {param}>{label}</button>'.format(
			param = self.html_params(name=field.name,**kwargs),
			label = field.label.text
			)
		)

class ButtonField(SubmitField):
	"""
	Field to be rendered
	"""
	widget = ButtonWidget()
	
	def __init__(self, label=None, validators=None, input_type='button', onclick=None, class_='btn btn-basic', **kwargs):
		super(ButtonField,self).__init__(label, validators, **kwargs)
		self.onclick = onclick
		self.input_type = input_type
		self.class_ = class_
		
	def _value(self):
		if self.data: return u''.join(self.data)
		else: return u''

class SignInForm(RegisterForm):
  '''
  Form for signing in to class
  '''
  location = ButtonField('Location',onclick="getLocation()",class_='btn btn-link')
  latitude = HiddenField("latitude",validators=[DataRequired("Please tap the location button")])
  longitude = HiddenField("longitude")