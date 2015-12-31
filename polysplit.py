import os
from osgeo import ogr, gdal, osr
import fiona
from shapely.geometry import MultiPolygon, MultiPoint, Polygon
from shapely.geometry import shape
from shapely.ops import unary_union
import time
from shapely.prepared import prep
from shapely.wkb import loads
from rtree import index
import pandas as pd
import pysal
import numpy as num
from operator import itemgetter

###split the union polygon into multiple polygons###
def polysplit(infile, outfile):
	#w="D:/crime geocoding/SOM/quadrat10/cascade_union.shp"
	driver = ogr.GetDriverByName('ESRI Shapefile')

	polygon1 = []
	# append the geometries to the list
	for pol in fiona.open(infile):
		polygon1.append(pol['geometry'])


	polygon2=polygon1[0]['coordinates'] #get individual coordinates for polygons

	t1=time.time()

	polygons=[]
	for i in polygon2:
		for j in i:
			polygons.append(Polygon(j)) #generate individual polygons

	idx = index.Index()
	for pos, poly in enumerate(polygons):
		idx.insert(pos, poly.bounds)

###identify relations of intersection polygons###
	inter=[] 
	mark=[]
	for i, j in zip(range(len(polygons)), polygons):
		#poly=list(k.exterior.coords)
		mylist=[]
		mymark=[]
		for m in idx.intersection(j.bounds):
			if j.within(polygons[m]) and not polygons[m].within(j):
				mylist.append(m)
				mymark.append(1)
			if polygons[m].within(j) and not j.within(polygons[m]):#small polygons (inter value) within the large polygon (index)
				mylist.append(m)
				mymark.append(0)
		inter.append(mylist)
		mark.append(mymark)
		mylist=[]
		mymark=[]

	t2=time.time()
	print t2-t1


###area properties###
	myarea=[]
	for i in inter:
		area=[]
		for j in i:
			area.append(polygons[j].area)
		myarea.append(area)


###three list for different polygon intersection: intersection, within intersection and no intersection###
	inter1=[] #intersection polygon list
	inter2=[] #mark interior polygons (third level)
	inter3=[] #single polygon
	for i, j in zip(inter, range(len(inter))):
		if i != [] and sum(mark[j]) == 0 and not (1 in mark[j] and 0 in mark[j]): #large polygon
			a=[j]+i[0:len(mark[j])] 
			inter1.append(a) 
			inter2.append(0)
		
		elif i != [] and sum(mark[j]) >= 1 and (1 in mark[j] and 0 in mark[j]) and  num.max(num.array(myarea[j]))<polygons[j].area: 
			print j
		elif i != [] and sum(mark[j]) >= 1 and (1 in mark[j] and 0 in mark[j]) and  num.max(num.array(myarea[j]))> polygons[j].area: #inside and outside polygons, but the index is not the largest one (third level up)
			indexa=[n for m, n in zip(mark[j], range(len(mark[j]))) if m == 1]
			a1=mark[j]*1
			a2=inter[j]
			withpoly=[j]+[a2[n] for m, n in zip(a1, range(len(a1))) if m == 0] 
		#first: the large polygon, others: polygons within the large polygon
			inter1.append(withpoly) 
			inter2.append(1) 
			#remove the largest one and keep the small one
		elif i == []:
			inter3.append(j) 
			#large polygons or polygons without intersections
	#else:
		#print j

	fir=zip(*inter1)[0] 
	#get the first element fot lists of lists
	first=sorted(list(set(fir))) 
	#get the list of large polygons

###generate polygons###

	poly=[]
	for i, j in zip(inter1, inter2):
		if j == 1: #remove the largest one and keep the small one
			for m in i[1:]:
				a=polygons[i[0]]
				b=a.intersection(polygons[m])
				poly.append(b)
		elif j == 0:
			for m in i[1:]:
				if m == i[1]:
					a=polygons[i[0]]
					b=a.difference(polygons[m])
				else:
					b=b.difference(polygons[m])
			poly.append(b)

	t3=time.time()
	print t3-t2

	single=[]
	for i in inter3:
		single.append(polygons[i])

	interpoly=poly+single


	spatialReference = osr.SpatialReference()
	spatialReference.ImportFromProj4('+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ')
	driver = ogr.GetDriverByName('Esri Shapefile')
	#outfile='D:/crime geocoding/SOM/quadrat10/cascade_split.shp'
	ds = driver.CreateDataSource(outfile)
	layer = ds.CreateLayer('', spatialReference, geom_type=ogr.wkbMultiPolygon)
# Add one attribute
	layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
	defn = layer.GetLayerDefn()
	for i in interpoly:
		feat = ogr.Feature(defn)
		feat.SetField('id', 0)

		geom = ogr.CreateGeometryFromWkb(i.wkb)
		feat.SetGeometry(geom)
		layer.CreateFeature(feat)
	feat = geom = None  # destroy these

	t4=time.time()
	print t4-t3
