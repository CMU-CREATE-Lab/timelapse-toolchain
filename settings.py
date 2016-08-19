import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, 'static')

TEMP_UPLOAD_DIR = os.path.join(BASE_DIR, 'tmp')

PROJECTS_DIR = os.path.join(BASE_DIR, 'projects')

PROJECTS_BASE_URL = '/projects'
