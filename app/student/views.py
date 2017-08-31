# app/student/views.py

import os
from flask import render_template, request, flash, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename

from .. import registration_folder
from ..database import db_session
from ..models import Student, Photo, Course
from ..student import student
from .forms import RegistrationForm, CourseForm, LoginForm

from pictures import allowed_file, register_get_url, compress_image
from populate import courses


# noinspection PyUnresolvedReferences
@student.route('/')
def home():
    """
    Function that directs to student homepage
    :return:
    """
    return render_template("student/home.html", title="Students Homepage", home=True)


@student.route("/login/", methods=["POST", 'GET'])
def login():
    """
    Handle requests to the /login route
    Log staff in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():
        # save current session
        session['student'] = form.student_.id
        # redirect to dashboard
        return redirect(url_for('student.home'))

    # load login template
    # noinspection PyUnresolvedReferences
    return render_template("student/login.html", form=form, title="Student Login")


# noinspection PyUnresolvedReferences
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
                               class_rep=False)
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
        return redirect(url_for("staff.login"))

    return render_template("student/register.html", form=form, title="Student Registration")


# noinspection PyUnresolvedReferences
@student.route('/courses/', methods=['POST', 'GET'])
def courses():
    form = CourseForm()

    return render_template("student/course.html", form=form, title="Course Registration")


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
