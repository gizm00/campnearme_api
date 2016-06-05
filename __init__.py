from flask_api import FlaskAPI
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer
from flask import render_template
import config
import mysql.connector

app = FlaskAPI(__name__)

try:
        conn = mysql.connector.connect(user=config.MYSQL_DATABASE_USER, password=config.MYSQL_DATABASE_PASSWORD,
                              host=config.MYSQL_DATABASE_HOST,
                              database=config.MYSQL_DATABASE_DBNAME)

except Exception as ex:
        print(ex)

	
cursor = conn.cursor()

@app.route("/")
@set_renderers(HTMLRenderer)
def hello():
	return render_template('index.html')

@app.route('/getData/')
def getData():
    return {'name':'roy'}

if __name__ == "__main__":
    app.run()
