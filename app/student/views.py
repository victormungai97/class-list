# app/student/views.py

from flask import render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, logout_user

from .. import registration_folder, upload_folder
from ..database import db_session
from ..models import Student, Course, Programme, StudentCourses, Class, LecturersTeaching
from ..student import student
from .forms import RegistrationForm, CourseForm, LoginForm, ClassForm, SignInForm
from ..extras import add_student, atten_dance

from pictures import allowed_file, determine_picture
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
    return render_template("student/home.html", title="Students Homepage", home=True, is_student=True,
                           pid=session['student_id'])


@student.route("/login/", methods=["POST", 'GET'])
def login():
    """
    Handle requests to the /login route
    Log student in through the login form
    """
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
    logout_user()
    if 'student_id' in session:
        session.pop("student_id")

    # redirect to the home page
    return redirect(url_for('home.index'))


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

    if form.validate_on_submit():
        reg_num, name = form.reg_num.data, form.first_name.data + " " + form.last_name.data
        images, counter, pic_url = request.files.getlist("photo"), 1, []
        if images:
            # if len(images) < 10: form.photo.errors.append("Please upload at least 10 images of yourself")
            for image in images:
                # check if allowed
                if not allowed_file(image.filename):
                    # if not allowed, raise error
                    form.photo.errors.append("Files should only be pictures")
                    return render_template("student/register.html", form=form, title="Student Registration",
                                           is_student=True)
                else:
                    pic_url.append(determine_picture(reg_num, folder=registration_folder,
                                                     list_of_images=images, image=image, counter=counter)
                                   )
                counter += 1

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
    form = CourseForm()
    form.reg_num.data = Student.query.filter_by(id=session['student_id']).first().reg_num

    if form.validate_on_submit():
        student_course = StudentCourses(id=(len(StudentCourses.query.all()) + 1),
                                        student_id=form.reg_num.data,
                                        courses_id=form.course.data,
                                        programme=form.programme.data
                                        )
        try:
            # save student and course ID to LecturerTeaching table
            db_session.add(student_course)
            db_session.commit()
            flash("Success")
            return redirect(url_for('student.home'))
        except Exception as err:
            print(err)
            db_session.rollback()
            flash("Error during registration")

    return render_template("student/course.html", form=form, title="Course Registration", is_student=True,
                           pid=session['student_id'])


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
    print(_courses)
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
    form, message, status = SignInForm(), '', 0
    reg_num, url, verified = Student.query.filter_by(id=session['student_id']).first().reg_num, "", 0
    # get chosen running class
    course = request.args.get("course")
    class_ = Class.query.filter(Class.is_active).filter(LecturersTeaching.courses_id == course) \
        .filter(Class.lec_course_id == LecturersTeaching.id).first().id

    if form.validate_on_submit():
        print(reg_num)
        image = request.files['photo']
        # check if allowed
        if allowed_file(image.filename):
            # if allowed, process image to get url and verification status of image
            url, verified = determine_picture(reg_num, image, upload_folder)
            # add to db
            message, status = atten_dance(reg_num, url, verified, class_)

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


@student.route('/classes/')
@login_required
def classes():
    pass
