'''
Created on 7 Sep. 2018

@author: Andrew Turner & Alex Ip, Geoscience Australia
'''
import os
import re
import tempfile
import requests
from flask import request, make_response, send_from_directory
from flask_restful import Resource


from geophys_kml_server import settings
import logging
#from pprint import pformat

logger = logging.getLogger(__name__)
    
if settings['global_settings']['debug']:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
logger.debug('Logger {} set to level {}'.format(logger.name, logger.level))

# This is used to define the path for the RESTful API, and also to set the URL prefix in cache_image_file()
image_url_path = '/images/<string:dataset_type>'

cache_dir = os.path.join((settings['global_settings'].get('cache_root_dir') or
                          tempfile.gettempdir()),
                          'kml_server_cache'
                          )
os.makedirs(cache_dir, exist_ok=True)




class RestfulImageQuery(Resource):
    '''
    RestfulImageQuery Resource subclass for RESTful API
    '''
    CONTENT_TYPE = 'image/png'

    #===========================================================================
    # def __init__(self):
    #     '''
    #     RestfulImageQuery Constructor
    #     '''
    #     super(RestfulImageQuery, self).__init__()
    #===========================================================================
        
            
            
    def get(self, dataset_type):
        '''
        get method for RESTful API to retrieve cached images
        Needs to have "?image=<image_name>" parameter set
        '''
        logger.debug('dataset_type: {}'.format(dataset_type))
        
        image_dir = os.path.join(cache_dir, dataset_type)
        
        #=======================================================================
        # dataset_settings = settings['dataset_settings'].get(dataset_type)
        # 
        # #TODO: Handle this more gracefully
        # assert dataset_settings, 'Invalid dataset type "{}"'.format(dataset_type)
        #=======================================================================
        image_basename = request.args.get('image')
        if not image_basename:
            #TODO: Craft a proper response for bad query
            logger.debug('image parameter not provided')
            return
        
        image_path = os.path.join(image_dir, image_basename)
        logger.debug('image_path: {}'.format(image_path))
        image_response = mc.get(image_path)
        if os.path.isfile(image_path):
            image_response = send_from_directory(image_dir, image_basename)
            logger.debug('image_response: {}'.format(image_response))
            response = make_response(image_response)
            response.headers['content-type'] = RestfulImageQuery.CONTENT_TYPE
            return response
        else:
            #TODO: Craft a proper response for bad query - 404 perhaps?
            logger.debug('Image file {} does not exist'.format(image_path))
            return
        
        
def cache_image_file(dataset_type, image_basename, image_source_url):
    '''
    Function to retrieve image from image_source_url, and save it into file
    @param dataset_type: String indicating dataset type - used in creating URL path
    @param image_basename: Base name for image file
    @param image_source_url: Source URL for image (probably WMS query)
    @return cached_image_url_path: URL path to cached image. Will be appended to server string
    '''
    logger.debug('dataset_type: {}'.format(dataset_type))

    image_dir = os.path.join(cache_dir, dataset_type)

    image_path = os.path.join(image_dir, image_basename)
    response = requests.get(image_source_url, stream=True)

    if settings['global_settings']['memchaced_endpoint']:
        response = requests.get(image_source_url, stream=True)

        print(image_path)
    else:

        if not os.path.isfile(image_path):
            os.makedirs(image_dir, exist_ok=True)
            logger.debug('Saving image {} from {}'.format(image_path, image_source_url))
            response = requests.get(image_source_url, stream=True)
            if response.status_code == 200:
                with open(image_path, 'wb') as image_file:
                    for chunk in response:
                        image_file.write(chunk)

            else:
                logger.debug('response.status_code {}'.format(response.status_code))
                return

    cached_image_url_path = re.sub('<.+>', dataset_type, image_url_path) + '?image=' + image_basename
    logger.debug('cached_image_url_path: {}'.format(cached_image_url_path))

    return cached_image_url_path


