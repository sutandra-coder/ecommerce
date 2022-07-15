from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import datetime
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
from pyfcm import FCMNotification
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

retailer_customer_notification = Blueprint('retailer_customer_notification', __name__)
api = Api(retailer_customer_notification, version='1.0', title='Ecommerce API',
    description='Ecommerce API')

name_space = api.namespace('EcommerceNotification',description='Ecommerce Notification')

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#-----------------------------------------------------------------#
appmsg_model = api.model('appmsg_model', {
	"user_id": fields.Integer()
	})

appmsgmodel = api.model('appmsgmodel', {
	"title": fields.String(),
	"msg": fields.String(),
	"img": fields.String(),
	"sdate": fields.String(),
	"pincode": fields.Integer(),
	"model": fields.String(),
	"brand": fields.String(),
	"pcost": fields.String(),
	"organisation_id": fields.Integer(),
	"appmsg_model":fields.List(fields.Nested(appmsg_model))
	})

notification_putmodel = api.model('notification_putmodel', {
	"is_read": fields.Integer(),
})

#----------------------------------------------------#
@name_space.route("/CustomerSearchingByPhoneNoOrName/<string:searchkey>/<int:organisation_id>")	
class CustomerSearchingByPhoneNoOrName(Resource):
	def get(self,searchkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today() 

		def check_user_input(searchkey):
		    try:
		        val = int(searchkey)
		        val = 'integer'
		    except ValueError:
		        val = 'string'

		    return val
		if check_user_input(searchkey) == 'string':
			if len(searchkey.split(" ")) < 2:				
				firstname = searchkey

				cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as
					name,concat('address line1-',`address_line_1`,',','address line2-',
					`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,profile_image,organisation_id,`pincode`,date_of_creation,loggedin_status,wallet FROM `admins` 
					WHERE locate(%s,`first_name`) and `role_id`=4 and 
					`status`=1 and `organisation_id`=%s""",(firstname,organisation_id))

				customerdata = cursor.fetchall()
				
				if customerdata:
					for i in range(len(customerdata)):
						customerdata[i]['dob'] = customerdata[i]['dob']
						customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

						customerdata[i]['outstanding'] = 0

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							customerdata[i]['customertype'] = customertype['customer_type']
						else:
							customerdata[i]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (customerdata[i]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customerdata[i]['retailer_city'] = city_data['retailer_city']
							customerdata[i]['retailer_address'] = city_data['retailer_address']
						else:
							customerdata[i]['retailer_city'] = ""
							customerdata[i]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customerdata[i]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customerdata[i]['enquiery_count'] = 0
				
				else:
					cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as
						name,concat('address line1-',`address_line_1`,',','address line2-',
						`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,profile_image,organisation_id,`pincode`,date_of_creation,loggedin_status,wallet FROM `admins` 
						WHERE locate(%s,`last_name`) and `role_id`=4 and 
						`status`=1 and `organisation_id`=%s""",(firstname,organisation_id))

					customerdata = cursor.fetchall()
					
					if customerdata:
						for i in range(len(customerdata)):
							customerdata[i]['dob'] = customerdata[i]['dob']
							customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

							customerdata[i]['outstanding'] = 0

							cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
							customertype = cursor.fetchone()
							if customertype:
								customerdata[i]['customertype'] = customertype['customer_type']
							else:
								customerdata[i]['customertype'] = ''

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (customerdata[i]['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customerdata[i]['retailer_city'] = city_data['retailer_city']
								customerdata[i]['retailer_address'] = city_data['retailer_address']
							else:
								customerdata[i]['retailer_city'] = ""
								customerdata[i]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customerdata[i]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customerdata[i]['enquiery_count'] = 0
							
			else:
				name = searchkey.split(" ", 1)
				firstname = name[0]
				lastname = name[1]

				cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as
					name,concat('address line1-',`address_line_1`,',','address line2-',
					`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,profile_image,organisation_id,`pincode`,date_of_creation,loggedin_status,wallet FROM `admins` 
					WHERE locate(%s,`first_name`) and locate(%s,`last_name`) and 
					`role_id`=4 and `status`=1 and `organisation_id`=%s""",
					(firstname,lastname,organisation_id))

				customerdata = cursor.fetchall()
				
				for i in range(len(customerdata)):
					customerdata[i]['dob'] = customerdata[i]['dob']
					customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

					customerdata[i]['outstanding'] = 0

					cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						customerdata[i]['customertype'] = customertype['customer_type']
					else:
						customerdata[i]['customertype'] = ''

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (customerdata[i]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						customerdata[i]['retailer_city'] = city_data['retailer_city']
						customerdata[i]['retailer_address'] = city_data['retailer_address']
					else:
						customerdata[i]['retailer_city'] = ""
						customerdata[i]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						customerdata[i]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						customerdata[i]['enquiery_count'] = 0
		
		else:
			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,organisation_id,`pincode`,date_of_creation,loggedin_status,wallet FROM `admins` 
				WHERE locate(%s,`phoneno`) and `role_id`=4 and `status`=1 and 
				`organisation_id`=%s""",(searchkey,organisation_id))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

				cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0
							
		
		return ({"attributes": {
		    		"status_desc": "Customer Searching Details",
		    		"status": "success"
		    	},
		    	"responseList":customerdata}), status.HTTP_200_OK

#----------------------------------------------------------------#
@name_space.route("/sendAppPushNotifications")
class sendAppPushNotifications(Resource):
	@api.expect(appmsgmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		selectedUsers = details.get('appmsg_model')
		title = details.get('title')
		msg = details.get('msg')
		img = details.get('img')
		sdate = details.get('sdate')
		pincode = details.get('pincode')
		model = details.get('model')
		brand = details.get('brand')
		pcost = details.get('pcost')
		organisation_id = details.get('organisation_id')
		
		if selectedUsers != None:
			
			selected = selectedUsers
			for sd in selected:
				user_id = sd['user_id']
				# print(user_id)
				cursor.execute("""SELECT * FROM `devices` WHERE `user_id`=%s and 
					organisation_id=%s""",(user_id,organisation_id))
				deviceDtls = cursor.fetchone()
				if deviceDtls == None:
					sent = "Not found user device token"
				else:
					device_id = deviceDtls['device_token']
					# print(device_id)
					cursor.execute("""SELECT * FROM `organisation_firebase_details` 
						where `organisation_id`=%s""",(organisation_id))
					firebaseDtls = cursor.fetchone()
					if firebaseDtls == None:
						sent = "Not found firebase key"
					else:
						api_key = firebaseDtls['firebase_key']

					data_message = {
									"title" : title,
									"message": msg,
									"image-url":img
									}
					
					push_service = FCMNotification(api_key=api_key)
					msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
					sent = 'No'
					if msgResponse.get('success') == 1:
						sent = 'Yes'
						
						app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
							image,`U_id`,`Device_ID`,`Sent`,`organisation_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s)""")
						insert_data = (title,msg,img,user_id,device_id,sent,organisation_id)
						appdata = cursor.execute(app_query,insert_data)
						

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and selectedUsers == None:
			
			cursor.execute("""SELECT `admin_id` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and `organisation_id`=%s and `date_of_creation` 
				between %s and %s""",(organisation_id,sdate,today))

			customerdata = cursor.fetchall()
			for i in range(len(customerdata)):
				user_id = customerdata[i]['admin_id']
				cursor.execute("""SELECT * FROM `devices` WHERE `user_id`=%s and 
					organisation_id=%s""",(user_id,organisation_id))
				deviceDtls = cursor.fetchone()
				if deviceDtls == None:
					sent = "Not found user device token"
				else:
					device_id = deviceDtls['device_token']

					cursor.execute("""SELECT * FROM `organisation_firebase_details` 
						where `organisation_id`=%s""",(organisation_id))
					firebaseDtls = cursor.fetchone()
					if firebaseDtls == None:
						sent = "Not found firebase key"
					else:
						api_key = firebaseDtls['firebase_key']

					data_message = {
									"title" : title,
									"message": msg,
									"image-url":img
									}
					
					push_service = FCMNotification(api_key=api_key)
					msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
					sent = 'No'
					if msgResponse.get('success') == 1:
						sent = 'Yes'
						
						app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
							image,`U_id`,`Device_ID`,`Sent`,`organisation_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s)""")
						insert_data = (title,msg,img,user_id,device_id,sent,organisation_id)
						appdata = cursor.execute(app_query,insert_data)
						
		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and selectedUsers == None:
			cursor.execute("""SELECT `admin_id` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and `organisation_id`=%s and 
				`date_of_creation` between %s and %s  and `pincode`=%s""",
			(organisation_id,sdate,today,pincode))

			customerdata = cursor.fetchall()
			for i in range(len(customerdata)):
				user_id = customerdata[i]['admin_id']
				cursor.execute("""SELECT * FROM `devices` WHERE `user_id`=%s and 
					organisation_id=%s""",(user_id,organisation_id))
				deviceDtls = cursor.fetchone()
				if deviceDtls == None:
					sent = "Not found user device token"
				else:
					device_id = deviceDtls['device_token']

					cursor.execute("""SELECT * FROM `organisation_firebase_details` 
						where `organisation_id`=%s""",(organisation_id))
					firebaseDtls = cursor.fetchone()
					if firebaseDtls == None:
						sent = "Not found firebase key"
					else:
						api_key = firebaseDtls['firebase_key']

					data_message = {
									"title" : title,
									"message": msg,
									"image-url":img
									}
					
					push_service = FCMNotification(api_key=api_key)
					msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
					sent = 'No'

					if msgResponse.get('success') == 1:
						sent = 'Yes'
						
						app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
							image,`U_id`,`Device_ID`,`Sent`,`organisation_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s)""")
						insert_data = (title,msg,img,user_id,device_id,sent,organisation_id)
						appdata = cursor.execute(app_query,insert_data)
						
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and selectedUsers == None:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,organisation_id,sdate,today,limit))

			customerdata = cursor.fetchall()
			for i in range(len(customerdata)):
				user_id = customerdata[i]['admin_id']
				cursor.execute("""SELECT * FROM `devices` WHERE `user_id`=%s and 
					organisation_id=%s""",(user_id,organisation_id))
				deviceDtls = cursor.fetchone()
				if deviceDtls == None:
					sent = "Not found user device token"
				else:
					device_id = deviceDtls['device_token']

					cursor.execute("""SELECT * FROM `organisation_firebase_details` 
						where `organisation_id`=%s""",(organisation_id))
					firebaseDtls = cursor.fetchone()
					if firebaseDtls == None:
						sent = "Not found firebase key"
					else:
						api_key = firebaseDtls['firebase_key']

					data_message = {
									"title" : title,
									"message": msg,
									"image-url":img
									}
					
					push_service = FCMNotification(api_key=api_key)
					msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
					sent = 'No'
					if msgResponse.get('success') == 1:
						sent = 'Yes'
						
						app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
							image,`U_id`,`Device_ID`,`Sent`,`organisation_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s)""")
						insert_data = (title,msg,img,user_id,device_id,sent,organisation_id)
						appdata = cursor.execute(app_query,insert_data)
						
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s""",
				(brand,organisation_id,model,organisation_id,sdate,today))

			customerdata = cursor.fetchall()
			for i in range(len(customerdata)):
				user_id = customerdata[i]['admin_id']
				cursor.execute("""SELECT * FROM `devices` WHERE `user_id`=%s and 
					organisation_id=%s""",(user_id,organisation_id))
				deviceDtls = cursor.fetchone()
				if deviceDtls == None:
					sent = "Not found user device token"
				else:
					device_id = deviceDtls['device_token']

					cursor.execute("""SELECT * FROM `organisation_firebase_details` 
						where `organisation_id`=%s""",(organisation_id))
					firebaseDtls = cursor.fetchone()
					if firebaseDtls == None:
						sent = "Not found firebase key"
					else:
						api_key = firebaseDtls['firebase_key']

					data_message = {
									"title" : title,
									"message": msg,
									"image-url":img
									}
					
					push_service = FCMNotification(api_key=api_key)
					msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
					sent = 'No'
					if msgResponse.get('success') == 1:
						sent = 'Yes'
						
						app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
							image,`U_id`,`Device_ID`,`Sent`,`organisation_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s)""")
						insert_data = (title,msg,img,user_id,device_id,sent,organisation_id)
						appdata = cursor.execute(app_query,insert_data)
						
		
		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and selectedUsers == None:
			pcostrange = pcost.split("-", 1)
			startingcost = pcostrange[0]
			endingcost = pcostrange[1]

			cursor.execute("""SELECT admin_id FROM `admins`
				WHERE `organisation_id`=%s and `date_of_creation` between %s and %s""",
				(organisation_id,sdate,today))
			userDtls = cursor.fetchall()
			for i in range(len(userDtls)):
				
				cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
					WHERE user_id=%s and `organisation_id` =%s and 
					`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
				costDtls = cursor.fetchone()
				total = costDtls['total']
				if total == None:
					total = 0
				scost = float(startingcost)
				ecost = float(endingcost)
				if scost <= total <= ecost:
					user_id = userDtls[i]['admin_id']			
					cursor.execute("""SELECT * FROM `devices` WHERE `user_id`=%s and 
						organisation_id=%s""",(user_id,organisation_id))
					deviceDtls = cursor.fetchone()
					if deviceDtls == None:
						sent = "Not found user device token"
					else:
						device_id = deviceDtls['device_token']

						cursor.execute("""SELECT * FROM `organisation_firebase_details` 
							where `organisation_id`=%s""",(organisation_id))
						firebaseDtls = cursor.fetchone()
						if firebaseDtls == None:
							sent = "Not found firebase key"
						else:
							api_key = firebaseDtls['firebase_key']

						data_message = {
										"title" : title,
										"message": msg,
										"image-url":img
										}
						
						push_service = FCMNotification(api_key=api_key)
						msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
						sent = 'No'
						if msgResponse.get('success') == 1:
							sent = 'Yes'
							
							app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
								image,`U_id`,`Device_ID`,`Sent`,`organisation_id`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s)""")
							insert_data = (title,msg,img,user_id,device_id,sent,organisation_id)
							appdata = cursor.execute(app_query,insert_data)
									
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and selectedUsers == None:
			pcostrange = pcost.split("-", 1)
			startingcost = pcostrange[0]
			endingcost = pcostrange[1]

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s""",
				(brand,organisation_id,organisation_id,sdate,today))

			userDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for i in range(len(userDtls)):
				cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
					WHERE user_id=%s and `organisation_id` =%s and 
					`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
				costDtls = cursor.fetchone()
				
				total = costDtls['total']
				if total == None:
					total = 0
				scost = float(startingcost)
				ecost = float(endingcost)
				if scost <= total <= ecost:
					user_id = userDtls[i]['admin_id']			
					cursor.execute("""SELECT * FROM `devices` WHERE `user_id`=%s and 
						organisation_id=%s""",(user_id,organisation_id))
					deviceDtls = cursor.fetchone()
					if deviceDtls == None:
						sent = "Not found user device token"
					else:
						device_id = deviceDtls['device_token']

						cursor.execute("""SELECT * FROM `organisation_firebase_details` 
							where `organisation_id`=%s""",(organisation_id))
						firebaseDtls = cursor.fetchone()
						if firebaseDtls == None:
							sent = "Not found firebase key"
						else:
							api_key = firebaseDtls['firebase_key']

						data_message = {
										"title" : title,
										"message": msg,
										"image-url":img
										}
						
						push_service = FCMNotification(api_key=api_key)
						msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
						sent = 'No'
						if msgResponse.get('success') == 1:
							sent = 'Yes'
							
							app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
								image,`U_id`,`Device_ID`,`Sent`,`organisation_id`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s)""")
							insert_data = (title,msg,img,user_id,device_id,sent,organisation_id)
							appdata = cursor.execute(app_query,insert_data)
							
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and selectedUsers == None:
			pcostrange = pcost.split("-", 1)
			startingcost = pcostrange[0]
			endingcost = pcostrange[1]

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s""",
				(brand,organisation_id,model,organisation_id,sdate,today))

			userDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for i in range(len(userDtls)):
				cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
					WHERE user_id=%s and `organisation_id` =%s and 
					`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
				costDtls = cursor.fetchone()
				
				total = costDtls['total']
				if total == None:
					total = 0
				scost = float(startingcost)
				ecost = float(endingcost)
				if scost <= total <= ecost:
					user_id = userDtls[i]['admin_id']			
					cursor.execute("""SELECT * FROM `devices` WHERE `user_id`=%s and 
						organisation_id=%s""",(user_id,organisation_id))
					deviceDtls = cursor.fetchone()
					if deviceDtls == None:
						sent = "Not found user device token"
					else:
						device_id = deviceDtls['device_token']

						cursor.execute("""SELECT * FROM `organisation_firebase_details` 
							where `organisation_id`=%s""",(organisation_id))
						firebaseDtls = cursor.fetchone()
						if firebaseDtls == None:
							sent = "Not found firebase key"
						else:
							api_key = firebaseDtls['firebase_key']

						data_message = {
										"title" : title,
										"message": msg,
										"image-url":img
										}
						
						push_service = FCMNotification(api_key=api_key)
						msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
						sent = 'No'
						if msgResponse.get('success') == 1:
							sent = 'Yes'
							
							app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
								image,`U_id`,`Device_ID`,`Sent`,`organisation_id`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s)""")
							insert_data = (title,msg,img,user_id,device_id,sent,organisation_id)
							appdata = cursor.execute(app_query,insert_data)
							

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and selectedUsers == None:
			
			pcostrange = pcost.split("-", 1)
			startingcost = pcostrange[0]
			endingcost = pcostrange[1]

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in(%s) and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s""",
				(brand,organisation_id,model,pincode,organisation_id,sdate,today))

			userDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for i in range(len(userDtls)):
				cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
					WHERE user_id=%s and `organisation_id` =%s and 
					`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
				costDtls = cursor.fetchone()
				
				total = costDtls['total']
				if total == None:
					total = 0
				scost = float(startingcost)
				ecost = float(endingcost)
				if scost <= total <= ecost:
					user_id = userDtls[i]['admin_id']			
					cursor.execute("""SELECT * FROM `devices` WHERE `user_id`=%s and 
						organisation_id=%s""",(user_id,organisation_id))
					deviceDtls = cursor.fetchone()
					if deviceDtls == None:
						sent = "Not found user device token"
					else:
						device_id = deviceDtls['device_token']

						cursor.execute("""SELECT * FROM `organisation_firebase_details` 
							where `organisation_id`=%s""",(organisation_id))
						firebaseDtls = cursor.fetchone()
						if firebaseDtls == None:
							sent = "Not found firebase key"
						else:
							api_key = firebaseDtls['firebase_key']

						data_message = {
										"title" : title,
										"message": msg,
										"image-url":img
										}
						
						push_service = FCMNotification(api_key=api_key)
						msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
						sent = 'No'
						if msgResponse.get('success') == 1:
							sent = 'Yes'
							
							app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
								image,`U_id`,`Device_ID`,`Sent`,`organisation_id`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s)""")
							insert_data = (title,msg,img,user_id,device_id,sent,organisation_id)
							appdata = cursor.execute(app_query,insert_data)
							
		connection.commit()
		cursor.close()
		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				"responseList": sent}), status.HTTP_200_OK

#--------------------------------------------------------------------#
@name_space.route("/getCustomerListByFilter/<string:sdate>/<int:pincode>/<string:model>/<string:brand>/<string:pcost>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByFilter(Resource):
	def get(self,sdate,pincode,model,brand,pcost,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None:
			print('hii')
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateOrganizationId/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
			
		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePincodeOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandModelOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePurchaseCostOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandPurchaseCostOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		connection.commit()
		cursor.close()
		return filterRes

#--------------------------------------------------------------------#
@name_space.route("/getCustomerListByFilterV2/<string:sdate>/<int:pincode>/<string:model>/<string:brand>/<string:pcost>/<string:city>/<string:edate>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByFilterV2(Resource):
	def get(self,sdate,edate,pincode,model,brand,pcost,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))


		if sdate != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and city == 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateOrganizationId/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
			
		if sdate != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and city == 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePincodeOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and city == 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and city == 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandModelOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and city == 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePurchaseCostOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and city == 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandPurchaseCostOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and city == 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		if sdate != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and city == 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		#----------------city-filtercombination-------------------#
		
		if sdate != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and city != 'n' and edate == 'n'and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByCityOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and city != 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePincodeCityOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and city != 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandCityOrganizationId//{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and city != 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandModelCityOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and city != 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePurchaseCostCityOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and city != 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandPurchaseCostCityOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and city != 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByBrandModelPurchaseCostCityOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		if sdate != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and city != 'n' and edate == 'n' and organisation_id != None:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByPincodeBrandModelPurchaseCostCityOrganizationId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		#----------------city-filtercombination-------------------#
		
		#----------------edate-filtercombination-------------------#
		if sdate != None and edate != 'n' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and city == 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
			
		if sdate != None and edate != 'n' and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and city == 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWisePincodeOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,pincode,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and city == 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseBrandOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,brand,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and city == 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseBrandModelOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,brand,model,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and city == 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWisePurchaseCostOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and city == 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseBrandPurchaseCostOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,brand,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and city == 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,brand,model,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		if sdate != None and edate != 'n' and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and city == 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWisePincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,pincode,brand,model,pcost,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		if sdate != None and edate != 'n' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and city != 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseCityOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and city != 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWisePincodeCityOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,pincode,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and city != 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseBrandCityOrganizationId//{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,brand,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and city != 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseBrandModelCityOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,brand,model,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and city != 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWisePurchaseCostCityOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,pcost,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and city != 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseBrandPurchaseCostCityOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,brand,pcost,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if sdate != None and edate != 'n' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and city != 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWiseBrandModelPurchaseCostCityOrganizationId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,brand,model,pcost,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		if sdate != None and edate != 'n' and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and city != 'n' and organisation_id != None:
			filterURL = BASE_URL + "filtercustomer_notify/EcommerceNotification/getCustomerListByDateWisePincodeBrandModelPurchaseCostCityOrganizationId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,edate,pincode,brand,model,pcost,city,organisation_id,start,limit,page)
			filterRes = requests.get(filterURL).json()

		#----------------edate-filtercombination-------------------#
		
		connection.commit()
		cursor.close()
		return filterRes

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateOrganizationId/<string:sdate>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateOrganizationId(Resource):
	def get(self,sdate,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		print('hiii')

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT `admin_id` FROM `admins`
			WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s""",(organisation_id,sdate,today))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(`admin_id`)as count FROM `admins`
			WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s""",(organisation_id,sdate,today))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and `organisation_id`=%s and 
				date(`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",(organisation_id,sdate,today,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s 
				and admin_id>%s and date(`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",
				(organisation_id,start,sdate,today,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				if customerdata[i]['date_of_creation'] == '0000-00-00 00:00:00':
					customerdata[i]['date_of_creation'] = '0000-00-00 00:00:00'
				else:
					customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''
					
				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s """,(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePincodeOrganizationId/<string:sdate>/<int:pincode>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePincodeOrganizationId(Resource):
	def get(self,sdate,pincode,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT `admin_id` FROM `admins`
			WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s and `pincode` in (%s)""",(organisation_id,sdate,today,pincode))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(`admin_id`)as count FROM `admins` ad
			WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s and `pincode` in (%s)""",
			(organisation_id,sdate,today,pincode))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s  and `pincode` in (%s) order by admin_id ASC limit %s""",
			(organisation_id,sdate,today,pincode,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s 
				and admin_id>%s and date(`date_of_creation`) between %s and %s and 
				pincode in (%s) order by admin_id ASC limit %s""",
				(organisation_id,start,sdate,today,pincode,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s """,(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandOrganizationId/<string:sdate>/<string:brand>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandOrganizationId(Resource):
	def get(self,sdate,brand,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		adminid = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT `admin_id` FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(`date_of_creation`) BETWEEN %s and %s and `organisation_id`=%s""",(brand,organisation_id,organisation_id,sdate,today,organisation_id))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(`date_of_creation`) BETWEEN %s and %s and `organisation_id`=%s""",
			(brand,organisation_id,organisation_id,sdate,today,organisation_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,organisation_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`)as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,start,organisation_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list_data':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandModelOrganizationId/<string:sdate>/<string:brand>/<string:model>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandModelOrganizationId(Resource):
	def get(self,sdate,brand,model,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		split_model = model.split(',')

		customerList_query = cursor.execute("""SELECT `admin_id` FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s)
			and `customer_id` !=0)) and date(`date_of_creation`) BETWEEN %s and %s and 
			`organisation_id`=%s""",(brand,organisation_id,split_model,sdate,today,organisation_id))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0)) and date(`date_of_creation`) BETWEEN %s and %s and 
			`organisation_id`=%s""",
			(brand,organisation_id,split_model,sdate,today,organisation_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,split_model,organisation_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`)as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,split_model,start,organisation_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0


		if prdcusmrDtls:			
			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list_data':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK


#-------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePurchaseCostOrganizationId/<string:sdate>/<string:pcost>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePurchaseCostOrganizationId(Resource):
	def get(self,sdate,pcost,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		scost = float(startingcost)
		ecost = float(endingcost)

		customerList_query = cursor.execute("""SELECT distinct(`admin_id`) FROM `admins` a
			INNER JOIN `instamojo_payment_request` ipr on ipr.`user_id` = a.`admin_id`
			WHERE a.`organisation_id`=%s and date(`date_of_creation`) between %s and %s and ipr.`organisation_id` = %s and amount BETWEEN %s and %s""",
			(organisation_id,sdate,today,organisation_id,scost,ecost))
		customer_list_data = cursor.fetchall()
		
		cursor.execute("""SELECT distinct(admin_id) FROM `admins` a
			INNER JOIN `instamojo_payment_request` ipr on ipr.`user_id` = a.`admin_id`
			WHERE a.`organisation_id`=%s and date(`date_of_creation`) between %s and %s and ipr.`organisation_id` = %s and amount BETWEEN %s and %s""",
			(organisation_id,sdate,today,organisation_id,scost,ecost))
		userDtls = cursor.fetchall()		
		
		total_count = len(userDtls)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT admin_id FROM `admins`
					WHERE `organisation_id`=%s and date(`date_of_creation`) between %s and %s""",
					(organisation_id,sdate,today))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))				

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:
				
					cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
						FROM `admins` where 
						`organisation_id`=%s and date(`date_of_creation`) 
						between %s and %s and `admin_id` in %s order by admin_id ASC limit %s""",
						(organisation_id,sdate,today,customerids,limit))

					prdcusmrDtls = cursor.fetchall()
					
					if prdcusmrDtls != None:
						for cid in range(len(prdcusmrDtls)):
							prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
							prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

							cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
							customertype = cursor.fetchone()
							if customertype:
								prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
							else:
								prdcusmrDtls[cid]['customertype'] = ''

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
								prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
							else:
								prdcusmrDtls[cid]['retailer_city'] = ""
								prdcusmrDtls[cid]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								prdcusmrDtls[cid]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								prdcusmrDtls[cid]['enquiery_count'] = 0
							
							scost = float(startingcost)
							ecost = float(endingcost) 

							cursor.execute("""SELECT `amount`as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
							print(cursor._last_executed)
							costDtls = cursor.fetchone()
							if costDtls['total'] != None:
								prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
							else:
								prdcusmrDtls[cid]['purchase_cost'] = 0
					else:
						prdcusmrDtls =[]
			else:
				cursor.execute("""SELECT admin_id FROM `admins`
					WHERE `organisation_id`=%s and date(`date_of_creation`) between %s and %s""",
					(organisation_id,sdate,today))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))				

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:
				
					cursor.execute("""SELECT `admin_id`,
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
						FROM `admins` where `organisation_id`=%s and date(`date_of_creation`) 
						between %s and %s and `admin_id` in %s and `admin_id`>%s order by admin_id ASC
						limit %s""",(organisation_id,sdate,today,customerids,start,limit))

					prdcusmrDtls = cursor.fetchall()
					if prdcusmrDtls:
						for cid in range(len(prdcusmrDtls)):
							prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
							prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

							cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
							customertype = cursor.fetchone()
							if customertype:
								prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
							else:
								prdcusmrDtls[cid]['customertype'] = ''

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
								prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
							else:
								prdcusmrDtls[cid]['retailer_city'] = ""
								prdcusmrDtls[cid]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								prdcusmrDtls[cid]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								prdcusmrDtls[cid]['enquiery_count'] = 0
							
							scost = float(startingcost)
							ecost = float(endingcost) 

							cursor.execute("""SELECT `amount`as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
							print(cursor._last_executed)
							costDtls = cursor.fetchone()
							if costDtls['total'] != None:
								prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
							else:
								prdcusmrDtls[cid]['purchase_cost'] = 0
					else:
						prdcusmrDtls = []
				print(cursor._last_executed)

		if prdcusmrDtls:
			page_next = page + 1			
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list_data':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandPurchaseCostOrganizationId/<string:sdate>/<string:brand>/<string:pcost>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandPurchaseCostOrganizationId(Resource):
	def get(self,sdate,brand,pcost,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		cursor.execute("""SELECT distinct(`admin_id`)as 'admin_id' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(`date_of_creation`) BETWEEN %s and %s and `organisation_id`=%s""",
			(brand,organisation_id,organisation_id,sdate,today,organisation_id))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			scost = float(startingcost)
			ecost = float(endingcost) 

			payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))		

			if payment_count > 0:					
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hiii')
		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		
		else:
		
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					
					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
						`organisation_id` = %s ) and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and 
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
						(brand,organisation_id,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,start,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					
					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
						`organisation_id` = %s ) and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and 
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
						(brand,organisation_id,start,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:
			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByBrandModelPurchaseCostOrganizationId/<string:sdate>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByBrandModelPurchaseCostOrganizationId(Resource):
	def get(self,sdate,brand,model,pcost,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		split_model = model.split(',')

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc""",
			(brand,organisation_id,split_model,organisation_id,sdate,today))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			scost = float(startingcost)
			ecost = float(endingcost)

			payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
			
			if payment_count > 0:
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})					
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hii')

		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and `amount` BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')	

					print(customerids)

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
						(brand,organisation_id,split_model,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0

						scost = float(startingcost)
						ecost = float(endingcost) 
					 	
						cursor.execute("""SELECT `amount` as total FROM 
							`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,start,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and `amount` BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')	

					print(customerids)

				if customerids:
				
					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s limit %s""",
						(brand,organisation_id,split_model,start,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost) 
					 	
						cursor.execute("""SELECT `amount` as total FROM 
							`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
					
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:

			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#----------------------------------------------------------------#
@name_space.route("/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/<string:sdate>/<int:pincode>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByPincodeBrandModelPurchaseCostOrganizationId(Resource):
	def get(self,sdate,pincode,brand,model,pcost,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		split_model = model.split(',')

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in (%s) and 
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc""",
			(brand,organisation_id,split_model,pincode,organisation_id,sdate,today))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			scost = float(startingcost)
			ecost = float(endingcost) 

			payment_count =  cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))
			
			if payment_count > 0:	
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})				
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hiii')
				
		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,pincode,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost)
					payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					
					if payment_count > 0:
						
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')
				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and ad.`pincode` in(%s) and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
						(brand,organisation_id,split_model,customerids,pincode,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0

						scost = float(startingcost)
						ecost = float(endingcost)
					 	
						cursor.execute("""SELECT `amount` as total FROM 
							`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				 	
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,start,pincode,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost)
					payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					
					if payment_count > 0:						
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:
				
					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s 
						and ad.`pincode` in(%s) and ad.`organisation_id`=%s and 
						date(`date_of_creation`) BETWEEN %s and %s limit %s""",
						(brand,organisation_id,split_model,start,customerids,pincode,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''
							
						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0

						scost = float(startingcost)
						ecost = float(endingcost)
					 	
						cursor.execute("""SELECT `amount` as total FROM 
							`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
						
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:

			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#--------------------------------------------------------------------#
@name_space.route("/GetNotificationHistoryByCustomerId/<int:customer_id>")	
class GetNotificationHistoryByCustomerId(Resource):
	def get(self,customer_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `App_Notification_ID`,`title`,`body`,
			`U_id`,`Device_ID`,`Sent`,`organisation_id`,
			`Last_Update_TS`,`is_read` FROM `app_notification` WHERE 
			`U_id`=%s""",(customer_id))

		notifydata = cursor.fetchall()
		if notifydata:
			for i in range(len(notifydata)):
				notifydata[i]['Last_Update_TS'] = notifydata[i]['Last_Update_TS'].isoformat()
		else:
			notifydata = []
	
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Customer App Notification Details",
		    		"status": "success"
		    	},
		    	"responseList": notifydata }), status.HTTP_200_OK


#----------------------Update-notification---------------------#

@name_space.route("/updatNotification/<int:App_Notification_ID>")
class updatNotification(Resource):
	@api.expect(notification_putmodel)
	def put(self,App_Notification_ID):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "is_read" in details:
			is_read = details['is_read']
			update_query = ("""UPDATE `app_notification` SET `is_read` = %s
				WHERE `App_Notification_ID` = %s""")
			update_data = (is_read,App_Notification_ID)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Update Notification Details",
		    		"status": "success"
		    	},
		    	"responseList": details }), status.HTTP_200_OK

#----------------------Update-notification---------------------#

#--------------------------------------------------------------------#
@name_space.route("/getCustomerListByCityOrganizationId/<string:sdate>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByCityOrganizationId(Resource):
	def get(self,sdate,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		today = date.today()
		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city
		cursor.execute("""SELECT count(`admin_id`)as count FROM `admins`
			WHERE `role_id`=4 and `status`=1 and city=%s and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s""",(store,organisation_id,sdate,today))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`city`as 'retailer_store',`dob`,`phoneno`,profile_image,
				`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and city=%s and `organisation_id`=%s and 
				date(`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",(store,organisation_id,sdate,today,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`city`as 'retailer_store',`dob`,`phoneno`,profile_image,
				`pincode`,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` WHERE `role_id`=4 and `status`=1 and city=%s and `organisation_id`=%s 
				and admin_id>%s and date(`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",
				(store,organisation_id,start,sdate,today,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				if customerdata[i]['date_of_creation'] == '0000-00-00 00:00:00':
					customerdata[i]['date_of_creation'] = '0000-00-00 00:00:00'
				else:
					customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePincodeCityOrganizationId/<string:sdate>/<int:pincode>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePincodeCityOrganizationId(Resource):
	def get(self,sdate,pincode,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city
		cursor.execute("""SELECT count(`admin_id`)as count FROM `admins` ad
			WHERE `role_id`=4 and `status`=1 and city=%s and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s and `pincode` in (%s)""",
			(store,organisation_id,sdate,today,pincode))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and city=%s and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s  and `pincode` in (%s) order by admin_id ASC limit %s""",
			(store,organisation_id,sdate,today,pincode,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` WHERE `role_id`=4 and `status`=1 and city=%s and `organisation_id`=%s 
				and admin_id>%s and date(`date_of_creation`) between %s and %s and 
				pincode in (%s) order by admin_id ASC limit %s""",
				(store,organisation_id,start,sdate,today,pincode,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandCityOrganizationId/<string:sdate>/<string:brand>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandCityOrganizationId(Resource):
	def get(self,sdate,brand,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		adminid = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(`date_of_creation`) BETWEEN %s and %s and city=%s and `organisation_id`=%s""",
			(brand,organisation_id,organisation_id,sdate,today,store,organisation_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and city=%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,store,organisation_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`)as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and city=%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,start,store,organisation_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandModelCityOrganizationId/<string:sdate>/<string:brand>/<string:model>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandModelCityOrganizationId(Resource):
	def get(self,sdate,brand,model,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in(%s)) 
			and `customer_id` !=0)) and date(`date_of_creation`) BETWEEN %s and %s and 
			`organisation_id`=%s and city=%s""",
			(brand,organisation_id,model,sdate,today,organisation_id,store))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and city=%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,model,store,organisation_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`)as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and city=%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,model,start,store,organisation_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK


#-------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePurchaseCostCityOrganizationId/<string:sdate>/<string:pcost>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePurchaseCostCityOrganizationId(Resource):
	def get(self,sdate,pcost,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]
		
		cursor.execute("""SELECT admin_id FROM `admins`
			WHERE `organisation_id`=%s and city=%s and date(`date_of_creation`) between %s and %s""",
			(organisation_id,store,sdate,today))
		userDtls = cursor.fetchall()
		
		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])
		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT admin_id FROM `admins`
					WHERE `organisation_id`=%s and city=%s and date(`date_of_creation`) between %s and %s""",
					(organisation_id,store,sdate,today))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
					FROM `admins` where 
					`organisation_id`=%s and date(`date_of_creation`) 
					between %s and %s and `admin_id` in %s order by admin_id ASC limit %s""",
					(organisation_id,sdate,today,customerids,limit))

				prdcusmrDtls = cursor.fetchall()
				
				if prdcusmrDtls != None:
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
							WHERE user_id=%s and `organisation_id` =%s and 
							`status`='Complete'""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
						total = costDtls['total']
			
						if total == None:
							prdcusmrDtls[cid]['purchase_cost'] = 0
						else:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
			else:
				cursor.execute("""SELECT admin_id FROM `admins`
					WHERE `organisation_id`=%s and city=%s and date(`date_of_creation`) between %s and %s""",
					(organisation_id,store,sdate,today))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
					if costDtls['total'] != None:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT `admin_id`,
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
					FROM `admins` where `organisation_id`=%s and date(`date_of_creation`) 
					between %s and %s and `admin_id` in %s and `admin_id`>%s order by admin_id ASC
					limit %s""",(organisation_id,sdate,today,customerids,start,limit))

				prdcusmrDtls = cursor.fetchall()
				if prdcusmrDtls:
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
							WHERE user_id=%s and `organisation_id` =%s and 
							`status`='Complete'""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						costDtls = cursor.fetchone()

						if total == None:
							prdcusmrDtls[cid]['purchase_cost'] = 0
						else:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
			page_next = page + 1			
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandPurchaseCostCityOrganizationId/<string:sdate>/<string:brand>/<string:pcost>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandPurchaseCostCityOrganizationId(Resource):
	def get(self,sdate,brand,pcost,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		cursor.execute("""SELECT distinct(`admin_id`)as 'admin_id' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(`date_of_creation`) BETWEEN %s and %s and city=%s and `organisation_id`=%s""",
			(brand,organisation_id,organisation_id,sdate,today,store,organisation_id))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])
		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		
		else:
		
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and city=%s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,store,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,customerids,organisation_id,sdate,today,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
						prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
					else:
						prdcusmrDtls[cid]['retailer_city'] = ""
						prdcusmrDtls[cid]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
																 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						prdcusmrDtls[cid]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
																 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						prdcusmrDtls[cid]['enquiery_count'] = 0
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and city=%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,start,store,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,start,customerids,organisation_id,sdate,today,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
						prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
					else:
						prdcusmrDtls[cid]['retailer_city'] = ""
						prdcusmrDtls[cid]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
																 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						prdcusmrDtls[cid]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
																 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						prdcusmrDtls[cid]['enquiery_count'] = 0
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByBrandModelPurchaseCostCityOrganizationId/<string:sdate>/<string:brand>/<string:model>/<string:pcost>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByBrandModelPurchaseCostCityOrganizationId(Resource):
	def get(self,sdate,brand,model,pcost,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and city=%s and
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc""",
			(brand,organisation_id,model,store,organisation_id,sdate,today))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])

		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and city=%s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,store,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,customerids,organisation_id,sdate,today,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
						prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
					else:
						prdcusmrDtls[cid]['retailer_city'] = ""
						prdcusmrDtls[cid]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
																 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						prdcusmrDtls[cid]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
																 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						prdcusmrDtls[cid]['enquiery_count'] = 0
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and city=%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,organisation_id,start,store,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s limit %s""",
					(brand,organisation_id,model,start,customerids,organisation_id,sdate,today,limit))

				prdcusmrDtls = cursor.fetchall()
				
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
						prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
					else:
						prdcusmrDtls[cid]['retailer_city'] = ""
						prdcusmrDtls[cid]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
																 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						prdcusmrDtls[cid]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
																 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						prdcusmrDtls[cid]['enquiery_count'] = 0
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#----------------------------------------------------------------#
@name_space.route("/getCustomerListByPincodeBrandModelPurchaseCostCityOrganizationId/<string:sdate>/<int:pincode>/<string:brand>/<string:model>/<string:pcost>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByPincodeBrandModelPurchaseCostCityOrganizationId(Resource):
	def get(self,sdate,pincode,brand,model,pcost,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in(%s)) 
			and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in (%s) and city=%s and 
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s""",
			(brand,organisation_id,model,pincode,store,organisation_id,sdate,today))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])
				
		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in(%s) and city=%s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,pincode,store,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,customerids,pincode,organisation_id,sdate,today,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
						prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
					else:
						prdcusmrDtls[cid]['retailer_city'] = ""
						prdcusmrDtls[cid]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
																 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						prdcusmrDtls[cid]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
																 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						prdcusmrDtls[cid]['enquiery_count'] = 0
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`pincode` in(%s) and city=%s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,start,pincode,store,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s limit %s""",
					(brand,organisation_id,model,start,customerids,pincode,organisation_id,sdate,today,limit))

				prdcusmrDtls = cursor.fetchall()
				
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
						prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
					else:
						prdcusmrDtls[cid]['retailer_city'] = ""
						prdcusmrDtls[cid]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
																 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						prdcusmrDtls[cid]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
																 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						prdcusmrDtls[cid]['enquiery_count'] = 0
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#--------------------------------------------------------------------#
