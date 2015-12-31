import pysal
from pandas import *
import fiona
from shapely.geometry import Point
import gdal, ogr, os, osr

from point_fre import point_fre
from polyraster import polyraster
from union import union
from polysplit import polysplit

#import rpy2.robjects as robjects
#from rpy2.robjects.packages import importr
#import rpy2.robjects.numpy2ri
#rpy2.robjects.numpy2ri.activate()

# Set up our R namespaces
#R = rpy2.robjects.r #run R in python namespaces
#spatstat = importr('spatstat') #import R packages

iteration=range(1001)
setwd="D:/crime geocoding/SOM/stability/"
db= pysal.open('D:/crime geocoding/SOM/tulsa_crime0911.dbf', 'r')
d = {col: db.by_col(col) for col in db.header}
table1=DataFrame(d)

polycount=[]

for it in iteration[1:21]:
#point frequency in raster
	fre=setwd+'quadrat'+str(it)+".tif"
	cenpoint=setwd+'pointcen'+str(it)+".shp"
	aggpoint=setwd+'aggpoint'+str(it-1)+".shp"
	point_fre(repeat=1, gridsize=20, table1=table1,outfile=fre, pointfile=cenpoint)
	"""
	#aggregate points
	if it  == 1:
		mypoints=[]
		for gf in fiona.open(cenpoint):
			mypoints.append(Point(gf['geometry']['coordinates']))
		crime=[]
		for gf in fiona.open('D:/crime geocoding/SOM/tulsa_crime0911.shp'):
			crime.append(Point(gf['geometry']['coordinates']))
		mypoints=crime+mypoints

	elif it > 1:
		points=[]	
		for gf in fiona.open(cenpoint):
			points.append(Point(gf['geometry']['coordinates']))
		mypoints=points+mypoints #combine

		spatialReference = osr.SpatialReference()
		spatialReference.ImportFromProj4('+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ')
		driver = ogr.GetDriverByName('Esri Shapefile')
		ds = driver.CreateDataSource(aggpoint)
		layer = ds.CreateLayer('', spatialReference, geom_type=ogr.wkbPoint)
# Add one attribute
		layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
		defn = layer.GetLayerDefn()
		for i in mypoints:
			feat = ogr.Feature(defn)
			feat.SetField('id', 0)

			geom = ogr.CreateGeometryFromWkb(i.wkb)
			feat.SetGeometry(geom)
			layer.CreateFeature(feat)
		feat = geom = None  # destroy these
	"""
	
#polygonize
	#inin=setwd+'quadrat'+str(it)+".tif"
	outout=setwd+'quadrat'+str(it)+".shp"
	polyraster(infile=fre, outfile=outout)

#polygon union and polygon split 
	
	if it == 1:
		in_cade=outout
		mypoly=[]
		for count in fiona.open(outout):
			mypoly.append(count['geometry'])
		
		polycount.append(len(mypoly))
	
	elif it > 1 and it == 2:
		in_cade=[in_cade]+[outout]
		out_cade=setwd+'cascade_union'+str(it)+".shp"
		out_split=setwd+'cascade_split'+str(it)+".shp"
		union(infile=in_cade, outfile=out_cade)
		polysplit(infile=out_cade, outfile=out_split)
		mypoly=[]
		for count in fiona.open(out_split):
			mypoly.append(count['geometry'])
		
		polycount.append(len(mypoly))
	elif it > 2:
		in_cade=[out_split]+[outout]
		union(infile=in_cade, outfile=setwd+'cascade_union'+str(it)+".shp")
		out_cade=setwd+'cascade_union'+str(it)+".shp"
		out_split=setwd+'cascade_split'+str(it)+".shp"
		polysplit(infile=out_cade, outfile=out_split)
		mypoly=[]
		for count in fiona.open(out_split):
			mypoly.append(count['geometry'])
		
		polycount.append(len(mypoly))
		
