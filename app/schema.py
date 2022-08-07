# app/schema.py

import graphene
import re
import os
from graphene import relay, Node, ClientIDMutation, Field, String, Int
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphene_file_upload.scalars import Upload
from flask_jwt_extended import (create_access_token, create_refresh_token)

from app import app
from . import numOfImages
from .extras import zipfile_handling, add_student, staff_send_confirmation_email, get_non_blank_input, validate_email
from .errors import system_logging
from .models import Programme, Lecturer, Student, User
from .email import send_password_reset_email
from .database import db_session
from pictures import decode_image
from populate import key_from_value, courses, year_of_study

"""
We can build our API via GraphQL
In this script, we are going to represent our objects as a graph structure for use with GraphQL
GraphQL has the advantage of less code and less endpoints than REST as we only need to define what data we need, 
not how to get the data, thus creating a headless CMS by decoupling the frontend from backend
"""


# NODES
# Are interfaces provided by graphene.relay that contain a single field id that are ID!
# These provide connections between the schema and the tables of the database
class DepartmentNode(SQLAlchemyObjectType):
    class Meta:
        description = "This connects to the departments belonging to an institution." \
                      "From here, we can obtain information on departments and possibly add new ones."
        model = Programme
        interfaces = (Node,)


class UserNode(SQLAlchemyObjectType):
    class Meta:
        model = User
        interfaces = (Node,)


class LecturerNode(SQLAlchemyObjectType):
    class Meta:
        description = "Provides information on the staff that belong to an institution"
        model = Lecturer
        interfaces = (Node,)
        # of course, password shouldn't be available for viewing
        exclude_fields = ('password_hash',)


class StudentNode(SQLAlchemyObjectType):
    class Meta:
        description = "Provides information on the students that belong to an institution"
        model = Student
        interfaces = Node,


# QUERIES
# These are used to get data from the database, including data pertaining to a specific maybe name

# noinspection PyMethodMayBeStatic
class ImageNumberQuery(graphene.ObjectType):
    name = "No. of images"
    description = "Number of images of each student's face required for registration"
    number_images = Int()

    def resolve_number_images(self, _):
        return numOfImages


# noinspection PyMethodMayBeStatic,PyUnresolvedReferences
class DepartmentQuery(graphene.ObjectType):
    department_node = relay.Node.Field(DepartmentNode)
    single_department = SQLAlchemyConnectionField(DepartmentNode)  # get specific node
    # find all pertaining to given argument(s) of lambda function
    find_department = Field(lambda: DepartmentNode, program_id=String())
    all_departments = SQLAlchemyConnectionField(DepartmentNode)

    def resolve_find_department(self, _, **kwargs):
        return Programme.query.filter(Programme.program_id == kwargs.get('program_id')).first()


class UserQuery(graphene.ObjectType):
    user_node = relay.Node.Field(UserNode)
    single_user = SQLAlchemyConnectionField(UserNode)
    all_users = SQLAlchemyConnectionField(UserNode)


class LecturerQuery(graphene.ObjectType):
    lecturer_node = relay.Node.Field(LecturerNode)
    single_lecturer = SQLAlchemyConnectionField(LecturerNode)
    all_lecturers = SQLAlchemyConnectionField(LecturerNode)


class StudentQuery(graphene.ObjectType):
    student_node = relay.Node.Field(StudentNode)
    single_student = SQLAlchemyConnectionField(StudentNode)
    all_students = SQLAlchemyConnectionField(StudentNode)


def capitalise(word=''):
    """
    This function returns a capitalised form of the string given
    :param word: String to be capitalised
    :return: Capitalised string
    """
    word_list = list(word)  # type: list
    for i in range(len(word_list)):
        word_list[i] = word_list[i].upper()
    return "".join(word_list)


# MUTATIONS
# These are used to add or update data in database

# noinspection PyUnresolvedReferences,DuplicatedCode
class NewStudent(ClientIDMutation):
    # output = MutationPayload
    message = String(required=True)
    status = Int(required=True)
    student_node = Field(StudentNode)

    class Input:  # appears as suggestions in the graphiQl interface in the input set
        reg_no = String(required=True)
        name = String(required=True)
        email = String(required=True)
        year = String(required=True)
        department = String(required=True)
        zip_file = String()  # receive registration images as zip file

    @classmethod
    def mutate_and_get_payload(cls, _, __, **args):
        try:
            message, status, reg_no = get_non_blank_input(capitalise(args.get('reg_no').strip()), "Registration number")
            if status:
                return NewStudent(message=message, status=status, student_node=None)
            message, status, name = get_non_blank_input(args.get('name').strip().title(), "Student name")
            if status:
                return NewStudent(message=message, status=status, student_node=None)
            message, status, email = get_non_blank_input(args.get('email').strip(), "Student email address")
            if status:
                return NewStudent(message=message, status=status, student_node=None)
            message, status, department = get_non_blank_input(args.get('department').strip(), "Department")
            if status:
                return NewStudent(message=message, status=status, student_node=None)
            zip_file = args.get('zip_file')
            student = None

            try:
                year = key_from_value(args.get('year').upper(), year_of_study)[0]
            except BaseException as err:
                print(err)
                system_logging(err, exception=True)
                if repr(err) == "IndexError('list index out of range',)":
                    return NewStudent(message="Year selected not within department's range", status=8,
                                      student_node=None)
                else:
                    return NewStudent(message='Something went wrong. Please contact the system administrator',
                                      status=-1, student_node=None)

            # check that correct format of student reg. num is followed
            if not re.search(r"\w\d\d/[\d]+/\d\d\d\d", reg_no):
                return NewStudent(message='Invalid registration number', status=4, student_node=None)

            # check that correct format of email is followed
            message, status = validate_email(email)
            if status:
                return NewStudent(message=message, status=status, student_node=None)

            # check if student is already registered
            if Student.query.filter_by(reg_num=reg_no).first():
                return NewStudent(message='Registration number already registered', status=2, student_node=None)

            if Student.query.filter_by(email=email).first():
                return NewStudent(message='Email already registered', status=5, student_node=None)

            # confirm that registration number given matches the department selected
            if reg_no.split('/')[0] not in key_from_value(department, courses):
                return NewStudent(message='Registration number does not belong to this programme', status=6,
                                  student_node=None)

            # check if programme is registered
            program = Programme.query.filter(Programme.name == department).first()
            # if not registered, raise error
            if not program:
                return NewStudent(message='Programme not registered', status=7, student_node=None)

            # check if year selected is within years allocated to department
            if year > Programme.query.filter_by(name=department).first().year:
                return NewStudent(message="Year selected is beyond department's range", status=8, student_node=None)

            # receive and save zip file
            message, status, pic_url = zipfile_handling(zip_file=decode_image(zip_file, name, reg_no, ext='.zip'),
                                                        reg_no=reg_no, name=name)

            # successful unzipping
            if not status:
                print(reg_no, name, email, year, department, pic_url, sep=', ', end='\n')
                message, status, student = add_student(reg_no, name, year, department, email, pic_url)
            return NewStudent(student_node=student, message=message, status=status)
        except BaseException as err:
            print(err)
            system_logging(err, exception=True)
            return NewStudent(message='Something went wrong. Please contact the system administrator', status=-1,
                              student_node=None)


# noinspection DuplicatedCode
class NewStaff(ClientIDMutation):
    message = String(required=True)
    status = Int(required=True)
    staff_node = Field(LecturerNode)

    class Input:
        staff_id = String(required=True)
        name = String(required=True)
        email = String(required=True)
        role = String(required=True)
        department = String(required=True)
        password = String(required=True)

    # noinspection PyUnresolvedReferences
    @classmethod
    def mutate_and_get_payload(cls, _, __, **args):
        try:
            message, status, staff_id = get_non_blank_input(capitalise(args.get('staff_id').strip()), "Staff ID number")
            if status:
                return NewStaff(message=message, status=status, staff_node=None)
            message, status, name = get_non_blank_input(args.get('name').strip().title(), "Staff name")
            if status:
                return NewStaff(message=message, status=status, staff_node=None)
            message, status, email = get_non_blank_input(args.get('email').strip(), "Staff email address")
            if status:
                return NewStaff(message=message, status=status, staff_node=None)
            message, status, department = get_non_blank_input(args.get('department').strip(), "Department")
            if status:
                return NewStaff(message=message, status=status, staff_node=None)
            message, status, role = get_non_blank_input(args.get('role').strip().title(), "Role")
            if status:
                return NewStaff(message=message, status=status, staff_node=None)
            password = args.get('password') or ''
            staff = None

            # check that correct format of email is followed
            message, status = validate_email(email)
            if status:
                return NewStaff(message=message, status=status, staff_node=None)

            # check if staff ID already registered
            if Lecturer.query.filter_by(staff_id=staff_id).first():
                return NewStaff(message="Staff ID already registered", status=2, staff_node=None)

            # check if email already registered
            if Lecturer.query.filter_by(email=email).first():
                return NewStaff(message='Email already registered', status=3, staff_node=None)

            # check if password of required length
            if len(password) < 6 or len(password) > 14:
                return NewStaff(message='Password should be between 6 to 14 characters', status=4, staff_node=None)

            # check if rank has been chosen and raise error if not
            if role == "None" or not role:
                return NewStaff(message="Please select a role", status=5, staff_node=None)

            # if someone selects rank as chairman
            if role == 'Chairman':
                # check if chairman of given dept already registered
                chairman = Lecturer.query.filter((Lecturer.rank == role) & (Lecturer.programme == department)).first()
                # if registered, raise error
                if chairman:
                    return NewStaff(message="Chairman of {} already registered".format(department), status=6,
                                    staff_node=None)

            # check if programme is registered
            program = Programme.query.filter(Programme.name == department).first()
            # if not registered and rank is 'Chairman', create programme
            if not program:
                # if not registered and rank is 'Chairman', create programme
                if not program:
                    if role == 'Chairman':
                        programme = Programme(program_id=key_from_value(department, courses)[0], name=department)
                        db_session.add(programme)
                        db_session.commit()
                    else:
                        return NewStaff(message='Programme not registered', status=7, staff_node=None)

            message, status = '', 0
            try:
                # noinspection PyArgumentList
                staff = Lecturer(staff_id=staff_id,
                                 name=name,
                                 programme=department,
                                 email=email,
                                 rank=role,
                                 password=password,
                                 user=len(User.query.all()) + 1,
                                 is_lecturer=True,
                                 email_confirmed=False,
                                 )
                # add staff to database
                db_session.add(staff)
                db_session.commit()
                # Now we'll send the email confirmation link
                staff_send_confirmation_email(email, name)
                # send message of successful registration
                message = "Successful registration of {}. Please check your email to activate your account".format(name)
            except BaseException as err:
                print(err)
                message, status = "Error during student registration", 1
            return NewStaff(message=message, status=status, staff_node=staff)
        except BaseException as err:
            print(err)
            system_logging(err, exception=True)
            return NewStaff(message='Something went wrong. Please contact the system administrator', status=-1,
                            staff_node=None)


class ResetStaffPassword(ClientIDMutation):
    message = String(required=True)
    status = Int(required=True)
    staff_node = Field(LecturerNode)

    class Input:
        staff_id = String(required=True)

    # noinspection PyUnresolvedReferences
    @classmethod
    def mutate_and_get_payload(cls, _, __, **args):
        try:
            message, status, staff_id = get_non_blank_input(args.get('staff_id').strip(), "Staff ID number")
            if status:
                return ResetStaffPassword(message=message, status=status, staff_node=None)
            staff = Lecturer.query.filter_by(staff_id=staff_id).first()
            if staff:
                send_password_reset_email(staff)
            # To prevent figuring out IDs of registered users,
            # send this message and redirect to login regardless of whether user is known or not
            message = 'Check your email for instructions on resetting your password'
            return ResetStaffPassword(staff_node=staff, message=message, status=0)
        except BaseException as err:
            print(err)
            system_logging(err, exception=True)
            return ResetStaffPassword(message='Something went wrong. Contact the system administrator', status=-1,
                                      staff_node=None)


class StudentLogin(ClientIDMutation):
    message = String(required=True)
    status = Int(required=True)
    access_token = String(required=True)
    student_node = Field(StudentNode)

    class Input:
        reg_no = String(required=True)

    # noinspection PyUnresolvedReferences
    @classmethod
    def mutate_and_get_payload(cls, _, __, **args):
        try:
            # check that correct format of student reg. num is followed
            message, status, reg_no = get_non_blank_input(capitalise(args.get('reg_no').strip()), "Registration number")
            if status:
                return StudentLogin(message=message, status=status, access_token='', student_node=None)

            if not re.search(r"\w\d\d/[\d]+/\d\d\d\d", reg_no):
                return StudentLogin(message='Invalid registration number', status=1, access_token='', student_node=None)

            # check if student is already registered
            student = Student.query.filter_by(reg_num=reg_no).first()
            if not student:
                return StudentLogin(message='Registration number not registered', status=2,
                                    access_token='', student_node=None)

            if not student.email_confirmed:
                return StudentLogin(message="Please check your email to activate your account", status=3,
                                    access_token='', student_node=None)

            return StudentLogin(message='Success! Welcome', status=0, student_node=student,
                                access_token=User.encode_auth_token(student.user))

        except BaseException as err:
            print(err)
            system_logging(err, exception=True)
            return StudentLogin(message='Something went wrong. Please contact the system administrator', status=-1,
                                access_token='', student_node=None)


class StaffLogout(ClientIDMutation):
    message = String(required=True)
    status = Int(required=True)

    class Input:
        staff_id = String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, _, info, __):
        auth_resp = User.decode_auth_token(info.context)
        print("Response: {}".format(auth_resp))
        return StaffLogout(message='', status=0)


class StaffLogin(ClientIDMutation):
    message = String(required=True)
    status = Int(required=True)
    access_token = String(required=True)
    refresh_token = String(required=True)
    staff_node = Field(LecturerNode)

    class Input:
        staff_id = String(required=True)
        password = String(required=True)

    # noinspection PyUnresolvedReferences
    @classmethod
    def mutate_and_get_payload(cls, _, __, **args):
        try:
            message, status, staff_id = get_non_blank_input(args.get('staff_id').strip(), "Staff ID number")
            if status:
                return StaffLogin(access_token='', message=message, status=status, refresh_token='', staff_node=None)
            staff = Lecturer.query.filter_by(staff_id=staff_id).first()
            # check if password of required length
            password = args.get('password', "")
            if len(password) < 6 or len(password) > 14:
                return StaffLogin(access_token='', message='Password should be between 6 to 14 characters', status=1,
                                  staff_node=None, refresh_token='')
            # confirm staff trying to log in is the correct one
            if staff is None or not staff.verify_password(password):
                system_logging("Invalid Credentials", exception=True)
                return StaffLogin(access_token='', message="Invalid Credentials", status=2, refresh_token='',
                                  staff_node=None)
            return StaffLogin(access_token=create_access_token(identity=staff_id), message="Successful login", status=0,
                              refresh_token=create_refresh_token(identity=staff_id), staff_node=staff)
        except BaseException as err:
            print(err)
            system_logging(err, exception=True)
            return StaffLogin(access_token='', refresh_token='', staff_node=None, message="Login error", status=-1)


class FileUpload(ClientIDMutation):
    class Input:
        file = Upload(required=True)

    success = graphene.Boolean()
    download_link = String()

    @classmethod
    def mutate_and_get_payload(cls, _, __, **args):
        # do something with your file
        from werkzeug.utils import secure_filename
        f = args.get('file', None)
        download_link = ''
        try:
            if not os.path.isdir(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            from flask import url_for
            download_link = url_for('static', filename="uploads/{}".format(f.filename), _external=True)
        except BaseException as err:
            print(err)

        return FileUpload(success=True, download_link=download_link)


# map mutations
class NewStudentMutation(graphene.ObjectType):
    new_student = NewStudent.Field(description="This is where a new student is added to the system.")


class NewStaffMutation(graphene.ObjectType):
    new_staff = NewStaff.Field(description="This is where a new staff member is added to the system.")


class StudentLoginMutation(graphene.ObjectType):
    student_login = StudentLogin.Field(
        description="Here, a student can login to the system. Upon successful login, an access token shall be issued."
                    "This token is necessary for further operations within the system"
    )


class ResetStaffPasswordMutation(graphene.ObjectType):
    reset_staff_password = ResetStaffPassword.Field(
        description="In case staff forgets their password, one can call this mutation to request resetting password."
                    "One shall thus receive an email to reset password if request is approved."
    )


class StaffLoginMutation(graphene.ObjectType):
    staff_login = StaffLogin.Field(
        description="Here, staff can login to the system. Upon successful login, an access token shall be issued."
                    "This token is necessary for further operations within the system"
    )


class StaffLogoutMutation(graphene.ObjectType):
    staff_logout = StaffLogout.Field(
        description="Here, a staff member can logout from the system. The previously provided token shall be revoked."
    )


class FileUploadMutation(graphene.ObjectType):
    file_upload = FileUpload.Field()


# all queries will be base classes for the root query
class RootQuery(DepartmentQuery, LecturerQuery, UserQuery, StudentQuery, ImageNumberQuery, graphene.ObjectType):
    pass


# all mutations will be base classes for the root mutation
class RootMutation(NewStudentMutation, NewStaffMutation, StudentLoginMutation, FileUploadMutation,
                   ResetStaffPasswordMutation, StaffLoginMutation, StaffLogoutMutation, graphene.ObjectType):
    pass


# noinspection PyTypeChecker
schema = graphene.Schema(query=RootQuery, mutation=RootMutation)
