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

ecommerce_retail_store = Blueprint('ecommerce_retail_store_api', __name__)
api = Api(ecommerce_retail_store,  title='Ecommerce API',description='Ecommerce API')

name_space = api.namespace('EcommerceRetailStore',description='Ecommerce Retail Store')

name_space_dashboard = api.namespace('DashboardWithRetailer',description='Dashboard With Retailer Store')

name_space_order_history = api.namespace('OrderHistoryWithRetailer',description='Order History With Retailer Store')

name_space_customer_list = api.namespace('CustomerListWithRetailer',description='Customer List With Retailer Store')

name_space_loyality_dashboard = api.namespace('LoyalityDashboardWithRetailer',description='Loyality Dashboard With Retailer Store')

name_space_offer = api.namespace('OfferWithRetailer',description='Offer With Retailer Store')

name_space_enquiry = api.namespace('EnquiryWithRetailer',description='Enquiry With Retailer Store')

name_space_exchange = api.namespace('ExchangeWithRetailer',description='Exchange With Retailer Store')

EMAIL_ADDRESS = 'communications@creamsonservices.com'
EMAIL_PASSWORD = 'CReam7789%$intELLi'

city_postmodel = api.model('city_postmodel',{	
	"city": fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"image": fields.String(required=True)
})

city_putmodel = api.model('city_putmodel',{	
	"city": fields.String(required=True),
	"image": fields.String(required=True)
})


retailstore_postmodel = api.model('retailstore_postmodel',{	
	"store_name": fields.String(required=True),
	"city_id": fields.Integer(required=True),
	"address":fields.String(required=True),
	"latitude":fields.String,
	"longitude":fields.String,
	"phoneno":fields.String(required=True),
	"organisation_id":fields.Integer(required=True)
})

retailstore_putmodel = api.model('retailstore_putmodel',{
	"store_name": fields.String,
	"address":fields.String,
	"latitude":fields.String,
	"longitude":fields.String,
	"retailstore_status":fields.Integer
})


ecommerce_otp = api.model('ecommerce_otp',{
	"USER_ID":fields.Integer(),
	"organisation_id":fields.Integer(),
	"role_id":fields.Integer(),
	"FIRST_NAME":fields.String(),
	"LAST_NAME":fields.String(),
	"MAIL_ID":fields.String(),
	"Address":fields.String(),
	"PHONE_NUMBER":fields.String()
})

sendotp_postmodel = api.model('sendOtp',{
	"phoneno":fields.String(required=True),
	"email":fields.String
})

checkotp_postmodel = api.model('checkOtp',{
	"phoneno":fields.String(required=True),
	"otp":fields.String(required=True)
})

login_postmodel = api.model('loginPostmodel',{
	"phoneno":fields.String(required=True),
	"device_token":fields.String(required=True)

})

general_login_postmodel = api.model('SelectOrganisation', {	
	"phoneno":fields.String(required=True),
	"email":fields.String,
	"device_token":fields.String,
	"is_head_office_login":fields.Integer(required=True),
	"registration_type":fields.Integer(required=True)
})

organisation_putmodel = api.model('organisation_putmodel', {	
	"organization_name":fields.String,
	"city":fields.String,	
	"latitude":fields.String,
	"longitude":fields.String,
	"store_address":fields.String
})

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#----------------------Catalog-List---------------------#
@name_space.route("/catalogList/<int:organisation_id>/<int:retailer_store_store_id>")	
class catalogList(Resource):
	def get(self,organisation_id,retailer_store_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT c.`catalog_id`,c.`catalog_name`,c.`language`,c.`is_home_section`,c.`sequence`,c.`last_update_ts`
				FROM `retailer_store_catalog_mapping` rscm
				INNER JOIN `catalogs` c ON c.`catalog_id` = rscm.`catalog_id`
				WHERE rscm.`organisation_id` = %s and rscm.`retailer_store_store_id` = %s ORDER BY c.`sequence`""")
		get_data = (organisation_id,retailer_store_store_id)

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

#----------------------Add-City---------------------#

@name_space.route("/addCity")	
class addCity(Resource):
	@api.expect(city_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		organisation_id = details['organisation_id']	
		city = details['city']
		retailer_name = city+" Retailer"
		last_update_id = details['organisation_id']
		image = details['image']

		get_query = ("""SELECT *
			FROM `retailer_store` WHERE `city` = %s and `organisation_id` = %s""")
		getData = (city,organisation_id)
		count_retailer = cursor.execute(get_query,getData)
		
		if count_retailer > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "city_details",
			    		"status": "error",
			    		"message":" Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

		else:
			store_status = 1
			insert_query = ("""INSERT INTO `retailer_store`(`retailer_name`,`city`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")
			data = (retailer_name,city,store_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)
			city_id = cursor.lastrowid

			city_image_status = 1
			insert_city_image_query = ("""INSERT INTO `retailer_store_image`(`retailer_store_id`,`image`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s) """)
			city_image_data = (city_id,image,city_image_status,organisation_id,last_update_id)
			cursor.execute(insert_city_image_query,city_image_data)

			return ({"attributes": {
		    		"status_desc": "city_details",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList": details}), status.HTTP_200_OK

#----------------------Add-City---------------------#

#----------------------City-List---------------------#

@name_space.route("/cityList/<int:organisation_id>")	
class cityList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()


		get_query =  ("""SELECT rs.`retailer_store_id`,rs.`retailer_name`,rs.`city`,rsi.`image`
			FROM `retailer_store` rs 
			INNER JOIN `retailer_store_image` rsi ON rsi.`retailer_store_id` = rs.`retailer_store_id`
			WHERE rs.`organisation_id` = %s """)

		get_data = (organisation_id)
		count_city = cursor.execute(get_query,get_data)

		if count_city >0:
			city_data = cursor.fetchall()

			for key,data in enumerate(city_data):
				get_query =  ("""SELECT rss.`store_name`,rss.`address`,rss.`latitude`,rss.`longitude`,rss.`phoneno`
					FROM `retailer_store_stores` rss 
					where rss.`organisation_id` = %s and rss.`retailer_store_id` = %s""")	
				get_data = (organisation_id,data['retailer_store_id'])
				count_reatiler = cursor.execute(get_query,get_data)

				#if count_reatiler > 0:
					#retail_store_data = cursor.fetchall()
					#city_data[key]['is_retailer_store'] = 1
					#city_data[key]['retailer_store'] = retail_store_data
				#else:
					#city_data[key]['is_retailer_store'] = 0
					#city_data[key]['retailer_store'] = []
		else:
			city_data = []

		return ({"attributes": {
		    		"status_desc": "location_details",
		    		"status": "success"
		    	},
		    	"responseList":city_data}), status.HTTP_200_OK

#----------------------City-List---------------------#

#----------------------Update-City---------------------#

@name_space.route("/UpdateCity/<int:city_id>/<int:organisation_id>")
class UpdateCity(Resource):
	@api.expect(city_putmodel)
	def put(self,city_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		if details and "city" in details:
			city = details['city']
			retailer_name = city+" Retailer"

			get_query_with_city_id = ("""SELECT *
			FROM `retailer_store` WHERE `city` = %s and `organisation_id` = %s and `retailer_store_id` = %s""")
			getDataWithCityId = (city,organisation_id,city_id)
			count_retailer_with_city_id = cursor.execute(get_query_with_city_id,getDataWithCityId)

			if count_retailer_with_city_id > 0:
				update_query = ("""UPDATE `retailer_store` SET `city` = %s,`retailer_name` = %s
						WHERE `retailer_store_id` = %s """)
				update_data = (city,retailer_name,city_id)
				cursor.execute(update_query,update_data)

				if details and "image" in details:
					image = details['image']

					update_image_query = ("""UPDATE `retailer_store_image` SET `image` = %s
						WHERE `retailer_store_id` = %s """)
					update_image_data = (image,city_id)
					cursor.execute(update_image_query,update_image_data)

			else:
				get_query = ("""SELECT *
				FROM `retailer_store` WHERE `city` = %s and `organisation_id` = %s""")
				getData = (city,organisation_id)
				count_retailer = cursor.execute(get_query,getData)
				
				if count_retailer > 0:
					data = cursor.fetchone()
					return ({"attributes": {
					    		"status_desc": "city_details",
					    		"status": "error",
					    		"message":" Already Exist"
					    	},
					    	"responseList":{} }), status.HTTP_200_OK
				else:
					update_query = ("""UPDATE `retailer_store` SET `city` = %s,`retailer_name` = %s
							WHERE `retailer_store_id` = %s """)
					update_data = (city,retailer_name,city_id)
					cursor.execute(update_query,update_data)

				if details and "image" in details:
					image = details['image']

					update_image_query = ("""UPDATE `retailer_store_image` SET `image` = %s
						WHERE `retailer_store_id` = %s """)
					update_image_data = (image,city_id)
					cursor.execute(update_image_query,update_image_data)


		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update City",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-City---------------------#

#----------------------Add-Retail-Store---------------------#

@name_space.route("/addRetailStore")	
class addRetailStore(Resource):
	@api.expect(retailstore_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		store_name = details['store_name']
		city_id = details['city_id']
		address = details['address']

		if details and "latitude" in details:
			latitude = details['latitude']
		else:
			latitude = 0.0

		if details and "longitude" in details:
			longitude = details['longitude']
		else:
			longitude = 0.0

		phoneno = details['phoneno']
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']

		store_status = 1

		get_query = ("""SELECT *
			FROM `retailer_store_stores` WHERE `phoneno` = %s""")
		getData = (phoneno)
		count_retailer = cursor.execute(get_query,getData)

		if count_retailer > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "retailer_details",
			    		"status": "error",
			    		"message":"Phone No Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK
		else:
			insert_query = ("""INSERT INTO `retailer_store_stores`(`store_name`,`retailer_store_id`,`address`,`latitude`,`longitude`,`phoneno`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			data = (store_name,city_id,address,latitude,longitude,phoneno,store_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)

			return ({"attributes": {
			    		"status_desc": "city_details",
			    		"status": "success",
			    		"message":""
			    	},
			    	"responseList": details}), status.HTTP_200_OK

#----------------------Add-Retail-Store---------------------#

#----------------------Retailer-List-By-City-Id---------------------#

@name_space.route("/retailerListByCityId/<int:city_id>/<int:organisation_id>")	
class retailerListByCityId(Resource):
	def get(self,city_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT rss.`retailer_store_store_id`,rs.`city`,rsi.`image`,rss.`store_name`,rss.`address`,rss.`latitude`,rss.`longitude`,rss.`phoneno`
			FROM `retailer_store_stores` rss 
			INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = rss.`retailer_store_id`
			INNER JOIN `retailer_store_image` rsi ON rsi.`retailer_store_id` = rss.`retailer_store_id`
			where rss.`organisation_id` = %s and rss.`retailer_store_id` = %s""")	
		get_data = (organisation_id,city_id)
		count_retailer = cursor.execute(get_query,get_data)

		if count_retailer > 0:
			retailer_data = cursor.fetchall()
		else:
			retailer_data = []	

		return ({"attributes": {
		    		"status_desc": "retailer_details",
		    		"status": "success"
		    	},
		    	"responseList":retailer_data}), status.HTTP_200_OK

#----------------------Retailer-List-By-City-Id---------------------#

#----------------------Update-Retail-Store---------------------#

@name_space.route("/updateRetailStore/<int:retailer_store_store_id>")	
class updateRetailStore(Resource):
	@api.expect(retailstore_putmodel)
	def put(self,retailer_store_store_id):		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "store_name" in details:
			store_name = details['store_name']

			update_query = ("""UPDATE `retailer_store_stores` SET `store_name` = %s
						WHERE `retailer_store_store_id` = %s """)
			update_data = (store_name,retailer_store_store_id)
			cursor.execute(update_query,update_data)

		if details and "address" in details:
			address = details['address']

			update_query = ("""UPDATE `retailer_store_stores` SET `address` = %s
						WHERE `retailer_store_store_id` = %s """)
			update_data = (address,retailer_store_store_id)
			cursor.execute(update_query,update_data)

		if details and "latitude" in details:
			latitude = details['latitude']

			update_query = ("""UPDATE `retailer_store_stores` SET `latitude` = %s
						WHERE `retailer_store_store_id` = %s """)
			update_data = (latitude,retailer_store_store_id)
			cursor.execute(update_query,update_data)

		if details and "longitude" in details:
			longitude = details['longitude']

			update_query = ("""UPDATE `retailer_store_stores` SET `longitude` = %s
						WHERE `retailer_store_store_id` = %s """)
			update_data = (longitude,retailer_store_store_id)
			cursor.execute(update_query,update_data)

		if details and "retailstore_status" in details:
			retailstore_status = details['retailstore_status']

			update_query = ("""UPDATE `retailer_store_stores` SET `status` = %s
						WHERE `retailer_store_store_id` = %s """)
			update_data = (retailstore_status,retailer_store_store_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Retail Store",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Retail-Store---------------------#

#----------------------Update-Organisation---------------------#

@name_space.route("/updateOrganisation/<int:organisation_id>")	
class updateOrganisation(Resource):
	@api.expect(organisation_putmodel)
	def put(self,organisation_id):		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		store_address = details['store_address']
		latitude = details['latitude']
		longitude = details['longitude']

		get_query = ("""SELECT *
			FROM `organisation_master` WHERE `organisation_id` = %s""")
		getData = (organisation_id)
		count_organisation = cursor.execute(get_query,getData)

		if count_organisation > 0:
			organisation_data = cursor.fetchone()

			if details and "organization_name" in details:
				organization_name = details['organization_name']
				update_query = ("""UPDATE `organisation_master` SET `organization_name` = %s
						WHERE `organisation_id` = %s """)
				update_data = (organization_name,organisation_id)
				cursor.execute(update_query,update_data)

			if details and "city" in details:
				city = details['city']

				update_query = ("""UPDATE `organisation_master` SET `city` = %s
						WHERE `organisation_id` = %s """)
				update_data = (city,organisation_id)
				cursor.execute(update_query,update_data)

				get_retailer_store_query = ("""SELECT *
					FROM `retailer_store` WHERE  `city` = %s and `organisation_id` = %s""")
				get_retailer_store_data = (city,organisation_id)
				count_retailer_store = cursor.execute(get_retailer_store_query,get_retailer_store_data)

				if count_retailer_store > 0:
					retailer_store_data = cursor.fetchone()

					get_retailer_store_store_query = ("""SELECT * FROM `retailer_store_stores` WHERE `retailer_store_id` = %s and `organisation_id` = %s """)
					get_retailer_store_store_data = (retailer_store_data['retailer_store_id'],organisation_id)
					count_retailer_store_store = cursor.execute(get_retailer_store_store_query,get_retailer_store_store_data)

					if count_retailer_store_store < 1:
						retailer_store_store_status = 1
						insert_retailer_store_store_query = ("""INSERT INTO `retailer_store_stores`(`store_name`,`retailer_store_id`,`address`,`latitude`,`longitude`,`phoneno`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
						insert_retailer_store_store_data = (details['organization_name'],retailer_store_data['retailer_store_id'],store_address,latitude,longitude,organisation_data['phoneno'],organisation_id,organisation_id)
						cursor.execute(insert_retailer_store_store_query,insert_retailer_store_store_data)
				else:
					retailer_store_status = 1
					retailer_name = city+" Retailer"
					insert_retailer_store_query = ("""INSERT INTO `retailer_store`(`retailer_name`,`city`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
					insert_retailer_store_data = (retailer_name,city,retailer_store_status,organisation_id,organisation_id)
					cursor.execute(insert_retailer_store_query,insert_retailer_store_data)

					retailer_store_id = cursor.lastrowid

					retailer_store_image_status = 1
					city_image = 'https://d1lwvo1ffrod0a.cloudfront.net/1/Ad_City_Icon.png'
					insert_retailer_store_image_query = ("""INSERT INTO `retailer_store_image`(`retailer_store_id`,`image`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
					insert_retailer_store_image_data = (retailer_store_id,city_image,retailer_store_image_status,organisation_id,organisation_id)
					cursor.execute(insert_retailer_store_image_query,insert_retailer_store_image_data)

					insert_retailer_store_store_query = ("""INSERT INTO `retailer_store_stores`(`store_name`,`retailer_store_id`,`address`,`latitude`,`longitude`,`phoneno`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
					insert_retailer_store_store_data = (details['organization_name'],retailer_store_id,store_address,latitude,longitude,organisation_data['phoneno'],organisation_id,organisation_id)
					cursor.execute(insert_retailer_store_store_query,insert_retailer_store_store_data)

		url = "http://techdrive.xyz/ecommerce-app/test.php?organisation_id="+str(organisation_id)
		post_data = {
						"organization_name": details['organization_name']
					}

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		post_response = requests.post(url, data=json.dumps(post_data), headers=headers).json()

		connection.commit()
		cursor.close()

		return post_response



#----------------------Update-Organisation---------------------#	

#----------------------------Generate-Otp--------------------------#
@name_space.route("/GenerateOTP")
class GenerateOTP(Resource):
	@api.expect(ecommerce_otp)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		USER_ID = details.get('USER_ID')
		organisation_id = details['organisation_id']
		role_id = details['role_id']
		FIRST_NAME = details.get('FIRST_NAME')
		LAST_NAME = details.get('LAST_NAME')
		MAIL_ID = details.get('MAIL_ID')
		Address = details.get('Address')
		PHONE_NUMBER = details['PHONE_NUMBER']
		
		if FIRST_NAME == '':
			FIRST_NAME = 'User'
		else:
			FIRST_NAME = FIRST_NAME

		def get_random_digits(stringLength=6):
		    Digits = string.digits
		    return ''.join((random.choice(Digits) for i in range(stringLength)))
		
		otp = get_random_digits()
			
		otp_query = ("""INSERT INTO `organisation_user_otp`(`USER_ID`,
			`organisation_id`,`OTP`,`role_id`,`FIRST_NAME`,`LAST_NAME`,
			`GENERATED_BY`, `MAIL_ID`, `Address`, `PHONE_NUMBER`)  
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		otpdata = cursor.execute(otp_query,(USER_ID,organisation_id,otp,role_id,
			FIRST_NAME,LAST_NAME,'System',MAIL_ID,Address,PHONE_NUMBER))

		if otpdata:
			details['OTP'] = otp 
			#----------------------------sms-----------------------#
			url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
			user = 'creamsonintelli'
			password = 'denver@1234'
			msisdn = PHONE_NUMBER
			sid = 'CRMLTD'
			msg = 'Hi '+FIRST_NAME+' The OTP for the Online Transaction is '+otp+'. This OTP is valid only for one time use.'
			fl = '0'
			gwid = '2'
			payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
				msisdn,sid,msg,fl,gwid)
			postUrl = url+payload
			print(postUrl)
			response = requests.request("POST", postUrl)

			if response.text == 'Failed#Invalid LoginThread was being aborted.':
				sent = 'N'
			else:	
				sms_response = json.loads(response.text)['ErrorMessage']
				# print(sms_response)
				res = {"status":sms_response}
				if res['status'] == 'Success':
					sent = 'Y'

					sms_query = ("""INSERT INTO `otp_sms`(`title`,`body`,
						`phone_number`,`Sent`,`organisation_id`)  
						VALUES(%s,%s,%s,%s,%s)""")
					smsdata = cursor.execute(sms_query,('OTP',msg,PHONE_NUMBER,
						'Yes',organisation_id))

				else:
					sent = 'N'
			#----------------------------sms-----------------------#

			#----------------------------mail----------------------#

			if MAIL_ID == 'string': 
				cursor.execute("""SELECT `email` FROM `retailer_store_stores` 
					WHERE `phoneno`=%s""",(PHONE_NUMBER))
				toMail = cursor.fetchone()

				if toMail['email'] == '' or  toMail == None:				
					cursor.execute("""SELECT `email` FROM `organisation_master` WHERE 
						`phoneno`=%s""",(PHONE_NUMBER))
					toMailcus = cursor.fetchone()
					if toMailcus:
						user_info = toMailcus['email']
					else:
						user_info = MAIL_ID
				else:
					user_info = toMail['email']
			else:
				user_info = MAIL_ID
			
			if user_info:				
				msg = MIMEMultipart()
				msg['Subject'] = 'Verification code'
				msg['From'] = EMAIL_ADDRESS
				msg['To'] = user_info
				html = """<html>
	                        <head>
	                        <title>E-Commerce.com</title>
	                        </head>
	                        <body>
	                        <p>
	                        Dear User,<br> <br>
	                        
	                        Your OTP is %s. This OTP is valid only for one time use.<br><br>
				            
				            Thank you for choosing E-Commerce<br><br><br>
	                        
	                        
	                        
	                        E-Commerce Support Team<br>
	                          E-mail: - support@ecommerce.com<br>
	                          Website: www.ecommerce.com<br>
	                            
	                        </p    
                            </body>
	                        </html>"""
				message = html % (otp)
				# print(message)
				part1 = MIMEText(message, 'html')
				msg.attach(part1)
				try:
					smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
					smtp.starttls()
					smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
					smtp.sendmail(EMAIL_ADDRESS, user_info, msg.as_string())
					
					res = {"status":'Success'}
					sent = 'Y'
					
				except Exception as e:
					res = {"status":'Failure'}
					sent = 'N'
					# raise e
				smtp.quit()
			

		#----------------------------mail----------------------#

		else:
			details = []

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "ECommerce OTP",
	                                "status": "success"
	                                },
				"responseList":details}), status.HTTP_200_OK

#----------------------------Generate-Otp--------------------------#

#----------------------Send-Otp---------------------#
@name_space.route("/sendOtp")
class sendOtp(Resource):
	@api.expect(sendotp_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()


		url = BASE_URL+"ecommerce_retail_store/EcommerceRetailStore/GenerateOTP"
		if details and "email" in details:
			post_data = {
						  "USER_ID": 0,
						  "organisation_id": 0,
						  "role_id": 0,
						  "FIRST_NAME": "string",
						  "LAST_NAME": "string",
						  "MAIL_ID": details['email'],
						  "Address": "string",
						  "PHONE_NUMBER": details['phoneno']
						}
		else:
			post_data = {
						  "USER_ID": 0,
						  "organisation_id": 0,
						  "role_id": 0,
						  "FIRST_NAME": "string",
						  "LAST_NAME": "string",
						  "MAIL_ID": "string",
						  "Address": "string",
						  "PHONE_NUMBER": details['phoneno']
						}



		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		post_response = requests.post(url, data=json.dumps(post_data), headers=headers)

		my_json_string = post_response.json()

		otpjson = my_json_string['responseList']['OTP']
		PHONE_NUMBER = my_json_string['responseList']['PHONE_NUMBER']

		if otpjson :
			return ({"attributes": {"status_desc": "Send Otp",
								"status": "success",
								"message":"Send Otp Successfully"
									},
				"responseList":{"otp":otpjson,"phoneno":PHONE_NUMBER}}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Send Otp",
								"status": "error",
								"message":"Having Issue"
									},
				"responseList":{}}), status.HTTP_200_OK	
#----------------------Send-Otp---------------------#

#----------------------Check-Otp---------------------#
@name_space.route("/CheckOtp")
class CheckOtp(Resource):
	@api.expect(checkotp_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()		

		get_otp_query = ("""SELECT *
					FROM `organisation_user_otp` WHERE `PHONE_NUMBER` = %s ORDER BY ID DESC LIMIT 1""")
		get_otp_data = (details['phoneno'])
		count_otp = cursor.execute(get_otp_query,get_otp_data)		

		if count_otp > 0:
			otp_data = cursor.fetchone()

			print(otp_data)

			if otp_data['OTP'] == int(details['otp']):
				
				otpjson = otp_data['OTP']
				PHONE_NUMBER = otp_data['PHONE_NUMBER']		

				if otpjson :
					return ({"attributes": {"status_desc": "Check Otp",
										"status": "success",
										"message":"Outhenticate Successfully"
											},
						"responseList":{"otp":otpjson,"phoneno":PHONE_NUMBER}}), status.HTTP_200_OK
			else:
				return ({"attributes": {"status_desc": "Check Otp",
									"status": "error",
									"message":"Otp Not Validated"
										},
					"responseList":{}}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Check Otp",
									"status": "error",
									"message":"Otp Not Validated"
										},
					"responseList":{}}), status.HTTP_200_OK	

#----------------------Check-Otp---------------------#

#----------------------General-Login---------------------#

@name_space.route("/GeneralLogin")	
class GeneralLogin(Resource):
	@api.expect(general_login_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		
		phoneno = details['phoneno']

		if details and "email" in details:
			email = details['email']
		else:
			email = ""

		if details and "device_token" in details:
			device_token = details['device_token']
		else:
			device_token = ""

		is_head_office_login = details['is_head_office_login']

		if details and "registration_type" in details:
			registration_type = details['registration_type']
		else:
			registration_type = ""
		

		if is_head_office_login == 1:
			url = BASE_URL+"ecommerce_organisation/EcommerceOrganisation/AddOrganisation"
			post_data = {
						  "phoneno": phoneno,
						  "email": email,
						  "device_token": device_token,
						  "registration_type": registration_type
						}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(url, data=json.dumps(post_data), headers=headers).json()

			return post_response	

		elif is_head_office_login == 0:
			url = BASE_URL+"ecommerce_retail_store/EcommerceRetailStore/Login"
			post_data = {
						  "phoneno": phoneno,
						  "device_token": device_token					  
						}
			print(post_data)

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(url, data=json.dumps(post_data), headers=headers).json()

			return post_response
		else:
			url = BASE_URL+"ecommerce_promoter/EcommercePromoter/PromoterLogin"
			post_data = {
						  "phoneno": phoneno
						}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(url, data=json.dumps(post_data), headers=headers).json()

			return post_response


#----------------------Retailer-Login---------------------#

@name_space.route("/Login")	
class Login(Resource):
	@api.expect(login_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		phoneno = details['phoneno']		

		get_query = ("""SELECT * FROM `retailer_store_stores` where `phoneno` = %s""")
		get_data = (phoneno)
		count_retailer_store = cursor.execute(get_query,get_data)

		if count_retailer_store > 0:
			login_data = cursor.fetchone()
			get_city_query = ("""SELECT * FROM `retailer_store` rs
								INNER JOIN `retailer_store_image` rsi ON rsi.`retailer_store_id` = rs.`retailer_store_id`
								where rs.`retailer_store_id` = %s""")
			get_city_data = (login_data['retailer_store_id'])
			count_city_data =  cursor.execute(get_city_query,get_city_data)
			if count_city_data > 0:
				city_data = cursor.fetchone()
				login_data['city'] = city_data['city']
				login_data['image'] = city_data['image']
			else:
				login_data['city'] = ""
				login_data['image'] = ""
			login_data['last_update_ts'] = str(login_data['last_update_ts'])


			get_query_organisation_login_data = ("""SELECT *					
						FROM `organisation_master`					
						WHERE `organisation_id` = %s """)
			getDataOrganisationLogin = (login_data['organisation_id'])
			cursor.execute(get_query_organisation_login_data,getDataOrganisationLogin)
			organisation_login_data = cursor.fetchone()

			login_data['organisation_id'] = organisation_login_data['organisation_id']
			login_data['organization_name'] = organisation_login_data['organization_name']
			login_data['logo'] = organisation_login_data['logo']
			login_data['email'] = organisation_login_data['email']
			login_data['org_password'] = organisation_login_data['org_password']
			login_data['phoneno'] = organisation_login_data['phoneno']
			login_data['area'] = organisation_login_data['area']
			login_data['city'] = organisation_login_data['city']
			login_data['pincode'] = organisation_login_data['pincode']
			login_data['gst_number'] = organisation_login_data['gst_number']
			login_data['currency'] = organisation_login_data['currency']
			login_data['instragram_link'] = organisation_login_data['instragram_link']
			login_data['privacy_and_return_policy'] = organisation_login_data['privacy_and_return_policy']
			login_data['about_user'] = organisation_login_data['about_user']
			login_data['ask_for_phone_no'] = organisation_login_data['ask_for_phone_no']
			login_data['allow_order_in_whats_app'] = organisation_login_data['allow_order_in_whats_app']
			login_data['registration_type'] = organisation_login_data['registration_type']
			login_data['organisation_code'] = organisation_login_data['organisation_code']
			login_data['whatsapp_no'] = organisation_login_data['whatsapp_no']
			login_data['app_link'] = organisation_login_data['app_link']

			get_otp_settings_query = ("""SELECT *				
									FROM `otp_settings`						
									WHERE `organisation_id` = %s """)
			getDataLogin = (login_data['organisation_id'])
			count_otp_setings = cursor.execute(get_otp_settings_query,getDataLogin)

			if count_otp_setings > 0:
				otp_settings_data = cursor.fetchone()
				login_data['otp_sent'] = otp_settings_data['otp_setting_value']
			else:
				login_data['otp_sent'] = 0

			get_signup_settings_query = ("""SELECT *				
									FROM `signup_settings`						
									WHERE `organisation_id` = %s """)
			getDataLogin = (login_data['organisation_id'])
			count_signup_setings = cursor.execute(get_signup_settings_query,getDataLogin)

			if count_signup_setings > 0:
				signup_settings_data = cursor.fetchone()
				login_data['is_mandatory'] = signup_settings_data['is_mandatory']
			else:
				login_data['is_mandatory'] = 0

			login_data['date_of_lastlogin'] = str(organisation_login_data['date_of_lastlogin'])				

			if organisation_login_data['organization_name'] :
				login_data['personal_website_link'] = organisation_login_data['personal_website_link']
			else:
				login_data['personal_website_link'] = ""

			login_data['is_head_office_login'] = 0

			if details and "device_token" in details:
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				saveDeviceTokenUrl = BASE_URL + "ret_notification/RetailerNotification/AddRetailStoreDeviceDetails"
				payloadpushData = {
					"device_type":"android",
					"device_token":details['device_token'],
					"retail_store_id":login_data['retailer_store_store_id'],
					"organisation_id": login_data['organisation_id']
				}

				saveDeviceToken = requests.post(saveDeviceTokenUrl,data=json.dumps(payloadpushData), headers=headers).json()

			return ({"attributes": {
				    		"status_desc": "login_details",
				    		"status": "success",
				    		"message":"Login Successfully"
				    	},
				    	"responseList":login_data}), status.HTTP_200_OK	

		else:
			login_data = {}

			return ({"attributes": {
				    		"status_desc": "login_details",
				    		"status": "error",
				    		"message":"Not Exsits"
				    	},
				    	"responseList":login_data}), status.HTTP_200_OK	

			


#----------------------Retailer-Login---------------------#

#---------------------------Retailer-Dashboard-Dtls-By-FilterKey-And-Retailer-Id-------------------------#
@name_space_dashboard.route("/RetailerDashboardDtlsByFilerKeyOrganizationwithdaterange/<string:filterkey>/<int:retailer_store_id>/<int:organisation_id>/<string:start_date>/<string:end_date>")	
class RetailerDashboardDtlsByFilerKeyOrganizationwithdaterange(Resource):
	def get(self,filterkey,retailer_store_id,organisation_id,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()

		if filterkey == 'today':
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			get_order_query = ("""SELECT count(`amount`)as total 
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) = %s
								""")
			get_oder_data = (organisation_id,organisation_id,retailer_store_id,today_date)

			order_count = cursor.execute(get_order_query,get_oder_data)
			order_data = cursor.fetchone()

			if order_data:				
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) = %s""")
			get_sales_data = (organisation_id,organisation_id,retailer_store_id,today_date)

			sales_count = cursor.execute(get_sales_query,get_sales_data)

			sales_data = cursor.fetchone()

			if sales_data['total'] !=None:
				sales = sales_data['total']
			else:
				sales = 0


			get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) = %s """)
			get_product_view_data =(organisation_id,today_date)	
			product_view_count = cur.execute(get_product_view_query,get_product_view_data)

			if product_view_count > 0:
				product_view_data = cur.fetchall()
				for key,data in enumerate(product_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						product_view_data[key]['is_retailer'] = 1
					else:
						product_view_data[key]['is_retailer'] = 0

				new_product_view_data = []
				for key,data in enumerate(product_view_data):
					if data['is_retailer'] == 1:
						new_product_view_data.append(product_view_data[key])

				prodview = len(new_product_view_data) 

			else:
				prodview = 0

			get_store_view_query = ("""SELECT * FROM `customer_store_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) = %s """)
			get_store_view_data =(organisation_id,today_date)	
			store_view_count = cur.execute(get_store_view_query,get_store_view_data)

			if store_view_count > 0:
				store_view_data = cur.fetchall()
				for key,data in enumerate(store_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						store_view_data[key]['is_retailer'] = 1
					else:
						store_view_data[key]['is_retailer'] = 0

				new_store_view_data = []
				for key,data in enumerate(store_view_data):
					if data['is_retailer'] == 1:
						new_store_view_data.append(store_view_data[key])

				storeview = len(new_store_view_data) 

			else:
				storeview = 0


		elif filterkey == 'yesterday':
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_order_query = ("""SELECT count(`amount`)as total 
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) = %s
								""")
			get_oder_data = (organisation_id,organisation_id,retailer_store_id,yesterday)

			order_count = cursor.execute(get_order_query,get_oder_data)
			print(cursor._last_executed)

			if order_count > 0 :
				order_data = cursor.fetchone()
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) = %s""")
			get_sales_data = (organisation_id,organisation_id,retailer_store_id,yesterday)

			sales_count = cursor.execute(get_sales_query,get_sales_data)

			sales_data = cursor.fetchone()

			if sales_data['total'] !=None:
				sales = sales_data['total']
			else:
				sales = 0

			get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) = %s """)
			get_product_view_data =(organisation_id,yesterday)	
			product_view_count = cur.execute(get_product_view_query,get_product_view_data)

			if product_view_count > 0:
				product_view_data = cur.fetchall()
				for key,data in enumerate(product_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						product_view_data[key]['is_retailer'] = 1
					else:
						product_view_data[key]['is_retailer'] = 0

				new_product_view_data = []
				for key,data in enumerate(product_view_data):
					if data['is_retailer'] == 1:
						new_product_view_data.append(product_view_data[key])

				prodview = len(new_product_view_data) 

			else:
				prodview = 0

			get_store_view_query = ("""SELECT * FROM `customer_store_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) = %s """)
			get_store_view_data =(organisation_id,yesterday)	
			store_view_count = cur.execute(get_store_view_query,get_store_view_data)

			if store_view_count > 0:
				store_view_data = cur.fetchall()
				for key,data in enumerate(store_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						store_view_data[key]['is_retailer'] = 1
					else:
						store_view_data[key]['is_retailer'] = 0

				new_store_view_data = []
				for key,data in enumerate(store_view_data):
					if data['is_retailer'] == 1:
						new_store_view_data.append(store_view_data[key])

				storeview = len(new_store_view_data) 

			else:
				storeview = 0

		elif filterkey == 'last 7 day':
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_order_query = ("""SELECT count(`amount`)as total 
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s
								""")
			get_oder_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			order_count = cursor.execute(get_order_query,get_oder_data)
			print(cursor._last_executed)

			if order_count > 0 :
				order_data = cursor.fetchone()
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s""")
			get_sales_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			sales_count = cursor.execute(get_sales_query,get_sales_data)

			sales_data = cursor.fetchone()

			if sales_data['total'] !=None:
				sales = sales_data['total']
			else:
				sales = 0

			get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")
			get_product_view_data =(organisation_id,start_date,end_date)	
			product_view_count = cur.execute(get_product_view_query,get_product_view_data)

			if product_view_count > 0:
				product_view_data = cur.fetchall()
				for key,data in enumerate(product_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						product_view_data[key]['is_retailer'] = 1
					else:
						product_view_data[key]['is_retailer'] = 0

				new_product_view_data = []
				for key,data in enumerate(product_view_data):
					if data['is_retailer'] == 1:
						new_product_view_data.append(product_view_data[key])

				prodview = len(new_product_view_data) 

			else:
				prodview = 0

			get_store_view_query = ("""SELECT * FROM `customer_store_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s """)
			get_store_view_data =(organisation_id,start_date,end_date)	
			store_view_count = cur.execute(get_store_view_query,get_store_view_data)

			if store_view_count > 0:
				store_view_data = cur.fetchall()
				for key,data in enumerate(store_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						store_view_data[key]['is_retailer'] = 1
					else:
						store_view_data[key]['is_retailer'] = 0

				new_store_view_data = []
				for key,data in enumerate(store_view_data):
					if data['is_retailer'] == 1:
						new_store_view_data.append(store_view_data[key])

				storeview = len(new_store_view_data) 

			else:
				storeview = 0

		elif filterkey == 'this month':
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_order_query = ("""SELECT count(`amount`)as total 
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s
								""")
			get_oder_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			order_count = cursor.execute(get_order_query,get_oder_data)
			print(cursor._last_executed)

			if order_count > 0 :
				order_data = cursor.fetchone()
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s""")
			get_sales_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			sales_count = cursor.execute(get_sales_query,get_sales_data)

			sales_data = cursor.fetchone()

			if sales_data['total'] !=None:
				sales = sales_data['total']
			else:
				sales = 0

			get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")
			get_product_view_data =(organisation_id,start_date,end_date)	
			product_view_count = cur.execute(get_product_view_query,get_product_view_data)

			if product_view_count > 0:
				product_view_data = cur.fetchall()
				for key,data in enumerate(product_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						product_view_data[key]['is_retailer'] = 1
					else:
						product_view_data[key]['is_retailer'] = 0

				new_product_view_data = []
				for key,data in enumerate(product_view_data):
					if data['is_retailer'] == 1:
						new_product_view_data.append(product_view_data[key])

				prodview = len(new_product_view_data) 

			else:
				prodview = 0

			get_store_view_query = ("""SELECT * FROM `customer_store_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")
			get_store_view_data =(organisation_id,start_date,end_date)	
			store_view_count = cur.execute(get_store_view_query,get_store_view_data)

			if store_view_count > 0:
				store_view_data = cur.fetchall()
				for key,data in enumerate(store_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						store_view_data[key]['is_retailer'] = 1
					else:
						store_view_data[key]['is_retailer'] = 0

				new_store_view_data = []
				for key,data in enumerate(store_view_data):
					if data['is_retailer'] == 1:
						new_store_view_data.append(store_view_data[key])

				storeview = len(new_store_view_data) 

			else:
				storeview = 0

		elif filterkey == 'lifetime':
			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_order_query = ("""SELECT count(`amount`)as total 
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s
								""")
			get_oder_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			order_count = cursor.execute(get_order_query,get_oder_data)
			print(cursor._last_executed)

			if order_count > 0 :
				order_data = cursor.fetchone()
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s""")
			get_sales_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			sales_count = cursor.execute(get_sales_query,get_sales_data)

			sales_data = cursor.fetchone()

			if sales_data['total'] !=None:
				sales = sales_data['total']
			else:
				sales = 0

			get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")
			get_product_view_data =(organisation_id,start_date,end_date)	
			product_view_count = cur.execute(get_product_view_query,get_product_view_data)

			if product_view_count > 0:
				product_view_data = cur.fetchall()
				for key,data in enumerate(product_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						product_view_data[key]['is_retailer'] = 1
					else:
						product_view_data[key]['is_retailer'] = 0

				new_product_view_data = []
				for key,data in enumerate(product_view_data):
					if data['is_retailer'] == 1:
						new_product_view_data.append(product_view_data[key])

				prodview = len(new_product_view_data)
			else:
				prodview = 0

			get_store_view_query = ("""SELECT * FROM `customer_store_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")
			get_store_view_data =(organisation_id,start_date,end_date)	
			store_view_count = cur.execute(get_store_view_query,get_store_view_data)

			if store_view_count > 0:
				store_view_data = cur.fetchall()
				for key,data in enumerate(store_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						store_view_data[key]['is_retailer'] = 1
					else:
						store_view_data[key]['is_retailer'] = 0

				new_store_view_data = []
				for key,data in enumerate(store_view_data):
					if data['is_retailer'] == 1:
						new_store_view_data.append(store_view_data[key])

				storeview = len(new_store_view_data) 

			else:
				storeview = 0

		elif filterkey == 'custom date':
			if start_date != 'NA' and end_date != 'NA':

				get_order_query = ("""SELECT count(`amount`)as total 
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s
								""")
				get_oder_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

				order_count = cursor.execute(get_order_query,get_oder_data)
			

				if order_count > 0 :
					order_data = cursor.fetchone()
					orders = order_data['total']
				else:
					orders = 0

				get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s""")
				get_sales_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

				sales_count = cursor.execute(get_sales_query,get_sales_data)

				sales_data = cursor.fetchone()

				if sales_data['total'] !=None:
					sales = sales_data['total']
				else:
					sales = 0

				get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")
				get_product_view_data =(organisation_id,start_date,end_date)	
				product_view_count = cur.execute(get_product_view_query,get_product_view_data)

				if product_view_count > 0:
					product_view_data = cur.fetchall()
					for key,data in enumerate(product_view_data):
						get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
						get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
						count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
						print(cursor._last_executed)

						if count_user_retailer > 0:
							product_view_data[key]['is_retailer'] = 1
						else:
							product_view_data[key]['is_retailer'] = 0

					new_product_view_data = []
					for key,data in enumerate(product_view_data):
						if data['is_retailer'] == 1:
							new_product_view_data.append(product_view_data[key])

					prodview = len(new_product_view_data)
				else:
					prodview = 0

				get_store_view_query = ("""SELECT * FROM `customer_store_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")
				get_store_view_data =(organisation_id,start_date,end_date)	
				store_view_count = cur.execute(get_store_view_query,get_store_view_data)

				if store_view_count > 0:
					store_view_data = cur.fetchall()
					for key,data in enumerate(store_view_data):
						get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
						get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
						count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
						print(cursor._last_executed)

						if count_user_retailer > 0:
							store_view_data[key]['is_retailer'] = 1
						else:
							store_view_data[key]['is_retailer'] = 0

					new_store_view_data = []
					for key,data in enumerate(store_view_data):
						if data['is_retailer'] == 1:
							new_store_view_data.append(store_view_data[key])

					storeview = len(new_store_view_data) 

				else:
					storeview = 0

			else:
				orders = 0
				sales = 0
				prodview = 0
				storeview = 0


		return ({"attributes": {
		    		"status_desc": "Retailer Dashborad Details",
		    		"status": "success"
		    	},
		    	"responseList":{
		    					 "orders":orders,
		    					 "sales": sales,
		    					 "storeview":storeview,
		    					 "productview":prodview,
						    	}
						    	}), status.HTTP_200_OK

#---------------------------Retailer-Dashboard-Dtls-By-FilterKey-And-Retailer-Id-------------------------#

#----------------------Search-Order-History---------------------#

@name_space_order_history.route("/searchorderHistory/<string:searchkey>/<int:organisation_id>/<int:retailer_store_id>/<int:page>")	
class searchorderHistory(Resource):
	def get(self,searchkey,organisation_id,retailer_store_id,page):
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
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id` 
			WHERE  ipr.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and ( ipr.`transaction_id` LIKE %s or a.`first_name` LIKE %s or a.`phoneno` LIKE %s or a.`last_name` LIKE %s or ipr.`delivery_option` LIKE %s or `order_payment_status` LIKE %s) LIMIT %s,20""")

		get_data = (organisation_id,organisation_id,retailer_store_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%",offset)
		cursor.execute(get_query,get_data)
		print(cursor._last_executed)

		order_data = cursor.fetchall()

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

#------------------------------Order-Detail-By-Date-And-Organisation-And-Store----------------------------#
@name_space_order_history.route("/OrderDtlsByDateOrganizationId/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>")	
class OrderDtlsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,
				concat(`first_name`,' ',`last_name`)as name,anniversary, `phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,ipr.`last_update_ts`
				FROM `order_product` op 
				INNER join `customer_product_mapping` cpm on op.`customer_mapping_id`=cpm.`mapping_id`
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = cpm.`customer_id`   
				INNER join `admins` ad on cpm.`customer_id`=ad.`admin_id` 
				INNER join `product_meta` pm on cpm.`product_meta_id`=pm.`product_meta_id` 
				INNER join `product` pd on pm.`product_id`=pd.`product_id` 
				INNER join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` 
				WHERE op.`organisation_id`=%s and date(op.`last_update_ts`)=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""",(organisation_id,today,organisation_id,retailer_store_id))

			orderdtls = cursor.fetchall()
			if orderdtls:
				for i in range(len(orderdtls)):
					orderdtls[i]['last_update_ts'] = orderdtls[i]['last_update_ts'].isoformat()
					
					orderdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(orderdtls[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						orderdtls[i]['customertype'] = customertype['customer_type']
					else:
						orderdtls[i]['customertype'] = ''

					if orderdtls[i]['name'] == None or orderdtls[i]['phoneno'] == None or orderdtls[i]['status'] == None or orderdtls[i]['order_payment_status'] == None or orderdtls[i]['delivery_option'] == None:
						orderdtls[i]['name'] = "" 
						orderdtls[i]['phoneno'] = ""
						orderdtls[i]['status'] = ""
						orderdtls[i]['order_payment_status'] = ""
						orderdtls[i]['delivery_option'] = ""

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					elif orderdtls[i]['order_payment_status'] == 4:
						orderdtls[i]['order_payment_status'] = 'Booked'

					else:
						orderdtls[i]['order_payment_status'] = ""

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					elif orderdtls[i]['delivery_option'] == 2:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'
			else:
				orderdtls = []
			
		elif filterkey == 'yesterday':
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,
				concat(`first_name`,' ',`last_name`)as name,anniversary,`phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,op.`last_update_ts`
				FROM `order_product` op 
				Left join `customer_product_mapping` cpm on op.`customer_mapping_id`=cpm.`mapping_id` 
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = cpm.`customer_id`
				Left join `admins` ad on cpm.`customer_id`=ad.`admin_id` 
				Left join `product_meta` pm on cpm.`product_meta_id`=pm.`product_meta_id` 
				INNER join `product` pd on pm.`product_id`=pd.`product_id` 
				Left join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` 
				WHERE op.`organisation_id`=%s and  urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				date(op.`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id,organisation_id,retailer_store_id))

			orderdtls = cursor.fetchall()
			if orderdtls:
				for i in range(len(orderdtls)):
					orderdtls[i]['last_update_ts'] = orderdtls[i]['last_update_ts'].isoformat()
					
					orderdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(orderdtls[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						orderdtls[i]['customertype'] = customertype['customer_type']
					else:
						orderdtls[i]['customertype'] = ''
						
					if orderdtls[i]['name'] == None or orderdtls[i]['phoneno'] == None or orderdtls[i]['status'] == None or orderdtls[i]['order_payment_status'] == None or orderdtls[i]['delivery_option'] == None:
						orderdtls[i]['name'] = "" 
						orderdtls[i]['phoneno'] = ""
						orderdtls[i]['status'] = ""
						orderdtls[i]['order_payment_status'] = ""
						orderdtls[i]['delivery_option'] = ""

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					elif orderdtls[i]['order_payment_status'] == 4:
						orderdtls[i]['order_payment_status'] = 'Booked'

					else:
						orderdtls[i]['order_payment_status'] = ""

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					elif orderdtls[i]['delivery_option'] == 2:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'

			else:
				orderdtls = []

		elif filterkey == 'last 7 day':
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,
				concat(`first_name`,' ',`last_name`)as name,anniversary,`phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,ipr.`last_update_ts`
				FROM `order_product` op 
				INNER join `customer_product_mapping` cpm on op.`customer_mapping_id`=cpm.`mapping_id`
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = cpm.`customer_id` 
				INNER join `admins` ad on cpm.`customer_id`=ad.`admin_id` 
				INNER join `product_meta` pm on cpm.`product_meta_id`=pm.`product_meta_id` 
				INNER join `product` pd on pm.`product_id`=pd.`product_id` 
				INNER join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` WHERE 
				op.`organisation_id`=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				date(op.`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(op.`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id,organisation_id,retailer_store_id))

			orderdtls = cursor.fetchall()
			if orderdtls:
				for i in range(len(orderdtls)):
					orderdtls[i]['last_update_ts'] = orderdtls[i]['last_update_ts'].isoformat()
					
					orderdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(orderdtls[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						orderdtls[i]['customertype'] = customertype['customer_type']
					else:
						orderdtls[i]['customertype'] = ''
						
					if orderdtls[i]['name'] == None or orderdtls[i]['phoneno'] == None or orderdtls[i]['status'] == None or orderdtls[i]['order_payment_status'] == None or orderdtls[i]['delivery_option'] == None:
						orderdtls[i]['name'] = "" 
						orderdtls[i]['phoneno'] = ""
						orderdtls[i]['status'] = ""
						orderdtls[i]['order_payment_status'] = ""
						orderdtls[i]['delivery_option'] = ""

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					elif orderdtls[i]['order_payment_status'] == 4:
						orderdtls[i]['order_payment_status'] = 'Booked'

					else:
						orderdtls[i]['order_payment_status'] = ""

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					elif orderdtls[i]['delivery_option'] == 2:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'

			else:
				orderdtls = []
			
		
		elif filterkey == 'this month':
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,
				concat(`first_name`,' ',`last_name`)as name,anniversary,`phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,ipr.`last_update_ts`
				FROM `order_product` op 
				INNER join `customer_product_mapping` cpm on op.`customer_mapping_id`=cpm.`mapping_id` 
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = cpm.`customer_id`
				INNER join `admins` ad on cpm.`customer_id`=ad.`admin_id` 
				INNER join `product_meta` pm on cpm.`product_meta_id`=pm.`product_meta_id` 
				INNER join `product` pd on pm.`product_id`=pd.`product_id` 
				INNER join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` 
				WHERE op.`organisation_id`=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				date(op.`last_update_ts`) between %s and %s""",(organisation_id,organisation_id,retailer_store_id,stday,today))

			orderdtls = cursor.fetchall()
			if orderdtls:
				for i in range(len(orderdtls)):
					orderdtls[i]['last_update_ts'] = orderdtls[i]['last_update_ts'].isoformat()
					
					orderdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(orderdtls[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						orderdtls[i]['customertype'] = customertype['customer_type']
					else:
						orderdtls[i]['customertype'] = ''
						
					if orderdtls[i]['name'] == None or orderdtls[i]['phoneno'] == None or orderdtls[i]['status'] == None or orderdtls[i]['order_payment_status'] == None or orderdtls[i]['delivery_option'] == None:
						orderdtls[i]['name'] = "" 
						orderdtls[i]['phoneno'] = ""
						orderdtls[i]['status'] = ""
						orderdtls[i]['order_payment_status'] = ""
						orderdtls[i]['delivery_option'] = ""

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					elif orderdtls[i]['order_payment_status'] == 4:
						orderdtls[i]['order_payment_status'] = 'Booked'

					else:
						orderdtls[i]['order_payment_status'] = ""

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					elif orderdtls[i]['delivery_option'] == 2:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'

			else:
				orderdtls = []


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,
				concat(`first_name`,' ',`last_name`)as name,anniversary,`phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,ipr.`last_update_ts`
				FROM `order_product` op 
				INNER join `customer_product_mapping` cpm on op.`customer_mapping_id`=cpm.`mapping_id` 
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = cpm.`customer_id`
				INNER join `admins` ad on cpm.`customer_id`=ad.`admin_id` 
				INNER join `product_meta` pm on cpm.`product_meta_id`=pm.`product_meta_id` 
				INNER join `product` pd on pm.`product_id`=pd.`product_id` 
				INNER join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` 
				WHERE op.`organisation_id`=%s and  urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and 
				date(op.`last_update_ts`) between %s and %s""",(organisation_id,organisation_id,retailer_store_id,slifetime,today))

			orderdtls = cursor.fetchall()
			if orderdtls:
				for i in range(len(orderdtls)):
					orderdtls[i]['last_update_ts'] = orderdtls[i]['last_update_ts'].isoformat()
					
					orderdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(orderdtls[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						orderdtls[i]['customertype'] = customertype['customer_type']
					else:
						orderdtls[i]['customertype'] = ''
						
					if orderdtls[i]['name'] == None or orderdtls[i]['phoneno'] == None or orderdtls[i]['status'] == None or orderdtls[i]['order_payment_status'] == None or orderdtls[i]['delivery_option'] == None:
						orderdtls[i]['name'] = "" 
						orderdtls[i]['phoneno'] = ""
						orderdtls[i]['status'] = ""
						orderdtls[i]['order_payment_status'] = ""
						orderdtls[i]['delivery_option'] = ""

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					elif orderdtls[i]['order_payment_status'] == 4:
						orderdtls[i]['order_payment_status'] = 'Booked'

					else:
						orderdtls[i]['order_payment_status'] = ""

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					elif orderdtls[i]['delivery_option'] == 2:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'

			else:
				orderdtls = []

		else:
			orderdtls = []
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Order Details",
		    		"status": "success"
		    	},
		    	"responseList": orderdtls}), status.HTTP_200_OK

#------------------------------Order-Detail-By-Date-And-Organisation-And-Store----------------------------#

#----------------------------Order-Status-Details-By-Organisation_Id-And-Retail-Store--------------------------#
@name_space_order_history.route("/OrderStatusDtlsByDateOrganisationId/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>")	
class OrderStatusDtlsByDateOrganisationId(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT `orderstatus_id`,`order_status` FROM 
				`order_status_master`""")

			statusList = cursor.fetchall()
			for i in range(len(statusList)):
				cursor.execute("""SELECT count(ipr.`request_id`)as total FROM 
					`instamojo_payment_request` ipr
					INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = ipr.`user_id`
					WHERE ipr.`status`=%s and 
					ipr.`organisation_id`=%s and date(ipr.`last_update_ts`)=%s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s""",
					(statusList[i]['order_status'],organisation_id,today,retailer_store_id,organisation_id))

				Count = cursor.fetchone()
				if Count:
					statusList[i]['count'] = Count['total']

				else:
					statusList[i]['count'] = 0


		elif filterkey == 'yesterday':
			cursor.execute("""SELECT `orderstatus_id`,`order_status` FROM 
				`order_status_master`""")

			statusList = cursor.fetchall()
			for i in range(len(statusList)):
				cursor.execute("""SELECT count(ipr.`request_id`)as total 
					FROM `instamojo_payment_request` ipr
					INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = ipr.`user_id`
					WHERE ipr.`status`=%s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
					ipr.`organisation_id`=%s and date(ipr.`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",
					(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id))

				Count = cursor.fetchone()
				if Count:
					statusList[i]['count'] = Count['total']

				else:
					statusList[i]['count'] = 0

			
		elif filterkey == 'last 7 days':
			cursor.execute("""SELECT `orderstatus_id`,`order_status` FROM 
				`order_status_master`""")

			statusList = cursor.fetchall()
			for i in range(len(statusList)):
				cursor.execute("""SELECT count(ipr.`request_id`)as total 
					FROM `instamojo_payment_request` ipr
					INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = ipr.`user_id`
					WHERE ipr.`status`=%s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
					ipr.`organisation_id`=%s and date(ipr.`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
	        		date(ipr.`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id))

				Count = cursor.fetchone()
				if Count:
					statusList[i]['count'] = Count['total']

				else:
					statusList[i]['count'] = 0

		
		elif filterkey == 'this month':
			cursor.execute("""SELECT `orderstatus_id`,`order_status` FROM 
				`order_status_master`""")

			statusList = cursor.fetchall()
			for i in range(len(statusList)):
				cursor.execute("""SELECT count(ipr.`request_id`)as total 
					FROM `instamojo_payment_request` ipr
					INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = ipr.`user_id`
					WHERE ipr.`status`=%s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
					ipr.`organisation_id`=%s and date(ipr.`last_update_ts`) between %s and %s""",
					(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id,stday,today))

				Count = cursor.fetchone()
				if Count:
					statusList[i]['count'] = Count['total']

				else:
					statusList[i]['count'] = 0


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			
			cursor.execute("""SELECT `orderstatus_id`,`order_status` FROM 
				`order_status_master`""")

			statusList = cursor.fetchall()
			for i in range(len(statusList)):
				cursor.execute("""SELECT count(ipr.`request_id`)as total 
					FROM `instamojo_payment_request` ipr
					INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = ipr.`user_id`
					WHERE ipr.`status`=%s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
					ipr.`organisation_id`=%s and date(ipr.`last_update_ts`) between %s and %s""",
					(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id,slifetime,today))

				Count = cursor.fetchone()
				if Count:
					statusList[i]['count'] = Count['total']

				else:
					statusList[i]['count'] = 0
				
		else:
			statusList = []

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Order Status Details",
		    		"status": "success"
		    	},
		    	"responseList": statusList }), status.HTTP_200_OK

#----------------------------Order-Status-Details-By-Organisation_Id-And-Retail-Store--------------------------#

#--------------------------------Order-Status-Details-By-Organisation-Id------------------------------------#
@name_space_order_history.route("/OrderStatusDtlsByOrganisationId/<int:organisation_id>/<int:retailer_store_id>")	
class OrderStatusDtlsByOrganisationId(Resource):
	def get(self,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `orderstatus_id`,`order_status`,
			color FROM `order_status_master` order by last_update_id asc""")

		statusList = cursor.fetchall()
		for i in range(len(statusList)):

			cursor.execute("""SELECT count(ipr.`request_id`)as total 
				FROM `instamojo_payment_request` ipr
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = ipr.`user_id`
				WHERE ipr.`status`=%s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and 
				ipr.`organisation_id`=%s""",(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id))

			Count = cursor.fetchone()
			if Count:
				statusList[i]['count'] = Count['total']

			else:
				statusList[i]['count'] = 0

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Order Status Details",
		    		"status": "success"
		    	},
		    	"responseList": statusList }), status.HTTP_200_OK

#--------------------------------Order-Status-Details-By-Organisation-Id------------------------------------#

#-------------------------------------Customer-Details-By-Date-OrganizationId-And-Retailstore-------------------------------#
@name_space_customer_list.route("/CustomerDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>")	
class CustomerDetailsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,a.`organisation_id`,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s""",(organisation_id,organisation_id,retailer_store_id,today))
			customerdtls = cursor.fetchall()
			if customerdtls:
				for i in range(len(customerdtls)):
					customerdtls[i]['date_of_creation'] = customerdtls[i]['date_of_creation'].isoformat()
					
					customerdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(customerdtls[i]['admin_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						customerdtls[i]['customertype'] = customertype['customer_type']
					else:
						customerdtls[i]['customertype'] = ''

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (customerdtls[i]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						customerdtls[i]['retailer_city'] = city_data['retailer_city']
						customerdtls[i]['retailer_address'] = city_data['retailer_address']
					else:
						customerdtls[i]['retailer_city'] = ""
						customerdtls[i]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (customerdtls[i]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						customerdtls[i]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						customerdtls[i]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (customerdtls[i]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						customerdtls[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						customerdtls[i]['enquiery_count'] = 0
			else:
				customerdtls = []
			

		elif filterkey == 'yesterday':
			cursor.execute("""SELECT  `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,a.`organisation_id`,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and 
				date(`date_of_creation`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id,organisation_id,retailer_store_id))

			customerdtls = cursor.fetchall()
			if customerdtls:
				for i in range(len(customerdtls)):
					customerdtls[i]['date_of_creation'] = customerdtls[i]['date_of_creation'].isoformat()
					
					customerdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(customerdtls[i]['admin_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						customerdtls[i]['customertype'] = customertype['customer_type']
					else:
						customerdtls[i]['customertype'] = ''


					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (customerdtls[i]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						customerdtls[i]['retailer_city'] = city_data['retailer_city']
						customerdtls[i]['retailer_address'] = city_data['retailer_address']
					else:
						customerdtls[i]['retailer_city'] = ""
						customerdtls[i]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (customerdtls[i]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						customerdtls[i]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						customerdtls[i]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (customerdtls[i]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						customerdtls[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						customerdtls[i]['enquiery_count'] = 0
			else:
				customerdtls = []

		elif filterkey == 'last 7 days':
			cursor.execute("""SELECT  `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,a.`organisation_id`,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and a.`status`=1 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				date(a.`date_of_creation`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(a.`date_of_creation`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id,organisation_id,retailer_store_id))

			customerdtls = cursor.fetchall()
			if customerdtls:
				for i in range(len(customerdtls)):
					customerdtls[i]['date_of_creation'] = customerdtls[i]['date_of_creation'].isoformat()
					
					customerdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(customerdtls[i]['admin_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						customerdtls[i]['customertype'] = customertype['customer_type']
					else:
						customerdtls[i]['customertype'] = ''

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (customerdtls[i]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						customerdtls[i]['retailer_city'] = city_data['retailer_city']
						customerdtls[i]['retailer_address'] = city_data['retailer_address']
					else:
						customerdtls[i]['retailer_city'] = ""
						customerdtls[i]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (customerdtls[i]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						customerdtls[i]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						customerdtls[i]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (customerdtls[i]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						customerdtls[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						customerdtls[i]['enquiery_count'] = 0
			else:
				customerdtls = []
			

		elif filterkey == 'this month':
			cursor.execute("""SELECT  `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,a.`organisation_id`,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and a.`status`=1 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				date(a.`date_of_creation`) between %s and %s""",(organisation_id,organisation_id,retailer_store_id,stday,today))

			customerdtls = cursor.fetchall()
			if customerdtls:
				for i in range(len(customerdtls)):
					customerdtls[i]['date_of_creation'] = customerdtls[i]['date_of_creation'].isoformat()
					
					customerdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(customerdtls[i]['admin_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						customerdtls[i]['customertype'] = customertype['customer_type']
					else:
						customerdtls[i]['customertype'] = ''

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (customerdtls[i]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						customerdtls[i]['retailer_city'] = city_data['retailer_city']
						customerdtls[i]['retailer_address'] = city_data['retailer_address']
					else:
						customerdtls[i]['retailer_city'] = ""
						customerdtls[i]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (customerdtls[i]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						customerdtls[i]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						customerdtls[i]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (customerdtls[i]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						customerdtls[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						customerdtls[i]['enquiery_count'] = 0
			else:
				customerdtls = []


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			
			cursor.execute("""SELECT  `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,a.`organisation_id`,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and a.`status`=1 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				date(a.`date_of_creation`) between %s and %s""",(organisation_id,organisation_id,retailer_store_id,slifetime,today))

			customerdtls = cursor.fetchall()
			if customerdtls:
				for i in range(len(customerdtls)):
					customerdtls[i]['date_of_creation'] = customerdtls[i]['date_of_creation'].isoformat()
			
					customerdtls[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(customerdtls[i]['admin_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						customerdtls[i]['customertype'] = customertype['customer_type']
					else:
						customerdtls[i]['customertype'] = ''

					get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
					get_city_data = (customerdtls[i]['admin_id'],organisation_id)
					count_city = cursor.execute(get_city_query,get_city_data)						

					if count_city > 0:
						city_data = cursor.fetchone()
						customerdtls[i]['retailer_city'] = city_data['retailer_city']
						customerdtls[i]['retailer_address'] = city_data['retailer_address']
					else:
						customerdtls[i]['retailer_city'] = ""
						customerdtls[i]['retailer_address'] = ""

					get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
					get_exchange_count_data = (customerdtls[i]['admin_id'],organisation_id)
					exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

					if exchange_count > 0:
						exchange_count_data =  cursor.fetchone()
						customerdtls[i]['exchange_count'] = exchange_count_data['exchane_count']
					else:
						customerdtls[i]['exchange_count'] = 0

					get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
					get_enquiery_count_data = (customerdtls[i]['admin_id'],organisation_id)
					enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

					if enquiery_count > 0:
						enquiery_count_data = cursor.fetchone()
						customerdtls[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
					else:
						customerdtls[i]['enquiery_count'] = 0
			else:
				customerdtls = []

		else:
			customerdtls = []
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Registered Customer Details",
		    		"status": "success"
		    	},
		    	"responseList":customerdtls }), status.HTTP_200_OK

#-------------------------------------Customer-Details-By-Date-OrganizationId-And-Retailstore-------------------------------#

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#

@name_space_customer_list.route("/CustomerCountWithOrganisationAndRetailStore/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>")	
class CustomerCountWithOrganisationAndRetailStore(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = ecommerce_analytics()
		cur = conn.cursor()

		registation_data = {}
		notification_data = {}
		loggedin_data = {}
		demo_data = {}
		total_login_user_from_registration_data = {}
		total_never_login_user_from_registration_data = {}

		if filterkey == 'today':
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,today_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(DISTINCT(an.`U_id`))as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,today_date,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`)=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (today_date,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) = %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,today_date,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,today_date)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,today_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []

		if filterkey == 'yesterday':
			
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,yesterday)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(DISTINCT(an.`U_id`))as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,yesterday,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`)=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (yesterday,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) = %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,yesterday,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,yesterday)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,yesterday)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []


		if filterkey == 'last 7 days':
			
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(DISTINCT(an.`U_id`))as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s  and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (start_date,end_date,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >=%s and date(a.`date_of_creation`) <=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []


		if filterkey == 'this month':
			
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(DISTINCT(an.`U_id`))as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s  and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (start_date,end_date,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >=%s and date(a.`date_of_creation`) <=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`user_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []	

		if filterkey == 'lifetime':

			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(DISTINCT(an.`U_id`))as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s  and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (start_date,end_date,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >=%s and date(a.`date_of_creation`) <=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []

		return ({"attributes": {
		    		"status_desc": "Customer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{"registation_data":registation_data,"notification_data":notification_data,"loggedin_data":loggedin_data,"demo_data":demo_data,"total_login_user_from_registration_data":total_login_user_from_registration_data,"total_never_login_user_from_registration_data":total_never_login_user_from_registration_data} }), status.HTTP_200_OK

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#

@name_space_customer_list.route("/CustomerCountWithOrganisationAndRetailStoreWithDateRange/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>/<string:start_date>/<string:end_date>")	
class CustomerCountWithOrganisationAndRetailStoreWithDateRange(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = ecommerce_analytics()
		cur = conn.cursor()

		registation_data = {}
		notification_data = {}
		email_data = {}
		loggedin_data = {}
		demo_data = {}
		total_login_user_from_registration_data = {}
		total_never_login_user_from_registration_data = {}

		if filterkey == 'today':
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,today_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(an.`U_id`) as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,today_date,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_email_customer_query = ("""SELECT count( ce.`customer_id`) as total_email_customer FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_email_customer_data = (organisation_id,today_date,organisation_id,retailer_store_id)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			email_data['store_data'] = []

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`)=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (today_date,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) = %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,today_date,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,today_date)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,today_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []

		if filterkey == 'yesterday':
			
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,yesterday)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(an.`U_id`) as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,yesterday,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_email_customer_query = ("""SELECT count( ce.`customer_id`) as total_email_customer FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_email_customer_data = (organisation_id,yesterday,organisation_id,retailer_store_id)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			email_data['store_data'] = []

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`)=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (yesterday,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) = %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,yesterday,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,yesterday)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`)=%s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,yesterday)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []


		if filterkey == 'last 7 days':
			
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(an.`U_id`)as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s  and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_email_customer_query = ("""SELECT count( ce.`customer_id`) as total_email_customer FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) >= %s and date(ce.`Last_Update_TS`) <= %sand urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_email_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			email_data['store_data'] = []

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (start_date,end_date,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >=%s and date(a.`date_of_creation`) <=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []


		if filterkey == 'this month':
			
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(an.`U_id`)as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s  and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_email_customer_query = ("""SELECT count( ce.`customer_id`) as total_email_customer FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) >= %s and date(ce.`Last_Update_TS`) <= %sand urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_email_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (start_date,end_date,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >=%s and date(a.`date_of_creation`) <=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`user_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []	

		if filterkey == 'lifetime':

			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(an.`U_id`)as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s  and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_email_customer_query = ("""SELECT count( ce.`customer_id`) as total_email_customer FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) >= %s and date(ce.`Last_Update_TS`) <= %sand urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_email_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (start_date,end_date,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >=%s and date(a.`date_of_creation`) <=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []

		if filterkey == 'custom date':			
			
			end_date = end_date
			
			start_date = start_date

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(a.`admin_id`)as total
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s""")
			get_registerd_customer_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
			else:
				registation_data['total_customer_count'] = 0
			
			registation_data['store_data'] = []

			get_notify_customer_query = ("""SELECT count(an.`U_id`)as total_notify_customer FROM 
				`app_notification` an
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = an.`U_id`
				WHERE an.`organisation_id`=%s and an.`destination_type` = 2 and date(an.`Last_Update_TS`) >= %s and date(an.`Last_Update_TS`) <= %s  and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			notification_data['store_data'] = []

			get_email_customer_query = ("""SELECT count( ce.`customer_id`) as total_email_customer FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) >= %s and date(ce.`Last_Update_TS`) <= %sand urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """)
			get_email_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0""")
			store_analytics_view_data = (start_date,end_date,organisation_id)
			count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

			if count_store_analytics_view > 0:
				store_analytics_view = cur.fetchall()

				print(store_analytics_view)

				for sakey,sadata in enumerate(store_analytics_view):

					get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
					get_customer_retailer_data = (organisation_id,retailer_store_id,sadata['customer_id'])

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						store_analytics_view[sakey]['s_view'] = 1
					else:
						store_analytics_view[sakey]['s_view'] = 0
							
				new_store_analytics_view = []
				for nsakey,nsadata in enumerate(store_analytics_view):
					if nsadata['s_view'] == 1:
						new_store_analytics_view.append(store_analytics_view[nsakey])
			else:
				new_store_analytics_view = []

			loggedin_data['total_customer_count'] = len(new_store_analytics_view)
			loggedin_data['store_data'] = []

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 				
				FROM `customer_remarks` cr 
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = cr.`customer_id`
				WHERE cr.`customer_id`!=0 and urm.`organisation_id`=%s and date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s
				and cr.`organisation_id` = %s and urm.`retailer_store_id` = %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			demo_data['store_data']	= []

			get_registed_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and 
				urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >=%s and date(a.`date_of_creation`) <=%s and a.`loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)			

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			total_login_user_from_registration_data['store_data'] = []

			get_registed_never_login_customer_query = ("""SELECT count(a.`admin_id`)as total 
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE a.`organisation_id`=%s and a.`role_id`=4 and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				a.`status`=1 and date(a.`date_of_creation`) >= %s and date(a.`date_of_creation`) <= %s and a.`loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			total_never_login_user_from_registration_data['store_data'] = []

		return ({"attributes": {
		    		"status_desc": "Customer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{"registation_data":registation_data,"notification_data":notification_data,"email_data":email_data,"loggedin_data":loggedin_data,"demo_data":demo_data,"total_login_user_from_registration_data":total_login_user_from_registration_data,"total_never_login_user_from_registration_data":total_never_login_user_from_registration_data} }), status.HTTP_200_OK

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#

#----------------------------------------------------#
@name_space_customer_list.route("/CustomerSearchingByPhoneNoOrName/<string:searchkey>/<int:organisation_id>/<int:retailer_store_id>")	
class CustomerSearchingByPhoneNoOrName(Resource):
	def get(self,searchkey,organisation_id,retailer_store_id):
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
					`dob`,`phoneno`,profile_image,a.`organisation_id`,`pincode`,date_of_creation,loggedin_status,wallet FROM `admins` a
					INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
					WHERE locate(%s,a.`first_name`) and a.`role_id`=4 and 
					a.`status`=1 and a.`organisation_id`=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s """,(firstname,organisation_id,organisation_id,retailer_store_id))

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
						`dob`,`phoneno`,profile_image,a.`organisation_id`,`pincode`,date_of_creation,loggedin_status,wallet FROM `admins` a
						INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
						WHERE locate(%s,a.`last_name`) and a.`role_id`=4 and 
						a.`status`=1 and a.`organisation_id`=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""",(firstname,organisation_id,organisation_id,retailer_store_id))

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
					`dob`,`phoneno`,profile_image,a.`organisation_id`,`pincode`,date_of_creation,loggedin_status,wallet FROM `admins` a
					INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
					WHERE locate(%s,a.`first_name`) and locate(%s,a.`last_name`) and 
					a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""",
					(firstname,lastname,organisation_id,organisation_id,retailer_store_id))

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
				`dob`,`phoneno`,profile_image,a.`organisation_id`,`pincode`,date_of_creation,loggedin_status,wallet FROM `admins` a
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
				WHERE locate(%s,a.`phoneno`) and a.`role_id`=4 and a.`status`=1 and
				a.`organisation_id`=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""",(searchkey,organisation_id,organisation_id,retailer_store_id))

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

#--------------------Loyality-Dashboard-------------------------#

@name_space_loyality_dashboard.route("/loyalityDashboard/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>")	
class loyalityDashboard(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		credit_data = {}
		redeem_data = {}

		if filterkey == 'today':
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			get_credited_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`)=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty' """)
			get_credited_customer_data = (organisation_id,today_date,organisation_id,retailer_store_id)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0

			credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`)=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,today_date,organisation_id,retailer_store_id)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	

			redeem_data['store_data'] = []

		if filterkey == 'yesterday':
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_credited_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`)=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty' """)
			get_credited_customer_data = (organisation_id,yesterday,organisation_id,retailer_store_id)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0

			credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`)=%s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,yesterday,organisation_id,retailer_store_id)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	

			redeem_data['store_data'] = []

		if filterkey == 'last 7 days':
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_credited_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >= %s and date(wt.`last_update_ts`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty' """)
			get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0

			credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	

			redeem_data['store_data'] = []

		if filterkey == 'this month':
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			get_credited_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >= %s and date(wt.`last_update_ts`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty' """)
			get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0

			credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	

			redeem_data['store_data'] = []

		if filterkey == 'lifetime':
			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_credited_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >= %s and date(wt.`last_update_ts`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty' """)
			get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0

			credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(wt.`customer_id`))as total 
				FROM `wallet_transaction` wt
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = wt.`customer_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	

			redeem_data['store_data'] = []

		get_loyality_master_query = ("""SELECT * FROM `general_loyalty_master` WHERE `organisation_id` = %s """)
		get_loyality_master_data = (organisation_id)
		loyality_master_count = cursor.execute(get_loyality_master_query,get_loyality_master_data)
		if loyality_master_count > 0:
			loyality_data = cursor.fetchone()
			signup_point = str(loyality_data['signup_point'])
			per_transaction_percentage = str(loyality_data['per_transaction_percentage'])
		else:
			signup_point = ""
			per_transaction_percentage = ""


		get_redeem_settings_query = ("""SELECT * FROM `redeem_setting` WHERE `organisation_id` = %s """)
		get_redeem_master_data = (organisation_id)
		redeem_master_count = cursor.execute(get_redeem_settings_query,get_redeem_master_data)
		if redeem_master_count > 0:
			redeem_master_data = cursor.fetchone()
			is_apply_for_online_user = str(redeem_master_data['is_apply_for_online_user'])
			point = str(redeem_master_data['point'])
			point_value_in_rs = str(redeem_master_data['point_value_in_rs'])
		else:
			is_apply_for_online_user = ""
			point = ""
			point_value_in_rs = ""

		get_redeem_value_query = ("""SELECT * FROM `redeem_value` WHERE `organisation_id` = %s """)
		get_redeem_value_data = (organisation_id)
		redeem_value_count = cursor.execute(get_redeem_value_query,get_redeem_value_data)
		if redeem_value_count > 0:
			redeem_value_data = cursor.fetchone()
			maximum_amount_percentage = str(redeem_value_data['maximum_amount_percentage'])
			maximum_amount_absolute_value = str(redeem_value_data['maximum_amount_absolute_value'])			
		else:
			maximum_amount_percentage = ""
			maximum_amount_absolute_value = ""		


		get_loyality_settings_query = ("""SELECT *
				FROM `referal_loyality_settings` rfl				 
				WHERE `organisation_id` = %s""")
		getLoyalitySettingsData = (organisation_id)
		count_Loyality_settings_data = cursor.execute(get_loyality_settings_query,getLoyalitySettingsData)	

		if count_Loyality_settings_data > 0:
			loyality_settings_data = cursor.fetchone()
			setting_value = loyality_settings_data['setting_value']
		else:
			setting_value = 0

		return ({"attributes": {
		    		"status_desc": "Customer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{"credit_data":credit_data,"redeem_data":redeem_data,"signup_point":signup_point,"per_transaction_percentage":per_transaction_percentage,"is_apply_for_online_user":is_apply_for_online_user,"point":point,"point_value_in_rs":point_value_in_rs,"maximum_amount_percentage":maximum_amount_percentage,"maximum_amount_absolute_value":maximum_amount_absolute_value,"setting_value":setting_value} }), status.HTTP_200_OK

#--------------------Loyality-Dashboard-------------------------#

#---------------------------Get-Loyality-Settings------------------------------------#

@name_space_loyality_dashboard.route("/getLoyalitySettings/<int:organisation_id>/<int:retailer_store_id>")	
class getLoyalitySettings(Resource):
	def get(self,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_loyality_settings_query = ("""SELECT `signup_point`,`per_transaction_percentage`,`birthday_bonus`,`anniversary_bonus`,`first_purchase_bonus`,
												`customer_review_bonus`,`prebook_loyality_bonus`,`e_bill_bonus` from `general_loyalty_master` WHERE `organisation_id` = %s""")
		get_loyality_settings_data = (organisation_id)
		loyality_settings_count = cursor.execute(get_loyality_settings_query,get_loyality_settings_data)

		if loyality_settings_count > 0:
			loyality_settings_data = cursor.fetchone()			
		else:
			loyality_settings_data = {}

		get_category_loyality_settings_query = ("""SELECT cls.*,mkm.`meta_key` FROM `category_loyality_settings` cls
												 INNER JOIN `meta_key_master` mkm ON mkm.`meta_key_id` = cls.`category_id`
												 where cls.`organisation_id` = %s order by cls.`category_loyality_id` asc""")
		get_category_loyality_settings_data = (organisation_id)
		category_loyality_settings_count = cursor.execute(get_category_loyality_settings_query,get_category_loyality_settings_data)
		if category_loyality_settings_count > 0:
			category_loyality = cursor.fetchall()

			for ckey,cdata in enumerate(category_loyality):
				category_loyality[ckey]['last_update_ts'] = str(cdata['last_update_ts'])

			loyality_settings_data['category_loyality'] = category_loyality
		else:
			loyality_settings_data['category_loyality'] = []

		get_sub_category_loyality_settings_query = ("""SELECT scls.*,mkvm.`meta_key_value` FROM `sub_category_loyality_settings` scls
													INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = scls.`sub_category_id`
													where scls.`organisation_id` = %s order by scls.`sub_category_loyality_id` asc""")
		get_sub_category_loyality_settings_data = (organisation_id)
		sub_category_loyality_settings_count = cursor.execute(get_sub_category_loyality_settings_query,get_sub_category_loyality_settings_data)
		if sub_category_loyality_settings_count > 0:
			sub_category_loyality = cursor.fetchall()

			for sckey,scdata in enumerate(sub_category_loyality):
				sub_category_loyality[sckey]['last_update_ts'] = str(scdata['last_update_ts'])
				
			loyality_settings_data['sub_category_loyality'] = sub_category_loyality
		else:
			loyality_settings_data['sub_category_loyality'] = []



		get_referal_loyality_settings_query = ("""SELECT * FROM `referal_loyality_settings_master` where `organisation_id` = %s order by `referal_loyality_settings_id` asc""")
		get_referal_loyality_settings_data = (organisation_id)
		referal_loyality_settings_count = cursor.execute(get_referal_loyality_settings_query,get_referal_loyality_settings_data)

		if referal_loyality_settings_count > 0:
			referal_loyality = cursor.fetchall()					

			for rkey,rdata in enumerate(referal_loyality):
				referal_loyality[rkey]['last_update_ts'] = str(rdata['last_update_ts'])
				
			loyality_settings_data['referal_loyality'] = referal_loyality
		else:
			loyality_settings_data['referal_loyality'] = []


		get_transactional_loyality_settings_query = ("""SELECT * FROM `total_transactional_loyality_settings` where `organisation_id` = %s order by `total_transactional_loyality_id` asc""")
		get_transactional_loyality_settings_data = (organisation_id)
		transactional_loyality_settings_count = cursor.execute(get_transactional_loyality_settings_query,get_transactional_loyality_settings_data)

		if transactional_loyality_settings_count > 0:
			transactional_loyality = cursor.fetchall()			

			for tkey,tdata in enumerate(transactional_loyality):
				transactional_loyality[tkey]['last_update_ts'] = str(tdata['last_update_ts'])
				
			loyality_settings_data['transactional_loyality'] = transactional_loyality
		else:
			loyality_settings_data['transactional_loyality'] = []

		get_buyback_loyality_settings_query = ("""SELECT * FROM `buy_back_loyality_settings` where `organisation_id` = %s order by `buy_back_loyality_id` asc""")
		get_buyback_loyality_settings_data = (organisation_id)
		buyback_loyality_settings_count = cursor.execute(get_buyback_loyality_settings_query,get_buyback_loyality_settings_data)

		if buyback_loyality_settings_count > 0:
			buyback_loyality = cursor.fetchall()			

			for bbkey,bbdata in enumerate(buyback_loyality):
				buyback_loyality[bbkey]['last_update_ts'] = str(bbdata['last_update_ts'])
				
			loyality_settings_data['buyback_loyality'] = buyback_loyality
		else:
			loyality_settings_data['buyback_loyality'] = []

		get_loyality_sms_query = ("""SELECT count(os.`otp_sms_id`) as total_loyality_sms 
			FROM `otp_sms` os
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = os.`customer_id`
			where os.`organisation_id` = %s and `title` = 'loyality' and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""")
		get_loyality_sms_data = (organisation_id,organisation_id,retailer_store_id)
		loyality_sms_count = cursor.execute(get_loyality_sms_query,get_loyality_sms_data)

		if loyality_sms_count > 0:
			loyality_sms_data = cursor.fetchone()	
			loyality_settings_data['sms_count'] = loyality_sms_data['total_loyality_sms']
		else:
			loyality_settings_data['sms_count'] = 0



		return ({"attributes": {
			    		"status_desc": "loyality_settings",
			    		"status": "success"
			    },
			    "responseList":loyality_settings_data}), status.HTTP_200_OK	

#---------------------------Get-Loyality-Settings------------------------------------#

#--------------------------Offer-Count-Detaile-By-Date-And-Organisation-And-Retail-Store-Id---------------------------#
@name_space_offer.route("/OfferCountDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>")	
class OfferCountDetailsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()

		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT count(`offer_id`)as total FROM 
				`offer` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			offerdata = cursor.fetchone()
			if offerdata:
				offer = offerdata['total']
			else:
				offer = 0
			
			cursor.execute("""SELECT count(ipr.`transaction_id`)as total 
				FROM `instamojo_payment_request` ipr
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`)=%s""",(retailer_store_id,organisation_id,organisation_id,today))

			offerapplieddata = cursor.fetchone()
			if offerapplieddata['total'] !=None:
				offerapplied = offerapplieddata['total']
			else:
				offerapplied = 0

			# cursor.execute("""SELECT count(distinct(`customer_id`))as total FROM 
			# 	`customer_store_analytics` WHERE `organisation_id`=%s and 
			# 	date(`last_update_ts`)=%s""",(organisation_id,today))

			# visitordata = cursor.fetchone()
			# if visitordata:
			# 	uniquevisitor = visitordata['total']
			# else:
			# 	uniquevisitor = 0

			get_offer_view_query = ("""SELECT * FROM `customer_offer_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) = %s """)
			get_offer_view_data =(organisation_id,today)	
			offer_view_count = cur.execute(get_offer_view_query,get_offer_view_data)

			if offer_view_count > 0:
				offer_view_data = cur.fetchall()
				for key,data in enumerate(offer_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						offer_view_data[key]['is_retailer'] = 1
					else:
						offer_view_data[key]['is_retailer'] = 0

				new_offer_view_data = []
				for key,data in enumerate(offer_view_data):
					if data['is_retailer'] == 1:
						new_offer_view_data.append(offer_view_data[key])

				offerview = len(new_offer_view_data) 

			else:
				offerview = 0

		elif filterkey == 'yesterday':
			cursor.execute("""SELECT count(`offer_id`)as total FROM 
				`offer` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			offerdata = cursor.fetchone()
			if offerdata:
				offer = offerdata['total']
			else:
				offer = 0		

			cursor.execute("""SELECT count(ipr.`transaction_id`)as total 
				FROM `instamojo_payment_request` ipr
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(retailer_store_id,organisation_id,organisation_id))

			offerapplieddata = cursor.fetchone()
			if offerapplieddata['total'] !=None:
				offerapplied = offerapplieddata['total']
			else:
				offerapplied = 0

			# cur.execute("""SELECT count(distinct(`customer_id`))as total FROM 
			# 	`customer_store_analytics` WHERE `organisation_id`=%s and 
			# 	date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			# visitordata = cur.fetchone()
			# if visitordata:
			# 	uniquevisitor = visitordata['total']
			# else:
			# 	uniquevisitor = 0
			

			get_offer_view_query = ("""SELECT * FROM `customer_offer_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY """)
			get_offer_view_data =(organisation_id)	
			offer_view_count = cur.execute(get_offer_view_query,get_offer_view_data)

			if offer_view_count > 0:
				offer_view_data = cur.fetchall()
				for key,data in enumerate(offer_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						offer_view_data[key]['is_retailer'] = 1
					else:
						offer_view_data[key]['is_retailer'] = 0

				new_offer_view_data = []
				for key,data in enumerate(offer_view_data):
					if data['is_retailer'] == 1:
						new_offer_view_data.append(offer_view_data[key])

				offerview = len(new_offer_view_data) 

			else:
				offerview = 0


		elif filterkey == 'last 7 days':
			cursor.execute("""SELECT count(`offer_id`)as total FROM 
				`offer` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			offerdata = cursor.fetchone()
			if offerdata:
				offer = offerdata['total']
			else:
				offer = 0			


			cursor.execute("""SELECT count(ipr.`transaction_id`)as total 
				FROM `instamojo_payment_request` ipr
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(retailer_store_id,organisation_id,organisation_id))

			offerapplieddata = cursor.fetchone()
			if offerapplieddata['total'] !=None:
				offerapplied = offerapplieddata['total']
			else:
				offerapplied = 0

			# cur.execute("""SELECT count(distinct(`customer_id`))as total FROM 
			# 	`customer_store_analytics` WHERE `organisation_id`=%s and 
			# 	date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
   #      		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			# visitordata = cur.fetchone()
			# if visitordata:
			# 	uniquevisitor = visitordata['total']
			# else:
			# 	uniquevisitor = 0
			
			get_offer_view_query = ("""SELECT * FROM `customer_offer_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""")
			get_offer_view_data =(organisation_id)	
			offer_view_count = cur.execute(get_offer_view_query,get_offer_view_data)

			if offer_view_count > 0:
				offer_view_data = cur.fetchall()
				for key,data in enumerate(offer_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						offer_view_data[key]['is_retailer'] = 1
					else:
						offer_view_data[key]['is_retailer'] = 0

				new_offer_view_data = []
				for key,data in enumerate(offer_view_data):
					if data['is_retailer'] == 1:
						new_offer_view_data.append(offer_view_data[key])

				offerview = len(new_offer_view_data) 

			else:
				offerview = 0

		
		elif filterkey == 'this month':
			cursor.execute("""SELECT count(`offer_id`)as total FROM 
				`offer` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			offerdata = cursor.fetchone()
			if offerdata:
				offer = offerdata['total']
			else:
				offer = 0			
			

			cursor.execute("""SELECT count(ipr.`transaction_id`)as total 
				FROM `instamojo_payment_request` ipr
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`) between %s and %s""",(retailer_store_id,organisation_id,organisation_id,stday,today))

			offerapplieddata = cursor.fetchone()
			if offerapplieddata['total'] !=None:
				offerapplied = offerapplieddata['total']
			else:
				offerapplied = 0

			# cur.execute("""SELECT count(distinct(`customer_id`))as total FROM 
			# 	`customer_store_analytics` WHERE `organisation_id`=%s and 
			# 	date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			# visitordata = cur.fetchone()
			# if visitordata:
			# 	uniquevisitor = visitordata['total']
			# else:
			# 	uniquevisitor = 0			

			get_offer_view_query = ("""SELECT * FROM `customer_offer_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`)  between %s and %s """)
			get_offer_view_data =(organisation_id,stday,today)	
			offer_view_count = cur.execute(get_offer_view_query,get_offer_view_data)

			if offer_view_count > 0:
				offer_view_data = cur.fetchall()
				for key,data in enumerate(offer_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						offer_view_data[key]['is_retailer'] = 1
					else:
						offer_view_data[key]['is_retailer'] = 0

				new_offer_view_data = []
				for key,data in enumerate(offer_view_data):
					if data['is_retailer'] == 1:
						new_offer_view_data.append(offer_view_data[key])

				offerview = len(new_offer_view_data) 

			else:
				offerview = 0


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			
			cursor.execute("""SELECT count(`offer_id`)as total FROM 
				`offer` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			offerdata = cursor.fetchone()
			if offerdata:
				offer = offerdata['total']
			else:
				offer = 0
			
			
			cursor.execute("""SELECT count(ipr.`transaction_id`)as total 
				FROM `instamojo_payment_request` ipr
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`) between %s and %s""",(retailer_store_id,organisation_id,organisation_id,slifetime,today))

			offerapplieddata = cursor.fetchone()
			if offerapplieddata['total'] !=None:
				offerapplied = offerapplieddata['total']
			else:
				offerapplied = 0

			# cur.execute("""SELECT count(distinct(`customer_id`))as total FROM 
			# 	`customer_store_analytics` WHERE `customer_id`!=0 and `organisation_id`=%s and 
			# 	date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			# visitordata = cur.fetchone()
			# if visitordata:
			# 	uniquevisitor = visitordata['total']
			# else:
			# 	uniquevisitor = 0

			
			get_offer_view_query = ("""SELECT * FROM `customer_offer_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`)  between %s and %s """)
			get_offer_view_data =(organisation_id,slifetime,today)	
			offer_view_count = cur.execute(get_offer_view_query,get_offer_view_data)

			if offer_view_count > 0:
				offer_view_data = cur.fetchall()
				for key,data in enumerate(offer_view_data):
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` WHERE `user_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id)
					count_user_retailer = cursor.execute(get_user_retailer_query,get_user_retailer_data)
					print(cursor._last_executed)

					if count_user_retailer > 0:
						offer_view_data[key]['is_retailer'] = 1
					else:
						offer_view_data[key]['is_retailer'] = 0

				new_offer_view_data = []
				for key,data in enumerate(offer_view_data):
					if data['is_retailer'] == 1:
						new_offer_view_data.append(offer_view_data[key])

				offerview = len(new_offer_view_data) 

			else:
				offerview = 0

		else:
			offer = 0
			offerapplied = 0
			discountgiven = 0
			offerview = 0
			
		conn.commit()
		cur.close()
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Offer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{
		    					 "offer":offer,
		    					 "offerapplied": offerapplied,
		    					 "discountgiven":offer,
		    					 "offerview":offerview,
						    	}
						    	}), status.HTTP_200_OK

#--------------------------Offer-Count-Detaile-By-Date-And-Organisation-And-Retail-Store-Id---------------------------#

#-----------------------------------Offer-Count-Details-By-Offer-Id----------------------------#
@name_space_offer.route("/OfferCountDetailsByOfferId/<int:offer_id>/<int:organisation_id>/<int:retailer_store_id>")	
class OfferCountDetailsByOfferId(Resource):
	def get(self,offer_id,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()
		
		cursor.execute("""SELECT count(ipr.`transaction_id`)as total FROM 
			`instamojo_payment_request` ipr
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id`
			WHERE ipr.`coupon_code` in(SELECT 
			`coupon_code` FROM `offer` o WHERE o.`offer_id`=%s and o.`organisation_id` = %s) and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""",(offer_id,organisation_id,organisation_id,retailer_store_id))

		offerapplieddata = cursor.fetchone()
		if offerapplieddata['total'] !=None:
			offerapplied = offerapplieddata['total']
		else:
			offerapplied = 0


		cur.execute("""SELECT count(`analytics_id`)as total FROM 
			`customer_offer_analytics` WHERE `offer_id`=%s""",(offer_id))

		offerviewdata = cur.fetchone()
		if offerviewdata:
			offerview = offerviewdata['total']
		else:
			offerview = 0

	
		conn.commit()
		cur.close()
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Offer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{
		    					 "offerapplied": offerapplied,
		    					 "offerview":offerview
						    	}
						    	}), status.HTTP_200_OK

#-----------------------------------Offer-Count-Details-By-Offer-Id----------------------------#

#-----------------------Get-Enquiry-List----------------------#

@name_space_enquiry.route("/getEnquiryList/<int:organisation_id>/<int:retailer_store_id>")	
class getEnquiryList(Resource):
	def get(self,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT em.`enquiry_id`,em.`user_id`,etm.`enquiry_type`,em.`enquiery_status`,em.`date_of_closer`,em.`last_update_ts`,a.`first_name`,a.`last_name`,a.`phoneno`
			FROM `enquiry_master` em
			INNER JOIN `enquiry_type_master` etm ON etm.`enquiry_type_id` = em.`enquiry_type_id`
			INNER JOIN `admins` a ON a.`admin_id` = em.`user_id`
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id` 
			WHERE em.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			ORDER BY em.`enquiry_id` DESC""")

		get_data = (organisation_id,organisation_id,retailer_store_id)
		cursor.execute(get_query,get_data)

		enquiry_data = cursor.fetchall()

		for key,data in enumerate(enquiry_data):
			enquiry_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "enquiery_details",
		    		"status": "success"
		    	},
		    	"responseList":enquiry_data}), status.HTTP_200_OK

#-----------------------Get-Enquiry-List----------------------#

#----------------------Customer-Exchange---------------------#

@name_space_exchange.route("/getCustomerExchangeWithPagination/<int:organisation_id>/<int:page>/<int:final_submission_status>/<int:exchange_status>/<string:start_date>/<string:end_date>/<int:retailer_store_id>")	
class getCustomerExchangeWithPagination(Resource):
	def get(self,organisation_id,page,final_submission_status,exchange_status,start_date,end_date,retailer_store_id):
		if page == 1:
			offset = 0
		else:
			offset = (page-1) * 20

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT ced.`exchange_id`,ced.`amount`,ced.`front_image`,ced.`back_image`,ced.`device_model`,ced.`last_update_ts`,a.`first_name`,a.`last_name`,ced.`status`,a.`admin_id` as `user_id`,a.`phoneno`,ced.`final_submission_status`,ced.`Is_clone`
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = %s and ced.`status` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s
			LIMIT %s,20""")

		get_data = (organisation_id,final_submission_status,exchange_status,organisation_id,retailer_store_id,start_date,end_date,offset)
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
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = %s and ced.`status` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s""")

		get_data_count = (organisation_id,final_submission_status,exchange_status,organisation_id,retailer_store_id,start_date,end_date)
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

#-----------------------------Customer-Exchange-Search-----------------------#
@name_space_exchange.route("/CustomerExchangeSearch/<string:searchkey>/<int:organisation_id>/<int:page>/<int:retailer_store_id>")	
class CustomerExchangeSearch(Resource):
	def get(self,searchkey,organisation_id,page,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if page == 1:
			offset = 0
		else:
			offset = (page-1) * 20

		get_customer_exchange_query = ("""SELECT ced.`exchange_id`,ced.`amount`,ced.`front_image`,ced.`back_image`,ced.`device_model`,ced.`last_update_ts`,a.`first_name`,a.`last_name`,ced.`status`,a.`admin_id` as `user_id`,a.`phoneno`,ced.`final_submission_status`,ced.`organisation_id`
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and (a.`first_name` LIKE %s or a.`last_name` LIKE %s or ced.`exchange_id` LIKE %s or a.`phoneno` LIKE %s or ced.`device_model` LIKE %s) LIMIT %s,20
			""")
		get_customer_exchange_data = (organisation_id,organisation_id,retailer_store_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%",offset)

		cursor.execute(get_customer_exchange_query,get_customer_exchange_data)
		print(cursor._last_executed)

		customer_exchange_data = cursor.fetchall()

		for key,data in enumerate(customer_exchange_data):
			#customer_exchange_data[key]['exchange_id'] = "AMEXCHANGE-"+str(data['exchange_id'])
			customer_exchange_data[key]['last_update_ts'] = str(data['last_update_ts'])		

		get_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and (a.`first_name` LIKE %s or a.`last_name` LIKE %s or ced.`exchange_id` LIKE %s or a.`phoneno` LIKE %s or ced.`device_model` LIKE %s)""")

		get_data_count = (organisation_id,organisation_id,retailer_store_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%")
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

#---------------------------Exchange-Count-Details-By-Date-Organisation-Id--------------------------#
@name_space_exchange.route("/ExhcnageCountDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>")	
class ExhcnageCountDetailsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if filterkey == 'today':
			
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			print(today_date)

			get_active_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
			ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) = %s""")

			get_data = (organisation_id,organisation_id,retailer_store_id,today_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) = %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 0 and ced.`status` = 0 
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
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) = %s """)

			get_data = (organisation_id,organisation_id,retailer_store_id,yesterday)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) = %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 0 and ced.`status` = 0 
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
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			get_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 0 and ced.`status` = 0 
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
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			get_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 0 and ced.`status` = 0 
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
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			get_data = (organisation_id,organisation_id,retailer_store_id,start_date,end_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s
			and ced.`final_submission_status` = 0 and ced.`status` = 0 
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