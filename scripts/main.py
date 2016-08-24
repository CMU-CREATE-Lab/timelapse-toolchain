import sys, os
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)
    

from flask import Flask, request, redirect, render_template, url_for, flash, get_flashed_messages
from werkzeug.utils import secure_filename
import os, re, errno, ast, json
import settings, db
from builder import generate_binary, generate_params, write_html, build_zip, get_fmt_fn



app = Flask(__name__)
app.secret_key = 'createx%8y#-t@#+ec7sbnoh^3s%+z8=zj%of8*9+vtu4y-=pkhxm7maps'
app.debug = True

@app.route("/")
def hello():
	return "Hello World"

@app.route('/create/', methods=['POST'])
def create_project():
	params = dict()
	params['email'] = request.form['email']
	params['title'] = request.form['project_title']
	project_id = request.form['project_id']

	if re.match(r'[^a-z\d\-]', project_id):
		flash('Invalid project id. ')
		return redirect(url_for('display_error'))		
	params['project_id'] = project_id
	project_dir = os.path.join(settings.PROJECTS_DIR, project_id)

	if 'csv_file' not in request.files:
		flash('No file uploaded')
		return redirect(url_for('display_error'))

	file = request.files['csv_file']

	if file.filename[-3:].lower() not in settings.ALLOWED_EXTENSIONS:
		return redirect(url_for('display_error', error='Invalid extension or file type'))

	filename = secure_filename(file.filename)
	filepath = os.path.join(settings.TEMP_UPLOAD_DIR, filename)
	file.save(filepath)

	try:
		os.makedirs(project_dir)
	except OSError as e:
		if e.errno == errno.EEXIST:
			flash('Project already exists.')
			return redirect(url_for('display_error'))
	except:
		raise

	# create project
	data_shape = generate_binary(filepath, project_dir + '/data.bin')
	params.update(data_shape)
	final_params = generate_params(params)
	write_html(final_params, project_dir + '/index.html')
	db.store(final_params)
	return redirect(url_for('edit_project', project_id=project_id))

@app.route('/edit/<project_id>')
def edit_project(project_id):
	params = db.retrieve(project_id)
	project_url = request.url_root[:request.url_root[:-1].rfind('/')] + '/timelapse-toolchain/html/projects/' + project_id
	return render_template('edit.html', STATIC_DIR=settings.STATIC_DIR, PROJECT_URL=project_url, **params)


@app.route('/update/', methods=['PUT'])
def update_project():
	params = request.get_json()
	project = request.referrer.split('/')[-1]
	params['project_id'] = project
	span = params['timeSlider']['endTime'] - params['timeSlider']['startTime']
	#print 'span:', span
	params['timeSlider']['timeFormat'] = get_fmt_fn(span)
	#print 'time format', params['timeFormat']
	project_dir = os.path.join(settings.PROJECTS_DIR, project)
	write_html(params, project_dir + '/index.html')
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
	return render_template('error.html')




if __name__ == "__main__":
	app.run()