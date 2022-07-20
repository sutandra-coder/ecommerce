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
import random
import json
import string
import smtplib
import imghdr
import io
import re
import math
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

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

def mysql_connection_analytics():
	connection_analytics = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='ecommerce_analytics',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection_analytics'''

def mysql_connection():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def mysql_connection_analytics():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce_analytics',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

ecommerce_consumer_configuration = Blueprint('ecommerce_consumer_configuration_api', __name__)
api = Api(ecommerce_consumer_configuration,  title='Ecommerce API',description='Ecommerce API')

name_space = api.namespace('EcommerceConsumerConfiguration',description='Ecommerce Consumer Configuration')
name_space_consumer_dashboard = api.namespace('Dashboard',description='Consumer Dashboard')


consumer_configuration_postmodel = api.model('consumer_configuration_postmodel',{	
	"section_id": fields.Integer,
	"catalog_id": fields.Integer,
	"category_id": fields.Integer,	
	"configuration_type":fields.Integer(required=True),
	"display_type":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"retailer_store_store_id": fields.Integer(required=True),
	"last_update_id": fields.Integer(required=True)
})

consumer_configuration_putmodel = api.model('consumer_configuration_putmodel',{
	"consumer_configuration_id":fields.List(fields.Integer)
})

#----------------------Add-Consumer-Configuration---------------------#

@name_space.route("/addConsumerConfigurarion")	
class addConsumerConfigurarion(Resource):
	@api.expect(consumer_configuration_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "section_id" in details:
			section_id = details['section_id']
		else:
			section_id = 0

		if details and "catalog_id" in details:
			catalog_id = details['catalog_id']
		else:
			catalog_id = 0

		if details and "category_id" in details:
			category_id = details['category_id']
		else:
			category_id = 0
		

		configuration_type =  details['configuration_type']
		display_type = details['display_type']
		organisation_id =  details['organisation_id']
		retailer_store_store_id =  details['retailer_store_store_id']
		last_update_id =  details['last_update_id']

		get_query = ("""SELECT sequence
					FROM `consumer_configuration` cc 
					where cc.`organisation_id` = %s and cc.`retailer_store_store_id` = %s and cc.`category_id` = %s ORDER BY sequence DESC limit 1""")
		get_data = (organisation_id,retailer_store_store_id,category_id)

		count = cursor.execute(get_query,get_data)

		if count > 0:
			consumer_sequence_data = cursor.fetchone()
			sequence = consumer_sequence_data['sequence'] + 1
		else:
			sequence = 1

		insert_query = ("""INSERT INTO `consumer_configuration`(`section_id`,`catalog_id`,`category_id`,`sequence`,`configuration_type`,`display_type`,`organisation_id`,`retailer_store_store_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		data = (section_id,catalog_id,category_id,sequence,configuration_type,display_type,organisation_id,retailer_store_store_id,last_update_id)
		cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "consumer configuration",
			    		"status": "success",
			    		"message":""
			    	},
			    	"responseList": details}), status.HTTP_200_OK

#----------------------Add-Consumer-Configuration---------------------#

#----------------------Update-Consumer-Configuration---------------------#

@name_space.route("/UpdateConsumerConfiguration/<int:retailer_store_store_id>/<int:organisation_id>/<int:category_id>")
class UpdateConsumerConfiguration(Resource):
	@api.expect(consumer_configuration_putmodel)
	def put(self,retailer_store_store_id,organisation_id,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		consumer_configuration_ids = details.get('consumer_configuration_id',[])

		sequence = 0
		for key,consumer_configuration_id in enumerate(consumer_configuration_ids):
			sequence = sequence+1
			print(sequence)

			update_query = ("""UPDATE `consumer_configuration` SET `sequence` = %s
						WHERE `consumer_configuration_id` = %s and `retailer_store_store_id` = %s and `organisation_id` = %s and `category_id` = %s""")
			update_data = (sequence,consumer_configuration_id,retailer_store_store_id,organisation_id,category_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Consumer Configuration",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Consumer-Configuration---------------------#

#----------------------Delete-Consumer-Configuration---------------------#	
@name_space.route("/deleteConsumerConfiguration/<int:consumer_configuration_id>/<int:retailer_store_store_id>/<int:organisation_id>/<int:category_id>")	
class deleteConsumerConfiguration(Resource):
	def delete(self,consumer_configuration_id,retailer_store_store_id,organisation_id,category_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		delete_query = ("""DELETE FROM `consumer_configuration` WHERE `consumer_configuration_id` = %s """)
		delData = (consumer_configuration_id)		
		cursor.execute(delete_query,delData)

		get_query = ("""SELECT *
					FROM `consumer_configuration` cc 
					where cc.`organisation_id` = %s and cc.`retailer_store_store_id` = %s and cc.`category_id` = %s ORDER BY sequence asc""")
		get_data = (organisation_id,retailer_store_store_id,category_id)

		count = cursor.execute(get_query,get_data)

		if count > 0:
			consumer_configuration_data = cursor.fetchall()

			sequence = 0
			for key,data in enumerate(consumer_configuration_data):
				print(data['consumer_configuration_id'])
				sequence = sequence+1

				update_query = ("""UPDATE `consumer_configuration` SET `sequence` = %s
						WHERE `consumer_configuration_id` = %s and `retailer_store_store_id` = %s and `organisation_id` = %s and `category_id` = %s""")
				update_data = (sequence,data['consumer_configuration_id'],retailer_store_store_id,organisation_id,category_id)
				cursor.execute(update_query,update_data)


		return ({"attributes": {"status_desc": "delete_consumer_configuration",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Consumer-Configuration---------------------#	

#----------------------Consumer-Configuration-List---------------------#

@name_space.route("/consumerConfigurationList/<int:organisation_id>/<int:retailer_store_store_id>")	
class consumerConfigurationList(Resource):
	def get(self,organisation_id,retailer_store_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
					FROM `consumer_configuration` cc 
					where cc.`organisation_id` = %s and cc.`retailer_store_store_id` = %s ORDER BY sequence asc""")
		get_data = (organisation_id,retailer_store_store_id)

		count = cursor.execute(get_query,get_data)

		if count > 0:
			consumer_configuration_data = cursor.fetchall()
			for key,data in enumerate(consumer_configuration_data):

				if data['configuration_type'] == 1:
					get_offer_section_query = ("""SELECT *
						FROM `section_master` sm 
						where `section_id` = %s""")
					get_offer_section_data = (data['section_id'])
					count_offer_section = cursor.execute(get_offer_section_query,get_offer_section_data)
					if count_offer_section > 0:
						offer_section_data = cursor.fetchone()
						consumer_configuration_data[key]['section_name'] = offer_section_data['offer_section_name']
						consumer_configuration_data[key]['catalouge_name'] = ""
					else:
						consumer_configuration_data[key]['section_name'] = ""
						consumer_configuration_data[key]['catalouge_name'] = ""

				elif data['configuration_type'] == 2:
					get_catalouge_query = ("""SELECT *
						FROM `catalogs` sm 
						where `catalog_id` = %s""")
					get_catalouge_data = (data['catalog_id'])
					count_catalouge = cursor.execute(get_catalouge_query,get_catalouge_data)

					if count_catalouge > 0:
						catalouge_data =  cursor.fetchone()
						consumer_configuration_data[key]['section_name'] = ""
						consumer_configuration_data[key]['catalouge_name'] = catalouge_data['catalog_name']
					else:
						consumer_configuration_data[key]['section_name'] = ""
						consumer_configuration_data[key]['catalouge_name'] = ""

				consumer_configuration_data[key]['last_update_ts'] = str(data['last_update_ts'])

		else:
			consumer_configuration_data = []

		return ({"attributes": {
				    		"status_desc": "consumer_configuration",
				    		"status": "success"
				    	},
				    	"responseList":consumer_configuration_data}), status.HTTP_200_OK	

#----------------------Consumer-Configuration-List---------------------#

#----------------------Consumer-Dashboard---------------------#

@name_space_consumer_dashboard.route("/dashboard/<int:organisation_id>/<int:retailer_store_store_id>/<int:category_id>/<string:language>/<int:user_id>/<int:wop>")	
class dashboard(Resource):
	def get(self,organisation_id,retailer_store_store_id,category_id,language,user_id,wop):
		connection = mysql_connection()
		cursor = connection.cursor()

		if category_id == 0:
			connection_analytics = mysql_connection_analytics()
			cursor_analytics = connection_analytics.cursor()

			customer_id = user_id
			product_meta_id = 0
			from_web_or_phone = wop
			organisation_id = organisation_id

			storeviewquery = ("""INSERT INTO `customer_store_analytics`(`customer_id`, 
				`product_meta_id`, `from_web_or_phone`, `organisation_id`) VALUES (%s,
				%s,%s,%s)""")
			storeviewdata = cursor_analytics.execute(storeviewquery,(customer_id,product_meta_id,
				from_web_or_phone,organisation_id))

		now = datetime.now()
		today_date = now.strftime("%Y-%m-%d")

		get_query = ("""SELECT *
					FROM `consumer_configuration` cc 
					where cc.`organisation_id` = %s and cc.`retailer_store_store_id` = %s and cc.`category_id` = %s ORDER BY sequence asc""")
		get_data = (organisation_id,retailer_store_store_id,category_id)

		count = cursor.execute(get_query,get_data)

		if count > 0:
			consumer_configuration_data = cursor.fetchall()
			for key,data in enumerate(consumer_configuration_data):
				if data['configuration_type'] == 2:
					get_catalouge_query = ("""SELECT *
						FROM `catalogs` c
						where `catalog_id` = %s""")
					get_catalouge_data = (data['catalog_id'])
					count_catalouge = cursor.execute(get_catalouge_query,get_catalouge_data)

					if count_catalouge > 0:
						catalouge_data =  cursor.fetchone()
						consumer_configuration_data[key]['catalog_id'] = catalouge_data['catalog_id']
						consumer_configuration_data[key]['catalouge_name'] = catalouge_data['catalog_name']
						if data['display_type'] == 2:
							get_catalouge_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
								p.`product_type`,p.`category_id` as `product_type_id`
								FROM `product` p				
								INNER JOIN `product_catalog_mapping` pcm ON pcm.`product_id` = p.`product_id`
								INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
								WHERE p.`status` = 1 and pcm.`catalog_id` = %s and pom.`product_status` = 1 and pom.`organisation_id` = %s limit 4""")
						if data['display_type'] == 3:
							get_catalouge_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
								p.`product_type`,p.`category_id` as `product_type_id`
								FROM `product` p				
								INNER JOIN `product_catalog_mapping` pcm ON pcm.`product_id` = p.`product_id`
								INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
								WHERE p.`status` = 1 and pcm.`catalog_id` = %s and pom.`product_status` = 1 and pom.`organisation_id` = %s limit 9""")
						if data['display_type'] == 1:
							get_catalouge_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
								p.`product_type`,p.`category_id` as `product_type_id`
								FROM `product` p				
								INNER JOIN `product_catalog_mapping` pcm ON pcm.`product_id` = p.`product_id`
								INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
								WHERE p.`status` = 1 and pcm.`catalog_id` = %s and pom.`product_status` = 1 and pom.`organisation_id` = %s""")
						get_catalouge_product_data = (catalouge_data['catalog_id'],organisation_id)

						cursor.execute(get_catalouge_product_query,get_catalouge_product_data)
						catalouge_product_data = cursor.fetchall()

						for cpkey,cpdata in enumerate(catalouge_product_data):

							get_product_meta = (""" SELECT pm.`product_id`,pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price` FROM `product_meta` pm WHERE 
								`out_price` =  ( SELECT MIN(`out_price`) FROM product_meta  where product_id = %s) and product_id= %s """)
							get_product_meta_data = (cpdata['product_id'],cpdata['product_id'])
							count_product_meta = cursor.execute(get_product_meta,get_product_meta_data)				

							if count_product_meta > 0:
								product_meta_data = cursor.fetchone()

								catalouge_product_data[cpkey]['product_meta_id'] = product_meta_data['product_meta_id']
								catalouge_product_data[cpkey]['product_meta_code'] = product_meta_data['product_meta_code']
								catalouge_product_data[cpkey]['meta_key_text'] = product_meta_data['meta_key_text']
								catalouge_product_data[cpkey]['in_price'] = product_meta_data['in_price']

								get_out_price_query = (""" SELECT `out_price` FROM `product_meta_out_price` where `organisation_id` = %s and `status` = 1 and `product_meta_id` = %s""")
								get_out_price_data = (organisation_id, product_meta_data['product_meta_id'])
								count_out_price_data = cursor.execute(get_out_price_query,get_out_price_data)
								if count_out_price_data >0:
									out_price_data = cursor.fetchone()
									catalouge_product_data[cpkey]['out_price'] = out_price_data['out_price']
								else:
									catalouge_product_data[cpkey]['out_price'] = product_meta_data['out_price']								

								a_string = cpdata['meta_key_text']
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

									catalouge_product_data[cpkey]['met_key_value'] = met_key
									

								image_a = []	
								get_query_images = ("""SELECT `image`,`image_type`
												FROM `product_meta_images` WHERE `product_meta_id` = %s ORDER BY default_image_flag DESC""")
								getdata_images = (product_meta_data['product_meta_id'])
								cursor.execute(get_query_images,getdata_images)
								images = cursor.fetchall()

								for image in images:
									image_a.append({"image":image['image'],"image_type":image['image_type']})						

								if not image_a:
									if organisation_id == 93:
										catalouge_product_data[cpkey]['images'] = [{"image":"https://d1o7xhcyswcoe3.cloudfront.net/1/placeholderAMMobile.png","image_type":1}]
										
									else:
										catalouge_product_data[cpkey]['images'] = [{"image":"https://d1o7xhcyswcoe3.cloudfront.net/32/placeholderOthers.png","image_type":1}]
								else:
									catalouge_product_data[cpkey]['images'] = image_a

								product_meta_offer_mapping_query = (""" SELECT *
												FROM `product_meta_offer_mapping` pmom
												INNER JOIN `offer` o ON o.`offer_id` = pmom.`offer_id` 
												where  pmom.`organisation_id` = %s and `product_id` = %s and `product_meta_id` = %s""")
								product_meta_offer_mapping_data = (organisation_id,cpdata['product_id'],product_meta_data['product_meta_id'])
								count_product_meta_offer_mapping_data = cursor.execute(product_meta_offer_mapping_query,product_meta_offer_mapping_data)

								if count_product_meta_offer_mapping_data > 0:
									product_meta_offer_data = cursor.fetchone()

									catalouge_product_data[cpkey]['absolute_price'] = product_meta_offer_data['absolute_price']
									catalouge_product_data[cpkey]['is_online'] =  product_meta_offer_data['is_online']
									catalouge_product_data[cpkey]['discount_percentage'] = product_meta_offer_data['discount_percentage']
									catalouge_product_data[cpkey]['discount_value'] = product_meta_offer_data['discount_value']
									catalouge_product_data[cpkey]['coupon_code'] = product_meta_offer_data['coupon_code']
									catalouge_product_data[cpkey]['instruction'] = product_meta_offer_data['instruction']
									catalouge_product_data[cpkey]['is_product_meta_offer'] = product_meta_offer_data['is_product_meta_offer']
									

								else:
									get_product_offer_query = 	 ("""SELECT *
											FROM `product_offer_mapping` pom
											INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`
											WHERE pom.`product_id` = %s and pom.`organisation_id` = %s""")
									get_product_offer_data = (cpdata['product_id'],organisation_id)
									rows_count_product_offer = cursor.execute(get_product_offer_query,get_product_offer_data)
									if rows_count_product_offer > 0:
										product_offer_data = cursor.fetchone()
										catalouge_product_data[cpkey]['absolute_price'] = product_offer_data['absolute_price']
										catalouge_product_data[cpkey]['is_online'] =  product_offer_data['is_online']
										catalouge_product_data[cpkey]['discount_percentage'] = product_offer_data['discount_percentage']
										catalouge_product_data[cpkey]['discount_value'] = product_offer_data['discount_value']
										catalouge_product_data[cpkey]['coupon_code'] = product_offer_data['coupon_code']
										catalouge_product_data[cpkey]['instruction'] = product_offer_data['instruction']										
									
									else:
										catalouge_product_data[cpkey]['absolute_price'] = 0
										catalouge_product_data[cpkey]['discount_percentage'] = 0
										catalouge_product_data[cpkey]['discount_value'] = 0
										catalouge_product_data[cpkey]['coupon_code'] = ""
										catalouge_product_data[cpkey]['is_online'] = 0
										catalouge_product_data[cpkey]['instruction'] = ""

							consumer_configuration_data[key]['products'] = catalouge_product_data
					else:
						consumer_configuration_data[key]['catalog_id'] = 0
						consumer_configuration_data[key]['catalouge_name'] = ""

				elif data['configuration_type'] == 1:
					get_section =  ("""SELECT sm.`section_id`,sm.`offer_section_name`
						FROM `section_master` sm			 
						WHERE `section_id` = %s """)
					get_section_data = (data['section_id'])
					count_section = cursor.execute(get_section,get_section_data)
					section_data = cursor.fetchone()
					consumer_configuration_data[key]['section_id'] = section_data['section_id']
					consumer_configuration_data[key]['offer_section_name'] = section_data['offer_section_name']

					if count_section > 0:
						if data['display_type'] == 2:
							get_offer_query =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,o.`discount_percentage`,o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`offer_image_type`
								FROM `offer_section_mapping` osm 
								INNER JOIN `offer` o ON o.`offer_id` = osm.`offer_id`			
								WHERE osm.`organisation_id` = %s and o.`language` = %s and osm.`section_id` = %s and o.`status` = 1 and date(o.`validity_date`) >= %s limit 4""")
						if data['display_type'] == 3:
							get_offer_query =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,o.`discount_percentage`,o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`offer_image_type`
								FROM `offer_section_mapping` osm 
								INNER JOIN `offer` o ON o.`offer_id` = osm.`offer_id`			
								WHERE osm.`organisation_id` = %s and o.`language` = %s and osm.`section_id` = %s and o.`status` = 1 and date(o.`validity_date`) >= %s limit 9 """)
						if data['display_type'] == 1:
							get_offer_query =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,o.`discount_percentage`,o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`offer_image_type`
								FROM `offer_section_mapping` osm 
								INNER JOIN `offer` o ON o.`offer_id` = osm.`offer_id`			
								WHERE osm.`organisation_id` = %s and o.`language` = %s and osm.`section_id` = %s and o.`status` = 1 and date(o.`validity_date`) >= %s""")
						get_offer_data = (organisation_id,language,section_data['section_id'],today_date)
						cursor.execute(get_offer_query,get_offer_data)
						print(cursor._last_executed)
						offer_data = cursor.fetchall()

						i = 1
						for pkey,pdata in enumerate(offer_data):	
							print(pdata['offer_id'])			
							offer_data[pkey]['appearence'] = i
							i =i+1

							if pdata['product_offer_type'] == 1:
								get_offer_product_query = ("""SELECT pofm.`product_id`
									FROM `product_offer_mapping` pofm
									INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = pofm.`product_id`
									WHERE pofm.`offer_id` = %s and pom.`organisation_id` = %s and pom.`product_status` = 1""")
								get_offer_product_data = (pdata['offer_id'],organisation_id)
								count_prroduct_offer = cursor.execute(get_offer_product_query,get_offer_product_data)
								if count_prroduct_offer >0:
									product_offer_data = cursor.fetchone()
									offer_data[pkey]['product_id'] = product_offer_data['product_id']

									get_product_meta_query = ("""SELECT `product_meta_id`
									FROM `product_meta` pm
									INNER JOIN `product_organisation_mapping` pom  ON pom.`product_id` = pm.`product_id`
									WHERE pm.`product_id` = %s and pom.`product_status` = 1 and pom.`organisation_id` = %s""")
									get_product_meta_data = (product_offer_data['product_id'],organisation_id)
									count_product_meta_data = cursor.execute(get_product_meta_query,get_product_meta_data)

									if count_product_meta_data > 0:
										product_meta_data = cursor.fetchone()
										offer_data[pkey]['product_meta_id'] = product_meta_data['product_meta_id']
									else:
										offer_data[pkey]['product_meta_id'] = 0
								else:
									offer_data[pkey]['product_id'] = 0
									offer_data[pkey]['product_meta_id'] = 0
							else:
								offer_data[pkey]['product_id'] = 0
								offer_data[pkey]['product_meta_id'] = 0


					consumer_configuration_data[key]['products'] = offer_data

				consumer_configuration_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
			 
		else:
			consumer_configuration_data = []

		get_loyality_query_type_1 = ("""SELECT *
					FROM `loyality_master`			
					WHERE `organisation_id` = %s and `loyality_type` = 1""")

		get_loyality_data_type_1 = (organisation_id)
		count_loyality_query_type_1 = cursor.execute(get_loyality_query_type_1,get_loyality_data_type_1)

		referal_loyalty_data_type_1 = cursor.fetchone()

		get_loyality_query_type_2 = ("""SELECT *
					FROM `loyality_master`			
					WHERE `organisation_id` = %s and `loyality_type` = 2""")

		get_loyality_data_type_2 = (organisation_id)
		count_loyality_query_type_2 = cursor.execute(get_loyality_query_type_2,get_loyality_data_type_2)

		referal_loyalty_data_type_2 = cursor.fetchone()

		if count_loyality_query_type_1 >0 and count_loyality_query_type_2 >0:

			if referal_loyalty_data_type_1['loyality_amount'] == 0 and  referal_loyalty_data_type_2['loyality_amount'] == 0 :
				is_referal = 0
			else:
				is_referal = 1
		else:
			is_referal = 0
				

		if 	organisation_id == 83:

			get_category_query = ("""SELECT `category_id`,`category_name`,`category_image`,`status`
						FROM `category` WHERE `organisation_id` = %s ORDER BY mapping_id ASC""")
		else:
			get_category_query = ("""SELECT `category_id`,`category_name`,`category_image`,`status`
						FROM `category` WHERE `organisation_id` = %s and `status` = 1 ORDER BY mapping_id ASC""")

		get_category_data = (organisation_id)
		category_count = cursor.execute(get_category_query,get_category_data)

		category_data = cursor.fetchall()

		if category_count > 0:
			category = category_data
		else:
			category = []

		if user_id == 0:
			cart_count = 0
			user_data =  {}
			user_data["address_line_1"] = ""
			user_data["address_line_2"] = ""
			user_data["city"] = ""
			user_data["country"] = ""
			user_data["state"] = ""
			user_data["pincode"] = 0
		else:
			get_query_count = ("""SELECT COALESCE(sum(cpmq.`qty`),0) as cart_count 
				FROM `customer_product_mapping` cpm 
				INNER JOIN `customer_product_mapping_qty`cpmq ON cpmq.`customer_mapping_id` = cpm.`mapping_id` 
				WHERE cpm.`customer_id` = %s and cpm.`product_status` = 'c' and cpm.`organisation_id` = %s and cpmq.`organisation_id` = %s""")

			getDataCount = (user_id,organisation_id,organisation_id)
					
			count_product = cursor.execute(get_query_count,getDataCount)

			if count_product > 0:
				cart_count_data = cursor.fetchone()
				cart_count = int(cart_count_data['cart_count'])
			else:
				cart_count = 0

			get_user_details_query = (""" SELECT address_line_1,address_line_2,city,country,state,pincode 
										FROM `admins` WHERE admin_id = %s """)
			get_user_details_data = (user_id)
			count_user_details = cursor.execute(get_user_details_query,get_user_details_data)

			if count_user_details > 0:
				user_data = cursor.fetchone()
			else:
				user_data = {}
				user_data["address_line_1"] = ""
				user_data["address_line_2"] = ""
				user_data["city"] = ""
				user_data["country"] = ""
				user_data["state"] = ""
				user_data["pincode"] = 0

		if category_id > 0:
			get_brand_query = ("""SELECT `brand_id`
			FROM `category_brand_mapping`  WHERE `organisation_id` = %s and `category_id` = %s""")
			get_brand_data = (organisation_id,category_id)

			count_category_brand = cursor.execute(get_brand_query,get_brand_data)

			if count_category_brand > 0:

				brand_data = cursor.fetchall()

				for hkey,hdata in enumerate(brand_data):
					get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
					FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

					getdata_key_value = (hdata['brand_id'])
					cursor.execute(get_key_value_query,getdata_key_value)

					key_value_data = cursor.fetchone()

					brand_data[hkey]['meta_key_value'] = key_value_data['meta_key_value']
					brand_data[hkey]['image'] = key_value_data['image']
			else:
				brand_data = []

			get_budget_query = ("""SELECT *
				FROM `budget` WHERE  `organisation_id` = %s and `category_id` = %s""")		
			get_budget_data = (organisation_id,category_id)
			budget_count = cursor.execute(get_budget_query,get_budget_data)

			if budget_count > 0:
				budget_data = cursor.fetchall()

				for key,data in enumerate(budget_data):
					budget_data[key]['last_update_ts'] = str(data['last_update_ts'])
			else:
				budget_data = []
			
		else:
			brand_data = []
			budget_data = []

		return ({"attributes": {
				    		"status_desc": "consumer_configuration",
				    		"status": "success",
				    		"is_referal":is_referal,
				    		"category":category,
				    		"cart_count":cart_count,
				    		"address":user_data,
				    		"brand_data":brand_data,
				    		"budget_data":budget_data
				    	},
				    	"responseList":consumer_configuration_data}), status.HTTP_200_OK

#----------------------Consumer-Dashboard---------------------#

#----------------------Consumer-Dashboard---------------------#

@name_space_consumer_dashboard.route("/dashboardWithPagination/<int:organisation_id>/<int:retailer_store_store_id>/<int:category_id>/<string:language>/<int:user_id>/<int:wop>/<int:page>")	
class dashboardWithPagination(Resource):
	def get(self,organisation_id,retailer_store_store_id,category_id,language,user_id,wop,page):
		connection = mysql_connection()
		cursor = connection.cursor()

		if page == 1:
			offset = 0
		else:
			offset = (page - 1)*5

		if category_id == 0:
			connection_analytics = mysql_connection_analytics()
			cursor_analytics = connection_analytics.cursor()

			customer_id = user_id
			product_meta_id = 0
			from_web_or_phone = wop
			organisation_id = organisation_id

			storeviewquery = ("""INSERT INTO `customer_store_analytics`(`customer_id`, 
				`product_meta_id`, `from_web_or_phone`, `organisation_id`) VALUES (%s,
				%s,%s,%s)""")
			storeviewdata = cursor_analytics.execute(storeviewquery,(customer_id,product_meta_id,
				from_web_or_phone,organisation_id))

		now = datetime.now()
		today_date = now.strftime("%Y-%m-%d")

		get_query = ("""SELECT *
					FROM `consumer_configuration` cc 
					where cc.`organisation_id` = %s and cc.`retailer_store_store_id` = %s and cc.`category_id` = %s ORDER BY sequence asc LIMIT %s,5""")
		get_data = (organisation_id,retailer_store_store_id,category_id,offset)

		count = cursor.execute(get_query,get_data)

		if count > 0:
			consumer_configuration_data = cursor.fetchall()
			for key,data in enumerate(consumer_configuration_data):
				if data['configuration_type'] == 2:
					get_catalouge_query = ("""SELECT *
						FROM `catalogs` c
						where `catalog_id` = %s""")
					get_catalouge_data = (data['catalog_id'])
					count_catalouge = cursor.execute(get_catalouge_query,get_catalouge_data)

					if count_catalouge > 0:
						catalouge_data =  cursor.fetchone()
						consumer_configuration_data[key]['catalog_id'] = catalouge_data['catalog_id']
						consumer_configuration_data[key]['catalouge_name'] = catalouge_data['catalog_name']
						if data['display_type'] == 2:
							get_catalouge_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
								p.`product_type`,p.`category_id` as `product_type_id`
								FROM `product` p				
								INNER JOIN `product_catalog_mapping` pcm ON pcm.`product_id` = p.`product_id`
								INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
								WHERE p.`status` = 1 and pcm.`catalog_id` = %s and pom.`product_status` = 1 and pom.`organisation_id` = %s limit 4""")
						if data['display_type'] == 3:
							get_catalouge_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
								p.`product_type`,p.`category_id` as `product_type_id`
								FROM `product` p				
								INNER JOIN `product_catalog_mapping` pcm ON pcm.`product_id` = p.`product_id`
								INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
								WHERE p.`status` = 1 and pcm.`catalog_id` = %s and pom.`product_status` = 1 and pom.`organisation_id` = %s limit 9""")
						if data['display_type'] == 1:
							get_catalouge_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
								p.`product_type`,p.`category_id` as `product_type_id`
								FROM `product` p				
								INNER JOIN `product_catalog_mapping` pcm ON pcm.`product_id` = p.`product_id`
								INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
								WHERE p.`status` = 1 and pcm.`catalog_id` = %s and pom.`product_status` = 1 and pom.`organisation_id` = %s""")
						get_catalouge_product_data = (catalouge_data['catalog_id'],organisation_id)

						cursor.execute(get_catalouge_product_query,get_catalouge_product_data)
						catalouge_product_data = cursor.fetchall()

						for cpkey,cpdata in enumerate(catalouge_product_data):

							get_product_meta = (""" SELECT pm.`product_id`,pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price` FROM `product_meta` pm WHERE 
								`out_price` =  ( SELECT MIN(`out_price`) FROM product_meta  where product_id = %s) and product_id= %s """)
							get_product_meta_data = (cpdata['product_id'],cpdata['product_id'])
							count_product_meta = cursor.execute(get_product_meta,get_product_meta_data)				

							if count_product_meta > 0:
								product_meta_data = cursor.fetchone()

								catalouge_product_data[cpkey]['product_meta_id'] = product_meta_data['product_meta_id']
								catalouge_product_data[cpkey]['product_meta_code'] = product_meta_data['product_meta_code']
								catalouge_product_data[cpkey]['meta_key_text'] = product_meta_data['meta_key_text']
								catalouge_product_data[cpkey]['in_price'] = product_meta_data['in_price']

								get_out_price_query = (""" SELECT `out_price` FROM `product_meta_out_price` where `organisation_id` = %s and `status` = 1 and `product_meta_id` = %s""")
								get_out_price_data = (organisation_id, product_meta_data['product_meta_id'])
								count_out_price_data = cursor.execute(get_out_price_query,get_out_price_data)
								if count_out_price_data >0:
									out_price_data = cursor.fetchone()
									catalouge_product_data[cpkey]['out_price'] = out_price_data['out_price']
								else:
									catalouge_product_data[cpkey]['out_price'] = product_meta_data['out_price']								

								a_string = cpdata['meta_key_text']
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

									catalouge_product_data[cpkey]['met_key_value'] = met_key
									

								image_a = []	
								get_query_images = ("""SELECT `image`,`image_type`
												FROM `product_meta_images` WHERE `product_meta_id` = %s ORDER BY default_image_flag DESC""")
								getdata_images = (product_meta_data['product_meta_id'])
								cursor.execute(get_query_images,getdata_images)
								images = cursor.fetchall()

								for image in images:
									image_a.append({"image":image['image'],"image_type":image['image_type']})						

								if not image_a:
									if organisation_id == 93:
										catalouge_product_data[cpkey]['images'] = [{"image":"https://d1o7xhcyswcoe3.cloudfront.net/1/placeholderAMMobile.png","image_type":1}]
										
									else:
										catalouge_product_data[cpkey]['images'] = [{"image":"https://d1o7xhcyswcoe3.cloudfront.net/32/placeholderOthers.png","image_type":1}]
								else:
									catalouge_product_data[cpkey]['images'] = image_a

								product_meta_offer_mapping_query = (""" SELECT *
												FROM `product_meta_offer_mapping` pmom
												INNER JOIN `offer` o ON o.`offer_id` = pmom.`offer_id` 
												where  pmom.`organisation_id` = %s and `product_id` = %s and `product_meta_id` = %s""")
								product_meta_offer_mapping_data = (organisation_id,cpdata['product_id'],product_meta_data['product_meta_id'])
								count_product_meta_offer_mapping_data = cursor.execute(product_meta_offer_mapping_query,product_meta_offer_mapping_data)

								if count_product_meta_offer_mapping_data > 0:
									product_meta_offer_data = cursor.fetchone()

									catalouge_product_data[cpkey]['absolute_price'] = product_meta_offer_data['absolute_price']
									catalouge_product_data[cpkey]['is_online'] =  product_meta_offer_data['is_online']
									catalouge_product_data[cpkey]['discount_percentage'] = product_meta_offer_data['discount_percentage']
									catalouge_product_data[cpkey]['discount_value'] = product_meta_offer_data['discount_value']
									catalouge_product_data[cpkey]['coupon_code'] = product_meta_offer_data['coupon_code']
									catalouge_product_data[cpkey]['instruction'] = product_meta_offer_data['instruction']
									catalouge_product_data[cpkey]['is_product_meta_offer'] = product_meta_offer_data['is_product_meta_offer']
									

								else:
									get_product_offer_query = 	 ("""SELECT *
											FROM `product_offer_mapping` pom
											INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`
											WHERE pom.`product_id` = %s and pom.`organisation_id` = %s""")
									get_product_offer_data = (cpdata['product_id'],organisation_id)
									rows_count_product_offer = cursor.execute(get_product_offer_query,get_product_offer_data)
									if rows_count_product_offer > 0:
										product_offer_data = cursor.fetchone()
										catalouge_product_data[cpkey]['absolute_price'] = product_offer_data['absolute_price']
										catalouge_product_data[cpkey]['is_online'] =  product_offer_data['is_online']
										catalouge_product_data[cpkey]['discount_percentage'] = product_offer_data['discount_percentage']
										catalouge_product_data[cpkey]['discount_value'] = product_offer_data['discount_value']
										catalouge_product_data[cpkey]['coupon_code'] = product_offer_data['coupon_code']
										catalouge_product_data[cpkey]['instruction'] = product_offer_data['instruction']										
									
									else:
										catalouge_product_data[cpkey]['absolute_price'] = 0
										catalouge_product_data[cpkey]['discount_percentage'] = 0
										catalouge_product_data[cpkey]['discount_value'] = 0
										catalouge_product_data[cpkey]['coupon_code'] = ""
										catalouge_product_data[cpkey]['is_online'] = 0
										catalouge_product_data[cpkey]['instruction'] = ""

							consumer_configuration_data[key]['products'] = catalouge_product_data
					else:
						consumer_configuration_data[key]['catalog_id'] = 0
						consumer_configuration_data[key]['catalouge_name'] = ""

				elif data['configuration_type'] == 1:
					get_section =  ("""SELECT sm.`section_id`,sm.`offer_section_name`
						FROM `section_master` sm			 
						WHERE `section_id` = %s """)
					get_section_data = (data['section_id'])
					count_section = cursor.execute(get_section,get_section_data)
					section_data = cursor.fetchone()
					consumer_configuration_data[key]['section_id'] = section_data['section_id']
					consumer_configuration_data[key]['offer_section_name'] = section_data['offer_section_name']

					if count_section > 0:
						if data['display_type'] == 2:
							get_offer_query =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,o.`discount_percentage`,o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`offer_image_type`
								FROM `offer_section_mapping` osm 
								INNER JOIN `offer` o ON o.`offer_id` = osm.`offer_id`			
								WHERE osm.`organisation_id` = %s and o.`language` = %s and osm.`section_id` = %s and o.`status` = 1 and date(o.`validity_date`) >= %s limit 4""")
						if data['display_type'] == 3:
							get_offer_query =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,o.`discount_percentage`,o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`offer_image_type`
								FROM `offer_section_mapping` osm 
								INNER JOIN `offer` o ON o.`offer_id` = osm.`offer_id`			
								WHERE osm.`organisation_id` = %s and o.`language` = %s and osm.`section_id` = %s and o.`status` = 1 and date(o.`validity_date`) >= %s limit 9 """)
						if data['display_type'] == 1:
							get_offer_query =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,o.`discount_percentage`,o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`offer_image_type`
								FROM `offer_section_mapping` osm 
								INNER JOIN `offer` o ON o.`offer_id` = osm.`offer_id`			
								WHERE osm.`organisation_id` = %s and o.`language` = %s and osm.`section_id` = %s and o.`status` = 1 and date(o.`validity_date`) >= %s""")
						get_offer_data = (organisation_id,language,section_data['section_id'],today_date)
						cursor.execute(get_offer_query,get_offer_data)
						print(cursor._last_executed)
						offer_data = cursor.fetchall()

						i = 1
						for pkey,pdata in enumerate(offer_data):	
							print(pdata['offer_id'])			
							offer_data[pkey]['appearence'] = i
							i =i+1

							if pdata['product_offer_type'] == 1:
								get_offer_product_query = ("""SELECT pofm.`product_id`
									FROM `product_offer_mapping` pofm
									INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = pofm.`product_id`
									WHERE pofm.`offer_id` = %s and pom.`organisation_id` = %s and pom.`product_status` = 1""")
								get_offer_product_data = (pdata['offer_id'],organisation_id)
								count_prroduct_offer = cursor.execute(get_offer_product_query,get_offer_product_data)
								if count_prroduct_offer >0:
									product_offer_data = cursor.fetchone()
									offer_data[pkey]['product_id'] = product_offer_data['product_id']

									get_product_meta_query = ("""SELECT `product_meta_id`
									FROM `product_meta` pm
									INNER JOIN `product_organisation_mapping` pom  ON pom.`product_id` = pm.`product_id`
									WHERE pm.`product_id` = %s and pom.`product_status` = 1 and pom.`organisation_id` = %s""")
									get_product_meta_data = (product_offer_data['product_id'],organisation_id)
									count_product_meta_data = cursor.execute(get_product_meta_query,get_product_meta_data)

									if count_product_meta_data > 0:
										product_meta_data = cursor.fetchone()
										offer_data[pkey]['product_meta_id'] = product_meta_data['product_meta_id']
									else:
										offer_data[pkey]['product_meta_id'] = 0
								else:
									offer_data[pkey]['product_id'] = 0
									offer_data[pkey]['product_meta_id'] = 0
							else:
								offer_data[pkey]['product_id'] = 0
								offer_data[pkey]['product_meta_id'] = 0


					consumer_configuration_data[key]['products'] = offer_data

				consumer_configuration_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
			 
		else:
			consumer_configuration_data = []

		get_loyality_query_type_1 = ("""SELECT *
					FROM `loyality_master`			
					WHERE `organisation_id` = %s and `loyality_type` = 1""")

		get_loyality_data_type_1 = (organisation_id)
		count_loyality_query_type_1 = cursor.execute(get_loyality_query_type_1,get_loyality_data_type_1)

		referal_loyalty_data_type_1 = cursor.fetchone()

		get_loyality_query_type_2 = ("""SELECT *
					FROM `loyality_master`			
					WHERE `organisation_id` = %s and `loyality_type` = 2""")

		get_loyality_data_type_2 = (organisation_id)
		count_loyality_query_type_2 = cursor.execute(get_loyality_query_type_2,get_loyality_data_type_2)

		referal_loyalty_data_type_2 = cursor.fetchone()

		if count_loyality_query_type_1 >0 and count_loyality_query_type_2 >0:

			if referal_loyalty_data_type_1['loyality_amount'] == 0 and  referal_loyalty_data_type_2['loyality_amount'] == 0 :
				is_referal = 0
			else:
				is_referal = 1
		else:
			is_referal = 0
				

		if 	organisation_id == 83:

			get_category_query = ("""SELECT `category_id`,`category_name`,`category_image`,`status`
						FROM `category` WHERE `organisation_id` = %s ORDER BY mapping_id ASC""")
		else:
			get_category_query = ("""SELECT `category_id`,`category_name`,`category_image`,`status`
						FROM `category` WHERE `organisation_id` = %s and `status` = 1 ORDER BY mapping_id ASC""")

		get_category_data = (organisation_id)
		category_count = cursor.execute(get_category_query,get_category_data)

		category_data = cursor.fetchall()

		if category_count > 0:
			category = category_data
		else:
			category = []

		if user_id == 0:
			cart_count = 0
			user_data =  {}
			user_data["address_line_1"] = ""
			user_data["address_line_2"] = ""
			user_data["city"] = ""
			user_data["country"] = ""
			user_data["state"] = ""
			user_data["pincode"] = 0
		else:
			get_query_count = ("""SELECT COALESCE(sum(cpmq.`qty`),0) as cart_count 
				FROM `customer_product_mapping` cpm 
				INNER JOIN `customer_product_mapping_qty`cpmq ON cpmq.`customer_mapping_id` = cpm.`mapping_id` 
				WHERE cpm.`customer_id` = %s and cpm.`product_status` = 'c' and cpm.`organisation_id` = %s and cpmq.`organisation_id` = %s""")

			getDataCount = (user_id,organisation_id,organisation_id)
					
			count_product = cursor.execute(get_query_count,getDataCount)

			if count_product > 0:
				cart_count_data = cursor.fetchone()
				cart_count = int(cart_count_data['cart_count'])
			else:
				cart_count = 0

			get_user_details_query = (""" SELECT address_line_1,address_line_2,city,country,state,pincode 
										FROM `admins` WHERE admin_id = %s """)
			get_user_details_data = (user_id)
			count_user_details = cursor.execute(get_user_details_query,get_user_details_data)

			if count_user_details > 0:
				user_data = cursor.fetchone()
			else:
				user_data = {}
				user_data["address_line_1"] = ""
				user_data["address_line_2"] = ""
				user_data["city"] = ""
				user_data["country"] = ""
				user_data["state"] = ""
				user_data["pincode"] = 0

		if category_id > 0:
			get_brand_query = ("""SELECT `brand_id`
			FROM `category_brand_mapping`  WHERE `organisation_id` = %s and `category_id` = %s""")
			get_brand_data = (organisation_id,category_id)

			count_category_brand = cursor.execute(get_brand_query,get_brand_data)

			if count_category_brand > 0:

				brand_data = cursor.fetchall()

				for hkey,hdata in enumerate(brand_data):
					get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
					FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

					getdata_key_value = (hdata['brand_id'])
					cursor.execute(get_key_value_query,getdata_key_value)

					key_value_data = cursor.fetchone()

					brand_data[hkey]['meta_key_value'] = key_value_data['meta_key_value']
					brand_data[hkey]['image'] = key_value_data['image']
			else:
				brand_data = []

			get_budget_query = ("""SELECT *
				FROM `budget` WHERE  `organisation_id` = %s and `category_id` = %s""")		
			get_budget_data = (organisation_id,category_id)
			budget_count = cursor.execute(get_budget_query,get_budget_data)

			if budget_count > 0:
				budget_data = cursor.fetchall()

				for key,data in enumerate(budget_data):
					budget_data[key]['last_update_ts'] = str(data['last_update_ts'])
			else:
				budget_data = []
			
		else:
			brand_data = []
			budget_data = []

		get_query_count = ("""SELECT count(*) as configuration_count
					FROM `consumer_configuration` cc 
					where cc.`organisation_id` = %s and cc.`retailer_store_store_id` = %s and cc.`category_id` = %s ORDER BY sequence asc""")

		get_data_count = (organisation_id,retailer_store_store_id,category_id)
		cursor.execute(get_query_count,get_data_count)

		data_count = cursor.fetchone()

		page_count = math.trunc(data_count['configuration_count']/5)

		if page_count == 0:
			page_count =1
		else:
			if page_count == 1:
				page_count = 1
			else:
				page_count = page_count + 1	

		return ({"attributes": {
				    		"status_desc": "consumer_configuration",
				    		"status": "success",
				    		"is_referal":is_referal,
				    		"category":category,
				    		"cart_count":cart_count,
				    		"address":user_data,
				    		"brand_data":brand_data,
				    		"budget_data":budget_data,
				    		"page_count":page_count,
		    				"page":page
				    	},
				    	"responseList":consumer_configuration_data}), status.HTTP_200_OK

#----------------------Consumer-Dashboard---------------------#
