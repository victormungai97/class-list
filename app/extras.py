# app/extras.py

import os
import pdfkit
from datetime import datetime
from flask import session, abort, make_response, render_template

from app import upload_folder
from .database import db_session
from .models import Student, Photo, Attendance, VerificationStatus, User
from populate import verification


# noinspection PyArgumentList
def add_student(reg_num, name, year, programme, email, pic_url):
    """
    Function to add student and registration photos to db
    :param email: Email address of student
    :param reg_num: Registration number of student
    :param name: Name of student
    :param year: Year of study of student
    :param programme: Programme student is undertaking e.g. Architecture
    :param pic_url: List of images student has uploaded
    :return: Error status - if any - and the associated message
    """
    photos, message, status = [], '', 0

    student_ = Student(reg_num=reg_num,
                       name=name,
                       year_of_study=year,
                       programme=programme,
                       email=email,
                       class_rep=False,
                       user=len(User.query.all()) + 1,
                       is_student=True)
    for pic in pic_url:
        photos.append(Photo(student_id=reg_num,
                            address=pic,
                            learning=True)
                      )
    try:
        db_session.add(student_)
        for photo in photos:
            db_session.add(photo)
        db_session.commit()

        message = "Successful registration of {}".format(name)
    except Exception as err:
        status, message = 1, "Error during registration"
        print(err)
        db_session.rollback()

    return message, status


def atten_dance(reg_num, url, verified, class_, course):
    """
    Method to save attendance and verification of a student to a class
    :param course: Course student is attending
    :param class_: ID of chosen running class
    :param reg_num: Registration number of student
    :param url: URL of uploaded picture
    :param verified: Verification code/status of student's picture
    :return: Error status - if any - and the associated message
    """
    message, status = '', 0

    photo = Photo(student_id=reg_num,
                  address=url,
                  learning=False)
    verify = VerificationStatus(description=verification[verified]['description'],
                                error_message=verification[verified]['error_message'])
    attendance = Attendance(id=(len(Attendance.query.all()) + 1),
                            student=reg_num,
                            class_=class_,  # to be adjusted
                            verified=verified,
                            uploaded_photo=url,
                            course=course)
    try:
        db_session.add(photo)
        db_session.add(verify)
        db_session.add(attendance)
        db_session.commit()

        message = "Success"
    except Exception as err:
        message, status = "Something went wrong in attendance. Please try again", 1
        print(err)
        db_session.rollback()

    return message, status


def return_403(key):
    """
    Function to raise 403 Forbidden error if key in session dict
    Prevents access to unauthorised pages
    :param key: Key to be checked in session dict
    :return: Error if key in session
    """
    if key in session:
        abort(403)


def unique_files(directory, filename, basename, extension='pdf'):
    """
    check if file is in current directory. If so, rename it
    :param directory: Directory to save in
    :param filename: Name of file currently
    :param basename: Base name of file
    :param extension: Extension of file
    :return: New file name if current name exists
    """
    for root, dirs, files in os.walk(directory):
        for i in range(len(files)):
            files[i] = os.path.join(root, files[i])
        common_files = []
        if filename in files:
            for _file in files:
                if os.path.basename(_file).startswith(basename):
                    common_files.append(_file)
            if common_files:
                common_files.sort()
                filename = common_files[-1]
                start, end = tuple(filename.rsplit('_', 1))
                filename = "_".join([start, ".".join([str(int(end[0]) + 1), extension])])
    return filename


def make_pdf(pid, rows, outfile, html, wrap):
    """
    Function converts HTML template page to PDF and passes the PDF to user for download
    :param wrap: Message above table
    :param pid: Unique identifier of user
    :param rows: List of fields in table
    :param outfile: PDF to be downloaded
    :param html: HTML template page to convert
    :return: response to download PDF
    """
    # list of css files
    css = ['app/static/css/style.css', 'app/static/css/bootstrap.min.css', 'app/static/css/narrow-jumbotron.css']
    # specify wkhtmltopdf options
    options = {'quiet': ''}
    # generate pdf as variable in memory
    pdf = pdfkit.from_string(render_template(html,
                                             reg_no=pid,
                                             date=datetime.now().strftime("%d %B %Y %I:%M:%S %p"),
                                             wrap=wrap,
                                             rows=rows, download=True),
                             False, options=options, css=css
                             )
    # create custom response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'  # receive pdf file
    # try and download the file
    response.headers['Content-Disposition'] = 'attachment; filename= {}'.format(outfile)
    return response


def create_path(reg_num=""):
    """
    Function that creates the users' file directories using their registration numbers
    :param reg_num: Registration number of students
    :return: Path to the directories
    """
    # split reg_num to retrieve year, course and specific number of student
    details = reg_num.split("/")
    # create new path to folder for student's image(s)
    path = '/'.join([upload_folder, details[0], details[2], details[1], '/'])
    # create the new folder
    if not os.path.isdir(path):
        os.makedirs(path)
    return os.path.abspath(path)
