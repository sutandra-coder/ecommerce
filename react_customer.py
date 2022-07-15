import pymysql
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import secure_filename
import os
import requests
import random, string

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
react_customer = Blueprint('react_customer_api', __name__)
api = Api(react_customer,  title='React Customer API',description='React Customer API')
name_space = api.namespace('reactCustomer',description='React Customer')

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

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'


#----------------------Product-List---------------------#
@react_customer.route("/productList/<int:category_id>/<string:organisation_code>")
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def productList(category_id,organisation_code):
		connection = mysql_connection()
		cursor = connection.cursor()
		get_organisation_query = ("SELECT organisation_id from `organisation_master` where `organisation_code` = %s")
		get_organisation_data = (organisation_code)
		count_organisation = cursor.execute(get_organisation_query,get_organisation_data)
		organisation_data = cursor.fetchone()
		if count_organisation > 0:
			organisation_id = organisation_data['organisation_id']
			if category_id == 0:
				get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,mm.`meta_key`,pm.`out_price`,pm.`product_meta_id`
					FROM `product` p
					INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
					INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
					WHERE p.`status` = 1 and p.`organisation_id` = %s""")
				get_data = (organisation_id)			
			else:
				get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,pm.`out_price`,pm.`product_meta_id`
					FROM `product` p
					INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
					WHERE p.`status` = 1 and p.`organisation_id` = %s and p.`category_id` = %s""")
				get_data = (organisation_id,category_id)

			cursor.execute(get_query,get_data)
			product_data = cursor.fetchall()

			for key,data in enumerate(product_data):
				get_category_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
					FROM `product_category_mapping` pcm
					INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pcm.`category_id`
					WHERE pcm.`product_id` = %s""")
				get_category_data = (data['product_id'])
				rows_count_category = cursor.execute(get_category_query,get_category_data)

				if rows_count_category >0:
					product_category = cursor.fetchone()
					product_data[key]['category_id'] = product_category['meta_key_value_id']
					product_data[key]['category'] = product_category['meta_key_value']
				else:
					product_data[key]['category_id'] = ""
					product_data[key]['category'] = ""

				get_query_image = ("""SELECT `image`
											FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
				getdata_image = (data['product_meta_id'])
				product_image_count = cursor.execute(get_query_image,getdata_image)

				if product_image_count >0 :
					product_image = cursor.fetchone()
					product_data[key]['image'] = product_image['image']
				else:
					product_data[key]['image'] = ""

				product_data[key]['is_cart'] = False
		else:
			product_data = []

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Catalog-List---------------------#
@react_customer.route("/catalogListN/<string:organisation_code>")
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def catalogListN(organisation_code):
	connection = mysql_connection()
	cursor = connection.cursor()
	
	get_organisation_query = ("SELECT organisation_id from `organisation_master` where `organisation_code` = %s")
	get_organisation_data = (organisation_code)
	count_organisation = cursor.execute(get_organisation_query,get_organisation_data)
	organisation_data = cursor.fetchone()

	if count_organisation > 0:
		organisation_id = organisation_data['organisation_id']

		get_query = ("""SELECT c.`catalog_id`,c.`catalog_name`
					FROM `catalogs` c										
					WHERE c.`organisation_id` = %s""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_product_query = ("""SELECT count(*) as product_count 
				FROM `product_catalog_mapping` pcm 
				INNER JOIN `product` p ON p.`product_id` = pcm .`product_id`
				WHERE pcm.`catalog_id` = %s""")
	else:
			product_data = []

	return ({"attributes": {
		    	"status_desc": "product_details",
		    	"status": "success"
		    },
		    "responseList":product_data}), status.HTTP_200_OK

#----------------------Catalog-List---------------------#

#----------------------Product-List-By-Catalog-Id---------------------#

@react_customer.route("/productListByCatalogId/<int:catalog_id>")
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def productListByCatalogId(catalog_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
					p.`product_type`,p.`category_id` as `product_type_id`,pm.`product_meta_id`,pm.`product_meta_code`,pm.`out_price`,pm.`product_meta_id`,pm.`meta_key_text`
					FROM `product` p
					INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
					INNER JOIN `product_catalog_mapping` pcm ON pcm.`product_id` = p.`product_id`
					WHERE p.`status` = 1 and pcm.`catalog_id` = %s""")
		get_data = (catalog_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			#get_product_meta_query = ("""SELECT pm.`product_meta_id`,pm.`product_meta_code`,pm.`out_price`,pm.`product_meta_id`,pm.`meta_key_text`
						#FROM `product_meta` pm WHERE pm.`product_id` = %s""")
			#get_product_data = (data['product_id'])
			#product_meta_count = cursor.execute(get_product_meta_query,get_product_data)

			#if product_meta_count >0:				
			#product_meta = cursor.fetchone()

			#product_data[key]['product_meta_id'] = data['product_meta_id']
			#product_data[key]['product_meta_code'] = product_meta['product_meta_code']
			#product_data[key]['out_price'] = product_meta['out_price']				

			a_string = data['meta_key_text']
			a_list = a_string.split(',')
				
			met_key = []
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

				met_key.append({met_key_data['meta_key']:met_key_value_data['meta_key_value']})

				product_data[key]['met_key_value'] = met_key
					

			image_a = []	
			get_query_images = ("""SELECT `image`,`image_type`
							FROM `product_meta_images` WHERE `product_meta_id` = %s """)
			getdata_images = (data['product_meta_id'])
			cursor.execute(get_query_images,getdata_images)
			images = cursor.fetchall()

			for image in images:
				image_a.append({"image":image['image'],"image_type":image['image_type']})

			product_data[key]['images'] = image_a

			get_query_discount = ("""SELECT `discount`
									FROM `product_meta_discount_mapping` pdm
									INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
									WHERE `product_meta_id` = %s """)
			getdata_discount = (data['product_meta_id'])
			count_dicscount = cursor.execute(get_query_discount,getdata_discount)

			if count_dicscount > 0:
				product_meta_discount = cursor.fetchone()
				product_data[key]['discount'] = product_meta_discount['discount']

				discount = (data['out_price']/100)*product_meta_discount['discount']
				actual_amount = data['out_price'] - discount
				product_data[key]['after_discounted_price'] = round(actual_amount,2)

			else:
				product_data[key]['discount'] = 0
				product_data[key]['after_discounted_price'] = data['out_price']

			get_brand_mapping_query = ("""SELECT mm.`meta_key_value` as `brand`,  mm.`meta_key_value_id` as `brand_id`
									FROM `product_brand_mapping` pbm
									INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = pbm.`brand_id`
									WHERE pbm.`product_id` = %s
								""")
			get_brand_mapping_data = (data['product_id'])
			count_brand_mapping = cursor.execute(get_brand_mapping_query,get_brand_mapping_data)

			if count_brand_mapping > 0:
				product_brnad = cursor.fetchone() 
				product_data[key]['brand'] = product_brnad['brand']
				product_data[key]['brand_id'] = product_brnad['brand_id']
			else:
				product_data[key]['brand'] = ""	
				product_data[key]['brand_id'] = 0


			get_category_mapping_query = ("""SELECT mm.`meta_key_value` as `category`, mm.`meta_key_value_id` as `category_id`
									FROM `product_category_mapping` pbm
									INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = pbm.`category_id`
									WHERE pbm.`product_id` = %s
								""")
			get_category_mapping_data = (data['product_id'])
			count_category_mapping = cursor.execute(get_category_mapping_query,get_category_mapping_data)

			if count_category_mapping > 0:
				product_category = cursor.fetchone() 
				product_data[key]['category'] = product_category['category']
				product_data[key]['category_id'] = product_category['category_id']
			else:
				product_data[key]['category'] = ""
				product_data[key]['category_id'] = 0

			get_best_sellling_mapping_query = ("""SELECT * from product_best_selling_mapping
											WHERE `product_meta_id` = %s
										""")
			get_best_selling_mapping_data = (data['product_meta_id'])
			count_best_selling = cursor.execute(get_best_sellling_mapping_query,get_best_selling_mapping_data)

			if count_best_selling > 0:
				product_data[key]['best_selling'] = 1
			else:
				product_data[key]['best_selling'] = 0


			get_top_sellling_mapping_query = ("""SELECT * from product_top_selling_mapping
											WHERE `product_meta_id` = %s
										""")
			get_top_sellling_mapping_data = (data['product_meta_id'])
			count_top_selling = cursor.execute(get_top_sellling_mapping_query,get_top_sellling_mapping_data)

			if count_top_selling > 0:
				product_data[key]['top_selling'] = 1
			else:
				product_data[key]['top_selling'] = 0

			get_latest_product_mapping_query = ("""SELECT * from latest_product_mapping
											WHERE `product_meta_id` = %s
										""")
			get_latest_product_mapping_data = (data['product_meta_id'])
			count_latest_product = cursor.execute(get_latest_product_mapping_query,get_latest_product_mapping_data)

			if count_latest_product > 0:
				product_data[key]['latest_product'] = 1
			else:
				product_data[key]['latest_product'] = 0

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List-By-Catalog-Id---------------------#

#----------------------Catalog-List---------------------#
@react_customer.route("/catalogList/<string:organisation_code>")
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def catalogList(organisation_code):
	connection = mysql_connection()
	cursor = connection.cursor()
	
	get_organisation_query = ("SELECT organisation_id from `organisation_master` where `organisation_code` = %s")
	get_organisation_data = (organisation_code)
	count_organisation = cursor.execute(get_organisation_query,get_organisation_data)
	organisation_data = cursor.fetchone()

	if count_organisation > 0:
		organisation_id = organisation_data['organisation_id']

		get_query = ("""SELECT c.`catalog_name`,pcm.`product_id`
					FROM `product_catalog_mapping` pcm
					INNER JOIN `catalogs` c ON c.`catalog_id` = pcm.`catalog_id`					
					WHERE pcm.`organisation_id` = %s""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
				get_query_product_meta = ("""SELECT `product_meta_id` FROM `product_meta` WHERE `product_id` = %s """)
				get_data_product_meta = (data['product_id'])
				cursor.execute(get_query_product_meta,get_data_product_meta)
				product_meta = cursor.fetchone()

				get_query_image = ("""SELECT `image`
											FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
				getdata_image = (product_meta['product_meta_id'])
				product_image_count = cursor.execute(get_query_image,getdata_image)

				if product_image_count >0 :
					product_image = cursor.fetchone()
					product_data[key]['image'] = product_image['image']
				else:
					product_data[key]['image'] = ""
	else:
			product_data = []

	return ({"attributes": {
		    	"status_desc": "product_details",
		    	"status": "success"
		    },
		    "responseList":product_data}), status.HTTP_200_OK

#----------------------Catalog-List---------------------#

#----------------------Product-List---------------------#
@react_customer.route("/getProductList/<int:product_id>")
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def getProductList(product_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_long_description`,
			pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,pm.`loyalty_points`
			FROM `product` p
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			WHERE p.`status` = 1 and p.`product_id` = %s""")
		get_data = (product_id)
		cursor.execute(get_query,get_data)

		product_data = cursor.fetchall()

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

			product_data[key]['is_cart'] = False

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Add-To-Cart---------------------#
@react_customer.route("/addProductToCart",methods=['POST'])
@cross_origin(origin='*')	
def addProductToCart():	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		product_meta_id = details.get('product_meta_id')
		customer_id = details.get('customer_id')
		organisation_id = details.get('organisation_id')
		last_update_id = details.get('organisation_id')
		product_status = "c"
		customer_prodcut_status = 1
		
		product_status = "c"
		get_query = ("""SELECT `product_meta_id`
			FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and `product_status` = %s """)

		getData = (product_meta_id,customer_id,product_status)
			
		count_product = cursor.execute(get_query,getData)

		if count_product > 0:

			connection.commit()
			cursor.close()

			return ({"attributes": {
				    	"status_desc": "customer_product_details",
				    	"status": "error"
				    },
				    "responseList":"Product Already Exsits" }), status.HTTP_200_OK

		else:

			insert_query = ("""INSERT INTO `customer_product_mapping`(`customer_id`,`product_meta_id`,`product_status`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s)""")

			data = (customer_id,product_meta_id,product_status,customer_prodcut_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)		

			mapping_id = cursor.lastrowid
			details['mapping_id'] = mapping_id

			qty = 1
			qty_status = 1

			insert_qty_query = ("""INSERT INTO `customer_product_mapping_qty`(`customer_mapping_id`,`qty`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
			data_qty = (mapping_id,qty,qty_status,organisation_id,last_update_id)
			cursor.execute(insert_qty_query,data_qty)
			
			get_query_count = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `customer_id` = %s and `product_status` = %s """)

			getDataCount = (customer_id,product_status)
				
			count_product = cursor.execute(get_query_count,getDataCount)

			connection.commit()
			cursor.close()

			return ({"attributes": {
					    		"status_desc": "customer_product_details",
					    		"status": "success"
					    	},
					    	"responseList":{"cart_count":count_product}}), status.HTTP_200_OK


#----------------------Add-To-Cart---------------------#

#----------------------Organisation---------------------#

@react_customer.route("/organisationDetails/<string:organisation_code>")
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def organisationDetails(organisation_code):

	connection = mysql_connection()
	cursor = connection.cursor()

	get_query = ("""SELECT *
					FROM `organisation_master` WHERE `organisation_code` = %s""")
	get_data = (organisation_code)

	cursor.execute(get_query,get_data)

	data = cursor.fetchone()

	return ({"attributes": {
				    "status_desc": "organisation_details",
				    "status": "success"
				},
				"responseList":data}), status.HTTP_200_OK


#----------------------Cart-List---------------------#

@react_customer.route("/getProductCustomerList/<string:key>/<int:user_id>")	
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])
def getProductCustomerList(key,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_wishlist_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
			pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
			FROM `customer_product_mapping` cpm 
			INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
			where cpm.`customer_id` = %s and cpm.`product_status` = %s """)	

		wishlist_data = (user_id,key)
		cursor.execute(get_wishlist_query,wishlist_data)

		wishlist = cursor.fetchall()	

		for tkey,tdata in enumerate(wishlist):			
			get_product_meta_image_quey = ("""SELECT `image` as `product_image`
				FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
			product_meta_image_data = (tdata['product_meta_id'])
			rows_count_image = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
			if rows_count_image > 0:
				product_meta_image = cursor.fetchone()
				wishlist[tkey]['image'] = product_meta_image['product_image']
			else:
				wishlist[tkey]['image'] = ""

			a_string = tdata['meta_key_text']
			a_list = a_string.split(',')

			met_key = []

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

				met_key.append({met_key_data['meta_key']:met_key_value_data['meta_key_value']})

				wishlist[tkey]['met_key_value'] = met_key

			get_query_discount = ("""SELECT `discount`
									FROM `product_meta_discount_mapping` pdm
									INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
									WHERE `product_meta_id` = %s """)
			getdata_discount = (tdata['product_meta_id'])
			count_dicscount = cursor.execute(get_query_discount,getdata_discount)

			if count_dicscount > 0:
				product_meta_discount = cursor.fetchone()
				wishlist[tkey]['discount'] = product_meta_discount['discount']

				discount = (tdata['out_price']/100)*product_meta_discount['discount']
				actual_amount = tdata['out_price'] - discount
				wishlist[tkey]['after_discounted_price'] = round(actual_amount,2)

			else:
				wishlist[tkey]['discount'] = 0
				wishlist[tkey]['after_discounted_price'] = tdata['out_price']

			qty_quey = ("""SELECT `qty` 
				FROM `customer_product_mapping_qty` WHERE `customer_mapping_id` = %s""")
			qty_data = (tdata['mapping_id'])
			rows_count_qty = cursor.execute(qty_quey,qty_data)
			if rows_count_qty > 0:
				qty = cursor.fetchone()
				wishlist[tkey]['count'] = qty['qty']
				wishlist[tkey]['total'] = tdata['out_price'] * qty['qty']
			else:
				wishlist[tkey]['count'] = 0	
				wishlist[tkey]['total'] = 0	
	   		
		return ({"attributes": {
		    		"status_desc": "customer_product_details",
		    		"status": "success"
		    	},
		    	"responseList":wishlist}), status.HTTP_200_OK


#----------------------Cart-List---------------------#

#----------------------Delete-cart-Item---------------------#

@react_customer.route("/deleteCartItem/<int:cart_id>",methods=['DELETE'])
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])
def deleteCartItem(cart_id):

	connection = mysql_connection()
	cursor = connection.cursor()
		
	delete_cart_query = ("""DELETE FROM `customer_product_mapping` WHERE `mapping_id` = %s """)
	delcartData = (cart_id)
		
	cursor.execute(delete_cart_query,delcartData)

	delete_cart_qty_query = ("""DELETE FROM `customer_product_mapping_qty` WHERE `customer_mapping_id` = %s """)
	delcartqtyData = (cart_id)
		
	cursor.execute(delete_cart_qty_query,delcartqtyData)

	connection.commit()
	cursor.close()
		
	return ({"attributes": {"status_desc": "Delete Cart",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-cart-Item---------------------#

#----------------------Update-Cart-Item---------------------#

@react_customer.route("/UpdateCartItem/<int:cart_id>", methods=['PUT'])
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])
def UpdateCartItem(cart_id):
	connection = mysql_connection()
	cursor = connection.cursor()
	details = request.get_json()

	qty = details.get('qty')
	update_query = ("""UPDATE `customer_product_mapping_qty` SET `qty` = %s
			WHERE `customer_mapping_id` = %s """)
	update_data = (qty,cart_id)
	cursor.execute(update_query,update_data)

	connection.commit()
	cursor.close()

	return ({"attributes": {"status_desc": "Update Cart Item",
							"status": "success"},
			"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Cart-Item---------------------#

#----------------------Save-Order---------------------#
@react_customer.route("/saveOrder",methods=['POST'])
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def saveOrder():
		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		user_id = details['user_id']
		amount = details['amount']
		purpose = details['purpose']
		coupon_code = details['coupon_code']

		initiate_paymengt_status = 1
		organisation_id  = details['organisation_id']
		last_update_id = 1

		select_product_status = "c"

		get_customer_product_query = ("""SELECT `mapping_id`,`product_meta_id`,`product_status`
			FROM `customer_product_mapping` WHERE  `customer_id` = %s and `product_status` = %s """)

		geCustomerProductData = (user_id,select_product_status)
			
		customerProductCount = cursor.execute(get_customer_product_query,geCustomerProductData)

		if customerProductCount > 0:

			customerProductData = cursor.fetchall()			

			initiatePaymentQuery = ("""INSERT INTO `instamojo_initiate_payment`(`user_id`, 
				`status`,`organisation_id`,`last_update_id`) VALUES (%s,%s,%s,%s)""")

			initiateData = (user_id,initiate_paymengt_status,organisation_id,last_update_id)

			cursor.execute(initiatePaymentQuery,initiateData)

			transaction_id = cursor.lastrowid

			for key,data in enumerate(customerProductData):
				product_status = "o"
				customer_product_update_query = ("""UPDATE `customer_product_mapping` SET `product_status` = %s
					WHERE `product_meta_id` = %s and `product_status` = %s""")
				update_data = (product_status,data['product_meta_id'],select_product_status)
				cursor.execute(customer_product_update_query,update_data)

				orderProductQuery = ("""INSERT INTO `order_product`(`transaction_id`, 
					`customer_mapping_id`,`status`,`organisation_id`,`last_update_id`) VALUES (%s,%s,%s,%s,%s)""")
				orderProductData = (transaction_id,data['mapping_id'],initiate_paymengt_status,organisation_id,last_update_id)
				cursor.execute(orderProductQuery,orderProductData)

			get_query = ("""SELECT `first_name`,`last_name`,`email`,`phoneno`
				FROM `admins` WHERE  `admin_id` = %s""")

			getData = (user_id)
				
			count = cursor.execute(get_query,getData)

			if count >0:

				data = cursor.fetchone()

				URL = BASE_URL + "ecommerce_customer/EcommerceCustomer/createPaymentRequest"

				headers = {'Content-type':'application/json', 'Accept':'application/json'}

				payload = {
							"amount":amount,
							"purpose":purpose,
							"buyer_name":data['first_name']+' '+data['last_name'],
							"email":data['email'],
							"phone":data['phoneno'],
							"user_id":user_id,
							"transaction_id":transaction_id,
							"coupon_code":coupon_code,
							"organisation_id" : organisation_id
						}

				mojoResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()

				if mojoResponse['responseList']['transactionId']:
					createInvoiceUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/createInvoice"
					payloadData = {
							"user_id":user_id,
							"transaction_id":mojoResponse['responseList']['transactionId']							
					}

					send_invoice = requests.post(createInvoiceUrl,data=json.dumps(payloadData), headers=headers).json()

					get_user_device_query = ("""SELECT `device_token`
								FROM `devices` WHERE  `user_id` = %s""")

					get_user_device_data = (user_id)
					device_token_count = cursor.execute(get_user_device_query,get_user_device_data)

					if device_token_count > 0:
						device_token_data = cursor.fetchone()

						get_organisation_firebase_query = ("""SELECT `firebase_key`
								FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
						get_organisation_firebase_data = (organisation_id)
						cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
						firebase_data = cursor.fetchone()

						sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/sendAppPushNotifications"
						payloadpushData = {
							"device_id":device_token_data['device_token'],
							"firebase_key": firebase_data['firebase_key']
						}

						send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

					get_user_query = ("""SELECT `name`,`first_name`,`last_name`,`email`,`phoneno`,`address_line_1`,`address_line_2`,
								`city`,`country`,`state`,`pincode`
					FROM `admins` WHERE  `admin_id` = %s""")
					getUserData = (user_id)
					countUser = cursor.execute(get_user_query,getUserData)

					if countUser > 0:
						customer_data = cursor.fetchone()
						send_sms(customer_data['phoneno'])

					for key,data in enumerate(customerProductData):	
						product_loyality_point_query = 	("""SELECT `loyalty_points`
							FROM `product_meta` WHERE  `product_meta_id` = %s """)
						getProductLoyaltyData = (data['product_meta_id'])
				
						productLoyaltyCount = cursor.execute(product_loyality_point_query,getProductLoyaltyData)	

						if productLoyaltyCount > 0:
							productLoyalityData = cursor.fetchone()
							get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s""")
							customer_wallet_data = (user_id)
							cursor.execute(get_customer_wallet_query,customer_wallet_data)
							wallet_data = cursor.fetchone()

							wallet = productLoyalityData['loyalty_points']+wallet_data['wallet']				

							insert_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
								`updated_value`,`organisation_id`,`status`,`last_update_id`)
									VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
							transaction_source = "product_loyalty"
							updated_value = wallet
							previous_value = 0
							wallet_transaction_data = (user_id,productLoyalityData['loyalty_points'],transaction_source,previous_value,updated_value,organisation_id,initiate_paymengt_status,last_update_id)

							cursor.execute(insert_wallet_transaction_query,wallet_transaction_data)	


							update_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s
														WHERE `admin_id` = %s """)
							update_customer_wallet_data = (updated_value,user_id)
							cursor.execute(update_customer_wallet_query,update_customer_wallet_data)

							get_user_device_query = ("""SELECT `device_token`
									FROM `devices` WHERE  `user_id` = %s""")		
							get_user_device_data = (user_id)
							device_token_count = cursor.execute(get_user_device_query,get_user_device_data)

							if device_token_count > 0:
								device_token_data = cursor.fetchone()
								get_organisation_firebase_query = ("""SELECT `firebase_key`
									FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
								get_organisation_firebase_data = (organisation_id)
								cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
								firebase_data = cursor.fetchone()

								headers = {'Content-type':'application/json', 'Accept':'application/json'}
								sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/sendAppPushNotificationforloyalityPoint"
								payloadpushData = {
									"device_id":device_token_data['device_token'],
									"firebase_key": firebase_data['firebase_key']
								}

								send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

				connection.commit()
				cursor.close()

				return ({"attributes": {"status_desc": "Instamojo payment request Details",
									"status": "success"},
					"responseList": mojoResponse['responseList']}), status.HTTP_200_OK
		else:
			return ({"attributes": {
			    		"status_desc": "Instamojo payment request Details",
			    		"status": "error",
			    		"message":"Cart Empty"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

#----------------------Save-Order---------------------#


#----------------------Add-Customer---------------------#

@react_customer.route("/AddCustomer",methods=['POST'])
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def AddCustomer():	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		first_name = details['first_name']
		last_name = details['last_name']
		email = details['email']
		password = details['password']
		phoneno = details['phoneno']
		address_line_1 = details['address_line_1']
		address_line_2 = details['address_line_2']
		city = details['city']
		county = details['county']
		state = details['state']
		pincode = details['pincode']
		emergency_contact = details['emergency_contact']
		role_id = 4
		admin_status = 1
		organisation_id = 1
		registration_type = details['registration_type']

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		if registration_type == 1:
			count_phone_type = 0

		else:
			get_phone_type_query = ("""SELECT *
				FROM `admins` WHERE `phoneno` = %s and `registration_type` = %s""")
			get_phone_type_data = (phoneno,registration_type)

			count_phone_type = cursor.execute(get_phone_type_query,get_phone_type_data)

		if count_phone_type > 0:
			get_query_login_data = ("""SELECT a.`admin_id` as `user_id`,a.`first_name`,a.`last_name`,a.`email`,a.`org_password`,
					a.`phoneno`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
					a.`pincode`,a.`emergency_contact`,a.`role_id`,a.`wallet`,a.`registration_type`,cr.`referral_code`,
					rs.`retailer_name`,rs.`phoneno` as retailer_phoneno					
					FROM `admins` a
					INNER JOIN `customer_referral` cr ON cr.`customer_id` = a.`admin_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
					WHERE a.`phoneno` = %s and a.`registration_type` = %s """)
			getDataLogin = (phoneno,registration_type)
			cursor.execute(get_query_login_data,getDataLogin)
			login_data = cursor.fetchone()

		else:

			get_query = ("""SELECT `email`
				FROM `admins` WHERE `email` = %s """)

			getData = (email)
			
			count_retailer = cursor.execute(get_query,getData)

			

			if count_retailer > 0:
				connection.commit()
				cursor.close()

				return ({"attributes": {
				    		"status_desc": "customer_details",
				    		"status": "error",
				    		"message":"Customer Phoneno Already Exist"
				    	},
				    	"responseList":{} }), status.HTTP_200_OK

			else:

				get_query_phone = ("""SELECT *
				FROM `admins` WHERE `phoneno` = %s and `role_id` = 4""")
				getDataPhone = (details['phoneno'])
				count_customer_phone = cursor.execute(get_query_phone,getDataPhone)

				
				if count_customer_phone > 0:
					connection.commit()
					cursor.close()

					return ({"attributes": {
					    		"status_desc": "customer_details",
					    		"status": "error",
					    		"message":"Customer Phoneno Already Exist"
					    	},
					    	"responseList":{} }), status.HTTP_200_OK

				else:
					insert_query = ("""INSERT INTO `admins`(`first_name`,`last_name`,`email`,`org_password`,
										`phoneno`,`address_line_1`,`address_line_2`,`city`,`country`,
										`state`,`pincode`,`emergency_contact`,`role_id`,`registration_type`,`status`,`organisation_id`,`date_of_creation`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
					data = (first_name,last_name,email,password,phoneno,address_line_1,address_line_2,city,county,state,pincode,emergency_contact,role_id,registration_type,admin_status,organisation_id,date_of_creation)
					cursor.execute(insert_query,data)

					admin_id = cursor.lastrowid				
							

					get_query_city = ("""SELECT *
						FROM `retailer_store` WHERE `city` = %s """)
					getDataCity = (details['city'])
					count_city = cursor.execute(get_query_city,getDataCity)

					if count_city > 0:
						city_data = cursor.fetchone()
						insert_mapping_user_retailer = ("""INSERT INTO `user_retailer_mapping`(`user_id`,`retailer_id`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
						organisation_id = 1
						last_update_id = 1
						city_insert_data = (admin_id,city_data['retailer_store_id'],admin_status,organisation_id,last_update_id)	
						cursor.execute(insert_mapping_user_retailer,city_insert_data)

					insert_customer_referal_code_query = ("""INSERT INTO `customer_referral`(`customer_id`,`referral_code`,`organisation_id`,`status`,`last_update_id`)
							VALUES(%s,%s,%s,%s,%s)""")
					organisation_id = 1
					last_update_id = 1	

					customer_referral_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

					referal_data = (admin_id,customer_referral_code,organisation_id,admin_status,last_update_id)
					cursor.execute(insert_customer_referal_code_query,referal_data)		

					if details['referal_code']:				

						get_referal_query = ("""SELECT *
							FROM `customer_referral` WHERE `referral_code` = %s""")
						getReferalData = (details['referal_code'])
						count_referal = cursor.execute(get_referal_query,getReferalData)

						if count_referal > 0:

							referal = cursor.fetchone()
							customer_referral_id = referal['customer_referral_id']
							

							insert_user_referal_code_query = ("""INSERT INTO `user_referral_mapping`(`customer_referral_id`,`customer_id`,`organisation_id`,`status`,`last_update_id`)
								VALUES(%s,%s,%s,%s,%s)""")
							user_referal_data = (customer_referral_id,admin_id,organisation_id,admin_status,last_update_id)

							cursor.execute(insert_user_referal_code_query,user_referal_data)

							customer_referral_user_id = referal['customer_id']

							organisation_id = 1
							referal_user_loyality_type = 1
							get_loyality_query = ("""SELECT *
									FROM `loyality_master`
				 					WHERE `organisation_id` = %s and loyality_type =%s """)

							get_loyality_data = (organisation_id,referal_user_loyality_type)
							cursor.execute(get_loyality_query,get_loyality_data)
							loyality_data = cursor.fetchone()

							referred_user_loyality_type = 2
							get_refferd_user_loyality_query = ("""SELECT *
									FROM `loyality_master`
				 					WHERE `organisation_id` = %s and loyality_type =%s""")
							get_reffered_loyality_data = (organisation_id,referred_user_loyality_type)
							cursor.execute(get_refferd_user_loyality_query,get_reffered_loyality_data)
							refered_loyality_data = cursor.fetchone()

							get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s""")
							customer_wallet_data = (customer_referral_user_id)
							cursor.execute(get_customer_wallet_query,customer_wallet_data)
							wallet_data = cursor.fetchone()

							wallet = loyality_data['loyality_amount']+wallet_data['wallet']

							update_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s
														WHERE `admin_id` = %s """)
							update_data = (wallet,customer_referral_user_id)
							cursor.execute(update_customer_wallet_query,update_data)

							update_refferd_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s
														WHERE `admin_id` = %s """)
							update_reffered_customer_data = (refered_loyality_data['loyality_amount'],admin_id)
							cursor.execute(update_refferd_customer_wallet_query,update_reffered_customer_data)

							insert_referal_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
								`updated_value`,`organisation_id`,`status`,`last_update_id`)
									VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
							transaction_source = "refer"
							updated_value = wallet
							previous_value = 0
							referal_wallet_transaction_data = (customer_referral_user_id,loyality_data['loyality_amount'],transaction_source,previous_value,updated_value,organisation_id,admin_status,last_update_id)

							cursor.execute(insert_referal_wallet_transaction_query,referal_wallet_transaction_data)	

							insert_referred_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
								`updated_value`,`organisation_id`,`status`,`last_update_id`)
									VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
							updated_reffered_value = refered_loyality_data['loyality_amount']

							referrd_wallet_transaction_data = (admin_id,refered_loyality_data['loyality_amount'],transaction_source,previous_value,updated_value,organisation_id,admin_status,last_update_id)

							cursor.execute(insert_referred_wallet_transaction_query,referrd_wallet_transaction_data)	


							get_user_device_query = ("""SELECT `device_token`
								FROM `devices` WHERE  `user_id` = %s""")

							get_user_device_data = (customer_referral_user_id)
							device_token_count = cursor.execute(get_user_device_query,get_user_device_data)

							if device_token_count > 0:
								device_token_data = cursor.fetchone()
								headers = {'Content-type':'application/json', 'Accept':'application/json'}
								sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/sendAppPushNotificationforloyalityPoint"
								payloadpushData = {
									"device_id":device_token_data['device_token'],
									"firebase_key":"AAAATLVsDiA:APA91bFYEaJWn4PT09fp53An-H2Gmsn9kojQpX6V9Y8ol0Rj6qhH_j_Uos6Gua1kGMcuO5YsxNgbwp3HDZlE9fUNiUsM9ePEghWGaMDCXWXDiURHlHZnkDEvIvGvfYTrCecioM0Nx9hX"
								}

								send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

							get_refferd_user_device_query = ("""SELECT `device_token`
								FROM `devices` WHERE  `user_id` = %s""")

							get_refferd_user_device_data = (admin_id)
							reffred_user_device_token_count = cursor.execute(get_refferd_user_device_query,get_refferd_user_device_data)	

							if reffred_user_device_token_count > 0:
								refferd_user_device_token_data = cursor.fetchone()

								headers = {'Content-type':'application/json', 'Accept':'application/json'}
								sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/sendAppPushNotificationforloyalityPoint"
								payloadpushData = {
									"device_id":refferd_user_device_token_data['device_token'],
									"firebase_key":"AAAATLVsDiA:APA91bFYEaJWn4PT09fp53An-H2Gmsn9kojQpX6V9Y8ol0Rj6qhH_j_Uos6Gua1kGMcuO5YsxNgbwp3HDZlE9fUNiUsM9ePEghWGaMDCXWXDiURHlHZnkDEvIvGvfYTrCecioM0Nx9hX"
								}

								send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

					get_query_login_data = ("""SELECT a.`admin_id` as `user_id`,a.`first_name`,a.`last_name`,a.`email`,a.`org_password`,
						a.`phoneno`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
						a.`pincode`,a.`emergency_contact`,a.`role_id`,a.`wallet`,a.`registration_type`,cr.`referral_code`,rs.`retailer_name`,
						rs.`phoneno` as retailer_phoneno				
						FROM `admins` a
						INNER JOIN `customer_referral` cr ON cr.`customer_id` = a.`admin_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
						INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
						WHERE a.`admin_id` = %s """)
					getDataLogin = (admin_id)
					cursor.execute(get_query_login_data,getDataLogin)
					login_data = cursor.fetchone()					

				connection.commit()
				cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_details",
				    "status": "success"
				},
				"responseList":login_data}), status.HTTP_200_OK

#----------------------Add-Customer---------------------#

#----------------------Customer-Login---------------------#

@react_customer.route("/Login",methods=['POST'])
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def Login():	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_emiail_query = ("""SELECT *
			FROM `admins` WHERE `email` = %s and `role_id` = 4""")
		getDataEmail = (details['email'])

		count_customer = cursor.execute(get_emiail_query,getDataEmail)

		if count_customer > 0:
			
			get_query = ("""SELECT a.`admin_id` as `user_id`,a.`first_name`,a.`last_name`,a.`email`,a.`org_password`,
				a.`phoneno`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
				a.`pincode`,a.`emergency_contact`,a.`role_id`,a.`wallet`,a.`registration_type`,cr.`referral_code`,
				rs.`retailer_name`,rs.`phoneno` as retailer_phoneno				
				FROM `admins` a
				INNER JOIN `customer_referral` cr ON cr.`customer_id` = a.`admin_id` 
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
				INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id`
				WHERE a.`email` = %s and a.`org_password` = %s""")
			getData = (details['email'],details['password'])
			count_customer_email_password = cursor.execute(get_query,getData)			

			if count_customer_email_password > 0:
				login_data = cursor.fetchone()			

				return ({"attributes": {
				    		"status_desc": "login_details",
				    		"status": "success",
				    		"message":"Login Successfully"
				    	},
				    	"responseList":login_data}), status.HTTP_200_OK
			else:
				return ({"attributes": {
				    		"status_desc": "login_details",
				    		"status": "error",
				    		"message":"Email id and password does't match"
				    	},
				    	"responseList":{}}), status.HTTP_200_OK
		else:		
			return ({"attributes": {
			    		"status_desc": "customer_details",
			    		"status": "error",
			    		"message":"We cannot find an account with that email address"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK
				    		

#----------------------Customer-Login---------------------#

#----------------------Dashboard---------------------#
@react_customer.route("/dashboard/<int:category_id>/<int:user_id>/<int:organisation_id>")	
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])
def dashboard(user_id,category_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_category_query = ("""SELECT meta_key_value_id
			FROM `home_category_mapping` WHERE organisation_id = %s LIMIT 6""")

		get_category_data = (organisation_id)
		cout_home_category = cursor.execute(get_category_query,get_category_data)

		if cout_home_category > 0:

			home_category_data = cursor.fetchall()

			for key,data in enumerate(home_category_data):
				get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
				FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

				getdata_key_value = (data['meta_key_value_id'])
				cursor.execute(get_key_value_query,getdata_key_value)

				key_value_data = cursor.fetchone()

				home_category_data[key]['meta_key_value'] = key_value_data['meta_key_value']
				home_category_data[key]['image'] = key_value_data['image']
		else:
			home_category_data = []

		get_brand_query = ("""SELECT meta_key_value_id
			FROM `home_brand_mapping`  WHERE organisation_id = %s """)
		get_brand_data = (organisation_id)

		count_home_brand = cursor.execute(get_brand_query,get_brand_data)

		if count_home_brand > 0:

			home_brand_data = cursor.fetchall()

			for hkey,hdata in enumerate(home_brand_data):
				get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
				FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

				getdata_key_value = (hdata['meta_key_value_id'])
				cursor.execute(get_key_value_query,getdata_key_value)

				key_value_data = cursor.fetchone()

				home_brand_data[hkey]['meta_key_value'] = key_value_data['meta_key_value']
				home_brand_data[hkey]['image'] = key_value_data['image']
		else:
			home_brand_data = []

		get_top_selling_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`
			FROM `product_top_selling_mapping` pts 
			INNER JOIN `product_meta` pm ON pts.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id` 
			WHERE pts.`organisation_id` = %s and p.`status` = %s
			LIMIT 6""")	
		top_selling_status = 1
		get_top_selling_product_data = (organisation_id,top_selling_status)
		cursor.execute(get_top_selling_product,get_top_selling_product_data)
		top_selling_product = cursor.fetchall()

		for tkey,tdata in enumerate(top_selling_product):			
			get_product_meta_image_quey = ("""SELECT `image` as `product_image`
			FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
			product_meta_image_data = (tdata['product_meta_id'])
			rows_count_image_top_selling = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
			if rows_count_image_top_selling > 0:
				product_meta_image = cursor.fetchone()
				top_selling_product[tkey]['product_image'] = product_meta_image['product_image']
			else:
				top_selling_product[tkey]['product_image'] = ""	

			get_product_meta_inventory_stock_quey = ("""SELECT `stock`
			FROM `product_inventory` WHERE `product_meta_id` = %s """)
			product_meta_inventory_stock_data = (tdata['product_meta_id'])
			row_count_stock = cursor.execute(get_product_meta_inventory_stock_quey,product_meta_inventory_stock_data)

			if row_count_stock > 0:
				product_meta_inventory_stock = cursor.fetchone()

				top_selling_product[tkey]['totalproduct'] = product_meta_inventory_stock['stock']
			else:
				top_selling_product[tkey]['totalproduct'] = 0

		get_best_selling_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`,pm.`out_price` price
			FROM `product_best_selling_mapping` pbsm 
			INNER JOIN `product_meta` pm ON pbsm.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id` 
			WHERE pbsm.`organisation_id` = %s and p.`status` = %s
			LIMIT 6""")
		best_selling_status = 1
		get_best_selling_product_data = (organisation_id,best_selling_status)
		cursor.execute(get_best_selling_product,get_best_selling_product_data)
		best_selling_product = cursor.fetchall()

		for bkey,bdata in enumerate(best_selling_product):
			get_product_meta_image_quey = ("""SELECT `image`
			FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
			product_meta_image_data = (bdata['product_meta_id'])
			rows_count_image_best_selling = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
			if rows_count_image_best_selling > 0:
				product_meta_image = cursor.fetchone()
				best_selling_product[bkey]['product_image'] = product_meta_image['image']
			else:
				best_selling_product[bkey]['product_image'] = ""

		get_offer_product =  ("""SELECT pom.`product_id`,o.`offer_id`,o.`offer_image`,o.`discount_percentage`
			FROM `product_offer_mapping` pom 
			INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id` 
			WHERE pom.`organisation_id` = %s""")
		get_offer_data = (organisation_id)
		cursor.execute(get_offer_product,get_offer_data)
		offer_product = cursor.fetchall()

		get_new_arrival_product =  ("""SELECT pnm.`product_id`,n.`new_arrival_id`,n.`new_arrival_image` as `offer_image`,n.`discount_percentage`,n.`image_type`
			FROM `product_new_arrival_mapping` pnm 
			INNER JOIN `new_arrival` n ON n.`new_arrival_id` = pnm.`new_arrival_id`
			WHERE pnm.`organisation_id` = %s
			limit 6""")
		get_new_arrival_data = (organisation_id)
		cursor.execute(get_new_arrival_product,get_new_arrival_data)
		new_arrival_product = cursor.fetchall()

		product_status = "c"

		get_query_count = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `customer_id` = %s and `product_status` = %s """)

		getDataCount = (user_id,product_status)
				
		count_product = cursor.execute(get_query_count,getDataCount)

		get_budget_query = ("""SELECT *
			FROM `budget` WHERE  `organisation_id` = %s and `category_id` = %s""")

		get_budget_data = (organisation_id,category_id)
		cursor.execute(get_budget_query,get_budget_data)

		budget_data = cursor.fetchall()

		for key,data in enumerate(budget_data):
			budget_data[key]['last_update_ts'] = str(data['last_update_ts'])
			
		connection.commit()
		cursor.close()	

		offer_data = 	[
							{
								"offer_id":1,
								"product_id":1,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/home_banner1.png",
								"discount_percentage":10
	        				},
	        				{
	        					"offer_id":2,
	        					"product_id":2,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/home_banner2.png",
								"discount_percentage":10
	        				},
	        				{
	        					"offer_id":3,
	        					"product_id":3,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/home_banner3.png",
								"discount_percentage":10
							}

						]  	

		new_arrivale = 	[
							{
								"new_arrivale_id":1,
								"product_id":4,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/home_1.png",
								"discount_percentage":10
	        				},
	        				{
	        					"new_arrivale_id":2,
	        					"product_id":5,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/images1.jpg",
								"discount_percentage":10
	        				},
	        				{
	        					"new_arrivale_id":3,
	        					"product_id":6,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/images2.jpg",
								"discount_percentage":10
							},
							{
	        					"new_arrivale_id":4,
	        					"product_id":7,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/images3.jpg",
								"discount_percentage":10
							}
						]	

		top_selling = 	[
							{
								"top_selling_id":1,
								"product_id":8,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/drive.png",
								"product_name":"test Product1",
								"totalproduct":1
	        				},
	        				{
	        					"top_selling_id":2,
	        					"product_id":9,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/image2.png",
								"product_name":"test Product2",
								"totalproduct":2
	        				},
	        				{
	        					"top_selling_id":3,
	        					"product_id":10,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/memorycard.png",
								"product_name":"test Product3",
								"totalproduct":3
							},
							{
	        					"top_selling_id":4,
	        					"product_id":11,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/phone.jpg",
								"product_name":"test Product3",
								"totalproduct":3
							}

						]

		best_selling = 	[
							{
								"product_id":12,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/image2.png",
								"product_name":"i phone 11",
								"price":79999
	        				},
	        				{	        					
	        					"product_id":13,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/81T7lVQGdxL._SY606_.jpg",
								"product_name":"MI A3",
								"price":16999
	        				},
	        				{	        					
	        					"product_id":14,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/3e97ce53c0a379894aff19753b7fa70c34f71e9256d725e07acdaf60458ab96e.jpg",
								"product_name":"Nokia 6.1",
								"price":13999
							},
							{	        					
	        					"product_id":15,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/01_Samsung-galaxy-a50-.png",
								"product_name":"Samsung Galaxy A50",
								"price":15499
							},
							{	        					
	        					"product_id":16,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/S_mdr.png",
								"product_name":"Sony MDR",
								"price":2199
							},
							{	        					
	        					"product_id":16,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/memorycard.png",
								"product_name":"Sandisk 16GB Micro SD",
								"price":899
							}

						]				

	   		
		return ({"attributes": {
		    		"status_desc": "customer_product_details",
		    		"status": "success"
		    	},
		    	"responseList":{"offer_data":offer_product,"new_arrivale":new_arrival_product,"top_selling":top_selling_product,"home_category_data":home_category_data,
		    					"home_brand_data":home_brand_data,"best_selling":best_selling_product,"budget_data":budget_data,
		    					"cart_count":count_product}}), status.HTTP_200_OK

#----------------------Dashboard---------------------#

def send_sms(phone_no):		
	url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
	user = 'creamsonintelli'
	password = 'denver@1234'	
	sid = 'CRMLTD'
	msg = "Thank You for Placing Order."
	msisdn = phone_no
	fl = '0'
	gwid = '2'
	payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
	msisdn,sid,msg,fl,gwid)
	postUrl = url+payload
	print(postUrl)
	print(msisdn,msg)

	response = requests.request("POST", postUrl)

	print(response.text)

def send_email(**kwagrs):
	connection = mysql_connection()
	cursor = connection.cursor()
	config_info = kwagrs['config_info']
	user_info = kwagrs['user_info']
	res = 'Failure. Wrong MailId or SourceApp.'

	if user_info['EMAIL_ID'] and config_info['application_name']:
		msg = MIMEMultipart()
		msg['Subject'] = config_info['Subject']
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = user_info['EMAIL_ID']

		html = config_info['Email_Body']
		part1 = MIMEText(html, 'html')
		msg.attach(part1)
		try:
			smtp = SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, user_info['EMAIL_ID'], msg.as_string())
			
			res = {"status":'Success'}
			sent = 'Y'
			
		except Exception as e:
			res = {"status":'Failure'}
			sent = 'N'
			# raise e
		smtp.quit()
		mailmessage_insert_query = ("""INSERT INTO `mails`(`tomail`, `subject`, `body`, 
			`sourceapp`, `sent`) VALUES (%s,%s,%s,%s,%s)""")
		mail_data = (user_info['EMAIL_ID'],config_info['Subject'],html,
			config_info['application_name'],sent)
		cursor.execute(mailmessage_insert_query,mail_data)
	connection.commit()
	cursor.close()
	
	return res

