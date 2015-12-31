from pandas import *
import numpy as num
import time
import glob
"""
tulsalist=sorted(glob.glob('D:/crime geocoding/SOM/Tulsa_Crime_*.csv'))
tultab=DataFrame({})

for x, y in zip(tulsalist, range(len(tulsalist))):
	table1= read_csv(x)
	tab_tulsa=tultab.append(table1)
	if y == 0:
		tultab=table1*1
	else:
		tultab=tab_tulsa*1

tab_tulsa.to_csv('D:/crime geocoding/SOM/Tulsa_Crime0911.csv', index=False)
"""

w='C:/Dropbox/open_codes/temporal mining/SOM/join_table.xlsx'
table1=read_excel(w, 'NIBRS_Tracks', index_col=None, na_values=['NA']).fillna(0)

w='D:/crime geocoding/SOM/Tulsa_Crime0911.csv'
tulsa=read_csv(w).fillna(0)

tulsa.is_copy = False
options.mode.chained_assignment = None

t1=time.time()

for i in range(len(tulsa)):
	if tulsa["IBR"][i]=='9A' or tulsa["IBR"][i] == '9B' or tulsa["IBR"][i] == '09A' or tulsa["IBR"][i] == '09B':
		tulsa["IBR"][i]='9'
	if tulsa["IBR"][i]=='11A' or tulsa["IBR"][i] == '11B' or tulsa["IBR"][i]=='11C' or tulsa["IBR"][i] == '11D' or tulsa["IBR"][i]=='36B':
		tulsa["IBR"][i]='11'
	if tulsa["IBR"][i]=='36A' or tulsa["IBR"][i] == '36B':
		tulsa["IBR"][i]='36'
	if tulsa["IBR"][i]=='13A' or tulsa["IBR"][i] == '13B' or tulsa["IBR"][i] == '13C':
		tulsa["IBR"][i]='13'
	#if tulsa["IBR"][i]=='23A' or tulsa["IBR"][i] == '23B' or tulsa["IBR"][i] == '23C' or tulsa["IBR"][i] == '23D' or tulsa["IBR"][i] == '23E' or tulsa["IBR"][i] == '23F' or tulsa["IBR"][i] == '23G' or tulsa["IBR"][i] == '23H':
	if tulsa["IBR"][i]=='23A' or tulsa["IBR"][i] == '23B' or tulsa["IBR"][i] == '23E' or tulsa["IBR"][i] == '23F' or tulsa["IBR"][i] == '23H':
		tulsa["IBR"][i]='23'
	if tulsa["IBR"][i]=='26A' or tulsa["IBR"][i] == '26B' or tulsa["IBR"][i] == '26C' or tulsa["IBR"][i] == '26D' or tulsa["IBR"][i] == '26E':
		tulsa["IBR"][i]='26'
	if tulsa["IBR"][i]=='35A' or tulsa["IBR"][i] == '35B':
		tulsa["IBR"][i]='35'
	if tulsa["IBR"][i]=='36A':
		tulsa["IBR"][i]='36'
	if tulsa["IBR"][i]=='39A' or tulsa["IBR"][i] == '39B' or tulsa["IBR"][i] == '39C' or tulsa["IBR"][i] == '39D':
		tulsa["IBR"][i]='39'
	if tulsa["IBR"][i]=='40A' or tulsa["IBR"][i] == '40B' or tulsa["IBR"][i] == '40C':
		tulsa["IBR"][i]='40'
	if tulsa["IBR"][i]=='64A' or tulsa["IBR"][i] == '64B':
		tulsa["IBR"][i]='64'
	if tulsa["IBR"][i]=='90A' or tulsa["IBR"][i] == '90B' or tulsa["IBR"][i] == '90C' or tulsa["IBR"][i] == '90H' or tulsa["IBR"][i] == '90F' or tulsa["IBR"][i] == '90G' or tulsa["IBR"][i]=='90J' or tulsa["IBR"][i]=='90Z':
		tulsa["IBR"][i]='90'


#convert to string for the join
for i in range(len(table1)):
	table1['IBR_code'][i]=str(table1['IBR_code'][i])

description=table1.set_index([ "IBR_code"])

t2=time.time()
print t2-t1

#index crime
tulsa["index"]=num.nan

for i in range(len(tulsa)): #convert to integer
	tulsa["index"][i]=tulsa.index[i]+1
	#if str(tulsa["IBR"][i]).isdigit():
		#tulsa["IBR"][i]=int(tulsa["IBR"][i])
	#elif not str(tulsa["IBR"][i]).isdigit() and tulsa["IBR"][i].find(",") == -1 and len(tulsa["IBR"][i])==3:
		#tulsa["IBR"][i]=int(tulsa["IBR"][i][:len(tulsa["IBR"][i])-1])

#join
tulsa=tulsa.join(description, on=["IBR"], sort=True, rsuffix='_right', how='outer').fillna(0)
tulsa=tulsa[(tulsa["index"] != 0)].reset_index().fillna(0)
tulsa["IBR_description"]=tulsa["crime_des12"]

"""
#adjustment for combined cases
for i in range(len(tulsa)):
	if not str(tulsa["IBR"][i]).isdigit() and tulsa["IBR"][i].find("TRAFFIC") != -1:
		tulsa["IBR_description"][i]=tulsa["IBR"][i]
		tulsa["IBR"][i]=0
	if not str(tulsa["IBR"][i]).isdigit() and tulsa["IBR"][i].find("TRACK") != -1:
		tulsa["IBR_description"][i]=tulsa["IBR"][i]
		tulsa["IBR"][i]=0
	if not str(tulsa["IBR"][i]).isdigit() and tulsa["IBR"][i].upper().find("NOT") != -1:
		tulsa["IBR_description"][i]=tulsa["IBR"][i]
		tulsa["IBR"][i]=0
	if not str(tulsa["IBR"][i]).isdigit():
		a=tulsa["IBR"][i].strip().split(",")
		if not str(a[0]).isdigit():
			a[0]=int(a[0][:len(a[0])-1])
			if a[0] in list(description.index):
				des1=table1["crime_des12"][list(description.index).index(a[0])]
			
		else:
			a[0]=int(a[0])
			if a[0] in list(description.index):
				des1=table1["crime_des12"][list(description.index).index(a[0])]

		if not str(a[1]).isdigit():
			a[1]=int(a[1][:len(a[1])-1])
			if a[1] in list(description.index):
				des2=table1["crime_des12"][list(description.index).index(a[1])]
			
		else:
			a[1]=int(a[1])
			if a[1] in list(description.index):
				des2=table1["crime_des12"][list(description.index).index(a[1])]

		tulsa["IBR_description"][i]=str(des1)+","+str(des2)
		#tulsa["IBR"]=str(a[0])+","+str(a[1])
"""

t3=time.time()
print t3-t2

tulsa=tulsa[["Global_ID","Reported_address","Incident_date","Incident_time","Report_date","Report_time","Latitude","Longitude","IBR","IBR_description","Police_Department_Code","PD_description","State_Statute_Literal","State_Statute_Number","flag_geocode"]]
tulsa=tulsa.replace("",num.nan)
tulsa=tulsa.replace("0",num.nan)
tulsa=tulsa.replace("00",num.nan)
tulsa=tulsa.replace(0,num.nan)
tulsa.to_csv('D:/crime geocoding/SOM/tulsa_con0911_12.csv',index=False)
