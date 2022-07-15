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
import csv

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



ecommerce_customer_xcl_upload = Blueprint('ecommerce_customer_xcl_upload', __name__)
api = Api(ecommerce_customer_xcl_upload,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceCustomerXclUpload',description='Ecommerce Customer Xcl Upload')

customer_postmodel = api.model('SelectCustomer', {	
	"city":fields.String,
	"retailer_store":fields.String,	
	"organisation_id":fields.Integer(required=True)
})


#----------------------Add-Multiple-Customer---------------------#

@name_space.route("/AddMultipleCustomer")
class AddMultipleCustomer(Resource):
	@api.expect(customer_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()			
		details = request.get_json()

		city = details['city']
		retailer_store = details['retailer_store']
		loc = ("siliguri_data.xls")

		#wb = xlrd.open_workbook(loc)
		#sheet = wb.sheet_by_index(0)
		#sheet.cell_value(0, 0)
 
		#for i in range(sheet.nrows):
			#now = datetime.now()
			#date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

			#date_of_creation = sheet.cell_value(i, 1)
		with open('v-k-telecom.csv', 'r') as file:
			reader = csv.reader(file, delimiter = ',')
			for row in reader:
				#date_of_creation = row[1]
				date_of_creation = row[2]
				#date_of_creation = datetime.strptime(row[1], "%Y-%m-%d")
				#first_name = row[7]
				#phoneno = row[8]
				first_name =  row[1]			
				phoneno = row[13]
				email =  row[3]
				org_password = phoneno
				role_id = 4
				admin_status = 1

				organisation_id = details['organisation_id']
				registration_type = 5

								
				insert_query = ("""INSERT INTO `admins`(`first_name`,`email`,`org_password`,
													`phoneno`,`city`,`role_id`,`registration_type`,`status`,`organisation_id`,`date_of_creation`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				data = (first_name,email,org_password,phoneno,city,role_id,registration_type,admin_status,organisation_id,date_of_creation)
				cursor.execute(insert_query,data)				

				admin_id = cursor.lastrowid

				print(admin_id)

				insert_customer_referal_code_query = ("""INSERT INTO `customer_referral`(`customer_id`,`referral_code`,`organisation_id`,`status`,`last_update_id`)
						VALUES(%s,%s,%s,%s,%s)""")
				
				last_update_id = organisation_id	

				customer_referral_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

				referal_data = (admin_id,customer_referral_code,organisation_id,admin_status,last_update_id)
				cursor.execute(insert_customer_referal_code_query,referal_data)

				get_query_city = ("""SELECT *
						FROM `retailer_store` WHERE `city` = %s and organisation_id = %s""")
				getDataCity = (details['city'],organisation_id)
				count_city = cursor.execute(get_query_city,getDataCity)

				if count_city > 0:
					city_data = cursor.fetchone()

					get_query_retailer_store = ("""SELECT *
								FROM `retailer_store_stores` WHERE `retailer_store_id` = %s and `organisation_id` = %s and `address` = %s""")
					getDataRetailerStore = (city_data['retailer_store_id'],organisation_id,retailer_store)
					count_retailer_store = cursor.execute(get_query_retailer_store,getDataRetailerStore)
					retailer_store_data = cursor.fetchone()

					insert_mapping_user_retailer = ("""INSERT INTO `user_retailer_mapping`(`user_id`,`retailer_id`,`retailer_store_id`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s)""")
									#organisation_id = 1
					last_update_id = organisation_id
					city_insert_data = (admin_id,city_data['retailer_store_id'],retailer_store_data['retailer_store_store_id'],admin_status,organisation_id,last_update_id)	
					cursor.execute(insert_mapping_user_retailer,city_insert_data)

				connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Add-Multiple-Customer---------------------#

@name_space.route("/TestCustomer")
class TestCustomer(Resource):
	@api.expect()
	def post(self):
		#loc = ("siliguri_data.xls")

		#wb = xlrd.open_workbook(loc)
		#sheet = wb.sheet_by_index(0)
		#sheet.cell_value(0, 0)
 
		#for i in range(sheet.nrows):
			#now = datetime.now()
			#date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

			#date_of_creation = sheet.cell_value(i, 1)
			#first_name =  sheet.cell_value(i, 7)
			#print(first_name)
		with open('shivay_customer.csv', 'r') as file:
			reader = csv.reader(file, delimiter = ',')
			for row in reader:
				#date_of_creation = row[1]
				#date_of_creation = datetime.strptime(row[5], "%d/%m/%Y").strftime("%Y-%m-%d")
				#date_of_creation = datetime.strptime(row[1], "%Y-%m-%d")
				
				phoneno = row[6]
				name = row[3]
				print(name)


