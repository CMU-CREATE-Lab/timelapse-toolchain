# timelapse-toolchain

a lightweight tool to empower non-technical users to create embedable timelapse visualizations

# Configure Apache2 to use WSGI
Webapp2 is a simple Python WSGI webb application framework. To use with Apache, the mod_wsgi module must first be configured with Apache. Install and enable the mod_wsgi module (roughly following the instructions at https://modwsgi.readthedocs.io/en/develop/user-guides/quick-installation-guide.html).

After downloading / compiling mod_wsgi.so, create a file at /etc/apache2/mods-available/wsgi.load with the following line:
```
LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
```
Then enable the module by running the commands:
```
sudo a2enmod mod-wsgi
sudo /etc/init.d/apache2 restart
```

Next, add the following lines to the appropriate Apache virtual host configuration file:
```
Alias "/create-maps/projects" "C:/users/markegge/work/timelapse-toolchain/projects"
WSGIScriptAlias /create-maps "C:/users/markegge/work/timelapse-toolchain/create-maps.wsgi"

<Directory "C:/users/markegge/work/timelapse-toolchain">
Require all granted # Apache 2.4
Order allow,deny # Apache 2.2
Allow from all
</Directory>
```

# Configure the web application

## Download, Set Permissions, Install requirements
```
cd /var/www
sudo git clone https://github.com/CMU-CREATE-Lab/timelapse-toolchain.git
cd timelapse-toolchain
git checkout flask
sudo pip install -r requirements.txt
```
## Modify create-maps.wsgi to specify application path
Change the `path=` to correspond to the location of scripts. E.g. create-maps.wsgi:
```
import sys
path = r'/var/www/timelapse-toolchain/scripts'
if path not in sys.path:
        sys.path.insert(0, path)
from create_maps import app as application
```
## Create database and uploads folder

Script checks if sqlite database (projects.db) exists. If not, creates.
```
mkdir projects
sudo chown YOURUSERNAME:www-data projects
cd scripts/
python db.py
sudo chwon YOURUSERNAMNE:www-data projects.db
mkdir uploads
sudo chown YOURUSERNAME:www-data uploads
```

## Run Flask's development server
Windows:
```
set FLASK_DEBUG=1
set FLASK_APP=main.py
python -m flask run
```
*nix:
```
export FLASK_DEBUG=1
export FLASK_APP=main.py
python -m flask run
```

# Testing
```
curl -X POST -F 'project_title=My Project' -F 'email=ma4k@a.com' -F 'project_id=marks-project' -F file=@example-x-y-time.csv localhost:5000/create/
curl -X GET localhost:5000/edit/marks-project
```