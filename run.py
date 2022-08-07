# run.py

import os

from app import create_app
from app.database import db_session
from app.models import User, Lecturer, Student, Class, Programme

config_name = None
try:
    # Here, we obtain environment variables from a settings file
    # Useful for running inside an IDE
    from settings import get_env_variable

    config_name = get_env_variable['FLASK_ENV']
except (ImportError, Exception):
    # Here, we obtain environment variables directly from computer
    # Useful for running in a terminal
    try:
        config_name = os.getenv('FLASK_ENV')
    except BaseException as err:
        print(err)

if not config_name:
    config_name = 'production'
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """
    Configures a "shell context", which is a list of other symbols to pre-import in flask shell.
    This helps us to work with db entities without having to import them.
    When flask shell command runs, it'll invoke this function & register the items returned by it in the shell session.
    The dictionary keys are the names under which the symbols are saved in shell
    """
    return {'db': db_session, 'User': User, 'Lecturer': Lecturer, 'Student': Student, 'Class': Class,
            'Programme': Programme, }


if __name__ == '__main__':
    app.run(host='0.0.0')
