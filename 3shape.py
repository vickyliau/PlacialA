from pandas import *
import uuid
from pyproj import Proj, transform
import numpy as num
import time
from shapely.geometry import Point
from osgeo import ogr, osr

options.mode.chained_assignment = None

w='D:/crime geocoding/SOM/tulsa_con0911_12.csv'
table1=read_csv(w, dtype=str).fillna(0)
#table1 = table1.sort(['Reported_address'])
table1=table1.replace(0,'NULL')

lon=list(table1['Longitude'])
lat=list(table1['Latitude'])
for i in range(len(table1)):
	lon[i]=float(lon[i])
	lat[i]=float(lat[i])


table1['Longitude']=lon
table1['Latitude']=lat
#table1=table1.replace('nan',num.nan)

#shrink column names
table1.columns = ["Global_ID","Readdress","Inci_date","Inci_time","Re_date","Re_time","Lat","Long","IBR","IBR_des","PDcode","PD_des","SSL","SSN","flag_geo"]
table1=table1.loc[table1['flag_geo'] != 'i'].reset_index(drop=True)
#global ID
newlist=[]
for i in range(len(table1)):
	newlist.append(str(uuid.uuid1()))


table1['Global_ID']=newlist

t1=time.time()

#the standard shapefile
wgs84=Proj("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs ", preserve_units = True)
#wgs84=Proj("+init=EPSG:4326")

#outProj = Proj('+proj=lcc +lat_1=35.56666666666667 +lat_2=36.76666666666667 +lat_0=35 +lon_0=-98 +x_0=600000.0000000001 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=1 +no_defs ')
#esri projection 102725 - nad 1983 stateplane oklahoma north fips 3502 feet/ http://spatialreference.org/ref/esri/102725/
#PyProj assumes that your coordinates are in meters, preserve_units = True
#Calling a Proj class instance with the arguments lon, lat will convert lon/lat (in degrees) to x/y native map projection coordinates (in meters) If the optional keyword 'preserve_units' is True, the units in map projection coordinates are not forced to be meters.

outProj = Proj('+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ')
#outProj = Proj("+init=EPSG:32615")

#convert projection
nad83_x = [0]*len(table1)
nad83_y = [0]*len(table1)
Longitude=list(table1['Long'])
Latitude=list(table1['Lat'])
for i in range(len(table1)):
	a=transform(wgs84,outProj,Longitude[i],Latitude[i])
	nad83_x[i], nad83_y[i] = a[0], a[1]


table1['nad83_x'] = nad83_x
table1['nad83_y'] = nad83_y
table1['myID'] = 1
table1['myID']=table1['myID'].astype(int)

t2=time.time()
print t2-t1

#create shape
points=[]
for i in range(len(table1)):
	points.append(Point(nad83_x[i],nad83_y[i]))


spatialReference = osr.SpatialReference()
#spatialReference.ImportFromProj4('+proj=lcc +lat_1=35.56666666666667 +lat_2=36.76666666666667 +lat_0=35 +lon_0=-98 +x_0=600000.0000000001 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=1 +no_defs ')#, preserve_units = True)
spatialReference.ImportFromProj4("+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ")#, preserve_units = True)
driver = ogr.GetDriverByName('Esri Shapefile')
ds = driver.CreateDataSource('D:/crime geocoding/SOM/tulsa_crime0911.shp')
layer = ds.CreateLayer('', spatialReference, geom_type=ogr.wkbPoint)

# Add attributes
cols=list(table1.columns)
defn=[]
for x, y in zip(cols, range(len(cols))):
	if x == 'nad83_x' or x == 'nad83_y' or x == 'Lat' or x=='Long':
		layer.CreateField(ogr.FieldDefn(x, ogr.OFTReal))
		m='defn'+str(y)
		m=layer.GetLayerDefn()
	elif x == 'myID':
		layer.CreateField(ogr.FieldDefn(x, ogr.OFTInteger))
		m='defn'+str(y)
		m=layer.GetLayerDefn()
	else:
		layer.CreateField(ogr.FieldDefn(x, ogr.OFTString))
		m='defn'+str(y)
		m=layer.GetLayerDefn()
	defn.append(m)

for i, k in zip(points, range(len(table1))):
	geom = ogr.CreateGeometryFromWkb(i.wkb)
	feat = ogr.Feature(layer.GetLayerDefn())
	for x, y, z in zip(cols, range(len(cols)), defn):
		#n='feat'+str(y)
		#n = ogr.Feature(z)
		feat.SetField(x, table1[x][k])
	feat.SetGeometry(geom)
	layer.CreateFeature(feat)
feat = geom = None 
		
#for x, y, z in zip(cols, range(len(cols)), defn): #
	#n='feat'+str(y)
	#n = ogr.Feature(z)
	#n.SetField(x, table1[x])
		
feat = geom = None  # destroy these

t3=time.time()
print t3-t2

