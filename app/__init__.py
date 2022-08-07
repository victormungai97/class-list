# app/__init__.py

from __future__ import print_function
import os
import shlex
from threading import Timer
from datetime import datetime
from flask import Flask, send_from_directory, redirect, url_for, request
from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from graphene_file_upload.flask import FileUploadGraphQLView
from subprocess import Popen

from config import app_config
from app.cache import cache
from app.database import db_session, init_db

# from automate import automate

# db = SQLAlchemy()  # db instance variable
app = Flask(__name__, instance_relative_config=True)
login_manager = LoginManager()
mail = Mail()
jwt = JWTManager()
cors = CORS(resources={r"/classlist_api/": {"origins": "http://localhost:3000"}})

# app.config['SQLALCHEMY_DATABASE_URI'] = '''mysql+pymysql://username:password@localhost/db_name'''
# app.config['SECRET_KEY'] = "your-secret-key"

home_folder = os.path.abspath(os.curdir)
print(u"Current path is", home_folder, sep=' ')
# set number of images for registration per user
numOfImages = 10
# This is the process that will set up Altair GraphQL Client IDE
altair_process = None


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


# path to logs folder
logs_folder = os.path.abspath(os.path.join("app/logs"))
if not os.path.isdir(logs_folder):
    os.makedirs(logs_folder)


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
    if not app.config['TESTING']:
        Bootstrap(app)
    cache.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    from app import models, errors, schema

    errors.system_logging('ClassList - A class attendance system')

    # these are blueprints, they are used in place of app in their respective view route decorators
    from .student import student as student_blueprint
    app.register_blueprint(student_blueprint)

    from .staff import staff as staff_blueprint
    app.register_blueprint(staff_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    # GraphQL has only a single URL from which it is accessed
    if not app.config['TESTING']:
        app.add_url_rule(
            '/classlist_api/',  # expose the GraphQL schema under this url
            view_func=FileUploadGraphQLView.as_view(
                'api',
                schema=schema.schema,
            )
        )

    return app


# Here, we shall start a background cmd process where we shall run a Express JS program so as to start GraphQL IDE
def setup_altair():
    global altair_process
    # set up command
    if app.config['DEBUG']:
        # during development
        cmd = 'npm run dev'
    else:
        if app.config['TESTING']:
            # During testing, do nothing
            cmd = ''
        else:
            # during production
            cmd = 'npm run start'
    # Take a string command and split into a list to run in command line terminal
    args = shlex.split(cmd)
    # start background process
    altair_process = Popen(args=args)


# Serve GraphQL Playground for testing
@app.route('/classlist_api/')
def graphql():
    from flask import render_template
    return render_template("graphql/playground.html", title="GraphQL Playground")


# serve home page
@app.route('/')
def index():
    return redirect(url_for('home.index'))


# serve the icon
@app.route('/favicon.ico/')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'), 'favicon.ico')


# serve document from upload folder
@app.route('/static/uploads/<filename>/')
def upload(filename):
    from werkzeug.utils import secure_filename
    return send_from_directory(os.path.join(app.root_path, 'static', 'uploads'), secure_filename(filename))


# path to class pictures
if not app.config.get("UPLOAD_FOLDER", None):
    app.config["UPLOAD_FOLDER"] = "app/static/uploads"

# create the folders
if not os.path.isdir(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

train_images()
setup_altair()


@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    Method closes database session after app closes or request is completed
    :return: None
    """
    if exception:
        print("Exception encountered: {}".format(repr(exception)))
    db_session.remove()
    # close altair-running process
    global altair_process
    altair_process.terminate()
