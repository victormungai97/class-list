# tests.py

import unittest
import time
from flask_testing import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app import create_app
from app.database import Base
from app.models import Lecturer, Student, User, Course, Programme

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://dt_admin:dtAdmin@2016@localhost/dreamteam_test'

# set up SQLAlchemy engine for testing db connection and session to handles commits
engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


class TestBase(TestCase):
    # noinspection PyUnresolvedReferences
    def setUp(self):
        """Will be called before every test"""
        # start timer
        self._started_at = time.time()

        # create the database tables
        Base.metadata.create_all(engine)

        # create test department
        department = Programme(id=1, program_id='F17', name='B.sc. (Electrical And Electronic Engineering)', year=5)
        course = Course(cid=101, pid='F17', name='Physics A')

        # save department to database
        db_session.add(department)
        # save a course
        db_session.add(course)

        # create test staff
        self.lecturer = Lecturer(staff_id='123456',
                                 name='staff',
                                 programme='B.sc. (Electrical And Electronic Engineering)',
                                 email='staff@example.com',
                                 rank='Professor',
                                 user=len(User.query.all()) + 1,
                                 is_lecturer=True,
                                 )

        # create test student
        self.student = Student(reg_num='F17/1829/2016',
                               name='student',
                               year_of_study=5,
                               programme='B.sc. (Electrical And Electronic Engineering)',
                               email='student@example.com',
                               class_rep=False,
                               user=len(User.query.all()) + 1,
                               is_student=True
                               )

        # save users to database
        db_session.add(self.lecturer)
        db_session.add(self.student)
        # save changes
        db_session.commit()

    def create_app(self):
        """Will set up testing app"""
        # pass in test configurations
        config_name = 'testing'
        # create brand new application
        self.app = create_app(config_name)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        # get application context to get application from
        self.app_context = self.app.app_context()
        self.app_context.push()
        return self.app

    def tearDown(self):
        """Will be called after every test"""
        # end session
        db_session.remove()
        # delete database tables
        Base.metadata.drop_all(engine)
        # remove application context
        self.app_context.pop()
        # end timer
        elapsed = time.time() - self._started_at
        print('{} ({}s)'.format(self.id(), round(elapsed, 2)))


class TestLecturerModel(TestBase):
    # noinspection PyUnresolvedReferences
    def test_staff_model(self):
        """
        Test number of records in Lecturer table
        """
        self.assertEqual(Lecturer.query.count(), 0)

    def test_password_hashing(self):
        # test password hashing
        self.lecturer.set_password('cat')
        self.assertFalse(self.lecturer.verify_password('dog'))
        self.assertTrue(self.lecturer.verify_password('cat'))


if __name__ == '__main__':
    unittest.main()
