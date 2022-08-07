#!/usr/bin/python3
# upgrade.py

"""
Used to upgrade the installed packages in an environment and save them to requirements file
"""

from __future__ import print_function
import os
import sys
import subprocess


def run_terminal(commands=None, file_object=None):
    """
  This function will run the list of commands supplied to the respective OS terminal/command prompt
  If file_object is passed, the subprocess' output will be written to file
  """
    if commands is None:
        commands = ['ls', '-l']
    try:
        # check python version and run appropriate subprocess function
        if repr(sys.version_info[0]) + repr(sys.version_info[1]) >= '35':  # Python 3.5 and higher
            subprocess.run(commands, stdout=file_object)
        else:
            subprocess.call(commands, stdout=file_object)
    except Exception as err:
        print('Something went wrong: {}'.format(err))


def main():
    # if there is a requirements file
    if os.path.isfile('requirements.txt'):
        file_object = open('requirements.txt', 'r')
        # iterate over all of the lines in file
        for line in file_object:
            package = line.split('=')[0]
            commands = ['pip', 'install', '--upgrade', package]
            # run the terminal, depending on python version
            run_terminal(commands)
        # update pip, if possible
        update = input('Update pip? (y|N) ')
        if update.lower() == 'y':
            run_terminal(['pip', 'install', '--upgrade', 'pip'])
        file_object.close()
    # create/write to requirements file
    with open('requirements.txt', 'w+') as file_object:
        run_terminal(['pip', 'freeze'], file_object)


# boilerplate
if __name__ == '__main__':
    main()
