from pandas import *
from pysal import *
import numpy as num
import os, glob
import random
import gdal, ogr, os, osr
import time
from shapely.geometry import Point
from shapely.geometry import shape

def point_fre(repeat, gridsize, table1, outfile, pointfile):
	repeat=1
	for w in range(repeat):
#generate a random point as the starting point
		mysam=random.sample(range(len(table1)), 1)
	#mysam=[26]
#calculate the extent of a grid
		cengrid=table1[table1.index == mysam[0]]
		cenX=list(cengrid["nad83_x"])[0]
		cenY=list(cengrid["nad83_y"])[0]

		#gridsize=50

		topleft=[cenX-gridsize/2,cenY+gridsize/2]
		topright=[cenX+gridsize/2,cenY+gridsize/2]
		bottomleft=[cenX-gridsize/2,cenY-gridsize/2]
		bottomright=[cenX+gridsize/2,cenY-gridsize/2]

#calculate the whole extent
		min_x, min_y = [num.min(num.array(table1["nad83_x"])), num.min(num.array(table1["nad83_y"]))]
		max_x, max_y = [num.max(num.array(table1["nad83_x"])), num.max(num.array(table1["nad83_y"]))]
		Btopleft=[min_x,max_y]
		Btopright=[max_x,max_y]
		Bbottomleft=[min_x,min_y]
		Bbottomright=[max_x,min_y]

#adjust the extent by the random grid
		x1=topleft[0]
		x2=topright[0]
		y2=topleft[1]
		y1=bottomleft[1]
		minX, minY = [[min_x if isinstance(abs(x1-min_x)/gridsize,int) else x1-gridsize-(int(abs(x1-min_x)/gridsize)*gridsize)][0],[min_y if isinstance(abs(y1-min_y)/gridsize,int) else y1-gridsize-(int(abs(y1-min_y)/gridsize)*gridsize)][0]]
		maxX, maxY = [[max_x if isinstance(abs(x2-max_x)/gridsize,int) else x2+gridsize+(int(abs(x2-max_x)/gridsize)*gridsize)][0],[max_y if isinstance(abs(y2-max_y)/gridsize,int) else y2+gridsize+(int(abs(y2-max_y)/gridsize)*gridsize)][0]]
		Wtopleft=[minX,maxY]
		Wtopright=[maxX,maxY]
		Wbottomleft=[minX,minY]
		Wbottomright=[maxX,minY]

#quadrat count and repeat 10 times (10 rasters)
		Xlist=num.array([minX]*int(1+((maxX-minX)/gridsize)))+num.array(range(0,int((maxX-minX)/gridsize)*gridsize+gridsize,gridsize))
		Ylist=num.array([minY]*int(1+((maxY-minY)/gridsize)))+num.array(range(0,int((maxY-minY)/gridsize)*gridsize+gridsize,gridsize))
	
	#get indices
		mycount=[0]*(len(Xlist)-1)*(len(Ylist)-1)
		mycou=[0]*(len(Xlist)-1)*(len(Ylist)-1)
		for k in range(len(table1["nad83_x"])):
			indexX = num.where((table1["nad83_x"][k]-Xlist)==(table1["nad83_x"][k]-Xlist)[(table1["nad83_x"][k]-Xlist)>0].min())[0][0]
			#indexX=num.nonzero(abs(table1["nad83_x"][k]-Xlist[1:])==num.min(abs(table1["nad83_x"][k]-Xlist[1:])))[0][0]
			indexY = num.where((table1["nad83_y"][k]-Ylist)==(table1["nad83_y"][k]-Ylist)[(table1["nad83_y"][k]-Ylist)>0].min())[0][0]
			#indexY=num.nonzero(abs(table1["nad83_y"][k]-Ylist[1:])==num.min(abs(table1["nad83_y"][k]-Ylist[1:])))[0][0]+1
			
	#calculate frequencies or existence
			if mycount[(len(Xlist)-1)*(indexY)+(indexX)] >= 1:
				mycount[(len(Xlist)-1)*(indexY)+(indexX)] = mycount[(len(Xlist)-1)*(indexY)+(indexX)] +1
			elif mycount[(len(Xlist)-1)*(indexY)+(indexX)] == 0:
				mycount[(len(Xlist)-1)*(indexY)+(indexX)] = 1
		
			mycou[(len(Xlist)-1)*(indexY)+(indexX)] = 1

		mycount1=num.array(mycou).reshape((len(Ylist)-1),(len(Xlist)-1))#[::-1]
		mycou1=num.array(mycount).reshape((len(Ylist)-1),(len(Xlist)-1))
		mycount2=mycount1*1#.astype(float)
		num.place(mycount2,mycount2==1,2)
		num.place(mycount2,mycount2==0,1)
		num.place(mycount2,mycount2==2,0)
		"""
	#get central points
		firfir=[minX+gridsize/2, maxY-gridsize/2]
		firlast=[maxX-gridsize/2,maxY-gridsize/2]
		lastfir=[minX+gridsize/2,minY+gridsize/2]
		lastlast=[maxX-gridsize/2,minY+gridsize/2]

	#y coordinates
		ycoors=firfir[1]-lastfir[1]
		FYlist=num.arange(lastfir[1], firfir[1], gridsize)
		
	#x coordinates
		xcoors=firlast[0]-firfir[0]
		FXlist=num.arange(firfir[0], firlast[0], gridsize)
		
		#coors=[]
		coor=[]
		for i in FYlist:
			#coor=[]
			for j in FXlist:
				coor.append(Point(j,i))
			#coors.append(coor)
		"""
		driver = gdal.GetDriverByName('GTiff')
		proj = osr.SpatialReference()
		#outfile = 'D:/crime geocoding/SOM/stability/quadrat'+ str(time.time())[6:10] + '.tif'
		dataset = driver.Create(outfile, mycount1.shape[1], mycount1.shape[0], 1, gdal.GDT_Float64, )
	        dataset.SetGeoTransform((minX, gridsize,0,minY,0,gridsize))
		wkt_projection='PROJCS["WGS 84 / UTM zone 15N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-93],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","32615"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
		dataset.SetProjection(wkt_projection)
		dataset.GetRasterBand(1).WriteArray(mycount1)
		dataset.FlushCache()
	
		dataset = None
		"""	
		spatialReference = osr.SpatialReference()
		spatialReference.ImportFromProj4('+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ')
		driver = ogr.GetDriverByName('Esri Shapefile')
		ds = driver.CreateDataSource(pointfile)
		layer = ds.CreateLayer('', spatialReference, geom_type=ogr.wkbPoint)
# Add one attribute
		layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
		defn = layer.GetLayerDefn()
		for i in coor:
			feat = ogr.Feature(defn)
			feat.SetField('id', 0)

			geom = ogr.CreateGeometryFromWkb(i.wkb)
			feat.SetGeometry(geom)
			layer.CreateFeature(feat)
		feat = geom = None  # destroy these
		"""
