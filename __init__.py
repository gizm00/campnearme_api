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

app = FlaskAPI(__name__)
mysql = MySQL(app)

app.config['MYSQL_USER'] = config.MYSQL_DATABASE_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_DATABASE_PASSWORD
app.config['MYSQL_HOST'] = config.MYSQL_DATABASE_HOST
app.config['MYSQL_DB'] = config.MYSQL_DATABASE_DBNAME

api = Api(app)

@app.route('/', methods=['GET'])
@set_renderers(HTMLRenderer)
def hello():
	return render_template('index.html')

# expect GetFacilitiesNear?lat=34.13&lon=122.42&radius=10 where lat/lon in degrees and radius in miles
@app.route('/GetFacilitiesNear', methods=['GET'])
def getFacilitiesNear():
	try :
		cursor = mysql.connection.cursor()
		lat = request.args.get('lat')
		lon = request.args.get('lon')
		radius = request.args.get('radius')
		print('got radius stuff')
		if ((not lat) or (not lon) or (not radius)):
			return {'error':'Must specify lat, lon, and radius for GetFacilitiesNear query'}
		query_string = utilities.create_radial_query(lat,lon,radius)
		cursor.execute(query_string)
		data = cursor.fetchall()

		items_list=[];
		for item in data:
			items_list.append({
				'FacilityId_Name':item[0],
				'FacilityName':item[1],
				'FacilityLatitude':str(item[2]),
				'FacilityLongitude':str(item[3])
				})
		return {'StatusCode':'200','Items':items_list}

	except Exception as ex:
		return {'error':str(ex)}


@app.route('/GetFacilityNames', methods=['GET'])
def getFacilityNames(): 
	try :
		cursor = mysql.connection.cursor()
		cursor.callproc('sp_GetFacilityNames')
		data = cursor.fetchall()

		items_list=[];
		for item in data:
			items_list.append({'FacilityName':item[0]})
		return {'StatusCode':'200','Items':items_list}

	except Exception as ex:
		return {'error':str(ex)}

class Welcome(Resource):
	@set_renderers(HTMLRenderer)
	def get(self) :
		return render_template('index.html')

class GetFacilityNames(Resource):
	def get(self):
		try :
			cursor = mysql.connection.cursor()
				#cursor = conn.cursor()
			cursor.callproc('sp_GetFacilityNames')
			data = cursor.fetchall()

			items_list=[];
			for item in data:
				i = {
					'Name':item[0]
				}
				items_list.append(i)
			return {'StatusCode':'200','Items':items_list}

		except Exception as ex:
			return {'error':str(ex)}

class HelloWorld(Resource):
	def get(self):
		return {'hello': 'world'}

#api.add_resource(Welcome, '/')
#api.add_resource(GetFacilityNames, '/GetFacilityNames')
#api.add_resource(Welcome, '/')		

if __name__ == "__main__":
	app.run()
