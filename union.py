from osgeo import gdal, ogr, osr
import sys
import os, glob
from osgeo.gdalconst import * 
import time
from shapely.ops import cascaded_union
from shapely.geometry import MultiPolygon
from shapely.geometry import shape
import fiona

#unions
def union(infile, outfile):
	#infile='D:/crime geocoding/SOM/quadrat10/quadrat*_n.shp'
	#db = sorted(glob.glob(infile))
	db=infile
	driver = ogr.GetDriverByName('ESRI Shapefile')

#cacaded union
	multi1 = []
# append the geometries to the list
	for pol in fiona.open(db[0]):
		multi1.append(MultiPolygon([shape(pol['geometry'])]))

	multi2 = []
# append the geometries to the list
	for pol in fiona.open(db[1]):
		multi2.append(MultiPolygon([shape(pol['geometry'])]))


	a= cascaded_union(multi1+multi2)

	spatialReference = osr.SpatialReference()
	spatialReference.ImportFromProj4('+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ')
	driver = ogr.GetDriverByName('Esri Shapefile')
	#outfile='D:/crime geocoding/SOM/statility/cascade_union.shp'
	ds = driver.CreateDataSource(outfile)
	layer = ds.CreateLayer('', spatialReference, geom_type=ogr.wkbMultiPolygon)
# Add one attribute
	layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
	defn = layer.GetLayerDefn()

	feat = ogr.Feature(defn)
	feat.SetField('id', 1)

	geom = ogr.CreateGeometryFromWkb(a.wkb)
	feat.SetGeometry(geom)
	layer.CreateFeature(feat)
	feat = geom = None  # destroy these

