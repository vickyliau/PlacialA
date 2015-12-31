from osgeo import gdal, ogr, osr
import sys
import os, glob
from osgeo.gdalconst import * 
import time
from shapely.ops import cascaded_union
from shapely.geometry import MultiPolygon
from shapely.geometry import shape
import fiona
import time

#polygonization

def polyraster(infile, outfile):
	#infile='D:/crime geocoding/SOM/stability/quadrat*.tif'
	#db1 = sorted(glob.glob(infile))
	db1=[infile]
# this allows GDAL to throw Python Exceptions
	gdal.UseExceptions()
	for i in range(len(db1)):
#  get raster datasource
		src_ds1 = gdal.Open( db1[i] )
		#src_ds2 = gdal.Open( db2[i] )
		if src_ds1 is None:
  	  		print 'Unable to open %s' % src_filename
   	 		sys.exit(1)

		try:
   	 		srcband1 = src_ds1.GetRasterBand(1)
		except RuntimeError, e:
    # for example, try GetRasterBand(10)
   	 		print 'Band ( %i ) not found' % band_num
    			print e
    			sys.exit(1)
				
#  create output datasource
		spatialReference = osr.SpatialReference()
		spatialReference.ImportFromProj4('+proj=utm +zone=15 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')
		driver_v = ogr.GetDriverByName("ESRI Shapefile")
		#outfile='D:/crime geocoding/SOM/stability/quadrat'+str(time.time())[6:10]+'_n.shp'
		outdataset = driver_v.CreateDataSource(outfile)
		outlayer = outdataset.CreateLayer(outfile, spatialReference, geom_type=ogr.wkbMultiPolygon)#, srs = None) 
		gdal.Polygonize( srcband1, srcband1, outlayer, -1, [], callback=None )
		outlayer = None
