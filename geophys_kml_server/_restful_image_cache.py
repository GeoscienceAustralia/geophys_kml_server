'''
Created on 7 Sep. 2018

@author: Andrew Turner & Alex Ip, Geoscience Australia
'''
import os
import re
import tempfile
import requests
from flask import request, send_file
from flask_restful import Resource
from io import BytesIO


import boto3

from geophys_kml_server import settings
import logging
#from pprint import pformat

logger = logging.getLogger(__name__)
    
# try:
#     import memcache
# except ModuleNotFoundError:
#     logger.warning('Unable to import memcache. AWS-specific functionality will not be enabled')
#     memcache = None

if settings['global_settings']['debug']:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
logger.debug('Logger {} set to level {}'.format(logger.name, logger.level))

# This is used to define the path for the RESTful API, and also to set the URL prefix in cache_image_file()
image_url_path = '/images/<string:dataset_type>'

print("HERE")
print(settings['global_settings'].get('cache_root_dir'))
print(tempfile.gettempdir())

# cache_dir = os.path.join((settings['global_settings'].get('cache_root_dir') or tempfile.gettempdir()),
#                          '/tmp/kml_server_cache/')
cache_dir = 'kml_server_cache'
print(cache_dir)
#os.makedirs(cache_dir, exist_ok=True)




class RestfulImageQuery(Resource):
    '''
    RestfulImageQuery Resource subclass for RESTful API
    '''
    CONTENT_TYPE = 'image/png'

    def __init__(self):
        '''
        RestfulImageQuery Constructor
        '''
        super(RestfulImageQuery, self).__init__()
        
        # if memcache is not None and settings['global_settings'].get('memcached_endpoint') is not None:
        #     self.memcached_connection = memcache.Client([settings['global_settings']['memcached_endpoint']], debug=0)
        # else:
        #     self.memcached_connection = None

        
            
            
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
        
        # if self.memcached_connection:
        #     #TODO: Finish implementing memcached to HTML here
        #     png_cache_key = os.path.join(image_dir, image_basename)
        #     png_object = self.memcached_connection.get(png_cache_key)
        #     if png_object is not None:
        #         buffer = BytesIO()
        #         buffer.write(png_object)
        #         buffer.seek(0)
        #         return send_file(buffer,
        #                          attachment_filename=image_basename,
        #                          mimetype=RestfulImageQuery.CONTENT_TYPE
        #                          )
        #     else:
        #         #TODO: Craft a proper response for bad query - 404 perhaps?
        #         logger.debug('Image key {} does not exist'.format(image_path))
        #         return
        
        if os.path.isfile(image_path):
            return send_file(image_path,
                             attachment_filename=image_basename,
                             mimetype=RestfulImageQuery.CONTENT_TYPE
                             )
        else:
            #TODO: Craft a proper response for bad query - 404 perhaps?
            logger.debug('Image file {} does not exist'.format(image_path))
            return


def cache_image_file(dataset_type, image_basename, image_source_url, s3_bucket_name=None, s3_key_name=None):  #, memcached_connection=None):
    '''
    Function to retrieve image from image_source_url, and save it into file
    @param dataset_type: String indicating dataset type - used in creating URL path
    @param image_basename: Base name for image file
    @param image_source_url: Source URL for image (probably WMS query)
    @return cached_image_url_path: URL path to cached image. Will be appended to server string
    '''
    def get_image_buffer(image_source_url):
        '''
        Helper function to return an in-memory buffer containing the requested image, or None for failure
        '''
        buffer = None
        logger.debug('Retrieving image from {}'.format(image_source_url))
        response = requests.get(image_source_url, stream=True)
        if response.status_code == 200:
            buffer = BytesIO()
            
            for chunk in response:
                buffer.write(chunk)
                    
            buffer.seek(0)
            
        return response.status_code, buffer

    # logger.debug("<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>")
    # logger.debug('dataset_type: {}'.format(dataset_type))
    #
    image_dir = os.path.join(cache_dir, dataset_type)
    # logger.debug('image dir: {}'.format(image_dir))
    image_path = os.path.join(dataset_type, image_basename)
    # key = os.path.join(dataset_type, image_basename)
    # logger.debug('image_path: {}'.format(image_path))
    # #s3_key_name = "{0}/{1}".format(s3_key_name, image_basename)
    # #logger.debug('s3_key_name: {}'.format(s3_key_name))
    # logger.debug('s3_bucket_name: {}'.format(s3_bucket_name))
    # if s3_bucket_name is not None:
    #
    #     status_code, buffer = get_image_buffer(image_source_url)
    #     logger.debug('status_code: {}'.format(status_code))
    #
    #     # logger.debug('buffer: {}'.format(buffer))
    #     # logger.debug('buffer type: {}'.format(type(buffer)))
    #     # logger.debug('buffer.read(): {}'.format(buffer.read()))
    #     # logger.debug('buffer.read() type: {}'.format(type(buffer.read())))
    #     # logger.debug('buffer.getbuffer(): {}'.format(buffer.getbuffer()))
    #     # logger.debug('buffer.getbuffer()) type: {}'.format(type(buffer.getbuffer())))
    #     s3 = boto3.resource('s3')
    #     s3_object = s3.Object('kml-server-cache', key)
    #     s3_object.put(Body=buffer)

        # import tempfile
        # tmp = tempfile.NamedTemporaryFile()
        # with open(tmp.name, 'wb') as f:
        #     f.write(buffer.read())
        # s3.upload_file(image_path, 'kml-server-cache', buffer)
        #s3_object.put(Body=buffer)



    # if memcache and memcached_connection:
    #     if memcached_connection.get(image_path) is None: #TODO: Determine whether we can check for object existence without retrieving it
    #         status_code, buffer = get_image_buffer(image_source_url)
    #         if status_code == 200 and buffer is not None:
    #             logger.debug('Writing image to memcached with key {}'.format(image_path))
    #             memcached_connection.set(image_path, buffer.read())
    #         else:
    #             logger.debug('response status_code {}'.format(status_code))
    #             return

    if not os.path.isfile(image_path):
        try:
            original_umask = os.umask(0)
            os.makedirs(cache_dir, mode=0o777, exist_ok=True)
        finally:
            os.umask(original_umask)
        status_code, buffer = get_image_buffer(image_source_url)
        if status_code == 200 and buffer is not None:
            logger.debug('Saving image to {}'.format(image_path))
            with open(image_path, 'wb') as image_file:
                image_file.write(buffer.read())
        else:
            logger.debug('response status_code {}'.format(status_code))
            return

    cached_image_url_path = re.sub('<.+>', dataset_type, image_url_path[1:]) + '?image=' + image_basename
    logger.debug('cached_image_url_path: {}'.format(cached_image_url_path))
    #logger.debug("KKKKKKKEEEEEEEEEEYYYYYYYYYY: " + key)
    #return key
    return cached_image_url_path




