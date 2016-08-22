import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, '..')

TEMP_UPLOAD_DIR = os.path.join(BASE_DIR, 'tmp')

PROJECTS_BASE_URL = '/projects'

PROJECTS_DIR = '/var/www/create-maps/documents/projects' # os.path.join(BASE_DIR, '..' + PROJECTS_BASE_URL)

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

