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

AMMobile_product_samsung = Blueprint('AMMobile_product_samsung_api', __name__)
api = Api(AMMobile_product_samsung,  title='AM Mobile Product Samsung',description='AM Mobile Product Samsung API')
name_space = api.namespace('AMMobileProductVivo',description='AM Mobile Product Samsung')

#----------------------database-connection---------------------#

def mysql_connection_ecommerce():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

Product_Name_postmodel = api.model('ProductNamepostmodel', {	
	"product_name":fields.String,
	"color":fields.String,
	"brand":fields.String,
	"rate":fields.Integer,
	"qty":fields.Integer
})

@name_space.route("/getProductNameAndMeta")
class getProductNameAndMeta(Resource):
	@api.expect(Product_Name_postmodel)
	def post(self):
		connection = mysql_connection_ecommerce()
		cursor = connection.cursor()

		details = request.get_json()
		get_product_name = details['product_name']
		brand = details['brand']
		color =  details['color']
		rate = details['rate']
		qty = details['qty']

		new_product_name = ""

		product = {}

		if brand == 'Samsung':
			try:
				brand_id = 8
				get_product_name = get_product_name.replace("(J2 2018)", " ", 1)
				get_product_name = get_product_name.replace("(New)", "", 1).rstrip()

				if "(" in get_product_name:
					product_name_split_for_storage_ram = get_product_name.split(' ')
					storage_ram_string = product_name_split_for_storage_ram[-1]
					final_product_name = get_product_name.replace(storage_ram_string, "",1).rstrip()
					storage_ram_string = re.findall(r'\(.*?\)', get_product_name)						
					storage_ram_string_split = str(storage_ram_string).split('+')
					ram = storage_ram_string_split[0].replace("['(", "", 1)
					storage = storage_ram_string_split[1].replace(")']", "", 1)		
					storage = re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + "", storage)
					ram = ram+" GB"
					product_name = final_product_name					
				else:				
					product_name_split_for_storage_ram = get_product_name.split(' ')
					storage_ram_string = product_name_split_for_storage_ram[-1]
					final_product_name = get_product_name.replace(storage_ram_string, "",1).rstrip()
					storage_ram_string_split = storage_ram_string.split('+')
					ram = storage_ram_string_split[0]
					storage = storage_ram_string_split[1]

					ram = ram+" GB"
					storage =  re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + "", storage)
					color = color
					product_name = final_product_name

				get_storage_query = ("""SELECT `meta_key_value_id`,`meta_key_value`
						FROM `meta_key_value_master` WHERE `meta_key_value` = %s and `organisation_id` = 1 and `meta_key_id` = 3""")
				get_storage_data = (storage)
				get_storage_count = cursor.execute(get_storage_query,get_storage_data)

				if get_storage_count > 0:
					storage_data =  cursor.fetchone()
					storage_id = storage_data['meta_key_value_id']
				else:
					meta_key_value_image = ''
					meta_key_id = 3
					meta_key_value = storage
					meta_key_value_status = 1
					organisation_id = 1
					last_update_id = 1

					insert_ram_query = ("""INSERT INTO `meta_key_value_master`(`meta_key_id`,`meta_key_value`,`image`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s)""")
					insert_color_data = (meta_key_id,meta_key_value,meta_key_value_image,meta_key_value_status,organisation_id,last_update_id)
					cursor.execute(insert_color_query,insert_color_data)
					ram_id = cursor.lastrowid				

				get_color_query = ("""SELECT `meta_key_value_id`,`meta_key_value`
						FROM `meta_key_value_master` WHERE `meta_key_value` like %s and `organisation_id` = 1  and `meta_key_id` = 5""")
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

				get_ram_query = ("""SELECT `meta_key_value_id`,`meta_key_value`
						FROM `meta_key_value_master` WHERE `meta_key_value` = %s and `organisation_id` = 1 and `meta_key_id` = 4""")
				get_ram_data = (ram)
				get_ram_count = cursor.execute(get_storage_query,get_storage_data)

				if get_ram_count > 0:
					ram_data =  cursor.fetchone()
					ram_id = ram_data['meta_key_value_id']
				else:
					meta_key_value_image = ''
					meta_key_id = 4
					meta_key_value = ram
					meta_key_value_status = 1
					organisation_id = 1
					last_update_id = 1

					insert_ram_query = ("""INSERT INTO `meta_key_value_master`(`meta_key_id`,`meta_key_value`,`image`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s)""")
					insert_color_data = (meta_key_id,meta_key_value,meta_key_value_image,meta_key_value_status,organisation_id,last_update_id)
					cursor.execute(insert_color_query,insert_color_data)
					ram_id = cursor.lastrowid

				meta_key_text = str(storage_id)+','+str(color_id)+','+str(ram_id)

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

						image = "https://d1lwvo1ffrod0a.cloudfront.net/28/vivo_default.jpeg"
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

					image = "https://d1lwvo1ffrod0a.cloudfront.net/28/vivo_default.jpeg"
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
				product_id = 1583
				get_product_meta_query = ("""SELECT `product_meta_id`,`product_meta_code`
							FROM `product_meta` WHERE `product_id` = %s and `organisation_id` = 1 order by `product_meta_code` desc""")
				get_product_meta_data = (product_id)
				product_meta_count = cursor.execute(get_product_meta_query,get_product_meta_data)
				product_meta_data = cursor.fetchone()
				product['ecommerce_product_meta_id'] = product_meta_data['product_meta_id']
				product['meta_key_text'] = ''
				product['ecommerce_product_name'] = 'Other Product'
				product['product_id'] = 1583

			connection.commit()
			cursor.close()	


		return ({"attributes": {
				    "status_desc": "product_details",
				    "status": "success"
				},
				"responseList":product}), status.HTTP_200_OK
