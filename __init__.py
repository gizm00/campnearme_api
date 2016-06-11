from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_api import FlaskAPI
from flask_api import status
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer
from flask import render_template
import config
import utilities
from flask_mysqldb import MySQL
from flask import request
import pandas as pd
import numpy as np 
from geopy.distance import vincenty

app = FlaskAPI(__name__)
mysql = MySQL(app)

app.config['MYSQL_USER'] = config.MYSQL_DATABASE_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_DATABASE_PASSWORD
app.config['MYSQL_HOST'] = config.MYSQL_DATABASE_HOST
app.config['MYSQL_DB'] = config.MYSQL_DATABASE_DBNAME

api = Api(app)

def replace_nan(value):
	try :
		if np.isnan(value):
			return None
	except:
		err = "value is not NaN convertable"

	if (value == 'NaN'):
		return None
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
                return {'NumRecords':df_items.campnear_id.count() ,'Items':items_list}

	except Exception as ex:
                return {'error':str(ex)},status.HTTP_500_INTERNAL_SERVER_ERROR


def clean_start_limit(start_id, limit):
	if not start_id:
		start_id = 0
        if not limit:
                limit = 50

        try :
                start_id = int(start_id)
        except Exception as ex:
                err_str = 'start_id must be an integer'
                return {'error':err_str}
   
        try :
                limit = int(limit)
        except Exception as ex:
                err_str = 'limit must be an integer'
                return {'error':err_str}

        if (limit > 50):
                return {'error':'limit must be <= 50'}
	

	return {'start_id':start_id,'limit':limit}

@app.route('/', methods=['GET'])
@set_renderers(HTMLRenderer)
def hello():
	return render_template('index.html')


# expect GetFacilityDetails with optional params limit (max 50) and start_index
# start_index is the campnear_id field, sequential from 0 to num records
# GetFacilityDetails?start_id=start_index&limit=int_records
@app.route('/GetAllFacilities', methods=['GET'])
def getAllFacilities():
	try :
		start_id = request.args.get('start_id')
		limit = request.args.get('limit')
		sl_dict = clean_start_limit(start_id,limit)
		try:
			start_id = sl_dict['start_id']
			limit = sl_dict['limit']
		except Exception as ex:
			return {'error': sl_dict},status.HTTP_400_BAD_REQUEST
		
		cursor = mysql.connection.cursor()
		end_id = start_id + limit-1
		query_string = "SELECT * FROM toorcamp where campnear_id between " + str(start_id) + " and " + str(end_id)
		df_items = pd.read_sql(query_string, mysql.connection)
		return(process_data(df_items))

	except Exception as ex:
		return {'error':str(ex)},status.HTTP_400_BAD_REQUEST

# expect GetFacilitiesNear?lat=34.13&lon=122.42&radius=10 where lat/lon in degrees and radius in miles
@app.route('/GetFacilitiesNear', methods=['GET'])
def getFacilitiesNear():
	try :
		cursor = mysql.connection.cursor()
		lat = float(request.args.get('lat'))
		lon = float(request.args.get('lon'))
		radius = float(request.args.get('radius'))
		
		if ((not lat) or (not lon) or (not radius)):
			return {'error':'Must specify lat, lon, and radius for GetFacilitiesNear query'}, status.HTTP_400_BAD_REQUEST
		
		if (radius > 50):
			return {'error':'radius must be <= 50 miles'}, status.HTTP_400_BAD_REQUEST

		query_string = utilities.create_radial_query(lat,lon,radius)
		df_items = pd.read_sql(query_string, mysql.connection)
                return(process_data(df_items))
		
	except Exception as ex:
		return {'error':str(ex)},status.HTTP_400_BAD_REQUEST

# expect paramter campnear_id
# GetFacilityDetails?campnear_id=2315
@app.route('/GetFacilityDetails', methods=['GET'])
def getFacilityDetails(): 
	try :
		cursor = mysql.connection.cursor()
		try :
			campnear_id = int(request.args.get('campnear_id'))
		except Exception as ex:
			return{'error':'campnear_id must be specified as an integer'},status.HTTP_400_BAD_REQUEST
		

		query_string = 'SELECT * from toorcamp where campnear_id=' + str(campnear_id)
		df_items = pd.read_sql(query_string, mysql.connection)
                return(process_data(df_items))

	except Exception as ex:
		return {'error':str(ex)},status.HTTP_400_BAD_REQUEST

@app.route('/GetAvailableFacilities', methods=['GET'])
def getAvailableFacilities():
	try: 
		cursor = mysql.connection.cursor()
		query_string = 'SELECT * from toorcamp where sites_available > 0'
                df_items = pd.read_sql(query_string, mysql.connection)
                return(process_data(df_items))

        except Exception as ex:
                return {'error':str(ex)},status.HTTP_400_BAD_REQUEST

# expect /GetDistanceBetween?lat1=44.12&lon1=-122.23&lat2=43.54&lon2=-122.45

@app.route('/GetDistanceBetween', methods=['GET'])
def getDistanceBetween() :
	try :
		lat1 = float(request.args.get('lat1'))
                lon1 = float(request.args.get('lon1'))
		lat2 = float(request.args.get('lat2'))
                lon2 = float(request.args.get('lon2'))	
	except:
		return {'error':'GetDistanceBetween: float values lat1,lon1,lat2,lon2 expected'},status.HTTP_400_BAD_REQUEST 

	try:
		distance = vincenty((lat1,lon1),(lat2,lon2)).miles
	except Exception as ex:
		return {'error':str(ex)},status.HTTP_500_INTERNAL_SERVER_ERROR

	return {'distance':distance}

if __name__ == "__main__":
	app.run()
