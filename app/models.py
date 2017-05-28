from time import *
from app import db

'''Module contains the models for the project'''
	
class Table(db.Model):
	'''Class that models basic student details'''
	__tablename__ = 'Details'
	id = db.Column('id', db.Integer, primary_key=True)
	name = db.Column('name', db.String(60), unique=True)
	reg_no = db.Column('regno', db.Unicode(60), unique=True)
	course = db.Column('course', db.String(60))
	# 1. Point to Test and Basic classes and load multiple tests and basics
	# 2. backref creates a virtual property in Test class that can be used to access student's details
	# 3. lazy defines how to load data 
	reg_nos = db.relationship('Test',backref='details',lazy='dynamic')
	reg_nos1 = db.relationship('Basic',backref='basic',lazy='dynamic')
	
	def __init__(self, name, reg_no, course):
		'''Function that adds basic details of students to table'''
		self.name = name
		self.reg_no = reg_no
		self.course = course
		
	def __repr__(self):
		return "<Student %r>" % self.name
	
class Test(db.Model):
	'''Class that models students table'''
	__tablename__ = 'students' # set table name
	id = db.Column('id', db.Integer, primary_key=True)
	name = db.Column('name',db.String(60))
	# create foreign key pointing to details table
	reg_no = db.Column('regno',db.Unicode(60),db.ForeignKey('Details.regno'))
	course = db.Column('course', db.String(60))
	latitude = db.Column('latitude',db.Float)
	longitude = db.Column('longitude',db.Float)
	lac = db.Column('lac',db.Float)
	ci = db.Column('ci',db.Float)
	pic_url = db.Column('picture_url',db.String(100))
	time = db.Column('time',db.Unicode(60))
	source = db.Column('source',db.Unicode(100))
	
	def __init__(self, name, reg_no, lat, longi, lac, ci, pic_url, source, course, time = None):
		'''Function initializes class and is used to add user to db'''
		self.name = name
		self.reg_no = reg_no
		self.course = course
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

		
class Basic(db.Model):
	'''Class that contains basic sign in details'''
	__tablename__= "Basic_Details"
	id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
	name = db.Column('name',db.String(60))
	reg_no = db.Column('regno',db.Unicode(60),db.ForeignKey('Details.regno'))
	course = db.Column('course', db.String(60))
	pic_url = db.Column('picture_url',db.String(100))
	
	def __init__(self, name, reg_no, pic_url, course):
		'''Function that adds basic sign in details of students to table'''
		self.name = name
		self.reg_no = reg_no
		self.pic_url = pic_url
		self.course = course
		
	def __repr__(self):
		return "<Student %r>" % self.name

class Suggestion(db.Model):
	'''Class that stores received suggestions'''
	__tablename__="Suggestions"
	id = db.Column('id', db.Integer, primary_key=True)
	choice = db.Column("title",db.String(60))
	message = db.Column("message",db.String(150))
	
	def __init__(self, title, msg):
		'''Function that receives and saves suggestions'''
		self.choice = title
		self.message = msg
		
	def __repr__(self):
		return "<Suggestion %r>" % self.message