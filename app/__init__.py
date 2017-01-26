from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask import render_template
from flask import request
import pandas as pd
import numpy as np
from geopy.distance import vincenty
from config import DEBUG
from database import init_db, db_session, engine
from models import RidbFacilities, RidbFacilitySchema, RidbFacilityDetailSchema
import utilities

def process_data(df_items):
	try:
		items = df_items.to_dict(orient='records')
		count = len(df_items.index)
		return jsonify({'items':items, 'count':count})
	except Exception as ex:
		resp =  jsonify({'error':'could not process data into json format' + str(ex)})
		resp.status_code = 500
		return resp

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
facilities_schema = RidbFacilitySchema(many=True)
facility_detail_schema = RidbFacilityDetailSchema(many=True)
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
		resp = jsonify({'error': sl_dict['error']})
		resp.status_code = 400
		return resp

	start_id = sl_dict['start_id']
	limit = sl_dict['limit']
	end_id = start_id + limit-1
	facilities_query = db_session.query(RidbFacilities)
	if start_id > facilities_query.count():
		resp = jsonify({'error': "start_id out of bounds"})
		resp.status_code = 400
		return resp

	facilities = facilities_query.filter(RidbFacilities.facilityindex >= start_id,
		RidbFacilities.facilityindex <= end_id)

	count = facilities.count()
	res = facilities_schema.dump(facilities)

	return jsonify({'count':count, 'items': res.data})


# expect GetFacilitiesNear?lat=34.13&lon=122.42&radius=10 where lat/lon in degrees and radius in miles
@app.route('/GetFacilitiesNear', methods=['GET'])
def getFacilitiesNear():

	lat = request.args.get('lat')
	lon = request.args.get('lon')
	radius = request.args.get('radius')

	if ((not lat) or (not lon) or (not radius)):
		resp = jsonify({'error':'Must specify lat, lon, and radius for GetFacilitiesNear query'})
		resp.status_code = 400
		return resp

	try:
		lat = float(lat)
		lon = float(lon)
		radius = float(radius)
	except Exception as ex:
		resp = jsonify({'error':"Must supply numerical values for lat, long, and radius"})
		resp.status_code = 400
		return resp

	if (radius > 50):
		resp = jsonify({'error':'radius must be <= 50 miles'})
		resp.status_code = 400
		return resp

	query_string = utilities.create_radial_query(lat,lon,radius)
	df_items = pd.read_sql(query_string, engine)
	return process_data(df_items)


# expect paramter campnear_id
# GetFacilityDetails?campnear_id=2315
@app.route('/GetFacilityDetails', methods=['GET'])
def getFacilityDetails():
	campnear_id = request.args.get('campnear_id')
	if not campnear_id:
		resp = jsonify({'error':'campnear_id must be specified'})
		resp.status_code = 400
		return resp
	try:
		campnear_id = int(campnear_id)
	except Exception as ex:
		resp = jsonify({'error':'campnear_id must be specified as an integer'})
		resp.status_code = 400
		return resp

	facilities_query = db_session.query(RidbFacilities)
	facility_details = facilities_query.filter(RidbFacilities.facilityindex == campnear_id)
	res = facility_detail_schema.dump(facility_details)
	return jsonify({'result':res.data})

@app.route('/GetAvailableFacilities', methods=['GET'])
def getAvailableFacilities():
	facilities_query = db_session.query(RidbFacilities)

	# replace staylimit with availability
	avail_facilities = facilities_query.filter(RidbFacilities.staylimit > 0)
	res = facilities_schema.dump(avail_facilities)
	return jsonify({'items':res.data, 'count':avail_facilities.count()})

if __name__ == "__main__":
	init_db()
	app.run(debug=DEBUG)
