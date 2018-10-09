'''
Created on 7 Sep. 2018

@author: Andrew Turner & Alex Ip, Geoscience Australia
'''
import sys
import os
from flask import Flask
from flask_restful import Api
from flask_compress import Compress
from geophys_kml_server import settings, RestfulKMLQuery, RestfulImageQuery, image_url_path
import logging

root_logger = logging.getLogger()

if settings['global_settings']['debug']:
    root_logger.setLevel(logging.DEBUG)
else:
    root_logger.setLevel(logging.INFO)
root_logger.debug('Root root_logger {} set to level {}'.format(root_logger.name, root_logger.level))

# Compression defaults
COMPRESS_MIMETYPES = ['application/vnd.google-earth.kml+xml',
                      'text/html', 
                      'text/css', 
                      'text/xml', 
                      'application/json', 
                      'application/javascript'
                      ]
DEFAULT_COMPRESS_LEVEL = 6
DEFAULT_COMPRESS_MIN_SIZE = 2000 # Don't bother compressing small KML responses

# Set proxy for outgoing traffic (used for testing with Fiddler)
http_proxy = settings['global_settings'].get('http_proxy')
if http_proxy:
    root_logger.info('Setting proxy to {}'.format(http_proxy))
    os.environ['http_proxy'] = http_proxy

def configure_app_compression(app):
    '''
    Helper function to set app config parameters
    '''
    app.config['COMPRESS_MIMETYPES'] = COMPRESS_MIMETYPES 
    app.config['COMPRESS_LEVEL'] = settings['global_settings'].get('compress_level') or DEFAULT_COMPRESS_LEVEL 
    app.config['COMPRESS_MIN_SIZE'] = settings['global_settings'].get('compress_min_size') or DEFAULT_COMPRESS_MIN_SIZE 

app = Flask('geophys_kml_server') # Note hard-coded module name

api = Api(app)
api.add_resource(RestfulKMLQuery, '/<string:dataset_type>/query')

if settings['global_settings']['cache_images']:
    api.add_resource(RestfulImageQuery, image_url_path)

if settings['global_settings']['http_compression']:
    configure_app_compression(app)
    Compress(app)

if __name__ == '__main__':
    # Setup logging handlers if required
    if not root_logger.handlers:
        # Set handler for root root_logger to standard output
        console_handler = logging.StreamHandler(sys.stdout)
        #console_handler.setLevel(logging.INFO)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    app.run(host=settings['global_settings'].get('host'), 
            debug=settings['global_settings']['debug'])

