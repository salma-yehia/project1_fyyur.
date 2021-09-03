import os
SECRET_KEY = os.urandom(32)
WTF_CSRF_ENABLED = False
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://salma:salma871999@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
