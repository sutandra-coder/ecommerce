from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2 import Environment, FileSystemLoader
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
import math
import os
#import asyncio
import threading
import tracemalloc

env = Environment(
    loader=FileSystemLoader('%s/templates/' % os.path.dirname(__file__)))

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
	return connection

def ecommerce_analytics():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='ecommerce_analytics',
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

def ecommerce_analytics():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce_analytics',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#


ecommerce_product_admin = Blueprint('ecommerce_product_admin_api', __name__)
api = Api(ecommerce_product_admin,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceProductAdmin',description='Ecommerce Product Admin')

promo_offer_postmodel = api.model('promo_offer_post_model',{
	"product_id":fields.List(fields.Integer),
	"select_all_product":fields.Integer(required=True),
	"coupon_code":fields.String(required=True),
	"coupon_type":fields.Integer(required=True),
	"coupn_image_url":fields.String(required=True),
	"coupon_amount":fields.Integer(required=True),
	"minimum_purchase":fields.Integer(required=True),
	"maximum_value":fields.Integer(required=True),
	"unique_flag":fields.Integer(required=True),
	"expiry_date":fields.String(required=True),
	"organisation_id":fields.Integer(required=True)
})

stock_putmodel = api.model('stock_putmodel',{
	"retailer_store_id":fields.Integer(required=True),
	"stock":fields.Integer(required=True),
	"product_meta_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

store_stock_putmodel = api.model('store_stock_putmodel',{
	"retailer_store_id":fields.Integer(required=True),
	"retailer_store_store_id":fields.Integer(required=True),
	"stock":fields.Integer(required=True),
	"product_meta_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

store_all_product_stock_postmodel = api.model('store_all_product_stock_postmodel',{	
	"retailer_store_store_id":fields.Integer(required=True),
	"stock":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

checkcoupon_postmodel = api.model('checkEmail',{
	"coupon_code":fields.String(required=True),
})

productcatalog_postmodel = api.model('productcatalog_postmodel',{
	"catalog_id": fields.Integer(required=True),
	"product_id": fields.Integer(required=True),
	"organisation_id": fields.Integer(required=True)
})

multipleproductcatalog_postmodel = api.model('multipleproductcatalog_postmodel',{
	"catalog_id": fields.Integer(required=True),
	"product_id": fields.List(fields.Integer),
	"organisation_id": fields.Integer(required=True)
})

catalog_category_postmodel = api.model('catalog_category_postmodel',{
	"catalog_id": fields.Integer(required=True),
	"category_id": fields.Integer,
	"is_home_section": fields.Integer,
	"organisation_id": fields.Integer(required=True)
})

product_meta_postmodel = api.model('product_meta', {
	"product_name":fields.String(required=True),
	"product_long_description":fields.String,
	"product_short_description":fields.String,
	"category_id":fields.Integer(required=True),
	"product_type":fields.String,
	"organisation_id":fields.Integer(required=True),
	"product_meta_code":fields.Integer(required=True),
	"meta_key_text":fields.String,
	"in_price":fields.Integer(required=True),
	"out_price":fields.Integer(required=True),
	"image":fields.List(fields.String),
	"brand_id":fields.Integer
})

product_price_meta_postmodel = api.model('product_price_meta', {
	"product_id":fields.Integer(required=True),
	"product_meta_code":fields.Integer(required=True),
	"meta_key_text":fields.String(required=True),
	"in_price":fields.Integer(required=True),
	"out_price":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True),
	"image":fields.List(fields.String),
})


filter_postmodel = api.model('product_replication_postmodel',{	
	"brand_id":fields.List(fields.Integer)
})

update_otp_settings_model = api.model('otp_settings_postmodel',{	
	"otp_setting_value":fields.Integer
})

update_referal_loyality_settings_model = api.model('update_referal_loyality_settings_model',{	
	"setting_value":fields.Integer
})

category_putmodel = api.model('category_putmodel',{	
	"status":fields.Integer
})

customer_exchange_putmodel = api.model('customer_exchange_putmodel',{	
	"status":fields.Integer,
	"Is_clone":fields.Integer
})

exchange_device_comments_postmodel = api.model('exchange_device_comments_postmodel',{	
	"text":fields.String,
	"image":fields.String,
	"exchange_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

changeorderpaymentstatus_putmodel = api.model('changeOrderPaymentStatus',{
	"order_payment_status":fields.Integer(required=True),
})

create_catalouge_pdf = api.model('createCatalougePdf',{
	"catalog_id":fields.Integer(required=True)
})

productoutprice_putmodel = api.model('productPrice',{
	"out_price":fields.Integer(required=True),
	"out_price_status":fields.Integer(required=True)
})

product_sub_category_section_putmodel = api.model('product_sub_category_section_putmodel',{
	"section_id":fields.Integer(required=True),
	"sub_category_id":fields.Integer(required=True)
})


ecommerce_share_model = api.model('ecommerce_share_model',{
	"source_type":fields.Integer(required=True),
	"source_id":fields.Integer,
	"organisation_id":fields.Integer(required=True)

})

ecommerce_missopportunity_model = api.model('ecommerce_misopportunity_model',{
	"customer_id":fields.Integer(required=True),
	"missopprtunity_product_name":fields.String(required=True),
	"whatsapp_no":fields.String(required=True),
	"retailer_store_store_id":fields.Integer(required=True),
	"name_of_customer":fields.String,
	"mobile_no":fields.String,
	"email_id":fields.String,
	"demo_given_by":fields.String,
	"reason_for_non_closure":fields.String,
	"follow_up_1":fields.String,
	"follow_up_2":fields.String,
	"remarks":fields.String,
	"name_by_whom_captued_data":fields.String,
	"missed_opportunity_date":fields.String,
	"followup_date":fields.String,
	"follow_up_2_date":fields.String,
	"organisation_id":fields.Integer(required=True)
})

ecommerce_missopportunity_mapping_model = api.model('ecommerce_misopportunity_mapping_model',{
	"customer_id":fields.Integer(required=True),
	"missopprtunity_product_name":fields.String(required=True),
	"product_id":fields.Integer(required=True),
	"product_meta_id":fields.Integer(required=True),
	"retailer_store_store_id":fields.Integer(required=True),
	"name_of_customer":fields.String,
	"mobile_no":fields.String,
	"email_id":fields.String,
	"demo_given_by":fields.String,
	"reason_for_non_closure":fields.String,
	"follow_up_1":fields.String,
	"follow_up_2":fields.String,
	"remarks":fields.String,
	"organisation_id":fields.Integer(required=True)
})

close_missopportunity_model = api.model('close_missopportunity_model',{
	"miss_opportunity_id":fields.Integer(required=True)
})

notification_model = api.model('notification_model', {
	"title": fields.String(required=True),
	"text": fields.String(required=True),
	"customer_id": fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

ecommerce_missopportunity_model_update = api.model('ecommerce_missopportunity_model_update',{
	"miss_opportunity_id":fields.Integer(required=True),
	"missopprtunity_product_name":fields.String(required=True),
	"whatsapp_no":fields.String(required=True),
	"email_id":fields.String(required=True),
	"demo_given_by":fields.String(required=True),
	"reason_for_non_closure":fields.String(required=True),
	"follow_up_1":fields.String(required=True),
	"follow_up_2":fields.String(required=True),
	"remarks":fields.String(required=True),
	"name_by_whom_captued_data":fields.String(required=True),
	"missed_opportunity_date":fields.String(required=True),
	"followup_date":fields.String(required=True),
	"follow_up_2_date":fields.String(required=True),
	"organisation_id":fields.Integer(required=True)
})

ecommerce_missopportunity_mapping_model_v2 = api.model('ecommerce_missopportunity_mapping_model_v2',{
	"miss_opportunity_id":fields.Integer(required=True),
	"product_id":fields.Integer(required=True),
	"product_meta_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'


#----------------------Product-List---------------------#
@name_space.route("/productListFromProductOrganisationMapping/<int:organisation_id>")	
class productListFromProductOrganisationMapping(Resource):	
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		get_query = ("""SELECT p.`product_id`,p.`product_name`
				FROM `product` p
				INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
				WHERE  pom.`organisation_id` = %s""")
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()		

		for key,data in enumerate(product_data):
			get_query_meta = (""" SELECT pm.`product_meta_id` from `product_meta` pm where pm.`product_id` = %s""")
			get_data_meta = (data['product_id'])
			count_product_meta = cursor.execute(get_query_meta,get_data_meta)

			if count_product_meta > 0:
				get_data_product_meta = cursor.fetchone()					

				get_query_images = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s """)
				getdata_images = (get_data_product_meta['product_meta_id'])
				image_count = cursor.execute(get_query_images,getdata_images)
				image = cursor.fetchone()

				if image_count > 0:
					product_data[key]['image'] = image['image']
			else:
				product_data[key]['image'] = ""

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Product-List---------------------#
@name_space.route("/RectproductListFromProductOrganisationMapping/<int:organisation_id>")	
class RecentproductListFromProductOrganisationMapping(Resource):	
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		get_query = ("""SELECT p.`product_id`,p.`product_name`,pom.`product_status`
				FROM `product_organisation_mapping` pom				
				INNER JOIN `product` p ON p.`product_id` = pom.`product_id`
				WHERE  pom.`organisation_id` = %s ORDER BY p.`product_id` DESC limit 10""")
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()		

		for key,data in enumerate(product_data):
			get_query_meta = (""" SELECT pm.`product_meta_id` from `product_meta` pm where pm.`product_id` = %s""")
			get_data_meta = (data['product_id'])
			count_product_meta = cursor.execute(get_query_meta,get_data_meta)

			if count_product_meta > 0:
				get_data_product_meta = cursor.fetchone()

				get_query_meta_count = ("""SELECT count(*) as `product_meta_count`  from `product_meta` pm where pm.`product_id` = %s""")
				get_data_meta_count = (data['product_id'])
				cursor.execute(get_query_meta_count,get_data_meta_count)
				product_meta = cursor.fetchone()
				product_data[key]['product_meta_count'] = product_meta['product_meta_count']									

				get_query_images = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s """)
				getdata_images = (get_data_product_meta['product_meta_id'])
				image_count = cursor.execute(get_query_images,getdata_images)
				image = cursor.fetchone()

				if image_count > 0:
					product_data[key]['image'] = image['image']
				else:
					product_data[key]['image'] = ""
			else:
				product_data[key]['product_meta_count'] = 0
				product_data[key]['image'] = ""

			get_offer_product =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,
				o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`is_online`,o.`instruction`,o.`status`
			FROM `product_offer_mapping` pom 
			INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id` 
			WHERE pom.`organisation_id` = %s and pom.`product_id` = %s""")
			get_offer_data = (organisation_id,data['product_id'])
			count_offer_product = cursor.execute(get_offer_product,get_offer_data)
			if count_offer_product > 0:
				offer_product = cursor.fetchall()
				product_data[key]['offer_product'] = offer_product
			else:
				product_data[key]['offer_product'] = []

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Product-List---------------------#
@name_space.route("/RectproductListByCategoryIdFromProductOrganisationMapping/<int:organisation_id>/<int:category_id>")	
class RectproductListByCategoryIdFromProductOrganisationMapping(Resource):	
	def get(self,organisation_id,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		get_query = ("""SELECT p.`product_id`,p.`product_name`,pom.`product_status`
				FROM `product_organisation_mapping` pom				
				INNER JOIN `product` p ON p.`product_id` = pom.`product_id`
				WHERE  pom.`organisation_id` = %s  and p.`category_id` = %s ORDER BY p.`product_id` DESC limit 10""")
		get_data = (organisation_id,category_id)
		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()		

		for key,data in enumerate(product_data):
			get_query_meta = (""" SELECT pm.`product_meta_id` from `product_meta` pm where pm.`product_id` = %s""")
			get_data_meta = (data['product_id'])
			count_product_meta = cursor.execute(get_query_meta,get_data_meta)

			if count_product_meta > 0:
				get_data_product_meta = cursor.fetchone()

				get_query_meta_count = ("""SELECT count(*) as `product_meta_count`  from `product_meta` pm where pm.`product_id` = %s""")
				get_data_meta_count = (data['product_id'])
				cursor.execute(get_query_meta_count,get_data_meta_count)
				product_meta = cursor.fetchone()
				product_data[key]['product_meta_count'] = product_meta['product_meta_count']									

				get_query_images = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s """)
				getdata_images = (get_data_product_meta['product_meta_id'])
				image_count = cursor.execute(get_query_images,getdata_images)
				image = cursor.fetchone()

				if image_count > 0:
					product_data[key]['image'] = image['image']
				else:
					product_data[key]['image'] = ""
			else:
				product_data[key]['product_meta_count'] = 0
				product_data[key]['image'] = ""

			get_offer_product =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,
				o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`is_online`,o.`instruction`,o.`status`
			FROM `product_offer_mapping` pom 
			INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id` 
			WHERE pom.`organisation_id` = %s and pom.`product_id` = %s""")
			get_offer_data = (organisation_id,data['product_id'])
			count_offer_product = cursor.execute(get_offer_product,get_offer_data)
			if count_offer_product > 0:
				offer_product = cursor.fetchall()
				product_data[key]['offer_product'] = offer_product
			else:
				product_data[key]['offer_product'] = []

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Check-Email-Exist---------------------#

@name_space.route("/CheckCouponCode/<int:organisation_id>")	
class CheckCouponCode(Resource):
	@api.expect(checkcoupon_postmodel)
	def post(self,organisation_id):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `coupon_type_master` WHERE `coupon_code` = %s and `organisation_id` = %s""")
		getData = (details['coupon_code'],organisation_id)
		count_coupon = cursor.execute(get_query,getData)

		connection.commit()
		cursor.close()

		if count_coupon > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "coupon_details",
			    		"status": "error",
			    		"message":"Coupon Already Exist"
			    	},
			    	"responseList":{"coupon_code":data['coupon_code']} }), status.HTTP_200_OK

		else:
			return ({"attributes": {
		    		"status_desc": "coupon_details",
		    		"status": "success",
		    		"message":"Coupon not Exist"
		    	},
		    	"responseList":{"coupon_code":details['coupon_code']}}), status.HTTP_200_OK

		

#----------------------Check-Email-Exist---------------------#

#----------------------Add-Promo-Offer---------------------#

@name_space.route("/addPromoOffer")	
class addPromoOffer(Resource):
	@api.expect(promo_offer_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		coupon_type = details['coupon_type']
		promo_offer_status = 1
		coupon_code = details['coupon_code']
		coupon_amount = details['coupon_amount']
		minimum_purchase = details['minimum_purchase']
		maximum_value = details['maximum_value']	
		validity_td = details['expiry_date']
		unique_flag =  details['unique_flag']
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']
		coupn_image_url = details['coupn_image_url']
		coupon_status = 1

	
		product_ids = details.get('product_id',[])
		select_all_product = details['select_all_product']

		insert_query = ("""INSERT INTO `coupon_type_master`(`coupon_type`,`coupn_image_url`,`coupon_code`,`coupon_amount`,`minimum_purchase`,`maximum_value`,`unique_flag`,`validity_td`,`organisation_id`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (coupon_type,coupn_image_url,coupon_code,coupon_amount,minimum_purchase,maximum_value,unique_flag,validity_td,organisation_id,coupon_status,last_update_id)
		cursor.execute(insert_query,data)	

		coupon_type_id = cursor.lastrowid
		details['coupon_type_id'] = coupon_type_id

		if select_all_product == 1:
			get_query = ("""SELECT *
					FROM  `product_organisation_mapping` WHERE `organisation_id` = %s""")
			getData = (organisation_id)
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:
				product_data = cursor.fetchall()
				for key,data in enumerate(product_data):
					insert_coupon_product_mapping_query = ("""INSERT INTO `coupon_product_mapping`(`coupon_type_id`,`product_id`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")
					coupon_product_mspping_data = (coupon_type_id,data['product_id'],organisation_id,last_update_id)
					cursor.execute(insert_coupon_product_mapping_query,coupon_product_mspping_data)

		else:
		
			for keyb,product_id in enumerate(product_ids):			
		
				insert_coupon_product_mapping_query = ("""INSERT INTO `coupon_product_mapping`(`coupon_type_id`,`product_id`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")
				coupon_product_mspping_data = (coupon_type_id,product_id,organisation_id,last_update_id)
				cursor.execute(insert_coupon_product_mapping_query,coupon_product_mspping_data)

		return ({"attributes": {
				    		"status_desc": "Promo Offer",
				    		"status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Add-Promo-Offer---------------------#

#----------------------Get-Offer-List---------------------#	
@name_space.route("/getPromoOfferList/<int:organisation_id>")	
class getPromoOfferList(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `coupon_type_master` where `organisation_id` = %s""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)

		offer_data = cursor.fetchall()

		for key,data in enumerate(offer_data):
			offer_data[key]['last_update_ts'] = str(data['last_update_ts'])	
			offer_data[key]['validity_td'] = str(data['validity_td'])	

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "offer_details",
		    		"status": "success"
		    	},
		    	"responseList":offer_data}), status.HTTP_200_OK

#----------------------Get-Offer-List---------------------#

#----------------------Meta-Key-value-List-meta-key-id---------------------#
@name_space.route("/getMetaKeyValueListMetaId/<int:meta_key_id>/<int:organisation_id>")	
class getMetaKeyValueListMetaId(Resource):
	def get(self,meta_key_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `meta_key_value_id`,`meta_key_id`,`meta_key_value`,`image`,`status`,`organisation_id`,
			`last_update_id`,`last_update_ts` FROM `meta_key_value_master` WHERE `meta_key_id` = %s
			 and `organisation_id` = %s and `status` = 1 """)

		getdata = (meta_key_id,organisation_id)
		cursor.execute(get_query,getdata)

		meta_value_data = cursor.fetchall()

		for key,data in enumerate(meta_value_data):
			meta_value_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "meta_key_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_value_data}), status.HTTP_200_OK

#----------------------Meta-Key-value-List-List-meta-key-id---------------------#

#----------------------Product-List-By-Category-Id-And-Brnad-Id---------------------#
@name_space.route("/productListByCategoryIdAndBrandId/<int:organisation_id>/<int:category_id>/<int:brand_id>")	
class productListByCategoryIdAndBrandId(Resource):
	def get(self,organisation_id,category_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		if brand_id == 0:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,p.`status`,p.`category_id` as `product_type_id`
						FROM `product_organisation_mapping` pom 
						INNER JOIN `product` p ON p.`product_id` = pom.`product_id` 
						WHERE pom.`product_id` not in (select `product_id` from product_brand_mapping where organisation_id = %s) 
						and pom.`organisation_id` = %s and p.`category_id` = %s""")
			get_data = (organisation_id,organisation_id,category_id)
					

		else:

			get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,p.`status`,p.`category_id` as `product_type_id`
					FROM `product_brand_mapping` pbm
					INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
					WHERE  pbm.`organisation_id` = %s and p.`category_id` = %s and pbm.`brand_id` = %s""")
			get_data = (organisation_id,category_id,brand_id)

		cursor.execute(get_query,get_data)
		print(cursor._last_executed) 
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):	

			get_query_meta = (""" SELECT pm.`product_meta_id` from `product_meta` pm where pm.`product_id` = %s""")
			get_data_meta = (data['product_id'])
			count_product_meta = cursor.execute(get_query_meta,get_data_meta)

			if count_product_meta > 0:
				get_data_product_meta = cursor.fetchone()					

				get_query_images = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s """)
				getdata_images = (get_data_product_meta['product_meta_id'])
				image_count = cursor.execute(get_query_images,getdata_images)
				image = cursor.fetchone()

				if image_count > 0:
					product_data[key]['image'] = image['image']

				product_data[key]['is_product_meta'] = 1
			else:
				product_data[key]['image'] = ""	
				product_data[key]['is_product_meta'] = 0

		new_product_data = []

		for nkey,ndata in enumerate(product_data):
			if ndata['is_product_meta'] == 1:
				new_product_data.append(product_data[nkey])

		for npkey,npdata in enumerate(new_product_data):
			get_offer_product =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,
				o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`is_online`,o.`instruction`,o.`status`
			FROM `product_offer_mapping` pom 
			INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id` 
			WHERE pom.`organisation_id` = %s and pom.`product_id` = %s""")
			get_offer_data = (organisation_id,npdata['product_id'])
			count_offer_product = cursor.execute(get_offer_product,get_offer_data)
			if count_offer_product > 0:
				offer_product = cursor.fetchall()
				new_product_data[npkey]['offer_product'] = offer_product
			else:
				new_product_data[npkey]['offer_product'] = []

			get_product_status_query = (""" SELECT pom.`product_status` 
											FROM `product_organisation_mapping` pom
											WHERE  pom.`organisation_id` = %s and pom.`product_id` = %s""") 
			get_product_status_data = (organisation_id,npdata['product_id'])
			count_product_status = cursor.execute(get_product_status_query,get_product_status_data)

			if count_product_status > 0:
				status_product = cursor.fetchone()
				new_product_data[npkey]['product_status'] = status_product['product_status']
			else:
				new_product_data[npkey]['product_status'] = 0
				
		return ({"attributes": {
		    		"status_desc": "Product Data",
		    		"status": "success"
		    	},
		    	"responseList":new_product_data}), status.HTTP_200_OK

#----------------------Product-List-By-Category-Id-And-Brnad-Id---------------------#

#----------------------Product-meta-List---------------------#

@name_space.route("/productMetaList/<int:product_id>/<int:organisation_id>")	
class productMetaList(Resource):
	def get(self,product_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_long_description`,
			pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,pm.`loyalty_points`,mkvm.`meta_key_value` brand,c.`category_name`
			FROM `product` p
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
			INNER JOIN `category` c ON c.`category_id` = p.`category_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = pbm.`brand_id`			
			WHERE p.`status` = 1 and p.`product_id` = %s and pom.`organisation_id` = %s and pbm.`organisation_id` = %s and c.`organisation_id` = %s""")
		get_data = (product_id,organisation_id,organisation_id,organisation_id)
		cursor.execute(get_query,get_data)

		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):

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

					product_data[key]['met_key_value'] = met_key

			get_out_price_query = (""" SELECT `out_price`,`status` as `product_meta_out_price_status` FROM `product_meta_out_price` where `organisation_id` = %s and `status` = 1 and `product_meta_id` = %s""")
			get_out_price_data = (organisation_id, data['product_meta_id'])
			count_out_price_data = cursor.execute(get_out_price_query,get_out_price_data)
			if count_out_price_data >0:
				out_price_data = cursor.fetchone()
				product_data[key]['out_price'] = out_price_data['out_price']
				product_data[key]['product_meta_out_price_status'] = out_price_data['product_meta_out_price_status']
			else:
				product_data[key]['out_price'] = data['out_price']
				product_data[key]['product_meta_out_price_status'] = 0

			image_a = []	
			get_query_images = ("""SELECT `image`
						FROM `product_meta_images` WHERE `product_meta_id` = %s """)
			getdata_images = (data['product_meta_id'])
			cursor.execute(get_query_images,getdata_images)
			images = cursor.fetchall()

			for image in images:
				image_a.append(image['image'])

			product_data[key]['images'] = image_a


			get_latest_product_query = ("""SELECT `product_meta_id`
			FROM `latest_product_mapping` WHERE  `product_meta_id` = %s""")

			getLatesProductData = (data['product_meta_id'])
		
			count_latest_product = cursor.execute(get_latest_product_query,getLatesProductData)

			if count_latest_product > 0:
				product_data[key]['latest_product'] = 1
			else:
				product_data[key]['latest_product'] = 0


			get_top_selling_product_query = ("""SELECT `product_meta_id`
			FROM `product_top_selling_mapping` WHERE  `product_meta_id` = %s and `organisation_id` = %s""")

			getTopSellingData = (data['product_meta_id'],organisation_id)
		
			count_top_selling_product = cursor.execute(get_top_selling_product_query,getTopSellingData)

			if count_top_selling_product > 0:
				product_data[key]['top_selling_product'] = 1
			else:
				product_data[key]['top_selling_product'] = 0


			get_best_selling_product_query = ("""SELECT `product_meta_id`
			FROM `product_best_selling_mapping` WHERE  `product_meta_id` = %s and `organisation_id` = %s""")

			getBestSellingData = (data['product_meta_id'],organisation_id)
		
			count_best_selling_product = cursor.execute(get_best_selling_product_query,getBestSellingData)

			if count_best_selling_product > 0:
				product_data[key]['best_selling_product'] = 1
			else:
				product_data[key]['best_selling_product'] = 0

			get_product_meta_stock_query = ("""SELECT `product_meta_id`,`stock`
			FROM `product_inventory` WHERE  `product_meta_id` = %s and `organisation_id` = %s """)
			getProductMetaStockData = (data['product_meta_id'],organisation_id)

			count_product_meta_stock = cursor.execute(get_product_meta_stock_query,getProductMetaStockData)

			if count_product_meta_stock >0:
				product_meta_stock = cursor.fetchone()
				product_data[key]['stock'] = product_meta_stock['stock']
			else:
				product_data[key]['stock'] = 0	

			get_query_discount = ("""SELECT `discount`
										FROM `product_meta_discount_mapping` pdm
										INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
										WHERE `product_meta_id` = %s and pdm.`organisation_id` = %s""")
			getdata_discount = (data['product_meta_id'],organisation_id)
			count_dicscount = cursor.execute(get_query_discount,getdata_discount)

			if count_dicscount > 0:
				product_meta_discount = cursor.fetchone()
				product_data[key]['discount'] = product_meta_discount['discount']

				discount = (data['out_price']/100)*product_meta_discount['discount']
				actual_amount = data['out_price'] - discount

				product_data[key]['after_discounted_price'] = actual_amount  
			else:
				product_data[key]['discount'] = 0
				product_data[key]['after_discounted_price'] = data['out_price']


			product_meta_offer_mapping_query = (""" SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,o.`discount_percentage`,
				o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`is_online`,o.`instruction`,o.`status`,o.`is_product_meta_offer`,o.`validity_date`
						FROM `product_meta_offer_mapping` pmom
						INNER JOIN `offer` o ON o.`offer_id` = pmom.`offer_id` 
						where  pmom.`organisation_id` = %s and `product_id` = %s and `product_meta_id` = %s""")
			product_meta_offer_mapping_data = (organisation_id,data['product_id'],data['product_meta_id'])
			count_product_meta_offer_mapping_data = cursor.execute(product_meta_offer_mapping_query,product_meta_offer_mapping_data)

			if count_product_meta_offer_mapping_data > 0:
				offer_product_meta = cursor.fetchall()

				for opmkey,opmdata in enumerate(offer_product_meta):
					get_query_offer_image = ("""SELECT `offer_image` FROM `offer_images` WHERE `offer_id` = %s""")
					getdata_offer_image = (opmdata['offer_id'])
					image_count = cursor.execute(get_query_offer_image,getdata_offer_image)

					if image_count > 0:
						offer_images = cursor.fetchall()
						image_a = []

						for image_offer in offer_images:
							image_a.append(image_offer['offer_image'])

						offer_product_meta[opmkey]['images'] = image_a
					else:
						offer_product_meta[opmkey]['images'] = []

				product_data[key]['offer_product'] = offer_product_meta			

			else:
				get_offer_product =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,o.`discount_percentage`,
					o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`is_online`,o.`instruction`,o.`status`,o.`validity_date`,o.`is_product_meta_offer`
				FROM `product_offer_mapping` pom 
				INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id` 
				WHERE pom.`organisation_id` = %s and pom.`product_id` = %s""")
				get_offer_data = (organisation_id,data['product_id'])
				count_offer_product = cursor.execute(get_offer_product,get_offer_data)
				if count_offer_product > 0:
					offer_product = cursor.fetchall()

					for opkey,opdata in enumerate(offer_product):
						get_query_offer_image = ("""SELECT `offer_image` FROM `offer_images` WHERE `offer_id` = %s""")
						getdata_offer_image = (opdata['offer_id'])
						image_count = cursor.execute(get_query_offer_image,getdata_offer_image)

						if image_count > 0:
							offer_images = cursor.fetchall()
							image_a = []

							for image_offer in offer_images:
								image_a.append(image_offer['offer_image'])

							offer_product[opkey]['images'] = image_a
						else:
							offer_product[opkey]['images'] = []

					product_data[key]['offer_product'] = offer_product
				else:
					product_data[key]['offer_product'] = []
			

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-meta-List---------------------#

#-----------------------Retailer-List-With-Stock---------------------#

@name_space.route("/getRetailerListWithStock/<int:organisation_id>/<int:product_meta_id>")	
class getRetailerListWithStock(Resource):
	def get(self,organisation_id,product_meta_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_retailer_store_query = ("""SELECT rs.`retailer_store_id`,rs.`retailer_name`,rs.`city`
			FROM `retailer_store` rs			
			WHERE rs.`organisation_id` = %s""")

		get_retailer_data = (organisation_id)
		cursor.execute(get_retailer_store_query,get_retailer_data)

		retailer_store_data = cursor.fetchall()

		for key,data in enumerate(retailer_store_data):
			get_product_meta_store_query = ("""SELECT pi.`stock`
			FROM `product_inventory` pi			
			WHERE pi.`retailer_store_id` = %s and pi.`product_meta_id` = %s""")

			get_product_meta_store_data = (data['retailer_store_id'],product_meta_id)
			count = cursor.execute(get_product_meta_store_query,get_product_meta_store_data)

			if count >0: 
				retailer_store_stock_data = cursor.fetchone()
				retailer_store_data[key]['stock'] = 1
			else:
				retailer_store_data[key]['stock'] = 0

			get_query =  ("""SELECT rss.`address`,rss.`latitude`,rss.`longitude`,rss.`phoneno`
				FROM `retailer_store_stores` rss 
				where rss.`organisation_id` = %s and rss.`retailer_store_id` = %s""")	
			get_data = (organisation_id,data['retailer_store_id'])
			count_reatiler = cursor.execute(get_query,get_data)

			if count_reatiler > 0:
				retailer_store_data[key]['is_retailer_store'] = 1
			else:
				retailer_store_data[key]['is_retailer_store'] = 0				
				
		return ({"attributes": {
		    		"status_desc": "retailer_store_details",
		    		"status": "success"
		    	},
		    	"responseList":retailer_store_data}), status.HTTP_200_OK

#-----------------------Retailer-List-With-Stock---------------------#

#-----------------------Retaile-Store-List-With-Stock---------------------#

@name_space.route("/getRetailStoreListWithStock/<int:organisation_id>/<int:product_meta_id>")	
class getRetailStoreListWithStock(Resource):
	def get(self,organisation_id,product_meta_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_retailer_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`,rss.`store_name`,rss.`address`
			FROM `retailer_store_stores` rss
			INNER JOIN `retailer_store` rs on rs.`retailer_store_id` = rss.`retailer_store_id`
			WHERE rs.`organisation_id` = %s""")

		get_retailer_data = (organisation_id)
		cursor.execute(get_retailer_store_query,get_retailer_data)

		retailer_store_data = cursor.fetchall()

		for key,data in enumerate(retailer_store_data):
			get_product_meta_store_query = ("""SELECT pi.`stock`
			FROM `product_inventory` pi			
			WHERE pi.`retailer_store_id` = %s and pi.`product_meta_id` = %s and pi.`retailer_store_store_id` = %s""")

			get_product_meta_store_data = (data['retailer_store_id'],product_meta_id,data['retailer_store_store_id'])
			count = cursor.execute(get_product_meta_store_query,get_product_meta_store_data)

			if count >0: 
				retailer_store_stock_data = cursor.fetchone()
				retailer_store_data[key]['stock'] = 1
			else:
				retailer_store_data[key]['stock'] = 0						
				
		return ({"attributes": {
		    		"status_desc": "retailer_store_details",
		    		"status": "success"
		    	},
		    	"responseList":retailer_store_data}), status.HTTP_200_OK

#-----------------------Retaile-Store-List-With-Stock---------------------#

#-----------------------Retaile-Store-List-With-Stock---------------------#

@name_space.route("/getRetailStoreWithStock/<int:organisation_id>/<int:product_meta_id>/<int:retailer_store_store_id>")	
class getRetailStoreWithStock(Resource):
	def get(self,organisation_id,product_meta_id,retailer_store_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_retailer_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`,rss.`store_name`,rss.`address`
			FROM `retailer_store_stores` rss
			INNER JOIN `retailer_store` rs on rs.`retailer_store_id` = rss.`retailer_store_id`
			WHERE rs.`organisation_id` = %s and rss.`retailer_store_store_id` = %s""")

		get_retailer_data = (organisation_id,retailer_store_store_id)
		cursor.execute(get_retailer_store_query,get_retailer_data)

		retailer_store_data = cursor.fetchall()

		for key,data in enumerate(retailer_store_data):
			get_product_meta_store_query = ("""SELECT pi.`stock`
			FROM `product_inventory` pi			
			WHERE pi.`retailer_store_id` = %s and pi.`product_meta_id` = %s and pi.`retailer_store_store_id` = %s""")

			get_product_meta_store_data = (data['retailer_store_id'],product_meta_id,data['retailer_store_store_id'])
			count = cursor.execute(get_product_meta_store_query,get_product_meta_store_data)

			if count >0: 
				retailer_store_stock_data = cursor.fetchone()
				retailer_store_data[key]['stock'] = 1
			else:
				retailer_store_data[key]['stock'] = 0						
				
		return ({"attributes": {
		    		"status_desc": "retailer_store_details",
		    		"status": "success"
		    	},
		    	"responseList":retailer_store_data}), status.HTTP_200_OK

#-----------------------Retaile-Store-List-With-Stock---------------------#

#-----------------------Update-Stock---------------------#

@name_space.route("/updateStock")	
class updateStock(Resource):
	@api.expect(stock_putmodel)
	def put(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		retailer_store_id = details['retailer_store_id']
		stock = details['stock']
		product_meta_id = details['product_meta_id']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		product_meta_transaction_status = 1

		if stock == 1:
			get_product_inventory_query = ("""SELECT `product_meta_id`,`stock`
				FROM `product_inventory` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
			get_prodcut_inventory_Data = (product_meta_id,retailer_store_id,organisation_id)			
			count_product_inventory = cursor.execute(get_product_inventory_query,get_prodcut_inventory_Data)

			if count_product_inventory >0:
				course_update_query = ("""UPDATE `product_inventory` SET `stock` = %s
					WHERE `product_meta_id` = %s and retailer_store_id = %s and `organisation_id` = %s""")
				update_data = (stock,product_meta_id,retailer_store_id,organisation_id)
				cursor.execute(course_update_query,update_data)
			else:	
				insert_product_inventory_query = ("""INSERT INTO `product_inventory`(`product_meta_id`,`stock`,`retailer_store_id`,`status`,
					`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s)""")

				insert_product_inventory_data = (product_meta_id,stock,retailer_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				cursor.execute(insert_product_inventory_query,insert_product_inventory_data)
				product_inventory_id = cursor.lastrowid

			get_product_transaction_query = ("""SELECT `product_meta_id`,`previous_stock`,`updated_stock`
				FROM `product_transaction` WHERE  `product_meta_id` = %s and retailer_store_id = %s and organisation_id = %s""")
			get_prodcut_transaction_Data = (product_meta_id,retailer_store_id,organisation_id)		
			count_product_transaction = cursor.execute(get_product_transaction_query,get_prodcut_transaction_Data)
			


			if count_product_transaction > 0:
				product_transaction = cursor.fetchone();
				insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,`retailer_store_id`,
				`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s)""")

				insert_product_transaction_data = (product_meta_id,product_transaction['updated_stock'],stock,retailer_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				cursor.execute(insert_product_transaction_query,insert_product_transaction_data)	


			else:
				insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,`retailer_store_id`,
				`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s)""")
				previous_stock = 0
				insert_product_transaction_data = (product_meta_id,previous_stock,stock,retailer_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				cursor.execute(insert_product_transaction_query,insert_product_transaction_data)

		else:
			delete_product_inventory_query = ("""DELETE FROM `product_inventory` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
			delproductInventoryData = (product_meta_id,retailer_store_id,organisation_id)
		
			cursor.execute(delete_product_inventory_query,delproductInventoryData)

			delete_product_transaction_query = ("""DELETE FROM `product_transaction` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
			cursor.execute(delete_product_transaction_query,delproductInventoryData)

		return ({"attributes": {"status_desc": "Update Stock",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#-----------------------Update-Stock---------------------#

#-----------------------Update-Stock-Store-Specific---------------------#

@name_space.route("/updateStockStoreSpecific")	
class updateStockStoreSpecific(Resource):
	@api.expect(store_stock_putmodel)
	def put(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		retailer_store_id = details['retailer_store_id']
		retailer_store_store_id = details['retailer_store_store_id']
		stock = details['stock']
		product_meta_id = details['product_meta_id']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		product_meta_transaction_status = 1

		if stock == 1:
			get_product_inventory_query = ("""SELECT `product_meta_id`,`stock`
				FROM `product_inventory` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s and `retailer_store_store_id` = %s""")
			get_prodcut_inventory_Data = (product_meta_id,retailer_store_id,organisation_id,retailer_store_store_id)			
			count_product_inventory = cursor.execute(get_product_inventory_query,get_prodcut_inventory_Data)

			if count_product_inventory >0:
				course_update_query = ("""UPDATE `product_inventory` SET `stock` = %s
					WHERE `product_meta_id` = %s and retailer_store_id = %s and `organisation_id` = %s and `retailer_store_store_id` = %s""")
				update_data = (stock,product_meta_id,retailer_store_id,organisation_id,retailer_store_store_id)
				cursor.execute(course_update_query,update_data)
			else:	
				insert_product_inventory_query = ("""INSERT INTO `product_inventory`(`product_meta_id`,`stock`,`retailer_store_id`,`retailer_store_store_id`,`status`,
					`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s,%s)""")

				insert_product_inventory_data = (product_meta_id,stock,retailer_store_id,retailer_store_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				cursor.execute(insert_product_inventory_query,insert_product_inventory_data)
				product_inventory_id = cursor.lastrowid

			get_product_transaction_query = ("""SELECT `product_meta_id`,`previous_stock`,`updated_stock`
				FROM `product_transaction` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `retailer_store_store_id` = %s and organisation_id = %s""")
			get_prodcut_transaction_Data = (product_meta_id,retailer_store_id,retailer_store_store_id,organisation_id)		
			count_product_transaction = cursor.execute(get_product_transaction_query,get_prodcut_transaction_Data)
			


			#if count_product_transaction > 0:
				#product_transaction = cursor.fetchone();
				#insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,`retailer_store_id`,`retailer_store_store_id`,
				#`status`,`organisation_id`,`last_update_id`) 
					#VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

				#insert_product_transaction_data = (product_meta_id,product_transaction['updated_stock'],stock,retailer_store_id,retailer_store_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				#cursor.execute(insert_product_transaction_query,insert_product_transaction_data)	


			if count_product_transaction < 1:
				insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,`retailer_store_id`,`retailer_store_store_id`,
				`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
				previous_stock = 0
				insert_product_transaction_data = (product_meta_id,previous_stock,stock,retailer_store_id,retailer_store_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				cursor.execute(insert_product_transaction_query,insert_product_transaction_data)

			get_product_meta_query = ("""SELECT p.`product_name`,pm.`meta_key_text`
				FROM `product_meta` pm
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				WHERE  pm.`product_meta_id` = %s """)
			get_product_meta_data = (product_meta_id)
			cursor.execute(get_product_meta_query,get_product_meta_data)

			product_meta_data = cursor.fetchone()

			a_string = product_meta_data['meta_key_text']
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

				product_meta_data['met_key_value'] = met_key

			print(product_meta_data['met_key_value']['Storage'])

			get_miss_opportunity_query = ("""SELECT *
				FROM `miss_opportunity` mo				
				WHERE  mo.`product_meta_id` = %s and mo.`retailer_store_store_id` = %s and mo.`organisation_id` = %s""")
			get_miss_opportunity_data = (product_meta_id,retailer_store_store_id,organisation_id)
			count_miss_opportunity = cursor.execute(get_miss_opportunity_query,get_miss_opportunity_data)

			if count_miss_opportunity > 0:
				miss_opportunity_data = cursor.fetchone()

				url = BASE_URL+"ecommerce_product_admin/EcommerceProductAdmin/sendNotifications"
				post_data = {
								"title":"Dear Customer",
								"text":"We are happy to notify you "+product_meta_data['product_name']+"("+product_meta_data['met_key_value']['Storage']+" "+product_meta_data['met_key_value']['Color']+" "+product_meta_data['met_key_value']['Ram']+") is back in stock.",
								"customer_id":miss_opportunity_data['customer_id'],
								"organisation_id":organisation_id
							}
				print(post_data)

				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				post_response = requests.post(url, data=json.dumps(post_data), headers=headers).json()

		else:
			delete_product_inventory_query = ("""DELETE FROM `product_inventory` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
			delproductInventoryData = (product_meta_id,retailer_store_id,organisation_id)
		
			cursor.execute(delete_product_inventory_query,delproductInventoryData)

			delete_product_transaction_query = ("""DELETE FROM `product_transaction` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
			cursor.execute(delete_product_transaction_query,delproductInventoryData)

		return ({"attributes": {"status_desc": "Update Stock",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#-----------------------Update-Stock-Store-Specific---------------------#

#-----------------------Update-All-Product-Stock-Store-Specific---------------------#

@name_space.route("/updateAllProductStockStoreSpecific")	
class updateAllProductStockStoreSpecific(Resource):
	@api.expect(store_all_product_stock_postmodel)
	def put(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		stock_data = {}
	
		stock_data['retailer_store_store_id'] = details['retailer_store_store_id']
		stock_data['stock'] = details['stock']		
		stock_data['organisation_id'] = details['organisation_id']
		stock_data['last_update_id'] = details['last_update_id']

		print(stock_data)


		def updateAllProductStockStoreSpecificAsync(**kwargs):
			stock_data = kwargs.get('post_data', {})

			connection = mysql_connection()
			cursor = connection.cursor()		
		
			retailer_store_store_id = stock_data['retailer_store_store_id']
			stock = stock_data['stock']		
			organisation_id = stock_data['organisation_id']
			last_update_id = stock_data['last_update_id']

			get_query_retail_store = ("""SELECT *
						FROM `retailer_store_stores` WHERE `retailer_store_store_id` = %s and organisation_id = %s""")
			getDataRetailStore = (retailer_store_store_id,organisation_id)
			count_Retail_Store = cursor.execute(get_query_retail_store,getDataRetailStore)

			retail_store = cursor.fetchone()

			get_product_meta_query = ("""SELECT `product_meta_id`
				FROM `product_meta` pm
				INNER JOIN `product_organisation_mapping` pom  ON pom.`product_id` = pm.`product_id`
				WHERE pom.`product_status` = 1 and pom.`organisation_id` = %s""")
			get_product_meta_data = (organisation_id)
			count_product_meta_data = cursor.execute(get_product_meta_query,get_product_meta_data)

			if count_product_meta_data > 0:
				product_meta_data = cursor.fetchall()
				for key,data in enumerate(product_meta_data):
					url = BASE_URL+"ecommerce_product_admin/EcommerceProductAdmin/updateStockStoreSpecific"
					post_data = {
								  	"retailer_store_id":retail_store['retailer_store_id'],
									"retailer_store_store_id":retailer_store_store_id,
									"stock":stock,
									"product_meta_id":data['product_meta_id'],
									"organisation_id":organisation_id,
									"last_update_id":last_update_id
								}

					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					post_response = requests.put(url, data=json.dumps(post_data), headers=headers)

		
		thread = threading.Thread(target=updateAllProductStockStoreSpecificAsync, kwargs={
                    'post_data': stock_data})
		thread.start()			

		return ({"attributes": {"status_desc": "Update Stock",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#-----------------------Update-All-Product-Stock-Store-Specific---------------------#

#-----------------------Update-All-Product-Stock-Store-Specific-Async---------------------#


#----------------------Send-Notification---------------------#

@name_space.route("/sendNotifications")
class sendNotifications(Resource):
	@api.expect(notification_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		customer_id = details['customer_id']
		organisation_id = details['organisation_id']	

		get_organisation_firebase_query = ("""SELECT `firebase_key`
								FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
		get_organisation_firebase_data = (organisation_id)
		cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
		firebase_data = cursor.fetchone()

		get_device_query = ("""SELECT *
									FROM `devices` WHERE  `organisation_id` = %s and `user_id` = %s""")
		get_device_data = (organisation_id,customer_id)
		cursor.execute(get_device_query,get_device_data)
		device_data = cursor.fetchone()

		data_message = {
							"title" : details['title'],
							"message": details['text'],
							"image-url":""
						}

		api_key = firebase_data['firebase_key']
		device_id = device_data['device_token']
		push_service = FCMNotification(api_key=api_key)
		msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = data_message)
		sent = 'N'
		if msgResponse.get('success') == 1:
			sent = 'Y'
			app_query = ("""INSERT INTO `app_notification`(`title`,`body`,`image`,
					`U_id`,`Device_ID`,`Sent`,`source_id`,`source_type`,`destination_type`,`organisation_id`) 
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			sent = 'Yes'
			destination_type = 2
			source_id = 0
			source_type = 3
			insert_data = (details['title'],details['text'],"",customer_id,device_data['device_token'],sent,source_id,source_type,destination_type,organisation_id)
			appdata = cursor.execute(app_query,insert_data)
		
		
		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				    	"responseList":msgResponse}), status.HTTP_200_OK

#----------------------Send-Notification---------------------#	

#-----------------------Update-All-Product-Stock-Store-Specific-Async---------------------#

#-----------------------Update-Stock-while-buy---------------------#

@name_space.route("/updateStockwithBuy")	
class updateStockwithBuy(Resource):
	@api.expect(stock_putmodel)
	def put(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		retailer_store_id = details['retailer_store_id']
		stock = details['stock']
		product_meta_id = details['product_meta_id']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		product_meta_transaction_status = 1

		get_product_inventory_query = ("""SELECT `product_meta_id`,`stock`
				FROM `product_inventory` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
		get_prodcut_inventory_Data = (product_meta_id,retailer_store_id,organisation_id)			
		count_product_inventory = cursor.execute(get_product_inventory_query,get_prodcut_inventory_Data)

		if count_product_inventory >0:
			product_inventory = cursor.fetchone()
			updated_stock = product_inventory['stock'] - stock
			course_update_query = ("""UPDATE `product_inventory` SET `stock` = %s
					WHERE `product_meta_id` = %s and retailer_store_id = %s and `organisation_id` = %s""")
			update_data = (updated_stock,product_meta_id,retailer_store_id,organisation_id)
			cursor.execute(course_update_query,update_data)
		else:	
			insert_product_inventory_query = ("""INSERT INTO `product_inventory`(`product_meta_id`,`stock`,`retailer_store_id`,`status`,
					`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s)""")

			insert_product_inventory_data = (product_meta_id,stock,retailer_store_id,product_meta_transaction_status,organisation_id,last_update_id)
			cursor.execute(insert_product_inventory_query,insert_product_inventory_data)
			product_inventory_id = cursor.lastrowid

		get_product_transaction_query = ("""SELECT `product_meta_id`,`previous_stock`,`updated_stock`
				FROM `product_transaction` WHERE  `product_meta_id` = %s and retailer_store_id = %s and organisation_id = %s order by product_transaction_id desc limit 1""")
		get_prodcut_transaction_Data = (product_meta_id,retailer_store_id,organisation_id)		
		count_product_transaction = cursor.execute(get_product_transaction_query,get_prodcut_transaction_Data)

		if count_product_transaction > 0:
			product_transaction = cursor.fetchone();
			insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,`retailer_store_id`,
				`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s)""")
			updated_stock = product_transaction['updated_stock'] - stock

			insert_product_transaction_data = (product_meta_id,product_transaction['updated_stock'],updated_stock,retailer_store_id,product_meta_transaction_status,organisation_id,last_update_id)
			cursor.execute(insert_product_transaction_query,insert_product_transaction_data)

		else:
				insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,`retailer_store_id`,
				`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s)""")
				previous_stock = 0
				insert_product_transaction_data = (product_meta_id,previous_stock,updated_stock,retailer_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				cursor.execute(insert_product_transaction_query,insert_product_transaction_data)

		return ({"attributes": {"status_desc": "Update Stock",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#-----------------------Update-Stock-while-buy---------------------#

#----------------------Customer-List---------------------#
@name_space.route("/customerList/<int:organisation_id>")	
class customerList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `admin_id` as `user_id`,`first_name`,`last_name`,`email`,
			`phoneno`,`profile_image`,`loggedin_status`,`date_of_lastlogin`
				FROM `admins` WHERE `organisation_id` = %s and `role_id` = 4""")
		getData = (organisation_id)
		cursor.execute(get_query,getData)

		customer_data = cursor.fetchall()

		for key,data in enumerate(customer_data):
			customer_data[key]['date_of_lastlogin'] = str(data['date_of_lastlogin'])

		return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success"
		    	},
		    	"responseList":customer_data}), status.HTTP_200_OK

#----------------------Customer-List---------------------#

#----------------------Catalog-List---------------------#
@name_space.route("/catalogListByCategoryId/<int:organisation_id>/<int:category_id>")	
class catalogListByCategoryId(Resource):
	def get(self,organisation_id,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT c.`catalog_id`,c.`catalog_name`,c.`is_home_section`,c.`last_update_ts`
			FROM `catalogs` c	
			INNER JOIN `catalog_category_mapping` ccm ON ccm.`catalog_id` = c.`catalog_id`		 
			WHERE ccm.`organisation_id` = %s and ccm.`category_id` = %s""")
		get_data = (organisation_id,category_id)

		cursor.execute(get_query,get_data)
		catalog_data = cursor.fetchall()

		for key,data in enumerate(catalog_data):
			get_product_query = ("""SELECT count(*) as product_count 
				FROM `product_catalog_mapping` pcm 
				INNER JOIN `product_meta` pm ON pm.`product_id` = pcm .`product_id`
				WHERE pcm.`catalog_id` = %s""")
			get_product_data = (data['catalog_id'])
			cursor.execute(get_product_query,get_product_data)
			catalog_product_count = cursor.fetchone()
			catalog_data[key]['product_count'] = catalog_product_count['product_count']
			catalog_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "catalog_details",
		    		"status": "success"
		    	},
		    	"responseList":catalog_data}), status.HTTP_200_OK

#----------------------Catalog-List---------------------#

#----------------------Add-Product-Catalog---------------------#

@name_space.route("/AddProductCatalog")
class AddProductCatalog(Resource):
	@api.expect(productcatalog_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		catalog_id = details['catalog_id']
		product_id = details['product_id']
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id'] 

		get_query = ("""SELECT `mapping_id`
			FROM `product_catalog_mapping` WHERE  `catalog_id` = %s and `product_id` = %s and `organisation_id` = %s""")

		getData = (catalog_id,product_id,organisation_id)
		
		count_product = cursor.execute(get_query,getData)

		if count_product > 0:

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "catalog_product",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

		else:

			insert_query = ("""INSERT INTO `product_catalog_mapping`(`catalog_id`,`product_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

			data = (catalog_id,product_id,organisation_id,last_update_id)
			cursor.execute(insert_query,data)		

			mapping_id = cursor.lastrowid
			details['mapping_id'] = mapping_id

			headers = {'Content-type':'application/json', 'Accept':'application/json'}

			createPdfeUrl = BASE_URL + "ecommerce_product_admin/EcommerceProductAdmin/createCatalougePdf"
			payloadData = {
								"catalog_id":catalog_id,
														
						  }

			createPdf = requests.post(createPdfeUrl,data=json.dumps(payloadData), headers=headers).json()

			connection.commit()
			cursor.close()

			return ({"attributes": {
					    		"status_desc": "catalog_product",
					    		"status": "success"
					    	},
					    	"responseList":details}), status.HTTP_200_OK	


#----------------------Add-Product-Catalog---------------------#

#----------------------Add-Product-Catalog---------------------#

@name_space.route("/AddMultipleProductwithCatalog")
class AddMultipleProductwithCatalog(Resource):
	@api.expect(multipleproductcatalog_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		catalog_id = details['catalog_id']
		product_ids = details.get('product_id',[])
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id'] 

		for key,product_id in enumerate(product_ids):

			get_query = ("""SELECT `mapping_id`
				FROM `product_catalog_mapping` WHERE  `catalog_id` = %s and `product_id` = %s and `organisation_id` = %s""")

			getData = (catalog_id,product_id,organisation_id)
			
			count_product = cursor.execute(get_query,getData)

			if count_product < 1:			

				insert_query = ("""INSERT INTO `product_catalog_mapping`(`catalog_id`,`product_id`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

				data = (catalog_id,product_id,organisation_id,last_update_id)
				cursor.execute(insert_query,data)		

		connection.commit()
		cursor.close()

		return ({"attributes": {
					    		"status_desc": "catalog_product",
					    		"status": "success"
					    	},
					    	"responseList":details}), status.HTTP_200_OK	


#----------------------Add-Product-Catalog---------------------#

#----------------------Add-Catalog-Catgeory---------------------#

@name_space.route("/AddCatalogCategory")
class AddCatalogCategory(Resource):
	@api.expect(catalog_category_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		catalog_id = details['catalog_id']		
		organisation_id = details['organisation_id']		 
		last_update_id =  details['organisation_id']

		if details and "is_home_section" in details:
			is_home_section = details['is_home_section']
			update_query = ("""UPDATE `catalogs` SET `is_home_section` = %s
					WHERE `catalog_id` = %s """)
			update_data = (is_home_section,catalog_id)
			cursor.execute(update_query,update_data)

		if details and "category_id" in details:
			category_id = details['category_id']
			get_catalog_category_query = ("""SELECT `catalog_id`,`category_id`
			FROM `catalog_category_mapping` WHERE  `catalog_id` = %s and `category_id` = %s and `organisation_id` = %s""")

			catalogCategoryData = (catalog_id,category_id,organisation_id)
		
			count_catalog_category = cursor.execute(get_catalog_category_query,catalogCategoryData)	

			if count_catalog_category < 1:			
				insert_query = ("""INSERT INTO `catalog_category_mapping`(`catalog_id`,`category_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

				data = (catalog_id,category_id,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

			get_category_query = ("""SELECT *
				FROM `category` c				
				WHERE c.`category_id` = %s and c.`organisation_id` = %s""")
			get_category_data = (details['category_id'],organisation_id)
			count_category = cursor.execute(get_category_query,get_category_data)

			if count_category > 0:
				category_data = cursor.fetchone()
				details['catalog_category'] = category_data['category_name']
			else:
				details['catalog_category']  = ""
		
		return ({"attributes": {
					    		"status_desc": "catalog_category",
					    		"status": "success"
					    	},
					    	"responseList":details}), status.HTTP_200_OK	


#----------------------Add-Catalog-Catgeory---------------------#

#----------------------Delete-catalog-Category---------------------#

@name_space.route("/deleteCatalogCategory/<int:catalog_id>/<int:category_id>/<int:organisation_id>")
class deleteCatalogCategory(Resource):
	def delete(self, catalog_id,category_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `catalog_category_mapping` WHERE `catalog_id` = %s and `category_id` = %s and `organisation_id` = %s""")
		delData = (catalog_id,category_id,organisation_id)
		
		cursor.execute(delete_query,delData)		

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Catalog Category",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-catalog-Category---------------------#

#----------------------Delete-catalog-Product---------------------#

@name_space.route("/deleteCatalogAllProduct/<int:catalog_id>/<int:organisation_id>")
class deleteCatalogAllProduct(Resource):
	def delete(self, catalog_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_catalog_mapping` WHERE `catalog_id` = %s and `organisation_id` = %s""")
		delData = (catalog_id,organisation_id)
		
		cursor.execute(delete_query,delData)		

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Catalog Product",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-catalog-Category---------------------#

#----------------------Delete-Product-From-Catalouge---------------------#

@name_space.route("/deleteProductFromCatalouge/<int:catalog_id>/<int:product_id>/<int:organisation_id>")
class deleteProductFromCatalouge(Resource):
	def delete(self, catalog_id,product_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_catalog_mapping` WHERE `catalog_id` = %s and `product_id` = %s and `organisation_id` = %s""")
		delData = (catalog_id,product_id,organisation_id)
		
		cursor.execute(delete_query,delData)		

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Catalog Product",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Product-From-Catalouge---------------------#

#----------------------Add-Product-With-Product-Meta---------------------#

@name_space.route("/AddProductWithProductMeta")
class AddProductWithProductMeta(Resource):
	@api.expect(product_meta_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_name = details['product_name']
		product_long_description = details['product_long_description']
		product_short_description = details['product_short_description']		
		category_id = details['category_id']
		if details and "product_type" in details:
			product_type = details['product_type']
		else:
			product_type = ""
		product_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']
		product_meta_code = details['product_meta_code']
		meta_key_text = details['meta_key_text']
		in_price = details['in_price']
		out_price = details['out_price']
		product_meta_status = 1
		images = details.get('image',[])
		other_specification_json = 0

		insert_query = ("""INSERT INTO `product`(`product_name`,`product_long_description`,
			`product_short_description`,`category_id`,`product_type`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_name,product_long_description,product_short_description,category_id,product_type,
			product_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		product_id = cursor.lastrowid

		insert_product_organisation_query = ("""INSERT INTO `product_organisation_mapping`(`product_id`,`organisation_id`,
			`last_update_id`) 
				VALUES(%s,%s,%s)""")
		product_organisation_data = (product_id,organisation_id,last_update_id)
		cursor.execute(insert_product_organisation_query,product_organisation_data)

		insert_query_product_meta = ("""INSERT INTO `product_meta`(`product_id`,`product_meta_code`,`meta_key_text`,`other_specification_json`,`in_price`,`out_price`,`status`,
			`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		product_meta_data = (product_id,product_meta_code,meta_key_text,other_specification_json,in_price,out_price,product_meta_status,organisation_id,last_update_id)
		cursor.execute(insert_query_product_meta,product_meta_data)
		product_meta_id = cursor.lastrowid

		for key,image in enumerate(images):
			if key == 0:
				default_image_flag = 1
			else:
				default_image_flag = 0

			product_meta_status_image = 1

			insert_query_image = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`status`,`organisation_id`,last_update_id) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

			data = (product_meta_id,image,default_image_flag,product_meta_status_image,organisation_id,last_update_id)
			cursor.execute(insert_query_image,data)

		if details and "brand_id" in details:		
			brand_id = details['brand_id']

			get_query = ("""SELECT *
			FROM `product_brand_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_brand = cursor.execute(get_query,get_data)

			if count_product_brand > 0:
				product_brand_data = cursor.fetchone()
				details['product_brand_id'] = product_brand_data['mapping_id']

				update_query = ("""UPDATE `product_brand_mapping` SET `brand_id` = %s
				WHERE `product_id` = %s """)
				update_data = (brand_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
				product_brand_mapping_status = 1
				data = (brand_id,product_id,product_brand_mapping_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)


		return ({"attributes": {
			    	"status_desc": "product_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Add-Product-With-Product-Meta---------------------#

#----------------------Add-Product-Meta-With-Images---------------------#

@name_space.route("/AddProductMetaWithImages")
class AddProductMetaWithImages(Resource):
	@api.expect(product_price_meta_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_id = details['product_id']
		product_meta_code = details['product_meta_code']
		meta_key_text = details['meta_key_text']
		in_price = details['in_price']
		out_price = details['out_price']
		product_meta_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		other_specification_json = 0
		images = details.get('image',[])

		insert_query = ("""INSERT INTO `product_meta`(`product_id`,`product_meta_code`,`meta_key_text`,`other_specification_json`,`in_price`,`out_price`,`status`,
			`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_id,product_meta_code,meta_key_text,other_specification_json,in_price,out_price,product_meta_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		product_meta_id = cursor.lastrowid

		details['product_meta_id'] = product_meta_id	

		for key,image in enumerate(images):
			if key == 0:
				default_image_flag = 1
			else:
				default_image_flag = 0

			product_meta_status_image = 1

			insert_query_image = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`status`,`organisation_id`,last_update_id) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

			data = (product_meta_id,image,default_image_flag,product_meta_status_image,organisation_id,last_update_id)

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_meta_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Add-Product-Meta-With-Images---------------------#

#----------------------Get-Brnad-List---------------------#
@name_space.route("/getBrandList/<int:organisation_id>")	
class getBrandList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT mkvm.`meta_key_value_id`,mkvm.`meta_key_id`,mkvm.`meta_key_value`,mkvm.`image`,mkvm.`status`,
			mkvm.`last_update_id`,mkvm.`last_update_ts` 
			FROM `organisation_brand_mapping` obm
			INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = obm .`brand_id`
			WHERE obm.`organisation_id` = %s and mkvm.`status` = 1 """)

		getdata = (organisation_id)
		cursor.execute(get_query,getdata)

		meta_value_data = cursor.fetchall()

		for key,data in enumerate(meta_value_data):

			if data['meta_key_id'] == 1:
				get_category_query = 	 ("""SELECT *
				FROM `home_category_mapping`
				WHERE `meta_key_value_id` = %s and `organisation_id` = %s""")
				get_category_data = (data['meta_key_value_id'],organisation_id)
				rows_count_category = cursor.execute(get_category_query,get_category_data)

				if rows_count_category >0:
					meta_value_data[key]['home_category'] = 1
				else:
					meta_value_data[key]['home_category'] = 0		

			else:
				get_brand_query = 	 ("""SELECT *
				FROM `home_brand_mapping`
				WHERE `meta_key_value_id` = %s and `organisation_id` = %s""")
				get_brand_data = (data['meta_key_value_id'],organisation_id)
				rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

				if rows_count_brand >0:
					meta_value_data[key]['home_brand'] = 1
				else:
					meta_value_data[key]['home_brand'] = 0	

			get_product_brand_query = (""" SELECT count(*) as product_brand_count
			 	FROM `product_brand_mapping` pbm  where pbm.`organisation_id` = %s and pbm.`brand_id` = %s""")
			get_product_brand_data = (organisation_id,data['meta_key_value_id'])
			cursor.execute(get_product_brand_query,get_product_brand_data)

			product_brand_data = cursor.fetchone()

			meta_value_data[key]['product_count'] = product_brand_data['product_brand_count']


			meta_value_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "meta_key_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_value_data}), status.HTTP_200_OK

#----------------------Get-Brnad-List---------------------#

#----------------------Get-Brnad-List---------------------#
@name_space.route("/getBrandListByCategoryId/<int:organisation_id>/<int:category_id>")	
class getBrandListByCategoryId(Resource):
	def get(self,organisation_id,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_brand_query = ("""SELECT `brand_id`
			FROM `category_brand_mapping`  WHERE `organisation_id` = %s and `category_id` = %s""")
		get_brand_data = (organisation_id,category_id)

		count_category_brand = cursor.execute(get_brand_query,get_brand_data)

		if count_category_brand > 0:

			brand_data = cursor.fetchall()
			brand_data.append({"brand_id":0})

			for hkey,hdata in enumerate(brand_data):
				if hdata['brand_id'] == 0:
					brand_data[hkey]['meta_key_value'] = "Others"
					brand_data[hkey]['image'] = ""

					get_product_brand_query = ("""SELECT count(pom.`product_id`) as product_brand_count 
						FROM `product_organisation_mapping` pom 
						INNER JOIN `product` p ON p.`product_id` = pom.`product_id` 
						WHERE pom.`product_id` not in (select `product_id` from product_brand_mapping where organisation_id = %s) 
						and pom.`organisation_id` = %s and p.`category_id` = %s""")
					get_product_brand_data = (organisation_id,organisation_id,category_id)
					cursor.execute(get_product_brand_query,get_product_brand_data)
					product_brand_data = cursor.fetchone()
					brand_data[hkey]['product_count'] = product_brand_data['product_brand_count']

				else:
					get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
					FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

					getdata_key_value = (hdata['brand_id'])
					cursor.execute(get_key_value_query,getdata_key_value)

					key_value_data = cursor.fetchone()

					brand_data[hkey]['meta_key_value'] = key_value_data['meta_key_value']
					brand_data[hkey]['image'] = key_value_data['image']

					get_product_brand_query = (""" SELECT count(*) as product_brand_count
				 	FROM `product_brand_mapping` pbm 
				 	INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`			 	
				 	where pbm.`organisation_id` = %s and pbm.`brand_id` = %s and p.`category_id` = %s""")
					get_product_brand_data = (organisation_id,hdata['brand_id'],category_id)
					cursor.execute(get_product_brand_query,get_product_brand_data)

					product_brand_data = cursor.fetchone()

					brand_data[hkey]['product_count'] = product_brand_data['product_brand_count']


		else:
			brand_data = []

		return ({"attributes": {
		    	"status_desc": "offer_details",
		    	"status": "success"
		    },
		    "responseList":brand_data}), status.HTTP_200_OK



#----------------------search-With-Language-And-Pagination---------------------#
@name_space.route("/SearchWithLanguageAndPaginationFromProductOrganisationMapping/<string:product_name>/<int:user_id>/<int:organisation_id>/<string:language>/<int:page>")	
class SearchWithLanguageAndPaginationFromProductOrganisationMapping(Resource):
	def get(self,product_name,user_id,organisation_id,language,page):

		if page == 1:
			offset = 0
			offsetvariation = 0
		else:
			offset = page * 20
			offsetvariation = page *2

		connection = mysql_connection()
		cursor = connection.cursor()

		product_status = 1

		if page > 0:
			get_product_query = ("""SELECT p.`product_id`,p.`product_name`,
								pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
							 	FROM `product` p						 	 						 	
						 		INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`	
						 		INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`					 			 
								WHERE p.`product_name` LIKE %s and pom.`organisation_id` = %s and p.`status` = %s and p.`language` = %s limit %s,20""")
			getProductData = ("%"+product_name+"%",organisation_id,product_status,language,offset)
			count_product_data = cursor.execute(get_product_query,getProductData)
		else:
			get_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_short_description`,
								pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
							 	FROM `product` p						 	
						 		INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`	
						 		INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`					 			 
								WHERE p.`product_name` LIKE %s and pom.`organisation_id` = %s and p.`status` = %s and p.`language` = %s""")
			getProductData = ("%"+product_name+"%",organisation_id,product_status,language)
			count_product_data = cursor.execute(get_product_query,getProductData)
						
		if count_product_data > 0:
			search_meta = cursor.fetchall()

			for key,data in enumerate(search_meta):
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


				get_query_image = ("""SELECT `image`
														FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
				getdata_image = (data['product_meta_id'])
				product_image_count = cursor.execute(get_query_image,getdata_image)

				if product_image_count >0 :
					product_image = cursor.fetchone()
					search_meta[key]['image'] = product_image['image']
				else:
					search_meta[key]['image'] = ""				
				

			if page > 0:		
				get_product_query_count = ("""SELECT count(*) as product_count
							FROM `product` p
							INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
							INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
							WHERE p.`product_name` LIKE %s and pom.`organisation_id` = %s and p.`status` = %s and p.`language` = %s""")
				getProductDataCount = ("%"+product_name+"%",organisation_id,product_status,language)
				cursor.execute(get_product_query_count,getProductDataCount)
					
				product_data_count = cursor.fetchone()

				page_count = math.trunc(product_data_count['product_count']/20)

				if page_count == 0:
					page_count = 1
				else:
					page_count = page_count + 1
			else:
				get_product_query_count = ("""SELECT count(*) as product_count
							FROM `product` p
							INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
							INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
							WHERE p.`product_name` LIKE %s and pom.`organisation_id` = %s and p.`status` = %s and p.`language` = %s""")
				getProductDataCount = ("%"+product_name+"%",organisation_id,product_status,language)
				page_count = cursor.execute(get_product_query_count,getProductDataCount)
		else:
			search_meta = []	

		return ({"attributes": {
					"status_desc": "product_list",
					"status": "success",
					"page_count":page_count,
					"page":page
				},
				"responseList":search_meta}), status.HTTP_200_OK

#----------------------search-With-Language-And-Pagination---------------------#

#----------------------Filter-With-Language-And-Pagination---------------------#

@name_space.route("/FilterhWithLanguageAndPaginationFromProductOrganisationMapping/<int:organisation_id>/<string:ram_value>/<string:storage_value>/<string:color_value>/<string:language>/<int:page>/<int:from_price>/<int:to_price>")	
class FilterhWithLanguageAndPaginationFromProductOrganisationMapping(Resource):
	@api.expect(filter_postmodel)
	def post(self,organisation_id,ram_value,storage_value,color_value,language,page,from_price,to_price):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		meta_keys = ["Storage","Color","Ram"]

		meta_key_text = []

		new_data = []

		brand_ids = details.get('brand_id',[])			

		for meta_key in meta_keys:
			if meta_key == "Storage" and storage_value != "na":
				get_meta_query = ("""SELECT `meta_key_id`,`meta_key` FROM `meta_key_master`
										 WHERE  `meta_key` LIKE %s and `organisation_id` = 1 """)
				getmetadata = (meta_key)
				count_meta_data = cursor.execute(get_meta_query,getmetadata)
					
				search_meta = cursor.fetchone()
				print(search_meta)
				get_meta_value_query = ("""SELECT `meta_key_value_id` FROM `meta_key_value_master` WHERE `meta_key_id` = %s
							 and `organisation_id` = 1 and `status` = 1 and `meta_key_value` = %s """)
				getdata_meta_data = (search_meta['meta_key_id'],storage_value)
				cursor.execute(get_meta_value_query,getdata_meta_data)

				meta_value_data = cursor.fetchone()

				meta_key_text.append(str(meta_value_data['meta_key_value_id']))				


			if meta_key == "Color" and color_value != "na":
				get_meta_query = ("""SELECT `meta_key_id`,`meta_key` FROM `meta_key_master`
										 WHERE  `meta_key` LIKE %s and `organisation_id` = 1 """)
				getmetadata = (meta_key)
				count_meta_data = cursor.execute(get_meta_query,getmetadata)
					
				search_meta = cursor.fetchone()
				get_meta_value_query = ("""SELECT `meta_key_value_id` FROM `meta_key_value_master` WHERE `meta_key_id` = %s
							 and `organisation_id` = 1 and `status` = 1 and `meta_key_value` = %s""")
				getdata_meta_data = (search_meta['meta_key_id'],color_value)
				cursor.execute(get_meta_value_query,getdata_meta_data)

				meta_value_data = cursor.fetchone()

				meta_key_text.append(str(meta_value_data['meta_key_value_id']))	

			if meta_key == "Ram" and ram_value != "na":

				get_meta_query = ("""SELECT `meta_key_id`,`meta_key` FROM `meta_key_master`
										 WHERE  `meta_key` LIKE %s and `organisation_id` = 1 """)
				getmetadata = (meta_key)
				count_meta_data = cursor.execute(get_meta_query,getmetadata)
					
				search_meta = cursor.fetchone()
				get_meta_value_query = ("""SELECT `meta_key_value_id` FROM `meta_key_value_master` WHERE `meta_key_id` = %s
							 and `organisation_id` = 1 and `status` = 1 and `meta_key_value` = %s""")
				getdata_meta_data = (search_meta['meta_key_id'],ram_value)
				cursor.execute(get_meta_value_query,getdata_meta_data)

				meta_value_data = cursor.fetchone()

				meta_key_text.append(str(meta_value_data['meta_key_value_id']))		


		smeta_key_text = ","		
		smeta_key_text = smeta_key_text.join(meta_key_text)
		print(smeta_key_text)

		for brand_id in brand_ids:

			get_query = ("""SELECT p.`product_id`,p.`product_name`,
					pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,pm.`loyalty_points`
					FROM `product_brand_mapping` pbm
					INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`				
					INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
					WHERE p.`status` = 1 and pm.`meta_key_text` = %s and pbm.`organisation_id` = %s and pm.`out_price` BETWEEN %s AND %s and pbm.`brand_id` = %s""")
			get_data = (smeta_key_text,organisation_id,from_price,to_price,brand_id)
			product_count = cursor.execute(get_query,get_data)

			product_data = cursor.fetchall()

				#print(product_data)

			if product_count >0 :
					

				for key,data in enumerate(product_data):

					get_query_image = ("""SELECT `image`
													FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
					getdata_image = (data['product_meta_id'])
					product_image_count = cursor.execute(get_query_image,getdata_image)

					if product_image_count >0 :
						product_image = cursor.fetchone()
						product_data[key]['image'] = product_image['image']
					else:
						product_data[key]['image'] = ""

					a_string = data['meta_key_text']
					a_list = a_string.split(',')

					met_key = {}

					for a in a_list:
						get_query_key_value = ("""SELECT mkvm.`meta_key_id`,`meta_key_value`,mkm.`meta_key` 
								FROM `meta_key_value_master` mkvm 
								INNER JOIN `meta_key_master` mkm ON mkvm.`meta_key_id` = mkm.`meta_key_id`
								WHERE `meta_key_value_id` = %s """)
						getdata_key_value = (a)
						cursor.execute(get_query_key_value,getdata_key_value)
						met_key_value_data = cursor.fetchone()

						met_key.update({met_key_value_data['meta_key']:met_key_value_data['meta_key_value']})

						product_data[key]['met_key_value'] = met_key
							
					new_data.append(product_data[key])

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":new_data}), status.HTTP_200_OK	

#----------------------Filter-With-Language-And-Pagination---------------------#

#----------------------Update-Otp-Settings---------------------#

@name_space.route("/UpdateOtpSettings/<int:organisation_id>")
class UpdateOtpSettings(Resource):
	@api.expect(update_otp_settings_model)
	def put(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "otp_setting_value" in details:
			otp_setting_value = details['otp_setting_value']
			get_otp_settings_query = ("""SELECT *				
									FROM `otp_settings`						
									WHERE `organisation_id` = %s """)
			getDataLogin = (organisation_id)
			count_otp_setings = cursor.execute(get_otp_settings_query,getDataLogin)

			if count_otp_setings > 0:									
				update_query = ("""UPDATE `otp_settings` SET `otp_setting_value` = %s
						WHERE `organisation_id` = %s """)
				update_data = (otp_setting_value,organisation_id)
				cursor.execute(update_query,update_data)
			else:
				if otp_setting_value == 1:
					insert_query = ("""INSERT INTO `otp_settings`(`otp_setting_value`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
					data = (otp_setting_value,organisation_id,organisation_id)
					cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Otp Settings",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Otp-Settings---------------------#

#----------------------Referal-Loyality-Details---------------------#
@name_space.route("/ReferalLoyalityDetails/<int:organisation_id>")	
class ReferalLoyalityDetails(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
				FROM `referal_loyality_settings` rfl				 
				WHERE `organisation_id` = %s""")
		getData = (organisation_id)
		count_data = cursor.execute(get_query,getData)	

		if count_data > 0:
			referel_loyality_data = cursor.fetchone()
			referel_loyality_data['last_update_ts'] = str(referel_loyality_data['last_update_ts'])
		else:
			referel_loyality_data = {}


		return ({"attributes": {
		    		"status_desc": "referal_loyality_details",
		    		"status": "success"
		    	},
		    	"responseList":referel_loyality_data}), status.HTTP_200_OK

#----------------------Referal-Loyality-Details---------------------#


#----------------------Update-Loyality-Settings---------------------#

@name_space.route("/UpdateReferalLoyalitySettings/<int:organisation_id>")
class UpdateReferalLoyalitySettings(Resource):
	@api.expect(update_referal_loyality_settings_model)
	def put(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "setting_value" in details:
			setting_value = details['setting_value']
			get_settings_query = ("""SELECT *				
									FROM `referal_loyality_settings`						
									WHERE `organisation_id` = %s """)
			getDataLogin = (organisation_id)
			count_setings = cursor.execute(get_settings_query,getDataLogin)

			if count_setings > 0:									
				update_query = ("""UPDATE `referal_loyality_settings` SET `setting_value` = %s
						WHERE `organisation_id` = %s """)
				update_data = (setting_value,organisation_id)
				cursor.execute(update_query,update_data)
			else:
				if setting_value == 1:
					insert_query = ("""INSERT INTO `referal_loyality_settings`(`setting_value`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
					data = (setting_value,organisation_id,organisation_id)
					cursor.execute(insert_query,data)

		return ({"attributes": {"status_desc": "Update Referal Loyality Settings",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Loyality-Settings---------------------#

#----------------------Update-Category---------------------#	
@name_space.route("/UpdateCategory/<int:category_id>/<int:organisation_id>")	
class UpdateCategory(Resource):
	@api.expect(category_putmodel)
	def put(self,category_id,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		categorystatus = details['status']
		
		update_query = ("""UPDATE `category` SET `status` = %s
				WHERE `category_id` = %s and `organisation_id` = %s""")
		update_data = (categorystatus,category_id,organisation_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update_Category",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK
#----------------------Update-Category---------------------#	

#----------------------Customer-Exchange---------------------#

@name_space.route("/getCustomerExchangeWithPagination/<int:organisation_id>/<int:page>/<int:final_submission_status>/<int:exchange_status>/<string:start_date>/<string:end_date>")	
class getCustomerExchangeWithPagination(Resource):
	def get(self,organisation_id,page,final_submission_status,exchange_status,start_date,end_date):
		if page == 1:
			offset = 0
		else:
			offset = (page-1) * 20

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT ced.`exchange_id`,ced.`amount`,ced.`front_image`,ced.`back_image`,ced.`device_model`,ced.`last_update_ts`,a.`first_name`,a.`last_name`,ced.`status`,a.`admin_id` as `user_id`,a.`phoneno`,ced.`final_submission_status`,ced.`Is_clone`
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = %s and ced.`status` = %s
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s
			LIMIT %s,20""")

		get_data = (organisation_id,final_submission_status,exchange_status,start_date,end_date,offset)
		cursor.execute(get_query,get_data)

		print(cursor._last_executed)

		customer_exchange_data = cursor.fetchall()

		for key,data in enumerate(customer_exchange_data):

			if data['final_submission_status'] == 1 and data['status'] == 0:
				customer_exchange_data[key]['exchange_status'] = 'active'
			if data['final_submission_status'] == 1 and data['status'] == 1:
				customer_exchange_data[key]['exchange_status'] = 'complete'
			if data['final_submission_status'] == 0 and data['status'] == 0:
				customer_exchange_data[key]['exchange_status'] = 'incomplete'
			#customer_exchange_data[key]['exchange_id'] = "AMEXCHANGE-"+str(data['exchange_id'])
			customer_exchange_data[key]['last_update_ts'] = str(data['last_update_ts'])

		get_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = %s 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s""")

		get_data_count = (organisation_id,final_submission_status,start_date,end_date)
		cursor.execute(get_query_count,get_data_count)

		customer_exchange_data_count = cursor.fetchone()

		page_count = math.trunc(customer_exchange_data_count['exchange_count']/20)

		if page_count == 0:
			page_count =1
		else:
			page_count = page_count + 1	
				
		return ({"attributes": {
		    		"status_desc": "customer_exchange_data",
		    		"status": "success",
		    		"page_count":page_count,
		    		"page":page
		    	},
		    	"responseList":customer_exchange_data}), status.HTTP_200_OK

#----------------------Customer-Exchange---------------------#


#----------------------Customer-Exchange---------------------#

@name_space.route("/getCustomerExchangeWithOutPagination/<int:organisation_id>")	
class getCustomerExchangeWithOutPagination(Resource):
	def get(self,organisation_id):	

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT ced.`exchange_id`,ced.`amount`,ced.`front_image`,ced.`back_image`,ced.`device_model`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts`,a.`first_name`,a.`last_name`,ced.`status`,a.`admin_id` as `user_id`,a.`phoneno`,ced.`final_submission_status`,ced.`Is_clone`
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 ORDER BY ced.`exchange_id` DESC LIMIT 10 """)

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		print(cursor._last_executed)

		customer_exchange_data = cursor.fetchall()

		for key,data in enumerate(customer_exchange_data):
			#customer_exchange_data[key]['exchange_id'] = "AMEXCHANGE-"+str(data['exchange_id'])
			customer_exchange_data[key]['last_update_ts'] = str(data['last_update_ts'])		
				
		return ({"attributes": {
		    		"status_desc": "customer_exchange_data",
		    		"status": "success"	
		    	},
		    	"responseList":customer_exchange_data}), status.HTTP_200_OK

#----------------------Customer-Exchange---------------------#

#---------------------------Exchange-Count-Details-By-Date-Organisation-Id--------------------------#
@name_space.route("/ExhcnageCountDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class OfferCountDetailsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if filterkey == 'today':
			
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			print(today_date)

			get_active_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) = %s """)

			get_data = (organisation_id,today_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) = %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 0 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) = %s """)

			cursor.execute(get_incolplete_exchange_query_count,get_data)
			exchange_incomplete_data = cursor.fetchone()

			incomplete_count = exchange_incomplete_data['exchange_count']

		if filterkey == 'yesterday':
			
			today = date.today()

			yesterday = today - timedelta(days = 1)

			print(yesterday)

			get_active_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) = %s """)

			get_data = (organisation_id,yesterday)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) = %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 0 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) = %s """)

			cursor.execute(get_incolplete_exchange_query_count,get_data)
			exchange_incomplete_data = cursor.fetchone()

			incomplete_count = exchange_incomplete_data['exchange_count']

		if filterkey == 'last 7 days':
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_active_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			get_data = (organisation_id,start_date,end_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 0 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			cursor.execute(get_incolplete_exchange_query_count,get_data)
			exchange_incomplete_data = cursor.fetchone()

			incomplete_count = exchange_incomplete_data['exchange_count']

		if filterkey == 'this month':
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_active_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			get_data = (organisation_id,start_date,end_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 0 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			cursor.execute(get_incolplete_exchange_query_count,get_data)
			exchange_incomplete_data = cursor.fetchone()

			incomplete_count = exchange_incomplete_data['exchange_count']

		if filterkey == 'lifetime':
			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_active_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			get_data = (organisation_id,start_date,end_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = 0 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			cursor.execute(get_incolplete_exchange_query_count,get_data)
			exchange_incomplete_data = cursor.fetchone()

			incomplete_count = exchange_incomplete_data['exchange_count']


		return ({"attributes": {
		    		"status_desc": "Exchange Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{
		    					 "complete_exchange":complete_count,
		    					 "active_exchange": active_count,
		    					 "imcomplete_exchange":incomplete_count
						    	}
						    	}), status.HTTP_200_OK

#---------------------------Exchange-Count-Details-By-Date-Organisation-Id--------------------------#

#-----------------------------Customer-Exchange-Search-----------------------#
@name_space.route("/CustomerExchangeSearch/<string:searchkey>/<int:organisation_id>/<int:page>")	
class CustomerSearchingByPhoneNoOrName(Resource):
	def get(self,searchkey,organisation_id,page):
		connection = mysql_connection()
		cursor = connection.cursor()

		if page == 1:
			offset = 0
		else:
			offset = (page-1) * 20

		get_customer_exchange_query = ("""SELECT ced.`exchange_id`,ced.`amount`,ced.`front_image`,ced.`back_image`,ced.`device_model`,ced.`last_update_ts`,a.`first_name`,a.`last_name`,ced.`status`,a.`admin_id` as `user_id`,a.`phoneno`,ced.`final_submission_status`,ced.`organisation_id`
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s 
			and (a.`first_name` LIKE %s or a.`last_name` LIKE %s or ced.`exchange_id` LIKE %s or a.`phoneno` LIKE %s or ced.`device_model` LIKE %s) LIMIT %s,20
			""")
		get_customer_exchange_data = (organisation_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%",offset)

		cursor.execute(get_customer_exchange_query,get_customer_exchange_data)
		print(cursor._last_executed)

		customer_exchange_data = cursor.fetchall()

		for key,data in enumerate(customer_exchange_data):
			#customer_exchange_data[key]['exchange_id'] = "AMEXCHANGE-"+str(data['exchange_id'])
			customer_exchange_data[key]['last_update_ts'] = str(data['last_update_ts'])		

		get_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s 
			and (a.`first_name` LIKE %s or a.`last_name` LIKE %s or ced.`exchange_id` LIKE %s or a.`phoneno` LIKE %s or ced.`device_model` LIKE %s)""")

		get_data_count = (organisation_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%")
		cursor.execute(get_query_count,get_data_count)

		customer_exchange_data_count = cursor.fetchone()

		page_count = math.trunc(customer_exchange_data_count['exchange_count']/20)

		if page_count == 0:
			page_count =1
		else:
			page_count = page_count + 1	
				
		return ({"attributes": {
		    		"status_desc": "customer_exchange_data",
		    		"status": "success",
		    		"page_count":page_count,
		    		"page":page	
		    	},
		    	"responseList":customer_exchange_data}), status.HTTP_200_OK


#-----------------------------Customer-Exchange-Search-----------------------#

#----------------------Update-Customer-Exchange-Status---------------------#	
@name_space.route("/UpdateCustomerExchangeStatus/<int:exchange_id>")	
class UpdateCustomerExchangeStatus(Resource):
	@api.expect(customer_exchange_putmodel)
	def put(self,exchange_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "status" in details:
			customerexchangestatus = details['status']	

			now = datetime.now()
			date_of_closer = now.strftime("%Y-%m-%d %H:%M:%S")

			update_query = ("""UPDATE `customer_exchange_device` SET `status` = %s,`date_of_closer` = %s
					WHERE `exchange_id` = %s""")
			update_data = (customerexchangestatus,date_of_closer,exchange_id)
			cursor.execute(update_query,update_data)

		if details and "Is_clone" in details:
			Is_clone = details['Is_clone']			
			update_query = ("""UPDATE `customer_exchange_device` SET `Is_clone` = %s
					WHERE `exchange_id` = %s""")
			update_data = (Is_clone,exchange_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update_Customer_Exchange",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Customer-Exchange-Status---------------------#	

#----------------------Add-Exchange-Device-Comments---------------------#

@name_space.route("/AddExchangeDeviveCommetns")
class AddExchangeDeviveCommetns(Resource):
	@api.expect(exchange_device_comments_postmodel)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		text = details['text']
		image = details['image']
		organisation_id = details['organisation_id']
		exchange_id =  details['exchange_id']

		insert_query = ("""INSERT INTO `exchange_device_comments`(`exchange_id`,`text`,`image`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")
		data = (exchange_id,text,image,organisation_id,organisation_id)
		cursor.execute(insert_query,data)

		exchange_device_comments_id = cursor.lastrowid
		details['exchange_device_comments_id'] = exchange_device_comments_id

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_story_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Add-Exchange-Device-Comments---------------------#

#----------------------Customer-Enquiery---------------------#

@name_space.route("/getCustomerEnquieryWithPagination/<int:organisation_id>/<int:page>")	
class getCustomerEnquieryWithPagination(Resource):
	def get(self,organisation_id,page):
		if page == 1:
			offset = 0
		else:
			offset = page * 20

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT ce.`phoneno`,ce.`name`,ce.`address`,a.`first_name`,a.`last_name`,a.`admin_id` as `user_id`,ce.`email`,ce.`comment`,ce.`last_update_ts`
			FROM `customer_enquiry` ce
			INNER JOIN `admins` a ON a.`admin_id` = ce.`customer_id` 
			WHERE ce.`organisation_id` = %s LIMIT %s,20""")

		get_data = (organisation_id,offset)
		cursor.execute(get_query,get_data)

		customer_enquiery_data = cursor.fetchall()

		for key,data in enumerate(customer_enquiery_data):
			customer_enquiery_data[key]['last_update_ts'] = str(data['last_update_ts'])

		get_query_count = ("""SELECT count(*) as count_enquiery
			FROM `customer_enquiry` WHERE `organisation_id` = %s""")

		get_data_count = (organisation_id)
		cursor.execute(get_query_count,get_data_count)

		customer_enquiery_data_count = cursor.fetchone()

		page_count = math.trunc(customer_enquiery_data_count['count_enquiery']/20)

		if page_count == 0:
			page_count =1
		else:
			page_count = page_count + 1	
				
		return ({"attributes": {
		    		"status_desc": "customer_exchange_data",
		    		"status": "success",
		    		"page_count":page_count,
		    		"page":page
		    	},
		    	"responseList":customer_enquiery_data}), status.HTTP_200_OK

#----------------------Customer-Enquiery---------------------#

#----------------------Search-Order-History---------------------#

@name_space.route("/searchorderHistory/<string:searchkey>/<int:organisation_id>/<int:page>")	
class searchorderHistory(Resource):
	def get(self,searchkey,organisation_id,page):
		connection = mysql_connection()
		cursor = connection.cursor()

		if page == 1:
			offset = 0
		else:
			offset = page * 20

		get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`, ipr.`delivery_option`,ipr.`order_payment_status`,ipr.`last_update_ts`,
			a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			WHERE  ipr.`organisation_id` = %s and ( ipr.`transaction_id` LIKE %s or a.`first_name` LIKE %s or a.`phoneno` LIKE %s or a.`last_name` LIKE %s or ipr.`delivery_option` LIKE %s or `order_payment_status` LIKE %s) LIMIT %s,20""")

		get_data = (organisation_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%",offset)
		cursor.execute(get_query,get_data)

		order_data = cursor.fetchall()

		#print(order_data)

		for key,data in enumerate(order_data):
			product_status = "o"
			customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
					pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
					FROM `order_product` op
					INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
					INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
					INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
					where op.`transaction_id` = %s and cpm.`product_status` = %s""")	

			customer_product_data = (data['transaction_id'],product_status)
			cursor.execute(customer_product_query,customer_product_data)

			customer_product = cursor.fetchall()

			print(customer_product)

			for tkey,tdata in enumerate(customer_product):			
				get_product_meta_image_quey = ("""SELECT `image` as `product_image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
				product_meta_image_data = (tdata['product_meta_id'])
				rows_count_image = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
				if rows_count_image > 0:
					product_meta_image = cursor.fetchone()
					customer_product[tkey]['product_image'] = product_meta_image['product_image']
				else:
					customer_product[tkey]['product_image'] = ""

				if 	tdata['meta_key_text'] :
					a_string = tdata['meta_key_text']
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

						customer_product[tkey]['met_key_value'] = met_key

			order_data[key]['customer_product'] = customer_product
			order_data[key]['last_update_ts'] = str(data['last_update_ts'])

		get_query_count = ("""SELECT count(*) as order_count
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			WHERE  ipr.`organisation_id` = %s and ( ipr.`transaction_id` LIKE %s or a.`first_name` LIKE %s or a.`phoneno` LIKE %s or a.`last_name` LIKE %s or ipr.`delivery_option` LIKE %s or `order_payment_status` LIKE %s)""")

		get_data_count = (organisation_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%")
		cursor.execute(get_query_count,get_data_count)

		customer_order_count = cursor.fetchone()

		page_count = math.trunc(customer_order_count['order_count']/20)

		if page_count == 0:
			page_count =1
		else:
			page_count = page_count + 1	

		return ({"attributes": {
					"status_desc": "order_history",
					"status": "success",
					"page":page,
					"page_count":page_count
				},
					"responseList":order_data}), status.HTTP_200_OK


#----------------------Search-Order-History---------------------#

#----------------------Change-Order-Payment-Status---------------------#

@name_space.route("/UpdateOrderPaymentStatus/<int:transaction_id>")
class UpdateOrderPaymentStatus(Resource):
	@api.expect(changeorderpaymentstatus_putmodel)
	def put(self,transaction_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()
		order_payment_status = details['order_payment_status']

		update_query = ("""UPDATE `instamojo_payment_request` SET `order_payment_status` = %s
				WHERE `transaction_id` = %s """)
		update_data = (order_payment_status,transaction_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Order Payment Status",
								"status": "success",
								"message":"Update successfully"
									},
				"responseList":details}), status.HTTP_200_OK


#----------------------Change-Order-Payment-Status---------------------#

#----------------------Category-List---------------------#

@name_space.route("/getCategoryList/<int:organisation_id>")	
class getCategoryList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query = ("""SELECT mkm.*
				FROM `category`	C			
				INNER JOIN `meta_key_master` mkm ON mkm.`meta_key_id` = c.`category_id`
				WHERE c.`organisation_id` = %s""")		

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		customer_category_data = cursor.fetchall()

		for key,data in enumerate(customer_category_data):			
			customer_category_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "customer_exchange_data",
		    		"status": "success"
		    	},
		    	"responseList":customer_category_data}), status.HTTP_200_OK

#----------------------Category-List---------------------#

#--------------------Customer-List-With-Organisation-And-Retailer-Store-------------------------#

@name_space.route("/CustomerListWithOrganisationAndRetailStore/<string:filterkey>/<string:list_type>/<int:retailer_store_store_id>/<int:organisation_id>")	
class CustomerListWithOrganisationAndRetailStore(Resource):
	def get(self,filterkey,list_type,retailer_store_store_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = ecommerce_analytics()
		cur = conn.cursor()

		if list_type == 'registation_data':			

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s """)
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,today_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []
				

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s """)
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,yesterday) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
			
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []		

		if list_type == 'notification_data':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_notify_customer_query = ("""SELECT distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `app_notification` an
					INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
					WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) = %s and  ur.`retailer_store_id` = %s and an.`destination_type` = 2
					and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,today_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)
				
				get_notify_customer_query = ("""SELECT  distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `app_notification` an
					INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
					WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) = %s and  ur.`retailer_store_id` = %s and an.`destination_type` = 2
					and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,yesterday,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2 and
						a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		if list_type == 'email_data':
			if filterkey == 'today':
				print('hi')
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_notify_customer_query = ("""SELECT distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `customer_email` an
					INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
					WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) = %s and  ur.`retailer_store_id` = %s and an.`destination_type` = 2
					and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,today_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)
				
				get_notify_customer_query = ("""SELECT  distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `customer_email` an
					INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
					WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) = %s and  ur.`retailer_store_id` = %s and an.`destination_type` = 2
					and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,yesterday,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2 and
						a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		if list_type == 'loggedin_data':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (today_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (yesterday,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0
			'''if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					`loggedin_status`=1 and date(`date_of_lastlogin`)=%s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,today_date,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					a.`loggedin_status`=1 and date(a.`date_of_lastlogin`)=%s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,yesterday,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					a.`loggedin_status`=1 and date(a.`date_of_lastlogin`) >= %s and date(a.`date_of_lastlogin`) <= %s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					a.`loggedin_status`=1 and date(a.`date_of_lastlogin`) >= %s and date(a.`date_of_lastlogin`) <= %s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					a.`loggedin_status`=1 and date(a.`date_of_lastlogin`) >= %s and date(a.`date_of_lastlogin`) <= %s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []'''

		if list_type == 'demo_data':

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) = %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,today_date)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) = %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,yesterday)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	
				print(cursor._last_executed)

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,start_date,end_date)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	
				print(cursor._last_executed)

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []	

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,start_date,end_date)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	
				print(cursor._last_executed)

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []	

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,start_date,end_date)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	
				print(cursor._last_executed)

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		if list_type == 'total_login_user_from_registration_data':			

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s and a.`loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,today_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []
				

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s and `loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,yesterday) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
			
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		if list_type == 'total_never_login_user_from_registration_data':			

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s and a.`loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,today_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []
				

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s and `loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,yesterday) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
			
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		return ({"attributes": {
		    		"status_desc": "Customer Details",
		    		"status": "success"
		    	},
		    	"responseList":customer_data }), status.HTTP_200_OK


#--------------------Customer-List-With-Organisation-And-Retailer-Store-------------------------#


#--------------------Customer-List-With-Organisation-And-Retailer-Store-with-Date-Range-------------------------#

@name_space.route("/CustomerListWithOrganisationAndRetailStoreWithDateRange/<string:filterkey>/<string:list_type>/<int:retailer_store_store_id>/<int:organisation_id>/<string:start_date>/<string:end_date>")	
class CustomerListWithOrganisationAndRetailStoreWithDateRange(Resource):
	def get(self,filterkey,list_type,retailer_store_store_id,organisation_id,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = ecommerce_analytics()
		cur = conn.cursor()

		if list_type == 'registation_data':			

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s """)
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,today_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []
				

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s """)
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,yesterday) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
			
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'custom date':			
				
				end_date = end_date
				
				start_date = start_date

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []		

		if list_type == 'notification_data':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_notify_customer_query = ("""SELECT distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `app_notification` an
					INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
					WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) = %s and  ur.`retailer_store_id` = %s and an.`destination_type` = 2
					and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,today_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)
				
				get_notify_customer_query = ("""SELECT  distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `app_notification` an
					INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
					WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) = %s and  ur.`retailer_store_id` = %s and an.`destination_type` = 2
					and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,yesterday,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2 and
						a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'custom date':				
				end_date = end_date				
				start_date = start_date

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`U_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `app_notification` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`U_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`U_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and an.`destination_type` = 2
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		if list_type == 'email_data':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_notify_customer_query = ("""SELECT distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `customer_email` an
					INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
					WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) = %s and  ur.`retailer_store_id` = %s
					and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,today_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)
				
				get_notify_customer_query = ("""SELECT  distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
					FROM `customer_email` an
					INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
					WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) = %s and  ur.`retailer_store_id` = %s
					and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,yesterday,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `customer_email` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `customer_email` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `customer_email` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s and
						a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'custom date':				
				end_date = end_date				
				start_date = start_date

				print(start_date)
				print(end_date)
					
				get_notify_customer_query = ("""SELECT  distinct (an.`customer_id`) as admin_id,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation`
						FROM `customer_email` an
						INNER JOIN `admins` a ON a.`admin_id` = an.`customer_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = an.`customer_id`
						WHERE an.`organisation_id`=%s and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s and ur.`retailer_store_id` = %s
						and a.`organisation_id` = %s and a.`status` = 1""")
				get_notify_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)

				count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

				if count_notify_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		if list_type == 'loggedin_data':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (today_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (yesterday,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'custom date':				
				end_date = end_date				
				start_date = start_date

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`wallet`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])
							customer_data[fkey]['wallet'] = user_data['wallet']

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0	
			'''if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					`loggedin_status`=1 and date(`date_of_lastlogin`)=%s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,today_date,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					a.`loggedin_status`=1 and date(a.`date_of_lastlogin`)=%s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,yesterday,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					a.`loggedin_status`=1 and date(a.`date_of_lastlogin`) >= %s and date(a.`date_of_lastlogin`) <= %s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					a.`loggedin_status`=1 and date(a.`date_of_lastlogin`) >= %s and date(a.`date_of_lastlogin`) <= %s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` 
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
					a.`loggedin_status`=1 and date(a.`date_of_lastlogin`) >= %s and date(a.`date_of_lastlogin`) <= %s and ur.`retailer_store_id` = %s and ur.`organisation_id` = %s""")
				get_loged_In_customer_data = (organisation_id,start_date,end_date,retailer_store_store_id,organisation_id)
				count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

				if count_loged_In_customer_data > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []'''

		if list_type == 'demo_data':

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) = %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,today_date)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) = %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,yesterday)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	
				print(cursor._last_executed)

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,start_date,end_date)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	
				print(cursor._last_executed)

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []	

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,start_date,end_date)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	
				print(cursor._last_executed)

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []	

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,start_date,end_date)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	
				print(cursor._last_executed)

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'custom date':				
				end_date = end_date				
				start_date = start_date

				print(start_date)
				print(end_date)

				get_demo_given_customer_query = ("""SELECT distinct cr.`customer_id` as `admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
						name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
						a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `customer_remarks` cr
					INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`customer_id`!=0 and cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")		
				get_demo_given_customer_data = (organisation_id,organisation_id,retailer_store_store_id,start_date,end_date)
				count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	
				print(cursor._last_executed)

				if count_demo_given_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		if list_type == 'total_login_user_from_registration_data':			

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s and a.`loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,today_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []
				

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s and `loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,yesterday) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
			
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'custom date':
			
				
				end_date = end_date
				
				start_date = start_date

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 1""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		if list_type == 'total_never_login_user_from_registration_data':			

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				
				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s and a.`loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,today_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []
				

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) = %s and `loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,yesterday) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'last 7 days':
			
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'this month':
				
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'lifetime':
				
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

			if filterkey == 'custom date':
			
				
				end_date = end_date
				
				start_date = start_date

				print(start_date)
				print(end_date)

				get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
					name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
					a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
					FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and `role_id`=4 and ur.`retailer_store_id` = %s and a.`organisation_id` = %s
					and a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
				get_registerd_customer_data = (organisation_id,retailer_store_store_id,organisation_id,start_date,end_date) 

				count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

				if count_registerd_customer > 0:
					customer_data = cursor.fetchall()
					for key,data in enumerate(customer_data):
						customer_data[key]['date_of_creation'] = str(data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['admin_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0
				else:
					customer_data = []

		return ({"attributes": {
		    		"status_desc": "Customer Details",
		    		"status": "success"
		    	},
		    	"responseList":customer_data }), status.HTTP_200_OK



#----------------------Update-Product-Out-Price---------------------#

@name_space.route("/UpdateProductOutPrice/<int:product_meta_id>/<organisation_id>")
class UpdateProductOutPrice(Resource):
	@api.expect(productoutprice_putmodel)
	def put(self,product_meta_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()
		
		if details and "out_price" in details:
			out_price = details['out_price']
			get_product_by_product_meta_id_query = ("""SELECT *				
										FROM `product_meta`						
										WHERE `product_meta_id` = %s""")
			get_product_by_product_meta_id_data = (product_meta_id)
			cursor.execute(get_product_by_product_meta_id_query,get_product_by_product_meta_id_data)
			product_data = cursor.fetchone()

			get_product_out_price_query = ("""SELECT *				
										FROM `product_meta_out_price`						
										WHERE `organisation_id` = %s and `product_meta_id` = %s""")
			get_product_out_price_data = (organisation_id,product_meta_id)
			count_product_out_price = cursor.execute(get_product_out_price_query,get_product_out_price_data)

			if count_product_out_price > 0:									
				update_query = ("""UPDATE `product_meta_out_price` SET `out_price` = %s
							WHERE `organisation_id` = %s and `product_meta_id` = %s""")
				update_data = (out_price,organisation_id,product_meta_id)
				cursor.execute(update_query,update_data)
			else:
				if details and "out_price_status" in details:
					out_price_status = details['out_price_status']
				else:
					out_price_status = 1
				insert_query = ("""INSERT INTO `product_meta_out_price`(`product_meta_id`,`product_id`,`out_price`,`status`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s,%s)""")
				data = (product_meta_id,product_data['product_id'],out_price,out_price_status,organisation_id,organisation_id)
				cursor.execute(insert_query,data)

		if details and "out_price_status" in details:
			out_price_status = details['out_price_status']
			update_query = ("""UPDATE `product_meta_out_price` SET `status` = %s
							WHERE `organisation_id` = %s and `product_meta_id` = %s""")
			update_data = (out_price_status,organisation_id,product_meta_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Product Out Price",
								"status": "success",
								"message":"Update successfully"
									},
				"responseList":details}), status.HTTP_200_OK


#----------------------Update-Product-Out-Price---------------------#

#----------------------Update-Product-Out-Price---------------------#

@name_space.route("/UpdateProductSubCategoryAndSection/<int:product_meta_id>/<organisation_id>")
class UpdateProductSubCategoryAndSection(Resource):
	@api.expect(product_sub_category_section_putmodel)
	def put(self,product_meta_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()
		get_product_by_product_meta_id_query = ("""SELECT *				
										FROM `product_meta`						
										WHERE `product_meta_id` = %s""")
		get_product_by_product_meta_id_data = (product_meta_id)
		cursor.execute(get_product_by_product_meta_id_query,get_product_by_product_meta_id_data)
		product_data = cursor.fetchone()
		
		if details and "sub_category_id" in details:
			sub_category_id = details['sub_category_id']			

			get_product_sub_category_query = ("""SELECT *				
										FROM `product_sub_category_mapping`						
										WHERE `organisation_id` = %s and `product_id` = %s""")
			get_product_sub_category_data = (organisation_id,product_data['product_id'])
			count_product_sub_category = cursor.execute(get_product_sub_category_query,get_product_sub_category_data)

			if count_product_sub_category > 0:									
				update_query = ("""UPDATE `product_sub_category_mapping` SET `sub_category_id` = %s
							WHERE `organisation_id` = %s and `product_id` = %s""")
				update_data = (sub_category_id,organisation_id,product_data['product_id'])
				cursor.execute(update_query,update_data)
			else:			
				sub_category_status = 1
				insert_query = ("""INSERT INTO `product_sub_category_mapping`(`product_id`,`sub_category_id`,`status`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s)""")
				data = (product_data['product_id'],sub_category_id,sub_category_status,organisation_id,organisation_id)
				cursor.execute(insert_query,data)

		if details and "section_id" in details:
			section_id = details['section_id']
			get_product_section_query = ("""SELECT *				
										FROM `product_section_mapping`						
										WHERE `organisation_id` = %s and `product_id` = %s""")
			get_product_section_data = (organisation_id,product_data['product_id'])
			count_product_section = cursor.execute(get_product_section_query,get_product_section_data)

			if count_product_section > 0:									
				update_query = ("""UPDATE `product_section_mapping` SET `section_id` = %s
							WHERE `organisation_id` = %s and `product_id` = %s""")
				update_data = (section_id,organisation_id,product_data['product_id'])
				cursor.execute(update_query,update_data)
			else:			
				section_status = 1
				insert_query = ("""INSERT INTO `product_section_mapping`(`product_id`,`section_id`,`status`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s)""")
				data = (product_data['product_id'],section_id,section_status,organisation_id,organisation_id)
				cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Product Section and Category",
								"status": "success",
								"message":"Update successfully"
									},
				"responseList":details}), status.HTTP_200_OK


#----------------------Update-Product-Out-Price---------------------#


#--------------------Customer-List-With-Organisation-And-Retailer-Store-with-Date-Range-------------------------#

@name_space.route("/createCatalougePdf")
class createCatalougePdf(Resource):
	@api.expect(create_catalouge_pdf)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		catalog_id = details['catalog_id']
		data = {}

		get_catalouge_query = ("""SELECT c.*,om.`logo`
				FROM `catalogs` c 
				INNER JOIN `organisation_master` om ON om.`organisation_id` = c.`organisation_id`
				WHERE  `catalog_id` = %s""")
		getCatalougeData = (catalog_id)
		countCatalouge = cursor.execute(get_catalouge_query,getCatalougeData)

		if countCatalouge > 0:		
			catalouge_data = cursor.fetchone()
			data['catalouge_data'] = catalouge_data
		else:
			data['catalouge_data'] = {}

		get_product_query = ("""SELECT p.`product_name`,p.`product_id` 
				FROM `product_catalog_mapping` pcm				
				INNER JOIN `product` p ON p.`product_id` = pcm.`product_id`
				WHERE pcm.`catalog_id` = %s""")
		get_product_data = 	(catalog_id)
		cout_product  = cursor.execute(get_product_query,get_product_data)

		if cout_product > 0:
			catalouge_product = cursor.fetchall()
			for tkey,tdata in enumerate(catalouge_product):
				get_product_meta_query = (""" SELECT pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
												FROM `product_meta` pm WHERE `product_id` = %s""")
				get_product_meta_data = (tdata['product_id'])
				cout_product_meta = cursor.execute(get_product_meta_query,get_product_meta_data)
				if cout_product_meta > 0:
					product_meta = cursor.fetchall()					

					for pmkey,pmdata in enumerate(product_meta):
						get_product_meta_image_quey = ("""SELECT `image` as `product_image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s order by default_image_flag desc""")
						product_meta_image_data = (pmdata['product_meta_id'])
						rows_count_image = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
						if rows_count_image > 0:
							product_meta_image = cursor.fetchone()
							product_meta[pmkey]['product_image'] = product_meta_image['product_image']
						else:
							product_meta[pmkey]['product_image'] = ""

						if pmdata['meta_key_text'] :	
								a_string = pmdata['meta_key_text']
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

									product_meta[pmkey]['met_key_value'] = met_key

						catalouge_product[tkey]['product_meta'] = product_meta
				else:
					catalouge_product[tkey]['product_meta'] = []
				
			data['catalouge_product_data'] = catalouge_product
		else:
			data['catalouge_product_data'] = []

		#print(data)	
		#catalougePdf(data)

		abs_html_path = catalougePdf(data)

		uploadURL = BASE_URL + 'aws_portal_upload/awsResourceUploadController/uploadToS3Bucket/{}'.format(catalog_id)
		headers = {"content-type": "multipart/form-data"}

		files = {}

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		file_name = "catalouge-"+str(catalog_id)+date_of_creation+".html"
		 
		files['file'] = (file_name, abs_html_path)
		
		uploadRes = requests.post(uploadURL,files=files).json()
		responselist = json.dumps(uploadRes['responseList'][0])
		s2 = json.loads(responselist)

		pdf_link = s2['FilePath']

		pdf_web_link = "http://techdrive.xyz/ecommerce-app/catalog.php?catalog_id="+str(catalog_id)

		update_query = ("""UPDATE `catalogs` SET `pdf_link` = %s,`pdf_web_link` = %s
				WHERE `catalog_id` = %s """)
		update_data = (pdf_link,pdf_web_link,catalog_id)
		cursor.execute(update_query,update_data)

		get_catalouge_query = ("""SELECT c.*,om.`logo`
					FROM `catalogs` c 
					INNER JOIN `organisation_master` om ON om.`organisation_id` = c.`organisation_id`
					WHERE  `catalog_id` = %s""")
		getCatalougeData = (catalog_id)
		countCatalouge = cursor.execute(get_catalouge_query,getCatalougeData)

		if countCatalouge > 0:		
			catalouge_data = cursor.fetchone()	
			catalouge_data['last_update_ts'] = 	str(catalouge_data['last_update_ts'])
		else:
			catalouge_data = {}

		return ({"attributes": {"status_desc": "Catalouge Data",
									"status": "success"},
					"responseList": catalouge_data}), status.HTTP_200_OK	
	

#--------------------Share-Catalouge-Offer-Web-App-------------------------#

@name_space.route("/ecommerceShare")
class ecommerceShare(Resource):
	@api.expect(ecommerce_share_model)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		source_type = details['source_type']
		source_id = details['source_id']
		organisation_id = details['organisation_id']
		is_share = 1
		last_update_id = details['organisation_id']

		insert_query = ("""INSERT INTO `ecommerce_share`(`source_type`,`source_id`,`is_share`,`organisation_id`) 
									VALUES(%s,%s,%s,%s)""")
		data = (source_type,source_id,is_share,organisation_id)
		cursor.execute(insert_query,data)

		return ({"attributes": {"status_desc": "Ecommerce Share",
									"status": "success"},
					"responseList": details}), status.HTTP_200_OK	


#--------------------Share-Catalouge-Offer-Web-App-------------------------#

#--------------------miss-opportunity-------------------------#

@name_space.route("/ecommerceMissOpportunity")
class ecommerceMissOpportunity(Resource):
	@api.expect(ecommerce_missopportunity_model)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		customer_id = details['customer_id']		
		missopprtunity_product_name = details['missopprtunity_product_name']
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']
		retailer_store_store_id = details['retailer_store_store_id']

		if details and "name_of_customer" in details:
			name_of_customer = details['name_of_customer']
		else:
			name_of_customer = ""

		if details and "mobile_no" in details:
			mobile_no = details['mobile_no']
		else:
			mobile_no = ""

		if details and "email_id" in details:
			email_id = details['email_id']
		else:
			email_id = ""

		if details and "demo_given_by" in details:
			demo_given_by = details['demo_given_by']
		else:
			demo_given_by = ""

		if details and "reason_for_non_closure" in details:
			reason_for_non_closure = details['reason_for_non_closure']
		else:
			reason_for_non_closure = ""

		if details and "follow_up_1" in details:
			follow_up_1 = details['follow_up_1']
		else:
			follow_up_1 = ""

		if details and "follow_up_2" in details:
			follow_up_2 = details['follow_up_2']
		else:
			follow_up_2 = ""

		if details and "remarks" in details:
			remarks = details['remarks']
		else:
			remarks = ""

		if details and "whatsapp_no" in details:
			whatsapp_no = details['whatsapp_no']
		else:
			whatsapp_no = ""

		if details and "name_by_whom_captued_data" in details:
			name_by_whom_captued_data = details['name_by_whom_captued_data']
		else:
			name_by_whom_captued_data = ""

		if details and "missed_opportunity_date" in details:
			missed_opportunity_date = details['missed_opportunity_date']
		else:
			missed_opportunity_date = ""

		if details and "followup_date" in details:
			followup_date = details['followup_date']
		else:
			followup_date = ""

		if details and "follow_up_2_date" in details:
			follow_up_2_date = details['follow_up_2_date']
		else:
			follow_up_2_date = ""

		

		insert_query = ("""INSERT INTO `miss_opportunity`(`customer_id`,`name_of_customer`,`mobile_no`,`email_id`,`demo_given_by`,`reason_for_non_closure`,`follow_up_1`,`follow_up_2`,`remarks`,`missopprtunity_product_name`,`whatsapp_no`,`name_by_whom_captued_data`,`missed_opportunity_date`,`followup_date`,`follow_up_2_date`,`retailer_store_store_id`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		data = (customer_id,name_of_customer,mobile_no,email_id,demo_given_by,reason_for_non_closure,follow_up_1,follow_up_2,remarks,missopprtunity_product_name,whatsapp_no,name_by_whom_captued_data,missed_opportunity_date,followup_date,follow_up_2_date,retailer_store_store_id,organisation_id,last_update_id)
		cursor.execute(insert_query,data)

		return ({"attributes": {"status_desc": "Ecommerce Miss Opportunity",
									"status": "success"},
					"responseList": details}), status.HTTP_200_OK	


#--------------------miss-opportunity-------------------------#

#--------------------miss-opportunity-Mapping-------------------------#

@name_space.route("/ecommerceMissOpportunityMapping")
class ecommerceMissOpportunityMapping(Resource):
	@api.expect(ecommerce_missopportunity_mapping_model)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		customer_id = details['customer_id']	
		missopprtunity_product_name = details['missopprtunity_product_name']	
		product_id = details['product_id']
		product_meta_id = details['product_meta_id']
		retailer_store_store_id = details['retailer_store_store_id']
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']

		if details and "name_of_customer" in details:
			name_of_customer = details['name_of_customer']
		else:
			name_of_customer = ""

		if details and "mobile_no" in details:
			mobile_no = details['mobile_no']
		else:
			mobile_no = ""

		if details and "email_id" in details:
			email_id = details['email_id']
		else:
			email_id = ""

		if details and "demo_given_by" in details:
			demo_given_by = details['demo_given_by']
		else:
			demo_given_by = ""

		if details and "reason_for_non_closure" in details:
			reason_for_non_closure = details['reason_for_non_closure']
		else:
			reason_for_non_closure = ""

		if details and "follow_up_1" in details:
			follow_up_1 = details['follow_up_1']
		else:
			follow_up_1 = ""

		if details and "follow_up_2" in details:
			follow_up_2 = details['follow_up_2']
		else:
			follow_up_2 = ""

		if details and "remarks" in details:
			remarks = details['remarks']
		else:
			remarks = ""

		get_query = ("""SELECT *
								FROM `miss_opportunity` WHERE  `organisation_id` = %s and `retailer_store_store_id` = %s and `missopprtunity_product_name` = %s and `customer_id` = %s""")
		get_data = (organisation_id,retailer_store_store_id,missopprtunity_product_name,customer_id)
		count_data = cursor.execute(get_query,get_data)

		if count_data > 0:
			update_query = ("""UPDATE `miss_opportunity` SET `product_id` = %s,`product_meta_id` = %s ,`name_of_customer` = %s,`mobile_no` = %s,`email_id` = %s,`demo_given_by` = %s,`reason_for_non_closure` = %s,`follow_up_1` = %s,`follow_up_2` = %s,`remarks` = %s
				WHERE  `organisation_id` = %s and `retailer_store_store_id` = %s and `missopprtunity_product_name` = %s and `customer_id` = %s""")
			update_data = (product_id,product_meta_id,name_of_customer,mobile_no,email_id,demo_given_by,reason_for_non_closure,follow_up_1,remarks,organisation_id,retailer_store_store_id,missopprtunity_product_name,customer_id)
			cursor.execute(update_query,update_data)

		else:

			insert_query = ("""INSERT INTO `miss_opportunity`(`customer_id`,`name_of_customer`,`mobile_no`,`email_id`,`demo_given_by`,`reason_for_non_closure`,`follow_up_1`,`follow_up_2`,`remarks`,`product_id`,`product_meta_id`,`retailer_store_store_id`,`organisation_id`,`last_update_id`) 
										VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			data = (customer_id,name_of_customer,mobile_no,email_id,demo_given_by,reason_for_non_closure,follow_up_1,follow_up_2,remarks,product_id,product_meta_id,retailer_store_store_id,organisation_id,last_update_id)
			cursor.execute(insert_query,data)

		return ({"attributes": {"status_desc": "Ecommerce Miss Opportunity",
									"status": "success"},
					"responseList": details}), status.HTTP_200_OK	


#--------------------miss-opportunity-Mapping-------------------------#

#--------------------miss-opportunity-List-------------------------#

@name_space.route("/missOpportunityList/<int:organisation_id>/<int:retailer_store_id>/<int:page>")	
class missOpportunityList(Resource):
	def get(self,organisation_id,retailer_store_id,page):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT `miss_opportunity_id`,`customer_id`,`product_id`,`product_meta_id`,`missopprtunity_product_name`,`name_of_customer`,`mobile_no`,`email_id`,`demo_given_by`,`reason_for_non_closure`,`follow_up_1`,`follow_up_2`,`remarks`,a.`first_name`,a.`phoneno`,`whatsapp_no`,`name_by_whom_captued_data`,`missed_opportunity_date`,`followup_date`,`follow_up_2_date`,`is_close`,`closure_date`
			FROM `miss_opportunity` mo 	
			INNER JOIN `admins` a ON a.`admin_id` = mo.`customer_id`		
			WHERE mo.`organisation_id` = %s and mo.`retailer_store_store_id` = %s order by `miss_opportunity_id` desc""")

		get_data = (organisation_id,retailer_store_id)
		cursor.execute(get_query,get_data)
		missopportunity_data = cursor.fetchall()

		for key,data in enumerate(missopportunity_data):
			if data['product_meta_id'] == 0:
				missopportunity_data[key]['product_name'] = ''
				missopportunity_data[key]['met_key_value'] = {}
			else:
				get_product_meta_query = ("""SELECT p.`product_name`,pm.`meta_key_text`
					FROM `product_meta` pm 		
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`	
					WHERE pm.`product_meta_id` = %s""")
				get_product_meta_data = (data['product_meta_id'])
				cursor.execute(get_product_meta_query,get_product_meta_data)
				product_meta_data = cursor.fetchone()
				missopportunity_data[key]['product_name'] = product_meta_data['product_name']

				if product_meta_data['meta_key_text'] :
					a_string = product_meta_data['meta_key_text']
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

						missopportunity_data[key]['met_key_value'] = met_key

		return ({"attributes": {
		    		"status_desc": "miss_opportunity_details",
		    		"status": "success"
		    	},
		    	"responseList":missopportunity_data}), status.HTTP_200_OK

#--------------------miss-opportunity-List-------------------------#

def catalougePdf(data):
	catalog_information = {}	
	catalog_information['catalog_name'] = data['catalouge_data']['catalog_name']
	if data['catalouge_data']['is_home_section'] == 1:
		catalog_information['is_home_section'] = "Yes"
	else:
		catalog_information['is_home_section'] = "No"

	if data['catalouge_data']['status'] == 1:
		catalog_information['status'] = 'Yes'
	else:
		catalog_information['status'] = 'No'

	catalog_information['date'] = data['catalouge_data']['last_update_ts']	
	catalog_information['logo'] = data['catalouge_data']['logo']
	catalog_information['catalouge_product_data'] = data['catalouge_product_data']
	template = env.get_template('catalouge.html')
	return template.render(catalog_information)
	#print( template.render(catalog_information))
	

@name_space.route("/ecommerceMissOpportunityUpdate")
class ecommerceMissOpportunityUpdate(Resource):
	@api.expect(ecommerce_missopportunity_model_update)
	def put(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		miss_opportunity_id = details['miss_opportunity_id']	
		missopprtunity_product_name = details['missopprtunity_product_name']

		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']
		demo_given_by = details['demo_given_by']
		reason_for_non_closure = details['reason_for_non_closure']
		follow_up_1 = details['follow_up_1']
		follow_up_2 = details['follow_up_2']
		remarks = details['remarks']
		email_id = details['email_id']

		if details and "whatsapp_no" in details:
			whatsapp_no = details['whatsapp_no']
		else:
			whatsapp_no = ""

		if details and "name_by_whom_captued_data" in details:
			name_by_whom_captued_data = details['name_by_whom_captued_data']
		else:
			name_by_whom_captued_data = ""

		if details and "missed_opportunity_date" in details:
			missed_opportunity_date = details['missed_opportunity_date']
		else:
			missed_opportunity_date = ""

		if details and "followup_date" in details:
			followup_date = details['followup_date']
		else:
			followup_date = ""

		if details and "follow_up_2_date" in details:
			follow_up_2_date = details['follow_up_2_date']
		else:
			follow_up_2_date = ""

			
		

		insert_query = ("""UPDATE `miss_opportunity` SET `demo_given_by` = %s,`reason_for_non_closure` = %s,`follow_up_1` = %s,`follow_up_2` = %s,`remarks` = %s,
			`missopprtunity_product_name` = %s,`whatsapp_no` = %s,`name_by_whom_captued_data` = %s,`missed_opportunity_date` = %s, `followup_date` = %s,`follow_up_2_date` = %s,`email_id` = %s,`last_update_id` = %s WHERE `miss_opportunity_id` = %s""")
		data = (demo_given_by,reason_for_non_closure,follow_up_1,follow_up_2,remarks,missopprtunity_product_name,whatsapp_no,name_by_whom_captued_data,missed_opportunity_date,followup_date,follow_up_2_date,email_id,last_update_id,miss_opportunity_id)
		cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Ecommerce Miss Opportunity",
									"status": "success"},
					"responseList": details}), status.HTTP_200_OK	


#--------------------miss-opportunity-------------------------#

@name_space.route("/closeMissOpportunity")
class closeMissOpportunity(Resource):
	@api.expect(close_missopportunity_model)
	def put(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		miss_opportunity_id = details['miss_opportunity_id']

		is_close = 1

		now = datetime.now()
		today_date = now.strftime("%Y-%m-%d")

		update_query = ("""UPDATE `miss_opportunity` SET `is_close` = %s,`closure_date` = %s WHERE `miss_opportunity_id` = %s""")
		data = (is_close,today_date,miss_opportunity_id)
		cursor.execute(update_query,data)


		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Ecommerce Miss Opportunity",
									"status": "success"},
					"responseList": details}), status.HTTP_200_OK

#--------------------miss-opportunity-Mapping-------------------------#

@name_space.route("/ecommerceMissOpportunityMappingV2")
class ecommerceMissOpportunityMappingV2(Resource):
	@api.expect(ecommerce_missopportunity_mapping_model_v2)
	def put(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		miss_opportunity_id = details['miss_opportunity_id']	
		product_id = details['product_id']
		product_meta_id = details['product_meta_id']
		last_update_id = details['organisation_id']

		update_query = ("""UPDATE `miss_opportunity` SET `product_id` = %s,`product_meta_id` = %s,`last_update_id` = %s WHERE `miss_opportunity_id` = %s""")
		update_data = (product_id,product_meta_id,last_update_id,miss_opportunity_id)
		cursor.execute(update_query,update_data)

		return ({"attributes": {"status_desc": "Ecommerce Miss Opportunity",
									"status": "success"},
					"responseList": details}), status.HTTP_200_OK	
