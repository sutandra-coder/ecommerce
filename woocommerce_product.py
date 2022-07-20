from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
# import urllib3, socket
# from urllib3.connection import HTTPConnection
import requests
import calendar
import json
from threading import Thread
from woocommerce import API
import time
import os  
import math


app = Flask(__name__)
cors = CORS(app)

woocommerce_product = Blueprint('woocommerce_product', __name__)
api = Api(woocommerce_product,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('WoocommerceProduct',description='Woocommerce Product')

#base_url = "http://shivaay.xyz/"
base_url = "http://ec2-3-141-41-236.us-east-2.compute.amazonaws.com/"

src = api.model('src', {
	"src":fields.String(),
	})

create_product =  api.model('create_product', {
	"category_id":fields.Integer(),
	"sku":fields.String(),
	"product_name":fields.String(),
	"regular_price":fields.String(),
	"sale_price":fields.String(),
	"stock_status":fields.String(),
	"long_description":fields.String(),
	"short_description":fields.String(),
	"storage":fields.String(),
	"ram":fields.String(),
	"color":fields.String(),
	"image_url":fields.List(fields.Nested(src))
})

create_customer = api.model('create_customer', {
	"first_name":fields.String()
})

customer_list_postmodel = api.model('customer_list_postmodel',{
	"organisation_id":fields.Integer(required=True),
	"page":fields.Integer(required=True)
})

#----------------------------------------------------------#
wcapi = API(
		    url= base_url,
		    consumer_key="ck_c5b75df2beceb7e805c566fd126a12f8ae0def36",
		    consumer_secret="cs_67f95ca8f2fd135b9fa3ef30982cd6e2d69905f0",
		    wp_api=True,
		    version="wc/v3",
			timeout=600
		)

#----------------------database-connection---------------------#
def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

#----------------------------------------------------------#
@name_space.route("/CreateProduct")
class CreateProduct(Resource):
	@api.expect(create_product)
	def post(self):
		
		details = request.get_json()
		regular_price = details.get('regular_price')

		sale_price = details.get('sale_price')

		data = {
			    "name": details.get('product_name'),
			    "type": "variable",
			    "sku": details.get('sku'),
			    "regular_price":details.get('regular_price'),
				"sale_price":details.get('sale_price'),
				"stock_status":details.get('stock_status'),
			    "description": details.get('long_description'),
			    "short_description": details.get('short_description'),
			    "categories": [
			        {
			            "id":details.get('category_id')
			        }
			    ],
			    "images": details.get('image_url'),
			    "attributes": [
					        {
						        'id': 3, 
						        'name': 'color', 
						        'position': 0, 
						        'visible': True, 
						        'variation': True, 
						        'options': ['Matte Aqua','Matte black']

					        },
					        {
						        'id': 1, 
						        'name': 'ram', 
						        'position': 1, 
						        'visible': True, 
						        'variation': True, 
						        'options': ['6 GB','8 GB']
					        },
					        {
						        'id': 2, 
						        'name': 'storage', 
						        'position': 2, 
						        'visible': True, 
						        'variation': True, 
						        'options': ['128 GB']
					        }
				    	]
			}
		#print(data)
		product_res = wcapi.post("products", data).json()

		if product_res.get('id'):
			product_id = product_res.get('id')
			print(product_id)			
			print("products/"+str(product_id)+"/variations")

			vdata1 = {
			    "regular_price": "23999",	
			    "sale_price":"20999",		   
			    "attributes": [
			        {
			            "id": 3,
			            "option": "Matte Aqua"
			        },
			        {
			            "id": 2,
			            "option": "128 GB"
			        },
			        {
			        	"id": 2,
			            "option": "6 GB"
			        }
			    ]
			}
		
			print(wcapi.post("products/"+str(product_id)+"/variations", vdata1).json())

			vdata2 = {
			    "regular_price": "25999",	
			    "sale_price":"22999",		   
			    "attributes": [
			        {
			            "id": 3,
			            "option": "Matte Black"
			        },
			        {
			            "id": 2,
			            "option": "128 GB"
			        },
			        {
			        	"id": 2,
			            "option": "8 GB"
			        }
			    ]
			}
		
			print(wcapi.post("products/"+str(product_id)+"/variations", vdata2).json())
		if product_res.get('name'):
			msg = "Added"
		else:
			msg = "Not Added"
			
		return ({"attributes": {
								"status_desc": "Product Details",
                                "status": "success"
                                },
	             "responseList": msg}), status.HTTP_200_OK

#----------------------------------------------------------#

@name_space.route("/productDetail")	
class productDetail(Resource):	
	def get(self):
		products = wcapi.get("products/20446").json()

		return ({"attributes": {
								"status_desc": "Product Details",
                                "status": "success"
                                },
	             "responseList": products}), status.HTTP_200_OK

#----------------------------------------------------------#

@name_space.route("/productVariantDetails")	
class productVariantDetails(Resource):	
	def get(self):
		products = wcapi.get("products/20409/variations/20409").json()

		return ({"attributes": {
								"status_desc": "Product Details",
                                "status": "success"
                                },
	             "responseList": products}), status.HTTP_200_OK


#---------------------------Product-List-------------------------------#
@name_space.route("/productList/<int:organisation_id>/<int:page>")	
class productList(Resource):	
	def get(self,organisation_id,page):

		connection = mysql_connection()
		cursor = connection.cursor()

		if page == 1:
			offset = 0
		else:
			offset = (page - 1)*10

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,`category_id`
				FROM `product` p				
				INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
				WHERE pom.`organisation_id` = %s limit %s,10""")
		getdata = (organisation_id,offset)
		cursor.execute(get_query,getdata)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_product_price_query = ("""SELECT `in_price`,`out_price`
				FROM `product_meta` where `product_id` = %s""")
			get_product_price_data = (data['product_id'])
			product_price_count = cursor.execute(get_product_price_query,get_product_price_data)

			if product_price_count > 0:
				product_price = cursor.fetchone()
				product_data[key]['in_price'] = product_price['in_price']
				product_data[key]['out_price'] = product_price['out_price']
			else:
				product_data[key]['in_price'] = 0
				product_data[key]['out_price'] = 0

			get_product_meta_query = ("""SELECT `product_meta_id` FROM `product_meta` where `product_id` = %s""")
			get_product_meta_data = (data['product_id'])
			product_meta_count = cursor.execute(get_product_meta_query,get_product_meta_data)

			if product_meta_count > 0:
				product_meta_data =  cursor.fetchone()
				get_query_image = ("""SELECT pmi.`image` as `src`  
					FROM  `product_meta_images` pmi
					WHERE pmi.`product_meta_id` = %s and pmi.`is_gallery` = 0""")
				getdata_image = (product_meta_data['product_meta_id'])
				product_image_count = cursor.execute(get_query_image,getdata_image)

				if product_image_count >0 :
					product_image = cursor.fetchall()
					product_data[key]['image'] = product_image
				else:
					product_data[key]['image'] = []
			else:
				product_data[key]['image'] = []

			get_meta_query = ("""SELECT DISTINCT pm.`meta_key_text`
			FROM `product_meta` pm
			WHERE pm.`product_id` = %s """)
			getmetadata = (data['product_id'])
			cursor.execute(get_meta_query,getmetadata)
			product_meta_data = cursor.fetchall()
			

			for pmkey,pmdata in enumerate(product_meta_data):
				a_string_meta = pmdata['meta_key_text']
				a_list_meta = a_string_meta.split(',')			

				met_key_meta = {}

				for a_meta in a_list_meta:

					get_query_key_value_meta = ("""SELECT mkvm.`meta_key_id`,`meta_key_value`,mkm.`meta_key` 
						FROM `meta_key_value_master` mkvm 
						INNER JOIN `meta_key_master` mkm ON mkvm.`meta_key_id` = mkm.`meta_key_id`
						WHERE `meta_key_value_id` = %s """)
					getdata_key_value_meta = (a_meta)
					cursor.execute(get_query_key_value_meta,getdata_key_value_meta)
					met_key_value_data_meta = cursor.fetchone()				

					met_key_meta[met_key_value_data_meta['meta_key']] = met_key_value_data_meta['meta_key_value']

				product_meta_data[pmkey]['meta_key_value'] = met_key_meta

				#print(product_meta_data)
			Storage = []
			Color = []
			Ram = []

			for pkey,pdata in enumerate(product_meta_data):
				if  pdata['meta_key_value'] and "Storage" in  pdata['meta_key_value']:
					Storage.append(pdata['meta_key_value']['Storage'])			
				if  pdata['meta_key_value'] and "Ram" in  pdata['meta_key_value']:
					Ram.append(pdata['meta_key_value']['Ram'])
				if  pdata['meta_key_value'] and "Color" in  pdata['meta_key_value']:
					Color.append(pdata['meta_key_value']['Color'])
					
			product_data[key]['Storage'] = unique(Storage)			
			product_data[key]['Ram'] = unique(Ram)
			product_data[key]['Color'] = unique(Color)	

			get_product_meta_query = ("""SELECT `product_meta_id`,`meta_key_text`,`in_price`,`out_price`
				FROM `product_meta` where product_id = %s""")
			get_product_meta_data = (data['product_id'])
			get_product_meta_count = cursor.execute(get_product_meta_query,get_product_meta_data)

			if get_product_meta_count > 0:
				product_meta = cursor.fetchall()

				for ppmkey,ppmdata in enumerate(product_meta):
					a_string = ppmdata['meta_key_text']
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

					product_meta[ppmkey]['met_key_value'] = met_key

					get_query_image = ("""SELECT `image`					 
						FROM`product_meta_images`
						WHERE `product_meta_id` = %s and `is_gallery` = 0""")
					getdata_image = (ppmdata['product_meta_id'])
					product_image_count = cursor.execute(get_query_image,getdata_image)

					if product_image_count >0 :
						product_image = cursor.fetchone()
						product_meta[ppmkey]['meta_image'] = product_image['image']
					else:
						product_meta[ppmkey]['meta_image'] = ""	

				product_data[key]['product_meta'] = product_meta
			else:
				product_data[key]['product_meta'] = []

		for fkey,fdata in enumerate(product_data):			
			if fdata['category_id'] == 6:
				category_id = 185
			if fdata['category_id'] == 7:
					category_id = 186
			if fdata['category_id'] == 8:
				category_id = 187
			data = {
				    "name": fdata['product_name'],
				    "type": "variable",
				    "sku": "",
				    "regular_price":str(fdata['in_price']),
					"sale_price":str(fdata['out_price']),
					"stock_status":"instock",
				    "description":fdata['product_long_description'],
				    "short_description": fdata['product_short_description'],
				    "categories": [
				        {
				            "id":category_id
				        }
				    ],
				    "images": fdata['image'],
				    "attributes": [
						        {
							        'id': 3, 
							        'name': 'color', 
							        'position': 0, 
							        'visible': True, 
							        'variation': True, 
							        'options': fdata['Color']

						        },
						        {
							        'id': 4, 
							        'name': 'ram', 
							        'position': 1, 
							        'visible': True, 
							        'variation': True, 
							        'options': fdata['Ram']
						        },
						        {
							        'id': 5, 
							        'name': 'storage', 
							        'position': 2, 
							        'visible': True, 
							        'variation': True, 
							        'options': fdata['Storage']
						        }
					    	]
				}

			product_res = wcapi.post("products", data).json()

			print(product_res)

			if product_res.get('id'):
				product_id = product_res.get('id')
				print(product_id)			
				print("products/"+str(product_id)+"/variations")

				for fmkey,fmdata in enumerate(fdata['product_meta']):

					if fmdata['met_key_value'] and "Color" in fmdata['met_key_value']:
						Color = fmdata['met_key_value']['Color'] 
					else:
						Color = ""

					if fmdata['met_key_value'] and "Storage" in fmdata['met_key_value']:
						Storage = fmdata['met_key_value']['Storage']
					else:
						Storage = ""

					if fmdata['met_key_value'] and "Ram" in fmdata['met_key_value']:
						Ram = fmdata['met_key_value']['Ram']
					else:
						Ram = ""

					vdata = {
					    "regular_price": str(fmdata['in_price']),	
					    "sale_price":str(fmdata['out_price']),	
					    "image": {"src":fmdata['meta_image']},		     
					    "attributes": [
						        {
						            "id": 3,
						            "option": Color
						        },
						        {
						            "id": 5,
						            "option": Storage
						        },
						        {
						        	"id": 4,
						            "option": Ram
						        }
					    	]
						}

					print(wcapi.post("products/"+str(product_id)+"/variations", vdata).json())

				

		get_query_count = ("""SELECT count(*) as product_count
				FROM `product` p
				INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
				INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
				WHERE pom.`organisation_id` = %s""")
		get_query_count_data = (organisation_id)
		product_count = cursor.execute(get_query_count,get_query_count_data)

		product_data_count = cursor.fetchone()

		page_count = math.trunc(product_data_count['product_count']/10)


		if page_count == 0:
			page_count = 1
		else:
			page_count = page_count + 1	

		return ({"attributes": {
					    "status_desc": "product_list",
					    "status": "success",					   
					    "page_count":page_count,
		    			"page": page
				},
				"responseList":product_data}), status.HTTP_200_OK

#---------------------------Product-List-------------------------------#

#---------------------------Create-Customer-------------------------------#
@name_space.route("/CreateCustomer")
class CreateCustomer(Resource):
	@api.expect(create_customer)
	def post(self):
		data = {
		    "email": "john.doe@example.com",
		    "first_name": "John",
		    "last_name": "Doe",
		    "username": "john.doe",
		    "billing": {
		        "first_name": "John",
		        "last_name": "Doe",
		        "company": "",
		        "address_1": "969 Market",
		        "address_2": "",
		        "city": "San Francisco",
		        "state": "CA",
		        "postcode": "94103",
		        "country": "US",
		        "email": "john.doe@example.com",
		        "phone": "(555) 555-5555"
		    },
		    "shipping": {
		        "first_name": "John",
		        "last_name": "Doe",
		        "company": "",
		        "address_1": "969 Market",
		        "address_2": "",
		        "city": "San Francisco",
		        "state": "CA",
		        "postcode": "94103",
		        "country": "US"
		    }
		}

		print(wcapi.post("customers", data).json())

#----------------------------------------------------------#

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
			offset = page * 10

		get_customer_query = ("""SELECT a.*
							 	FROM `admins` a							 							 							 					 			 
								WHERE a.`organisation_id` = %s LIMIT %s,10""")
		getCustomerData = (organisation_id,offset)
		count_customer_data = cursor.execute(get_customer_query,getCustomerData)

		search_meta = cursor.fetchall()

		get_customer_query_count = ("""SELECT count(*) as customer_count
										 	FROM `admins` a										 							 							 					 			 
											WHERE a.`organisation_id` = %s""")
			
		getCustomerData = (organisation_id)
		count_customer_data = cursor.execute(get_customer_query_count,getCustomerData)		
		customer_data_count = cursor.fetchone()

		page_count = math.trunc(customer_data_count['customer_count']/1000)

		if page_count == 0:
			page_count = 1
		else:
			page_count = page_count + 1

		for key,data in enumerate(search_meta):			
			search_meta[key]['last_updated_date'] = str(data['last_updated_date'])
			search_meta[key]['date_of_lastlogin'] = str(data['date_of_lastlogin'])
			search_meta[key]['date_of_creation'] = str(data['date_of_creation'])
			search_meta[key]['date_of_update'] = str(data['date_of_update'])

			if data['email'] == '':
				data['email'] = 'test@gmail.com'
			else:
				data['email'] = data['email']

			cdata = {
			    "email": data['email'],
			    "first_name": data['first_name'],
			    "last_name": data['last_name'],
			    "username": data['username'],
			    "billing": {
			        "first_name": data['first_name'],
			        "last_name": data['last_name'],
			        "company": "",
			        "address_1": data['address_line_1'],
			        "address_2": data['address_line_2'],
			        "city": data['city'],
			        "state": data['state'],
			        "postcode": 94103,
			        "country": data['country'],
			        "email": data['email'],
			        "phone": data['phoneno']
			    },
			    "shipping": {
			        "first_name": data['first_name'],
			        "last_name": data['last_name'],
			        "company": "",
			        "address_1": data['address_line_1'],
			        "address_2": data['address_line_2'],
			        "city": data['city'],
			        "state": data['state'],
			        "postcode": 94103,
			        "country": data['country'],
			        "email": data['email'],
			        "phone": data['phoneno']
			    }
			}

			print(wcapi.post("customers", cdata).json())

		return ({"attributes": {
					"status_desc": "customer_list",
					"status": "success",
					"page":page,
					"page_count":page_count
				},
				"responseList":search_meta}), status.HTTP_200_OK

def unique(list1): 
  
    # intilize a null list 
    unique_list = [] 
      
    # traverse for all elements 
    for x in list1: 
        # check if exists in unique_list or not 
        if x not in unique_list: 
            unique_list.append(x) 
    # print list 
    return unique_list
