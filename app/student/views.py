# app/student/views.py

import re
import os
from werkzeug.utils import secure_filename
from flask import render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, logout_user
from zipfile import ZipFile, is_zipfile
from shutil import move, rmtree

from .. import home_folder
from ..database import db_session
from ..models import Student, Course, Programme, StudentCourses, Class, LecturersTeaching, Attendance
from ..student import student
from .forms import RegistrationForm, CourseForm, LoginForm, ClassForm, SignInForm
from ..extras import add_student, atten_dance, return_403, make_pdf, create_path

from pictures import allowed_file, determine_picture  # , decode_image
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
    Zipping functionality is courtesy of http://www.geeksforgeeks.org/working-zip-files-python/
    :return: JSON Object containing error code and accompanying message
    """
    json, message, status, pic_url, filename, unzip, files = request.form, '', 0, [], None, False, []
    name = json['name']
    reg_no = json['regno']
    email = json['email']

    # check that correct format of student reg. num is followed
    if not re.search("/[\S]+/", reg_no):
        return jsonify({'message': 'Invalid registration number', 'status': 4})

    # check if student is already registered
    if Student.query.filter_by(reg_num=reg_no).first():
        return jsonify({'message': 'Registration number already registered', 'status': 2})

    if Student.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered', 'status': 5})

    department = json['departments']
    year = json['year']
    # receive and save zip file
    zip_file = request.files['FILE']
    if zip_file:
        filename = secure_filename(zip_file.filename)
        zip_file.save(os.path.join(create_path(reg_no), filename))
    path = create_path(reg_no) + "/" + os.path.basename(filename).replace(".zip", "")

    # confirm that file is a zip file
    if is_zipfile(zip_file):
        # open the zip file in READ mode
        with ZipFile(os.path.join(create_path(reg_no), filename), 'r') as zip_file:
            # print all the contents of the zip file in table format
            zip_file.printdir()

            # extract all the files in zip file
            print('Extracting all the files now...')
            zip_file.extractall(path=path)
            # remember unzipping has happened
            unzip = True

            # delete redundant zip file
            print('Deleting file {}...'.format(filename))
            filename = os.path.join(create_path(reg_no), filename)
            os.remove(filename)
            print('Done!')

    # if successful unzipping
    if unzip:
        # read the files in the resultant directory
        files = os.listdir(path)
        # change working directory in resultant directory
        os.chdir(path)
        for image in files:
            # move files into the parent directory
            filename = secure_filename(image)
            move(filename, os.path.join(os.pardir, filename))

    # move to parent directory
    os.chdir(os.pardir)
    # delete resultant directory
    rmtree(path)
    # process the files
    for image in files:
        if os.path.isfile(os.path.join(os.curdir, image)):
            filename = secure_filename(image)
            if not allowed_file(filename):
                # noinspection PyUnusedLocal
                message, status = "File format not supported", 3
                break
            else:
                url, verified = determine_picture(reg_no, name.replace(" ", "_"), image, filename, phone=True)
                pic_url.append(url)

    # return to original location
    os.chdir(home_folder)
    print(u"Current path is", os.path.abspath(os.curdir), sep=' ')

    message, status = add_student(reg_no, name, year, department, email, pic_url)

    # print(reg_no, name, department, year, email, sep='\n')

    return jsonify({'message': message, "status": 1})


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
                    url, verified = determine_picture(reg_num, name.replace(" ", "_"), image, filename)
                    pic_url.append(url)

        # check if student already registered
        message, status = add_student(form.reg_num.data, name, form.year_of_study.data,
                                      courses.get(form.programme.data), form.email.data, pic_url)
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

    return render_template("student/attend.html", form=form, title="Attend Class", is_student=True,
                           pid=session['student_id'])


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
        return make_pdf(reg_no, rows, "courses.pdf", html, "Add Courses")

    return render_template(html, title="Courses Registered", is_student=True, pid=session['student_id'],
                           rows=rows, url="student.courses_", empty=True, wrap="Add Courses", to_download=False)


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

        return make_pdf(reg_no, rows, outfile, html, wrap)

    return render_template(html, title="Classes Attended", is_student=True, pid=session['student_id'],
                           rows=rows, url="student.classes", empty=True, wrap=wrap, to_download=True)
