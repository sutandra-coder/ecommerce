from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
import requests
import calendar
import json
import random, string

app = Flask(__name__)
cors = CORS(app)

ecommerce_app_settings = Blueprint('ecommerce_app_settings_api', __name__)
api = Api(ecommerce_app_settings,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceAppSettings',description='Ecommerce Customer')


#----------------------database-connection---------------------#
'''def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def mysql_connection():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

update_app_version_settings_model = api.model('update_app_version_settings_model',{
	"app_version":fields.String,
	"is_update":fields.Integer
})


#----------------------Get-App-Version---------------------#
@name_space.route("/getappVersion/<int:organisation_id>")	
class organisationDetails(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *				
									FROM `app_version`						
									WHERE `organisation_id` = %s """)
		getData = (organisation_id)
		count_version = cursor.execute(get_query,getData)

		if count_version > 0:
			version_data = cursor.fetchone()
			version_data['last_update_ts'] = str(version_data['last_update_ts'])
		else:
			version_data = {}


		return ({"attributes": {
				    "status_desc": "app_version_details",
				    "status": "success"
				},
				"responseList":version_data}), status.HTTP_200_OK

#----------------------Get-App-Version---------------------#

#----------------------Update-App-Version---------------------#

@name_space.route("/UpdateAppVersion/<int:organisation_id>")
class UpdateAppVersion(Resource):
	@api.expect(update_app_version_settings_model)
	def put(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "app_version" in details:
			app_version = details['app_version']
			is_update = details['is_update']			

			get_app_version_settings_query = ("""SELECT *				
									FROM `app_version`						
									WHERE `organisation_id` = %s """)
			getDataAppVersionSettings = (organisation_id)
			count_app_version_setings = cursor.execute(get_app_version_settings_query,getDataAppVersionSettings)

			if count_app_version_setings > 0:									
				update_query = ("""UPDATE `app_version` SET `app_version` = %s,`is_update` = %s
						WHERE `organisation_id` = %s """)
				update_data = (app_version,is_update,organisation_id)
				cursor.execute(update_query,update_data)
			else:
				
				insert_query = ("""INSERT INTO `app_version`(`app_version`,`is_update`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s)""")
				data = (app_version,is_update,organisation_id,organisation_id)
				cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update app version",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-App-Version---------------------#