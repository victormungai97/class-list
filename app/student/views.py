# app/student/views.py

import re
import os
from werkzeug.utils import secure_filename
from flask import render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, logout_user

from .. import app, numOfImages
from ..cache import cache
from ..database import db_session
from ..errors import system_logging
from ..models import Student, Course, Programme, StudentCourses, Class, LecturersTeaching, Attendance
from ..student import student
from .forms import RegistrationForm, CourseForm, LoginForm, ClassForm, SignInForm
from ..extras import add_student, atten_dance, return_403, make_pdf, zipfile_handling, get_courses
from ..security import ts

from pictures import allowed_file, determine_picture  # , decode_image
from populate import courses, key_from_value


# noinspection PyUnresolvedReferences
@student.route('/')
@student.route('/dashboard/')
@cache.cached()
@login_required
def home():
    """
    Function that directs to student homepage
    :return: HTML template to student homepage
    """
    return_403('lecturer_id')
    return render_template("student/home.html", title="Students Homepage", home=True, is_student=True, )


@student.route("/login/", methods=["POST", 'GET'])
def login():
    """
    Handle requests to the /login route
    Log student in through the login form
    """
    if 'student_id' in session:
        return redirect(url_for('student.home'))
    return_403('lecturer_id')

    form = LoginForm()
    if form.validate_on_submit():
        # save current session
        session['student_id'] = form.student_.id
        # redirect to dashboard
        return redirect(url_for('student.home'))

    # load login template
    # noinspection PyUnresolvedReferences
    return render_template("student/login.html", form=form, title="Student Login")


@student.route('/logout/', methods=["POST", "GET"])
@login_required
def logout():
    """
    Handle logging out requests
    :return: redirection to home page
    """
    return_403('lecturer_id')
    logout_user()
    if 'student_id' in session:
        session.pop("student_id")

    # redirect to the home page
    return redirect(url_for('home.index'))


# noinspection PyUnresolvedReferences
@student.route('/phone/', methods=['POST'])
def phone():
    """
    Function to register student from the mobile app
    Zipping functionality is courtesy of http://www.geeksforgeeks.org/working-zip-files-python/
    :return: JSON Object containing error code and accompanying message
    """
    json, message, status, pic_url, filename, unzip, files = request.form, '', 0, [], None, False, []
    name = json['name']
    reg_no = json['regno']
    email = json['email']
    department = json['department']
    try:
        year = int(json['year'])
    except ValueError as err:
        print(err)
        system_logging(err, exception=True)
        return jsonify({'message': 'Year should be a number', 'status': -1})

    # check that correct format of student reg. num is followed
    if not re.search(r"\w\d\d/[\d]+/\d\d\d\d", reg_no):
        return jsonify({'message': 'Invalid registration number', 'status': 4})

    # check if student is already registered
    if Student.query.filter_by(reg_num=reg_no).first():
        return jsonify({'message': 'Registration number already registered', 'status': 2})

    if Student.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered', 'status': 5})

    # confirm that registration number given matches the department selected
    if reg_no.split('/')[0] not in key_from_value(department, courses):
        return jsonify({'message': 'Registration number does not belong to this programme', 'status': 6})

    # check if programme is registered
    program = Programme.query.filter(Programme.name == department).first()
    # if not registered, raise error
    if not program:
        return jsonify({'message': 'Programme not registered', 'status': 7})

    # check if year selected is within years allocated to department
    if year > Programme.query.filter_by(name=department).first().year:
        return jsonify({'message': "Year selected is beyond department's range", 'status': 8})

    # receive and save zip file
    message, status, pic_url = zipfile_handling(zip_file=request.files['FILE'], reg_no=reg_no, name=name)

    if not status:
        message, status, args = add_student(reg_no, name, year, department, email, pic_url)

    # print(reg_no, name, department, year, email, sep='\n')

    return jsonify({'message': message, "status": status})


# noinspection PyUnresolvedReferences
@student.route('/login2/', methods=['POST'])
def login2():
    """
    Function enables student to login to the system from the android app
    :return: JSON Object containing name of student or error and accompanying message
    """
    json, message, status = request.get_json(force=True), '', 0
    reg_no = json['regno']

    student_ = Student.query.filter_by(reg_num=reg_no).first()
    if not student_:
        message, status = "Unknown Registration Number", 1
    else:
        message = student_.name

    return jsonify({'message': message, "status": status})


# noinspection PyUnresolvedReferences,PyArgumentList
@student.route('/register/', methods=["GET", 'POST'])
def web():
    """
    Function to render form to student on the website
    and subsequently register student
    :return: Student login page if successful, else registration page
    """
    form, message, status = RegistrationForm(), '', 0

    if 'student_id' in session:
        flash("Logout out first")
        return redirect(url_for('student.home'))

    return_403('lecturer_id')

    if form.validate_on_submit():
        reg_num, name = form.reg_num.data, form.first_name.data + " " + form.last_name.data
        images, pic_url = request.files.getlist("photo"), []
        # process images
        if images:
            if len(images) != numOfImages:
                form.photo.errors.append("Please upload {} images of yourself".format(numOfImages))
                return render_template("student/register.html", form=form, title="Student Registration")
            else:
                for image in images:
                    # get name of the source file + Make the filename safe, remove unsupported chars
                    filename = str(secure_filename(image.filename))
                    # check if allowed
                    if not allowed_file(image.filename):
                        # if not allowed, raise error
                        form.photo.errors.append("Files should only be pictures")
                        return render_template("student/register.html", form=form, title="Student Registration",
                                               is_student=True)
                    else:
                        url, verified = determine_picture(reg_num, name.replace(" ", "_"), image, filename)
                        pic_url.append(url)

        # process saving student
        message, status, args = add_student(form.reg_num.data, name, form.year_of_study.data,
                                            courses.get(form.programme.data), form.email.data, pic_url)
        if not status:
            flash(message)
            return redirect(url_for('student.login'))
        else:
            form.reg_num.errors.append(message)
    return render_template("student/register.html", form=form, title="Student Registration")


# noinspection PyUnresolvedReferences,DuplicatedCode
@student.route('/confirm/<token>/')
def confirm_email(token):
    try:
        # retrieve user's email from token. Maximum duration is 24 hours
        email = ts.loads(token, salt=app.config['EMAIL_CONFIRMATION_KEY'], max_age=86400)
        user = Student.query.filter_by(email=email).first()

        user.email_confirmed = True

        # Update student's record to show as activated
        db_session.add(user)
        db_session.commit()
        # send message of successful registration
        flash("Successful account activation. You can now login.")
        # redirect to login page
        return redirect(url_for("student.login"))
    except BaseException as err:
        system_logging(err, exception=True)
        print(err)
        abort(404)


# noinspection PyUnresolvedReferences
@student.route('/courses/', methods=['POST', 'GET'])
@login_required
def courses_():
    """
    Render form to register a student to a course, then save the IDs of the student and course to StudentCourses table
    :return: redirection to student homepage if successful, else html for course form
    """
    return_403('lecturer_id')
    form = CourseForm()
    form.programme.choices = [(programme.program_id, programme.name) for programme in Programme.query.all()]
    form.course.choices = [(course.id, course.name) for course in Course.query.all()]
    form.reg_num.data = Student.query.filter_by(id=session['student_id']).first().reg_num

    if form.validate_on_submit():
        try:
            # save student and course ID to StudentCourses table
            for unit in form.course.data:
                db_session.add(StudentCourses(id=(len(StudentCourses.query.all()) + 1),
                                              student_id=form.reg_num.data,
                                              courses_id=unit,
                                              programme=form.programme.data
                                              )
                               )
            db_session.commit()
            flash("Success")
            return redirect(url_for('student.home'))
        except Exception as err:
            print(err)
            db_session.rollback()
            flash("Error during registration")

    return render_template("student/course.html", form=form, title="Course Registration", is_student=True, )


# noinspection PyUnresolvedReferences
@student.route('/get_departments/')
def get_departments():
    """
    Function to send department names to the phone during registration
    :return: JSON Object containing array of department names
    """
    dept = request.args.get("text", type=str).split('/')[0]
    departments = {"departments": [programme.name
                                   for programme in Programme.query.filter(Programme.program_id == dept).all()]}
    print(departments)
    return jsonify(departments)


# noinspection PyUnresolvedReferences
@student.route('/_get_department/')
@login_required
def _get_departments():
    dept = request.args.get("text", type=str).split('/')[0]
    departments = [(programme.program_id, programme.name)
                   for programme in Programme.query.filter(Programme.program_id == dept).all()]
    return jsonify(departments)


# noinspection PyUnresolvedReferences
@student.route('/_get_courses/')
@login_required
def _get_courses():
    return get_courses()


# noinspection PyUnresolvedReferences
@student.route('/attend/', methods=['POST', 'GET'])
@login_required
def web_():
    """
    Function that enables a student to sign into a respective class
    :return:
    """
    return_403('lecturer_id')
    # retrieve student's reg number
    reg_num = Student.query.filter(Student.id == session['student_id']).first().reg_num
    # query courses student is registered to
    _courses = []
    for course in Course.query.filter(Course.id == StudentCourses.courses_id).filter(
            StudentCourses.student_id == reg_num).all():
        # query running classes among registered courses
        for crs in Course.query.filter(Course.id == course.id).filter(LecturersTeaching.courses_id == Course.id).filter(
                Class.lec_course_id == LecturersTeaching.id).filter(Class.is_active):
            _courses.append((crs.id, crs.name))
    # attach running class to form
    form = ClassForm()
    form.courses.choices = [(0, "None")]
    form.courses.choices.extend(_courses)
    return render_template("student/class.html", form=form, title="Attend Class", is_student=True, )


# noinspection PyUnresolvedReferences
@student.route('/sign_in/', methods=['POST', 'GET'])
@login_required
def attend_class():
    """
    Function to render form for class attendance
    :return: redirection to student homepage, else attendance template
    """
    return_403('lecturer_id')
    form, message, status = SignInForm(), '', 0
    reg_num, url, verified = Student.query.filter_by(id=session['student_id']).first().reg_num, "", 0
    # get chosen running class
    course = request.args.get("course")
    course_title = Course.query.filter(Course.id == course).first().name  # course title
    class_ = Class.query.filter(Class.is_active).filter(LecturersTeaching.courses_id == course) \
        .filter(Class.lec_course_id == LecturersTeaching.id).first().id

    # check if student has already signed into a class
    if Attendance.query.filter((Attendance.student == reg_num) & (Attendance.class_ == class_)).first():
        flash("Class already attended")
        return redirect(url_for('student.web_', pid=session['student_id']))

    if form.validate_on_submit():
        image = request.files['photo']
        # check if allowed
        if allowed_file(image.filename):
            # get name of the source file + Make the filename safe, remove unsupported chars
            filename = str(secure_filename(image.filename))
            # get name of student
            student_name = Student.query.filter_by(reg_num=reg_num).first().name
            # if allowed, process image to get url and verification status of image
            url, verified = determine_picture(reg_num, student_name.replace(" ", "_"), image, filename,
                                              attendance=True)
            # add to db
            message, status = atten_dance(reg_num, url, verified, class_, course_title)

            if not status:
                flash(message)
                return redirect(url_for('student.home'))
            else:
                form.photo.errors.append(message)

        if not allowed_file(image.filename):
            # if not allowed, raise error
            form.photo.errors.append("Files should only be pictures")

    return render_template("student/attend.html", form=form, title="Attend Class", is_student=True, )


# noinspection PyUnresolvedReferences
@student.route('/registered/')
@login_required
def registered_courses():
    """
    Function to list courses student is registered to
    One can also download a PDF document of this list
    :return: HTML template of registered courses or PDF conversion of the HTML page
    """
    return_403('lecturer_id')
    rows, reg_no, html = [], Student.query.filter_by(id=session['student_id']).first().reg_num, "lists/units.html"
    for course in Course.query.filter(
            (Course.id == StudentCourses.courses_id) &
            (StudentCourses.student_id == reg_no)
    ).all():
        rows.append(('FEE' + str(course.id), course.name))

    if request.args.get("download"):
        return make_pdf(reg_no, rows, "courses.pdf", html, "Add Courses", title="Courses Registered")

    return render_template(html, title="Courses Registered", is_student=True,
                           rows=rows, url="student.courses_", empty=True, wrap="Add Courses", to_download=False)


# noinspection PyUnresolvedReferences
@student.route('/classes/')
@login_required
def classes():
    """
    Function that shows the classes a student has attended
    One can also download a PDF document of this list
    :return: HTML template of attended classes or PDF conversion of the HTML page
    """
    return_403('lecturer_id')
    rows, counter, reg_no = [], 1, Student.query.filter_by(id=session['student_id']).first().reg_num
    outfile, html, wrap = "attendance.pdf", "lists/classes.html", "Download Attendance"
    for attendance in Attendance.query.filter(
            (Attendance.student == reg_no) & (Attendance.verified == 1)).all():
        rows.append([counter, attendance.course, attendance.time_attended.strftime("%A %d, %B %Y"),
                     attendance.uploaded_photo])
        counter += 1

    if request.args.get("download"):
        for row in rows:
            # set path of picture to its absolute path
            if isinstance(row[3], str) and row[3].endswith('.jpg'):
                row[3] = os.path.abspath('app/static/' + row[3]).replace('\\', '/')

        return make_pdf(reg_no, rows, outfile, html, wrap, title="Courses Registered")

    return render_template(html, title="Classes Attended", is_student=True,
                           rows=rows, url="student.classes", empty=True, wrap=wrap, to_download=True)
