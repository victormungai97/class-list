# app/staff/views.py

from flask import flash, redirect, render_template, url_for, session, request, jsonify
from flask_login import login_required, logout_user
from datetime import datetime

from populate import staff_roles, courses
from . import staff
from .forms import RegistrationForm, LoginForm, CourseForm, ClassForm
from ..database import db_session
from ..models import Lecturer, Course, LecturersTeaching, Class, User


@staff.route('/register/', methods=['GET', 'POST'])
def register():
    """
        Handle requests to the /register route
        Add a staff member to the database through the registration form
        """
    form = RegistrationForm()

    # if successful validation
    if form.validate_on_submit():
        # noinspection PyArgumentList
        lecturer = Lecturer(staff_id=form.staff_id.data,
                            name=" ".join([form.first_name.data, form.last_name.data]),
                            programme=courses.get(form.programme.data),
                            email=form.email.data,
                            rank=staff_roles.get(form.rank.data),
                            password=form.password.data,
                            user=len(User.query.all()) + 1,
                            is_lecturer=True
                            )

        # add staff to database
        db_session.add(lecturer)
        db_session.commit()
        # send message of successful registration
        flash("Successful registration of {}. You can now login".format(lecturer.name))
        # redirect to login page
        return redirect(url_for("staff.login"))

    # load registration template
    # noinspection PyUnresolvedReferences
    return render_template("staff/register.html", form=form, title='Register Staff')


@staff.route('/login/', methods=['GET', 'POST'])
def login():
    """
        Handle requests to the /login route
        Log staff in through the login form
        """
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
    if 'active' in session and session['active']:
        flash("You cannot log out while a class is running")
        return redirect(url_for('staff.dashboard'))
    logout_user()
    if 'lecturer_id' in session:
        session.pop('lecturer_id')
    if 'start' in session:
        session.pop('start')

    # redirect to the home page
    return redirect(url_for('home.index'))


@staff.route('/dashboard/')
@login_required
def dashboard():
    active = False
    if 'active' in session:
        active = session['active']
    # noinspection PyUnresolvedReferences
    return render_template("staff/dashboard.html", title="Staff Dashboard", home=True, active=active, is_lecturer=True,
                           pid=session['lecturer_id'])


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
    active = False
    if 'active' in session:
        active = session['active']
    form = CourseForm()
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


@staff.route('/_get_courses/')
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


# noinspection PyUnresolvedReferences
@staff.route('/start_class/', methods=['POST', 'GET'])
@login_required
def _start_class():
    """
    Function that enables a staff member to start a class
    from a list of courses (s)he has registered to
    :return: HTML template of the class form
    """
    if 'active' in session and session['active']:
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
    active = False
    if 'active' in session:
        active = session['active']
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
    active = False
    if 'active' in session:
        active = session['active']
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
        active = False
        if 'active' in session:
            active = session['active']
        return render_template("staff/clock.html", active=active, title="Running Class", is_lecturer=True,
                               pid=session['lecturer_id'])
