# app/__init__.py

import os
from threading import Timer
from datetime import datetime
from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

from config import app_config
from app.database import db_session, init_db
# from automate import automate

# db = SQLAlchemy()  # db instance variable
app = Flask(__name__, instance_relative_config=True)
login_manager = LoginManager()

# app.config['SQLALCHEMY_DATABASE_URI'] = '''mysql+pymysql://username:password@localhost/db_name'''
# app.config['SECRET_KEY'] = "your-secret-key"

home_folder = os.path.abspath(os.curdir)
print(u"Current path is", home_folder, sep=' ')


def train_images():
    """
    This function checks if the registration deadline - to be provided by admin - has been reached
    If so, it will close the registration options and call the image training code
    If not, it will count for another 24 hours and check again
    It uses the Timer class in the threading module to loop for (24*3600) seconds
    :return: None
    """
    t = Timer(86400, train_images)
    t.start()

    if datetime.now() >= datetime(2015, 12, 12):
        print("Calling image training")
        # image training code goes here
        ###############################
        """
        automate()
        """
        ###############################
        t.cancel()
        return

    print("Registration still on")


def create_app(config_name):
    """
    This is the method that initializes modules used in the app
    :param config_name: The key for the configuration to use
    :return: Flask app
    """
    if config_name not in app_config.keys():
        config_name = 'development'
    app.config.from_object(".".join(["config", app_config[config_name]]))
    # use if you have instance/config.py with your SECRET_KEY and SQLALCHEMY_DATABASE_URI
    app.config.from_pyfile('config.py')
    # db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message = "Log in required to view this page"
    Bootstrap(app)

    from app import models

    from .student import student as student_blueprint
    app.register_blueprint(student_blueprint)

    from .staff import staff as staff_blueprint
    app.register_blueprint(staff_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    # noinspection PyUnresolvedReferences
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html', title='Forbidden', wrapper='Forbidden', error=True), 403

    # noinspection PyUnresolvedReferences
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', title='Page Not Found', wrapper='Page Not Found', error=True), 404

    # noinspection PyUnresolvedReferences
    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html', title='Internal Server Error', wrapper='Server Error',
                               error=True), 500

    # noinspection PyUnresolvedReferences
    @app.errorhandler(401)
    def bad_or_missing_authentication(error):
        return render_template('errors/401.html', title='Unauthorized', wrapper="Unauthorized", error=True), 401

    # noinspection PyUnresolvedReferences
    @app.errorhandler(503)
    def temporarily_unavailable(error):
        return render_template('errors/503.html', title="Temporarily Unavailable", wrapper="Temporarily Unavailable",
                               error=True), 503

    return app


# path to class pictures
upload_folder = os.path.abspath(os.path.join("app/static/uploads"))

# create the folders
if not os.path.isdir(upload_folder):
    os.makedirs(upload_folder)

train_images()


@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    Method closes database session after app closes or request is completed
    :return: None
    """
    db_session.remove()
