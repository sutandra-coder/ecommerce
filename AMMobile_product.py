from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json,render_template
from flask_api import status
from jinja2 import Environment, FileSystemLoader
from datetime import datetime,timedelta,date
import pymysql
from smtplib import SMTP
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
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
from datetime import datetime
import boto3
from botocore.config import Config
import csv
import re
from decimal import Decimal

AMMobile_product = Blueprint('AMMobile_product_api', __name__)
api = Api(AMMobile_product,  title='AM Mobile Product',description='AM Mobile Product API')
name_space = api.namespace('AMMobileProduct',description='AM Mobile Product')

#----------------------database-connection---------------------#

def mysql_connection():
	connection = pymysql.connect(host='ammobileproduct.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='EKr3RnhsAssFw78a91N5',
	                             db='AMMobileProduct',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def mysql_connection_ecommerce():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

'''def mysql_connection_ecommerce():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection'''

#----------------------database-connection---------------------#

user_postmodel = api.model('SelectUser', {	
	"user_name":fields.String,
	"phoneno":fields.String,
	"password":fields.String
})

user_login_postmodel = api.model('SelectUserLogin', {	
	"phoneno":fields.String,
	"password":fields.String
})

UploadingTrack_postmodel = api.model('UploadingTrack', {	
	"uploading_file_name":fields.String,
	"last_update_id":fields.Integer
})

Product_Name_postmodel = api.model('ProductNamepostmodel', {	
	"product_name":fields.String,
	"color":fields.String,
	"brand":fields.String,
	"rate":fields.Integer,
	"qty":fields.Integer
})



#----------------------Add-User---------------------#

@name_space.route("/AddUser")
class AddUser(Resource):
	@api.expect(user_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		user_name = details['user_name']
		phoneno = details['phoneno']
		password = details['password']

		insert_query = ("""INSERT INTO `user`(`user_name`,`phoneno`,`password`) 
								VALUES(%s,%s,%s)""")
		data = (user_name,phoneno,password)
		cursor.execute(insert_query,data)
		print(cursor._last_executed)
		user_id = cursor.lastrowid	

		details['user_id'] = user_id

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "user_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK	

#----------------------Add-User---------------------#

#----------------------Login-User---------------------#

@name_space.route("/LoginUser")	
class LoginUser(Resource):
	@api.expect(user_login_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `user` WHERE `phoneno` = %s and `password` = %s""")
		getData = (details['phoneno'],details['password'])
		count_user = cursor.execute(get_query,getData)

		if count_user > 0:
			user_details = cursor.fetchone()
			user_details['last_update_ts'] = str(user_details['last_update_ts'])
		else:
			user_details = {}

		return ({"attributes": {
				    "status_desc": "user_details",
				    "status": "success"
				},
				"responseList":user_details}), status.HTTP_200_OK

#----------------------Login-User---------------------#

#----------------------Uploading-Track---------------------#

@name_space.route("/UploadingTrack")
class UploadingTrack(Resource):
	@api.expect(UploadingTrack_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		uploading_file_name = details['uploading_file_name']
		last_update_id  = details['last_update_id']
		
		insert_query = ("""INSERT INTO `uploading_track`(`uploading_file_name`,`last_update_id`) 
								VALUES(%s,%s)""")
		data = (uploading_file_name,last_update_id)
		cursor.execute(insert_query,data)
		print(cursor._last_executed)
		request_no  = cursor.lastrowid	

		details['request_no'] = request_no

		connection.commit()
		cursor.close()


		return ({"attributes": {
				    "status_desc": "track_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Uploading-Track---------------------#


@name_space.route("/getProductNameAndMeta")
class getProductNameAndMeta(Resource):
	@api.expect(Product_Name_postmodel)
	def post(self):
		connection = mysql_connection_ecommerce()
		cursor = connection.cursor()

		details = request.get_json()

		get_product_name = details['product_name']
		color = details['color']
		brand = details['brand']
		rate = details['rate']
		qty = details['qty']

		print(color)



		product = {}

		if brand == 'Apple':
			try:
				brand_id = 11			
				if "iPad" in get_product_name or "Ipad" in get_product_name or "IPAD" in get_product_name or "IPad" in get_product_name:
					print('hi')
					product['ecommerce_product_meta_id'] = 0
					product['meta_key_text'] = ''
					product['ecommerce_product_name'] = ''
					product['ecommerce_product_id'] = 0
				else:
					print('hello')
					get_product_name = get_product_name.rstrip()
					new_product_name = get_product_name.replace("Handsets ", "", 1)
					new_product_name_split = get_product_name.split(' ')	
					storage = new_product_name_split[-1]
					if len(storage) > 2:
						new_storage = re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + " ", storage)
						product_name = new_product_name.replace(storage, "",1).rstrip()
						
					else:
						new_storage = new_product_name_split[-2]+ " "+new_product_name_split[-1]

						if (new_storage.find('-') != -1):
							new_storage_split = new_storage.split('-')
							new_storage = new_storage_split[1]
						else:
							new_storage = new_storage						
							print(new_storage)

						product_name = new_product_name.replace(new_storage, "",1).rstrip()

					print(product_name)
					print(new_storage)

					get_storage_query = ("""SELECT `meta_key_value_id`,`meta_key_value`
							FROM `meta_key_value_master` WHERE `meta_key_value` = %s and `organisation_id` = 1""")
					get_storage_data = (new_storage)
					get_storage_count = cursor.execute(get_storage_query,get_storage_data)

					if get_storage_count > 0:
						storage_data =  cursor.fetchone()
						storage_id = storage_data['meta_key_value_id']
					else:
						storage_id = ''

					print(storage_id)

					get_color_query = ("""SELECT `meta_key_value_id`,`meta_key_value`
							FROM `meta_key_value_master` WHERE `meta_key_value` like %s and `organisation_id` = 1""")
					get_color_data = (color)
					get_color_count = cursor.execute(get_color_query,get_color_data)

					if get_color_count > 0:
						color_data = cursor.fetchone()
						color_id = color_data['meta_key_value_id']
					else:
						meta_key_value_image = ''
						meta_key_id = 5
						meta_key_value = color
						meta_key_value_status = 1
						organisation_id = 1
						last_update_id = 1

						insert_color_query = ("""INSERT INTO `meta_key_value_master`(`meta_key_id`,`meta_key_value`,`image`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s)""")
						insert_color_data = (meta_key_id,meta_key_value,meta_key_value_image,meta_key_value_status,organisation_id,last_update_id)
						cursor.execute(insert_color_query,insert_color_data)
						color_id = cursor.lastrowid

					'''if storage_id != '' and color_id != '':
						meta_key_text = str(storage_id)+','+str(color_id)
					elif color_id == '' and storage_id != '':
						meta_key_text = storage_id
					elif storage_id == '' and color_id != '':
						meta_key_text = color_id'''

					meta_key_text = str(storage_id)+','+str(color_id)

					print(meta_key_text)

					get_product_query = ("""SELECT `product_id`,`product_name`
							FROM `product` WHERE `product_name` like %s and `organisation_id` = 1 and status = 1""")
					get_product_data = (product_name)
					get_product_count = cursor.execute(get_product_query,get_product_data)
					print(cursor._last_executed)

					if get_product_count > 0:
						product_data = cursor.fetchone()
						get_product_meta_query = ("""SELECT `product_meta_id`,`meta_key_text`
							FROM `product_meta` WHERE `product_id` = %s and `meta_key_text` = %s and `organisation_id` = 1""")
						get_product_meta_data = (product_data['product_id'],meta_key_text)
						get_product_meta_count = cursor.execute(get_product_meta_query,get_product_meta_data)

						if get_product_meta_count > 0:
							product_meta_data = cursor.fetchone()
							product['ecommerce_product_meta_id'] = product_meta_data['product_meta_id']
							product['meta_key_text'] = product_meta_data['meta_key_text']					
						else:
							get_product_meta_query = ("""SELECT `product_meta_id`,`product_meta_code`
								FROM `product_meta` WHERE `product_id` = %s and `organisation_id` = 1 order by `product_meta_code` desc""")
							get_product_meta_data = (product_data['product_id'])
							product_meta_count = cursor.execute(get_product_meta_query,get_product_meta_data)

							if product_meta_count > 0:
								print(cursor._last_executed)
								product_meta_data = cursor.fetchone()
								product_meta_code = product_meta_data['product_meta_code']
								new_product_meta_code = product_meta_code + str(1)
							else:
								new_product_meta_code = 1

							product_price = rate/qty
							product_meta_status = 1
							organisation_id = 1
							last_update_id = 1
							other_specification_json = 0
							loyalty_points = 0
							zoho_product_meta_id = 0

							insert_product_meta_query = ("""INSERT INTO `product_meta`(`product_id`,`product_meta_code`,`meta_key_text`,`other_specification_json`,`in_price`,`out_price`,`loyalty_points`,`zoho_product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")							
				
							insert_product_meta_data = (product_data['product_id'],new_product_meta_code,meta_key_text,other_specification_json,product_price,product_price,loyalty_points,zoho_product_meta_id,product_meta_status,organisation_id,last_update_id)	
							cursor.execute(insert_product_meta_query,insert_product_meta_data)	

							product_meta_id = cursor.lastrowid
							default_image_flag = 1
							is_gallery = 0
							image_type = 1
							product_meta_image_status = 1

							image = "https://d1lwvo1ffrod0a.cloudfront.net/28/iphone_default.jpeg"
							insert_product_meta_images_query_1 = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`is_gallery`,`image_type`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
							insert_product_meta_images_data_1 = (product_meta_id,image,default_image_flag,is_gallery,image_type,product_meta_image_status,organisation_id,last_update_id)	
							cursor.execute(insert_product_meta_images_query_1,insert_product_meta_images_data_1)

							is_gallery = 1
							default_image_flag = 0
							insert_product_meta_images_query_2 = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`is_gallery`,`image_type`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
							insert_product_meta_images_data_2 = (product_meta_id,image,default_image_flag,is_gallery,image_type,product_meta_image_status,organisation_id,last_update_id)	
							cursor.execute(insert_product_meta_images_query_2,insert_product_meta_images_data_2)

							
							product['ecommerce_product_meta_id'] = product_meta_id
							product['meta_key_text'] = meta_key_text

						product['ecommerce_product_name'] = product_data['product_name']
						product['ecommerce_product_id'] = product_data['product_id']
						
					else:
						category_id = 6
						product_name = product_name
						product_long_description = product_name
						product_short_description = product_name
						product_type = 'Smart Phone'
						product_status = 1
						organisation_id = 1
						last_update_id = 1

						insert_product_query = ("""INSERT INTO `product`(`product_name`,`product_long_description`,`product_short_description`,`category_id`,`product_type`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
						insert_product_data = (product_name,product_long_description,product_short_description,category_id,product_type,product_status,organisation_id,last_update_id)
						cursor.execute(insert_product_query,insert_product_data)

						product_id = cursor.lastrowid

						organisation_mapping_organisation_id = 93
						product_status = 1

						insert_product_organisation_mapping_query = ("""INSERT INTO `product_organisation_mapping`(`product_id`,`organisation_id`,`product_status`,`last_update_id`) 
							VALUES(%s,%s,%s,%s)""")
						insert_product_organisation_mapping_data = (product_id,organisation_mapping_organisation_id,product_status,organisation_mapping_organisation_id)
						cursor.execute(insert_product_organisation_mapping_query,insert_product_organisation_mapping_data)

						print(cursor._last_executed)

						prodct_brand_mapping_status = 1

						insert_product_brand_mapping_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s)""")
						insert_product_brand_mapping_data = (brand_id,product_id,prodct_brand_mapping_status,organisation_id,last_update_id)
						cursor.execute(insert_product_brand_mapping_query,insert_product_brand_mapping_data)

						insert_product_organisation_brand_mapping_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s)""")
						insert_product_organisation_brand_mapping_data = (brand_id,product_id,prodct_brand_mapping_status,organisation_mapping_organisation_id,organisation_mapping_organisation_id)
						cursor.execute(insert_product_organisation_brand_mapping_query,insert_product_organisation_brand_mapping_data)

						new_product_meta_code = 1

						product_price = rate/qty
						product_meta_status = 1
						organisation_id = 1
						last_update_id = 1
						other_specification_json = 0
						loyalty_points = 0
						zoho_product_meta_id = 0

						insert_product_meta_query = ("""INSERT INTO `product_meta`(`product_id`,`product_meta_code`,`meta_key_text`,`other_specification_json`,`in_price`,`out_price`,`loyalty_points`,`zoho_product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")							
				
						insert_product_meta_data = (product_id,new_product_meta_code,meta_key_text,other_specification_json,product_price,product_price,loyalty_points,zoho_product_meta_id,product_meta_status,organisation_id,last_update_id)	
						cursor.execute(insert_product_meta_query,insert_product_meta_data)	

						product_meta_id = cursor.lastrowid
						default_image_flag = 1
						is_gallery = 0
						image_type = 1
						product_meta_image_status = 1

						image = "https://d1lwvo1ffrod0a.cloudfront.net/28/iphone_default.jpeg"
						insert_product_meta_images_query_1 = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`is_gallery`,`image_type`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
						insert_product_meta_images_data_1 = (product_meta_id,image,default_image_flag,is_gallery,image_type,product_meta_image_status,organisation_id,last_update_id)	
						cursor.execute(insert_product_meta_images_query_1,insert_product_meta_images_data_1)

						is_gallery = 1
						default_image_flag = 0
						insert_product_meta_images_query_2 = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`is_gallery`,`image_type`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
						insert_product_meta_images_data_2 = (product_meta_id,image,default_image_flag,is_gallery,image_type,product_meta_image_status,organisation_id,last_update_id)	
						cursor.execute(insert_product_meta_images_query_2,insert_product_meta_images_data_2)
							
						product['ecommerce_product_meta_id'] = product_meta_id
						product['meta_key_text'] = meta_key_text


						product['ecommerce_product_name'] = product_name
						product['product_id'] = product_id
			except:
				product_id = 1511
				get_product_meta_query = ("""SELECT `product_meta_id`,`product_meta_code`
								FROM `product_meta` WHERE `product_id` = %s and `organisation_id` = 1 order by `product_meta_code` desc""")
				get_product_meta_data = (product_id)
				product_meta_count = cursor.execute(get_product_meta_query,get_product_meta_data)
				product_meta_data = cursor.fetchone()
				product['ecommerce_product_meta_id'] = product_meta_data['product_meta_id']
				product['meta_key_text'] = ''
				product['ecommerce_product_name'] = 'Other Product'
				product['product_id'] = 1511

			connection.commit()
			cursor.close()				


		return ({"attributes": {
				    "status_desc": "product_details",
				    "status": "success"
				},
				"responseList":product}), status.HTTP_200_OK





