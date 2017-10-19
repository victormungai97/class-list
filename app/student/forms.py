# app/student/forms.py

import re
from flask_wtf import FlaskForm
from flask_login import login_user
from wtforms import StringField, SubmitField, SelectField, FileField, Field, SelectMultipleField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.widgets import HTMLString, html_params

from populate import year_of_study, dict_to_tuple, courses
from pictures import ALLOWED_EXTENSIONS
from ..models import Programme, Course, StudentCourses, Student


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
    email = StringField("Email", validators=[Email(), DataRequired()])
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

        # check if student is already registered
        if Student.query.filter_by(reg_num=self.reg_num.data).first():
            self.reg_num.errors.append('Registration number already registered')
            return False

        # check if email already registered
        lecturer = Student.query.filter_by(email=self.email.data).first()
        if lecturer:
            self.email.errors.append("Email already registered")
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


class CourseForm(FlaskForm):
    """
    This form registers the course that a student takes.
    It takes the program, year, semester and code of the course
    """
    reg_num = StringField("Registration Number", validators=[DataRequired()], render_kw={"disabled": True})
    programme = SelectField("Department", validators=[DataRequired()],
                            choices=[(programme.program_id, programme.name) for programme in Programme.query.all()],
                            default="")
    study_year = SelectField("Year", validators=[DataRequired()], choices=dict_to_tuple(year_of_study), coerce=int)
    semester = SelectField("Semester", validators=[DataRequired()], choices=[(1, "I"), (2, "II")], coerce=int)
    course = SelectMultipleField("Course", validators=[DataRequired()],
                                 choices=[(course.id, course.name) for course in Course.query.all()],
                                 coerce=int)
    submit = SubmitField("Submit")

    def validate(self):
        # check that all required fields have been filled
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        # check if student is registered in Students table and raise error if not
        student = Student.query.filter_by(reg_num=self.reg_num.data).first()
        if not student:
            self.reg_num.errors.append("Registration number not recognised")
            return False

        # check if student has already registered given course and raise error if so
        for unit in self.course.data:
            registered = StudentCourses.query.filter((StudentCourses.student_id == self.reg_num.data) &
                                                     (StudentCourses.courses_id == unit)).first()
            if registered:
                self.course.errors.append("Course '{}' registered".format(
                    Course.query.filter_by(id=unit).first().name))
                return False

        return True


class SignInForm(FlaskForm):
    """
    Form to sign in a class
    """
    # reg_num = StringField("Registration Number", validators=[DataRequired()],render_kw={"disabled":True})
    photo = FileField("Picture",
                      validators=[FileRequired(),
                                  FileAllowed(ALLOWED_EXTENSIONS, "Images Only!")
                                  ],
                      )
    image = ImageField(label="Image", src='#', pid="image", class_="img-circle",
                       width="100", height='100')
    submit = SubmitField("Sign In")


class LoginForm(FlaskForm):
    """
    Form for student to login
    """
    reg_num = StringField("Registration Number", [DataRequired()])
    submit = SubmitField("Login")
    student_ = ''

    def validate(self):
        # check that all required fields have been filled
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        # check if given student reg no. is already registered
        student_ = Student.query.filter_by(reg_num=self.reg_num.data).first()
        if not student_:
            self.reg_num.errors.append("Unknown Registration Number")
            return False

        # save lecturer
        self.student_ = student_
        # log staff in
        login_user(student_)
        # successful validation
        return True


class ClassForm(FlaskForm):
    """
    Form to start a class
    """
    courses = SelectField("Course", validators=[DataRequired()])
