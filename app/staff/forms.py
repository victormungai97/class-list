# app/staff/forms.py

from flask_login import login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from populate import courses, staff_roles, year_of_study, dict_to_tuple
from ..models import Lecturer, Programme, Course, LecturersTeaching
from ..database import db_session


class RegistrationForm(FlaskForm):
    """
    Form for the registration of a staff member
    This form contains data on the staff's id, name, email, rank and password which the user will input
    so as to register into the database
    """
    staff_id = StringField("Staff ID", validators=[DataRequired("This field is required")])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[Email(), DataRequired()])
    programme = SelectField("Department", validators=[DataRequired()], choices=dict_to_tuple(courses), default="")
    rank = SelectField("Role", validators=[DataRequired("This field is required")], choices=dict_to_tuple(staff_roles),
                       coerce=int)
    password = PasswordField("Password", validators=[DataRequired(),
                                                     Length(min=6, max=14,
                                                            message="Password should be between 6 to 14 characters"),
                                                     ])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(),
                                                                     EqualTo('password',
                                                                             message="Passwords should match")
                                                                     ])
    submit = SubmitField(label="Register")
    lecturer = None

    def validate(self):
        # check if all required fields are filled
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        # check if staff ID already registered
        lecturer = Lecturer.query.filter_by(staff_id=self.staff_id.data).first()
        if lecturer:
            self.staff_id.errors.append("Staff ID already registered")
            return False

        # check if email already registered
        lecturer = Lecturer.query.filter_by(email=self.email.data).first()
        if lecturer:
            self.email.errors.append("Email already registered")
            return False

        # check if rank has been chosen and raise error if not
        if self.rank.data == 0:
            self.rank.errors.append("Please select a role")
            return False

        # if someone selects rank as chairman
        if self.rank.data == 1:
            # check if chairman of given dept already registered
            chairman = Lecturer.query.filter((Lecturer.rank == staff_roles.get(self.rank.data)) &
                                             (Lecturer.programme == courses.get(self.programme.data))).first()
            # if registered, raise error
            if chairman:
                self.rank.errors.append("Chairman of {} already registered".format(courses.get(self.programme.data)))
                return False

        # check if programme is registered
        program = Programme.query.filter(Programme.program_id == self.programme.data).first()
        # if not registered and rank is 'Chairman', create programme
        if not program:
            if self.rank.data == 1:
                programme = Programme(program_id=self.programme.data,
                                      name=courses.get(self.programme.data)
                                      )
                db_session.add(programme)
                db_session.commit()
            else:
                self.programme.errors.append("Programme not registered")
                return False

        # save lecturer
        self.lecturer = lecturer
        # successful validation
        return True


class LoginForm(FlaskForm):
    """
    This form facilitates the logging in of a staff members
    It requires the user's staff ID, email and password
    """
    staff_id = StringField("Staff ID", validators=[DataRequired("Please enter the staff ID")])
    password = PasswordField("Password", validators=[DataRequired(),
                                                     Length(min=6,
                                                            max=14,
                                                            message="Passwords should be between 6 to 14 characters"
                                                            )
                                                     ])
    remember_me = BooleanField("Remember Me", default=True)
    submit = SubmitField(label="Login")
    lecturer = None

    def validate(self):
        # check that all required fields have been filled
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        # check if given staff ID is already registered
        lecturer = Lecturer.query.filter_by(staff_id=self.staff_id.data).first()
        if not lecturer:
            self.staff_id.errors.append("Unknown Staff ID")
            return False

        # validate password
        if not lecturer.verify_password(password=self.password.data):
            self.password.errors.append("Invalid password")
            return False

        # save lecturer
        self.lecturer = lecturer
        # log staff in
        login_user(lecturer)
        # successful validation
        return True


class CourseForm(FlaskForm):
    """
    This form registers the course that a lecturer teaches
    It takes the program, year, semester and code of the course that the lecturer will teach
    """
    programme = SelectField("Department", validators=[DataRequired()], choices=dict_to_tuple(courses), default="")
    study_year = SelectField("Year", validators=[DataRequired()], choices=dict_to_tuple(year_of_study), coerce=int)
    semester = SelectField("Semester", validators=[DataRequired()], choices=[(1, "I"), (2, "II")], coerce=int)
    course = SelectField("Course", validators=[DataRequired()],
                         choices=[(course.id, course.name) for course in Course.query.all()],
                         coerce=int)
    submit = SubmitField("Submit")
    staff_id = ''

    def validate(self):
        # check that all required fields have been filled
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        # check if lecturer has already registered given course and raise error if so
        registered = LecturersTeaching.query.filter((LecturersTeaching.lecturers_id == self.staff_id) &
                                                    (LecturersTeaching.courses_id == self.course.data)).first()
        if registered:
            self.course.errors.append("Course already registered")
            return False

        return True


class ClassForm(FlaskForm):
    """
    Form to start a class
    """
    courses = SelectField("Course", validators=[DataRequired()])
