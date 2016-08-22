import webapp2
import os
import sys
#site.addsitedir(os.path.dirname(__file__))
sys.stdout = sys.stderr
print os.path.dirname(__file__)

import settings

DEBUG = True

config = {
    'STATIC_DIR': settings.STATIC_DIR,
    'TEMP_UPLOAD_DIR': settings.TEMP_UPLOAD_DIR,
    'PROJECTS_DIR': settings.PROJECTS_DIR,
    'PROJECTS_BASE_URL': settings.PROJECTS_BASE_URL,
}


app = webapp2.WSGIApplication([
    webapp2.Route(r'/upload_csv', handler='handlers.UploadHandler', name='upload-csv'),
    webapp2.Route(r'/update_project', handler='handlers.UpdateHandler', name='update-project'),
    webapp2.Route(r'/error', handler='handlers.ErrorHandler', name='error')
], debug=DEBUG, config=config)


