import os
import re
import shutil
from flask import Flask,render_template,request,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from time import gmtime, strftime
import pymysql as mysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = '''mysql+pymysql://myuser:xxxx@localhost/test'''
db = SQLAlchemy(app)

class Test(db.Model):
	__tablename__ = 'students'
	id = db.Column('id', db.Integer, primary_key=True)
	name = db.Column('name',db.String(60),unique=True)
	reg_no = db.Column('regno',db.Unicode(60),unique=True)
	#gps = db.Column('gps',db.Float)
	latitude = db.Column('latitude',db.Float)
	longitude = db.Column('longitude',db.Float)
	lac = db.Column('lac',db.Float)
	ci = db.Column('ci',db.Float)
	pic_url = db.Column('picture_url',db.String(60))
	time = db.Column('time',db.Unicode(60))
	source = db.Column('source',db.Unicode(60))

	def __init__(self, name, reg_no, lat, longi, lac, ci, pic_url, source, time = None):
		self.name = name
		self.reg_no = reg_no
		if not time:
			time = strftime("%b %d, %Y %H:%M:%S")
		self.time = time
		#self.gps = gps
		self.latitude = lat
		self.longitude = longi
		self.lac = lac
		self.ci = ci
		self.pic_url = pic_url
		self.source = source

	def __repr__(self):
		return "<Student %r>" % self.name

# This is the path to the upload directory
print (os.path.abspath(os.curdir))
new_folder = os.path.join("static/uploads/")
app.config['UPLOAD_FOLDER'] = new_folder
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def create_database():
	db.create_all()

#home page
@app.route('/')
def home():
	create_database()
	return render_template('home.html')

#add student page
@app.route('/enternew/')
def new_student():
    return render_template('add.html')
	
def get_url(pic,regno,method):
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

	#get path to destination of uploaded file
	##regno=re.findall(r'/([\w^/]+)/',regno)
	##regno=str(regno[0]) 
	destination=app.config['UPLOAD_FOLDER']+regno+'.'+extension

	#rename file
	os.rename(source,destination)
	pic_url ='uploads\\'+regno+'.'+extension
	return os.path.abspath(pic_url)
	
@app.route('/fromapp/',methods=['POST','GET'])
def from_app():
	create_database()
	name=''; regno=''; time=None; latitude=0; longitude=0; lac=0; ci=0; pic=None; #gps = 0
	message = ""; error = ""
	if request.method == 'POST':
		json = request.get_json(force=True)
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
		with open(pic_name, 'wb') as fh:
			fh.write(base64.b64decode(img_data))
		pic = pic_name
		phone=json['phone']
		
		(message, status) = insert_db(name,regno,time,latitude,longitude,lac,ci,pic,'fromapp',phone)
		if not status:
			error=str(False)
		else:
			error=str(True)
	result = "{message : %s, error=%s}" % (message, error)
	return result
	
def insert_db(name, regno, time, latitude, longitude, lac, ci, pic,method,source="Browser"):
	pic_url=''
	match = re.search("/[\S]+/",regno)
	if match:
		paths = regno.split('/')
		print (regno)
		course_code = paths[0]
		year_of_study = paths[2]
		app.config['UPLOAD_FOLDER'] = "/".join([app.config.get('UPLOAD_FOLDER'),course_code,year_of_study,'/'])
		regno = paths[1]
  # Check if the file is one of the allowed types/extensions
	if method == "record":
		if pic and allowed_file(pic.filename):
			pic_url = get_url(pic,regno,method)
	elif method == "fromapp":
		if pic and allowed_file(pic):
			pic_url = get_url(pic,regno,method)
		
	# Get student with specific regno
	data = Test.query.filter_by(reg_no=regno).first()
	
	status = 0
	message = ''
	# if student not in db, enter into db
	if not data:
		#(self, name, reg_no, time=None, gps, lac, ci, pic_url)
		test = Test(name, regno, latitude, longitude, lac, ci, pic_url, source, time)
		# for successful connection
		try:
			# add new row to db
			db.session.add(test)
			# save changes
			db.session.commit()
			message = "Record successfully added"
		except:
			db.session.rollback()
			message = "Record not added. Connection unsuccessful"
			status = 1
	# if user in db
	else:
		message = "Student is in database"
		status = 2
	app.config['UPLOAD_FOLDER'] = new_folder
	return (message, status)
	
@app.route('/record/',methods=['POST', 'GET'])
def record():
	create_database()
	#fh = open('imageToSave.jpg',"wb")
	name=''; regno=''; time=None; latitude=0; longitude=0; lac=0; ci=0; pic=None; #gps = 0
	if request.method == 'POST':

		regno=request.form['regno']
		name=request.form['name']
		time=request.form['time']
		#gps=request.files['gps']
		#lac=request.files['lac']
		#ci=request.files['ci']        
		pic=request.files['picture']

		message, status = insert_db(name,regno,time,latitude,longitude,lac,ci,pic,'record')
		return render_template("result.html",msg=message,sts=status)
	#fh.close()
	
def get_contents():
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
	# select all from database
	#rows = Test.query.all()
	rows = get_contents()
	#print contents
	return render_template("list.html",rows=rows)
	
#delete row in db
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
	
'''# delete row in db
@app.route('/delete',methods =['POST'])	
def delete():
	"""Function to delete row in db"""
	# create query for deletion
	delete = Test.query.filter_by(id=2).first()
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
	
'''
if __name__=='__main__':
	# start app
	app.run(debug=True)
	