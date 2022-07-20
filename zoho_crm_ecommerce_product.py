from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import requests
import calendar
import json
import math
from zcrmsdk import ZCRMRestClient, ZohoOAuth, ZCRMRecord, ZCRMOrganization, ZCRMModule, ZCRMUser, ZCRMException, ZCRMInventoryLineItem
#import zcrmsdk

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

zoho_crm_ecommerce_product = Blueprint('zoho_crm_ecommerce_product_api', __name__)
api = Api(zoho_crm_ecommerce_product,  title='Zoho Crm Ecommrce Product API',description='Zoho Crm Ecommerce Product API')
name_space = api.namespace('ZohoCrmEcommerceProduct',description='Zoho Crm Ecommerce Product API')

product_postmodel = api.model('record_postmodel',{			
	"Product_Category":fields.String(required=True),
	"Product_Code":fields.String(required=True),
	"Product_Name":fields.String(required=True),
	"Brand":fields.String(required=True),
	"Unit_Price":fields.String(required=True)
})

contact_postmodel = api.model('contact_postmodel',{
	"First_Name":fields.String(required=True),
	"Last_Name":fields.String(required=True),
	"store":fields.String(required=True)
})

search_postmodel = api.model('search_postmodel',{
	"PhoneNo":fields.String(required=True)
})

product_import_postmodel = api.model('product_import_postmodel',{
	"organisation_id":fields.Integer(required=True),
	"Product_Category":fields.String(required=True),
	"Product_Name":fields.String(required=True),
	"Brand":fields.String(required=True),
	"Unit_Price":fields.String(required=True),
	"Storage":fields.String(required=True),
	"Ram":fields.String(required=True),
	"Color":fields.String(required=True),
	"Product_Meta_Id":fields.String(required=True),
	"Product_Code":fields.String(required=True),
	"Description":fields.String(required=True)
})

product_list_postmodel = api.model('product_list_postmodel',{
	"organisation_id":fields.Integer(required=True),
	"page":fields.Integer(required=True)
})

customer_list_postmodel = api.model('customer_list_postmodel',{
	"organisation_id":fields.Integer(required=True),
	"page":fields.Integer(required=True)
})

customer_import_postmodel = api.model('customer_import_postmodel',{
	"First_Name":fields.String(required=True),
	"Last_Name":fields.String(required=True),
	"Email":fields.String(required=True),
	"store":fields.String(required=True),
	"City":fields.String(required=True),
	"Phone":fields.String(required=True),
	"Loggedin_Status":fields.String(required=True),
	"Lead_Source":fields.String(required=True),
	"organisation_id":fields.Integer(required=True)
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

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/zoho_crm_ecommerce_product/'


#----------------------Get-Product-By-Id--------------------#

@name_space.route("/getProductByProductId")	
class getProductByProductId(Resource):
	def get(self):
		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.3a9732f840d73414932f028b8489a88e.e833430b08fdaa71d50c5114d05b07e4"
		#oauth_tokens = oauth_client.generate_access_token(grant_token)
		userEmail = "sanjoy@myelsa.io"

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)
		#ZCRMRestClient.initialize(config)
		#oAuth_client = ZohoOAuth.get_client_instance()
		#resp = ZCRMOrganization.get_all_users(1,20)

		product_record_instance = ZCRMRecord.get_instance('Products',4821214000000447978)
		product_record = product_record_instance.get()		
		print(product_record.data)
		#print(product_record.data.field_data)
		product_record_data = product_record.data.field_data

		return ({"attributes": {
			    		"status_desc": "Record List",
			    		"status": "success",
			    		"message":""
			    	},
			    	"responseList": product_record_data}), status.HTTP_200_OK

#----------------------Get-Product-By-Id--------------------#

#----------------------Create-Product---------------------#

@name_space.route("/createProduct")
class createProduct(Resource):	
	@api.expect(product_postmodel)
	def post(self):
		details = request.get_json()

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
		
		userEmail = "sutandra.mazumder@gmail.com"
		#oauth_tokens = oauth_client.generate_access_token(grant_token)

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)

		Product_Category = details['Product_Category']
		Product_Code = details['Product_Code']
		Product_Name = details['Product_Name']
		Brand = details['Brand']
		Unit_Price = details['Unit_Price']

		record = ZCRMRecord.get_instance('Products')  # Module API Name
		record.set_field_value('Product_Category', Product_Category)		
		record.set_field_value('Product_Code', Product_Code)
		record.set_field_value('Product_Name', Product_Name)
		record.set_field_value('Brand', Brand)
		record.set_field_value('Unit_Price', Unit_Price)

		resp = record.create()
		print(resp.status_code)
		print(resp.code)
		print(resp.details)
		print(resp.message)
		print(resp.status)


		return ({"attributes": {
			    	"status_desc": "product",
			    	"status": "success"
			    },
			    "responseList":resp.message}), status.HTTP_200_OK


#----------------------Create-Product---------------------#

#----------------------Get-Sales-Order-By-Id--------------------#

@name_space.route("/getSalesOrderById")	
class getSalesOrderById(Resource):
	def get(self):
		try:
			ZCRMRestClient.initialize(config)
			oauth_client = ZohoOAuth.get_client_instance()
			grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
			#oauth_tokens = oauth_client.generate_access_token(grant_token)
			userEmail = "sanjoy@myelsa.io"

			oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

			print(oauth_tokens)

			module_ins = ZCRMRecord.get_instance('Sales_Orders',4821214000000338988)# Module API Name
			resp = module_ins.get()# Related list id
			print(resp.data.line_items)

			for line_item in resp.data.line_items:				
				print(line_item.id)
				print(line_item.product.get_field_value('Product_Code'))
				print(line_item.product.get_field_value('Product_Name'))

		except ZCRMException as ex:
			print(ex.status_code)
			print(ex.error_message)
			print(ex.error_code)
			print(ex.error_details)
			print(ex.error_content)

		return ({"attributes": {
			    	"status_desc": "product",
			    	"status": "success"
			    },
			    "responseList":resp.data.field_data}), status.HTTP_200_OK

		
		
		

		
#----------------------Get-Product-By-Id--------------------#

#----------------------Create-Sales-Order---------------------#

@name_space.route("/createSalesOrder")
class createSalesOrder(Resource):	
	@api.expect(product_postmodel)
	def post(self):
		details = request.get_json()

		try:

			ZCRMRestClient.initialize(config)
			oauth_client = ZohoOAuth.get_client_instance()
			grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
			
			userEmail = "sutandra.mazumder@gmail.com"
			#oauth_tokens = oauth_client.generate_access_token(grant_token)

			oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

			print(oauth_tokens)

			record = ZCRMRecord.get_instance('Sales_Orders')  # Module API Name
			print(record)
			record.set_field_value('Subject','Order Galaxy A10 A105(Black)')			
			record.set_field_value('Product_Name', 'product_name1')
			record.set_field_value('Grand_Total', '8490')			
			#record.set_field_value('Discount', '0')

			user = ZCRMRecord.get_instance('Contacts', 4821214000000364159)  # user id and user name
			user.name = 'KARAN PASWAN'
			user.id = 4821214000000364159
			record.set_field_value('Contact_Name', user)

	        # Following methods are being used only by Inventory modules        
			line_item = ZCRMInventoryLineItem.get_instance(ZCRMRecord.get_instance('Products', 4821214000000368008))  # module api name and record id
			line_item.discount = 0
			line_item.list_price = 8490
			line_item.description = 'Product Description'
			line_item.quantity = 1
			record.add_line_item(line_item)        
			
			resp = record.create()
			print(resp.status_code)
			print(resp.code)
			print(resp.details)
			print(resp.message)
			print(resp.status)
			print(resp.data.entity_id)
			print(resp.data.created_by.id)
			print(resp.data.created_time)

		except ZCRMException as ex:
			print(ex.status_code)
			print(ex.error_message)
			print(ex.error_code)
			print(ex.error_details)
			print(ex.error_content)

#----------------------Create-Sales-Order---------------------#

#----------------------Convert-Lead-to-contact---------------------#

@name_space.route("/convertLeadToContact")
class convertLeadToContact(Resource):	
	def post(self):
		try:
			ZCRMRestClient.initialize(config)
			oauth_client = ZohoOAuth.get_client_instance()
			grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
			
			userEmail = "sutandra.mazumder@gmail.com"
			#oauth_tokens = oauth_client.generate_access_token(grant_token)

			oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

			print(oauth_tokens)

			record = ZCRMRecord.get_instance('Leads', 4821214000000364039) # module api name and record id
			potential_record = ZCRMRecord.get_instance('Deals')
			potential_record.set_field_value('Deal_Name', 'SAI1')
			potential_record.set_field_value('Closing_Date', '2017-10-10')
			potential_record.set_field_value('Stage', 'Needs Analysis')
			assign_to_user = ZCRMUser.get_instance(4821214000000325001, 'Sanjoy Paul') # user id and name
			resp = record.convert(potential_record,assign_to_user)
			print(resp)
			#print(resp[APIConstants.ACCOUNTS])
			#print(resp[APIConstants.DEALS])
			#print(resp[APIConstants.CONTACTS])

		except ZCRMException as ex:
			print(ex.status_code)
			print(ex.error_message)
			print(ex.error_code)
			print(ex.error_details)
			print(ex.error_content)	


#----------------------Get-Contact-By-Id--------------------#

@name_space.route("/getContactById")	
class getContactById(Resource):
	def get(self):
		try:
			ZCRMRestClient.initialize(config)
			oauth_client = ZohoOAuth.get_client_instance()
			grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
			#oauth_tokens = oauth_client.generate_access_token(grant_token)
			userEmail = "sanjoy@myelsa.io"

			oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

			print(oauth_tokens)		

			lead_record_instance = ZCRMRecord.get_instance('Contacts',4821214000000368001)
			lead_response = lead_record_instance.get()
			print(lead_response.data)
			print(lead_response.data.field_data)
			print(json.dumps(lead_response.data.field_data))

		except ZCRMException as ex:
			print(ex.status_code)
			print(ex.error_message)
			print(ex.error_code)
			print(ex.error_details)
			print(ex.error_content)	

#----------------------Get-Contact-By-Id--------------------#

#----------------------Create-Contact---------------------#

@name_space.route("/createContact")
class createContact(Resource):	
	@api.expect(contact_postmodel)
	def post(self):
		details = request.get_json()

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
		
		userEmail = "sutandra.mazumder@gmail.com"
		#oauth_tokens = oauth_client.generate_access_token(grant_token)

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)

		First_Name = details['First_Name']
		Last_Name = details['Last_Name']
		store = details['store']

		record = ZCRMRecord.get_instance('Contacts')  # Module API Name
		record.set_field_value('First_Name', First_Name)		
		record.set_field_value('Last_Name', Last_Name)	
		record.set_field_value('store', store)	

		resp = record.create()
		print(resp.status_code)
		print(resp.code)
		print(resp.details)
		print(resp.message)
		print(resp.status)


		return ({"attributes": {
			    	"status_desc": "product",
			    	"status": "success"
			    },
			    "responseList":resp.message}), status.HTTP_200_OK


#----------------------Create-Contact---------------------#


#---------------------Search---------------------#

@name_space.route("/SearchByPhoneNo")
class SearchByPhoneNo(Resource):	
	@api.expect(search_postmodel)
	def post(self):
		details = request.get_json()

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
		
		userEmail = "sutandra.mazumder@gmail.com"
		#oauth_tokens = oauth_client.generate_access_token(grant_token)

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)

		PhoneNo = details['PhoneNo']
		
		module_ins = ZCRMModule.get_instance('Contacts')
		resp = module_ins.search_records_by_phone(PhoneNo)

		record_ins_arr = resp.data

		for record_ins in record_ins_arr:
			print(record_ins.entity_id)
			print(record_ins.get_field_value('Last_Name'))
			

#---------------------Search---------------------#

#---------------------Search---------------------#

@name_space.route("/SearchByProductName")
class SearchByProductName(Resource):	
	@api.expect(search_postmodel)
	def post(self):
		try:
			details = request.get_json()

			ZCRMRestClient.initialize(config)
			oauth_client = ZohoOAuth.get_client_instance()
			grant_token = "1000.585b31409aa8399ea66f685acc074c9a.1b9e762e14b9a20badc7f4afe67501b3"
			
			userEmail = "sutandra.mazumder@gmail.com"
			#oauth_tokens = oauth_client.generate_access_token(grant_token)

			oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

			print(oauth_tokens)

			PhoneNo = details['PhoneNo']
			
			module_ins = ZCRMModule.get_instance('Products')
			resp = module_ins.search_records_by_criteria('(Product_Name:equals:S20) and(Brand:equals:Samsung) and (Color:equals:Pink) and(Ram:equals:8GB)')

			record_ins_arr = resp.data

			for record_ins in record_ins_arr:
				print(record_ins.get_field_value('Product_Name'))

		except ZCRMException as ex:
			print(ex.status_code)
			print(ex.error_message)
			print(ex.error_code)
			print(ex.error_details)
			print(ex.error_content)	

		'''record_ins_arr = resp.data

		for record_ins in record_ins_arr:
			print(record_ins.entity_id)
			print(record_ins.get_field_value('Last_Name'))'''
			

#---------------------Search---------------------#

#---------------------Product-Import-Into-Zoho---------------------#

@name_space.route("/productImportintoZoho")
class productImportintoZoho(Resource):	
	@api.expect(product_import_postmodel)
	def post(self):
		details = request.get_json()

		connection = mysql_connection()
		cursor = connection.cursor()

		organisation_id = details['organisation_id']

		get_query = ("""SELECT *
			FROM `organisation_zoho_details` WHERE `organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		data = cursor.fetchone()

		if data['account_type'] == 1:
			sandbox = "True"
		else:
			sandbox = "False"

		config = {
			"sandbox": sandbox,
			"applicationLogFilePath":"/home/ubuntu/Log",
			"client_id": data['client_id'],
			"client_secret": data['client_secret'],
			"redirect_uri": data['redirect_uri'],
			"accounts_url":data['accounts_url'],
			"apiBaseUrl":"https://www.zohoapis.in",
			"token_persistence_path":"/home/ubuntu/flaskapp",
			"currentUserEmail":data['current_user_email']
		}

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = data['grant_token']
			
		userEmail = data['current_user_email']
		#oauth_tokens = oauth_client.generate_access_token(grant_token)

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)

		Product_Category = details['Product_Category']
		Product_Code = details['Product_Code']
		Product_Name = details['Product_Name']
		Brand = details['Brand']
		Unit_Price = details['Unit_Price']
		Storage = details['Storage']
		Ram = details['Ram']
		Color = details['Color']
		Product_Meta_Id = details['Product_Meta_Id']
		Description = details['Description']

		try:
			try: 
				module_ins = ZCRMModule.get_instance('Products')
				resp = module_ins.search_records_by_criteria('(Product_Meta_Id:equals:'+Product_Meta_Id+')')

				resp_info = resp.info
				product_count = resp_info.count	

				
				return ({"attributes": {
			    		"status_desc": "product_details",
			    		"status": "success"
			    	},
			    	"responseList":{"id":0}}), status.HTTP_200_OK

			except ZCRMException as ex:		
				record = ZCRMRecord.get_instance('Products')  # Module API Name
				record.set_field_value('Product_Category', Product_Category)		
				record.set_field_value('Product_Code', Product_Code)
				record.set_field_value('Product_Name', Product_Name)
				record.set_field_value('Brand', Brand)
				record.set_field_value('Unit_Price', Unit_Price)
				record.set_field_value('Capacity', Storage)
				record.set_field_value('Ram', Ram)
				record.set_field_value('Color', Color)
				record.set_field_value('Product_Meta_Id', Product_Meta_Id)
				record.set_field_value('Description', Description)

				resp_product = record.create()

				print(resp_product.details)
				

				return ({"attributes": {
			    		"status_desc": "product_details",
			    		"status": "success"
			    	},
			    	"responseList":resp_product.details}), status.HTTP_200_OK
		except ZCRMException as ex:
			print(ex.status_code)
			print(ex.error_message)
			print(ex.error_code)
			print(ex.error_details)
			print(ex.error_content)

			return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":{"id":0}}), status.HTTP_200_OK

#---------------------Product-Import-Into-Zoho---------------------#

#---------------------Product-List-From-Organisation---------------------#

@name_space.route("/productListFromOrganisation")
class productListFromOrganisation(Resource):	
	@api.expect(product_list_postmodel)
	def post(self):
		details = request.get_json()

		connection = mysql_connection()
		cursor = connection.cursor()

		organisation_id = details['organisation_id']
		page = details['page']

		if page == 1:
			offset = 0			
		else:
			offset = page * 50

		get_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,
								pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,mkvm.`meta_key_value` brand,c.`category_name`
							 	FROM `product` p						 	 						 	
						 		INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`	
						 		INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`	
						 		INNER JOIN `category` c ON c.`category_id` = p.`category_id`
						 		INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
						 		INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = pbm.`brand_id`			 			 
								WHERE pom.`organisation_id` = %s and pbm.`organisation_id` = %s and c.`organisation_id` = %s LIMIT %s,50""")
		getProductData = (organisation_id,organisation_id,organisation_id,offset)
		count_product_data = cursor.execute(get_product_query,getProductData)

		search_meta = cursor.fetchall()

		for key,data in enumerate(search_meta):
			#print(data['product_meta_id'])

			if data['meta_key_text'] :
				a_string = data['meta_key_text']
				a_list = a_string.split(',')

				met_key = {}

				for a in a_list:
					get_query_key_value = ("""SELECT `meta_key_id`,`meta_key_value`
															FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)
					getdata_key_value = (a)
					cursor.execute(get_query_key_value,getdata_key_value)
					met_key_value_data = cursor.fetchone()

					get_query_key = ("""SELECT `meta_key`
															FROM `meta_key_master` WHERE `meta_key_id` = %s """)
					getdata_key = (met_key_value_data['meta_key_id'])
					cursor.execute(get_query_key,getdata_key)
					met_key_data = cursor.fetchone()

					met_key.update({met_key_data['meta_key']:met_key_value_data['meta_key_value']})

					search_meta[key]['met_key_value'] = met_key

		for key,data in enumerate(search_meta):
			Product_Name = data['product_name']
			Product_Code = data['product_meta_code']
			Brand = data['brand']
			Product_Category = data['category_name']
			Product_Meta_Id = data['product_meta_id']

			if data['meta_key_text']:

				if data['met_key_value'] and "Storage" in  data['met_key_value']:
					Capacity =  data['met_key_value']['Storage']
				else:
					Capacity = ""

				if data['met_key_value'] and "Color" in  data['met_key_value']:
					Color =  data['met_key_value']['Color']
				else:
					Color = ""

				if data['met_key_value'] and "Ram" in  data['met_key_value']:
					Ram =  data['met_key_value']['Ram']
				else:
					Ram = ""
			else:
				Capacity = ""
				Color = ""
				Ram = ""
			
			Unit_Price = data['out_price']

			Description = data['product_short_description']						

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			Url = BASE_URL + "ZohoCrmEcommerceProduct/productImportintoZoho"
			payloadhData = {
					"organisation_id":organisation_id,
					"Product_Name": Product_Name,
					"Product_Code": Product_Code,
					"Brand":Brand,
					"Product_Category":Product_Category,
					"Storage":Capacity,
					"Color":Color,
					"Ram":Ram,
					"Unit_Price":str(Unit_Price),
					"Product_Meta_Id":str(Product_Meta_Id),
					"Description":Description
			}

			print(payloadhData)

			create_product_to_zoho = requests.post(Url,data=json.dumps(payloadhData), headers=headers).json()

			#print(create_product_to_zoho['responseList']['id'])			

			insert_query = ("""INSERT INTO `product_meta_zoho_id_mapping`(`product_meta_id`,`product_id`,`product_zoho_id`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")

			data = (data['product_meta_id'],data['product_id'],create_product_to_zoho['responseList']['id'],organisation_id,organisation_id)
			cursor.execute(insert_query,data)

		if page > 0:		
			get_product_query_count = ("""SELECT count(*) as product_count
							 	FROM `product` p						 	 						 	
						 		INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`	
						 		INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`	
						 		INNER JOIN `category` c ON c.`category_id` = p.`category_id`
						 		INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
						 		INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = pbm.`brand_id`			 			 
								WHERE pom.`organisation_id` = %s and pbm.`organisation_id` = %s and c.`organisation_id` = %s""")
			
			getProductData = (organisation_id,organisation_id,organisation_id)
			count_product_data = cursor.execute(get_product_query_count,getProductData)		
			product_data_count = cursor.fetchone()

			page_count = math.trunc(product_data_count['product_count']/50)

			if page_count == 0:
				page_count = 1
			else:
				page_count = page_count + 1
		else:
			get_product_query_count = ("""SELECT count(*) as product_count
							 	FROM `product` p						 	 						 	
						 		INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`	
						 		INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`	
						 		INNER JOIN `category` c ON c.`category_id` = p.`category_id`
						 		INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
						 		INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = pbm.`brand_id`			 			 
								WHERE pom.`organisation_id` = %s and pbm.`organisation_id` = %s and c.`organisation_id` = %s""")
			
			getProductData = (organisation_id,organisation_id,organisation_id)
			page_count = cursor.execute(get_product_query_count,getProductData)	


		return ({"attributes": {
					"status_desc": "product_list",
					"status": "success",
					"page":page,
					"page_count":page_count
				},
				"responseList":search_meta}), status.HTTP_200_OK
		
#---------------------Product-List-From-Organisation---------------------#

#----------------------Update-Product-Information---------------------#

@name_space.route("/updateProductInfomaion/<int:zoho_product_meta_id>/<int:organisation_id>")	
class updateProductInfomaion(Resource):
	@api.expect()
	def put(self,zoho_product_meta_id,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()				

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

		get_product_meta_query = ("""SELECT *
			FROM `product_meta_zoho_id_mapping` WHERE `organisation_id` = %s and `product_zoho_id` = %s""")
		get_product_meta_data = (organisation_id,str(zoho_product_meta_id))
		cursor.execute(get_product_meta_query,get_product_meta_data)
		print(cursor._last_executed)
		product_meta_data = cursor.fetchone()

		print(str(product_meta_data['product_meta_id']))

		record = ZCRMRecord.get_instance('Products', zoho_product_meta_id)  # Module API Name
		#record.set_field_value('id', 4819682000000363001)
		record.set_field_value('Product_Meta_Id', str(product_meta_data['product_meta_id']))		
		# Actions to be triggered
		trigger = ["approval", "workflow", "blueprint"]
		# Process to be run
		process = ["review_process"]

		resp = record.update()
		print(resp.status_code)
		print(resp.code)
		print(resp.details)
		print(resp.message)
		print(resp.status)
		print(resp.data.entity_id)
		print(resp.data.created_by.id)
		print(resp.data.created_time)


#----------------------Update-Product-Information---------------------#

#---------------------Customer-List-From-Organisation---------------------#

@name_space.route("/customerListFromOrganisation")
class customerListFromOrganisation(Resource):	
	@api.expect(customer_list_postmodel)
	def post(self):
		details = request.get_json()

		connection = mysql_connection()
		cursor = connection.cursor()

		organisation_id = details['organisation_id']
		page = details['page']

		if page == 1:
			offset = 0			
		else:
			offset = page * 1000

		get_customer_query = ("""SELECT a.*,urm.`retailer_store_id`,rss.`store_name`
							 	FROM `admins` a
							 	INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`	
							 	INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = urm.`retailer_store_id`						 							 					 			 
								WHERE a.`organisation_id` = %s LIMIT %s,1000""")
		getCustomerData = (organisation_id,offset)
		count_customer_data = cursor.execute(get_customer_query,getCustomerData)

		search_meta = cursor.fetchall()

		for key,data in enumerate(search_meta):			
			search_meta[key]['last_updated_date'] = str(data['last_updated_date'])
			search_meta[key]['date_of_lastlogin'] = str(data['date_of_lastlogin'])
			search_meta[key]['date_of_creation'] = str(data['date_of_creation'])
			search_meta[key]['date_of_update'] = str(data['date_of_update'])

			if data['first_name'] == '':
				Last_Name = data['store_name']+" Customer"
			else:
				Last_Name = data['first_name']

			if data['loggedin_status'] == 1:
				loggedin_status = "logged In" 
			else:
				loggedin_status = "Never Logged In"

			if data['registration_type'] == 4 or data['registration_type'] == 1:
				Lead_Source = "Online Store"
			else:
				Lead_Source = "Facebook"

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			Url = BASE_URL + "ZohoCrmEcommerceProduct/customerImportintoZoho"
			payloadhData = {
					"First_Name":"",
					"Last_Name":  Last_Name,
					"Email": data['email'],
					"store": data['store_name'],
					"City": data['city'],
					"Phone": data['phoneno'],
					"Loggedin_Status":loggedin_status,
					"Lead_Source":Lead_Source,
					"organisation_id":organisation_id
			}


			print(payloadhData)
			create_customer_to_zoho = requests.post(Url,data=json.dumps(payloadhData), headers=headers).json()
			if int(create_customer_to_zoho['responseList']['id']) > 0:
				print(create_customer_to_zoho['responseList']['id'])

				update_query = ("""UPDATE `admins` SET `zoho_customer_id` = %s
									WHERE `phoneno` = %s and `organisation_id` = %s""")
				update_data = (create_customer_to_zoho['responseList']['id'],data['phoneno'],organisation_id)
				cursor.execute(update_query,update_data)

				print(cursor._last_executed)

				connection.commit()
			

		if page > 0:		
			get_customer_query_count = ("""SELECT count(*) as customer_count
										 	FROM `admins` a
										 	INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`	
										 	INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = urm.`retailer_store_id`						 							 					 			 
											WHERE a.`organisation_id` = %s""")
			
			getCustomerData = (organisation_id)
			count_customer_data = cursor.execute(get_customer_query_count,getCustomerData)		
			customer_data_count = cursor.fetchone()

			page_count = math.trunc(customer_data_count['customer_count']/1000)

			if page_count == 0:
				page_count = 1
			else:
				page_count = page_count + 1
		else:
			get_customer_query_count = ("""SELECT count(*) as customer_count
										 	FROM `admins` a
										 	INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`	
										 	INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = urm.`retailer_store_id`						 							 					 			 
											WHERE a.`organisation_id` = %s""")
			
			getCustomerData = (organisation_id)
			page_count = cursor.execute(get_customer_query_count,getCustomerData)



		return ({"attributes": {
					"status_desc": "customer_list",
					"status": "success",
					"page":page,
					"page_count":page_count
				},
				"responseList":search_meta}), status.HTTP_200_OK

#---------------------Customer-List-From-Organisation---------------------#

#---------------------Customer-Import-Into-Zoho---------------------#

@name_space.route("/customerImportintoZoho")
class customerImportintoZoho(Resource):	
	@api.expect(customer_import_postmodel)
	def post(self):
		details = request.get_json()

		connection = mysql_connection()
		cursor = connection.cursor()

		organisation_id = details['organisation_id']

		get_query = ("""SELECT *
			FROM `organisation_zoho_details` WHERE `organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		data = cursor.fetchone()

		if data['account_type'] == 1:
			sandbox = "True"
		else:
			sandbox = "False"

		config = {
			"sandbox": sandbox,
			"applicationLogFilePath":"/home/ubuntu/Log",
			"client_id": data['client_id'],
			"client_secret": data['client_secret'],
			"redirect_uri": data['redirect_uri'],
			"accounts_url":data['accounts_url'],
			"apiBaseUrl":"https://www.zohoapis.in",
			"token_persistence_path":"/home/ubuntu/flaskapp",
			"currentUserEmail":data['current_user_email']
		}

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = data['grant_token']
			
		userEmail = data['current_user_email']
		#oauth_tokens = oauth_client.generate_access_token(grant_token)

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)

		First_Name = details['First_Name']
		Last_Name = details['Last_Name']
		Email = details['Email']
		store = details['store']
		City = details['City']
		Phone = details['Phone']
		Logged_In = details['Loggedin_Status']
		Lead_Source = details['Lead_Source']

		try:

			module_ins = ZCRMModule.get_instance('Contacts')
			resp = module_ins.search_records_by_phone(Phone)

			record_ins_arr = resp.data

			return ({"attributes": {
			    		"status_desc": "product_details",
			    		"status": "success"
			    	},
			    	"responseList":{"id":0}}), status.HTTP_200_OK

		except ZCRMException as ex:
			try:
				record = ZCRMRecord.get_instance('Contacts')  # Module API Name
				record.set_field_value('First_Name', First_Name)		
				record.set_field_value('Last_Name', Last_Name)	
				record.set_field_value('Email', Email)	
				record.set_field_value('store', store)	
				record.set_field_value('City', City)
				record.set_field_value('Phone', Phone)
				record.set_field_value('Logged_In', Logged_In)
				record.set_field_value('Lead_Source', Lead_Source)

				resp = record.create()

				print(resp.details)
					

				return ({"attributes": {
				    		"status_desc": "product_details",
				    		"status": "success"
				    	},
				    	"responseList":resp.details}), status.HTTP_200_OK
			except ZCRMException as ex:
				print(ex.status_code)
				print(ex.error_message)
				print(ex.error_code)
				print(ex.error_details)
				print(ex.error_content)
				return ({"attributes": {
				    		"status_desc": "product_details",
				    		"status": "success"
				    	},
				    	"responseList":{"id":0}}), status.HTTP_200_OK

def get_records():
    import requests

    url = 'https://www.zohoapis.com/crm/v2/Sales_Orders/4821214000000338988'

    headers = {
        'Authorization': 'Zoho-oauthtoken 1000.5db1c0fd945408a3c8b137992672491c.b91248f047f2b0dc567ea4f69b9b8ab4',
        'If-Modified-Since': '2020-03-19T17:59:50+05:30'
    }

    parameters = {
        'approved': 'both'
    }

    print(headers)

    response = requests.get(url=url, headers=headers, params=parameters)

    #print(response)

    if response is not None:
        print("HTTP Status Code : " + str(response.status_code))

        print(response.json())


def get_modules():
    import requests

    url = 'https://www.zohoapis.com/crm/v2/settings/modules'

    headers = {
        'Authorization': 'Zoho-oauthtoken 1000.5db1c0fd945408a3c8b137992672491c.b91248f047f2b0dc567ea4f69b9b8ab4'
    }

    response = requests.get(url=url, headers=headers)

    if response is not None:
        print("HTTP Status Code : " + str(response.status_code))

        print(response.json())

def search_records():
    import requests

    url = 'https://www.zohoapis.com/crm/v2/Leads/search'

    headers = {
        'Authorization': 'Zoho-oauthtoken 1000.04be928e4a96XXXXXXXXXXXXX68.0b9eXXXXXXXXXXXX60396e268',
    }

    parameters = {
        'criteria': '((Last_Name:starts_with:Last Name) and (Company:starts_with:fasf\\\\(123\\\\) K))',
        'email': 'newlead@zoho.com',
        'phone': '234567890',
        'word': 'First Name Last Name',
        'converted': 'both',
        'approved': 'both',
        'page': 1,
        'per_page': 15
    }

    response = requests.get(url=url, headers=headers, params=parameters)

    if response is not None:
        print("HTTP Status Code : " + str(response.status_code))

        print(response.json())



