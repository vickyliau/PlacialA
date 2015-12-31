This is a cooperation results with Dr. May Yuan, and has presented in Yuan, M., & Liau, Y.T. (2015). From Spatial Analysis to Placial Analysis. In, the Evolving GIScience workshop in memory of Pete Fisher. University of Leicester, UK 

excel files:
- tulsa_code: tulsa UCC codes to IBR codes
- join_table: aggregated into 12 crime types

python codes:
###data processing###
- 1tulsa: join UCC code with IBR codes
- 2con_tulsa: aggregate crime types and join IBR description
- 3shape: reproject and generate shape

###stability test###
- point_fre: random sampling approach
	- repeat: the number of repeating running the random sample approach (integer)
	- gridsize: cell size (integer)
	- table1: crime data (pandas dataframe)
	- outfile: output file of quadrat tif
- polyraster: polygonize raster
	- infile: quadrat tif
	- outfile: quadrat shapefile
- union: union polygons
	- infile: quadrat shapefile
	- outfile: union shapefile
- polysplit: split polygons with individual attributes
	- infile: union shapefile
	- outfile: individual polygon shapefile

- work_stab: the code to use the above four modules

###crime count###
- crimecount: count crime events within polygons
	- pointfile: crime events (dbf file)
	- polygonfile: polygons after the random sample approach (shapefile)
- SOMtable: organize 12 crime types in a table
	- dbf: dbf files of crime count 
	- shp: shapefiles of crime count 
	- outfile: output file (csv file)
	- pointfile: output for central point shapefiles

- work_SOM: the code to use the above two modules

###SOM group###
-cluster3
-cluster4
-cluster_group: create sequences of crime types, incidence date
	- crimeshp: crime data (shapefile)
	- groupshp: after random sample approach (shapefile)
	- group(integer)
	- repeat: whether to count repeated sequences (0: non-repetitive; 1: repetitive)
	- outputcsv: output file (csv file)

-work_g: the code to use the cluster_group function
