# app/extras.py

import os
import re
from datetime import datetime
from flask import session, abort, render_template, url_for, request, jsonify
from flask_weasyprint import render_pdf, HTML
from shutil import rmtree, move
from werkzeug.utils import secure_filename
from zipfile import ZipFile, is_zipfile

from app import app, home_folder
from .database import db_session
from .models import Student, Photo, Attendance, VerificationStatus, User, Course
from .errors import system_logging
from .email import send_email
from .security import ts
from populate import verification


# noinspection PyArgumentList,PyUnresolvedReferences
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

        # Now we'll send the email confirmation link
        subject = "[Class Attendance System] Confirm Your Email"
        # encode the email address in the token.
        # The token will also contain a timestamp to let us set a time limit on how long it's valid
        token = ts.dumps(email, salt=app.config["EMAIL_CONFIRMATION_KEY"])
        # url to carry out email confirmation
        confirm_url = url_for('student.confirm_email', token=token, _external=True)
        # send email
        send_email(subject,
                   sender=app.config['MAIL_USERNAME'],
                   recipients=[email],
                   text_body=render_template('email/confirm_email.txt', name=name, confirm_url=confirm_url),
                   html_body=render_template('email/confirm_email.html', name=name, confirm_url=confirm_url)
                   )

        # send message of successful registration
        message = "Successful registration of {}. Please check your email to activate your account".format(name)
    except Exception as err:
        status, message = 1, "Error during student registration"
        print(err)
        system_logging(err, exception=True)
        db_session.rollback()

    return message, status, student_


# noinspection PyUnresolvedReferences
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

        message = "Success."
        system_logging("{} Class attended by {}".format(message, reg_num))
    except Exception as err:
        message, status = "Something went wrong in attendance. Please try again", 1
        print(err)
        system_logging(err, exception=True)
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
    print(filename)
    return filename


def make_pdf(pid, rows, outfile, html, wrap, title):
    """
    Function converts HTML template page to PDF and passes the PDF to user for download
    :param title: Title of web page
    :param wrap: Message above table
    :param pid: Unique identifier of user
    :param rows: List of fields in table
    :param outfile: PDF to be downloaded
    :param html: HTML template page to convert
    :return: response to download PDF
    """
    # list of css files
    css = ['app/static/css/style.css',
           'app/static/css/bootstrap.min.css',
           'app/static/css/narrow-jumbotron.css',
           'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
           'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css'
           ]
    # generate pdf as variable in memory
    pdf = render_template(html,
                          title=title,
                          reg_no=pid,
                          date=datetime.now().strftime("%d %B %Y %I:%M:%S %p"),
                          wrap=wrap,
                          rows=rows,
                          download=True)

    # Make a PDF straight from HTML in a string. render_pdf takes care of creating Response with correct headers
    return render_pdf(HTML(string=pdf), stylesheets=css, download_filename=outfile)


# noinspection PyUnresolvedReferences
def zipfile_handling(zip_file=None, reg_no='', name=''):
    """
    Here, the images used for registration are received from the mobile app in a zip file
    The zip file is then extracted and the images stored in the upload folder under the student's registration number
    and the images named using the student's name
    :param zip_file: Zip file containing student's registration images
    :param reg_no: Student's registration number
    :param name: Student's name
    :return: List of urls pointing to where the images are stored or empty list
    """
    from pictures import allowed_file, determine_picture
    if not zip_file or not reg_no or not name:
        return 'Details used for storing images missing', 3, []
    pic_url, unzip, files, filename = [], False, [], ""
    message, status = '', 0
    path = create_path(reg_no)
    # if file has come as file object ie filename = open(file)
    if hasattr(zip_file, "read"):
        filename = secure_filename(zip_file.filename)
        zip_file.save(os.path.join(path, filename))
    else:
        filename = zip_file
        zip_file = path + filename
    directory = path + os.path.basename(filename).replace(".zip", "")

    # confirm that file is a zip file
    if is_zipfile(zip_file):
        # open the zip file in READ mode
        with ZipFile(os.path.join(path, filename), 'r') as zip_file:
            # print all the contents of the zip file in table format
            zip_file.printdir()

            # extract all the files in zip file
            print('Extracting all the files now...')
            zip_file.extractall(path=directory)
            # remember unzipping has happened
            unzip = True

            # delete redundant zip file
            print('Deleting file {}...'.format(filename))
            filename = path + filename
            os.remove(filename)
            print('Done!')
    else:
        return "Failure!! Non-zipfile sent", -2, []

    # if successful unzipping
    if unzip:
        # read the files in the resultant directory
        files = os.listdir(directory)
        # change working directory in resultant directory
        os.chdir(directory)
        for image in files:
            # move files into the parent directory
            filename = secure_filename(image)
            move(filename, os.path.join(os.pardir, filename))

    # move to parent directory
    os.chdir(os.pardir)
    # delete resultant directory
    rmtree(directory)
    # process the files
    for image in files:
        if os.path.isfile(os.path.join(os.curdir, image)):
            filename = secure_filename(image)
            if not allowed_file(filename):
                # noinspection PyUnusedLocal
                message, status = "File format not supported", 3
                return message, status, pic_url
            else:
                message, status = 'Success', 0
                url, verified = determine_picture(reg_no, name.replace(" ", "_"), image, filename, path=path,
                                                  phone=True)
                pic_url.append(url)

    # return to original location
    os.chdir(home_folder)
    print(u"Current path is", os.path.abspath(os.curdir), sep=' ')
    return message, status, pic_url


def create_path(reg_num=""):
    """
    Function that creates the users' file directories using their registration numbers
    :param reg_num: Registration number of students
    :return: Path to the directories
    """
    # split reg_num to retrieve year, course and specific number of student
    details = reg_num.split("/")
    # create new path to folder for student's image(s)
    path = '/'.join([os.getcwd(), app.config["UPLOAD_FOLDER"], '_'.join([details[0], details[2], details[1]]), ''])
    # create the new folder
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


# noinspection PyUnresolvedReferences
def get_courses():
    """
    The views calling this function will respond to XHR requests for courses
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


def staff_send_confirmation_email(email, name):
    """
    Here, we send the email to the staff member for confirmation
    :param email: The email address of the user
    :param name: The name of the user
    :return: None
    """
    subject = "[Class Attendance System] Confirm Your Email"
    # encode the email address in the token.
    # The token will also contain a timestamp to let us set a time limit on how long it's valid
    token = ts.dumps(email, salt=app.config["EMAIL_CONFIRMATION_KEY"])
    # url to carry out email confirmation
    confirm_url = url_for('staff.confirm_email', token=token, _external=True)
    # send email
    send_email(subject,
               sender=app.config['MAIL_USERNAME'],
               recipients=[email],
               text_body=render_template('email/confirm_email.txt', name=name, confirm_url=confirm_url),
               html_body=render_template('email/confirm_email.html', name=name, confirm_url=confirm_url)
               )


def validate_email(email=''):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param email: Email address to be validated
    :return: Result and status of check
    """
    # This is the format that we shall check our email against
    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE)
    # Here, email not passed or email doesn't contain '@'
    if not email or '@' not in email:
        return 'Invalid email address.', -3
    # split email based on '@', then check the user and domain parts individually
    user_part, domain_part = email.rsplit('@', 1)
    if not user_regex.match(user_part):
        return 'Invalid email address.', -3
    validate_hostname = HostnameValidation(require_tld=True)
    if not validate_hostname(domain_part):
        return 'Invalid email address.', -3
    return "Email address valid", 0


def get_non_blank_input(string='', variable=""):
    """
    This is a function that will ensure that a string, particularly an input, is not empty
    :param string: The string that should not be empty
    :param variable: The variable that string will be assigned to
    :return: The message telling us result of check, the status of check and string
    """
    response, status = "", 0
    if not string or string == '' or len(string.strip()) == 0:
        response, status = "{var} cannot be an empty string".format(var=variable), -2

    return response, status, string


class HostnameValidation(object):
    """
    Helper class for checking hostnames for validation.

    This is not a validator in and of itself, and as such is not exported.
    """
    hostname_part = re.compile(r'^(xn-|[a-z0-9]+)(-[a-z0-9]+)*$', re.IGNORECASE)
    tld_part = re.compile(r'^([a-z]{2,20}|xn--([a-z0-9]+-)*[a-z0-9]+)$', re.IGNORECASE)

    def __init__(self, require_tld=True):
        self.require_tld = require_tld

    def __call__(self, hostname):
        from six import string_types
        # Encode out IDNA hostnames. This makes further validation easier.
        try:
            hostname = hostname.encode('idna')
        except UnicodeError:
            pass

        # Turn back into a string in Python 3x
        if not isinstance(hostname, string_types):
            hostname = hostname.decode('ascii')

        if len(hostname) > 253:
            return False

        # Check that all labels in the hostname are valid
        parts = hostname.split('.')
        for part in parts:
            if not part or len(part) > 63:
                return False
            if not self.hostname_part.match(part):
                return False

        if self.require_tld:
            if len(parts) < 2 or not self.tld_part.match(parts[-1]):
                return False

        return True
