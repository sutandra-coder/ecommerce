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

ecommerce_autoload = Blueprint('ecommerce_autoload_api', __name__)
api = Api(ecommerce_autoload,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceAutoload',description='Ecommerce Autoload')

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

autopopulate_postmodel = api.model('SelectAutoPopulate', {	
	"organisation_id":fields.Integer(required=True),
	"auto_popultae_id":fields.List(fields.Integer)
})

#----------------------AutoPopulate---------------------#

@name_space.route("/AutoPopulate")	
class AutoPopulate(Resource):
	@api.expect(autopopulate_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		organisation_id = details['organisation_id']

		auto_popultae_ids = details.get('auto_popultae_id',[])

		for auto_popultae_id in auto_popultae_ids:

			if auto_popultae_id == 1:

				metakeylist = ["Storage","Color","Ram","Brand","Category"]
				addMetaKeyUrl = BASE_URL + "ecommerce_product/EcommerceProduct/AddMetaKey"
				

				headers = {'Content-type':'application/json', 'Accept':'application/json'}

				meta_key_text = []		
				brand_id = 0

				for metakey in metakeylist:
					if metakey == 'Storage':
						metakeyData = {
						
										  "meta_key": metakey,
										  "organisation_id": organisation_id,
										  "last_update_id": organisation_id
									 }
						metaKeyResponse = requests.post(addMetaKeyUrl,data=json.dumps(metakeyData), headers=headers).json()	
						meta_key_id = metaKeyResponse['responseList']['meta_key_id']				

						if meta_key_id :
							meta_key_id =  meta_key_id
					
							metaKeyValue = "128 GB"		
							addMetaKeyValueUrl =  BASE_URL + "ecommerce_product/EcommerceProduct/AddMetaKeyValue"
							
							metekeyValueData = {

													"meta_key_id": meta_key_id,
													"meta_key_value" : metaKeyValue,
													"image" : "",
													"organisation_id": organisation_id,
													"last_update_id": organisation_id
												}
							metaKeyValueResponse = requests.post(addMetaKeyValueUrl,data=json.dumps(metekeyValueData), headers=headers).json()
							metaKeyValueId = metaKeyValueResponse['responseList']['meta_key_value_id']
							meta_key_text.append(metaKeyValueId)


					if metakey == 'Color':
						metakeyData = {
						
										  "meta_key": metakey,
										  "organisation_id": organisation_id,
										  "last_update_id": organisation_id
									 }
						metaKeyResponse = requests.post(addMetaKeyUrl,data=json.dumps(metakeyData), headers=headers).json()	
						meta_key_id = metaKeyResponse['responseList']['meta_key_id']				

						if meta_key_id :
							meta_key_id =  meta_key_id
					
							metaKeyValue = "Black"		
							addMetaKeyValueUrl =  BASE_URL + "ecommerce_product/EcommerceProduct/AddMetaKeyValue"
							
							metekeyValueData = {

													"meta_key_id": meta_key_id,
													"meta_key_value" : metaKeyValue,
													"image" : "",
													"organisation_id": organisation_id,
													"last_update_id": organisation_id
												}
							metaKeyValueResponse = requests.post(addMetaKeyValueUrl,data=json.dumps(metekeyValueData), headers=headers).json()
							metaKeyValueId = metaKeyValueResponse['responseList']['meta_key_value_id']
							meta_key_text.append(metaKeyValueId)

					if metakey == 'Ram':
						metakeyData = {
						
										  "meta_key": metakey,
										  "organisation_id": organisation_id,
										  "last_update_id": organisation_id
									 }
						metaKeyResponse = requests.post(addMetaKeyUrl,data=json.dumps(metakeyData), headers=headers).json()	
						meta_key_id = metaKeyResponse['responseList']['meta_key_id']				

						if meta_key_id :
							meta_key_id =  meta_key_id
					 
							metaKeyValue = "6 GB"	
							addMetaKeyValueUrl =  BASE_URL + "ecommerce_product/EcommerceProduct/AddMetaKeyValue"

							
							metekeyValueData = {

													"meta_key_id": meta_key_id,
													"meta_key_value" : metaKeyValue,
													"image" : "",
													"organisation_id": organisation_id,
													"last_update_id": organisation_id
												}
							metaKeyValueResponse = requests.post(addMetaKeyValueUrl,data=json.dumps(metekeyValueData), headers=headers).json()
							metaKeyValueId = metaKeyValueResponse['responseList']['meta_key_value_id']
							meta_key_text.append(metaKeyValueId)

					if metakey == 'Brand':
						metakeyData = {
						
										  "meta_key": metakey,
										  "organisation_id": organisation_id,
										  "last_update_id": organisation_id
									 }
						metaKeyResponse = requests.post(addMetaKeyUrl,data=json.dumps(metakeyData), headers=headers).json()	
						meta_key_id = metaKeyResponse['responseList']['meta_key_id']

						if meta_key_id:
							meta_key_id = meta_key_id

							metaKeyValue = "Apple"
							addMetaKeyValueUrl =  BASE_URL + "ecommerce_product/EcommerceProduct/AddMetaKeyValue"

							metekeyValueData = {

													"meta_key_id": meta_key_id,
													"meta_key_value" : metaKeyValue,
													"image" : "https://d1lwvo1ffrod0a.cloudfront.net/117/A.png",
													"organisation_id": organisation_id,
													"last_update_id": organisation_id
												}
							metaKeyValueResponse = requests.post(addMetaKeyValueUrl,data=json.dumps(metekeyValueData), headers=headers).json()
							brand_id = metaKeyValueResponse['responseList']['meta_key_value_id']					
				

				product_meta_key_text = ','.join(map(str, meta_key_text)) 

				catalog = "Catalog1"
				addCatalogUrl = BASE_URL + "ecommerce_product/EcommerceProduct/AddCatalog"
						
				catalogData = {
									"catalog_name": catalog,
									"organisation_id": organisation_id
							  }

				catalogResponse = requests.post(addCatalogUrl,data=json.dumps(catalogData), headers=headers).json()

				if catalogResponse['responseList']['catalog_id'] :
						catalog_id = catalogResponse['responseList']['catalog_id']

						addCatalogProductWithMetaUrl = BASE_URL + "ecommerce_product/EcommerceProduct/AddCatalogProductWithMeta"
						ctalogProductWithMetaData = {
														"product_name": "Product1",												
														"product_long_description":"Product1",
														"product_short_description":"Product1",
														"catalog_id": catalog_id,
														"product_meta_code":"TESTPRODCUT"+str(organisation_id),
														"meta_key_text":product_meta_key_text,
														"in_price":100,
														"out_price":100,
														"organisation_id":organisation_id,
														"image":[
																	"https://d1lwvo1ffrod0a.cloudfront.net/117/01_Samsung-galaxy-a50-_1.png",
																	"https://d1lwvo1ffrod0a.cloudfront.net/117/02_Samsung-galaxy-a50-.png"
																],
														"discount":20,
														"product_type":"Smart Phone",
														"product_type_id":6,
														"top_selling":1,
														"best_selling":1,
														"brand_id":brand_id
													}

												
						catalogproductwithMetaResponse = 	requests.post(addCatalogProductWithMetaUrl,data=json.dumps(ctalogProductWithMetaData), headers=headers).json()

			if auto_popultae_id == 2:
				addCustomerUrl = BASE_URL + "ecommerce_customer_new/EcommerceCustomerNew/AddCustomer"
				customerData = {
									"first_name":"",
									"last_name":"",
									"email":"",
									"password":"",									
									"phoneno":112233,
									"address_line_1":"",
									"address_line_2":"",
									"city":"Kolkata",

									"registration_type":4,
									"organisation_id":organisation_id
								}
				customerResponse = requests.post(addCustomerUrl,data=json.dumps(customerData), headers=headers).json()

				if customerResponse['responseList']['user_id'] :
					user_id = customerResponse['responseList']['user_id']
					details['user_id'] = user_id

		return ({"attributes": {
				    "status_desc": "autoload_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK




