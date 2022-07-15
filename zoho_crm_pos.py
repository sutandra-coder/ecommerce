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
from werkzeug import secure_filename
import requests
import calendar
import json
import csv
from zcrmsdk import ZCRMRestClient, ZohoOAuth, ZCRMRecord, ZCRMOrganization, ZCRMModule, ZCRMUser, ZCRMException, ZCRMInventoryLineItem

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

zoho_crm_pos = Blueprint('zoho_crm_pos_api', __name__)
api = Api(zoho_crm_pos,  title='Zoho Crm Pos API',description='Zoho Crm Pos API')
name_space = api.namespace('ZohoCrmPos',description='Zoho Crm Pos API')

customer_list_postmodel = api.model('customer_list_postmodel',{
	"organisation_id":fields.Integer(required=True),
	"store":fields.String(required=True)
})

config = {
	"sandbox":"true",
	"applicationLogFilePath":"./Log",
	"client_id":"1000.DUWCGKAK2N1WEHVWQWINI68ST5XJ6T",
	"client_secret":"464617935b5f0fee64a9d1fa48533d410300798592",
	"redirect_uri":"http://www.retail360.in/",
	"accounts_url":"https://accounts.zoho.com",
	"token_persistence_path":".",
	"currentUserEmail":"sanjoy@myelsa.io"
}

#----------------------Import-Product---------------------#

@name_space.route("/ImportProduct")
class ImportProduct(Resource):		
	def post(self):
		details = request.get_json()

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
		
		userEmail = "sutandra.mazumder@gmail.com"
		#oauth_tokens = oauth_client.generate_access_token(grant_token)

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)

		with open('DURGAPUR-P.csv', 'r') as file:
			reader = csv.reader(file, delimiter = ',')
			for row in reader:
				Brand =  row[2]
				product = row[3]
				variation = row[4]
				Product_Name = Brand+" "+product+" ("+variation+")"
				Unit_Price = row[5]
				Product_Category = "Smart Phone"

				record = ZCRMRecord.get_instance('Products')  # Module API Name
				record.set_field_value('Product_Category', Product_Category)		
				#record.set_field_value('Product_Code', Product_Code)
				record.set_field_value('Product_Name', Product_Name)
				record.set_field_value('Brand', Brand)
				record.set_field_value('Unit_Price', Unit_Price)

				resp = record.create()

				print(resp.status_code)
				print(resp.code)
				print(resp.details)
				print(resp.message)
				print(resp.status)

#----------------------Import-Product---------------------#

#----------------------Import-Customer---------------------#

@name_space.route("/ImportCustomer")
class ImportCustomer(Resource):		
	def post(self):
		details = request.get_json()

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
		
		userEmail = "sutandra.mazumder@gmail.com"
		#oauth_tokens = oauth_client.generate_access_token(grant_token)

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)

		with open('DURGAPUR.csv', 'r') as file:
			reader = csv.reader(file, delimiter = ',')
			for row in reader:
				try:
					Customer_Name =  row[7]
					split_customer_name = Convert(Customer_Name)
					#print(split_customer_name)
					if len(split_customer_name) == 2:
						First_Name = split_customer_name[0]
						Last_Name = split_customer_name[1]
					elif len(split_customer_name) == 1:
						Last_Name = split_customer_name[0]
						First_Name = ''
					
					Phone = row[8]
					store = "Durgapur"

					record = ZCRMRecord.get_instance('Contacts')  # Module API Name
					record.set_field_value('First_Name', First_Name)		
					record.set_field_value('Last_Name', Last_Name)	
					record.set_field_value('Phone', Phone)
					record.set_field_value('store', store)	

					resp = record.create()
					print(resp.status_code)
					print(resp.code)
					print(resp.details)
					print(resp.message)
					print(resp.status)

				except ZCRMException as ex:
					print(ex.status_code)
					print(ex.error_message)
					print(ex.error_code)
					print(ex.error_details)
					print(ex.error_content)	

def Convert(string):
    li = list(string.split(" "))
    return li


#----------------------Import-Customer---------------------#

@name_space.route("/ImportCustomerFromXcel")
class ImportCustomerFromXcel(Resource):	
	@api.expect(customer_list_postmodel)	
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()

		organisation_id = details['organisation_id']
		store = details['store']

		get_query = ("""SELECT *
			FROM `organisation_zoho_details` WHERE `organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		data = cursor.fetchone()

		if data['account_type'] == 1:
			sandbox = "true"
		else:
			sandbox = "true"

		config = {
			"sandbox": sandbox,
			"applicationLogFilePath":"./Log",
			"client_id": data['client_id'],
			"client_secret": data['client_secret'],
			"redirect_uri": data['redirect_uri'],
			"accounts_url":data['accounts_url'],
			"token_persistence_path":".",
			"currentUserEmail":data['current_user_email']
		}

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
			
		userEmail = "sutandra.mazumder@gmail.com"
		#oauth_tokens = oauth_client.generate_access_token(grant_token)

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)

		with open('shivay_customer.csv', 'r') as file:
			reader = csv.reader(file, delimiter = ',')
			for row in reader:
				Phone = row[6]
				print(Phone)

				try:

					module_ins = ZCRMModule.get_instance('Contacts')
					resp = module_ins.search_records_by_phone(Phone)

					print(resp.status)

				except ZCRMException as ex:

					Logged_In = "Never Logged In"
					Lead_Source = "Online Store"

					First_Name = ""
					Last_Name = row[3]
					store = store

					record = ZCRMRecord.get_instance('Contacts')  # Module API Name
					record.set_field_value('First_Name', First_Name)		
					record.set_field_value('Last_Name', Last_Name)	
					record.set_field_value('store', store)
					record.set_field_value('Phone', Phone)
					record.set_field_value('Logged_In', Logged_In)
					record.set_field_value('Lead_Source', Lead_Source)
					
					resp = record.create()

					update_query = ("""UPDATE `admins` SET `zoho_customer_id` = %s
								WHERE `phoneno` = %s and `organisation_id` = %s""")
					update_data = (resp.details['id'],Phone,organisation_id)
					cursor.execute(update_query,update_data)

					connection.commit()

		return ({"attributes": {
					"status_desc": "customer_list",
					"status": "success"
				},
				"responseList":"Imported Successfully"}), status.HTTP_200_OK


#----------------------Import-Customer---------------------#

#----------------------Import-Sales-Order---------------------#

@name_space.route("/ImportSalesFromXcel")
class ImportSalesFromXcel(Resource):	
	@api.expect(customer_list_postmodel)	
	def post(self):
		details = request.get_json()
		connection = mysql_connection()
		cursor = connection.cursor()

		organisation_id = details['organisation_id']
		store = details['store']

		with open('DURGAPUR-S.csv', 'r') as file:
			reader = csv.reader(file, delimiter = ',')
			product_ids =[]
			for row in reader:
				storage = row[9]
				Color = row[4]
				ram = row[10]
				product_name = row[3]

				get_storage_query = (""" SELECT *
					FROM `meta_key_value_master` WHERE `meta_key_value` = %s and `organisation_id` = 1 and `meta_key_id` = 3""")
				get_storage_data = (storage)

				cursor.execute(get_storage_query,get_storage_data)

				storage_data = cursor.fetchone()

				meta_key_text = []

				meta_key_text.append(storage_data['meta_key_value_id'])

				get_color_query = (""" SELECT *
					FROM `meta_key_value_master` WHERE `meta_key_value` = %s and `organisation_id` = 1 and `meta_key_id` = 5""")
				get_color_data = (Color)

				cursor.execute(get_color_query,get_color_data)

				color_data = cursor.fetchone()

				meta_key_text.append(color_data['meta_key_value_id'])

				get_ram_query = (""" SELECT *
					FROM `meta_key_value_master` WHERE `meta_key_value` = %s and `organisation_id` = 1 and `meta_key_id` = 4""")
				get_ram_data = (ram)

				cursor.execute(get_ram_query,get_ram_data)

				ram_data = cursor.fetchone()

				meta_key_text.append(ram_data['meta_key_value_id'])

				meta_key_text = ','.join([str(elem) for elem in meta_key_text])

				get_product_query = ("""  SELECT *
					FROM `product` WHERE `product_name` = %s """)
				get_product_data = (product_name)
				cursor.execute(get_product_query,get_product_data)
				product_data = cursor.fetchone()

				get_product_meta_query = ("""  SELECT *
					FROM `product_meta` WHERE `product_id` = %s and `meta_key_text` = %s""")
				get_product_meta_data = (product_data['product_id'],meta_key_text)

				cursor.execute(get_product_meta_query,get_product_meta_data)
				print(cursor._last_executed)
				product_meta = cursor.fetchone()

				Product_Meta_Id = str(product_meta['product_meta_id'])

				print(Product_Meta_Id)

				try:

					get_query = ("""SELECT *
						FROM `organisation_zoho_details` WHERE `organisation_id` = %s""")

					get_data = (organisation_id)
					cursor.execute(get_query,get_data)

					data = cursor.fetchone()

					if data['account_type'] == 1:
						sandbox = "true"
					else:
						sandbox = "false"

					config = {
						"sandbox": sandbox,
						"applicationLogFilePath":"./Log",
						"client_id": data['client_id'],
						"client_secret": data['client_secret'],
						"redirect_uri": data['redirect_uri'],
						"accounts_url":data['accounts_url'],
						"apiBaseUrl":"https://www.zohoapis.in",
						"token_persistence_path":".",
						"currentUserEmail":data['current_user_email']
					}

					ZCRMRestClient.initialize(config)
					oauth_client = ZohoOAuth.get_client_instance()
					grant_token = data['grant_token']
						
					userEmail = "sutandra.mazumder@gmail.com"
					#oauth_tokens = oauth_client.generate_access_token(grant_token)

					oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

					print(oauth_tokens)

					module_ins = ZCRMModule.get_instance('Products')
					resp = module_ins.search_records_by_criteria('(Product_Meta_Id:equals:'+Product_Meta_Id+')')

					record_ins_arr = resp.data
					for record_ins in record_ins_arr:
						product_ids.append(record_ins.entity_id)					
					

				except ZCRMException as ex:
					print(ex.status_code)
					print(ex.error_message)
					print(ex.error_code)
					print(ex.error_details)
					print(ex.error_content)

			print(product_ids)

				

