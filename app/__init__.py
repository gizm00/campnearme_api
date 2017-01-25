from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask import render_template
from flask import request
import pandas as pd
import numpy as np
from geopy.distance import vincenty
from config import ProductionConfig
from database import init_db, db_session, engine
from models import RidbFacilities, RidbCampsites, RidbFacilitiesSchema
import utilities



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
		items = df_items.to_dict(orient='records')
		count = len(df_items.index)
		return {'items':items, 'count':count}
	except Exception as ex:
		return {'error':'could not process data into json format' + str(ex), 'status_code':500}

def clean_start_limit(start_id, limit):
	if not start_id:
		# facilityindex starts at 1
		start_id = 1
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



app = Flask(__name__)
ridb_facilities = RidbFacilities()
ridb_campsites = RidbCampsites()
facilities_schema = RidbFacilitiesSchema(many=True)
#db.init_app(app)

#### api
@app.route('/', methods=['GET'])
def hello():
	return render_template('index.html')

# expect GetFacilityDetails with optional params limit (max 50) and start_index
# start_index is the campnear_id field, sequential from 0 to num records
# GetFacilityDetails?start_id=start_index&limit=int_records
@app.route('/GetAllFacilities', methods=['GET'])
def getAllFacilities():
	# look for optional params
	start_id = request.args.get('start_id')
	limit = request.args.get('limit')
	sl_dict = clean_start_limit(start_id,limit)
	if 'error' in sl_dict:
		return jsonify({'error': sl_dict['error'], 'status_code': 404})

	start_id = sl_dict['start_id']
	limit = sl_dict['limit']
	end_id = start_id + limit-1
	facilities_query = db_session.query(RidbFacilities)
	if start_id > facilities_query.count():
		return jsonify({'error': "start_id out of bounds", 'status_code':404})

	facilities = facilities_query.filter(RidbFacilities.facilityindex >= start_id,
		RidbFacilities.facilityindex <= end_id)

	count = facilities.count()
	res = facilities_schema.dump(facilities)
	print(jsonify({'items':res.data}))
	return jsonify({'count':count, 'items': res.data})


# expect GetFacilitiesNear?lat=34.13&lon=122.42&radius=10 where lat/lon in degrees and radius in miles
@app.route('/GetFacilitiesNear', methods=['GET'])
def getFacilitiesNear():

	lat = request.args.get('lat')
	lon = request.args.get('lon')
	radius = request.args.get('radius')

	if ((not lat) or (not lon) or (not radius)):
		return jsonify({'error':'Must specify lat, lon, and radius for GetFacilitiesNear query', 'status_code':404})

	try:
		lat = float(lat)
		lon = float(lon)
		radius = float(radius)
	except Exception as ex:
		return jsonify({'error':"Must supply numerical values for lat, long, and radius", 'status_code':404})

	if (radius > 50):
		return jsonify({'error':'radius must be <= 50 miles', 'status_code':404})

	query_string = utilities.create_radial_query(lat,lon,radius)
	df_items = pd.read_sql(query_string, engine)
	return jsonify(process_data(df_items))



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



if __name__ == "__main__":
	#global session
	#session = loadSession()
	init_db()
	app.run(debug=True)
