# config.py

class Config(object):
	"""Common configurations"""
	#Put any configurations common across all environments
	SESSION_COOKIE_NAME="session"
	TESTING=False
	
class DevelopmentConfig(Config):
	"""Development configurations"""
	
	TESTING=True
	DEBUG=True # activates debug mode on app
	SQLALCHEMY_ECHO=True # allows SQLAlchemy to log errors
	SQLALCHEMY_TRACK_MODIFICATIONS=True # allows SQLAlchemy to track changes while running
	
class ProductionConfig(Config):
	"""Production configurations"""
	DEBUG=False
	SQLALCHEMY_TRACK_MODIFICATIONS=False
	
app_config = {
	'development':DevelopmentConfig,
	'production':ProductionConfig
}

courses = {
	'F17':"B.sc. ( Electrical And Electronic Engineering)",
	'F16':"B.sc. (Civil Engineering)",
	'F18':"B.sc. (Mechanical Engineering)",
	'F19':"B.sc. (Geospatial Engineering)",
	'F21':"B.sc. (Environmental and Biosystems Engineering)",
	'B04':"Bachelor of Real Estate",
	'B66':"Bachelor Of Quantity Surveying",
	'B76':"Bachelor Of Construction Management",
	'B65':"B.A. (urban & Regional Planning)"
}

def myHelper(filename, message):
	'''Function to write into database'''
	import sqlite3
	conn = sqlite3.connect(filename)
	cursor = conn.cursor()
	create = "CREATE TABLE IF NOT EXISTS Logs (Time varchar(60), Message varchar(60))"
	cursor.execute(create)
	conn.commit()
	from datetime import datetime
	current_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S') # current time
	query = "INSERT INTO Logs VALUES ('{0}','{1}')".format(current_time, message)
	cursor.execute(query)
	conn.commit()
	cursor.close()
	conn.close()