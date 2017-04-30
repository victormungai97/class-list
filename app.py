import os
import re
import shutil
from flask import Flask,render_template,request,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from time import *
import pymysql as mysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = '''mysql+pymysql://myuser:xxxx@localhost/test'''
db = SQLAlchemy(app) # db instance variable

class Table(db.Model):
	'''Class that models basic student details'''
	__tablename__ = 'Details'
	id = db.Column('id', db.Integer, primary_key=True)
	name = db.Column('name', db.String(60), unique=True)
	reg_no = db.Column('regno', db.Unicode(60), unique=True)
	
	def __init__(self, name, reg_no):
		'''Function that adds basic details of students to table'''
		self.name = name
		self.reg_no = reg_no
		
	def __repr__(self):
		return ",Student %r>" % self.name

class Test(db.Model):
	'''Class that models students table'''
	__tablename__ = 'students' # set table name
	id = db.Column('id', db.Integer, primary_key=True)
	name = db.Column('name',db.String(60))
	reg_no = db.Column('regno',db.Unicode(60))
	latitude = db.Column('latitude',db.Float)
	longitude = db.Column('longitude',db.Float)
	lac = db.Column('lac',db.Float)
	ci = db.Column('ci',db.Float)
	pic_url = db.Column('picture_url',db.String(100))
	time = db.Column('time',db.Unicode(60))
	source = db.Column('source',db.Unicode(60))

	def __init__(self, name, reg_no, lat, longi, lac, ci, pic_url, source, time = None):
		'''Function initializes class and is used to add user to db'''
		self.name = name
		self.reg_no = reg_no
		if not time:
			time = strftime("%b %d, %Y %H:%M:%S")
		self.time = time
		self.latitude = lat
		self.longitude = longi
		self.lac = lac
		self.ci = ci
		self.pic_url = pic_url
		self.source = source

	def __repr__(self):
		return "<Student %r>" % self.name

# This is the path to the upload directory
print ("Current path is", os.path.abspath(os.curdir))
new_folder = os.path.join("static/uploads/")
app.config['UPLOAD_FOLDER'] = new_folder
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	'''Checks whether file is allowed based on filename extension'''
	return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def create_database():
	'''Function creates table where not created'''
	db.create_all()

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
	return render_template('add.html')
	
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
	extension=str(extension[1])
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
	pic_url ='uploads\\'+regno+'.'+extension
	return os.path.abspath(destination)
	
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
		
	# Get student with specific regno or name
	data = Table.query.filter((Table.reg_no==regno)|(Table.name==name)).first()
	
	status = 0
	message = ''
	# if student not in db, enter into db
	if not data:
		test = Table(name, regno)
		# for successful connection
		try:
			# add new row to db
			db.session.add(test)
			# save changes
			db.session.commit()
			message = "Record successfully added"
		# for unsuccessful connection
		except Exception as err:
			# display error
			print (err)
			# undo changes
			db.session.rollback()
			message = "Record not added. Connection unsuccessful"
			status = 1
	# if user in db
	else:
		message = "Student is in database"
		status = 2
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
		res = Table.query.all()
		#for person in res:
		#	print (person.name,'\n',person.reg_no)
		return render_template('blist.html', res=res)
	
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
	
def insert_db(name, regno, time, latitude, longitude, lac, ci, pic,method,source="Browser"):
	'''Function to save given user data into db'''
	pic_url='' # url of picture
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
	test = Test(name, regno, latitude, longitude, lac, ci, pic_url, source, time)
	# for successful connection
	try:
		# add new row to db
		db.session.add(test)
		# save changes
		db.session.commit()
		message = "Record successfully added"
	# for unsuccessful connection
	except Exception as err:
		# display error
		print (err)
		# undo changes
		db.session.rollback()
		message = "Record not added. Connection unsuccessful"
		status = 1

	app.config['UPLOAD_FOLDER'] = new_folder
	return (message, status)
	
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
	#fh.close()
	
def get_contents():
	'''Function to get data from db'''
	# open db connection
	host = 'localhost' # host
	userName = 'myuser' # user
	password = 'xxxx' # password
	db = 'test' # user
	#create connection
	conn = mysql.connect(host, userName, password, db)
	#define cursor for traversal
	cursor = conn.cursor()
	#execute query for all items
	cursor.execute("SELECT * FROM students")
	#retrieve results
	return cursor.fetchall()
	
@app.route('/list/')
def list():
	'''Function to print contents of db to webpage'''
	# select all from database
	#rows = Test.query.all()
	rows = get_contents()
	#print contents
	return render_template("list.html",rows=rows)
	
#delete row in db
'''
@app.route('/delete/',methods =['POST'])
def delete():
    #capture reference to mysql connection
    conn = mysql.connect()
    #initiate cursor
    cursor = conn.cursor()
    #delete from students table
    cursor.callproc("delete_entry",[request.form['id']]) 
    #update db after command execution using connection captured earlier
    conn.commit()

    cursor.execute("SELECT * FROM Basic_Details") 
    #update db after command execution using connection captured earlier
    conn.commit()
    #retrive query n initualite it
    rows=cursor.fetchall()
    return render_template("list.html",rows=rows)
'''
	
# delete row in db
@app.route('/blist/delete/',methods =['POST'])	
def blist_delete():
	"""Function to delete row in details table"""
	# create query for deletion
	delete = Table.query.filter(Table.id==request.form['id']).first()
	# carry out deletion
	db.session.delete(delete)
	# save changes
	db.session.commit()
	
	# select all from database
	rows = Table.query.all()
	# update db after command execution 
	db.session.commit()
	#print contents
	return render_template("blist.html",res=rows)

# delete row in db
@app.route('/delete/',methods =['POST'])	
def delete():
	"""Function to delete row in students table"""
	# create query for deletion
	delete = Test.query.filter(Test.id==request.form['id']).first()
	# carry out deletion
	db.session.delete(delete)
	# save changes
	db.session.commit()
	
	# select all from database
	#rows = Test.query.all()
	rows = get_contents()
	# update db after command execution 
	db.session.commit()
	#print contents
	return render_template("list.html",rows=rows)

	
if __name__=='__main__':
	# start app
	app.run(debug=True)
	