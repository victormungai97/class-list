# app/errors.py

"""
This module will handles the errors that might arise from the system
It will contain custom functions that redirect user to custom URLs when various errors occur
and a function that logs the errors and informs the admin(s) when said errors occur
"""

import logging
import os
import werkzeug.exceptions as ex
from werkzeug.http import HTTP_STATUS_CODES
from flask import render_template
from logging.handlers import SMTPHandler, RotatingFileHandler

from app import app, logs_folder


class BandwidthExceeded(ex.HTTPException):
    """
    Create custom status code for error 509
    """
    code = 509
    description = 'The server is temporarily unable to service your request due to the site owner ' \
                  'reaching his/her bandwidth limit. Please try again later. '


ex.default_exceptions[509] = BandwidthExceeded
HTTP_STATUS_CODES[509] = 'Bandwidth Limit Exceeded'
abort = ex.Aborter()

# change format of log message
# here, we've set the timestamp, logging level, message, source file & line no where log entry originated
LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"


@app.errorhandler(403)
def forbidden(error):
    errs = str(error).split(':')[-1].split('.')
    return render_template('errors/error.html', title='Forbidden', error=True, errors=errs), 403


@app.errorhandler(404)
def page_not_found(error):
    errs = str(error).split(':')[-1].split('.')
    return render_template('errors/error.html', title='Page Not Found', error=True, errors=errs), 404


@app.errorhandler(500)
def internal_server_error(error):
    errs = str(error).split(':')[-1].split('.')
    system_logging(error, exception=True)
    return render_template('errors/error.html', title='Internal Server Error', error=True, errors=errs), 500


@app.errorhandler(401)
def bad_or_missing_authentication(error):
    errs = str(error).split(':')[-1].split('.')
    errs[1] = '.'.join([errs[1], errs[2], ''])
    errs.remove('g')
    return render_template('errors/error.html', title='Unauthorized', error=True, errors=errs), 401


@app.errorhandler(503)
def temporarily_unavailable(error):
    errs = str(error).split(':')[-1].split('.')
    system_logging(error, exception=True)
    return render_template('errors/error.html', title="Temporarily Unavailable", error=True, errors=errs), 503


@app.errorhandler(509)
def bandwidth_limit_exceeded(error):
    errs = str(error).split(':')[-1].split('.')
    system_logging(error, exception=True)
    return render_template('errors/error.html', title="Bandwidth Limit Exceeded", error=True, errors=errs), 509


def _email():
    """
    Lets email errors to the developers
    :return:
    """
    # if app is running without debug mode
    if not app.debug:
        # allow sending logs by email only if mail server has been set
        if app.config.get('MAIL_SERVER'):
            auth = None
            # receive email server credentials, if any
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            # set up secure email traffic transport
            if app.config['MAIL_USE_TLS']:
                secure = ()
            # SMTPHandler from logging enables sending logs to admins by email
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'],
                subject='Class Attendance System Failure',
                credentials=auth,
                secure=secure,
            )
            # ensure only errors are reported
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)


def set_logger(filename):
    # save info, warnings, errors and critical messages in log file
    # limit size of log file to 10KB(10240 bytes) and keep last 30 log files as backup
    file_handler = RotatingFileHandler(filename, maxBytes=10240,
                                       backupCount=30)
    # set format
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # setting logging level to INFO enables logging to cover everything except DEBUG
    file_handler.setLevel(logging.INFO)
    return file_handler


def system_logging(msg, exception=False):
    """
    This is a function that handles system error logging,
    from emailing errors to logging the errors in a file.
    The messages in log file will have as much information as possible.
    RotatingFileHandler rotates the logs, ensuring that the log files
    do not grow too large when the application runs for a long time.
    The server writes a line to the logs each time it starts.
    When this application runs on a production server, these log entries will tell you when the server was restarted.
    :param: logs_folder = The folder that will contain the log file
    """
    # if log folder does not exist, create it
    if not os.path.isdir(logs_folder):
        os.makedirs(logs_folder)

    _email()

    app.logger.addHandler(set_logger(logs_folder + '/class_list.log'))
    app.logger.setLevel(logging.INFO)
    if exception:
        app.logger.exception(msg)
    else:
        app.logger.info(msg)
