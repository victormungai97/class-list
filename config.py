# config.py

"""
Module containing the configurations for different environments
"""

import os
import instance.config as cfg

try:
    # Here, we obtain environment variables from a settings file
    # Useful for running inside an IDE
    from settings import get_env_variable

    SECRET_KEY = get_env_variable['SECRET_KEY']
    ADMIN_PASSWORD = get_env_variable['ADMIN_PASSWORD']
    JWT_SECRET_KEY = get_env_variable['JWT_SECRET_KEY']
except (ImportError, Exception):
    # Here, we obtain environment variables directly from computer
    # Useful for running in a terminal
    SECRET_KEY = os.getenv('SECRET_KEY')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


class Config(object):
    """Common configurations"""
    # Put any configurations common across all environments
    SESSION_COOKIE_NAME = "session"
    TESTING = False
    CSRF_ENABLED = True
    ADMIN_PASSWORD = ADMIN_PASSWORD or "admin-password"
    SECRET_KEY = SECRET_KEY or "my-secret-key"
    JWT_SECRET_KEY = JWT_SECRET_KEY or 'jwt-secret-string'
    # Define path for upload folder
    UPLOAD_FOLDER = "app/static/uploads"
    # specify the type of cache required, 'simple' should do
    CACHE_TYPE = 'simple'
    # used for email confirmation
    EMAIL_CONFIRMATION_KEY = cfg.EMAIL_CONFIRMATION_KEY
    # email server details to configure Flask to send email immediately after an error, with stack trace in email body
    MAIL_SERVER = cfg.MAIL_SERVER  # if not set, then emailing errors will be disabled
    MAIL_PORT = int(cfg.MAIL_PORT or 25)  # set to standard port 25 if not set
    # Transport Layer Security(TLS) with SMTP provides confidentiality and authentication for email traffic
    MAIL_USE_TLS = cfg.MAIL_USE_TLS or 1
    # mail server credentials, optional,
    # remember to create official email, with Oscar's number, specifically for this purpose
    MAIL_USERNAME = cfg.MAIL_USERNAME
    MAIL_PASSWORD = cfg.MAIL_PASSWORD
    # list of the email addresses that will receive error reports
    ADMINS = ['venturikenya@gmail.com']
    # ADMINS = ['victormungai97@gmail.com', 'pollwalker71@gmail.com', 'jjumapaul@gmail.com', 'oscaruon@gmail.com',
    #           'petermule.pkm@gmail.com', 'dianawanjiru450@gmail.com']


class DevelopmentConfig(Config):
    """Development configurations"""
    DEBUG = True  # activates debug mode on app
    SQLALCHEMY_ECHO = True  # allows SQLAlchemy to log errors
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # allows SQLAlchemy to track changes while running


class ProductionConfig(Config):
    """Production configurations"""
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(DevelopmentConfig):
    """Testing configurations"""

    TESTING = True
    # Give a testing database
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://dt_admin:dtAdmin@2016@localhost/dreamteam_test'


app_config = {
    'development': 'DevelopmentConfig',
    'production': 'ProductionConfig',
    'testing': 'TestingConfig',
}
