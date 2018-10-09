'''
Created on 7 Sep. 2018

@author: Andrew Turner & Alex Ip, Geoscience Australia
'''
import os
import sys
import yaml
import logging

# Read settings before doing any more imports
settings = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                            'geophys_kml_server_settings.yml')))
#print('settings = {}'.format(settings))
#print('settings: {}'.format(yaml.safe_dump(settings)))

logger = logging.getLogger(__name__)

if settings['global_settings']['debug']:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
logger.debug('Logger {} set to level {}'.format(logger.name, logger.level))

from ._restful_image_cache import RestfulImageQuery, cache_image_file, image_url_path
from ._restful_kml_query import RestfulKMLQuery
