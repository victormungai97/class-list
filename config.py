# config.py
# courtesy of mbithe nzomo(scotch.io/@mbithenzomo)

class Config(object):
	"""Common configurations"""
	#Put any configurations common across all environments
	
class DevelopmentConfig(Config):
	"""Development configurations"""
	
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
	'F17':"Electrical Engineering",
	'F16':"Civil Engineering"
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