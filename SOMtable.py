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
import uuid

###a table: rows for places; columns for crime types###

def SOMtable(dbf, shp, outfile):
	polygons = [shape(pol['geometry']) for pol in fiona.open(shp[0])]

	crimelist=['Part II crime', 'aggravated assault', 'all other larcery', 'burglary', 'drug', 'forcible rape', 'larcery from building', 'larcery from shoplifting', 'larcery from vehicle', 'motor vehicle theft', 'murder', 'robbery']

	crime=[] #simplify IBR description into abbreviation
	for i in crimelist:
		if len(i.split()) != 1 and len(i.split()[0]) > 3:
			a=i.split()[0][0:3]+' '+' '.join(i.split()[1:])
		else:
			a=i*1
	
		if len(i.split())>1 and len(i.split()[1]) > 3:
			b=a.split()[0]+' '+i.split()[1][0:3]+' '+' '.join(i.split()[2:])
		else:
			b=a*1
	
		if len(i.split())>2 and len(i.split()[2]) > 3:
			c=a.split()[0]+' '+b.split()[1]+' '+i.split()[2][0:3]
		elif len(i.split())>1 and len(i.split()[1]) > 3:
			c=a.split()[0]+' '+b.split()[1]
		else:
			c=a.split()[0]
		crime.append(c.replace(' ',''))

	alltab=pd.DataFrame({})
	for x, y, z in zip(dbf, range(len(dbf)), crime):
		db= pysal.open(x, 'r')
		d = {col: db.by_col(col) for col in db.header}
		table1=pd.DataFrame(d).astype(int)
		table1.columns = [z]
		alltab[z]=table1[z]
	
	myID=[]
	for i in range(len(table1)): 
		myID.append(str(uuid.uuid1()))
	alltab['myID']=myID
	crime=crime+['myID']

	spatialReference = osr.SpatialReference()
	spatialReference.ImportFromProj4('+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ')
	driver = ogr.GetDriverByName('Esri Shapefile')
	ds = driver.CreateDataSource(outfile)
	layer = ds.CreateLayer('', spatialReference, geom_type=ogr.wkbMultiPolygon)

	# Add attributes
	defn=[]
	for p, q in zip(crime, range(len(crime))):
		if p == 'myID':
			layer.CreateField(ogr.FieldDefn(p, ogr.OFTString))
			m='defn'+str(q)
			m=layer.GetLayerDefn()
			defn.append(m)
		else:
			layer.CreateField(ogr.FieldDefn(p, ogr.OFTInteger))
			m='defn'+str(q)
			m=layer.GetLayerDefn()
			defn.append(m)

	for i, k in zip(polygons, range(len(alltab))):
		geom = ogr.CreateGeometryFromWkb(i.wkb)
		feat = ogr.Feature(layer.GetLayerDefn())
		for x, y, z in zip(crime, range(len(crime)), defn):
			#n='feat'+str(y)
			#n = ogr.Feature(z)
			feat.SetField(x, alltab[x][k])
		feat.SetGeometry(geom)
		layer.CreateFeature(feat)

	feat = geom = None  # destroy these
