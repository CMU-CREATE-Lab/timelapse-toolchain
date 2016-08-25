import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir)) # the directory of this file

PROJECTS_DIR = os.path.join(BASE_DIR, 'projects')

STATIC_DIR = os.path.join(BASE_DIR, 'static')

TEMP_UPLOAD_DIR = os.path.join(CURRENT_DIR, 'uploads')

ALLOWED_EXTENSIONS = set(['txt', 'csv'])

