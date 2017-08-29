# app/student/forms.py

import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FileField, Field  # , HiddenField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.widgets import HTMLString, html_params

from populate import year_of_study, dict_to_tuple, courses
from pictures import ALLOWED_EXTENSIONS
from ..models import Programme


class ImageWidget(object):
    """
    Class render an image field in the form
    """
    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("src", field.src)
        kwargs.setdefault("alt", field.alt)
        kwargs.setdefault("class", field.class_)
        kwargs.setdefault("width", field.width)
        kwargs.setdefault("height", field.height)
        if 'value' not in kwargs:
            # noinspection PyProtectedMember
            kwargs['value'] = field._value()

        return HTMLString('<img {param} />'.format(
            param=self.html_params(**kwargs)
        ))


class ImageField(Field):
    """
    Class inherits from the main form field and calls the image rendering widget
    """
    widget = ImageWidget()

    def __init__(self, label=None, validators=None, src="", pid='', alt="Preview", class_="img-circle", width="",
                 height="", **kwargs):
        super(ImageField, self).__init__(label, validators, **kwargs)
        self.id = pid
        self.src = src
        self.alt = alt
        self.class_ = class_
        self.width = width
        self.height = height

    def _value(self):
        if self.data:
            return u''.join(self.data)
        else:
            return u''


class RegistrationForm(FlaskForm):
    """
    Form for the registration of a student
    """
    reg_num = StringField("Registration Number", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    year_of_study = SelectField("Year of Study",
                                choices=dict_to_tuple(year_of_study),
                                validators=[DataRequired()],
                                default='None',
                                coerce=int,
                                )
    programme = SelectField("Programme", validators=[DataRequired()], choices=dict_to_tuple(courses), default="")
    photo = FileField("Pictures",
                      validators=[FileRequired(),
                                  FileAllowed(ALLOWED_EXTENSIONS, "Images Only!")
                                  ],
                      render_kw={"multiple": True}
                      )
    image = ImageField(label="Image", src="#", pid="image", class_="img-circle",
                       width="100", height="100")
    submit = SubmitField("Register")

    def validate(self):
        # check if all required fields are filled
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        # check that correct format of student reg. num is followed
        match = re.search("/[\S]+/", self.reg_num.data)
        if not match:
            self.reg_num.errors.append("Invalid registration number")
            return False

        # check if programme is registered
        program = Programme.query.filter(Programme.program_id == self.programme.data).first()
        # if not registered, raise error
        if not program:
            self.programme.errors.append("Programme not registered")
            return False

        return True

class SignInForm(FlaskForm):
    """
    Form that takes a student's registration number
    """
