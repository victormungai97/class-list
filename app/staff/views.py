# app/staff/views.py

import os
from flask import flash, redirect, render_template, url_for, session, abort, request
from flask_login import login_required, logout_user, current_user
from datetime import datetime

from app import app
from populate import staff_roles, courses, verification
from . import staff
from .forms import RegistrationForm, LoginForm, CourseForm, ClassForm, ResetPasswordRequestForm, ResetPasswordForm
from ..cache import cache
from ..database import db_session
from ..errors import system_logging
from ..models import Lecturer, Course, LecturersTeaching, Class, User, Attendance, Photo
from ..extras import return_403, make_pdf, get_courses, staff_send_confirmation_email
from ..email import send_password_reset_email
from ..security import ts


def check_class_activity():
    if 'active' in session:
        return session['active']
    else:
        return False


# noinspection PyUnresolvedReferences
@staff.route('/register/', methods=['GET', 'POST'])
def register():
    """
        Handle requests to the /register route
        Add a staff member to the database through the registration form
        """
    if 'lecturer_id' in session:
        flash("Logout out first")
        return redirect(url_for('staff.dashboard'))
    return_403('student_id')

    form = RegistrationForm()

    # if successful validation
    if form.validate_on_submit():
        try:
            name = " ".join([form.first_name.data, form.last_name.data])
            email = form.email.data
            # noinspection PyArgumentList
            lecturer = Lecturer(staff_id=form.staff_id.data,
                                name=name,
                                programme=courses.get(form.programme.data),
                                email=email,
                                rank=staff_roles.get(form.rank.data),
                                password=form.password.data,
                                user=len(User.query.all()) + 1,
                                is_lecturer=True,
                                email_confirmed=False,
                                )

            # add staff to database
            db_session.add(lecturer)
            db_session.commit()
            # Now we'll send the email confirmation link
            staff_send_confirmation_email(email, name)
            # send message of successful registration
            flash("Successful registration. Please check your email to activate your account.")
            # redirect to home page
            return redirect(url_for("home.index"))
        except BaseException as err:
            system_logging(err, exception=True)
            print(err)
            flash("Something went wrong. Please contact system administrator")

    # load registration template
    # noinspection PyUnresolvedReferences
    return render_template("staff/register.html", form=form, title='Register Staff')


# noinspection PyUnresolvedReferences,DuplicatedCode
@staff.route('/confirm/<token>/')
def confirm_email(token):
    try:
        # retrieve user's email from token. Maximum duration is 24 hours
        email = ts.loads(token, salt=app.config['EMAIL_CONFIRMATION_KEY'], max_age=86400)
        user = Lecturer.query.filter_by(email=email).first()

        user.email_confirmed = True

        # Update lecturer's record to show as activated
        db_session.add(user)
        db_session.commit()
        # send message of successful registration
        flash("Successful account activation. You can now login.")
        # redirect to login page
        return redirect(url_for("staff.login"))
    except BaseException as err:
        system_logging(err, exception=True)
        print(err)
        abort(404)


@staff.route('/login/', methods=['GET', 'POST'])
def login():
    """
        Handle requests to the /login route
        Log staff in through the login form
        """
    if 'lecturer_id' in session:
        return redirect(url_for('staff.dashboard'))
    return_403('student_id')

    form = LoginForm()
    if form.validate_on_submit():
        # save current session
        session['lecturer_id'] = form.lecturer.id
        # redirect to dashboard
        return redirect(url_for('staff.dashboard'))

    # load login template
    # noinspection PyUnresolvedReferences
    return render_template("staff/login.html", form=form, title="Staff Login")


@staff.route('/logout/')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log a staff member out through the logout link
    """
    return_403('student_id')
    if check_class_activity() and session['active']:
        flash("You cannot log out while a class is running")
        return redirect(url_for('staff.dashboard'))
    logout_user()
    if 'lecturer_id' in session:
        session.pop('lecturer_id')
    if 'start' in session:
        session.pop('start')

    # redirect to the home page
    return redirect(url_for('home.index'))


# noinspection PyUnresolvedReferences
@staff.route('/reset_password_request/', methods=['GET', 'POST'])
def reset_password_request():
    # if user already logged in, just redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('staff.dashboard'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Lecturer.query.filter_by(staff_id=form.staff_id.data).first()
        if user:
            send_password_reset_email(user)
        # To prevent figuring out IDs of registered users,
        # flash this message and redirect to login regardless of whether user is known or not
        flash('Check your email for instructions on resetting your password')
        return redirect(url_for('staff.login'))
    return render_template('staff/reset_password_request.html',
                           title='Request Password Request', form=form)


@staff.route('/reset_password/<token>/', methods=['GET', 'POST'])
def reset_password(token):
    # if user already logged in, just redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('staff.dashboard'))
    # Determine who the user is by invoking the token verification method in the Lecturer class
    # This method returns the user if the token is valid, or None if not
    user = Lecturer.verify_reset_password_token(token)
    # If the token is invalid, redirect to the home page
    if not user:
        flash('The token is invalid')
        return redirect(url_for('home.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db_session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('staff.login'))
    return render_template('staff/reset_password.html', form=form, title="Reset Password")


@staff.route('/')
@staff.route('/dashboard/')
@cache.cached()
@login_required
def dashboard():
    return_403('student_id')
    active = check_class_activity()
    # noinspection PyUnresolvedReferences
    return render_template("staff/dashboard.html", title="Staff Dashboard", home=True, active=active, is_lecturer=True,
                           pid=session['lecturer_id'])


# noinspection PyUnresolvedReferences
def autoincrement():
    """
    Function will autoincrement id in LecturersTeaching table
    by querying entire table
    and adding one to the len of returned list
    :return: New ID number
    """
    return len(LecturersTeaching.query.all()) + 1


# noinspection PyUnresolvedReferences
@staff.route('/register_course/<pid>/', methods=['GET', 'POST'])
@login_required
def register_course(pid):
    """
    This function will render the form for course registration
    and save the entered data into the database
    :param pid: ID of the lecturer
    :return: Dashboard if successful or template of registration form if otherwise
    """
    return_403('student_id')
    active = check_class_activity()
    form = CourseForm()
    form.course.choices = [(course.id, course.name) for course in Course.query.all()]
    form.staff_id = Lecturer.query.filter_by(id=pid).first().id

    if form.validate_on_submit():
        lecturer_course = LecturersTeaching(id=(len(LecturersTeaching.query.all()) + 1),
                                            lecturers_id=form.staff_id,
                                            courses_id=form.course.data,
                                            programme=form.programme.data
                                            )
        try:
            # save lecturer and course ID to LecturerTeaching table
            db_session.add(lecturer_course)
            db_session.commit()
            flash("Successful registration of course!")
            return redirect(url_for('staff.dashboard'))
        except Exception as err:
            print(err)
            db_session.rollback()
            flash("Error during registration")

    return render_template("staff/course.html", form=form, title="Course Registration", active=active,
                           is_lecturer=True, pid=session['lecturer_id'])


# noinspection PyUnresolvedReferences
@staff.route('/_get_courses/')
@login_required
def _get_courses():
    return get_courses()


# noinspection PyUnresolvedReferences
@staff.route('/start_class/', methods=['POST', 'GET'])
@login_required
def _start_class():
    """
    Function that enables a staff member to start a class
    from a list of courses (s)he has registered to
    :return: HTML template of the class form
    """
    return_403('student_id')
    if check_class_activity() and session['active']:
        flash("You cannot start a class while a class is running")
        return redirect(url_for('staff.dashboard'))
    # get lecturer's ID
    staff_id = Lecturer.query.filter_by(id=request.args.get("pid")).first().id
    form = ClassForm()
    form.courses.choices = [(0, "None")]
    # query courses that a given lecturer has registered to and add them to the drop down list
    for course in Course.query.filter(Course.id == LecturersTeaching.courses_id) \
            .filter(LecturersTeaching.lecturers_id == staff_id).all():
        form.courses.choices.append((course.id, course.name))
    form.courses.default = 0
    return render_template("staff/class.html", form=form, title="Start Class", id=staff_id, is_lecturer=True,
                           pid=session['lecturer_id'])


# noinspection PyUnresolvedReferences
@staff.route("/_show_clock/")
@login_required
def _show_clock():
    """
    Function that shows the current time using a representation of an analogue clock
    Here, we retrieve the IDs of a staff member and the course so as so to start the new class
    using the lecturers-courses relationship table ID.
    We save the start time and the title of the class to the session for use in later functions
    :return:
    """
    return_403('student_id')
    active = check_class_activity()
    staff_id = request.args.get("a")
    course = request.args.get("q")
    session['start'] = datetime.now()
    lec_course = LecturersTeaching.query.filter((LecturersTeaching.lecturers_id == staff_id) &
                                                (LecturersTeaching.courses_id == course)).first().id
    # create instance of class
    class_ = Class(time_started=session['start'],
                   duration=0.0,
                   archived=False,
                   lec_course_id=lec_course,
                   is_active=True
                   )
    # save class to db
    try:
        db_session.add(class_)
        db_session.commit()
    except Exception as err:
        print(err)
        db_session.rollback()
        flash("An error occurred")
        return render_template("staff/class.html", form=form, title="Start Class", id=staff_id, active=active,
                               is_lecturer=True, pid=session['lecturer_id'])

    # get id of latest started class and pass it to the end clock function
    class_id = Class.query.all()[len(Class.query.all()) - 1].id
    session['name'] = Course.query.filter(Course.id == course).first().name
    session['active'] = True
    session['id'] = class_id
    return render_template("staff/clock.html", class_=session['name'], active=active, title="Running Class",
                           is_lecturer=True, pid=session['lecturer_id'])


# noinspection PyUnresolvedReferences
@staff.route('/running_class/')
@login_required
def running_class():
    return_403('student_id')
    active = check_class_activity()
    return render_template('staff/clock.html', class_=session['name'], active=active, title="Running Class",
                           is_lecturer=True, pid=session['lecturer_id'])


# noinspection PyUnresolvedReferences
@staff.route("/end_class_/")
@login_required
def _end_class():
    """
    We end the latest class here by retrieving the latest running class from the Class table
    and update its duration - by subtracting its start time found the global session from the end time
    and update its running status
    :return: redirection to the staff dashboard if successful
    """
    return_403('student_id')
    if 'start' in session:
        # search for current class and update duration and active state
        class_ = Class.query.filter((Class.id == session['id'])).first()
        class_.duration = (datetime.now() - session['start']).total_seconds() / 3600
        class_.is_active = False
        if session['active']:
            session['active'] = False
        # save class to db
        try:
            db_session.commit()
        except Exception as err:
            print(err)
            db_session.rollback()
            flash("An error occurred")
            return render_template("staff/class.html", title="Start Class", is_lecturer=True,
                                   pid=session['lecturer_id'])

        return redirect(url_for('staff.dashboard'))
    else:
        active = check_class_activity()
        return render_template("staff/clock.html", active=active, title="Running Class", is_lecturer=True,
                               pid=session['lecturer_id'])


# noinspection PyUnresolvedReferences
@staff.route('/list_units/')
@login_required
def list_units():
    return_403('student_id')
    active = check_class_activity()
    rows, pid, html = [], Lecturer.query.filter_by(id=session['lecturer_id']).first().id, "lists/subjects.html"
    for course in Course.query.filter(
            (Course.id == LecturersTeaching.courses_id) &
            (
                    LecturersTeaching.lecturers_id == pid
            )
    ).all():
        rows.append(('FEE' + str(course.id), course.name))

    if request.args.get("download"):
        pid = Lecturer.query.filter_by(id=session['lecturer_id']).first().staff_id
        return make_pdf(pid, rows, "subjects.pdf", html, "Add Courses", title="Courses Registered")

    return render_template(html, title="Courses Registered", is_lecturer=True,
                           pid=session['lecturer_id'], to_download=False,
                           rows=rows, url="staff.register_course", empty=True, wrap="Add Courses", active=active)


# noinspection PyUnresolvedReferences
@login_required
def verify_persons():
    counter, rows = 1, []
    for attendance in Attendance.query.filter(Attendance.verified != 1).all():
        rows.append([counter,
                     attendance.student,
                     verification[attendance.verified]['error_message'],
                     attendance.uploaded_photo,
                     Photo.query.filter((Photo.student_id == attendance.student) & (Photo.learning == 1))
                    .all()[-1].address,
                     attendance.id])
        counter += 1
    return rows


# noinspection PyUnresolvedReferences
@staff.route('/verify/')
@login_required
def verify():
    """
    Function to display list of students whose face have not been verified
    :return: HTML template page
    """
    active, rows, html = check_class_activity(), [], 'lists/verify.html'

    rows = verify_persons()

    if request.args.get("download"):
        for row in rows:
            # set path of pictures to their absolute paths
            row[3] = os.path.abspath('app/static/' + row[3]).replace('\\', '/')
            row[4] = os.path.abspath('app/static/' + row[4]).replace('\\', '/')

        pid = Lecturer.query.filter_by(id=session['lecturer_id']).first().staff_id
        return make_pdf(pid, rows, "verify.pdf", html, "Verified Students", title="Verify Students")

    return render_template(html, title="Verify Students", is_lecturer=True,
                           pid=session['lecturer_id'], rows=rows, to_download=False,
                           url="staff.students", empty=True, wrap="Verified Students", active=active)


# noinspection PyUnresolvedReferences
@staff.route('/approve/<pid>/')
@login_required
def approve(pid):
    """
    Function to confirm student's appearance in class
    :param pid: row ID in Attendance table
    :return: HTML template table
    """
    attendance, active = Attendance.query.filter_by(id=pid).first(), check_class_activity()
    if attendance and attendance.verified != 1:
        attendance.verified = 1
        db_session.commit()

    return render_template('lists/verify.html', title="Verify Students", is_lecturer=True,
                           pid=session['lecturer_id'], rows=verify_persons(), to_download=False,
                           url="staff.students", empty=True, wrap="Verified Students", active=active)


@staff.route('/students/')
def students():
    abort(503)
