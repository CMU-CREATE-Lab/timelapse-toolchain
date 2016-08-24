import os

SCRIPTS_DIR = 'scripts'

HTML_DIR = 'html'

PROJECTS_DIR = 'projects'

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir)) # the directory of this file

PROJECTS_DIR = os.path.join(BASE_DIR, HTML_DIR, PROJECTS_DIR)

#STATIC_DIR = os.path.join(BASE_DIR, HTML_DIR)
STATIC_DIR = ''

STATIC_CSS_DIR = os.path.join(BASE_DIR, HTML_DIR, 'css')

STATIC_JS_DIR = os.path.join(BASE_DIR, HTML_DIR, 'js')

TEMP_UPLOAD_DIR = os.path.join(CURRENT_DIR, 'uploads')

ALLOWED_EXTENSIONS = set(['txt', 'csv'])

#STATIC_DIR = os.path.join(BASE_DIR, os.pardir)



#TEMPLATES_DIR = os.path.join(CURRENT_DIR, 'templates')