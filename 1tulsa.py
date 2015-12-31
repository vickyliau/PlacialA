from pandas import *
import numpy as num
from pysal import *
import os, glob
from osgeo import ogr
import csv


#read in data from geodatabase
driver = ogr.GetDriverByName("ESRI Shapefile")
tulsalist = glob.glob('D:/crime geocoding/CrimeData/Tulsa/Tulsa_Crime_*.dbf')

nlist = []
for m,n in zip(tulsalist, range(len(tulsalist))):
	a=tulsalist[n].rfind("Tulsa_")
	b=tulsalist[n].rfind(".dbf")
	nlist.append(m[a:b])

IBRtable=read_excel('tulsa_code.xlsx', 'tulsa_code', index_col=None, na_values=['NA']).fillna(0)
for i in range(len(IBRtable)):
	IBRtable["UCC_code"][i] = str(IBRtable["UCC_code"][i])
	
for x,y in zip(tulsalist, nlist):
	db= pysal.open(x, 'r')
	d = {col: db.by_col(col) for col in db.header}
	table1=DataFrame(d).fillna(0)
	
	newtable1=DataFrame({})
	#newtable1["Location_name"]=table1["Loc_name"]
	Reported_address = list(table1["ADDRESS"])
	newtable1["Reported_address"]=table1["ADDRESS"]
	newtable1=newtable1.fillna(0)
	flag_geocode = ['str']*len(table1["ADDRESS"])

	for i in range(len(table1["ADDRESS"])):
		if Reported_address[i] != '' and Reported_address[i] != 0 and Reported_address[i].strip().find("UNKNOWN") == -1 and Reported_address[i].strip().find("UNKOWN"):
			Reported_address[i]=str(Reported_address[i]).strip()+",TULSA,OK"
		else:
			Reported_address[i]="TULSA,OK"
		if table1["Loc_name"][i] == "US_CityState":
			flag_geocode[i] = "i"
		if table1["Loc_name"][i] == "US_StreetName":
			flag_geocode[i] = "s"
	newtable1["Reported_address"]=Reported_address
	newtable1["flag_geocode"]=flag_geocode
	Incident_date=['str']*len(table1["ADDRESS"])
	Incident_time=['str']*len(table1["ADDRESS"])
	for i in range(len(table1["ADDRESS"])):
		if "DATE" in db.header:
			Incident_date[i] = str(table1["DATE"][i])
			Incident_time[i] = num.nan
			
			if table1["TIME"][i] != 0 and len(str(int(table1["TIME"][i]))) ==4:
				Incident_time[i] = str(int(table1["TIME"][i]))[0:2]+':'+str(int(table1["TIME"][i]))[2:4]+":"+"00"
			elif table1["TIME"][i] != 0 and len(str(int(table1["TIME"][i]))) ==3:
				Incident_time[i] = str(int(table1["TIME"][i]))[0:1]+':'+str(int(table1["TIME"][i]))[1:]+":"+"00"
			elif table1["TIME"][i] != 0 and len(str(int(table1["TIME"][i]))) ==1:
				Incident_time[i]=num.nan

		elif "DATE1" in db.header:
			if x == 'Q:/NIJ_Data/Crime_Data/Crime_Data_Match_vicky/Tulsa\\Tulsa_Crime_2001.dbf':
				Incident_date[i] =str(table1["DATE2"][i])
				Incident_time[i] = num.nan
				if table1["TIME2"][i] != 0 and len(str(int(table1["TIME2"][i]))) ==4:
					Incident_time[i] = str(int(table1["TIME2"][i]))[0:2]+':'+str(int(table1["TIME2"][i]))[2:4]+":"+"00"
				elif table1["TIME2"][i] != 0 and len(str(int(table1["TIME2"][i]))) ==3:
					Incident_time[i] = str(int(table1["TIME2"][i]))[0:1]+':'+str(int(table1["TIME2"][i]))[1:]+":"+"00"
				elif table1["TIME2"][i] != 0 and len(str(int(table1["TIME2"][i]))) ==1:
					Incident_time[i]=num.nan
			else:
				Incident_date[i] = str(table1["DATE1"][i])
				Incident_time[i] = num.nan
				if table1["TIME1"][i] != 0 and len(str(int(table1["TIME1"][i]))) ==4:
					Incident_time[i] = str(int(table1["TIME1"][i]))[0:2]+':'+str(int(table1["TIME1"][i]))[2:4]+":"+"00"
				elif table1["TIME1"][i] != 0 and len(str(int(table1["TIME1"][i]))) ==3:
					Incident_time[i] = str(int(table1["TIME1"][i]))[0:1]+':'+str(int(table1["TIME1"][i]))[1:]+":"+"00"
				elif table1["TIME1"][i] != 0 and len(str(int(table1["TIME1"][i]))) ==1:
					Incident_time[i]=num.nan

		else:
			Incident_date[i] = str(table1["Incident_d"][i])
			if table1["Incident_t"][i] != 0 and len(str(int(table1["Incident_t"][i]))) ==4:
				Incident_time[i] = str(int(table1["Incident_t"][i]))[0:2]+':'+str(int(table1["Incident_t"][i]))[2:4]+":"+"00"
			elif table1["Incident_t"][i] != 0 and len(str(int(table1["Incident_t"][i]))) ==3:
				Incident_time[i] = str(int(table1["Incident_t"][i]))[0:1]+':'+str(int(table1["Incident_t"][i]))[1:]+":"+"00"
			elif table1["Incident_t"][i] != 0 and len(str(int(table1["Incident_t"][i]))) ==1:
				Incident_time[i]=num.nan
	
	newtable1["Incident_date"] = Incident_date
	newtable1["Incident_time"] = Incident_time

	newtable1["Report_date"] = num.nan
	newtable1["Report_time"] = num.nan
	newtable1["PD_description"] = num.nan
	if "DESCR" in db.header:
		newtable1["PD_description"] = table1["DESCR"]	
	elif "DESCRP" in db.header:
		newtable1["PD_description"] = table1["DESCRP"]
	if "X" in db.header:
		newtable1["Longitude"] = table1["X"]
		newtable1["Latitude"] = table1["Y"]
	else:
		newtable1["Latitude"] = table1["Latitude"]
		newtable1["Longitude"] = table1["Longitude"]
	newtable1["State_Statute_Number"]=num.nan
	newtable1["State_Statute_Literal"]=num.nan
	newtable1["Global_ID"] = num.nan
	newtable1["IBR_description"] = num.nan
	
	#if "DESCR" in db.header:
		#newtable1["IBR_description"] = table1["DESCR"]	
	#elif "DESCRP" in db.header:
		#newtable1["IBR_description"] = table1["DESCRP"]
	
	UCC=['str']*len(table1["ADDRESS"])
	newtable1.is_copy = False
	for i in range(len(table1["ADDRESS"])):
		if "CLASS" in db.header:
			UCC[i] = str(table1["CLASS"][i])
		elif "TYPE" in db.header:
			UCC[i] = str(table1["TYPE"][i])
		
	newtable1["Police_Department_Code"] = UCC
	newtable1["UCC"] = UCC

	IBRindex=IBRtable.set_index(["UCC_code"])
	newtable1=newtable1.join(IBRindex, on=["UCC"], sort=True, how='outer').reset_index().fillna(0)
	newtable1=newtable1.loc[newtable1["Reported_address"] != 0]

	#df2dbf(newtable1, x)
	#newtable1=newtable1.sort(["Incident_date"])
	#newtable1["incid"] = Series(range(1, len(newtable1)+1)).unique()
	newtable1=newtable1[["Global_ID", "Reported_address", "Incident_date", "Incident_time", "Report_date", "Report_time", "Latitude", "Longitude", "IBR", "IBR_description", "Police_Department_Code", "PD_description", "State_Statute_Number", "State_Statute_Literal","flag_geocode"]]
	newtable1=newtable1.replace(0,num.nan)
	newtable1=newtable1.replace("0",num.nan)
	newtable1=newtable1.replace("00",num.nan)
	newtable1=newtable1.replace("None",num.nan)
	newtable1=newtable1.replace("",num.nan)
	newtable1=newtable1.replace('str',num.nan)
	newtable1.to_csv("D:/crime geocoding/geocoding_csv/"+str(y)+'.csv', index=False)
