import os
import errno
import re

import webapp2


class ProjectIDAlreadyInUse(Exception):
        """Raise when trying to create a project with an ID already in use"""


class Project(object):
    def __init__(self, _id):
        self.id = _id

    @classmethod
    def create(cls, project_id):
        assert cls.is_valid_project_id(project_id)
        app = webapp2.get_app()
        project_dir = os.path.join(app.config.get('PROJECTS_DIR'), project_id)
        try:
            os.mkdir(project_dir)
        except OSError, e:
            if e.errno == errno.EEXIST:
                raise ProjectIDAlreadyInUse("Project ID already in use")
            else:
                raise
        # Create initial directory layout
        return cls(project_id)

    @staticmethod
    def is_valid_project_id(project_id):
        return re.match(r'^[-a-zA-Z0-9]+$', project_id) is not None
