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
    DocumentRoot /create-maps /var/www/create-maps/documents
    <Directory /var/www/create-maps/documents>
      Order allow,deny
      Allow from all
    </Directory>

    WSGIDaemonProcess create-maps processes=2 threads=15 display-name=%{GROUP}
    WSGIProcessGroup create-maps

    WSGIScriptAlias /scripts /var/www/create-maps/wsgi-scripts/main.py

    <Directory /var/www/create-maps/wsgi-scripts>
      Order allow,deny
      Allow from all
    </Directory>
```

# Setting webapp2 development environment

## Install requirements

```
pip install -r requirements.txt
```

## Update settings and create directory structure

Edit wsgi_scripts/settings.py to setup the input and output folders.
```
cd timelapse_tchain/
mkdir tmp
```

## Run webapp2's development server
Access the page at www.example.com/
and the scripts at www.example.com/scripts
```

```
