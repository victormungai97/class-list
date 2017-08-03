# app/views.py

import os, pdfkit
from flask import render_template, request, make_response

from app import app, create_database, insert_db, get_contents, register_db, general_delete, insert_suggestion, decode_image, get_regno, compress_image
from .models import Table, Test
from .forms import RegisterForm, SignInForm
from config import myHelper

#home page
@app.route('/')
def home():
	'''Defines home page'''
	create_database()
	return render_template('home.html')
	
#add student page
@app.route('/enternew/')
def new_student():
	'''Function to enable one to enter information into db'''
	from random import randint
	create_database()
	form = SignInForm()
	return render_template('add.html',form=form,version=randint(1,100))
	
#register student
@app.route('/register/')
def register_student():
	'''Function to register new students'''
	create_database()
	form = RegisterForm() # web form
	return render_template('register.html',form=form)
	
@app.route('/registration2/',methods=['POST', 'GET'])
def register_web():
	'''Function to take data from website'''
	create_database()
	name=''; regno=''; error=''; form = RegisterForm()
	if request.method == 'POST':
		#check if form has been presented to user and filled accordingly
		if form.validate_on_submit():
			# receive details from website
			regno=request.form['regno']
			name=request.form['name']
			pic=request.files['picture']
			compress_image(pic.filename)

			# get results from insertion into db
			message, status = register_db(regno, name, pic, "register2")
			return render_template("result.html",msg=message,sts=status)
		else:
			return render_template('register.html',form=form)
	
@app.route('/registration/',methods=['POST','GET'])
def register():
	'''Function to take data from app'''
	create_database()
	# user details
	name=''; regno=''; error=''
	if request.method == 'POST':
		# receive json
		json = request.get_json(force=True)
		# get user details
		regno = json['regno']
		name = json['name']
		pic = decode_image(json['picture'], name)
		
	message, status = register_db(regno, name, pic, "register")
	if not status:
		error = str(False)
	else:
		error = str(True)
	result = '{"message": "%s", "error": "%s"}' % (message, error)
	return result
	
@app.route('/getstudents/')
def students():
	if request.method == 'GET':
		rows = get_contents ('Table')
		return render_template('rlist.html', rows=rows, table='rlist')

@app.route('/getstudent/',methods=['POST','GET'])
def get_students():
	'''Function to check registered students'''
	message=''; regno=''; status=0; error=''
	# file to save signing in from phone
	log_file = os.path.join(app.config['LOG_FOLDER'],"signin_log.db")
	if request.method == 'POST':
		json = request.get_json(force=True)
		regno = json['regno']
		# save attempt to sign in
		myHelper(log_file, "Student: "+regno+" attempting to sign in")
	
		# check whether student is registered
		data = Table.query.filter(Table.reg_no==regno).first()
		
		if data:
			message = data.name
		else:
			status = 1
			message = "Student not registered. Please register"
		
		if not status:
			error = str(False)
			# save successful signing in
			myHelper(log_file, "Student: "+regno+" logged in successfully")
		else:
			error = str(True)
			# save unsuccessful signing in
			myHelper(log_file, "Unsuccessful signing in")
		
		return '{"message" : "%s", "error" : "%s"}' % (message, error)
	
	if request.method == 'GET':
		rows = get_contents ('Table')
		return render_template('rlist.html', rows=rows, table='rlist')
		
@app.route('/fromapp/',methods=['POST','GET'])
def from_app():
	'''Function to take data from app'''
	create_database()
	# user details
	name=''; regno=''; time=None; latitude=0; longitude=0; lac=0; ci=0; pic=None; #gps = 0
	message = ""; error = ""
	if request.method == 'POST':
		# receive json sent
		json = request.get_json(force=True)
		# get received user details
		regno = json['regno']
		name=json['name']
		time=json['time']
		latitude=float(json['latitude'])
		longitude=float(json['longitude'])
		lac=float(json['lac'])
		ci=float(json['ci'])
		pic = decode_image(json['picture'], name)
		phone=json['phone']
		
		(message, status) = insert_db(name,regno,time,latitude,longitude,lac,ci,pic,'fromapp',phone)
		if not status:
			error=str(False)
		else:
			error=str(True)
	result = '{"message": "%s", "error": "%s"}' % (message, error)
	return result
	
@app.route('/record/',methods=['POST', 'GET'])
def record():
	'''Function to take data from website'''
	create_database()
	name=''; regno=''; time=None; latitude=0; longitude=0; lac=0; ci=0; pic=None; #gps = 0
	form = SignInForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			# receive details from website
			regno=request.form['regno']
			name=request.form['name']
			latitude=form.latitude.data
			longitude=form.longitude.data
			#lac=request.files['lac']
			#ci=request.files['ci']        
			pic=request.files['picture']
			agent = request.user_agent
			source = " ".join([agent.platform.title(), agent.browser.title(), agent.version])

			# get results from insertion into db
			message, status = insert_db(name,regno,time,latitude,longitude,lac,ci,pic,'record',source)
			return render_template("result.html",msg=message,sts=status)
		else:
			return render_template('add.html',form=form)
@app.route('/list/')
def list():
	'''Function to print contents of db to webpage'''
	# select all from database
	rows = get_contents('Test')
	#print contents
	return render_template("list.html",rows=rows,table='list')
	
@app.route('/basic/')
def blist():
	'''Function to print contents of db to webpage'''
	# select all from database
	rows = get_contents("Basic")
	#print contents
	return render_template("blist.html",rows=rows,table='blist')
	
@app.route('/download/<variable>')
def download(variable):
	'''
	Function that generates PDF from results and downloads them on user's machine
	'''
	rows = []
	if variable == 'list': rows = get_contents('Test')
	elif variable == 'rlist': rows = get_contents ('Table')
	elif variable == 'blist': rows = get_contents('Basic')
	else: rows = get_contents('Suggestion')
	outfile = variable+'.pdf'
	for row in rows:
		# set path of picture to its absolute path
		if row.pic_url: row.pic_url = os.path.abspath('app/static/'+row.pic_url).replace('\\','/')
	# specify wkhtmltopdf options
	options = {'quiet':'','user-style-sheet':os.path.abspath('app/static/css/style.css')}
	# generate pdf as variable in memory
	pdf = pdfkit.from_string(render_template(variable+'.html',rows=rows, download=True),False,options=options)
	# create custom response
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf' # receive pdf file
	# try and download the file
	response.headers['Content-Disposition'] = 'attachment; filename= {}'.format(outfile)
	return response
	
# delete row in db
@app.route('/rlist/delete/',methods =['POST'])	
def rlist_delete():
	"""Function to delete row in details table"""
	row = get_regno(request.form['id'])
	print (row.reg_no)
	general_delete("Basic",reg_no=row.reg_no)
	general_delete("Test",reg_no=row.reg_no)
	rows = general_delete("Table",id=request.form['id'])
	#print contents
	return render_template("rlist.html",res=rows,table='rlist')
	
# delete row in db
@app.route('/delete/',methods =['POST'])	
def delete():
	"""Function to delete row in students table"""
	general_delete("Basic",id=request.form['id'])
	rows = general_delete("Test",id=request.form['id'])
	#print contents
	return render_template("list.html",rows=rows,table='list')
	
@app.route('/suggestions/',methods =['POST','GET'])
def suggestions():
	if request.method == 'POST':
		json = request.get_json(force=True)
		suggestion = json['suggestion']
		choice = json['choice']
		(message, status) = insert_suggestion(choice, suggestion)
		if not status:
			error=str(False)
		else:
			error=str(True)
		result = '{"message": "%s", "error": "%s"}' % (message, error)
		return result
	elif request.method == "GET":
		rows = get_contents("Suggestion")
		return render_template("suggestions.html",rows=rows,table='suggestions')