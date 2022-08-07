# app/models.py

import datetime
import jwt
from time import time
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.schema import FetchedValue
# from sqlalchemy_views import CreateView, DropView
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import Base
from app import app, login_manager

from .errors import system_logging


class Class(Base):
    """
    Class maps to the class table
    Contains the ID(autoincrement), start date-time of class, duration, and lecturer teaching course
    I also thought to put a field for active classes so as to separate active classes from completed class
    """
    __tablename__ = 'classes'

    id = Column('id', Integer, primary_key=True)
    time_started = Column('time_started', DateTime, nullable=False, default=datetime.datetime.now, index=True)
    duration = Column('duration', Float, nullable=False, server_default=FetchedValue())
    archived = Column('archived', Boolean, nullable=False, server_default=FetchedValue())
    lec_course_id = Column('lec_course_id',
                           ForeignKey('lecturers_teaching.id', ondelete='CASCADE', onupdate='CASCADE'),
                           nullable=False,
                           index=True)
    is_active = Column('is_active', Boolean, nullable=False, default=False)
    attendance = relationship('Attendance',
                              primaryjoin='Attendance.class_ == Class.id',
                              backref='class')

    def __repr__(self):
        return "<Class Time: {}>".format(self.time_started)


class Programme(Base):
    """
    Class maps the programmes table.
    Contains the ID and name of the department
    """

    __tablename__ = 'programmes'

    id = Column("id", Integer, primary_key=True)
    program_id = Column("program_id", String(8), unique=True, nullable=False)
    name = Column("name", String(80), nullable=False, unique=True)
    year = Column('years', Integer, nullable=False, default=4)
    student = relationship('Student', primaryjoin="Student.programme == Programme.name", backref='student')
    course = relationship('Course', primaryjoin='Course.programme_id == Programme.program_id', backref='course')
    lecturer = relationship('Lecturer', primaryjoin='Lecturer.programme == Programme.name', backref='lecturer')
    lecturer_teaching = relationship('LecturersTeaching',
                                     primaryjoin='LecturersTeaching.programme == Programme.program_id',
                                     backref='lecturer_teaching')
    student_course = relationship('StudentCourses',
                                  primaryjoin='StudentCourses.programme == Programme.program_id',
                                  backref='student_course')

    def __repr__(self):
        return "<Department {}>".format(self.name)


class Course(Base):
    """
    Class maps to the courses table
    It contains the ID, name and relationship to department(programme)
    """

    __tablename__ = 'courses'

    id = Column('id', Integer, primary_key=True)
    programme_id = Column("programme_id", String(8), ForeignKey('programmes.program_id'), nullable=False, index=True)
    name = Column('name', String(80), nullable=False, unique=True)
    lecturers_teaching = relationship('LecturersTeaching',
                                      primaryjoin='LecturersTeaching.courses_id == Course.id',
                                      backref='courses')
    student_courses = relationship('StudentCourses',
                                   primaryjoin='StudentCourses.courses_id == Course.id',
                                   backref='courses2')
    attended = relationship('Attendance',
                            primaryjoin='Attendance.course == Course.name',
                            backref='attended')

    # class_details = relationship("ClassDetails",
    #                            primaryjoin='ClassDetails.CourseName == Course.name '
    #                                       'and ClassDetails.CourseId == Course.id',
    #                           backref='class_details')
    # active_classes = relationship("ActiveClasses",
    #                             primaryjoin='ActiveClasses.CourseName == Course.name '
    #                                        'and ActiveClasses.CourseId == Course.id',
    #                           backref='active_class')

    def __init__(self, cid, pid, name):
        self.id = cid
        self.programme_id = pid
        self.name = name

    def __repr__(self):
        return "<Course {}>".format(self.name)


class User(UserMixin, Base):
    """
    Class that maps to user tables that Lecturer and Student inherit
    """
    __tablename__ = "users"

    user_id = Column("user_id", Integer, primary_key=True)

    @staticmethod
    def encode_auth_token(user_id):
        """
        This function generates the authentication token
        to be used by user, either student or lecturer,
        to request data from or add data to the system
        :param user_id: The ID of the user from User table, not Student or Lecturer tables
        :return: Generated JWT token as string
        """
        try:
            payload = {
                # token expires 30 minutes after login
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
                # token issued at time of login
                'iat': datetime.datetime.utcnow(),
                # token not accepted before time of login
                'nbf': datetime.datetime.utcnow(),
                # this is subject of the token (the user whom it identifies)
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256',
            ).decode('utf-8')
        except Exception as e:
            print(e)
            system_logging(e, exception=True)
            return "Error generating token."

    @staticmethod
    def decode_auth_token(request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Lecturer(User):
    """
    Class maps to the lecturers table
    It contains the ID, name, email and rank of the lecturer/staff
    It will also have a login functionality to validate the staff
    Also contains reference to general users table
    """

    __tablename__ = 'lecturers'

    id = Column('id', Integer, primary_key=True)
    staff_id = Column('staff_id', String(15), unique=True, nullable=False)
    name = Column('name', String(45), nullable=False)
    email = Column('email', String(120), unique=True, nullable=False)
    email_confirmed = Column('email_confirmed', Boolean, nullable=False, default=False)
    rank = Column('rank', String(25), nullable=True)
    programme = Column('programme',
                       String(80),
                       ForeignKey("programmes.name", onupdate='CASCADE', ondelete='CASCADE'),
                       )
    is_lecturer = Column("is_lecturer", Boolean)
    password_hash = Column(String(128))
    user = Column("user", Integer, ForeignKey("users.user_id"))
    lecturers_teaching = relationship('LecturersTeaching',
                                      primaryjoin='LecturersTeaching.lecturers_id == Lecturer.id',
                                      backref='lecturer')

    @property
    def password(self):
        """
        Prevent password from being accessed
        """
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        # generates a JWT token as a string.
        # decode('utf-8') required to convert token which was generated as bytes to string
        # Our payload consists of the user id and duration for validity of the JWT token
        # After the duration, the token sent to the user in the reset password link is considered invalid
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    # noinspection PyUnresolvedReferences
    @staticmethod
    def verify_reset_password_token(token):
        # This method takes a token and attempts to decode it by invoking PyJWT's jwt.decode() function.
        # If the token cannot be validated or is expired, an exception will be raised
        # Return None if error raised
        # If the token is valid, then the value of the reset_password key from the token's payload is the ID of the user
        # , so I can load the user and return it
        try:
            jwt_id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except BaseException as e:
            print(e)
            return None
        return Lecturer.query.filter_by(id=jwt_id).first()

    def __repr__(self):
        return "<Lecturer {}>".format(self.name)


# Set up user_loader
# noinspection PyUnresolvedReferences
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Student(User):
    """
    Class maps to the students table.
    Contains the student's ID, registration number, email, year of study, department
    and whether on is a class representative
    Also contains reference to general users table
    """

    __tablename__ = 'students'

    id = Column("id", Integer, primary_key=True)
    reg_num = Column("reg_num", String(45), unique=True, index=True)
    name = Column("name", String(60), nullable=False, index=True)
    email = Column('email', String(120), unique=True, nullable=False)
    email_confirmed = Column('email_confirmed', Boolean, nullable=False, default=False)
    year_of_study = Column("year_of_study", Integer, nullable=False, index=True)
    programme = Column("programme", String(80), ForeignKey('programmes.name'), nullable=False)
    class_rep = Column("class_rep", Boolean, nullable=False, default=False, index=True)
    is_student = Column("is_student", Boolean)
    user = Column("user", Integer, ForeignKey("users.user_id"))
    attendance = relationship('Attendance',
                              primaryjoin='Attendance.student == Student.reg_num',
                              backref='attendance')
    student_courses = relationship('StudentCourses',
                                   primaryjoin='StudentCourses.student_id == Student.reg_num',
                                   backref='student')
    photo = relationship('Photo', primaryjoin='Photo.student_id == Student.reg_num', backref='photo')

    def __repr__(self):
        return "<Student {}>".format(self.reg_num)


class Photo(Base):
    """
    Class maps to the photos table
    Contains the photo's ID, its address and the student's registration number
    """

    __tablename__ = 'photos'

    id = Column('id', Integer, primary_key=True)
    student_id = Column("student_id", String(45),
                        ForeignKey('students.reg_num', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False,
                        index=True)
    address = Column("address", String(100), nullable=False, unique=True)
    learning = Column("learning", Boolean, nullable=False, server_default=FetchedValue())
    attendance = relationship('Attendance',
                              primaryjoin='Attendance.uploaded_photo == Photo.address',
                              backref='photo')

    def __repr__(self):
        return "<Picture URL {}>".format(self.address)


class LecturersTeaching(Base):
    """
    Class maps the relationship between lecturers and courses
    Contains the ID of the lecturers, departments and courses
    The department field helps to differentiate the courses
    """

    __tablename__ = 'lecturers_teaching'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    lecturers_id = Column('lecturers_id',
                          Integer,
                          ForeignKey('lecturers.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False,
                          primary_key=True,
                          index=True)
    courses_id = Column('courses_id',
                        Integer,
                        ForeignKey('courses.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False,
                        primary_key=True,
                        index=True)
    programme = Column('programme',
                       String(8),
                       ForeignKey('programmes.program_id', ondelete='CASCADE', onupdate='CASCADE'),
                       nullable=False)
    class_ = relationship('Class',
                          primaryjoin='Class.lec_course_id == ''LecturersTeaching.id',
                          backref='lecturers_teaching')

    def __repr__(self):
        return "<Lecturer {}, Course {}.>".format(self.lecturers_id, self.courses_id)


class StudentCourses(Base):
    """
    Class maps the relationship between students and courses
    Contains the ID of the courses, departments and students
    The department field helps to differentiate the courses
    """

    __tablename__ = 'student_courses'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    student_id = Column('student_id',
                        String(45),
                        ForeignKey('students.reg_num', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False,
                        primary_key=True,
                        index=True)
    courses_id = Column('courses_id',
                        Integer,
                        ForeignKey('courses.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False,
                        primary_key=True,
                        index=True)
    programme = Column('programme',
                       String(8),
                       ForeignKey('programmes.program_id', ondelete='CASCADE', onupdate='CASCADE'),
                       nullable=False)

    def __repr__(self):
        return "<Student {}, Course {}.>".format(self.student_id, self.courses_id)


class VerificationStatus(Base):
    """
    Class maps to the table containing the various verification statuses.
    """

    __tablename__ = 'verification_statuses'

    id = Column('id', Integer, primary_key=True)
    description = Column('description', String(40), nullable=False)
    error_message = Column('error_message', String(140), nullable=False)
    attendance = relationship('Attendance',
                              primaryjoin='Attendance.verified == VerificationStatus.id',
                              backref='verification')

    def __repr__(self):
        return "<Verification description: {}, Message {}>".format(self.description, self.error_message)


class Attendance(Base):
    """
    Class that maps the students who attended a given class
    Contains the student's picture, registration number, class attended and verification id
    Also contains the time of attendance and the unit student is attending
    """

    __tablename__ = 'attendance'

    id = Column('id', Integer, primary_key=True)
    student = Column('student',
                     String(45),
                     ForeignKey('students.reg_num', ondelete='CASCADE', onupdate='CASCADE'),
                     primary_key=True,
                     nullable=False)
    class_ = Column('class_',
                    Integer,
                    ForeignKey('classes.id', ondelete='CASCADE', onupdate='CASCADE'),
                    primary_key=True,
                    nullable=False)
    verified = Column('verified',
                      Integer,
                      ForeignKey('verification_statuses.id', ondelete='CASCADE', onupdate='CASCADE'),
                      nullable=True,
                      index=True)
    uploaded_photo = Column("uploaded_photo",
                            String(100),
                            ForeignKey('photos.address', ondelete='CASCADE', onupdate='CASCADE'),
                            primary_key=True,
                            nullable=False)
    course = Column("course",
                    String(80),
                    ForeignKey('courses.name', ondelete='CASCADE', onupdate='CASCADE'))
    time_attended = Column('time_started', DateTime, nullable=False, default=datetime.datetime.now, index=True)

    def __repr__(self):
        return "<Student {} attended class {}.>".format(self.student, self.class_)


class DaysOfTheWeek(Base):
    """
    Class contains the days of the week and their respective IDs
    """
    __tablename__ = 'days_of_the_week'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)

    def __init__(self, day_id, name):
        self.id = day_id
        self.name = name

    def __repr__(self):
        return "Day: {}, ID: {}.".format(self.name, self.id)


class Suggestion(Base):
    """
    Class to store suggestions from user
    """
    __tablename__ = 'suggestions'

    id = Column("id", Integer, primary_key=True)
    title = Column("title", String(20), nullable=False)
    message = Column("message", String(2000), nullable=False)


class Extras(Base):
    """
    Class contains values that are optional but important for the running of the app
    """

    __tablename__ = "extras"

    id = Column("id", Integer, primary_key=True)
    # device user is accessing backend from
    source = Column("source", String(120))
    # gps coordinates
    longitude = Column("longitude", Float, default=0.0)
    latitude = Column("latitude", Float, default=0.0)
    altitude = Column("altitude", Float, default=0.0)
    # cell network coordinates
    lac = Column("LAC", Float, default=0.0)
    cid = Column("CID", Float, default=0.0)
