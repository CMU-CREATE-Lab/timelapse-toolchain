import webapp2

import settings

DEBUG = True

config = {
    'STATIC_DIR': settings.STATIC_DIR,
    'TEMP_UPLOAD_DIR': settings.TEMP_UPLOAD_DIR,
    'PROJECTS_DIR': settings.PROJECTS_DIR,
    'PROJECTS_BASE_URL': settings.PROJECTS_BASE_URL,
}


app = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler='handlers.LandingPageHandler', name='home'),
    webapp2.Route(r'/upload_csv', handler='handlers.UploadHandler', name='upload-csv'),
    webapp2.Route(r'/update_project', handler='handlers.UpdateHandler', name='update-project')
], debug=DEBUG, config=config)


def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='9888')

if __name__ == '__main__':
    main()
