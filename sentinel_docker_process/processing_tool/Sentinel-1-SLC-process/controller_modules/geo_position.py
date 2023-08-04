#--------------------------------------------------------------------------------------------------------------------------------
# Name:        geo_position
# Purpose:
#
# Author:      jennifer.mcclelland
#
# Created:     2022
# Copyright:   (c) jennifer.mcclelland 2022
#
# ----This class contains multiple methods for coordinate derivation, calculation and coordinate format transformation.
# ----To derive the coordinates for a sentinel-1 SAR scene a xml file query is performed.
#--------------------------------------------------------------------------------------------------------------------------------


from typing import Callable, Any, Generator

from sentinelsat import geojson_to_wkt
from geomet import wkt
from lxml import etree
import json
import geojson
from shapely.geometry import shape, Polygon, Point
from shapely import wkt, geometry
import math


class GeoPosition:

    def loadGeojson(self, geoJsonFile):
        with open(geoJsonFile) as data:
            return json.load(data)

    def loadWktFromGeojson(self, geoJsonFile):
        with open(geoJsonFile) as data:
            geo = json.load(data)
        return geojson_to_wkt(geo)

    def wktToGeojsonShapely(self, wktCoords):
        g1 = wkt.loads(wktCoords)
        g2 = geojson.Feature(geometry=g1, properties={})
        return g2.geometry

    def geojsonToWktShapely(self, geojsonCoords):
        s = json.dumps(geojsonCoords)
        g1 = geojson.loads(s)
        g2 = shape(g1)

        # Now it's very easy to get a WKT/WKB representation
        return g2.wkt

    def snapCoordsToWkt(self, snapCoords) -> str:
        transformationFunc = (lambda x: (' '.join((lambda y: [y[1], y[0]])(i.split(","))) for i in x))

        openPolygon = list(transformationFunc(snapCoords.split(" ")))
        openPolygon.append(openPolygon[0])

        coordinatesAsString = ','.join(openPolygon)
        return "POLYGON((" + coordinatesAsString + "))"

    def swMultiPolygonFromScene(self, scene):
        wktScene = self.getWktFromScene(scene)
        if wktScene is None:
            return None

        polyWktScene = wkt.loads(wktScene)
        points = list(zip(*polyWktScene.exterior.coords.xy))
        l1p4 = Point(points[0])
        l1p1 = Point(points[1])
        l1p2 = Point(1 / 3 * l1p4.x + 2 / 3 * l1p1.x, 1 / 3 * l1p4.y + 2 / 3 * l1p1.y)
        l1p3 = Point(2 / 3 * l1p4.x + 1 / 3 * l1p1.x, 2 / 3 * l1p4.y + 1 / 3 * l1p1.y)

        l2p1 = Point(points[2])
        l2p4 = Point(points[3])
        l2p2 = Point(2 / 3 * l2p1.x + 1 / 3 * l2p4.x, 2 / 3 * l2p1.y + 1 / 3 * l2p4.y)
        l2p3 = Point(1 / 3 * l2p1.x + 2 / 3 * l2p4.x, 1 / 3 * l2p1.y + 2 / 3 * l2p4.y)

        polyList = []
        pointList1 = [l1p1, l1p2, l2p2, l2p1]
        polyList.append(geometry.Polygon([[p.x, p.y] for p in pointList1]))
        pointList2 = [l1p2, l1p3, l2p3, l2p2]
        polyList.append(geometry.Polygon([[p.x, p.y] for p in pointList2]))
        pointList3 = [l1p3, l1p4, l2p4, l2p3]
        polyList.append(geometry.Polygon([[p.x, p.y] for p in pointList3]))
        return [polyList[0], polyList[1], polyList[2]]

    def getWktFromScene(self, scene: str) -> str:
        tree = etree.parse(scene)
        root = tree.getroot()
        result = root.findall('.//{http://www.opengis.net/gml}coordinates')
        return self.snapCoordsToWkt(result[0].text) if result is not None and len(result) > 0 else None

    def areaOverlap(self, scene1, scene2):
        wkt1 = self.getWktFromScene(scene1)
        wkt2 = self.getWktFromScene(scene2)

        poly1: Polygon = wkt.loads(wkt1)
        poly2: Polygon = wkt.loads(wkt2)

        areaOverlap = poly2.intersection(poly1).area
        return areaOverlap

    def roundedIntersect(self, scene1, scene2):
        wkt1 = self.getWktFromScene(scene1)
        wkt2 = self.getWktFromScene(scene2)

        roundAll: Callable[[Any], Generator[list[str], Any, None]] = lambda x: (
        (lambda y: [str(math.floor(float(y[0]) * 100) / 100), str(math.floor(float(y[1]) * 100) / 100)])(i.split(' '))
        for i in x)

        coords1 = wkt1.replace("POLYGON", "").replace("((", "").replace("))", "").split(',')
        coords2 = wkt2.replace("POLYGON", "").replace("((", "").replace("))", "").split(',')

        roundedList1 = list(roundAll(coords1))
        roundedList2 = list(roundAll(coords2))

        createWkt = lambda x: (' '.join(i) for i in x)
        wkt1 = ','.join(createWkt(roundedList1))
        wkt2 = ','.join(createWkt(roundedList2))

        roundedWkt1 = "POLYGON((" + wkt1 + "))"
        roundedWkt2 = "POLYGON((" + wkt2 + "))"

        poly1: Polygon = wkt.loads(roundedWkt1)
        poly2: Polygon = wkt.loads(roundedWkt2)

        return poly1.intersects(poly2)
