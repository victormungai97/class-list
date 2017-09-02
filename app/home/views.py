# app/home/views.py

from flask import render_template, request, jsonify

from . import home
from app.models import Lecturer, Student


@home.route('/')
def index():
    return render_template("home/home.html", title="Home", home=True)


@home.route('/user_name/')
def get_name():
    table = request.args.get("table")
    pid = int(request.args.get("id"))
    user = None
    if table == 'Lecturer':
        user = [(lec.name,) for lec in Lecturer.query.filter(Lecturer.id == pid).all()]
    elif table == 'Student':
        user = Student.query.filter_by(id=pid).first().name
    print(user)
    return jsonify(user)
