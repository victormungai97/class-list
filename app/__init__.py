# app/__init__.py

import os
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

from config import app_config
from app.database import db_session, init_db

db = SQLAlchemy()  # db instance variable
app = Flask(__name__, instance_relative_config=True)
login_manager = LoginManager()

# app.config['SQLALCHEMY_DATABASE_URI'] = '''mysql+pymysql://username:password@localhost/db_name'''
# app.config['SECRET_KEY'] = "your-secret-key"

print(u"Current path is", os.path.abspath(os.curdir), sep=' ')


def create_app(config_name):
    """
    This is the method that initializes modules used in the app
    :param config_name: The key for the configuration to use
    :return: Flask app
    """
    if config_name not in app_config.keys():
        config_name = 'development'
    app.config.from_object(app_config[config_name])
    # use if you have instance/config.py with your SECRET_KEY and SQLALCHEMY_DATABASE_URI
    app.config.from_pyfile('config.py')
    db.init_app(app)
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

    @app.route('/500/')
    def error():
        abort(500)

    return app


# path to registration pictures
registration_folder = os.path.join("app/static/register")
# path to class pictures
upload_folder = os.path.join("app/static/uploads")

# create the folders
if not os.path.isdir(registration_folder):
    os.makedirs(registration_folder)
if not os.path.isdir(upload_folder):
    os.makedirs(upload_folder)


@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    Method closes database session after app closes or request is completed
    :return: None
    """
    db_session.remove()
