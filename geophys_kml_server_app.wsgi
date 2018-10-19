'''
Created on 9 Oct. 2018

@author: Andrew Turner & Alex Ip, Geoscience Australia
'''
import sys
import logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/var/www/html/geophys_kml_server')

from geophys_kml_server.app import app as application