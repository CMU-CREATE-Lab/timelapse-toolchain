import sys, os
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)
    

from flask import Flask, request, redirect, render_template, url_for, flash, get_flashed_messages
from werkzeug.utils import secure_filename
import os, re, errno, ast, json
import settings, db, builder


app = Flask(__name__)
app.secret_key = 'createx%8y#-t@#+ec7sbnoh^3s%+z8=zj%of8*9+vtu4y-=pkhxm7maps'
app.debug = True

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
	except ValueError as e:
		flash(e)
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
	return render_template('edit.html', PROJECT_URL=project_url, **params)


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




if __name__ == "__main__":
	app.run()