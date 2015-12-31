import os
from osgeo import ogr, gdal, osr
import time
from shapely.wkb import loads
from rtree import index
import pandas as pd
import pysal
import fiona
from shapely.geometry import MultiPolygon, MultiPoint, Polygon, Point
from shapely.geometry import shape
import os, glob

###count different crime types###
def crimecount(pointfile, polygonfile):
	#w='D:/crime geocoding/SOM/quadrat10/cascade_split.dbf'
	#v="D:/crime geocoding/SOM/tulsa_crime0911.dbf"

	t1=time.time()

	db= pysal.open(pointfile, 'r')
	d = {col: db.by_col(col) for col in db.header}
	table1=pd.DataFrame(d).fillna(0)

#crimelist=list(table1.sort(['IBR']).groupby('IBR').aggregate(lambda x: tuple(x)).index)
	crime=list(table1.sort(['IBR_des']).groupby('IBR_des').size().index)
	myin=[(j) for i,j in zip(crime, range(len(crime))) if i =='NULL']
	del crime[myin[0]]

	#crimelist=[]
	#for i in crime:
		#if i[0].isdigit():
			#crimelist.append(i)

	t2=time.time()
	print t2-t1

	points = [pt for pt in fiona.open(pointfile)]
	mn=fiona.open(pointfile)
	for x in crime:
		t3=time.time()
		polygons = [pol for pol in fiona.open(polygonfile)]
		idx = index.Index()
		for pos, poly in enumerate(polygons):
			idx.insert(pos, shape(poly['geometry']).bounds)
		for k, l in zip(range(len(mn)), mn):
			if l['properties']['IBR_des'] == x: #for 12 crime types
				point=shape(l['geometry'])
				for j in idx.intersection(point.coords[0]):
					if point.within(shape(polygons[j]['geometry'])):
						polygons[j]['properties']['id'] = polygons[j]['properties']['id'] + int(points[k]['properties']['myID'])

		t4=time.time()
		print t4-t3


		mycount=[]
		for e in range(len(polygons)):
			mycount.append(polygons[e]['properties']['id'])


		spatialReference = osr.SpatialReference()
		spatialReference.ImportFromProj4('+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ')
		driver = ogr.GetDriverByName('Esri Shapefile')
		ds = driver.CreateDataSource('D:/crime geocoding/SOM/place/c_'+str(x).replace(' ','_')+'.shp')
		layer = ds.CreateLayer('', spatialReference, geom_type=ogr.wkbMultiPolygon)
# Add one attribute
		layer.CreateField(ogr.FieldDefn('crime', ogr.OFTInteger))
		defn = layer.GetLayerDefn()
		for i, k in zip(polygons, mycount):
			feat = ogr.Feature(defn)
			feat.SetField('crime', k)

			geom = ogr.CreateGeometryFromWkb(shape(i['geometry']).wkb)
			feat.SetGeometry(geom)
			layer.CreateFeature(feat)
		feat = geom = None  # destroy these


