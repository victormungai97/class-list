# app/__init__.py
import os
import re
import shutil
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename

from config import app_config, courses, myHelper

db = SQLAlchemy() # db instance variable
app = Flask(__name__, instance_relative_config=True)

def create_app(config_name):
	global app; global db
	if config_name not in app_config.keys():
		config_name = 'development'
	app.config.from_object(app_config[config_name])
	app.config.from_pyfile('config.py')
	db.init_app(app)
	
	return app

from .models import *

# This is the path to the upload directory
print ("Current path is", os.path.abspath(os.curdir))
new_folder = os.path.join("app/static/uploads/")
app.config['UPLOAD_FOLDER'] = new_folder
# folder for log files 
app.config['LOG_FOLDER'] = os.path.join("app/logs/")
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	'''Checks whether file is allowed based on filename extension'''
	return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def create_database():
	'''Function creates table where not created'''
	if not os.path.isdir(app.config['LOG_FOLDER']):
		os.makedirs(app.config['LOG_FOLDER'])
	db.create_all()
	
def get_url(pic,regno,method):
	'''Function stores and returns url for image'''
	# Move the file form the temporal folder to the upload folder
	if not os.path.isdir(app.config['UPLOAD_FOLDER']):
		os.makedirs(app.config['UPLOAD_FOLDER'])
	filename = ''
	#get name of the source file + Make the filename safe, remove unsupported chars
	if method == "fromapp":
		filename = str(secure_filename(pic))
		route = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		shutil.move(pic, route)
	if method == "record":
		filename = str(secure_filename(pic.filename))
		pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	#get file extension
	extension=filename.split(".")
	extension=str(extension[len(extension) - 1])
	#get path to source of uploaded file
	source=app.config['UPLOAD_FOLDER']+filename

	#delete existing file
	file = app.config['UPLOAD_FOLDER'] + regno + "." + extension
	if os.path.isfile(file):
		os.remove(file)
	
	#get path to destination of uploaded file 
	destination=app.config['UPLOAD_FOLDER']+regno+'.'+extension

	#rename file
	os.rename(source,destination)
	log_file = os.path.join(app.config['LOG_FOLDER'],"insert_log.db")
	myHelper(log_file, "Picture saved")
	pic_url = destination.replace("app","")
	return pic_url
	
def insert_db(name, regno, time, latitude, longitude, lac, ci, pic,method,source="Browser"):
	'''Function to save given user data into db'''
	log_file = os.path.join(app.config['LOG_FOLDER'],'insert_log.db')
	pic_url='' # url of picture
	course_code=""
	# check for '/' in regno
	match = re.search("/[\S]+/",regno)
	# if '/' found
	if match:
		paths = regno.split('/')
		print (regno)
		# get course code
		course_code = paths[0]
		# get year of study
		year_of_study = paths[2]
		# create new path
		app.config['UPLOAD_FOLDER'] = "/".join([app.config.get('UPLOAD_FOLDER'),course_code,year_of_study,'/'])
		regno = paths[1]
  # Check if the file is one of the allowed types/extensions
	if method == "record":
		if pic and allowed_file(pic.filename):
			pic_url = get_url(pic,regno,method)
	elif method == "fromapp":
		if pic and allowed_file(pic):
			pic_url = get_url(pic,regno,method)
	
	status = 0
	message = ''
	regno = '/'.join(paths)
	test = Test(name, regno, latitude, longitude, lac, ci, pic_url, source, time=time, course=courses.get(course_code))
	basic = Basic(name, regno, pic_url, courses.get(course_code))
	# get details for given reg_no
	data = Table.query.filter((Table.reg_no==regno)).first()
	
	# Incorrect name for reg_no given
	if data.name != name:
		message = "Name not registered. Connection unsuccessful"
		myHelper(log_file, message)
		status = 1
	else:
		# for successful connection
		try:
			# add new row to dbs
			db.session.add(test)
			db.session.add(basic)
			# save changes
			db.session.commit()
			message = "Record successfully added"
			myHelper(log_file, message + ". Student: " + regno)
		# for unsuccessful connection
		except Exception as err:
			# display error
			print (err)
			# undo changes
			db.session.rollback()
			message = "Record not added. Connection unsuccessful."
			myHelper(log_file, message + " " + err)
			status = 2

	app.config['UPLOAD_FOLDER'] = new_folder
	return (message, status)

def register_db(reg_no, name):
	'''Function to save registered new students into db'''
	log_file = os.path.join(app.config['LOG_FOLDER'],"register_log.db")
	# Get student with specific regno or name
	data = Table.query.filter((Table.reg_no==reg_no)|(Table.name==name)).first()
	
	# check course code
	course_name = reg_no[:3]
	if course_name not in courses.keys():
		myHelper(log_file, "Incorrect course code")
		return ("Incorrect course code", 3)
	
	status = 0
	message = ''
	# if student not in db, enter into db
	if not data:
		test = Table(name, reg_no, courses.get(course_name))
		# for successful connection
		try:
			# add new row to db
			db.session.add(test)
			# save changes
			db.session.commit()
			message = "Record successfully added."
			myHelper(log_file, message + " Student: " + reg_no)
		# for unsuccessful connection
		except Exception as err:
			# display error
			print (err)
			# undo changes
			db.session.rollback()
			message = "Record not added. Connection unsuccessful"
			myHelper(log_file, message + ". " + err)
			status = 1
	# if user in db
	else:
		message = "Student is in database"
		myHelper(log_file, message)
		status = 2
	return (message, status)
	
def insert_suggestion(choice, msg):
	'''Function to save suggestions'''
	log_file = os.path.join(app.config['LOG_FOLDER'],"suggestion_log.db")
	status = 0; message = ""
	suggestion = Suggestion(choice, msg)
	
	try:
		db.session.add(suggestion)
		db.session.commit()
		message = "Suggestion received"
		myHelper(log_file, message)
	except Exception as err:
		print (err)
		db.session.rollback()
		message = "Connection unsuccessful. Suggestion not sent"
		myHelper(log_file, message)
		status = 1
		
	return (message, status)
	
	
def get_contents(table):
	'''Function to get data from db'''
	rows = "";log_file = os.path.join(app.config['LOG_FOLDER'],"insert_log.db")
	myHelper(log_file, "Retrieving items from "+table)
	if table == 'Table':
		rows = Table.query.all()
	elif table == 'Basic':
		rows = Basic.query.all()
	elif table == 'Test':
		rows = Test.query.all()
	elif table == "Suggestion":
		rows = Suggestion.query.all()
	myHelper(log_file, "Items retrieved")
	return rows
	
def general_delete(tablename="",id=""):
	"""Function to delete row from passed table"""
	delete = ""
	log_file = os.path.join(app.config['LOG_FOLDER'],"delete_log.db")
	myHelper(log_file, "Deleting item from "+tablename)
	# create query for deletion
	if tablename == "Table":
		delete = Table.query.filter(Table.id==id).first()
	elif tablename == 'Test':
		delete = Test.query.filter(Test.id==id).first()
	elif tablename == 'Basic':
		delete = Basic.query.filter(Basic.id==id).first()
	# carry out deletion
	db.session.delete(delete)
	# save changes
	db.session.commit()
	myHelper(log_file,"Item deleted")
	
	rows = get_contents(tablename)
	# return results
	return rows
	
from app import views