from cluster_group import cluster_group

p='D:/crime geocoding/SOM/oldCrimeData_crime0911.shp'
g='D:/crime geocoding/SOM/May/new/SOMGroup.shp'
outputcsv=('D:/crime geocoding/SOM/May/clusterlist/cluster_pack.csv')
		
cluster_group(crimeshp=p, groupshp=g,group=0, repeat=1, outputcsv=outputcsv)

