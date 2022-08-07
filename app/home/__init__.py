# app/home/__init__.py

from flask import Blueprint

home = Blueprint("home", __name__, url_prefix='/home')

from . import views
