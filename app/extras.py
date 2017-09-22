# app/extras.py

from flask import session, abort
from .database import db_session
from .models import Student, Photo, Attendance, VerificationStatus, User
from populate import verification


# noinspection PyArgumentList
def add_student(reg_num, name, year, programme, pic_url):
    """
    Function to add student and registration photos to db
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


def atten_dance(reg_num, url, verified, class_):
    """
    Method to save attendance and verification of a student to a class
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
                            uploaded_photo=url)
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
