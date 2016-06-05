from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
#from flask_api import FlaskAPI
#from flask_api.decorators import set_renderers
#from flask_api.renderers import HTMLRenderer
#from flask import render_template
import config
from flask_mysqldb import MySQL

app = Flask(__name__)
mysql = MySQL(app)

app.config['MYSQL_USER'] = config.MYSQL_DATABASE_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_DATABASE_PASSWORD
app.config['MYSQL_HOST'] = config.MYSQL_DATABASE_HOST
app.config['MYSQL_DB'] = config.MYSQL_DATABASE_DBNAME

api = Api(app)

class Welcome(Resource):
	def get(self) :
		#@set_renderers(HTMLRenderer)
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

api.add_resource(HelloWorld, '/')
api.add_resource(GetFacilityNames, '/GetFacilityNames')
#api.add_resource(Welcome, '/')		

if __name__ == "__main__":
    app.run()
