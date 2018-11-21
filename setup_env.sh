#!/usr/bin/env bash
 su -

apt-get update
apt install python3-pip

pip3 install flask
pip3 install flask_restful
pip3 install flask_compress
pip3 install shapely
pip3 install simplekml
pip3 install numpy
pip3 install matplotlib
pip3 install netcdf4
pip3 install scipy
pip3 install numexpr
pip3 install owslib
install psycopg2-binary
pip3 install python3-memcached
pip3 install boto
pip3 install cottoncandy

pip3 install awscli

add-apt-repository -y ppa:ubuntugis/ppa
apt update
apt install gdal-bin python3-gdal

apt-get install apache2
apt-get install apache2-dev
apt-get install libapache2-mod-wsgi-py3
Y
pip3 install mod-wsgi

apt-get update

cd
git clone https://github.com/GeoscienceAustralia/geophys_utils
cd geophys_utils
python3 setup.py install --force

cd /var/www/html
git clone https://github.com/GeoscienceAustralia/geophys_kml_server

echo "<VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        #ServerName www.example.com

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

    	# KML Server Python Flask API under /kml directory alias
    	WSGIDaemonProcess geophys_kml_server_app threads=8
    	WSGIScriptAlias /kml /var/www/html/geophys_kml_server/geophys_kml_server_app.wsgi

    	<Directory geophys_kml_server_app>
            WSGIProcessGroup geophys_kml_server_app
            WSGIApplicationGroup %{GLOBAL}
            Require all denied
    	</Directory>

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with \"a2disconf\".
        #Include conf-available/serve-cgi-bin.conf
</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
" > /etc/apache2/sites-enabled/000-default.conf


export PYTHONPATH=/var/www/html/geophys_kml_server


# Increase the upload and download limits in cottoncandy settings
echo "access_key = False
secret_key = False
endpoint_url = https://s3.amazonaws.com/
verbose_boto = False

[basic]
default_acl = authenticated-read
default_bucket =
mandatory_bucket_prefix =
force_bucket_creation = False
path_separator = /
signature_version =

[upload_settings]
mpu_use_threshold = 2000
mpu_chunksize = 1000
dask_chunksize = 100
min_mpu_size = 5
max_put_size = 50000
max_mpu_size_tb = 50
max_mpu_parts = 100000

[download_settings]
mpd_use_threshold = 1000000
mpd_chunksize = 100000

[extensions]
ccgroup = grp, ccg
ccdataset = arr, dar, rarr, ccd

[gdrive]
secrets = client_secrets.json
credentials = credentials.txt

[encryption]
method = AES
key = False
" > /root/.config/cottoncandy/options.cfg

apachectl restart

