# app/home/views.py

from flask import render_template

from . import home


@home.route('/')
def index():
    return render_template("home/home.html", title="Home", home=True)

