import pandas as pd
import requests
from pandas.io.json import json_normalize
import json

#
def get_details(campnear_id):
	try:
		req_url = "http://api.campnear.me/GetFacilityDetails?campnear_id=" + str(campnear_id)
		data = requests.get(req_url)
		camping_json  = json.loads(data.text)
		camping_df = json_normalize(camping_json['Items'])
		return camping_df
	except Exception as ex:
		print str(ex)
		return pd.DataFrame()

# transform dataframe into geojson. option_cols are a list of column names from the df to include in the feature properties
def create_geojson(df, option_cols=[]):
	json_out = '{"type": "FeatureCollection","features": [' # begin array of records
	for index,row in df.iterrows():
		json_out = json_out + '{"type": ' # begin record
		json_out = json_out + '"Feature","properties": {'  # begin properties
		json_out = json_out + '"title":"' + row.facilityname + '",'
		json_out = json_out + '"description":"' + row.site_url + '",'
		for col in option_cols :
			try:
				val = row[col]
				json_out = json_out + '"' + col + '":"' + str(val) + '",'
			except Exception as ex:
				print("create_geojoson(): Couldnt get column:" + col)
				print(str(ex))
				continue
		json_out = json_out + '"marker-size":"small"'
		json_out = json_out + '},' # end properties
		
		#geo point
			
		json_out = json_out + '"geometry": {"type": "Point","coordinates":[' + str(row.facilitylongitude) \
		+ ',' + str(row.facilitylatitude) + ']}'
	
		json_out = json_out + '},' # end record 
	
	# remove last comma
	json_out = json_out[0:len(json_out)-1]
	json_out = json_out + "]}"
	return json_out

# get some campgrounds near Doe Bay!
data = requests.get('http://apidev.campnear.me/GetFacilitiesNear?lat=48.6411985&lon=-122.7808991&radius=10')
camping_json  = json.loads(data.text)
camping_df = json_normalize(camping_json['Items'])

# for each campground, fetch the full details
doe_bay = pd.DataFrame()
for index,row in camping_df.iterrows():
	doe_bay = doe_bay.append(get_details(row.campnear_id))

# select columns you want in the geojson properties. See http://api.campnear.me/static/datadef.html
geojson_properties = ['cg_flush','cg_shower']
geojson_out = create_geojson(doe_bay, geojson_properties)
outfile = 'doe_bay.geojson'

with open(outfile, 'w') as fp:
	fp.write(str(geojson_out))

# import the geojson file into your favorite geojson receptacle.. try http://geojson.io/
