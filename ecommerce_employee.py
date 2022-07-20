from flask import Flask, request, jsonify, json
from flask_api import status
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

app = Flask(__name__)
cors = CORS(app)

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

ecommerce_employee = Blueprint('ecommerce_employee_api', __name__)
api = Api(ecommerce_employee,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceEmployee',description='Ecommerce Employee')

employee_postmodel = api.model('SelectEmployee', {	
	"phoneno":fields.String(required=True),	
	"name":fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"retailer_store_id":fields.Integer(required=True),
	"retailer_store_store_id":fields.Integer(required=True)
})

login_postmodel = api.model('loginCustomer',{
	"phoneno":fields.String(required=True),
	"organisation_id":fields.Integer(required=True)
})

employee_putmodel = api.model('updateEmployee',{	
	"name":fields.String,
	"retailer_store_id":fields.Integer,
	"retailer_store_store_id":fields.Integer
})

#----------------------Add-Employee---------------------#

@name_space.route("/AddEmployee")
class AddEmployee(Resource):
	@api.expect(employee_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		phoneno = details['phoneno']
		organisation_id = details['organisation_id']
		retailer_store_id = details['retailer_store_id']
		retailer_store_store_id = details['retailer_store_store_id']
		name = 	details['name']	
		last_update_id =  details['organisation_id']
		employee_status = 1
		role = 1



		get_query = ("""SELECT *
					FROM `employee` WHERE `phoneno` = %s and `organisation_id` = %s and `retailer_store_id` = %s and `retailer_store_store_id` = %s""")
		get_data = (phoneno,organisation_id,retailer_store_id,retailer_store_store_id)

		count_data = cursor.execute(get_query,get_data)

		if count_data > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "employee_details",
			    		"status": "error",
			    		"message":"Employee Already Exist"
			    	},
			    	"responseList":{"phoneno":data['phoneno']} }), status.HTTP_200_OK
		else:

			insert_query = ("""INSERT INTO `employee`(`name`,`phoneno`,`status`,`organisation_id`,`retailer_store_id`,`role`,`retailer_store_store_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
			data = (name,phoneno,employee_status,organisation_id,retailer_store_id,role,retailer_store_store_id,last_update_id)
			cursor.execute(insert_query,data)
			employee_id = cursor.lastrowid
			details['employee_id'] = employee_id

			connection.commit()
			cursor.close()

			return ({"attributes": {
					    "status_desc": "employee_details",
					    "status": "success"
					},
					"responseList":details}), status.HTTP_200_OK		

#----------------------Add-Employee---------------------#

#-----------------------Employee-Login---------------------#

@name_space.route("/Login")
class Login(Resource):
	@api.expect(login_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		phoneno = details['phoneno']
		organisation_id = details['organisation_id']

		get_query = ("""SELECT e.`name` employee_name,e.`phoneno` employee_phone_no,e.`retailer_store_id`,e.`retailer_store_store_id`,e.`status`,o.*
					FROM `employee` e
					INNER JOIN `organisation_master`o on o.`organisation_id` = e.`organisation_id`
					WHERE e.`phoneno` = %s and e.`organisation_id` = %s""")
		get_data = (phoneno,organisation_id)

		count_data = cursor.execute(get_query,get_data)

		if count_data > 0:
			data = cursor.fetchone()
			if data['status'] == 0:
				return ({"attributes": {
			    		"status_desc": "employee_details",
			    		"status": "error",
			    		"message":"Employee Is Inactive Please Contact Administrator"
			    	},
			    	"responseList":{"phoneno":phoneno} }), status.HTTP_200_OK
			else:
				get_retailer_store_query = (""" SELECT * FROM `retailer_store` WHERE `retailer_store_id` = %s """)
				getRetailerStoreData = (data['retailer_store_id'])
				count_retailer_store = cursor.execute(get_retailer_store_query,getRetailerStoreData)

				if count_retailer_store > 0:
					retailer_store_data =  cursor.fetchone()
					data['reatiler_city'] = retailer_store_data['city']
				else:
					data['reatiler_city'] = ""

				get_retailer_store_store_query = (""" SELECT * FROM `retailer_store_stores` WHERE `retailer_store_store_id` = %s """)
				getRetailerStorStoreeData = (data['retailer_store_store_id'])
				count_retailer_store_stores = cursor.execute(get_retailer_store_store_query,getRetailerStorStoreeData)

				if count_retailer_store_stores > 0:
					retailer_store_stores_data =  cursor.fetchone()
					data['reatiler_store_address'] = retailer_store_stores_data['address']
					data['reatiler_store_latitude'] = retailer_store_stores_data['latitude']
					data['reatiler_store_longitude'] = retailer_store_stores_data['longitude']
					data['reatiler_store_phoneno'] = retailer_store_stores_data['phoneno']
				else:
					data['reatiler_store_address'] = ""
					data['reatiler_store_latitude'] = ""
					data['reatiler_store_longitude'] = ""
					data['reatiler_store_phoneno'] = ""

				data['date_of_lastlogin'] = str(data['date_of_lastlogin'])
				data['last_update_ts'] = str(data['last_update_ts'])


				return ({"attributes": {
					    "status_desc": "employee_details",
					    "status": "success"
					},
					"responseList":data}), status.HTTP_200_OK
		else:
			return ({"attributes": {
			    		"status_desc": "employee_details",
			    		"status": "error",
			    		"message":"Employee Phone No Is Not Valid"
			    	},
			    	"responseList":{"phoneno":phoneno} }), status.HTTP_200_OK


#-----------------------Employee-Login---------------------#

#----------------------Get-Employee-List---------------------#
@name_space.route("/getEmployeeList/<int:organisation_id>")	
class getEmployeeList(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		

		get_query = ("""SELECT * FROM `employee` WHERE `organisation_id` = %s """)
		getData = (organisation_id)
		cursor.execute(get_query,getData)
		employee_data = cursor.fetchall()


		for key,data in enumerate(employee_data):
			get_retailer_store_query = (""" SELECT * FROM `retailer_store` WHERE `retailer_store_id` = %s """)
			getRetailerStoreData = (data['retailer_store_id'])
			count_retailer_store = cursor.execute(get_retailer_store_query,getRetailerStoreData)

			if count_retailer_store > 0:
				retailer_store_data =  cursor.fetchone()
				employee_data[key]['reatiler_city'] = retailer_store_data['city']
			else:
				employee_data[key]['reatiler_city'] = ""

			get_retailer_store_store_query = (""" SELECT * FROM `retailer_store_stores` WHERE `retailer_store_store_id` = %s """)
			getRetailerStorStoreeData = (data['retailer_store_store_id'])
			count_retailer_store_stores = cursor.execute(get_retailer_store_store_query,getRetailerStorStoreeData)

			if count_retailer_store_stores > 0:
				retailer_store_stores_data =  cursor.fetchone()
				employee_data[key]['reatiler_store_address'] = retailer_store_stores_data['address']
				employee_data[key]['reatiler_store_latitude'] = retailer_store_stores_data['latitude']
				employee_data[key]['reatiler_store_longitude'] = retailer_store_stores_data['longitude']
				employee_data[key]['reatiler_store_phoneno'] = retailer_store_stores_data['phoneno']
			else:
				employee_data[key]['reatiler_store_address'] = ""
				employee_data[key]['reatiler_store_latitude'] = ""
				employee_data[key]['reatiler_store_longitude'] = ""
				employee_data[key]['reatiler_store_phoneno'] = ""

			employee_data[key]['last_update_ts'] = str(data['last_update_ts'])	

		return ({"attributes": {
					    "status_desc": "employee_details",
					    "status": "success"
					},
					"responseList":employee_data}), status.HTTP_200_OK

#----------------------Get-Employee-List---------------------#

#----------------------Update-Employee-Information---------------------#

@name_space.route("/updateEmployeeInformation/<int:employee_id>")
class updateEmployeeInformation(Resource):
	@api.expect(employee_putmodel)
	def put(self, employee_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "name" in details:
			name = details['name']
			update_query = ("""UPDATE `employee` SET `name` = %s
				WHERE `employee_id` = %s """)
			update_data = (name,employee_id)
			cursor.execute(update_query,update_data)

		if details and "retailer_store_id" in details:
			retailer_store_id = details['retailer_store_id']
			update_query = ("""UPDATE `employee` SET `retailer_store_id` = %s
				WHERE `employee_id` = %s """)
			update_data = (retailer_store_id,employee_id)
			cursor.execute(update_query,update_data)

		if details and "retailer_store_store_id" in details:
			retailer_store_store_id = details['retailer_store_store_id']
			update_query = ("""UPDATE `employee` SET `retailer_store_store_id` = %s
				WHERE `employee_id` = %s """)
			update_data = (retailer_store_store_id,employee_id)
			cursor.execute(update_query,update_data)


		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "employee_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK



