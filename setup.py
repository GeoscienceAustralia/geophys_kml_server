#!/usr/bin/env python

#===============================================================================
#    Copyright 2017 Geoscience Australia
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#===============================================================================
from distutils.core import setup

version = '0.0.0'

setup(name='geophys_utils',
      version=version,
      packages=[
          'geophys_kml_server'
      ],
      package_data={
                    'geophys_kml_server': ['geophys_kml_server_settings.yml']
                    },
      scripts=[],
      requires=[
            'geophys_utils' # https://github.com/GeoscienceAustralia/geophys_utils
            'flask',
            'flask_compress',
            'flask_restful',
            'matplotlib',
            'requests',
            'shapely',
            'simplekml'
            'tempfile',
            'yaml'
            ],
      url='https://github.com/geoscienceaustralia/geophys_kml_server',
      author='Alex Ip - Geoscience Australia',
      maintainer='Alex Ip - Geoscience Australia',
      maintainer_email='alex.ip@ga.gov.au',
      description='Dynamic Geophysics KML Server',
      long_description='Dynamic Geophysics KML Server',
      license='Apache License Version 2.0'
      )
