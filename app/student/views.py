# app/student/views.py

import re
import os
import pdfkit
from werkzeug.utils import secure_filename
from flask import render_template, request, flash, redirect, url_for, jsonify, session, make_response
from flask_login import login_required, logout_user

from ..database import db_session
from ..models import Student, Course, Programme, StudentCourses, Class, LecturersTeaching, Attendance
from ..student import student
from .forms import RegistrationForm, CourseForm, LoginForm, ClassForm, SignInForm
from ..extras import add_student, atten_dance, return_403

from pictures import allowed_file, determine_picture, decode_image
from populate import courses


# noinspection PyUnresolvedReferences
@student.route('/')
@student.route('/dashboard/')
@login_required
def home():
    """
    Function that directs to student homepage
    :return: HTML template to student homepage
    """
    return_403('lecturer_id')
    return render_template("student/home.html", title="Students Homepage", home=True, is_student=True,
                           pid=session['student_id'])


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


@student.route('/phone/', methods=['POST'])
def phone():
    """
    Function to register student from the mobile app
    :return: JSON Object containing error code and accompanying message
    """
    json, message, status, pic_url = request.get_json(force=True), '', 0, []
    name = json['name']
    reg_no = json['regno']

    # check that correct format of student reg. num is followed
    if not re.search("/[\S]+/", reg_no):
        return jsonify({'message': 'Invalid registration number', 'status': 4})

    # check if student is already registered
    if Student.query.filter_by(reg_num=reg_no).first():
        return jsonify({'message': 'Registration number already registered', 'status': 2})

    department = json['departments']
    year = json['year']
    images = json['images']

    for image in images:
        image = decode_image(image, name, reg_no)

        filename = secure_filename(image)
        if not allowed_file(filename):
            # noinspection PyUnusedLocal
            message, status = "File format not supported", 3
        else:
            url, verified = determine_picture(reg_no, image=image, filename=filename, phone=True)
            pic_url.append(url)

    message, status = add_student(reg_no, name, year, department, pic_url)

    return jsonify({'message': message, "status": status})


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
        if images:
            # if len(images) < 10: form.photo.errors.append("Please upload at least 10 images of yourself")
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
                    url, verified = determine_picture(reg_num, image, filename)
                    pic_url.append(url)

        # check if student already registered
        message, status = add_student(form.reg_num.data, name, form.year_of_study.data,
                                      courses.get(form.programme.data), pic_url)
        if not status:
            flash(message)
            return redirect(url_for('student.login'))
        else:
            form.reg_num.errors.append(message)
    return render_template("student/register.html", form=form, title="Student Registration")


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

    return render_template("student/course.html", form=form, title="Course Registration", is_student=True,
                           pid=session['student_id'])


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


@student.route('/_get_department/')
@login_required
def _get_departments():
    dept = request.args.get("text", type=str).split('/')[0]
    departments = [(programme.program_id, programme.name)
                   for programme in Programme.query.filter(Programme.program_id == dept).all()]
    return jsonify(departments)


@student.route('/_get_courses/')
@login_required
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


@student.route('/attend/<pid>/', methods=['POST', 'GET'])
@login_required
def web_(pid):
    """
    Function that enables a student to sign into a respective class
    :return:
    """
    return_403('lecturer_id')
    # retrieve student's reg number
    reg_num = Student.query.filter(Student.id == pid).first().reg_num
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
    return render_template("student/class.html", form=form, title="Start Class", is_student=True,
                           pid=session['student_id'])


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
    name = Course.query.filter(Course.id == course).first().name
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
            # if allowed, process image to get url and verification status of image
            url, verified = determine_picture(reg_num, image, filename, attendance=True)
            # add to db
            message, status = atten_dance(reg_num, url, verified, class_, name)

            if not status:
                flash(message)
                return redirect(url_for('student.home'))
            else:
                form.photo.errors.append(message)

        if not allowed_file(image.filename):
            # if not allowed, raise error
            form.photo.errors.append("Files should only be pictures")

    return render_template("student/attend.html", form=form, title="Attend Class", is_student=True,
                           pid=session['student_id'])


@student.route('/registered/')
@login_required
def registered_courses():
    """
    Function to list courses student is registered to
    :return: HTML template of registered courses
    """
    return_403('lecturer_id')
    rows = []
    for course in Course.query.filter(
                    (Course.id == StudentCourses.courses_id) &
                    (StudentCourses.student_id == Student.query.filter_by(id=session['student_id']).first().reg_num)
    ).all():
        rows.append(('FEE' + str(course.id), course.name))

    return render_template("lists/units.html", title="Courses Registered", is_student=True, pid=session['student_id'],
                           rows=rows, url="student.courses_", empty=True, wrap="Add Courses")


@student.route('/classes/')
@login_required
def classes():
    return_403('lecturer_id')
    rows, counter = [], 1
    for attendance in Attendance.query.filter(
                    Attendance.student == Student.query.filter_by(id=session['student_id']).first().reg_num).all():
        rows.append((counter, attendance.course, attendance.time_attended.strftime("%A %d, %B %Y"), attendance.uploaded_photo))
        counter += 1

    print(session['student_id'], rows)
    return render_template("lists/classes.html", title="Classes Attended", is_student=True, pid=session['student_id'],
                           rows=rows, url="student.download", empty=True, wrap="Download Attendance")


@student.route('/download/')
@login_required
def download():
    """
    Function converts HTML template page to pdf and passes the pdf to user for download
    :return: response to download pdf
    """
    return_403('lecturer_id')
    rows, reg_no, outfile, text, counter = [], "", "attendance.pdf", '', 1
    for attendance in Attendance.query.filter(
                    Attendance.student == Student.query.filter_by(id=session['student_id']).first().reg_num).all():
        reg_no = attendance.student
        rows.append([counter, attendance.course, attendance.time_attended.strftime("%A %d, %B %Y"), attendance.uploaded_photo])
        counter += 1

    for row in rows:
        # set path of picture to its absolute path
        if isinstance(row[3], str) and row[3].endswith('.jpg'):
            row[3] = os.path.abspath('app/static/' + row[3]).replace('\\', '/')

    # list of css files
    css = ['app/static/css/style.css', 'app/static/css/bootstrap.min.css', 'app/static/css/narrow-jumbotron.css']
    # specify wkhtmltopdf options
    options = {'quiet': ''}
    # generate pdf as variable in memory
    pdf = pdfkit.from_string(render_template("lists/classes.html",
                                             reg_no=reg_no,
                                             wrap="Download Attendance",
                                             rows=rows, download=True),
                             False, options=options, css=css
                             )
    # create custom response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'  # receive pdf file
    # try and download the file
    response.headers['Content-Disposition'] = 'attachment; filename= {}'.format(outfile)

    return response
