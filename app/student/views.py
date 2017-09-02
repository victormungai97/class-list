# app/student/views.py

import os
from flask import render_template, request, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

from .. import registration_folder
from ..database import db_session
from ..models import Student, Photo, Course, Programme, StudentCourses
from ..student import student
from .forms import RegistrationForm, CourseForm

from pictures import allowed_file, register_get_url, compress_image
from populate import courses


# noinspection PyUnresolvedReferences
@student.route('/')
def home():
    """
    Function that directs to student homepage
    :return:
    """
    return render_template("student/home.html", title="Students Homepage", home=True, is_student=True)


# noinspection PyUnresolvedReferences,PyArgumentList
@student.route('/register/', methods=["GET", 'POST'])
def web():
    """
    Function to render form to student on the website
    and subsequently register student
    :return:
    """
    form = RegistrationForm()

    if form.validate_on_submit():
        reg_num = form.reg_num.data
        name = form.first_name.data + " " + form.last_name.data
        images = request.files.getlist("photo")
        counter = 1
        pic_url = []
        photos = []
        if images:
            # if len(images) < 10: form.photo.errors.append("Please upload at least 10 images of yourself")
            for image in images:
                # check if allowed
                if not allowed_file(image.filename):
                    # if not allowed, raise error
                    form.photo.errors.append("Files should only be pictures")
                    return render_template("student/register.html", form=form, title="Student Registration")
                else:
                    # split reg_num to retrieve year, course and specific number of student
                    details = reg_num.split("/")
                    # create new path to folder for student's image(s)
                    path = '/'.join([registration_folder, details[0], details[2], details[1], '/'])
                    # create the new folder
                    if not os.path.isdir(path):
                        os.makedirs(path)
                    # get name of the source file + Make the filename safe, remove unsupported chars
                    filename = str(secure_filename(image.filename))
                    image.save(os.path.join(path, filename))
                    # compress image
                    compress_image(os.path.join(path, image.filename))
                    pic_url.append(register_get_url(filename, path, counter, regno=details[1], list_of_images=images))
                counter += 1

        # check if student already registered
        if not Student.query.filter(Student.reg_num == form.reg_num.data).first():
            # if student not registered, them register
            student_ = Student(reg_num=reg_num,
                               name=name,
                               year_of_study=form.year_of_study.data,
                               programme=courses.get(form.programme.data),
                               class_rep=False,
                               is_student=True)
            for pic in pic_url:
                photos.append(Photo(student_id=form.reg_num.data,
                                    address=pic,
                                    learning=True)
                              )
            try:
                db_session.add(student_)
                for photo in photos:
                    db_session.add(photo)
                db_session.commit()
            except Exception as err:
                print(err)
                db_session.rollback()
                return render_template("student/register.html", form=form, title="Student Registration")

        else:
            form.reg_num.errors.append("Registration number already registered")
            return render_template("student/register.html", form=form, title="Student Registration")

        flash("Successful registration of {}".format(name))
        return redirect(url_for("student.home"))

    return render_template("student/register.html", form=form, title="Student Registration")


def autoincrement():
    """
    Function will autoincrement id in StudentCourses table
    by querying entire table
    and adding one to the len of returned list
    :return: New ID number
    """
    return len(StudentCourses.query.all()) + 1


# noinspection PyUnresolvedReferences
@student.route('/courses/', methods=['POST', 'GET'])
def courses_():
    form = CourseForm()

    if form.validate_on_submit():
        student_course = StudentCourses(id=autoincrement(),
                                        student_id=form.reg_num.data,
                                        courses_id=form.course.data,
                                        programme=form.programme.data
                                        )
        try:
            # save lecturer and course ID to LecturerTeaching table
            db_session.add(student_course)
            db_session.commit()
            flash("Success")
            return redirect(url_for('student.home'))
        except Exception as err:
            print(err)
            db_session.rollback()
            flash("Error during registration")

    return render_template("student/course.html", form=form, title="Course Registration", is_student=True)


@student.route('/_get_department/')
def _get_departments():
    dept = request.args.get("text", type=str).split('/')[0]
    departments = [(programme.program_id, programme.name)
                   for programme in Programme.query.filter(Programme.program_id == dept)
                       .all()]
    return jsonify(departments)


@student.route('/_get_courses/')
def _get_courses():
    """
    This view will respond to XHR requests for courses
    :return: JSON list of courses
    """
    department = request.args.get("department", type=str)
    year = request.args.get("year", type=int)
    sem = request.args.get("sem", type=int)
    course = [(course.id, course.name)
              for course in Course.query.filter((Course.programme_id == department) &
                                                (Course.id.like("{}%".format(year))) &
                                                (Course.id.like("%{}".format(sem)))
                                                ).all()]
    return jsonify(course)


@student.route('/sign_in/', methods=['POST', 'GET'])
def web_():
    """
    Function that enables a student to sign into a respective class
    :return:
    """
    return "Hello"
