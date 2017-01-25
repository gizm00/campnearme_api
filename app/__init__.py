from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask import render_template
from flask import request
import pandas as pd
import numpy as np
from geopy.distance import vincenty
from config import ProductionConfig
from database import init_db, db_session
from models import RidbFacilities, RidbCampsites, RidbFacilitiesSchema



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

"""meta = MetaData()
Base = None
#def create_app(config_object=ProductionConfig):


Base = declarative_base(db.engine)
session = None

#### models
class RidbFacilities(Base):
    __tablename__ = 'ridb_facilities_orig'
    __table_args__ = {'autoload':True}

class RidbCampsites(Base):
    __tablename__ = 'ridb_campgrounds_orig'
    __table_args__ = {'autoload':True}

#### schemas

"""

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

	facilities = db_session.query(RidbFacilities).all()
	res = facilities_schema.dump(facilities)
	return jsonify({'facilities': res.data})

	"""
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
		end_id = start_id + limit-1"""
		#query_string = "SELECT * FROM toorcamp where campnear_id between " + str(start_id) + " and " + str(end_id)
		#df_items = pd.read_sql(query_string, mysql.connection)
		#return(process_data(df_items))

	#except Exception as ex:
		#return {'error':str(ex)},status.HTTP_400_BAD_REQUEST"""

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



if __name__ == "__main__":
	#global session
	#session = loadSession()
	init_db()
	app.run()
