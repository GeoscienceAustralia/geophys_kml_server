'''
Created on 3 Oct. 2018

@author: Alex Ip - Geoscience Australia

Hacky utility to cache EVERYTHING from OPeNDAP & WMS endpoints. 
WARNING: This will take some time to run to completion and consume a considerable amount of bandwidth. Do NOT try this at home.
'''
import os
import sys
import tempfile
import re
from geophys_kml_server import settings
from geophys_utils.dataset_metadata_cache import get_dataset_metadata_cache
from geophys_utils import NetCDFPointUtils, NetCDFLineUtils
from geophys_kml_server import cache_image_file
import logging
import cottoncandy

root_logger = logging.getLogger()

bbox_list = [-180.0, -90.0, 180.0, 90.0] # Get everything regardless of spatial position

netcdf_util_subclass={'point': NetCDFPointUtils, 'line': NetCDFLineUtils} # Subclasses keyed by dataset_format

# Set proxy for outgoing traffic (used for testing with Fiddler)
http_proxy = settings['global_settings'].get('http_proxy')
if http_proxy:
    root_logger.info('Setting proxy to {}'.format(http_proxy))
    os.environ['http_proxy'] = http_proxy

def main():

    if settings['global_settings']['s3_bucket_name']:
        s3_bucket_name = settings['global_settings']['s3_bucket_name']
    else:
        s3_bucket_name = None

    myvars = {}
    with open("/var/www/html/keys") as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            myvars[name.strip()] = var.strip('\n')

    cci = cottoncandy.get_interface(s3_bucket_name, ACCESS_KEY=myvars["Access key ID"],
                                         SECRET_KEY=myvars["Secret access key"],
                                         endpoint_url="https://s3-ap-southeast-2.amazonaws.com")

    list_of_objects = cci.get_bucket_objects()

    dataset_metadata_cache = get_dataset_metadata_cache(db_engine=settings['global_settings']['database_engine'], 
                                                        debug=settings['global_settings']['debug'])
    
    for dataset_type, dataset_settings in settings['dataset_settings'].items():

        #=======================================================================
        # #TODO: Remove this - it's only to exclude things we've already done
        # if dataset_type in ['ground_gravity']:
        #     continue
        #=======================================================================
        
        dataset_format = dataset_settings['dataset_format']
        cache_dir = os.path.join((settings['global_settings'].get('cache_root_dir') or
                                  tempfile.gettempdir()),
                                 'kml_server_cache',
                                 dataset_type)
        if dataset_format not in ['point', 'line', 'grid']:
        #if dataset_format not in ['line']:
            continue
        if s3_bucket_name is None:

            os.makedirs(cache_dir, exist_ok=True)

        dataset_metadata_dict_list = dataset_metadata_cache.search_dataset_distributions(keyword_list=dataset_settings['keyword_list'],
            protocol=dataset_settings['protocol'],
            ll_ur_coords=[[bbox_list[0], bbox_list[1]], [bbox_list[2], bbox_list[3]]]
        )
        print('{} {} datasets found'.format(len(dataset_metadata_dict_list), dataset_type))
        
        
        for dataset_metadata_dict in dataset_metadata_dict_list:
            dataset_metadata_dict['netcdf_path'] = modify_nc_path(dataset_settings.get('netcdf_path_prefix'), 
                                                                  str(dataset_metadata_dict['distribution_url']))
            dataset_metadata_dict['netcdf_basename'] = os.path.basename(dataset_metadata_dict['netcdf_path'])
                                  
            #===================================================================
            # dataset_link = dataset_settings.get('dataset_link')
            # if dataset_link:
            #     for key, value in dataset_metadata_dict.items():
            #         dataset_link = dataset_link.replace('{'+key+'}', str(value))
            # dataset_metadata_dict['dataset_link'] = dataset_link
            #===================================================================
            
            distribution_url = dataset_metadata_dict['distribution_url']
            
            if dataset_format == 'grid':
                wms_url = distribution_url.replace('/dodsC/', '/wms/') #TODO: Replace this hack

                image_basename = os.path.splitext(os.path.basename(distribution_url))[0] + '.png'

                wms_pixel_size = dataset_settings.get('wms_pixel_size') or settings['default_dataset_settings'].get('wms_pixel_size')
                assert wms_pixel_size, 'Unable to determine wms_pixel_size'

                # Retrieve image for entire dataset
                north = dataset_metadata_dict['latitude_max']
                south = dataset_metadata_dict['latitude_min']
                east = dataset_metadata_dict['longitude_max']
                west = dataset_metadata_dict['longitude_min']

                wms_url = wms_url + "?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={0},{1},{2},{3}&CRS=EPSG:4326&WIDTH={4}&HEIGHT={5}&LAYERS={6}&STYLES=&FORMAT=image/png" \
                      "&DPI=120&MAP_RESOLUTION=120&FORMAT_OPTIONS=dpi:120&TRANSPARENT=TRUE" \
                      "&COLORSCALERANGE={7}%2C{8}&NUMCOLORBANDS=127".format(south,
                                                                             west,
                                                                             north,
                                                                             east,
                                                                             int((east - west) / wms_pixel_size),
                                                                             int((north - south) / wms_pixel_size),
                                                                             dataset_settings['wms_layer_name'],
                                                                             dataset_settings['wms_color_range'][0],
                                                                             dataset_settings['wms_color_range'][1],
                                                                             )

                print('\tCaching image {} from {}'.format(image_basename, wms_url))
                s3_key_name = re.sub('/tmp/kml_server_cache/', '', cache_dir)
                #s3_key_name = re.sub('?image=', '', s3_key_name)
                print("s3_key_name" + str(s3_key_name))
                cached_image_url_path = cache_image_file(dataset_type, image_basename, wms_url, s3_bucket_name, s3_key_name)

                print('\t\tImage URL: {}'.format(cached_image_url_path))
                continue
            #
            # Points and lines handled below
            
            try:
                print('\tCaching data for {} dataset {}'.format(dataset_format, distribution_url))

                s3_path_key = "{}/{}".format(dataset_type, dataset_metadata_dict['netcdf_basename'])
                #cache_path = re.sub('.nc', '_xycoords_narray', s3_path_key)
                cache_path = os.path.join(cache_dir,
                                          re.sub('\.nc$', '_cache.nc', dataset_metadata_dict['netcdf_basename']))

                # netcdf_util = netcdf_util_subclass[dataset_format](distribution_url,
                #      enable_disk_cache=True,
                #      enable_memory_cache=True,
                #      cache_path=cache_path,
                #      s3_path_key= s3_path_key,
                #      s3_bucket='kml-cache-server',
                #      cci = cci,
                #      debug=settings['global_settings']['debug']
                #      )
                print("HERE")
                print("s3_bucket_name: " + str(s3_bucket_name))
                print("cci: " + str(cci))
                print("s3_path_key: " + str(s3_path_key))
                print("cache_path: " + str(cache_path))
                key_with_xycoords = re.sub('.nc', "_xycoords_narray", s3_path_key)
                # print(key_with_xycoords)
                # for l in list_of_objects:
                #     #print(str(l))
                #     # l looks like this s3.ObjectSummary(bucket_name='kml-server-cache', key='ground_gravity/199159_xycoords_narray')
                #     #print(key_with_xycoords)
                #     if re.search(key_with_xycoords, str(l)):
                #         logging.debug('key found, skipping')
                #         continue
                #
                # print('key not found')
                netcdf_util = NetCDFPointUtils(distribution_url,
                     enable_disk_cache=True,
                     enable_memory_cache=True,
                     cache_path=cache_path,
                     s3_path_key=s3_path_key,
                     s3_bucket=s3_bucket_name,
                     cci = cci,
                     debug=settings['global_settings']['debug']
                     )

                print('\t\tCached {} points'.format(len(netcdf_util.xycoords))) # Cause xycoords to be cached
                
                if dataset_format == 'line':
                    print('\t\tCached {} lines'.format(len(netcdf_util.line))) # Cause line & line_index to be cached
                    
                netcdf_util.netcdf_dataset.close()
            except BaseException as e:
                print('\t\tUnable to cache data for {}: {}'.format(distribution_url, e))
    
def modify_nc_path(netcdf_path_prefix, opendap_endpoint):    
    '''
    Helper function to substitute netcdf_path_prefix in netcdf_path if defined
    '''
    if netcdf_path_prefix:
        return os.path.join(netcdf_path_prefix, os.path.basename(opendap_endpoint))
    else:
        return opendap_endpoint

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

    main()
