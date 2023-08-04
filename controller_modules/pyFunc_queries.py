#--------------------------------------------------------------------------------------------------------------------------------
# Name:        pyFunc_queries
# Purpose:
#
# Author:      florian.beyer
#
# Created:     2022
# Copyright:   (c) florian.beyer 2022
#
#-------This class offers methods to create a Sentinel 1 Query to Code-De and filter out a list of tiles depending on the given parameters
#-------Code not cleaned up, fully functional. Imported from https://gitea.julius-kuehn.de/FLF/pyQuery_EO_Finder
#--------------------------------------------------------------------------------------------------------------------------------

import geopandas as gpd
import requests



class PyFuncQueries:

    def buildSentinel1QueryTileList(self, geometry, startDate, endDate, productType):

        url = self.build_query(
        collection='Sentinel1',      # 'Sentinel1', 'Sentinel2', 'Sentinel3'
        geometry=geometry, 
        start=startDate,          # 'YYYY-MM-DD' or None  
        end=endDate,            # 'YYYY-MM-DD' or None
        processingLevel='LEVEL1',    # 'LEVEL0','LEVEL1','LEVEL1B','LEVEL1C','LEVEL2','LEVEL2A','LEVEL2AP','LEVEL3'
        productType=productType,           # 'L1C','L2A','L2A-MAJA','L2A-FORCE','GRD','SLC','CARD-BS','CARD-INF6'
        sensorMode='IW',             # 'IW', 'EW', 'WV', 'SM' or None
        maxRecords=2000
        )
        return self.createTileListFromUrl(url)

    def build_query(self, collection, 
                    geometry=None, 
                    maxRecords = 2000, 
                    start=None, 
                    end=None, 
                    location='all',
                    processingLevel=None, 
                    productType=None,
                    sensorMode=None,
                    orbitDirection=None,
                    sortParam='startDate',
                    sortOrder='descending',
                    status='all'
                    ):

        test = False

        url = 'https://finder.code-de.org/resto/api/collections/' + collection + '/search.json?'

        query_attributes = []

        if maxRecords != None:
            query_attributes.append('maxRecords={}'.format(maxRecords)) 

        if start != None:
            query_attributes.append('startDate={}T00%3A00%3A00Z'.format(start))

        if end != None:
            query_attributes.append('completionDate={}T23%3A59%3A59Z'.format(end))

        query_attributes.append('location={}'.format(location))

        if processingLevel != None:
            query_attributes.append('processingLevel={}'.format(processingLevel))

        if productType != None:
            query_attributes.append('productType={}'.format(productType))

        if sensorMode != None:
            if collection == 'Sentinel1':
                query_attributes.append('sensorMode={}'.format(sensorMode))
            else:
                print('sensorMode only works for Sentinel-1!')

        if orbitDirection != None: 
            if collection == 'Sentinel1':
                query_attributes.append('orbitDirection={}'.format(orbitDirection))
            else:
                print('orbitDirection only works for Sentinel-1!')

        query_attributes.append('sortParam={}&sortOrder={}&status={}'.format(sortParam,sortOrder,status))

        if geometry != None:
            geometry = self.__handle_geometry(geometry)
            if isinstance(geometry, str):
                if geometry[:3] == 'lat':
                    query_attributes.append(geometry)
                else:
                    query_attributes.append('geometry={}'.format(geometry))
            elif isinstance(geometry, list):
                    test = geometry


        query_attributes.append('dataset=ESA-DATASET')


        query = url + '&'.join(query_attributes) 
        print('query url: {}'.format(query))

        if test is False:
            return query
        else:
            return [query, test]

    def createTileListFromUrl(self, url):

        if isinstance(url, str):
            query_results = self.__request_CodeDE(url)
            tiles = self.__get_result_list(query_results)
            if len(tiles) < 2000:
                print('Number of images: {}'.format(len(tiles)))
                print('first 5 tiles: {}'.format(tiles[0:5]))
            else:
                print('More than 2000 images found. Several requests required to collect all images ...')
                page = 2
                while len(self.__get_result_list(self.__request_CodeDE(url+'&page='+str(page)))) == 2000:
                    more_tiles = self.__get_result_list(self.__request_CodeDE(url+'&page='+str(page)))
                    tiles = tiles + more_tiles
                    page = page + 1
                last_tiles = self.__get_result_list(self.__request_CodeDE(url+'&page='+str(page)))
                tiles = tiles + last_tiles

                print('Number of images: {}'.format(len(tiles)))
                print('first 5 tiles: {}'.format(tiles[0:5]))
        else:
            list_of_urls = []
            for polygon in url[1]:
                url_ = url[0] + '&geometry=' + polygon
                list_of_urls.append(url_)

            list_of_images = []
            for query in list_of_urls:
                print('query url: {}'.format(query))
                query_temp = self.__request_CodeDE(query)
                tiles_temp = self.__get_result_list(query_temp)
                list_of_images.append(tiles_temp)

            flat_list = [item for sublist in list_of_images for item in sublist]
            print('number of images with duplicates: {}'.format(len(flat_list)))

            tiles = list(set(flat_list))
            print('final number of images: {}'.format(len(tiles)))
            print('first 5 tiles: {}'.format(tiles[0:5]))
        return tiles


    def __handle_geometry(self, geometry):

        if isinstance(geometry, list) and len(geometry) == 2:
            geometry_ = 'POINT({}+{})'.format(geometry[0], geometry[1])

        elif isinstance(geometry, list) and len(geometry) > 2:
            if geometry[0] == geometry [-1]:
                geometry_ = 'POLYGON'+str(geometry).replace('), (','%2C').replace(', ','+').replace('[(','((').replace(')]','))')
            else:
                print('polygone is not closed! Please enter a correct geometry.')

        elif isinstance(geometry, str) and geometry.endswith('.geojson'):
            location = gpd.read_file(geometry)
            polygones = location['geometry']

            if len(polygones) == 1:
                geometry_ = str(polygones[0]).replace('POLYGON ', 'POLYGON').replace(', ','%2C').replace(' ', '+')

            elif len(polygones) > 1:
                print('more than one polygon is inputted. A list of query urls will be returned!!!')

                geometry_ = []
                for polygon in polygones:
                    geometry = str(polygon).replace('POLYGON ', 'POLYGON').replace(', ','%2C').replace(' ', '+')
                    geometry_.append(geometry)
        else:
            print('Something went wrong with geometry input. Pleace insert point as list or polygone(s) as geojson file!')

        return geometry_

    def __request_CodeDE(self, query_url):

        try:
            response = requests.get(query_url)
            response.raise_for_status()
            # Code here will only run if the request is successful
            if response.status_code == 200:
                print('Request was sucessful.')

            return response
        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as err:
            print(err)

    def __get_result_list(self, response):
        results = response.json()['features']

        dir_list = []
        for i in range(len(results)):
            dir_list.append(results[i]['properties']['productIdentifier'])

        return dir_list

    def __get_map_coords(self, geometry):

        if isinstance(geometry, list) and len(geometry) == 2:
            return [(geometry[1],geometry[0]),[]]

        elif isinstance(geometry, list) and len(geometry) > 2:
            lon = []
            lat = []
            for x,y in geometry:
                lon.append(x)
                lat.append(y)
            polygon = []
            for i in range(len(lon)):
                polygon.append((lat[i],lon[i]))

            return [(sum(lat)/len(lat), sum(lon)/len(lon)), polygon]

        elif isinstance(geometry, str) and geometry.endswith('.geojson'):
            location = gpd.read_file(geometry)
            polygones = location['geometry']

            if len(polygones) == 1:
                coords = list(polygones[0].exterior.coords)
                center = (polygones[0].centroid.coords.xy[1][0], polygones[0].centroid.coords.xy[0][0])

                lon = []
                lat = []
                for x,y in coords:
                    lon.append(x)
                    lat.append(y)
                polygon = []
                for i in range(len(lon)):
                    polygon.append((lat[i],lon[i]))

                return  [center, polygon]

            elif len(polygones) > 1:

                all_polygones = []

                for polygon in polygones:
                    coords_ = list(polygon.exterior.coords)
                    center = (polygon.centroid.coords.xy[1][0], polygon.centroid.coords.xy[0][0])

                    lon = []
                    lat = []
                    for x,y in coords_:
                        lon.append(x)
                        lat.append(y)
                    polygon_ = []
                    for i in range(len(lon)):
                        polygon_.append((lat[i],lon[i]))

                    all_polygones.append([center, polygon_])

                return  all_polygones

        else:
            print('Something went wrong with geometry input. Pleace insert point as list of tuples or polygone(s) as geojson file!')