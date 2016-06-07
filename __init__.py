from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_api import FlaskAPI
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer
from flask import render_template
import config
import utilities
from flask_mysqldb import MySQL
from flask import request
import pandas as pd
import numpy as np 

app = FlaskAPI(__name__)
mysql = MySQL(app)

app.config['MYSQL_USER'] = config.MYSQL_DATABASE_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_DATABASE_PASSWORD
app.config['MYSQL_HOST'] = config.MYSQL_DATABASE_HOST
app.config['MYSQL_DB'] = config.MYSQL_DATABASE_DBNAME

api = Api(app)

def replace_nan(value):
	if value == 'NaN':
		return null
	else:
		return value

def process_data(df_items):
	try:
		items_list=[]
                for index,row in df_items.iterrows():
                        item={}
                        for col,value in row.iteritems():
                                val = replace_nan(value)
                                item.update({col: val})
                        items_list.append(item)
                return {'StatusCode':'200','Items':items_list}

	except Exception as ex:
                return {'error':str(ex)}

@app.route('/', methods=['GET'])
@set_renderers(HTMLRenderer)
def hello():
	return render_template('index.html')
# expect GetFacilityDetails?facilityid_name=facid_name_str
@app.route('/GetAllFacilities', methods=['GET'])
def getFacilityDetails():
	try :
		cursor = mysql.connection.cursor()
		query_string = "SELECT * FROM campnear_consolidated_toorcamp limit 20;"
		df_items = pd.read_sql(query_string, mysql.connection)
		return(process_data(df_items))

	except Exception as ex:
		return {'error':str(ex)}

# expect GetFacilitiesNear?lat=34.13&lon=122.42&radius=10 where lat/lon in degrees and radius in miles
@app.route('/GetFacilitiesNear', methods=['GET'])
def getFacilitiesNear():
	try :
		cursor = mysql.connection.cursor()
		lat = float(request.args.get('lat'))
		lon = float(request.args.get('lon'))
		radius = float(request.args.get('radius'))
		
		if ((not lat) or (not lon) or (not radius)):
			return {'error':'Must specify lat, lon, and radius for GetFacilitiesNear query'}
		query_string = utilities.create_radial_query(lat,lon,radius)
		df_items = pd.read_sql(query_string, mysql.connection)
                return(process_data(df_items))
		
		#cursor.execute(query_string)
		#data = cursor.fetchall()

		#items_list=[];
		#for item in data:
		#	items_list.append({
		#		'FacilityId_Name':item[0],
		#		'FacilityName':item[1],
		#		'FacilityLatitude':str(item[2]),
		#		'FacilityLongitude':str(item[3])
		#		})
		#return {'StatusCode':'200','Items':items_list}
		
	except Exception as ex:
		return {'error':str(ex)}


@app.route('/GetFacilityNames', methods=['GET'])
def getFacilityNames(): 
	try :
		cursor = mysql.connection.cursor()
		cursor.execute('SELECT facilityname from campnear_consolidated_toorcamp')
		data = cursor.fetchall()

		items_list=[];
		for item in data:
			items_list.append({'facilityname':item[0]})
		return {'StatusCode':'200','Items':items_list}

	except Exception as ex:
		return {'error':str(ex)}


if __name__ == "__main__":
	app.run()
