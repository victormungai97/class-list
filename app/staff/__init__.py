# app/staff/__init__.py

from flask import Blueprint

staff = Blueprint("staff", __name__, url_prefix='/staff')

from . import views
