import sys, os
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)
    

from flask import Flask, request, redirect, render_template, url_for, flash, get_flashed_messages
from werkzeug.utils import secure_filename
import os, re, errno, ast, json, shutil
import settings, db, builder


app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
app.debug = settings.DEBUG_MODE

sentry = None
if not app.debug:
	from raven.contrib.flask import Sentry
	sentry = Sentry(app, dsn='https://4ee36d6a040e40ee978713b57205782e:2db8c0a1f3844bc0bc32c2f33cc15f01@sentry.io/94695')

required_paths = ['projects', 'scripts/db', 'scripts/uploads', 'failed-projects']

for path in required_paths:
	if not os.path.exists(path):
		raise Exception('Required directory ' + path + ' does not exist. Please verify installation.')
@app.route("/")
def home():
	return render_template('home.html')
	# return "Hello World"

@app.route('/create/', methods=['POST'])
def create_project():
	params = dict()
	params['email'] = request.form['email']
	params['title'] = request.form['project_title']
	project_id = request.form['project_id']

	if re.match(r'[^a-z\d\-]', project_id):
		flash('Invalid project id. ')
		return render_template('home.html')	
	params['project_id'] = project_id
	project_dir = os.path.join(settings.PROJECTS_DIR, project_id)

	if 'csv_file' not in request.files:
		flash('No file uploaded')
		return redirect(url_for('home'))

	file = request.files['csv_file']

	if file.filename[-3:].lower() not in settings.ALLOWED_EXTENSIONS:
		flash('Invalid file extension or file type')
		return redirect(url_for('home'))

	filename = secure_filename(file.filename)
	filepath = os.path.join(settings.TEMP_UPLOAD_DIR, filename)
	file.save(filepath)

	try:
		os.makedirs(project_dir)
	except OSError as e:
		if e.errno == errno.EEXIST:
			flash('Project already exists.')
			return redirect(url_for('home'))
	except:
		raise

	# create project
	try:
		data_shape = builder.generate_binary(filepath, project_id)
	except (ValueError, RuntimeError, Exception) as e:
		if isinstance(e, ValueError):
			message = repr(e)
		else: 
			if sentry:
				sentry.captureException()
			message = "There was an error processing your uploaded data."
			message += "Please review the file upload specifications. (Details: " + repr(e) + ")"
		flash(message)
		if not os.path.exists(os.path.join("failed-projects", filename)):
			shutil.move(filepath, "failed-projects") # if the project CSV isn't already in the failed projects folder...
		shutil.rmtree(project_dir, ignore_errors=True)
		return redirect(url_for('home'))
	
	params.update(data_shape)
	final_params = builder.generate_params(params)
	builder.write_html(final_params)
	db.store(final_params)
	return redirect(url_for('edit_project', project_id=project_id))

@app.route('/edit/<project_id>')
def edit_project(project_id):
	params = db.retrieve(project_id)
	project_url = 'projects/' + project_id
	return render_template('edit.html', PROJECT_ID=project_id, PROJECT_URL=project_url, **params)


@app.route('/update/<project_id>', methods=['PUT'])
def update_project(project_id):
	params = request.get_json()
	params['project_id'] = project_id
	span = params['timeSlider']['endTime'] - params['timeSlider']['startTime']
	params['timeSlider']['timeFormat'] = builder.get_fmt_fn(span)
	project_dir = os.path.join(settings.PROJECTS_DIR, project_id)
	builder.write_html(params)
	builder.build_zip(project_id)
	db.store(params)
	if True:
		return 'success', 200
	else:
		return 'error', 400

@app.route('/error')
def display_error():
	messages = get_flashed_messages()
	if messages:
		for message in messages:
			print message
	return redirect(url_for('home'))

# Serve static files
# Only for local-development
if app.debug:
	@app.route('/projects/<project_id>/')
	def serve_project(project_id):
	    return serve_project_file(project_id, 'index.html')

	@app.route('/projects/<project_id>/<static_file>')
	def serve_project_file(project_id, static_file):
	    import flask
	    # send_static_file will guess the correct MIME type
	    project_dir = os.path.join(settings.PROJECTS_DIR, project_id)
	    return flask.send_from_directory(project_dir, static_file)


if __name__ == "__main__":
	app.run()
