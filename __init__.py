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
                return {'StatusCode':'200','NumRecords':df_items.campnear_id.count() ,'Items':items_list}

	except Exception as ex:
                return {'error':str(ex)}


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
			return {'error': sl_dict}
		
#		if not start_id:
#			start_id = 0
#		if not limit:
#			limit = 50
#
#		try :
#			start_id = int(start_id)
#		except Exception as ex:
#			err_str = 'start_id must be an integer'
#			return {'error':err_str}
#		try :
#                       limit = int(limit)
#                except Exception as ex:
#                        err_str = 'limit must be an integer'
#                        return {'error':err_str}

#		if (limit > 50):
#			return {'error':'limit must be <= 50'}

		cursor = mysql.connection.cursor()
		end_id = start_id + limit-1
		query_string = "SELECT * FROM campnear_consolidated_toorcamp where campnear_id between " + str(start_id) + " and " + str(end_id)
		df_items = pd.read_sql(query_string, mysql.connection)
		return(process_data(df_items))

	except Exception as ex:
		return {'error':str(ex)}

# expect GetFacilitiesNear?lat=34.13&lon=122.42&radius=10 where lat/lon in degrees and radius in miles
# optional argument limit with number of records to fetch, i.e.
# GetFacilitiesNear?lat=34.13&lon=122.42&radius=10&limit=50
@app.route('/GetFacilitiesNear', methods=['GET'])
def getFacilitiesNear():
	try :
		cursor = mysql.connection.cursor()
		lat = float(request.args.get('lat'))
		lon = float(request.args.get('lon'))
		radius = float(request.args.get('radius'))
		start_id = request.args.get('start_id')
		limit = request.args.get('limit')
		
		if ((not lat) or (not lon) or (not radius)):
			return {'error':'Must specify lat, lon, and radius for GetFacilitiesNear query'}
		query_string = utilities.create_radial_query(lat,lon,radius,start_id,limit)
		df_items = pd.read_sql(query_string, mysql.connection)
                return(process_data(df_items))
		
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
