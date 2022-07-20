from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import haversine as hs
import requests
import calendar
import json
from threading import Thread
import time
import os   

app = Flask(__name__)
cors = CORS(app)

test_database = Blueprint('test_database_api', __name__)
api = Api(test_database,  title='Test Database API',description='Test Database API')
name_space = api.namespace('TestDatabase',description='TestDatabase')

app_version_postmodel = api.model('checkPhone',{
	"app_version":fields.String(required=True),
})

#----------------------database-connection---------------------#

def ecommerce():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='oxjkW0NuDtjKfEm5WZuP',
									db='ecommerce',
									charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

#----------------------Inventory-List---------------------#

@name_space.route("/InventoryList")	
class InventoryList(Resource):
	def get(self):
		connection = ecommerce()
		cursor = connection.cursor()

		get_query = ("""SELECT `organization_name`
					FROM `organisation_master`""")
		cursor.execute(get_query)
		Inventory_list = cursor.fetchall()	


		return ({"attributes": {"status_desc": "Inventory List",
	                            "status": "success"
	                            },
	             "responseList": Inventory_list}), status.HTTP_200_OK

#----------------------Inventory-List---------------------#

#----------------------Add-Organisation---------------------#

@name_space.route("/AddOrganisation")
class AddOrganisation(Resource):
	@api.expect(app_version_postmodel)
	def post(self):
		
		connection = ecommerce()
		cursor = connection.cursor()

		details = request.get_json()

		app_version = details['app_version']
		is_update = 1
		organsation_id = 42
		
		insert_query = ("""INSERT INTO `app_version`(`app_version`,`is_update`,`organisation_id`) 
								VALUES(%s,%s,%s)""")
		data = (app_version,is_update,organsation_id)
		cursor.execute(insert_query,data)
		organisation_id = cursor.lastrowid

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "organisation_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK	
