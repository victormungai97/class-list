# app/email.py

"""
Handles sending of emails
"""

from flask import render_template, url_for, current_app
from flask_mail import Message
from threading import Thread

from app import mail


# this function makes sending email asynchronous(scheduled to run in background)
# freeing the send_email() to return immediately
# so that the application can continue running concurrently with the email being sent
def send_async_email(app, msg):
    # The application context that is created with the with app.app_context() call
    # makes the application instance accessible via the current_app variable from Flask.
    with app.app_context():
        mail.send(msg)


# noinspection PyProtectedMember
def send_email(subject, sender, recipients, text_body, html_body):
    """
    This method facilitates sending of email, using Flask-Mail
    :param subject: Subject of the email
    :param sender: Sender of the email
    :param recipients: List of receivers of email
    :param text_body: Message to be sent as text
    :param html_body: Message to be sent as HTML
    :return: None
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    # Text and HTML bodies are important as some server might render text while others show the HTML
    msg.body = text_body
    msg.html = html_body
    # Here, we start a background thread for email being sent
    # which is much less resource intensive than starting a brand new process
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_password_reset_email(user):
    # Here, we shall generate a reset password token and send it to the user's email
    # We are rendering a text and HTML file so as to carter for the possible email text body allowed by user's email
    token = user.get_reset_password_token()
    confirm_url = url_for('staff.reset_password', token=token, _external=True)
    send_email('[Class Attendance System] Reset Your Password',
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         name=user.name, confirm_url=confirm_url),
               html_body=render_template('email/reset_password.html',
                                         name=user.name, confirm_url=confirm_url)
               )
