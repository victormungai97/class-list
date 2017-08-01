import os
import sys
import site

# Add virtualenv site packages
site.addsitedir('/home/attendance/.virtualenvs/attendance/lib/python3.5/site-packages')

sys.path.insert(0, '/var/www/html/class-list')

# Fired up virtualenv before include application
activate_this = '/home/attendance/.virtualenvs/attendance/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))


from app import create_app

config_name = os.getenv('FLASK_CONFIG')
if not config_name:
	config_name = 'development'
application = create_app(config_name)

