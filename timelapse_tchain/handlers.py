import os, ast, json
from email.utils import parseaddr

import webapp2
from webapp2_extras import jinja2

import models


class LandingPageHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        rendered_template = self.jinja2.render_template(_template, **context)
        self.response.write(rendered_template)

    def get(self):
        self.render_response('index.html')


class UploadHandler(webapp2.RequestHandler):
    def post(self):
        # Validate form fields
        errors = self.validate_form()
        # If invalid form, redirect to landing with error details
        if errors:
            return self.redirect_to('home', errors='.'.join(errors))
        # Create project
        try:
            project_name = self.request.POST['project_name']
            project = models.Project.create(project_name)
        except models.ProjectIDAlreadyInUse:
            return self.redirect_to(
                    'home', errors='Project name already in use')
        # Write CSV file to temporary upload folder
        self.save_csv(self.request.POST['csv_file'], project.id)
        # Launch csv2dotmap task
        self.build_project(project.id)
        # Redirect to dotmap view page
        project_url = '%s/%s' % (
             self.app.config.get('PROJECTS_BASE_URL'), project.id
        )
        return self.redirect(project_url)

    def validate_form(self):
        # Check form contains all required fields
        required_fields = ['csv_file', 'project_name', 'email']
        missing_fields = [
            f for f in required_fields if f not in self.request.POST]
        errors = []
        if missing_fields:
            errors = ['Missing required fields: %s' % ','.join(missing_fields)]
        if not errors:
            # Check project-id is valid
            project_id = self.request.POST['project_name']
            if not models.Project.is_valid_project_id(project_id):
                errors.append('Invalid project name')
            # Check email is valid
            email = self.request.POST['email']
            parsed_email = parseaddr(email)[1]
            if '@' not in parsed_email or '.' not in parsed_email:
                errors.append('Invalid email address')
        return errors

    def save_csv(self, csv_field, project_id):
        assert csv_field.file is not None
        # TODO: Check if we want to limit the number of lines / filesize
        MAX_LINES = 10 ** 9
        line_count = 0
        out_dir = self.app.config.get('TEMP_UPLOAD_DIR')
        out_file = open(os.path.join(out_dir, '%s.csv' % project_id), 'w')
        # Reading  line by line, but maybe chunks could be more efficient.
        while line_count < MAX_LINES:
            line = csv_field.file.readline()
            if not line:
                break
            out_file.write(line)
            line_count += 1
        out_file.close()

    def build_project(self, project_id):
        # TODO: Use celery
        from csv_to_zip import main as generate_dotmap

        input_file = '%s.csv' % project_id
        input_path = os.path.join(
            self.app.config.get('TEMP_UPLOAD_DIR'), input_file)
        output_dir = os.path.join(
            self.app.config.get('PROJECTS_DIR'), project_id)

        generate_dotmap(input_path, output_dir)
class UpdateHandler(webapp2.RequestHandler):
    def post(self):
        params = self.request.body
        params = params.replace('true', 'True')
        params = params.replace('false', 'False')
        params = dict(ast.literal_eval(params))
        print params
        
        #return webapp2.Response().set_status(200)
        if True:
            self.response.set_status(200)
        else:
            self.response.set_status(400)
