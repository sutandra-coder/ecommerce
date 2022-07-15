from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json,render_template
from flask_api import status
from jinja2._compat import izip
from jinja2 import Environment, FileSystemLoader
from datetime import datetime,timedelta,date
import pymysql
from smtplib import SMTP
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
import requests
import calendar
import json
from instamojoConfig import CLIENT_ID,CLIENT_SECRET,referrer
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import os
import hashlib
import random, string
import math

app = Flask(__name__)
cors = CORS(app)

ecommerce_autopopulation = Blueprint('ecommerce_autopopulation_api', __name__)
api = Api(ecommerce_autopopulation,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceAutopopulation',description='Ecommerce Autopopulation')


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

copy_catalog_model = api.model('Selectcatalog', {
	"from_organisation_id":fields.Integer(required=True),
	"catalog_id":fields.List(fields.Integer(required=True)),
	"to_organisation_id":fields.Integer(required=True)
})

copy_brand_category_model = api.model('SelectBrandCategory', {	
	"brand_id":fields.List(fields.Integer(required=True)),
	"category_id":fields.Integer(required=True),
	"to_organisation_id":fields.Integer(required=True)
})

copy_section_offer_model = api.model('SelectSectionOffer',{
	"from_organisation_id":fields.Integer(required=True),	
	"category_id":fields.Integer(required=True),
	"to_organisation_id":fields.Integer(required=True)
})

copy_budget_model = api.model('SelectBudget',{
	"from_organisation_id":fields.Integer(required=True),	
	"category_id":fields.Integer(required=True),
	"to_organisation_id":fields.Integer(required=True)
})

copy_location_retailer_model = api.model('SelectLocationRetailer',{
	"from_organisation_id":fields.Integer(required=True),	
	"retailer_store_id":fields.Integer(required=True),
	"to_organisation_id":fields.Integer(required=True)
})

copy_customer_model = api.model('SelectCustomer',{
	"from_organisation_id":fields.Integer(required=True),	
	"user_id":fields.Integer(required=True),
	"to_organisation_id":fields.Integer(required=True)
})

copy_location_post_model = api.model('copy_location_post_model',{	
	"organisation_id":fields.Integer(required=True)
})

#----------------------Copy-Catalog---------------------#

@name_space.route("/copyCatalog")	
class copyCatalog(Resource):
	@api.expect(copy_catalog_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		catalog_ids = details.get('catalog_id',[])
		from_organisation_id = details['from_organisation_id']
		to_organisation_id = details['to_organisation_id']

		for key,catalog_id in enumerate(catalog_ids):
			get_catalog_query = ("""SELECT *
					FROM  `catalogs` WHERE `catalog_id` = %s and `organisation_id` = %s""")
			getCatalogData = (catalog_id,from_organisation_id)
			cursor.execute(get_catalog_query,getCatalogData)

			catalog_data = cursor.fetchone()

			catalogstatus = 1
			is_home_section = 1

			insert_query = ("""INSERT INTO `catalogs`(`catalog_name`,`organisation_id`,`is_home_section`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")
			data = (catalog_data['catalog_name'],to_organisation_id,is_home_section,catalogstatus,to_organisation_id)
			cursor.execute(insert_query,data)
			catalog_id = cursor.lastrowid

			get_catalog_product_mapping_query = ("""SELECT *
					FROM  `product_catalog_mapping` WHERE `catalog_id` = %s and `organisation_id` = %s""")
			cursor.execute(get_catalog_product_mapping_query,getCatalogData)
			catalog_product_data = cursor.fetchall()

			for pkey,catalog_product in enumerate(catalog_product_data):

				insert_catalog_product_query = ("""INSERT INTO `product_catalog_mapping`(`catalog_id`,`product_id`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")
				catalog_product_data = (catalog_id,catalog_product['product_id'],to_organisation_id,to_organisation_id)
				cursor.execute(insert_catalog_product_query,catalog_product_data)

			get_catalog_category_mapping_query = ("""SELECT *
					FROM  `catalog_category_mapping` WHERE `catalog_id` = %s and `organisation_id` = %s""")
			cursor.execute(get_catalog_category_mapping_query,getCatalogData)
			catalog_category_data = cursor.fetchall()

			for ckey,catalog_category in enumerate(catalog_category_data):

				insert_catalog_category_query = ("""INSERT INTO `catalog_category_mapping`(`catalog_id`,`category_id`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")
				catalog_category_data = (catalog_id,catalog_category['category_id'],to_organisation_id,to_organisation_id)

				cursor.execute(insert_catalog_category_query,catalog_category_data)


		return ({"attributes": {
			    	"status_desc": "copy_catalog",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Copy-Catalog---------------------#

#----------------------Copy-Brand-Category---------------------#

@name_space.route("/copyBrandCategory")	
class copyBrandCategory(Resource):
	@api.expect(copy_brand_category_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		brand_ids = details.get('brand_id',[])
		category_id = details['category_id']
		to_organisation_id = details['to_organisation_id']

		for key,brand_id in enumerate(brand_ids):
			get_brand_category_query = (""" SELECT `brand_id`,`category_id`
				FROM `category_brand_mapping` WHERE  `brand_id` = %s and `category_id` = %s and `organisation_id` = %s""")
			get_brand_category_data = (brand_id,category_id,to_organisation_id)
			count_brand_category = cursor.execute(get_brand_category_query,get_brand_category_data)

			if count_brand_category > 0:
				delete_query = ("""DELETE FROM `category_brand_mapping` WHERE `brand_id` = %s and `category_id` = %s and `organisation_id` = %s""")
				delData = (brand_id,category_id,to_organisation_id)		
				cursor.execute(delete_query,delData)

				insert_brand_category_query = ("""INSERT INTO `category_brand_mapping`(`brand_id`,`category_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")
				brand_category_data = (brand_id,category_id,to_organisation_id,to_organisation_id)
				cursor.execute(insert_brand_category_query,brand_category_data)		

			else:
				insert_brand_category_query = ("""INSERT INTO `category_brand_mapping`(`brand_id`,`category_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")
				brand_category_data = (brand_id,category_id,to_organisation_id,to_organisation_id)
				cursor.execute(insert_brand_category_query,brand_category_data)

		return ({"attributes": {
			    	"status_desc": "copy_catalog",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Copy-Brand-Category---------------------#

#----------------------Copy-Section-Offer---------------------#

@name_space.route("/copySectionOffer")	
class copySectionOffer(Resource):
	@api.expect(copy_section_offer_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		from_organisation_id = details['from_organisation_id']
		category_id = details['category_id']
		to_organisation_id = details['to_organisation_id']

		get_section_query = ("""SELECT *
					FROM  `section_master` WHERE `category_id` = %s and `organisation_id` = %s and `home_section` = 1""")
		getSectionData = (category_id,from_organisation_id)
		cursor.execute(get_section_query,getSectionData)

		section_data = cursor.fetchall()

		for skey,section in enumerate(section_data):
			section_status = 1

			insert_section_query = ("""INSERT INTO `section_master`(`offer_section_name`,`offer_section_type`,`category_id`,`organisation_id`,`home_section`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s)""")
			insertsectionData = (section['offer_section_name'],section['offer_section_type'],category_id,to_organisation_id,section['home_section'],section_status,to_organisation_id)
			cursor.execute(insert_section_query,insertsectionData)
			section_id = cursor.lastrowid

			get_section_offer_query = ("""SELECT *
					FROM  `offer_section_mapping` WHERE `section_id` = %s and `organisation_id` = %s""")
			getSectionOfferData = (section['section_id'],from_organisation_id)
			cursor.execute(get_section_offer_query,getSectionOfferData)

			section_Offer_data = cursor.fetchall()

			for sokey,section_offer in enumerate(section_Offer_data):
				get_offer_query = ("""SELECT *
					FROM  `offer` WHERE `offer_id` = %s and `organisation_id` = %s""")
				offerData = (section_offer['offer_id'],from_organisation_id)
				cursor.execute(get_offer_query,offerData)
				offer_data = cursor.fetchone()

				offer_status = 1

				insert_offer_query = ("""INSERT INTO `offer`(`offer_image`,`coupon_code`,`discount_percentage`,`absolute_price`,`discount_value`,`product_offer_type`,`is_landing_page`,`offer_type`,`offer_image_type`,`status`,`organisation_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				insertOfferData = (offer_data['offer_image'],offer_data['coupon_code'],offer_data['discount_percentage'],offer_data['absolute_price'],offer_data['discount_value'],
					offer_data['product_offer_type'],offer_data['is_landing_page'],offer_data['offer_type'],offer_data['offer_image_type'],offer_status,to_organisation_id)
				cursor.execute(insert_offer_query,insertOfferData)
				offer_id = cursor.lastrowid

				insert_offer_section_query = ("""INSERT INTO `offer_section_mapping`(`section_id`,`offer_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")
				insertoffersectionData = (section_id,offer_id,to_organisation_id,to_organisation_id)
				cursor.execute(insert_offer_section_query,insertoffersectionData)

				get_product_offer_query = ("""SELECT * from `product_offer_mapping` WHERE `offer_id` = %s and `organisation_id` = %s""")
				getproductOfferData = (offer_data['offer_id'],from_organisation_id)
				cursor.execute(get_product_offer_query,getproductOfferData)
				product_offer_data = cursor.fetchall()

				for pokey,product_offer in enumerate(product_offer_data): 
					product_offer_status = 1
					insert_product_offer_query = ("""INSERT INTO `product_offer_mapping`(`offer_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
					insertproductOfferData = (offer_id,product_offer['product_id'],product_offer_status,to_organisation_id,to_organisation_id)
					cursor.execute(insert_product_offer_query,insertproductOfferData)

		return ({"attributes": {
			    	"status_desc": "copy_section_offer",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Copy-Section-Offer---------------------#


#----------------------Copy-Budget---------------------#

@name_space.route("/copyBudget")	
class copyBudget(Resource):
	@api.expect(copy_budget_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		from_organisation_id = details['from_organisation_id']
		category_id = details['category_id']
		to_organisation_id = details['to_organisation_id']

		get_budget_category_query = ("""SELECT *
				FROM `budget` WHERE  `category_id` = %s and `organisation_id` = %s""")
		get_budget_category_data = (category_id,from_organisation_id)
		count_budget_category = cursor.execute(get_budget_category_query,get_budget_category_data)

		if count_budget_category > 0:
				budget_data = cursor.fetchall()
				delete_query = ("""DELETE FROM `budget` WHERE `category_id` = %s and `organisation_id` = %s""")
				delData = (category_id,to_organisation_id)		
				cursor.execute(delete_query,delData)

				for key,data in enumerate(budget_data):
					insert_brand_category_query = ("""INSERT INTO `budget`(`greaterthanvalue`,`lessthanvalue`,`category_id`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
					brand_category_data = (data['greaterthanvalue'],data['lessthanvalue'],data['category_id'],to_organisation_id,to_organisation_id)
					cursor.execute(insert_brand_category_query,brand_category_data)		

		else:
			insert_brand_category_query = ("""INSERT INTO `budget`(`greaterthanvalue`,`lessthanvalue`,`category_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
			brand_category_data = (budget_data['greaterthanvalue'],budget_data['lessthanvalue'],budget_data['category_id'],to_organisation_id,to_organisation_id)
			cursor.execute(insert_brand_category_query,brand_category_data)

		return ({"attributes": {
			    	"status_desc": "copy_budget",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Copy-Budget---------------------#


#----------------------Copy-Location-With-Retail-Store---------------------#
@name_space.route("/copyLocationWithRetailer")	
class copyLocationWithRetailer(Resource):
	@api.expect(copy_location_retailer_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		from_organisation_id = details['from_organisation_id']
		retailer_store_id = details['retailer_store_id']
		to_organisation_id = details['to_organisation_id']

		get_retailer_store_query = ("""SELECT *
				FROM `retailer_store` WHERE  `retailer_store_id` = %s and `organisation_id` = %s""")
		get_retailer_store_data = (retailer_store_id,from_organisation_id)
		count_retailer_store = cursor.execute(get_retailer_store_query,get_retailer_store_data)

		retailer_store = cursor.fetchone()

		print(retailer_store)

		get_retailer_store_image_query = ("""SELECT * FROM `retailer_store_image` WHERE `retailer_store_id` = %s and `organisation_id` = %s """)
		get_retailer_store_image_data = (retailer_store_id,from_organisation_id)
		count_retailer_store_image = cursor.execute(get_retailer_store_image_query,get_retailer_store_image_data)

		retailer_store_image = cursor.fetchone()

		get_reatiler_store_store_query = ("""SELECT * FROM `retailer_store_stores` WHERE `retailer_store_id` = %s and `organisation_id` = %s""")
		get_retailer_store_store_data = (retailer_store_id,from_organisation_id)
		count_retailer_store_store = cursor.execute(get_reatiler_store_store_query,get_retailer_store_store_data)

		retailer_store_store = cursor.fetchone()

		get_retailer_store_query_to_organisation = ("""SELECT *
				FROM `retailer_store` WHERE  `retailer_name` = %s and `organisation_id` = %s""")
		get_retailer_store_data_to_organisation = (retailer_store['retailer_name'],to_organisation_id)
		count_retailer_store_to_organisation = cursor.execute(get_retailer_store_query_to_organisation,get_retailer_store_data_to_organisation)	

		if count_retailer_store_to_organisation > 0:
			print('hello')
			retailer_store_to_organisation_id = cursor.fetchone()
			current_retailer_store_id = retailer_store_to_organisation_id['retailer_store_id']

			update_retailer_store_query = ("""UPDATE `retailer_store` SET `retailer_name` = %s
				WHERE `organisation_id` = %s """)
			update_retailer_store_data = (retailer_store['retailer_name'],to_organisation_id)
			cursor.execute(update_retailer_store_query,update_retailer_store_data)			

			if current_retailer_store_id:
				get_retailer_store_image_query_to_organisation_id = ("""SELECT * FROM `retailer_store_image` WHERE `retailer_store_id` = %s and `organisation_id` = %s """)
				get_retailer_store_image_data_to_organisation_id = (current_retailer_store_id,to_organisation_id)
				count_retailer_store_image_to_organisation_id = cursor.execute(get_retailer_store_image_query_to_organisation_id,get_retailer_store_image_data_to_organisation_id)

				if count_retailer_store_image_to_organisation_id > 0:
					retailer_store_image_to_organisation_id = cursor.fetchone()
					update_retailer_store_image_query = ("""UPDATE `retailer_store_image` SET `image` = %s
						WHERE `organisation_id` = %s and `retailer_store_id` = %s""")
					update_retailer_store_image_data = (retailer_store_image['image'],to_organisation_id,current_retailer_store_id)
					cursor.execute(update_retailer_store_image_query,update_retailer_store_image_data)
				else:
					retailer_store_image_status = 1
					insert_retailer_store_image_query = ("""INSERT INTO `retailer_store_image`(`retailer_store_id`,`image`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
					insert_retailer_store_image_data = (current_retailer_store_id,retailer_store_image['image'],retailer_store_image_status,to_organisation_id,to_organisation_id)
					cursor.execute(insert_retailer_store_image_query,insert_retailer_store_image_data)

				get_retailer_store_store_query_to_organisation_id = ("""SELECT * FROM `retailer_store_stores` WHERE `retailer_store_id` = %s and `organisation_id` = %s """)
				get_retailer_store_store_data_to_organisation_id = (current_retailer_store_id,to_organisation_id)
				count_retailer_store_store_to_organisation_id = cursor.execute(get_retailer_store_store_query_to_organisation_id,get_retailer_store_store_data_to_organisation_id)

				if count_retailer_store_store_to_organisation_id > 0:
					retailer_store_store_to_organisation_id = cursor.fetchone()
					update_retailer_store_store_query = ("""UPDATE `retailer_store_stores` SET `address` = %s,`latitude` = %s,`longitude` = %s,`phoneno` = %s
						WHERE `organisation_id` = %s and `retailer_store_id` = %s""")
					update_retailer_store_image_data = (retailer_store_store['address'],retailer_store_store['latitude'],retailer_store_store['longitude'],retailer_store_store['phoneno'],to_organisation_id,current_retailer_store_id)
					cursor.execute(update_retailer_store_store_query,update_retailer_store_image_data)
				else:
					retailer_store_store_status = 1
					insert_retailer_store_store_query = ("""INSERT INTO `retailer_store_stores`(`retailer_store_id`,`address`,`latitude`,`longitude`,`phoneno`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s,%s)""")
					insert_retailer_store_store_data = (current_retailer_store_id,retailer_store_store['address'],retailer_store_store['latitude'],retailer_store_store['longitude'],retailer_store_store['phoneno'],to_organisation_id,to_organisation_id)
					cursor.execute(insert_retailer_store_store_query,insert_retailer_store_store_data)

		else:
			retailer_store_status = 1
			insert_retailer_store_query = ("""INSERT INTO `retailer_store`(`retailer_name`,`city`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
			insert_retailer_store_data = (retailer_store['retailer_name'],retailer_store['city'],retailer_store_status,to_organisation_id,to_organisation_id)
			cursor.execute(insert_retailer_store_query,insert_retailer_store_data)

			retailer_store_id = cursor.lastrowid	

			if 	retailer_store_id:
				get_retailer_store_image_query_to_organisation_id = ("""SELECT * FROM `retailer_store_image` WHERE `retailer_store_id` = %s and `organisation_id` = %s """)
				get_retailer_store_image_data_to_organisation_id = (retailer_store_id,to_organisation_id)
				count_retailer_store_image_to_organisation_id = cursor.execute(get_retailer_store_image_query_to_organisation_id,get_retailer_store_image_data_to_organisation_id)

				if count_retailer_store_image_to_organisation_id > 0:
					retailer_store_image_to_organisation_id = cursor.fetchone()
					update_retailer_store_image_query = ("""UPDATE `retailer_store_image` SET `image` = %s
						WHERE `organisation_id` = %s """)
					update_retailer_store_image_data = (retailer_store_image['image'],to_organisation_id)
					cursor.execute(update_retailer_store_image_query,update_retailer_store_image_data)
				else:					
					retailer_store_image_status = 1
					insert_retailer_store_query = ("""INSERT INTO `retailer_store_image`(`retailer_store_id`,`image`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
					insert_retailer_store_data = (retailer_store_id,retailer_store_image['image'],retailer_store_image_status,to_organisation_id,to_organisation_id)
					cursor.execute(insert_retailer_store_query,insert_retailer_store_data)

			get_retailer_store_store_query_to_organisation_id = ("""SELECT * FROM `retailer_store_stores` WHERE `retailer_store_id` = %s and `organisation_id` = %s """)
			get_retailer_store_store_data_to_organisation_id = (retailer_store_id,to_organisation_id)
			count_retailer_store_store_to_organisation_id = cursor.execute(get_retailer_store_store_query_to_organisation_id,get_retailer_store_store_data_to_organisation_id)

			if count_retailer_store_store_to_organisation_id > 0:
				retailer_store_store_to_organisation_id = cursor.fetchone()
				update_retailer_store_store_query = ("""UPDATE `retailer_store_stores` SET `address` = %s,`latitude` = %s,`longitude` = %s,`phoneno` = %s
						WHERE `organisation_id` = %s and `retailer_store_id` = %s""")
				update_retailer_store_image_data = (retailer_store_store['address'],retailer_store_store['latitude'],retailer_store_store['longitude'],retailer_store_store['phoneno'],to_organisation_id,current_retailer_store_id)
				cursor.execute(update_retailer_store_store_query,update_retailer_store_image_data)
			else:
				retailer_store_store_status = 1
				insert_retailer_store_store_query = ("""INSERT INTO `retailer_store_stores`(`retailer_store_id`,`address`,`latitude`,`longitude`,`phoneno`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s,%s)""")
				insert_retailer_store_store_data = (retailer_store_id,retailer_store_store['address'],retailer_store_store['latitude'],retailer_store_store['longitude'],retailer_store_store['phoneno'],to_organisation_id,to_organisation_id)
				cursor.execute(insert_retailer_store_store_query,insert_retailer_store_store_data)	

		return ({"attributes": {
			    "status_desc": "copy_location_with_retailer",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Copy-Location-With-Retail-Store---------------------#

#----------------------Copy-Location---------------------#
@name_space.route("/copyLocation")	
class copyLocation(Resource):
	@api.expect(copy_location_post_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		organisation_id = details['organisation_id']

		get_city_query = ("""SELECT *
				FROM `city_master` WHERE `organisation_id` = 1 and `status` = 1""")		
		count_city = cursor.execute(get_city_query)

		if count_city > 0:
			city_data = cursor.fetchall()

			for key,data in enumerate(city_data):
				get_retailer_store_query = ("""SELECT *
					FROM `retailer_store` WHERE  `city` = %s and `organisation_id` = %s""")
				get_retailer_store_data = (data['city'],organisation_id)
				count_retailer_store = cursor.execute(get_retailer_store_query,get_retailer_store_data)

				if count_retailer_store < 1:
					retailer_store_status = 1
					retailer_name = data['city']+" Retailer"
					insert_retailer_store_query = ("""INSERT INTO `retailer_store`(`retailer_name`,`city`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
					insert_retailer_store_data = (retailer_name,data['city'],retailer_store_status,organisation_id,organisation_id)
					cursor.execute(insert_retailer_store_query,insert_retailer_store_data)

					retailer_store_id = cursor.lastrowid

					retailer_store_image_status = 1
					insert_retailer_store_image_query = ("""INSERT INTO `retailer_store_image`(`retailer_store_id`,`image`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
					insert_retailer_store_image_data = (retailer_store_id,data['city_image'],retailer_store_image_status,organisation_id,organisation_id)
					cursor.execute(insert_retailer_store_image_query,insert_retailer_store_image_data)

		else:
			city_data = []


		return ({"attributes": {
			    "status_desc": "copy_location",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK	

#----------------------Copy-Location---------------------#
		



	