# geophys\_kml\_server - Dynamic KML Server for netCDF Encoded Geophysics Data
The geophys\_kml\_server Python module implements a Flask KML server for geophysics data accessed via web services or from netCDF files.

This application requires the geophys\_utils Python libraries available at <https://github.com/GeoscienceAustralia/geophys_utils>.

Details on the netCDF encoding for point and line data can be viewed at <https://docs.google.com/document/d/1C-SsT1vOcAaPT_4jdY1S_NjUjbk-WbUjb1FCw7uPrxw/edit?usp=sharing>

Feedback, suggestions or contributions will be gratefully accepted.

## License
The content of this repository is licensed for use under the [Apache 2.0 License](http://www.apache.org/licenses/LICENSE-2.0). See the [license deed](https://github.com/GeoscienceAustralia/geophys_utils/blob/master/LICENSE) for full details.

## Contacts
**Geoscience Australia**  
*Publisher*  
<http://www.ga.gov.au>  
<clientservices@ga.gov.au>  

**Alex Ip**  
*Author*  
<alex.ip@ga.gov.au>  
<https://orcid.org/0000-0001-8937-8904>

**Andrew Turner**  
*Author*  
<andrew.turner@ga.gov.au>  
<https://orcid.org/0000-0001-5085-8783>

## Deployment Instructions
After installing Apache and all required Python3 dependencies, perform the following tasks as the root user:

**Clone the geophys_utils repo (https://github.com/GeoscienceAustralia/geophys_utils) and run the setup.py script to install the geophys_utils dependency**

        cd
        git clone https://github.com/GeoscienceAustralia/geophys_utils
        cd geophys_utils
        python setup.py install

**Clone this geophys_kml_server repo (https://github.com/GeoscienceAustralia/geophys_kml_server) under /var/www/html**

        cd /var/www/html
        git clone https://github.com/GeoscienceAustralia/geophys_kml_server

**Edit settings file /var/www/html/geophys_kml_server/geophys_kml_server_settings.yml for Linux environment**

        cache_root_dir: /tmp

**Ensure Apache has mod_wsgi installed**

        sudo a2enmod wsgi

**Add the following lines to Apache configuration file (usually /etc/apache2/sites-available/000-default.conf):**

        # KML Server Python Flask API under /kml directory alias
        WSGIDaemonProcess geophys_kml_server_app threads=8
        WSGIScriptAlias /kml /var/www/html/geophys_kml_server/geophys_kml_server_app.wsgi

        <Directory geophys_kml_server_app>
            WSGIProcessGroup geophys_kml_server_app
            WSGIApplicationGroup %{GLOBAL}
            Require all denied
        </Directory>

**Reload Apache**

        sudo service apache2 reload
