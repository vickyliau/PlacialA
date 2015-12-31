import pysal
import pandas as pd
import fiona
from rtree import index
from shapely.geometry import MultiPolygon, MultiPoint, Polygon, Point
from shapely.geometry import shape
import time
from osgeo import ogr, gdal, osr
import numpy as num
import datetime
from jdcal import *

def cluster_group(crimeshp, groupshp,group, repeat, outputcsv):
	points = [pt for pt in fiona.open(crimeshp)]
	if group != 0:
		polygons = [pt for pt in fiona.open(groupshp) if pt['properties']['GID'] == group]
	else:
		polygons = [pt for pt in fiona.open(groupshp)]
	polylist=[str(i) for i in pt['properties'].keys()]

	db= pysal.open(crimeshp.replace('.shp','.dbf'), 'r')
	d = {col: db.by_col(col) for col in db.header}
	pointtable=pd.DataFrame(d).fillna(0)
	pointtable=pointtable.sort(['Inci_date','Inci_time'], ascending=[True,True])
	crimelist=list(pointtable.sort(['IBR_des']).groupby('IBR_des').size().index)
	crimelist=[i for i in crimelist if i != 'NULL']
	
	db= pysal.open(groupshp.replace('.shp','.dbf'), 'r')
	d = {col: db.by_col(col) for col in db.header}
	polytable=pd.DataFrame(d).fillna(0).reset_index(drop=True)
	if group != 0:
		polytable=polytable.loc[polytable['GID'] == group].reset_index(drop=True)
	for i in polylist:
		if not i in ['G_ID', 'crimestr', 'incidate', 'incitime']:
			polytable[i]=polytable[i].astype(num.int32)
	
	idx = index.Index()
	for pos, poly in enumerate(polygons):
		idx.insert(pos, shape(poly['geometry']).bounds)

	#record events within polygons, including crime types, incident date & time
	for k, l in zip(range(len(points)), points):
		point=shape(l['geometry'])
		for j in idx.intersection(point.coords[0]):
			if point.within(shape(polygons[j]['geometry'])) and str(pointtable['IBR_des'][k]) != 'NULL':
				polygons[j]['properties']['crimestr'] = str(polygons[j]['properties']['crimestr'])+','+str(pointtable['IBR_des'][k])

				polygons[j]['properties']['incidate'] = str(polygons[j]['properties']['incidate'])+','+str(pointtable['Inci_date'][k])
				
				polygons[j]['properties']['incitime'] = str(polygons[j]['properties']['incitime'])+','+str(pointtable['Inci_time'][k])

	#get and sort records in the lists
	if repeat == 1:
		#repeated
		myIBR=[]
		mydate=[]
		mytime=[]
		myID=[]
		for e in range(len(polygons)):
			#split event
			table1=pd.DataFrame({})
			if str(polygons[e]['properties']['crimestr']) != 'None':
				table1['crimestr']=polygons[e]['properties']['crimestr'][5:].split(',')
				table1['incidate']=polygons[e]['properties']['incidate'][5:].split(',')
				table1['incitime']=polygons[e]['properties']['incitime'][5:].split(',')
				#sort by date and time
				table1=table1.sort(['incidate','incitime'], ascending=[True,True])
				#table1['G_ID']=polygons[e]['properties']['G_ID'][5:].split(',')
				myIBR.append(','.join(list(table1['crimestr'])))
				mydate.append(','.join(list(table1['incidate'])))
				mytime.append(','.join(list(table1['incitime'])))
				#myID.append(','.join(list(table1['G_ID'])))
			else:
				myIBR.append(0)
				mydate.append(0)
				mytime.append(0)
			

		polytable['crimestr']=myIBR
		polytable['incidate']=mydate
		polytable['incitime']=mytime
				
	else:
		#non-repeated
		myIBR=[]
		mydate=[]
		mytime=[]
		myID=[]
		for e in range(len(polygons)):
			#split event
			table1=pd.DataFrame({})
			table1['crimestr']=polygons[e]['properties']['crimestr'][5:].split(',')
			table1['incidate']=polygons[e]['properties']['incidate'][5:].split(',')
			table1['incitime']=polygons[e]['properties']['incitime'][5:].split(',')
			#table1['G_ID']=polygons[e]['properties']['G_ID'][5:].split(',')
			#sort by date and time
			table1=table1.sort(['incidate','incitime'], ascending=[True,True])

			crimestr=(','.join(list(table1['crimestr']))).split(',')
			incidate=(','.join(list(table1['incidate']))).split(',')
			incitime=(','.join(list(table1['incitime']))).split(',')
		
			crimestr=[crimestr[i] for i in range(len(crimestr)) if i<len(crimestr)-1 and crimestr[i] != crimestr[i+1]]+[crimestr[len(crimestr)-1]]
			incidate=[incidate[i] for i in range(len(crimestr)) if i<len(crimestr)-1 and crimestr[i] != crimestr[i+1]]+[incidate[len(crimestr)-1]]
			incitime=[incitime[i] for i in range(len(crimestr)) if i<len(crimestr)-1 and crimestr[i] != crimestr[i+1]]+[incitime[len(crimestr)-1]]

			myIBR.append(','.join(list(crimestr)))
			mydate.append(','.join(list(incidate)))
			mytime.append(','.join(list(incitime)))
			#myID.append(','.join(list(table1['G_ID'])))
		
		polytable['crimestr']=myIBR
		polytable['incidate']=mydate
		polytable['incitime']=mytime

	polytable=polytable[['ParIIcri', 'aggass', 'allothlar', 'burglary', 'drug', 'forrap', 'larfrobui', 'larfrosho', 'larfroveh', 'motvehthe', 'murder', 'robbery', 'UID', 'SOMID', 'GID', 'Shape_Leng', 'Shape_Area', 'crimestr', 'incidate', 'incitime']]

	#convert crime types into simple code
	#for i in range(len(polytable)):
	for j in range(len(crimelist)):
		polytable['crimestr'] = polytable['crimestr'].str.replace('larcery', 'larceny') #.str.replace(crimelist[j], symbol[j])
		polytable['crimestr'] = polytable['crimestr'].str.replace('larceny from shoplifting', 'shoplifting')

	
	datedate=[0]*len(polytable)
	for j in range(len(polytable)):
		if polytable['incidate'][j] != 0:
			sep =polytable['incidate'][j].strip().split(',') 
			mydate=[0]*len(sep)
			for p, q in zip(sep,range(len(sep))):
				a=time.strptime(p, "%Y-%m-%d")
				mydate[q]=str(sum(gcal2jd(a.tm_year,a.tm_mon,a.tm_mday)))
			datedate[j]=','.join(mydate)

	polytable['incidate']=datedate
	
	polytable=polytable[['UID','incidate','crimestr']]
	polytable.columns = ['UID', 'Date', 'CrimeType']
	polytable.to_csv(outputcsv,index=False)

	"""
	#save as a shapefile
	spatialReference = osr.SpatialReference()
	spatialReference.ImportFromProj4('+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ')
	driver = ogr.GetDriverByName('Esri Shapefile')
	ds = driver.CreateDataSource('D:/crime geocoding/SOM/May/clusterlist/clist31.shp')
	layer = ds.CreateLayer('', spatialReference, geom_type=ogr.wkbMultiPolygon)
	# Add one attribute
	defn=[]
	for b, q in zip(polylist, range(len(polylist))):
		if b == 'Shape_Leng' or b == 'Shape_Area':
			layer.CreateField(ogr.FieldDefn(b, ogr.OFTReal))
			m ='defn'+str(q)
			m = layer.GetLayerDefn()
			
		elif b == 'G_ID' or b == 'crimestr' or b == 'incidate' or b == 'incitime':
			layer.CreateField(ogr.FieldDefn(b, ogr.OFTString))
			m ='defn'+str(q)
			m = layer.GetLayerDefn()
		else:
			layer.CreateField(ogr.FieldDefn(b, ogr.OFTInteger))
			m ='defn'+str(q)
			m = layer.GetLayerDefn()
		defn.append(m)

	for i, j in zip(polygons, range(len(polytable))):
		geom = ogr.CreateGeometryFromWkb(shape(i['geometry']).wkb)
		feat = ogr.Feature(layer.GetLayerDefn())
		for c, d in zip(polylist, range(len(polylist))):
			feat.SetField(c, list(polytable[c])[j])
				
		feat.SetGeometry(geom)
		layer.CreateFeature(feat)
	feat = geom = None  # destroy these

	"""
