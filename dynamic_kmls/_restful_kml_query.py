'''
Created on 7 Sep. 2018

@author: Andrew Turner
'''
import yaml
import os
from flask_restful import Resource
from flask import request, make_response
import simplekml
import time
from shapely.geometry import Polygon
from shapely import wkt
from geophys_utils.netcdf_converter import netcdf2kml
from geophys_utils.dataset_metadata_cache import get_dataset_metadata_cache
from dynamic_kmls import DEBUG, DATABASE_ENGINE
import logging
from pprint import pprint, pformat

# Define maximum bounding box width for point display. Uses survey convex-hull polygons for anything larger.
MAX_BOX_WIDTH_FOR_POINTS = 1.5

logger = logging.getLogger(__name__)
if DEBUG:
    logger.setLevel(logging.DEBUG) # Initial logging level for this module
else:
    logger.setLevel(logging.INFO) # Initial logging level for this module


settings = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                            'netcdf2kml_settings.yml')))

class RestfulKMLQuery(Resource):
    '''
    RestfulKMLQuery Resource subclass
    '''
    def __init__(self):
        '''
        RestfulKMLQuery Constructor
        '''
        super(RestfulKMLQuery, self).__init__()
        
        self.sdmc = get_dataset_metadata_cache(db_engine=DATABASE_ENGINE, debug=False)
           
    
    def get(self, dataset_type):
        logger.debug(dataset_type)
        get_function = {'ground_gravity': RestfulKMLQuery.build_ground_gravity_kml,
                        'aem': RestfulKMLQuery.build_aem_kml
                        }
        
        get_function = get_function.get(dataset_type)
        
        #TODO: Handle this more gracefully
        assert get_function, 'Invalid dataset type "{}"'.format(dataset_type)
        
        bbox = request.args['BBOX'] 
    
        xml = get_function(self, bbox)
        
        response = make_response(xml)
        response.headers['content-type'] = 'application/vnd.google-earth.kml+xml'
        return response

    
    def modify_nc_path(self, netcdf_path_prefix, opendap_endpoint):    
        #logger.debug("point_data_tuple: " + str(point_data_tuple))
        if netcdf_path_prefix:
            return netcdf_path_prefix + os.path.basename(opendap_endpoint)
        else:
            return opendap_endpoint

    #@app.route('/aem/<bounding_box>', methods=['GET'])
    def build_aem_kml(self, bbox):
    
        yaml_settings = settings['aem']
    
        t0 = time.time()  # retrieve coordinates from query
        print("AEM")

        bbox_list = bbox.split(',')
        west = float(bbox_list[0])
        south = float(bbox_list[1])
        east = float(bbox_list[2])
        north = float(bbox_list[3])
    
        bbox_polygon = Polygon(((west, south),
                                (east, south),
                                (east, north),
                                (west, north),
                                (west, south)
                                ))
    
        t1 = time.time()
        logger.debug("Retrieve bbox values from get request...")
        logger.debug("Time: " + str(t1 - t0))
    
        # Get the point_data_tuple surveys from the database that are within the bbox
        
        point_data_tuple_list = self.sdmc.search_dataset_distributions(
            keyword_list=yaml_settings['keyword_list'],
            protocol=yaml_settings['protocol'],
            ll_ur_coords=[[west, south], [east, north]]
        )
    
        logger.debug([[west, south], [east, north]])
        t2 = time.time()
        logger.debug("Retrieve point_data_tuple strings from database...")
        logger.debug("Time: " + str(t2 - t1))
    
        kml = simplekml.Kml()
        netcdf_file_folder = kml.newfolder(name=yaml_settings['netcdf_file_folder_name'])
    
        t_polygon_1 = time.time()
    
        if len(point_data_tuple_list) > 0:
    
                for point_data_tuple in point_data_tuple_list:
                    logger.debug("point_data_tuple: " + str(point_data_tuple))
                    
                    netcdf_path = self.modify_nc_path(yaml_settings['netcdf_path_prefix'], str(point_data_tuple[2]))
                    
                    netcdf2kml_obj = netcdf2kml.NetCDF2kmlConverter(netcdf_path, yaml_settings, point_data_tuple)
                    t_polygon_2 = time.time()
                    logger.debug("set style and create netcdf2kmlconverter instance from point_data_tuple for polygon ...")
                    logger.debug("Time: " + str(t_polygon_2 - t_polygon_1))
    
                    try:
                        survey_polygon = wkt.loads(point_data_tuple[3])
                    except Exception as e:
                        # print(e)
                        continue  # Skip this polygon
    
                    if survey_polygon.intersects(bbox_polygon):
                        # if survey_polygon.within(bbox_polygon):
                        # if not survey_polygon.contains(bbox_polygon):
                        # if survey_polygon.centroid.within(bbox_polygon):
                        # if not survey_polygon.contains(bbox_polygon) and survey_polygon.centroid.within(bbox_polygon):
    
                        netcdf2kml_obj.build_lines(netcdf_file_folder, bbox_list)
    
                    else:
                        netcdf2kml_obj.build_lines(netcdf_file_folder, False)
    
                    #dataset_polygon_region = netcdf2kml_obj.build_region(-1, -1, 200, 800)
                return str(netcdf_file_folder)
    
        else:
                empty_folder = kml.newfolder(name="no points in view")
                return str(empty_folder)
    
    #grav
    
    #@app.route('/ground_gravity/<bounding_box>', methods=['GET'])
    def build_ground_gravity_kml(self, bbox):
    
        yaml_settings = settings['ground_gravity']
    
        t0 = time.time()  # retrieve coordinates from query
    
        bbox_list = bbox.split(',')
        west = float(bbox_list[0])
        south = float(bbox_list[1])
        east = float(bbox_list[2])
        north = float(bbox_list[3])
    
        bbox_polygon = Polygon(((west, south),
                                (east, south),
                                (east, north),
                                (west, north),
                                (west, south)
                                ))
    
        t1 = time.time()
        logger.debug("Retrieve bbox values from get request...")
        logger.debug("Time: " + str(t1 - t0))
    
        # Get the point_data_tuple surveys from the database that are within the bbox
        point_data_tuple_list = self.sdmc.search_dataset_distributions(
            keyword_list=yaml_settings['keyword_list'],
            protocol=yaml_settings['protocol'],
            ll_ur_coords=[[west, south], [east, north]]
        )
        logger.debug("tuple: " + str(point_data_tuple_list))
    
        logger.debug([[west, south], [east, north]])
        t2 = time.time()
        logger.debug("Retrieve point_data_tuple strings from database...")
        logger.debug("Time: " + str(t2 - t1))
    
        kml = simplekml.Kml()
        netcdf_file_folder = kml.newfolder(name=yaml_settings['netcdf_file_folder_name'])
    
        # ----------------------------------------------------------------------------------------------------------------
        # High zoom: show points rather than polygons.
        if east - west < MAX_BOX_WIDTH_FOR_POINTS:
            logger.debug('gravity points')
            if len(point_data_tuple_list) > 0:
                for point_data_tuple in point_data_tuple_list:
                    netcdf_path = self.modify_nc_path(yaml_settings['netcdf_path_prefix'], str(point_data_tuple[2]))
                    
                    logger.debug("Building NETCDF: " + str(point_data_tuple[2]))
                    netcdf2kml_obj = netcdf2kml.NetCDF2kmlConverter(netcdf_path, yaml_settings, point_data_tuple)
                    t3 = time.time()
                    logger.debug("set style and create netcdf2kmlconverter instance of point_data_tuple file ...")
                    logger.debug("Time: " + str(t3 - t2))
    
                    # logger.debug("Number of points in file: " + str(netcdf2kml_obj.npu.point_count))
    
                    ta = time.time()
                    netcdf2kml_obj.build_points(netcdf_file_folder, bbox_list)
                    tb = time.time()
                    logger.debug("do the things time: " + str(tb - ta))
                    logger.debug("Build the point ...")
                    dataset_points_region = netcdf2kml_obj.build_region(100, -1, 200, 800)
                    netcdf_file_folder.region = dataset_points_region
                    netcdf2kml_obj.netcdf_dataset.close()  # file must be closed after use to avoid errors when accessed again.
                    del netcdf2kml_obj  # Delete netcdf2kml_obj to removenetcdf2kml_obj.npu cache file
                    t4 = time.time()
                return str(netcdf_file_folder)
    
            else:
                logger.debug("No surveys in view")
    
        # ----------------------------------------------------------------------------------------------------------------
        # Low zoom: show polygons and not points.
        else:
            logger.debug('gravity polygons')
            t_polygon_1 = time.time()
    
            if len(point_data_tuple_list) > 0:
    
                for point_data_tuple in point_data_tuple_list:
                    netcdf_path = self.modify_nc_path(yaml_settings['netcdf_path_prefix'], str(point_data_tuple[2]))
                    #logger.debug(netcdf_path)
                    netcdf2kml_obj = netcdf2kml.NetCDF2kmlConverter(netcdf_path, yaml_settings, point_data_tuple)
                    t_polygon_2 = time.time()
                    logger.debug("set style and create netcdf2kmlconverter instance from point_data_tuple for polygon ...")
                    logger.debug("Time: " + str(t_polygon_2 - t_polygon_1))
    
                    try:
                        survey_polygon = wkt.loads(point_data_tuple[3])
                    except Exception as e:
                        # print(e)
                        continue  # Skip this polygon
    
                    if survey_polygon.intersects(bbox_polygon):
                        # if survey_polygon.within(bbox_polygon):
                        # if not survey_polygon.contains(bbox_polygon):
                        # if survey_polygon.centroid.within(bbox_polygon):
                        # if not survey_polygon.contains(bbox_polygon) and survey_polygon.centroid.within(bbox_polygon):
    
                        polygon_folder = netcdf2kml_obj.build_polygon(netcdf_file_folder)
                        #polygon_folder = netcdf2kml_obj.build_lines(netcdf_file_folder, bbox_list)
    
                    else:
                        polygon_folder = netcdf2kml_obj.build_polygon(netcdf_file_folder)
    
                    dataset_polygon_region = netcdf2kml_obj.build_region(-1, -1, 200, 800)
                # polygon_folder.region = dataset_polygon_region  # insert built polygon region into polygon folder
    
                # else:  # for surveys with 1 or 2 points. Can't make a polygon. Still save the points?
                #    logger.debug("not enough points")
    
                # neww = kml.save("test_polygon.kml")
                return str(netcdf_file_folder)
            else:
                empty_folder = kml.newfolder(name="no points in view")
                return str(empty_folder)