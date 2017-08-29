# app/models.py

import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.schema import FetchedValue
# from sqlalchemy_views import CreateView, DropView
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import Base
from app import login_manager


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
    name = Column("name", String(60), nullable=False, unique=True)
    student = relationship('Student', primaryjoin="Student.programme == Programme.program_id", backref='student')
    course = relationship('Course', primaryjoin='Course.programme_id == Programme.program_id', backref='course')
    lecturer = relationship('Lecturer', primaryjoin='Lecturer.programme == Programme.name', backref='lecturer')

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
    name = Column('name', String(45), nullable=False, unique=True)
    lecturers_teaching = relationship('LecturersTeaching',
                                      primaryjoin='LecturersTeaching.courses_id == Course.id',
                                      backref='courses')

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


class Lecturer(UserMixin, Base):
    """
    Class maps to the lecturers table
    It contains the ID, name, email and rank of the lecturer/staff
    It will also have a login functionality to validate the staff
    """

    __tablename__ = 'lecturers'

    id = Column('id', Integer, primary_key=True)
    staff_id = Column('staff_id', String(15), unique=True, nullable=False)
    name = Column('name', String(45), nullable=False)
    email = Column('email', String(120), unique=True, nullable=False)
    rank = Column('rank', String(25), nullable=True)
    programme = Column('programme',
                       String(60),
                       ForeignKey("programmes.name", onupdate='CASCADE', ondelete='CASCADE'),
                       )
    password_hash = Column(String(128))
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

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<Lecturer {}>".format(self.name)


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return Lecturer.query.get(int(user_id))


class Student(Base):
    """
    Class maps to the students table.
    Contains the student's ID, registration number, year of study, department and whether on is a class representative
    """

    __tablename__ = 'students'

    id = Column("id", Integer, primary_key=True)
    reg_num = Column("reg_num", String(45), unique=True, index=True)
    name = Column("name", String(60), nullable=False, index=True)
    year_of_study = Column("year_of_study", Integer, nullable=False, index=True)
    programme = Column("programme", String(8), ForeignKey('programmes.program_id'), nullable=False)
    class_rep = Column("class_rep", Boolean, nullable=False, default=False, index=True)
    attendance = relationship('Attendance',
                              primaryjoin='Attendance.student == Student.reg_num',
                              backref='attendance')
    photo = relationship('Photo', primaryjoin='Photo.student_id == Student.reg_num', backref='photo')

    def __repr__(self):
        return "<Student {}>".format(self.reg_num)


class Photo(Base):
    """
    Class maps to the photos table
    Contains the photo's ID, itsaddress and the student's registration number
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
    Contains the ID of the lecturers and students
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
    class_ = relationship('Class',
                          primaryjoin='Class.lec_course_id == ''LecturersTeaching.id',
                          backref='lecturers_teaching')

    def __repr__(self):
        return "<Lecturer {}, Course {}.>".format(self.lecturers_id, self.courses_id)


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
                      nullable=False,
                      index=True)
    uploaded_photo = Column("uploaded_photo",
                            String(100),
                            ForeignKey('photos.address', ondelete='CASCADE', onupdate='CASCADE'),
                            primary_key=True,
                            nullable=False)

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
