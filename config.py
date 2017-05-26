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