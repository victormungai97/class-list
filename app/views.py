from flask import render_template, request

from app import app, create_database, insert_db, get_contents, register_db, general_delete, insert_suggestion
from .models import Table, Test

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
	create_database()
	return render_template('add.html')
	
#register student
@app.route('/register/')
def register_student():
	'''Function to register new students'''
	create_database()
	return render_template('register.html')
	
@app.route('/registration2/',methods=['POST', 'GET'])
def register2():
	'''Function to take data from website'''
	create_database()
	name=''; regno=''; error=''
	if request.method == 'POST':
		# receive details from website
		regno=request.form['regno']
		name=request.form['name']

		# get results from insertion into db
		message, status = register_db(regno, name)
		return render_template("result.html",msg=message,sts=status)
	
@app.route('/registration/',methods=['POST','GET'])
def register():
	'''Function to register new students'''
	create_database()
	# user details
	name=''; regno=''; error=''
	if request.method == 'POST':
		# receive json
		json = request.get_json(force=True)
		# get user details
		regno = json['regno']
		name = json['name']
		
	message, status = register_db(regno, name)
	if not status:
		error = str(False)
	else:
		error = str(True)
	result = '{"message": "%s", "error": "%s"}' % (message, error)
	return result
	
@app.route('/getstudent/',methods=['POST','GET'])
def get_students():
	'''Function to check registered students'''
	message=''; regno=''; status=0; error=''
	if request.method == 'POST':
		json = request.get_json(force=True)
		regno = json['regno']
	
		# check whether student is registered
		data = Table.query.filter(Table.reg_no==regno).first()
		
		if data:
			message = data.name
		else:
			status = 1
			message = "Student not registered. Please register"
		if not status:
			error = str(False)
		else:
			error = str(True)
		return '{"message" : "%s", "error" : "%s"}' % (message, error)
	
	if request.method == 'GET':
		result = get_contents ('Table')
		return render_template('rlist.html', res=result)
		
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
		#gps=float(json['gps'])
		latitude=float(json['latitude'])
		longitude=float(json['longitude'])
		lac=float(json['lac'])
		ci=float(json['ci'])
		img_data=json['picture']
		img_data=img_data.encode('UTF-8','strict')
		import base64
		pic_name = name + ".jpg"
		# decode image string and write into file
		with open(pic_name, 'wb') as fh:
			fh.write(base64.b64decode(img_data))
		pic = pic_name
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
	if request.method == 'POST':
		# receive details from website
		regno=request.form['regno']
		name=request.form['name']
		time=request.form['time']
		#lac=request.files['lac']
		#ci=request.files['ci']        
		pic=request.files['picture']

		# get results from insertion into db
		message, status = insert_db(name,regno,time,latitude,longitude,lac,ci,pic,'record')
		return render_template("result.html",msg=message,sts=status)
		
@app.route('/list/')
def list():
	'''Function to print contents of db to webpage'''
	# select all from database
	rows = get_contents('Test')
	#print contents
	return render_template("list.html",rows=rows)
	
@app.route('/basic/')
def blist():
	'''Function to print contents of db to webpage'''
	# select all from database
	rows = get_contents("Basic")
	#print contents
	return render_template("blist.html",rows=rows)
	
# delete row in db
@app.route('/rlist/delete/',methods =['POST'])	
def rlist_delete():
	"""Function to delete row in details table"""
	rows = general_delete("Table",id=request.form['id'])
	#print contents
	return render_template("rlist.html",res=rows)
	
# delete row in db
@app.route('/delete/',methods =['POST'])	
def delete():
	"""Function to delete row in students table"""
	general_delete("Basic",id=request.form['id'])
	rows = general_delete("Test",id=request.form['id'])
	#print contents
	return render_template("list.html",rows=rows)
	
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
		return render_template("suggestions.html",rows=rows)