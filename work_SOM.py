from crimecount import crimecount
from SOMtable import SOMtable
import glob
from pysal import *
import pandas as pd
import uuid
from mvpa2.suite import *
from minisom import MiniSom

#count
point='D:/crime geocoding/SOM/tulsa_crime0911.dbf'
polygon='D:/crime geocoding/SOM/place/cascade_split15.shp'
crimecount(pointfile=point, polygonfile=polygon)

#SOM table
dbf=sorted(glob.glob("D:/crime geocoding/SOM/place/c_*.dbf"))
shp=sorted(glob.glob("D:/crime geocoding/SOM/place/c_*.shp"))
outfile='D:/crime geocoding/SOM/place/counting12.shp'
SOMtable(dbf=dbf, shp=shp, outfile=outfile)

dbf='D:/crime geocoding/SOM/place/counting12.dbf'
db= pysal.open(dbf, 'r')
d = {col: db.by_col(col) for col in db.header}
table1=pd.DataFrame(d).fillna(0)
table1.to_csv('D:/crime geocoding/SOM/place/counting12.csv',index=False)