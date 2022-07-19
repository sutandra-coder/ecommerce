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

app = Flask(__name__)
cors = CORS(app)

env = Environment(
    loader=FileSystemLoader('%s/templates/' % os.path.dirname(__file__)))

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

ecommerce_customer = Blueprint('ecommerce_customer_api', __name__)
api = Api(ecommerce_customer,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceCustomer',description='Ecommerce Customer')

customer_postmodel = api.model('SelectCustomer', {
	"first_name":fields.String,
	"last_name":fields.String,
	"email":fields.String,
	"password":fields.String,
	"phoneno":fields.Integer(required=True),
	"address_line_1":fields.String,
	"address_line_2":fields.String,
	"city":fields.String,
	"county":fields.String,
	"state":fields.String,
	"pincode":fields.Integer,
	"emergency_contact":fields.Integer,
	"referal_code":fields.String,
	"registration_type":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

checkemail_postmodel = api.model('checkEmail',{
	"email":fields.String(required=True),
})

checkreferal_postmodel = api.model('checkReferal',{
	"referral_code":fields.String(required=True),
})

checkphoneno_postmodel = api.model('checkPhone',{
	"phoneno":fields.String(required=True),
})

login_postmodel = api.model('loginCustomer',{
	"email":fields.String(required=True),
	"password":fields.String(required=True)
})

devicetoken_postmodel = api.model('deviceToken',{
	"user_id":fields.Integer(required=True),	
	"device_type":fields.Integer(required=True),
	"device_token":fields.String(required=True)
})

changepassword_putmodel = api.model('changePasswod',{
	"new_password":fields.String(required=True),
})

checkotp_postmodel = api.model('checkOtp',{
	"phoneno":fields.String(required=True),
	"otp":fields.String(required=True)
})

customer_product_postmodel = api.model('customerproduct',{
	"customer_id":fields.Integer(required=True),
	"product_meta_id":fields.Integer(required=True),
	"is_favourite":fields.String(required=True)
})


add_to_cart_postmodel = api.model('addToCart',{
	"customer_id":fields.Integer(required=True),
	"product_meta_id":fields.Integer(required=True)
})

cart_putmodel = api.model('updateCart',{
	"qty":fields.Integer(required=True)
})

customer_stories_postmodel = api.model('customerstories',{
	"user_id":fields.Integer(required=True),
	"review":fields.String(required=True),
	"ratting":fields.Integer(required=True)
})

customer_address_putmodel = api.model('customerAddress',{
	"address_line_1":fields.String,
	"address_line_2":fields.String,
	"city":fields.String,
	"country":fields.String,
	"state":fields.String,
	"pincode":fields.Integer
})

apply_cupon_postmodel = api.model('cuponPostModel',{
	"coupon_code":fields.String(required=True)
})

create_payment_link_model = api.model('create_payment_link_model', {
	"amount":fields.Integer(required=True),
	"purpose":fields.String(),
	"buyer_name":fields.String(),
	"email":fields.String(),
	"phone":fields.Integer(),
	"user_id":fields.Integer(required=True),
	"transaction_id":fields.Integer(),
	"coupon_code":fields.String
})

save_order = api.model('save_order', {
	"amount":fields.Integer(required=True),
	"purpose":fields.String(required=True),
	"user_id":fields.Integer(required=True),
	"coupon_code":fields.String
})

create_invoice = api.model('create_invoice', {
	"user_id":fields.Integer(required=True),
	"transaction_id":fields.Integer(required=True)
})

buy_model = api.model('buy_model', {
	"product_meta_id":fields.Integer(required=True),
	"amount":fields.Integer(required=True),
	"purpose":fields.String(required=True),
	"user_id":fields.Integer(required=True),
	"coupon_code":fields.String
})

appmsg_model = api.model('appmsg_model', {	
	"firebase_key":fields.String(),
	"device_id":fields.String()
})


send_email_model = api.model('email_model', {	
	"To":fields.String(),
	"Subject":fields.String()
})

customer_exchange_model = api.model('customer_exchange_model', {	
	"customer_id":fields.Integer(required=True),
	"amount":fields.Integer(required=True),
	"front_image":fields.String,
	"back_image":fields.String,
	"question_ans_id":fields.List(fields.Integer(required=True))	
})

customer_wallet_putmodel = api.model('customer_wallet_putmodel', {	
	"wallet":fields.Float(required=True)	
})

enquiry_postmodel = api.model('enquiry_postmodel',{
	"enquiry_type_id":fields.Integer(required=True),
	"user_id":fields.Integer(required=True)
})

enquiry_communication_postmodel = api.model('enquiry_communication_postmodel',{
	"enquiry_id":fields.Integer(required=True),
	"user_id":fields.Integer(required=True),
	"image":fields.String,
	"text":fields.String(required=True)
})

productreplication_postmodel = api.model('product_replication_postmodel',{	
	"from_organisation_id":fields.Integer(required=True),
	"brand_id":fields.List(fields.Integer),
	"to_organisation_id":fields.Integer(required=True),
	"coppy_all_product":fields.Integer(required=True)
})

filter_postmodel = api.model('product_replication_postmodel',{	
	"brand_id":fields.List(fields.Integer)
})



class DictModel(fields.Raw):
	def format(self, value):
		dictmodel = {}
		return dictmodel

communication_model = api.model('communication_model', {
	"sourceapp":fields.String(),
	"mailParams":DictModel()
})

enquiry_communication_parser = api.parser()
enquiry_communication_parser.add_argument('file', location='files', type=FileStorage, required=True)

upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)

#BASE_URL = 'http://ec2-3-19-228-138.us-east-2.compute.amazonaws.com/flaskapp/'
BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

MOJO_TEST_URL = 'https://test.instamojo.com/'

MOJO_BASE_URL = 'https://api.instamojo.com/'

EMAIL_ADDRESS = 'communications@creamsonservices.com'
EMAIL_PASSWORD = 'CReam7789%$intELLi'

#----------------------Check-Email-Exist---------------------#

@name_space.route("/CheckEmail")	
class CheckEmail(Resource):
	@api.expect(checkemail_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `admins` WHERE `email` = %s and `role_id` = 4""")
		getData = (details['email'])
		count_customer = cursor.execute(get_query,getData)

		connection.commit()
		cursor.close()

		if count_customer > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "customer_details",
			    		"status": "error",
			    		"message":"Customer Email Already Exist"
			    	},
			    	"responseList":{"phoneno":data['phoneno'],"city":data['city']} }), status.HTTP_200_OK

		else:
			return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success",
		    		"message":"Email Id not Exist"
		    	},
		    	"responseList":{"email":details['email'],"phoneno":"","city":""}}), status.HTTP_200_OK

		

#----------------------Check-Email-Exist---------------------#

#----------------------Check-Phone-No-Exist---------------------#

@name_space.route("/CheckPhoneno")	
class CheckPhoneno(Resource):
	@api.expect(checkphoneno_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `admins` WHERE `phoneno` = %s and `role_id` = 4""")
		getData = (details['phoneno'])
		count_customer = cursor.execute(get_query,getData)

		connection.commit()
		cursor.close()

		if count_customer > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "customer_details",
			    		"status": "error",
			    		"message":"Customer Phoneno Already Exist"
			    	},
			    	"responseList":{"city":data['city']} }), status.HTTP_200_OK

		else:
			return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList":{"phoneno":details['phoneno']}}), status.HTTP_200_OK

		

#----------------------Check-Phone-No-Exist---------------------#

#----------------------Location-List---------------------#

@name_space.route("/getLocation")	
class getLocation(Resource):
	def get(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query =  ("""SELECT rs.`retailer_store_id`,rs.`retailer_name`,rs.`city`,rsi.`image`
			FROM `retailer_store` rs 
			INNER JOIN `retailer_store_image` rsi ON rsi.`retailer_store_id` = rs.`retailer_store_id`""")	

		cursor.execute(get_query)
		location_data = cursor.fetchall()

		return ({"attributes": {
		    		"status_desc": "customer_notification_details",
		    		"status": "success"
		    	},
		    	"responseList":location_data}), status.HTTP_200_OK

#----------------------Location-List---------------------#

#----------------------Retailer-List---------------------#

@name_space.route("/getRetailer/<int:organisation_id>")	
class getRetailer(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query =  ("""SELECT rs.`retailer_store_id`,rs.`retailer_name`,rs.`latitude`,rs.`longitude`,rs.`city`,rs.`county`,rsi.`image`,rs.`phoneno`
			FROM `retailer_store` rs 
			INNER JOIN `retailer_store_image` rsi ON rsi.`retailer_store_id` = rs.`retailer_store_id` where rs.`organisation_id` = %s""")	
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)
		retailer_data = cursor.fetchall()

		return ({"attributes": {
		    		"status_desc": "retailer_details",
		    		"status": "success"
		    	},
		    	"responseList":retailer_data}), status.HTTP_200_OK

#----------------------Retailer-List---------------------#

#----------------------Emi-List---------------------#

@name_space.route("/getEmiList/<int:organisation_id>")	
class getEmiList(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query =  ("""SELECT * FROM `emi_bank` where `organisation_id` = %s""")	
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)
		emi_bank_data = cursor.fetchall()

		for key,data in enumerate(emi_bank_data):
			emi_bank_data[key]['last_update_ts'] = str(data['last_update_ts'])


		get_brand_query =  ("""SELECT * FROM `emi_brand` where `organisation_id` = %s""")	
		get_brand_data = (organisation_id)
		cursor.execute(get_brand_query,get_brand_data)
		emi_band_data = cursor.fetchall()

		for bkey,bdata in enumerate(emi_band_data):
			emi_band_data[bkey]['last_update_ts'] = str(bdata['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "emi_details",
		    		"status": "success"
		    	},
		    	"responseList":{"bank_list":emi_bank_data,"brand_list":emi_band_data}}), status.HTTP_200_OK

#----------------------Emi-List---------------------#

#----------------------Emi-Band-List---------------------#

@name_space.route("/getEmiBrandList/<int:organisation_id>")	
class getEmiBrandList(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query =  ("""SELECT * FROM `emi_brand` where `organisation_id` = %s""")	
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)
		emi_bank_data = cursor.fetchall()

		for key,data in enumerate(emi_bank_data):
			emi_bank_data[key]['last_update_ts'] = str(data['last_update_ts'])


		return ({"attributes": {
		    		"status_desc": "emi_bank_details",
		    		"status": "success"
		    	},
		    	"responseList":emi_bank_data}), status.HTTP_200_OK

#----------------------Emi-Band-List---------------------#

#----------------------User-Retailer---------------------#

@name_space.route("/getUserRetailerInformation/<int:user_id>")	
class getUserRetailerInformation(Resource):
	def get(self,user_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query =  ("""SELECT rs.`retailer_name`,rs.`address_line_1`,rs.`address_line_2`,rs.`latitude`,rs.`longitude`,
			rs.`city`,rs.`county`,rs.`state`,rs.`pincode`,rs.`phoneno`
			FROM `user_retailer_mapping` urm 
			INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = urm.`retailer_id`
			where urm.`user_id` = %s""")	

		get_data = (user_id)
		cursor.execute(get_query,get_data)
		user_retailer_data = cursor.fetchall()

		return ({"attributes": {
		    		"status_desc": "user_retailer_information",
		    		"status": "success"
		    	},
		    	"responseList":user_retailer_data}), status.HTTP_200_OK

#----------------------User-Retailer---------------------#

#----------------------Check-Referal-Exist---------------------#

@name_space.route("/Checkreferal")	
class Checkreferal(Resource):
	@api.expect(checkreferal_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_referal_query = ("""SELECT *
			FROM `customer_referral` WHERE `referral_code` = %s""")
		getReferalData = (details['referral_code'])
		count_referal = cursor.execute(get_referal_query,getReferalData)

		if count_referal > 0:
			
			return ({"attributes": {
				    	"status_desc": "referal_details",
				    	"status": "success",
				    	"message":"referral code Exist"
				    },
				    "responseList":{} }), status.HTTP_200_OK		
				
		else:
			return ({"attributes": {
		    		"status_desc": "referal_details",
		    		"status": "error",
		    		"message":"referal code Not Exsits"
		    	},
		    	"responseList":{} }), status.HTTP_200_OK

		

#----------------------Check-Referal-Exists---------------------#

#----------------------Add-Customer---------------------#

@name_space.route("/AddCustomer")
class AddCustomer(Resource):
	@api.expect(customer_postmodel)
	def post(self):
	
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
		organisation_id = details['organisation_id']
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
				last_update_id = details['organisation_id']
				city_insert_data = (admin_id,city_data['retailer_store_id'],admin_status,organisation_id,last_update_id)	
				cursor.execute(insert_mapping_user_retailer,city_insert_data)

			insert_customer_referal_code_query = ("""INSERT INTO `customer_referral`(`customer_id`,`referral_code`,`organisation_id`,`status`,`last_update_id`)
					VALUES(%s,%s,%s,%s,%s)""")
			organisation_id = details['organisation_id']
			last_update_id = details['organisation_id']	

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

					organisation_id = details['organisation_id']
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

#----------------------User-Loyality-Point-List---------------------#
@name_space.route("/getUserLoyalityPointList/<int:user_id>")	
class getMetaKeyValueList(Resource):
	def get(self,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_wallet_query = ("""SELECT `wallet` FROM `admins` 
						WHERE `admin_id` = %s """)
		getwalletdata = (user_id)
		cursor.execute(get_wallet_query,getwalletdata)
		wallet_data = cursor.fetchone()

		get_transaction_query = ("""SELECT * FROM `wallet_transaction` 
						WHERE `customer_id` = %s """)
		gettransactiondata = (user_id)
		cursor.execute(get_transaction_query,gettransactiondata)

		wallet_data['transactions'] = cursor.fetchall()

		for key,data in enumerate(wallet_data['transactions']):
			wallet_data['transactions'][key]['last_update_ts'] = str(data['last_update_ts'])
		

		return ({"attributes": {
		    		"status_desc": "wallet_details",
		    		"status": "success"
		    	},
		    	"responseList":wallet_data}), status.HTTP_200_OK

#----------------------User-Loyality-Point-List---------------------#


#----------------------Update-Customer-Address---------------------#

@name_space.route("/updateCustomerAddress/<int:user_id>")
class updateCustomerAddress(Resource):
	@api.expect(customer_address_putmodel)
	def put(self, user_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()


		if details and "address_line_1" in details:
			address_line_1 = details['address_line_1']
			update_query = ("""UPDATE `admins` SET `address_line_1` = %s
				WHERE `admin_id` = %s """)
			update_data = (address_line_1,user_id)
			cursor.execute(update_query,update_data)

		if details and "address_line_2" in details:
			address_line_2 = details['address_line_2']
			update_query = ("""UPDATE `admins` SET `address_line_2` = %s
				WHERE `admin_id` = %s """)
			update_data = (address_line_2,user_id)
			cursor.execute(update_query,update_data)

		if details and "city" in details:
			city = details['city']
			update_query = ("""UPDATE `admins` SET `city` = %s
				WHERE `admin_id` = %s """)
			update_data = (city,user_id)
			cursor.execute(update_query,update_data)

		if details and "country" in details:
			country = details['country']
			update_query = ("""UPDATE `admins` SET `country` = %s
				WHERE `admin_id` = %s """)
			update_data = (country,user_id)
			cursor.execute(update_query,update_data)

		if details and "state" in details:
			state = details['state']
			update_query = ("""UPDATE `admins` SET `state` = %s
				WHERE `admin_id` = %s """)
			update_data = (state,user_id)
			cursor.execute(update_query,update_data)

		if details and "pincode" in details:
			pincode = details['pincode']
			update_query = ("""UPDATE `admins` SET `pincode` = %s
				WHERE `admin_id` = %s """)
			update_data = (pincode,user_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Customer Address",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Customer-Address---------------------#

#----------------------Update-Customer-Information---------------------#

@name_space.route("/updateCustomerInformation/<int:user_id>")
class updateCustomerInformation(Resource):
	@name_space.expect(upload_parser)
	def put(self, user_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		uploadURL = BASE_URL + 'aws_portal_upload/awsResourceUploadController/uploadToS3Bucket/{}'.format(user_id)
		headers = {"content-type": "multipart/form-data"}
		files = {}
		#print(request.files)
		for form_file_param in request.files:
			fs = request.files[form_file_param] 
			files[form_file_param] = (fs.filename, fs.read())

		uploadRes = requests.post(uploadURL,files=files).json()
		responselist = json.dumps(uploadRes['responseList'][0])
		s2 = json.loads(responselist)
		
		profile_image = s2['FilePath'] 

		update_query = ("""UPDATE `admins` SET `profile_image` = %s
			WHERE `admin_id` = %s """)
		update_data = (profile_image,user_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Customer Information",
								"status": "success"},
				"responseList": profile_image}), status.HTTP_200_OK

#----------------------Update-Customer-Information---------------------#

#----------------------Customer-Details---------------------#
@name_space.route("/customerDetails/<int:user_id>")	
class customerDetails(Resource):
	def get(self,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT a.`admin_id` as `user_id`,a.`first_name`,a.`last_name`,a.`email`,a.`org_password`,
			a.`phoneno`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`,a.`emergency_contact`,a.`role_id`,
			d.`device_token`
				FROM `admins` a
				INNER JOIN `devices` d ON d.`user_id` = a.`admin_id` 
				WHERE `admin_id` = %s""")
		getData = (user_id)
		cursor.execute(get_query,getData)

		data = cursor.fetchone()

		return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success"
		    	},
		    	"responseList":data}), status.HTTP_200_OK

#----------------------Customer-Details---------------------#

#----------------------Customer-List---------------------#
@name_space.route("/customerList/<int:organisation_id>")	
class customerList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `admin_id` as `user_id`,`first_name`,`last_name`,`email`,
			`phoneno`,`profile_image`
				FROM `admins` WHERE `organisation_id` = %s and `role_id` = 4""")
		getData = (organisation_id)
		cursor.execute(get_query,getData)

		data = cursor.fetchall()

		return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success"
		    	},
		    	"responseList":data}), status.HTTP_200_OK

#----------------------Customer-Details---------------------#

#----------------------Customer-Login---------------------#

@name_space.route("/Login")	
class Login(Resource):
	@api.expect(login_postmodel)
	def post(self):
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

#----------------------Forgotpassword---------------------#

@name_space.route("/Forgotpassword")	
class Forgotpassword(Resource):
	@api.expect(checkphoneno_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `admins` WHERE `phoneno` = %s and `role_id` = 4""")
		getData = (details['phoneno'])
		count_customer = cursor.execute(get_query,getData)

		connection.commit()
		cursor.close()

		if count_customer > 0:
			login_data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "customer_details",
			    		"status": "success",
			    		"mesaage":"Exist"
			    	},
			    	"responseList":{"user_id": login_data['admin_id']}}), status.HTTP_200_OK

		else:
			return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success",
		    		"message":"Did not Exist"
		    	},
		    	"responseList":{"phoneno":details['phoneno']}}), status.HTTP_200_OK

		

#----------------------Forgotpassword---------------------#

#----------------------Change-Password---------------------#

@name_space.route("/changePasswod/<int:user_id>")
class changePasswod(Resource):
	@api.expect(changepassword_putmodel)
	def put(self,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()

		update_query = ("""UPDATE `admins` SET `org_password` = %s
				WHERE `admin_id` = %s """)
		update_data = (details['new_password'],user_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Change Password",
								"status": "success",
								"message":"Password set successfully"
									},
				"responseList":details}), status.HTTP_200_OK

#----------------------Change-Password---------------------#

#----------------------Send-Otp---------------------#

@name_space.route("/sendOtp")	
class sendOtp(Resource):
	@api.expect(checkphoneno_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		url = "http://creamsonservices.com:8080/NewSignUpService/postInstitutionUserOtp"
		post_data = {
					  "firstName": "string",
					  "generatedBy": "string",
					  "institutionId": 1,
					  "institutionUserId": 0,
					  "institutionUserRole": "S1",
					  "lastName": "string",
					  "mailId": "string",
					  "otp": 123456,
					  "phoneNumber": details['phoneno']
					}

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		post_response = requests.post(url, data=json.dumps(post_data), headers=headers)

		my_json_string = post_response.json()

		s1 = json.dumps(my_json_string['responseList'][0])
		s2 = json.loads(s1)

		InstitutionUserOtp = json.dumps(s2['InstitutionUserOtp '])
		otpjson = json.loads(InstitutionUserOtp)

		if otpjson :
			return ({"attributes": {"status_desc": "Send Otp",
								"status": "success",
								"message":"Send Otp Successfully"
									},
				"responseList":{"otp":otpjson['otp'],"phoneno":otpjson['phoneNumber']}}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Send Otp",
								"status": "error",
								"message":"Having Issue"
									},
				"responseList":{}}), status.HTTP_200_OK	
#----------------------Send-Otp---------------------#

#----------------------Check-Otp---------------------#

@name_space.route("/checkOtp")	
class checkOtp(Resource):
	@api.expect(checkotp_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = 'http://creamsonservices.com:8080/NewSignUpService/validateOtpByPhone/{}/{}'.format(details['otp'],details['phoneno'])

		getResponse = requests.get(url, headers=headers)

		my_json_string = getResponse.json()

		check_response = json.dumps(my_json_string['attributes'])

		response = json.loads(check_response)

		if(response['status'] == 'success'):

			responselist = json.dumps(my_json_string['responseList'][0])
			responselistjson = json.loads(responselist)

			InstitutionUserOtp = json.dumps(responselistjson['InstitutionUserOtp '])
			otpjson = json.loads(InstitutionUserOtp)

			if otpjson :
				return ({"attributes": {"status_desc": "Check Otp",
									"status": "success",
									"message":"Outhenticate Successfully"
										},
					"responseList":{"otp":otpjson['otp'],"phoneno":otpjson['phoneNumber']}}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Check Otp",
								"status": "error",
								"message":"Otp Not Validated"
									},
				"responseList":{}}), status.HTTP_200_OK	

#----------------------Check-Otp---------------------#


#----------------------Get-Customer-Notification---------------------#	

@name_space.route("/getCustomerNotificationList/<int:user_id>")	
class getCustomerNotificationList(Resource):
	def get(self,user_id):
		
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `customer_notification_mapping` where `customer_id` = %s""")
		get_data = (user_id)
		cursor.execute(get_query,get_data)

		cusomer_notification_data = cursor.fetchall()

		for key,data in enumerate(cusomer_notification_data):
			cusomer_notification_data[key]['Last_update_TS'] = str(data['Last_update_TS'])

			get_product_query = ("""SELECT `product_id`,`product_name`,`product_long_description`,`product_short_description`,`price`
			FROM `product` WHERE `product_id` = %s """)
			get_product_data = (data['product_id'])
			cursor.execute(get_product_query,get_product_data)
			product_data = cursor.fetchone()

			get_notification_query = ("""SELECT `notification_id`,`text`,`image`,`email`,`whatsapp`
			FROM `notification` WHERE `notification_id` = %s """)
			get_notification_data = (data['notification_id'])
			cursor.execute(get_notification_query,get_notification_data)
			notification_data = cursor.fetchone()

			cusomer_notification_data[key]['product_name'] = product_data['product_name']
			cusomer_notification_data[key]['notification_id'] = notification_data['notification_id']	
			cusomer_notification_data[key]['text'] = notification_data['text']
			cusomer_notification_data[key]['image'] = notification_data['image']
			cusomer_notification_data[key]['email'] = notification_data['email']
			cusomer_notification_data[key]['whatsapp'] = notification_data['whatsapp']
		return ({"attributes": {
		    		"status_desc": "customer_notification_details",
		    		"status": "success"
		    	},
		    	"responseList":cusomer_notification_data}), status.HTTP_200_OK

#----------------------Get-Customer-Notification---------------------#	

#----------------------Get-Customer-List---------------------#

@name_space.route("/getCustomerList")	
class getCustomerList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `admin_id`,`first_name`,`last_name`,`email`,`org_password`,`phoneno`,
			`address_line_1`,`address_line_2`,`city`,`county`,`state`,`pincode`,`emergency_contact`,
			`status`
			FROM `admins` WHERE `role_id` = 4 """)

		cursor.execute(get_query)

		data = cursor.fetchall()
				
		return ({"attributes": {
		    		"status_desc": "Customer_details",
		    		"status": "success"
		    	},
		    	"responseList":data}), status.HTTP_200_OK
		
#-----------------------Get-Customer-List---------------------#

#----------------------Add-Customer-Stories---------------------#

@name_space.route("/AddCustomerStories")
class AddCustomerStories(Resource):
	@api.expect(customer_stories_postmodel)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		customer_id = details['user_id']
		review = details['review']
		ratting = details['ratting']

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		insert_query = ("""INSERT INTO `customer_stories`(`customer_id`,`review`,`ratting`,`date_of_creation`) 
				VALUES(%s,%s,%s,%s)""")
		data = (customer_id,review,ratting,date_of_creation)
		cursor.execute(insert_query,data)

		customer_story_id = cursor.lastrowid
		details['customer_story_id'] = customer_story_id

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_story_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Add-Customer-Stories---------------------#

#----------------------Get-Customer-Stories---------------------#

@name_space.route("/getCustomerStoryList")	
class getCustomerStoryList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `customer_stories`""")

		cursor.execute(get_query)

		story_data = cursor.fetchall()

		for key,data in enumerate(story_data):
			story_data[key]['date_of_creation'] = str(data['date_of_creation'])

			get_customer_query = ("""SELECT `first_name`,`last_name`
			FROM `admins` WHERE `admin_id` = %s """)
			customer_data = (data['customer_id'])
			cursor.execute(get_customer_query,customer_data)

			customer_data_result = cursor.fetchone()

			story_data[key]['first_name'] = customer_data_result['first_name']
			story_data[key]['last_name'] = customer_data_result['last_name']

				
		return ({"attributes": {
		    		"status_desc": "Customer_stories",
		    		"status": "success"
		    	},
		    	"responseList":story_data}), status.HTTP_200_OK
		
#-----------------------Get-Customer-Stories---------------------#

#----------------------Add-Customer-Product---------------------#
@name_space.route("/addCustomerProduct")	
class addCustomerProduct(Resource):
	@api.expect(customer_product_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		product_meta_id = details['product_meta_id']
		customer_id = details['customer_id']
		organisation_id = 1
		last_update_id = 1
		product_status = "w"
		customer_prodcut_status = 1

		is_favourite = details['is_favourite']

		if is_favourite == "y":

			get_query = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status = "w" """)

			getData = (product_meta_id,customer_id)
			
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

				connection.commit()
				cursor.close()

			return ({"attributes": {
					    		"status_desc": "customer_product_details",
					    		"status": "success"
					    	},
					    	"responseList":"Product Added Successfully"}), status.HTTP_200_OK
		else:
			delete_query = ("""DELETE FROM `customer_product_mapping` WHERE `product_meta_id` = %s and `customer_id` = %s""")
			delData = (product_meta_id,customer_id)
			
			cursor.execute(delete_query,delData)
			connection.commit()
			cursor.close()

			return ({"attributes": {"status_desc": "customer_product_details",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK		


#----------------------Add-Customer-Product---------------------#


#----------------------Product-Customer-List---------------------#

@name_space.route("/getProductCustomerList/<string:key>/<int:user_id>")	
class getProductCustomerList(Resource):
	def get(self,key,user_id):
		if key == "c" or key == "w" or key == "o":
			product_data = 	[
								{
									"user_id":user_id,
									"product_id":1,
									"product_name": "Test Product1",
								    "image": "https://d1lwvo1ffrod0a.cloudfront.net/117/drive.png",
								    "price": 9999.00
	        					},
	        					{
	        						"user_id":user_id,
	        						"product_id":2,
									"text": "Test Product2",
								    "image": "https://d1lwvo1ffrod0a.cloudfront.net/117/image2.png",
								    "price": 10000.00
	        					},
	        					{
	        						"user_id":user_id,
	        						"product_id":3,
									"text": "Test Product3",
								    "image": "https://d1lwvo1ffrod0a.cloudfront.net/117/memorycard.png",
								    "price": 11000.00
								},
								{
	        						"user_id":user_id,
	        						"product_id":4,
									"text": "Test Product4",
								    "image": "https://d1lwvo1ffrod0a.cloudfront.net/117/phone.jpg",
								    "price": 11000.00
								}
							]  					    
	   		
		return ({"attributes": {
		    		"status_desc": "customer_product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK


#----------------------Product-Customer-List---------------------#

#----------------------Product-Customer-List---------------------#

@name_space.route("/getProductCustomerListD/<string:key>/<int:user_id>")	
class getProductCustomerListD(Resource):
	def get(self,key,user_id):

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
				wishlist[tkey]['product_image'] = product_meta_image['product_image']
			else:
				wishlist[tkey]['product_image'] = ""

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
				wishlist[tkey]['qty'] = qty['qty']
			else:
				wishlist[tkey]['qty'] = ""		
	   		
		return ({"attributes": {
		    		"status_desc": "customer_product_details",
		    		"status": "success"
		    	},
		    	"responseList":wishlist}), status.HTTP_200_OK


#----------------------Product-Customer-List---------------------#

#----------------------Dashboard---------------------#
@name_space.route("/dashboard/<int:category_id>/<int:user_id>")	
class dashboard(Resource):
	def get(self,category_id,user_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_category_query = ("""SELECT meta_key_value_id
			FROM `home_category_mapping` """)

		cursor.execute(get_category_query)

		home_category_data = cursor.fetchall()

		for key,data in enumerate(home_category_data):
			get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
			FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

			getdata_key_value = (data['meta_key_value_id'])
			cursor.execute(get_key_value_query,getdata_key_value)

			key_value_data = cursor.fetchone()

			home_category_data[key]['meta_key_value'] = key_value_data['meta_key_value']
			home_category_data[key]['image'] = key_value_data['image']

		get_brand_query = ("""SELECT meta_key_value_id
			FROM `home_brand_mapping` """)

		cursor.execute(get_brand_query)

		home_brand_data = cursor.fetchall()

		for hkey,hdata in enumerate(home_brand_data):
			get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
			FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

			getdata_key_value = (hdata['meta_key_value_id'])
			cursor.execute(get_key_value_query,getdata_key_value)

			key_value_data = cursor.fetchone()

			home_brand_data[hkey]['meta_key_value'] = key_value_data['meta_key_value']
			home_brand_data[hkey]['image'] = key_value_data['image']

		get_top_selling_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`
			FROM `product_top_selling_mapping` pts 
			INNER JOIN `product_meta` pm ON pts.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id` LIMIT 6""")		
		cursor.execute(get_top_selling_product)
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
				top_selling_product[tkey]['totalproduct'] = ""

		get_best_selling_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`,pm.`out_price` price
			FROM `product_best_selling_mapping` pbsm 
			INNER JOIN `product_meta` pm ON pbsm.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id` LIMIT 6""")
		cursor.execute(get_best_selling_product)
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
			INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`""")
		cursor.execute(get_offer_product)
		offer_product = cursor.fetchall()

		get_new_arrival_product =  ("""SELECT pnm.`product_id`,n.`new_arrival_id`,n.`new_arrival_image` as `offer_image`,n.`discount_percentage`
			FROM `product_new_arrival_mapping` pnm 
			INNER JOIN `new_arrival` n ON n.`new_arrival_id` = pnm.`new_arrival_id`  limit 6""")
		cursor.execute(get_new_arrival_product)
		new_arrival_product = cursor.fetchall()

		product_status = "c"

		get_query_count = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `customer_id` = %s and `product_status` = %s """)

		getDataCount = (user_id,product_status)
				
		count_product = cursor.execute(get_query_count,getDataCount)
			
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
		    					"home_brand_data":home_brand_data,"best_selling":best_selling_product,"cart_count":count_product}}), status.HTTP_200_OK

#----------------------Dashboard---------------------#

#----------------------Offer-Details---------------------#
@ecommerce_customer.route("/EcommerceCustomerNew/OfferDetails/<int:organisation_id>/<string:language>/<int:offer_id>/<int:user_id>")	
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])	
def OfferDetails(organisation_id,language,offer_id,user_id):
	connection = mysql_connection()
	cursor = connection.cursor()

	connection_analytics = mysql_connection_analytics()
	cursor_analytics = connection_analytics.cursor()

	customer_id = user_id
	offer_id = offer_id
	from_web_or_phone = 2
	organisation_id = organisation_id
		

	offerviewquery = ("""INSERT INTO `customer_offer_analytics`(`customer_id`,
			`offer_id`, `from_web_or_phone`, `organisation_id`) VALUES (%s,
			%s,%s,%s)""")
	offerviewdata = cursor_analytics.execute(offerviewquery,(customer_id,offer_id,
			from_web_or_phone,organisation_id))

	get_offer_query =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,o.`discount_percentage`,o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`offer_image_type`
			FROM `offer` o		
			WHERE o.`offer_id` = %s""")
	get_offer_data = (offer_id)
	cursor.execute(get_offer_query,get_offer_data)
	offer_data = cursor.fetchone()

	get_offer_product =  ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_long_description`
			FROM `product_offer_mapping` pom			
			INNER JOIN `product` p ON pom.`product_id` = p.`product_id`  			
			WHERE pom.`offer_id` = %s and pom.`organisation_id` = %s """)
	get_offer_product_data = (offer_id,organisation_id)			
	cursor.execute(get_offer_product,get_offer_product_data)
	product_data = cursor.fetchall()

	for key,data in enumerate(product_data):
		get_offer_product_meta = (""" SELECT pm.`product_id`,pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price` FROM `product_meta` pm WHERE 
			`out_price` =  ( SELECT MIN(`out_price`) FROM product_meta  where product_id = %s) and product_id= %s """)
		get_offer_product_meta_data = (data['product_id'],data['product_id'])
		cursor.execute(get_offer_product_meta,get_offer_product_meta_data)

		product_meta_data = cursor.fetchone()

		product_data[key]['product_meta_id'] = product_meta_data['product_meta_id']
		product_data[key]['product_meta_code'] = product_meta_data['product_meta_code']
		product_data[key]['meta_key_text'] = product_meta_data['meta_key_text']
		product_data[key]['in_price'] = product_meta_data['in_price']
		product_data[key]['out_price'] = product_meta_data['out_price']

		a_string = product_meta_data['meta_key_text']
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
			
		get_query_image = ("""SELECT `image`
										FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
		getdata_image = (product_meta_data['product_meta_id'])
		product_image_count = cursor.execute(get_query_image,getdata_image)

		if product_image_count >0 :
			product_image = cursor.fetchone()
			product_data[key]['image'] = product_image['image']
		else:
			product_data[key]['image'] = ""

		get_query_discount = ("""SELECT `discount`
										FROM `product_meta_discount_mapping` pdm
										INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
										WHERE `product_meta_id` = %s """)
		getdata_discount = (product_meta_data['product_meta_id'])
		count_dicscount = cursor.execute(get_query_discount,getdata_discount)

		if count_dicscount > 0:
			product_meta_discount = cursor.fetchone()
			product_data[key]['discount'] = product_meta_discount['discount']

			discount = (data['out_price']/100)*product_meta_discount['discount']
			actual_amount = data['out_price'] - discount

			product_data[key]['after_discounted_price'] = round(actual_amount ,2) 
		else:
			product_data[key]['discount'] = 0
			product_data[key]['after_discounted_price'] = product_meta_data['out_price']

		product_data[key]['rating'] = 4.3

		get_favourite = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

		getFavData = (product_meta_data['product_meta_id'],user_id)
			
		count_fav_product = cursor.execute(get_favourite,getFavData)

		if count_fav_product > 0:
			product_data[key]['is_favourite'] = "y"
		else:
			product_data[key]['is_favourite'] = "n"

		get_cart = ("""SELECT `product_meta_id`
			FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
		getCartData = (product_meta_data['product_meta_id'],user_id)
		count_cart_product = cursor.execute(get_cart,getCartData)

		if count_cart_product > 0:
			product_data[key]['is_cart'] = "y"
		else:
			product_data[key]['is_cart'] = "n"

		get_stock = ("""SELECT pi.`stock` 
			FROM `user_retailer_mapping` urm 
			INNER JOIN `product_inventory` pi ON pi.`retailer_store_id` = urm.`retailer_id` 
			WHERE urm.`user_id` = %s and pi.`product_meta_id` = %s""")
		getstockData = (user_id,product_meta_data['product_meta_id'])

		count_stock = cursor.execute(get_stock,getstockData)

		if count_stock > 0:
			product_data[key]['stock'] = "In Stock"
		else:
			product_data[key]['stock'] = "Out Of Stock"	

	offer_data['product_data'] = product_data

	get_query_offer_image = ("""SELECT `offer_image` FROM `offer_images` WHERE `offer_id` = %s""")
	getdata_offer_image = (offer_id)
	image_count = cursor.execute(get_query_offer_image,getdata_offer_image)

	if image_count > 0:
		offer_images = cursor.fetchall()

		image_a = []

		for image_offer in offer_images:
			image_a.append(image_offer['offer_image'])

		offer_data['images'] = image_a
	else:
		offer_data['images'] = []

	return ({"attributes": {
		    	"status_desc": "offer_details",
		    	"status": "success"
		    },
		    "responseList":offer_data}), status.HTTP_200_OK


#----------------------Offer-Details---------------------#

#----------------------Product-List-By-Home-Brnad-With-Language-and-Pagination---------------------#

@name_space.route("/getProductListByBrandAndCatgoryWithLanguageandPagination/<int:brand_id>/<int:user_id>/<int:organisation_id>/<string:language>/<int:page>/<int:category_id>")	
class getProductListByBrandAndCatgoryWithLanguageandPagination(Resource):
	def get(self,brand_id,user_id,organisation_id,language,page,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if page == 1:
			offset = 0
		else:
			offset = page * 20

		product_status = 1
		get_product_list =  ("""SELECT pbm.`mapping_id`,p.`product_id`,p.`product_name`
			FROM `product_brand_mapping` pbm 
			INNER JOIN `product` p ON pbm.`product_id` = p.`product_id`						
			WHERE pbm.`brand_id` = %s and pbm.`organisation_id` = %s and p.`status` = %s and p.`language` =%s and p.`category_id` = %s LIMIT %s, 20""")
		get_product_data = (brand_id,organisation_id,product_status,language,category_id,offset)
		cursor.execute(get_product_list,get_product_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):

			get_product_meta = (""" SELECT pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price` FROM `product_meta` pm WHERE 
			`out_price` =  ( SELECT MIN(`out_price`) FROM product_meta  where product_id = %s) and product_id= %s """)
			get_product_meta_data = (data['product_id'],data['product_id'])
			count_product_meta = cursor.execute(get_product_meta,get_product_meta_data)

			if count_product_meta > 0:

				product_meta_data = cursor.fetchone()

				product_data[key]['product_meta_id'] = product_meta_data['product_meta_id']
				product_data[key]['product_meta_code'] = product_meta_data['product_meta_code']
				product_data[key]['meta_key_text'] = product_meta_data['meta_key_text']
				product_data[key]['in_price'] = product_meta_data['in_price']
				product_data[key]['out_price'] = product_meta_data['out_price']

				if product_meta_data['meta_key_text'] :

					a_string = product_meta_data['meta_key_text']
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
				
				get_query_image = ("""SELECT `image`
											FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
				getdata_image = (product_meta_data['product_meta_id'])
				product_image_count = cursor.execute(get_query_image,getdata_image)
				product_image = cursor.fetchone()

				get_query_discount = ("""SELECT `discount`
											FROM `product_meta_discount_mapping` pdm
											INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
											WHERE `product_meta_id` = %s """)
				getdata_discount = (product_meta_data['product_meta_id'])
				count_dicscount = cursor.execute(get_query_discount,getdata_discount)

				if count_dicscount > 0:
					product_meta_discount = cursor.fetchone()
					product_data[key]['discount'] = product_meta_discount['discount']

					discount = (product_meta_data['out_price']/100)*product_meta_discount['discount']
					actual_amount = product_meta_data['out_price'] - discount

					product_data[key]['after_discounted_price'] = round(actual_amount,2) 
				else:
					product_data[key]['discount'] = 0
					product_data[key]['after_discounted_price'] = product_meta_data['out_price']

				product_data[key]['rating'] = 4.3

				if product_image_count > 0:
					product_data[key]['image'] = product_image['image']
				else:
					product_data[key]['image'] = ""

				
				get_favourite = ("""SELECT `product_meta_id`
					FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

				getFavData = (product_meta_data['product_meta_id'],user_id)
				
				count_fav_product = cursor.execute(get_favourite,getFavData)

				if count_fav_product > 0:
					product_data[key]['is_favourite'] = "y"
				else:
					product_data[key]['is_favourite'] = "n"

				get_cart = ("""SELECT `product_meta_id`
					FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
				getCartData = (product_meta_data['product_meta_id'],user_id)
				count_cart_product = cursor.execute(get_cart,getCartData)

				if count_cart_product > 0:
					product_data[key]['is_cart'] = "y"
				else:
					product_data[key]['is_cart'] = "n"


				get_stock = ("""SELECT pi.`stock` 
					FROM `user_retailer_mapping` urm 
					INNER JOIN `product_inventory` pi ON pi.`retailer_store_id` = urm.`retailer_id` 
					WHERE urm.`user_id` = %s and pi.`product_meta_id` = %s""")
				getstockData = (user_id,product_meta_data['product_meta_id'])

				count_stock = cursor.execute(get_stock,getstockData)

				if count_stock > 0:
					product_data[key]['stock'] = "In Stock"
				else:
					product_data[key]['stock'] = "Out Of Stock"
			else:
				product_data[key]['out_price'] = 0

		get_product_list_count =  ("""SELECT count(*) as product_count
			FROM `product_brand_mapping` pbm 
			INNER JOIN `product` p ON pbm.`product_id` = p.`product_id`
			INNER JOIN `product_meta` pm ON pbm.`product_id` = pm.`product_id`			
			WHERE pbm.`brand_id` = %s and pbm.`organisation_id` = %s and p.`status` = %s and p.`language` =%s and p.`category_id` = %s""")
		get_product_data_count = (brand_id,organisation_id,product_status,language,category_id)
		cursor.execute(get_product_list_count,get_product_data_count)
		product_data_count = cursor.fetchone()

		page_count = math.trunc(product_data_count['product_count']/20)

		if page_count == 0:
			page_count = 1
		else:
			page_count = page_count + 1

		return ({"attributes": {
		    		"status_desc": "product_list",
		    		"status": "success",
		    		"page_count":page_count,
		    		"current_page": page
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK
			
#----------------------Product-List-By-Home-Brnad-With-Language-and-Pagination---------------------#	

#----------------------Offer-List---------------------#

@name_space.route("/offerList/<int:offer_id>/<int:user_id>")	
class offerList(Resource):
	def get(self,offer_id,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_offer_product =  ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_long_description`,
			pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
			FROM `product_offer_mapping` pom			
			INNER JOIN `product` p ON pom.`product_id` = p.`product_id`  
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			WHERE pom.`offer_id` = %s """)
		get_offer_product_data = (offer_id)			
		cursor.execute(get_offer_product,get_offer_product_data)
		product_data = cursor.fetchall()	

		for key,data in enumerate(product_data):

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
			
			get_query_image = ("""SELECT `image`
										FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
			getdata_image = (data['product_meta_id'])
			product_image_count = cursor.execute(get_query_image,getdata_image)

			if product_image_count >0 :
				product_image = cursor.fetchone()
				product_data[key]['image'] = product_image['image']
			else:
				product_data[key]['image'] = ""

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

				product_data[key]['after_discounted_price'] = round(actual_amount ,2) 
			else:
				product_data[key]['discount'] = 0
				product_data[key]['after_discounted_price'] = data['out_price']

			product_data[key]['rating'] = 4.3

			

			
			get_favourite = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

			getFavData = (data['product_meta_id'],user_id)
			
			count_fav_product = cursor.execute(get_favourite,getFavData)

			if count_fav_product > 0:
				product_data[key]['is_favourite'] = "y"
			else:
				product_data[key]['is_favourite'] = "n"

			get_cart = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
			getCartData = (data['product_meta_id'],user_id)
			count_cart_product = cursor.execute(get_cart,getCartData)

			if count_cart_product > 0:
				product_data[key]['is_cart'] = "y"
			else:
				product_data[key]['is_cart'] = "n"

			get_stock = ("""SELECT pi.`stock` 
				FROM `user_retailer_mapping` urm 
				INNER JOIN `product_inventory` pi ON pi.`retailer_store_id` = urm.`retailer_id` 
				WHERE urm.`user_id` = %s and pi.`product_meta_id` = %s""")
			getstockData = (user_id,data['product_meta_id'])

			count_stock = cursor.execute(get_stock,getstockData)

			if count_stock > 0:
				product_data[key]['stock'] = "In Stock"
			else:
				product_data[key]['stock'] = "Out Of Stock"			

		return ({"attributes": {
		    	"status_desc": "offer_details",
		    	"status": "success"
		    },
		    "responseList":{"offer_data":product_data}}), status.HTTP_200_OK

#----------------------Offer-List---------------------#


#----------------------View-More---------------------#

@name_space.route("/viewMoreProductList/<string:key>/<int:category_id>")	
class viewMoreProductList(Resource):
	def get(self,key,category_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		if key == 'top_selling':
			get_top_selling_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`
			FROM `product_top_selling_mapping` pts 
			INNER JOIN `product_meta` pm ON pts.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id`""")		
			cursor.execute(get_top_selling_product)
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
					top_selling_product[tkey]['totalproduct'] = ""

			return ({"attributes": {
		    		"status_desc": "product_list",
		    		"status": "success"
		    	},
		    	"responseList":top_selling_product}), status.HTTP_200_OK

		if key == 'best_selling':
			get_best_selling_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`,pm.`out_price`
			FROM `product_best_selling_mapping` pbsm 
			INNER JOIN `product_meta` pm ON pbsm.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id` """)
			cursor.execute(get_best_selling_product)
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

			return ({"attributes": {
		    		"status_desc": "product_list",
		    		"status": "success"
		    	},
		    	"responseList":best_selling_product}), status.HTTP_200_OK

		if key == 'new_arrival':
			get_new_arrival_product =  ("""SELECT pnm.`product_id`,n.`new_arrival_id`,n.`new_arrival_image` as `offer_image`,n.`discount_percentage`
			FROM `product_new_arrival_mapping` pnm 
			INNER JOIN `new_arrival` n ON n.`new_arrival_id` = pnm.`new_arrival_id`""")
			cursor.execute(get_new_arrival_product)
			new_arrival_product = cursor.fetchall()

			return ({"attributes": {
		    		"status_desc": "product_list",
		    		"status": "success"
		    	},
		    	"responseList":new_arrival_product}), status.HTTP_200_OK

		if key == 'offer':
			get_offer =  ("""SELECT `offer_id`,`offer_image`,`discount_percentage`,`coupon_code`
			FROM `offer`""")
			cursor.execute(get_offer)
			offer = cursor.fetchall()

			for key,data in enumerate(offer):
				get_offer_product =  ("""SELECT p.`product_id`,p.`product_name`
					FROM `product_offer_mapping` pom			
					INNER JOIN `product` p ON pom.`product_id` = p.`product_id`  
					WHERE pom.`offer_id` = %s """)
				get_offer_product_data = (data['offer_id'])			
				cursor.execute(get_offer_product,get_offer_product_data)
				offer_product = cursor.fetchall()
				offer[key]['product'] = offer_product

			return ({"attributes": {
		    		"status_desc": "product_list",
		    		"status": "success"
		    	},
		    	"responseList":offer}), status.HTTP_200_OK

		if key == 'latest_product':

			get_latest_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`,pm.`out_price`
			FROM `latest_product_mapping` pbsm 
			INNER JOIN `product_meta` pm ON pbsm.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id` 
			WHERE p.`category_id` = %s""")
			latest_product_data = (category_id)
			cursor.execute(get_latest_product,latest_product_data)
			latest_product = cursor.fetchall()

			for bkey,bdata in enumerate(latest_product):
				get_product_meta_image_quey = ("""SELECT `image`
				FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
				product_meta_image_data = (bdata['product_meta_id'])
				rows_count_image_best_selling = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
				if rows_count_image_best_selling > 0:
					product_meta_image = cursor.fetchone()
					latest_product[bkey]['product_image'] = product_meta_image['image']
				else:
					latest_product[bkey]['product_image'] = ""

			return ({"attributes": {
		    		"status_desc": "product_list",
		    		"status": "success"
		    	},
		    	"responseList":latest_product}), status.HTTP_200_OK

#----------------------View-More---------------------#

#----------------------Product-List-By-Category---------------------#
@name_space.route("/getProductListByCategory/<int:category_id>")	
class getProductListByCategory(Resource):
	def get(self,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_latest_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`,pm.`out_price`,pm.`loyalty_points`
			FROM `latest_product_mapping` pbsm 
			INNER JOIN `product_meta` pm ON pbsm.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id` 
			WHERE p.`category_id` = %s LIMIT 6""")
		latest_product_data = (category_id)
		cursor.execute(get_latest_product,latest_product_data)
		latest_product = cursor.fetchall()

		for bkey,bdata in enumerate(latest_product):
			get_product_meta_image_quey = ("""SELECT `image`
			FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
			product_meta_image_data = (bdata['product_meta_id'])
			rows_count_image_best_selling = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
			if rows_count_image_best_selling > 0:
				product_meta_image = cursor.fetchone()
				latest_product[bkey]['product_image'] = product_meta_image['image']
			else:
				latest_product[bkey]['product_image'] = ""

		return ({"attributes": {
		    		"status_desc": "latest_product",
		    		"status": "success"
		    	},
		    	"responseList":latest_product}), status.HTTP_200_OK

#----------------------Product-List-By-Category---------------------#

#----------------------Product-List-By-Category-Price-Range---------------------#
@name_space.route("/getProductListByCategoryPriceRange/<int:category_id>/<int:from_price>/<int:to_price>/<int:user_id>")	
class getProductListByCategoryPriceRange(Resource):
	def get(self,category_id,from_price,to_price,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if category_id == 0:

			get_product_list =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`,pm.`product_meta_code`,pm.`out_price`,pm.`meta_key_text`,pm.`loyalty_points` 
				FROM `product` p 
				INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id` 
				WHERE pm.`out_price` BETWEEN %s AND %s""")
			data = (from_price,to_price)
			

		else:
			get_product_list =  ("""SELECT DISTINCT p.`product_id`,p.`product_name`,pm.`product_meta_id`,pm.`product_meta_code`,pm.`out_price`,pm.`meta_key_text` 
				FROM `product` p 
				INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`  
				WHERE p.`category_id` = %s and pm.`out_price` BETWEEN %s AND %s""")
			data = (category_id,from_price,to_price)
			

		cursor.execute(get_product_list,data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):

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
			
			get_query_image = ("""SELECT `image`
										FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
			getdata_image = (data['product_meta_id'])
			cursor.execute(get_query_image,getdata_image)
			product_image = cursor.fetchone()

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

			product_data[key]['rating'] = 4.3

			product_data[key]['image'] = product_image['image']

			
			get_favourite = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

			getFavData = (data['product_meta_id'],user_id)
			
			count_fav_product = cursor.execute(get_favourite,getFavData)

			if count_fav_product > 0:
				product_data[key]['is_favourite'] = "y"
			else:
				product_data[key]['is_favourite'] = "n"

			get_cart = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
			getCartData = (data['product_meta_id'],user_id)
			count_cart_product = cursor.execute(get_cart,getCartData)

			if count_cart_product > 0:
				product_data[key]['is_cart'] = "y"
			else:
				product_data[key]['is_cart'] = "n"

			get_stock = ("""SELECT pi.`stock` 
				FROM `user_retailer_mapping` urm 
				INNER JOIN `product_inventory` pi ON pi.`retailer_store_id` = urm.`retailer_id` 
				WHERE urm.`user_id` = %s and pi.`product_meta_id` = %s""")
			getstockData = (user_id,data['product_meta_id'])

			count_stock = cursor.execute(get_stock,getstockData)

			if count_stock > 0:
				product_data[key]['stock'] = "In Stock"
			else:
				product_data[key]['stock'] = "Out Of Stock"

		return ({"attributes": {
		    		"status_desc": "latest_product",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List-By-Category-Price-Range---------------------#

#----------------------Product-List-By-Home-Brnad---------------------#

@name_space.route("/getProductListByHomeBrand/<int:meta_key_value_id>/<int:user_id>")	
class getProductListByHomeBrand(Resource):
	def get(self,meta_key_value_id,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_product_list =  ("""SELECT pbm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,pm.`loyalty_points`,
			pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
			FROM `product_brand_mapping` pbm 
			INNER JOIN `product` p ON pbm.`product_id` = p.`product_id`
			INNER JOIN `product_meta` pm ON pbm.`product_id` = pm.`product_id`			
			where pbm.`brand_id` = %s """)
		get_product_data = (meta_key_value_id)
		cursor.execute(get_product_list,get_product_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):

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
			
			get_query_image = ("""SELECT `image`
										FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
			getdata_image = (data['product_meta_id'])
			product_image_count = cursor.execute(get_query_image,getdata_image)
			product_image = cursor.fetchone()

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

			product_data[key]['rating'] = 4.3

			if product_image_count > 0:
				product_data[key]['image'] = product_image['image']
			else:
				product_data[key]['image'] = ""

			
			get_favourite = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

			getFavData = (data['product_meta_id'],user_id)
			
			count_fav_product = cursor.execute(get_favourite,getFavData)

			if count_fav_product > 0:
				product_data[key]['is_favourite'] = "y"
			else:
				product_data[key]['is_favourite'] = "n"

			get_cart = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
			getCartData = (data['product_meta_id'],user_id)
			count_cart_product = cursor.execute(get_cart,getCartData)

			if count_cart_product > 0:
				product_data[key]['is_cart'] = "y"
			else:
				product_data[key]['is_cart'] = "n"


			get_stock = ("""SELECT pi.`stock` 
				FROM `user_retailer_mapping` urm 
				INNER JOIN `product_inventory` pi ON pi.`retailer_store_id` = urm.`retailer_id` 
				WHERE urm.`user_id` = %s and pi.`product_meta_id` = %s""")
			getstockData = (user_id,data['product_meta_id'])

			count_stock = cursor.execute(get_stock,getstockData)

			if count_stock > 0:
				product_data[key]['stock'] = "In Stock"
			else:
				product_data[key]['stock'] = "Out Of Stock"

		return ({"attributes": {
		    		"status_desc": "product_list",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK
			
#----------------------Product-List-By-Home-Brnad---------------------#

#----------------------Product-List-By-Home-Category---------------------#

@name_space.route("/getProductListByHomeCategory/<int:meta_key_value_id>/<int:user_id>")	
class getProductListByHomeCategory(Resource):
	def get(self,meta_key_value_id,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_product_list =  ("""SELECT pbm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
			pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`loyalty_points`
			FROM `product_category_mapping` pbm 
			INNER JOIN `product` p ON pbm.`product_id` = p.`product_id`
			INNER JOIN `product_meta` pm ON pbm.`product_id` = pm.`product_id`			
			where pbm.`category_id` = %s """)
		get_product_data = (meta_key_value_id)
		cursor.execute(get_product_list,get_product_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):

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
			
			get_query_image = ("""SELECT `image`
										FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
			getdata_image = (data['product_meta_id'])
			cursor.execute(get_query_image,getdata_image)
			product_image = cursor.fetchone()

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

			product_data[key]['rating'] = 4.3

			product_data[key]['image'] = product_image['image']

			
			get_favourite = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

			getFavData = (data['product_meta_id'],user_id)
			
			count_fav_product = cursor.execute(get_favourite,getFavData)

			if count_fav_product > 0:
				product_data[key]['is_favourite'] = "y"
			else:
				product_data[key]['is_favourite'] = "n"

			get_cart = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
			getCartData = (data['product_meta_id'],user_id)
			count_cart_product = cursor.execute(get_cart,getCartData)

			if count_cart_product > 0:
				product_data[key]['is_cart'] = "y"
			else:
				product_data[key]['is_cart'] = "n"


			get_stock = ("""SELECT pi.`stock` 
				FROM `user_retailer_mapping` urm 
				INNER JOIN `product_inventory` pi ON pi.`retailer_store_id` = urm.`retailer_id` 
				WHERE urm.`user_id` = %s and pi.`product_meta_id` = %s""")
			getstockData = (user_id,data['product_meta_id'])

			count_stock = cursor.execute(get_stock,getstockData)

			if count_stock > 0:
				product_data[key]['stock'] = "In Stock"
			else:
				product_data[key]['stock'] = "Out Of Stock"

		return ({"attributes": {
		    		"status_desc": "product_list",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK
			
#----------------------Product-List-By-Home-Category---------------------#

#----------------------Product-List---------------------#
@name_space.route("/getProductList/<int:product_id>/<int:user_id>")	
class getProductList(Resource):
	def get(self,product_id,user_id):
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
			
			get_query_image = ("""SELECT `image`
										FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
			getdata_image = (data['product_meta_id'])
			product_image_count = cursor.execute(get_query_image,getdata_image)

			if product_image_count >0 :
				product_image = cursor.fetchone()
				product_data[key]['image'] = product_image['image']
			else:
				product_data[key]['image'] = ""

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

				product_data[key]['after_discounted_price'] = round(actual_amount ,2) 
			else:
				product_data[key]['discount'] = 0
				product_data[key]['after_discounted_price'] = data['out_price']

			product_data[key]['rating'] = 4.3

			

			
			get_favourite = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

			getFavData = (data['product_meta_id'],user_id)
			
			count_fav_product = cursor.execute(get_favourite,getFavData)

			if count_fav_product > 0:
				product_data[key]['is_favourite'] = "y"
			else:
				product_data[key]['is_favourite'] = "n"

			get_cart = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
			getCartData = (data['product_meta_id'],user_id)
			count_cart_product = cursor.execute(get_cart,getCartData)

			if count_cart_product > 0:
				product_data[key]['is_cart'] = "y"
			else:
				product_data[key]['is_cart'] = "n"

			get_stock = ("""SELECT pi.`stock` 
				FROM `user_retailer_mapping` urm 
				INNER JOIN `product_inventory` pi ON pi.`retailer_store_id` = urm.`retailer_id` 
				WHERE urm.`user_id` = %s and pi.`product_meta_id` = %s""")
			getstockData = (user_id,data['product_meta_id'])

			count_stock = cursor.execute(get_stock,getstockData)

			if count_stock > 0:
				product_data[key]['stock'] = "In Stock"
			else:
				product_data[key]['stock'] = "Out Of Stock"

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Product-Details---------------------#
@name_space.route("/productDetails/<int:product_id>/<int:product_meta_code>/<int:user_id>")	
class productDetails(Resource):
	def get(self,product_id,product_meta_code,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
			pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,pm.`loyalty_points`
			FROM `product` p
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			WHERE p.`product_id` = %s and `product_meta_code` = %s""")
		getdata = (product_id,product_meta_code)
		cursor.execute(get_query,getdata)
		product_data = cursor.fetchone()

		
		a_string = product_data['meta_key_text']
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

			product_data['met_key_value'] = met_key

			get_query_all_key_value = ("""SELECT `meta_key_id`,`meta_key_value`,`meta_key_value_id`
					FROM `meta_key_value_master` WHERE `meta_key_id` = %s """)
			getdata_all_key_value = (met_key_value_data['meta_key_id'])
			cursor.execute(get_query_all_key_value,getdata_all_key_value)
			met_key_value_all_data = cursor.fetchall()

				#product_meta[key][met_key_data['meta_key']] = met_key_value_all_data
			met_key_value_all_data_new = []		

			for key_all,met_key_value_all_data_one in  enumerate(met_key_value_all_data):
				met_key_value_all_data_new.append({met_key_value_all_data_one['meta_key_value_id']:met_key_value_all_data_one['meta_key_value']})

			product_data[met_key_data['meta_key']] = met_key_value_all_data_new

		image_a = []	
		get_query_images = ("""SELECT `image`
					FROM `product_meta_images` WHERE `product_meta_id` = %s """)
		getdata_images = (product_data['product_meta_id'])
		cursor.execute(get_query_images,getdata_images)
		images = cursor.fetchall()

		for image in images:
			image_a.append(image['image'])

		product_data['images'] = image_a

		get_query_discount = ("""SELECT `discount`
									FROM `product_meta_discount_mapping` pdm
									INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
									WHERE `product_meta_id` = %s """)
		getdata_discount = (product_data['product_meta_id'])
		count_dicscount = cursor.execute(get_query_discount,getdata_discount)

		if count_dicscount > 0:
			product_meta_discount = cursor.fetchone()
			product_data['discount'] = product_meta_discount['discount']

			discount = (product_data['out_price']/100)*product_meta_discount['discount']
			actual_amount = product_data['out_price'] - discount
			product_data['after_discounted_price'] = round(actual_amount,2)

		else:
			product_data['discount'] = 0
			product_data['after_discounted_price'] = product_data['out_price']

		get_favourite = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)
		getFavData = (product_data['product_meta_id'],user_id)
		count_fav_product = cursor.execute(get_favourite,getFavData)

		if count_fav_product > 0:
			product_data['is_favourite'] = "y"
		else:
			product_data['is_favourite'] = "n"

		get_cart = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
		getCartData = (product_data['product_meta_id'],user_id)
		count_cart_product = cursor.execute(get_cart,getCartData)

		if count_cart_product > 0:
			product_data['is_cart'] = "y"
		else:
			product_data['is_cart'] = "n"
		

		product_data['rating'] = 4.3

		get_stock = ("""SELECT pi.`stock` 
				FROM `user_retailer_mapping` urm 
				INNER JOIN `product_inventory` pi ON pi.`retailer_store_id` = urm.`retailer_id` 
				WHERE urm.`user_id` = %s and pi.`product_meta_id` = %s""")
		getstockData = (user_id,product_data['product_meta_id'])
		count_stock = cursor.execute(get_stock,getstockData)

		if count_stock > 0:
			product_data['stock'] = "In Stock"
		else:
			product_data['stock'] = "Out Of Stock"

		get_address_query = ("""SELECT `address_line_1`,`address_line_2`,`city`,`country`,`state`,`pincode`
				FROM `admins` WHERE `admin_id` = %s""")
		getAddressData = (user_id)
		cursor.execute(get_address_query,getAddressData)

		address_data = cursor.fetchone()

		product_data['address'] = address_data

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-Details---------------------#

#----------------------Add-To-Cart---------------------#
@name_space.route("/addProductToCart")	
class addProductToCart(Resource):
	@api.expect(add_to_cart_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		product_meta_id = details['product_meta_id']
		customer_id = details['customer_id']
		organisation_id = 1
		last_update_id = 1
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

#----------------------Apply-Cupon---------------------#

@name_space.route("/applyCoupon")	
class applyCupon(Resource):
	@api.expect(apply_cupon_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		coupon_code = details['coupon_code']

		get_query = ("""SELECT `coupon_code`
			FROM `offer` WHERE  `coupon_code` = %s""")

		getData = (coupon_code)
			
		count = cursor.execute(get_query,getData)

		if count >0:

			data = cursor.fetchone()


			return ({"attributes": {
					"status_desc": "coupon_details",
					"status": "success"
				},
					"responseList":data}), status.HTTP_200_OK
		else:

			return ({"attributes": {
			    		"status_desc": "coupon_details",
			    		"status": "error",
			    		"message":"Invalid Coupon"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

#----------------------Apply-Cupon---------------------#


#----------------------Delete-cart-Item---------------------#

@name_space.route("/deleteCartItem/<int:cart_id>")
class deleteFolderCourse(Resource):
	def delete(self, cart_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_cart_query = ("""DELETE FROM `customer_product_mapping` WHERE `mapping_id` = %s """)
		delcartData = (cart_id)
		
		cursor.execute(delete_cart_query,delcartData)

		delete_cart_qty_query = ("""DELETE FROM `customer_product_mapping_qty` WHERE `customer_product_mapping_qty` = %s """)
		delcartqtyData = (cart_id)
		
		cursor.execute(delete_cart_qty_query,delcartqtyData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Cart",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Folder-Course---------------------#

#----------------------Update-Cart-Item---------------------#

@name_space.route("/UpdateCartItem/<int:cart_id>")
class UpdateCartItem(Resource):
	@api.expect(cart_putmodel)
	def put(self,cart_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		qty = details['qty']
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
@name_space.route("/saveOrder")
class saveOrder(Resource):
	@api.expect(save_order)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		user_id = details['user_id']
		amount = details['amount']
		purpose = details['purpose']
		coupon_code = details['coupon_code']

		initiate_paymengt_status = 1
		organisation_id  = 1
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
							"coupon_code":coupon_code
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
						sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/sendAppPushNotifications"
						payloadpushData = {
							"device_id":device_token_data['device_token'],
							"firebase_key":"AAAATLVsDiA:APA91bFYEaJWn4PT09fp53An-H2Gmsn9kojQpX6V9Y8ol0Rj6qhH_j_Uos6Gua1kGMcuO5YsxNgbwp3HDZlE9fUNiUsM9ePEghWGaMDCXWXDiURHlHZnkDEvIvGvfYTrCecioM0Nx9hX"
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
								headers = {'Content-type':'application/json', 'Accept':'application/json'}
								sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/sendAppPushNotificationforloyalityPoint"
								payloadpushData = {
									"device_id":device_token_data['device_token'],
									"firebase_key":"AAAATLVsDiA:APA91bFYEaJWn4PT09fp53An-H2Gmsn9kojQpX6V9Y8ol0Rj6qhH_j_Uos6Gua1kGMcuO5YsxNgbwp3HDZlE9fUNiUsM9ePEghWGaMDCXWXDiURHlHZnkDEvIvGvfYTrCecioM0Nx9hX"
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

@name_space.route("/createInvoice")
class createInvoice(Resource):
	@api.expect(create_invoice)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		data = {}

		get_user_query = ("""SELECT `name`,`first_name`,`last_name`,`email`,`phoneno`,`address_line_1`,`address_line_2`,
							`city`,`country`,`state`,`pincode`
				FROM `admins` WHERE  `admin_id` = %s""")
		getUserData = (details['user_id'])
		countUser = cursor.execute(get_user_query,getUserData)

		if countUser > 0:
			customer_data = cursor.fetchone()
			data['customer_data'] = customer_data
		else:
			data['customer_data'] = ""

		get_transaction_query = ("""SELECT `transaction_id`,`amount`,`status`,`customer_product_json`,`coupon_code`,`last_update_ts`
			FROM `instamojo_payment_request` WHERE  `user_id` = %s and transaction_id = %s""")

		getTransactionData = (details['user_id'],details['transaction_id'])
			
		countTransaction = cursor.execute(get_transaction_query,getTransactionData)

		if countTransaction > 0:
			order_data = cursor.fetchone()

			product_status = "o"
			customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
				pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
				FROM `order_product` op
				INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
				INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
				INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
				where op.`transaction_id` = %s and cpm.`product_status` = %s""")	

			customer_product_data = (order_data['transaction_id'],product_status)				

			count_customer_product = cursor.execute(customer_product_query,customer_product_data)

			if count_customer_product > 0:

				customer_product = cursor.fetchall()

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

						get_query_discount = ("""SELECT `discount`
												FROM `product_meta_discount_mapping` pdm
												INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
												WHERE `product_meta_id` = %s """)
						getdata_discount = (tdata['product_meta_id'])
						count_dicscount = cursor.execute(get_query_discount,getdata_discount)

						if count_dicscount > 0:
							product_meta_discount = cursor.fetchone()
							customer_product[tkey]['discount'] = product_meta_discount['discount']

							discount = (tdata['out_price']/100)*product_meta_discount['discount']
							actual_amount = tdata['out_price'] - discount
							customer_product[tkey]['after_discounted_price'] = round(actual_amount,2)

						else:
							customer_product[tkey]['discount'] = 0
							customer_product[tkey]['after_discounted_price'] = tdata['out_price']

						qty_quey = ("""SELECT `qty` 
							FROM `customer_product_mapping_qty` WHERE `customer_mapping_id` = %s""")
						qty_data = (tdata['mapping_id'])
						rows_count_qty = cursor.execute(qty_quey,qty_data)
						if rows_count_qty > 0:
							qty = cursor.fetchone()
							customer_product[tkey]['qty'] = qty['qty']
						else:
							customer_product[tkey]['qty'] = 0

						customer_product[tkey]['actual_price'] = qty['qty'] * tdata['out_price']	

					order_data['customer_product'] = customer_product
					order_data['last_update_ts'] = str(order_data['last_update_ts'])
			
			data['order_data'] = order_data

		else:
			data['order_data'] = {}

		sent_email_status = invoice(data)


		"""abs_html_path = 
		print(abs_html_path)	
	
		res = 'Failure. Wrong MailId or SourceApp.'

		msg = MIMEMultipart()
		msg['Subject'] = "Order Details"
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = "sutandra.mazumder@gmail.com"

		html = invoice(data)
		part1 = MIMEText(html, 'html')
		
		msg.attach(part1)

		try:
			smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, "talk.to.sutandra@gmail.com", msg.as_string())

			res = {"status":'Success'}
			sent = 'Y'

		except Exception as e:
			res = {"status":'Failure'}
			sent = 'N'
		smtp.quit()	

		user_id = details['user_id']

		uploadURL = BASE_URL + 'aws_portal_upload/awsResourceUploadController/uploadToS3Bucket/{}'.format(user_id)
		headers = {"content-type": "multipart/form-data"}

		files = {}

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		file_name = "Invoice"+date_of_creation+str(details['transaction_id'])+".html"
		 
		files['file'] = (file_name, abs_html_path)
		
		uploadRes = requests.post(uploadURL,files=files).json()
		responselist = json.dumps(uploadRes['responseList'][0])
		s2 = json.loads(responselist)

		invoice_url = s2['FilePath'] 

		if(len(invoice_url) != 0): """ 

			#update_query = ("""UPDATE `instamojo_payment_request` SET `invoice_url` = %s
				#WHERE `transaction_id` = %s """)
			#update_data = (invoice_url,details['transaction_id'])
			#cursor.execute(update_query,update_data)

		return ({"attributes": {"status_desc": "Invoice Created Successfully",
									"status": "success"},
					"responseList": sent_email_status}), status.HTTP_200_OK


#----------------------Buy---------------------#

@name_space.route("/buy")
class buy(Resource):
	@api.expect(buy_model)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		user_id = details['user_id']
		amount = details['amount']
		purpose = details['purpose']
		product_meta_id = details['product_meta_id']
		coupon_code = details['coupon_code']

		initiate_paymengt_status = 1
		organisation_id  = 1
		last_update_id = 1

		select_product_status = "c"

		initiatePaymentQuery = ("""INSERT INTO `instamojo_initiate_payment`(`user_id`, 
				`status`,`organisation_id`,`last_update_id`) VALUES (%s,%s,%s,%s)""")
		initiateData = (user_id,initiate_paymengt_status,organisation_id,last_update_id)
		cursor.execute(initiatePaymentQuery,initiateData)
		transaction_id = cursor.lastrowid

		get_customer_product_query = ("""SELECT `mapping_id`,`product_meta_id`,`product_status`
			FROM `customer_product_mapping` WHERE  `customer_id` = %s and `product_meta_id` = %s and product_status = %s""")

		geCustomerProductData = (user_id,product_meta_id,select_product_status)
			
		customerProductCount = cursor.execute(get_customer_product_query,geCustomerProductData)

		if customerProductCount > 0:
			customerProductData = cursor.fetchone()
			get_customer_product_qty_query = ("""SELECT `qty`
			FROM `customer_product_mapping_qty` WHERE  `customer_mapping_id` = %s """)

			getCustomerProductQtyData = (customerProductData['mapping_id'])
			
			customerProductQtyCount = cursor.execute(get_customer_product_qty_query,getCustomerProductQtyData)

			if customerProductQtyCount > 0 :

				customer_product_status = "o"

				customerProductQtyData = cursor.fetchone()

				qty = customerProductQtyData['qty'] + 1

				customer_product_update_qty_query = ("""UPDATE `customer_product_mapping_qty` SET `qty` = %s
					WHERE `customer_mapping_id` = %s""")
				update_qty_data = (qty,customerProductData['mapping_id'])
				cursor.execute(customer_product_update_qty_query,update_qty_data)

				CustomerProductUpdateQuery = ("""UPDATE `customer_product_mapping` SET `product_status` = %s 
					WHERE `mapping_id` = %s""")
				update_customer_product_data = (customer_product_status,customerProductData['mapping_id'])
				cursor.execute(CustomerProductUpdateQuery,update_customer_product_data)

			else:
				insert_qty = 1 
				insertCustomerProductQtyQuery = ("""INSERT INTO `customer_product_mapping_qty`(`customer_mapping_id`, 
					`qty`,`status`,`organisation_id`,`last_update_id`) VALUES (%s,%s,%s,%s,%s)""")
				insertCustomerProductQtyData = (customerProductData['mapping_id'],insert_qty,initiate_paymengt_status,organisation_id,last_update_id)
				cursor.execute(orderProductQuery,orderProductData)

			orderProductQuery = ("""INSERT INTO `order_product`(`transaction_id`, 
				`customer_mapping_id`,`status`,`organisation_id`,`last_update_id`) VALUES (%s,%s,%s,%s,%s)""")
			orderProductData = (transaction_id,customerProductData['mapping_id'],initiate_paymengt_status,organisation_id,last_update_id)
			cursor.execute(orderProductQuery,orderProductData)
		else:

			customer_product_status = "o"
			insert_query = ("""INSERT INTO `customer_product_mapping`(`customer_id`,`product_meta_id`,`product_status`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s)""")

			data = (user_id,product_meta_id,customer_product_status,initiate_paymengt_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)		

			mapping_id = cursor.lastrowid
			details['mapping_id'] = mapping_id

			qty = 1
			qty_status = 1

			insert_qty_query = ("""INSERT INTO `customer_product_mapping_qty`(`customer_mapping_id`,`qty`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
			data_qty = (mapping_id,qty,qty_status,organisation_id,last_update_id)
			cursor.execute(insert_qty_query,data_qty)

			orderProductQuery = ("""INSERT INTO `order_product`(`transaction_id`, 
				`customer_mapping_id`,`status`,`organisation_id`,`last_update_id`) VALUES (%s,%s,%s,%s,%s)""")
			orderProductData = (transaction_id,mapping_id,initiate_paymengt_status,organisation_id,last_update_id)
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
						"coupon_code":coupon_code
					}
	

			mojoResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()	

			product_loyality_point_query = 	("""SELECT `loyalty_points`
				FROM `product_meta` WHERE  `product_meta_id` = %s """)
			getProductLoyaltyData = (product_meta_id)
			
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
					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/sendAppPushNotificationforloyalityPoint"
					payloadpushData = {
						"device_id":device_token_data['device_token'],
						"firebase_key":"AAAATLVsDiA:APA91bFYEaJWn4PT09fp53An-H2Gmsn9kojQpX6V9Y8ol0Rj6qhH_j_Uos6Gua1kGMcuO5YsxNgbwp3HDZlE9fUNiUsM9ePEghWGaMDCXWXDiURHlHZnkDEvIvGvfYTrCecioM0Nx9hX"
					}
					print(payloadpushData)

					send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()


			if mojoResponse['responseList']['transactionId']:
				createInvoiceUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/createInvoice"
				#createInvoiceUrl = "http://127.0.0.1:5000/ecommerce_customer/EcommerceCustomer/createInvoice"
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
				sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer/EcommerceCustomer/sendAppPushNotifications"
				payloadpushData = {
					"device_id":device_token_data['device_token'],
					"firebase_key":"AAAATLVsDiA:APA91bFYEaJWn4PT09fp53An-H2Gmsn9kojQpX6V9Y8ol0Rj6qhH_j_Uos6Gua1kGMcuO5YsxNgbwp3HDZlE9fUNiUsM9ePEghWGaMDCXWXDiURHlHZnkDEvIvGvfYTrCecioM0Nx9hX"
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

			connection.commit()
			cursor.close()

			return ({"attributes": {"status_desc": "Instamojo payment request Details",
									"status": "success"},
					"responseList": mojoResponse['responseList']}), status.HTTP_200_OK
		else:
			return ({"attributes": {
			    		"status_desc": "Instamojo payment request Details",
			    		"status": "error",
			    		"message":"Invalid User"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK
		

#----------------------Buy---------------------#


@name_space.route("/updateCustomerWallet/<int:user_id>")
class updateCustomerWallet(Resource):
	@api.expect(customer_wallet_putmodel)
	def put(self, user_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		user_wallet = details['wallet']

		update_query = ("""UPDATE `admins` SET `wallet` = %s
				WHERE `admin_id` = %s """)
		update_data = (user_wallet,user_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Customer Wallet",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------createPaymentRequest---------------------#
@name_space.route("/createPaymentRequest")
class createPaymentRequest(Resource):
	@api.expect(create_payment_link_model)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		details['redirect_url'] = 'http://creamsonservices.com/instamojoEcommerce.php'
		details['allow_repeated_payments'] = False
		details['send_email'] = False
		details['send_sms'] = True
		userId = details.get('user_id',None)
		details.pop('user_id',None)
		transactionId = details.get('transaction_id',None)		
		details.pop('transaction_id',None)

		coupon_code = details.get('coupon_code',None)
		organisation_id = 1

		payload = {"grant_type": "client_credentials",
					"client_id": CLIENT_ID,
					"client_secret": CLIENT_SECRET}

		authResponse = requests.post(MOJO_TEST_URL+"oauth2/token/",
			data=payload).json()

		accesstoken = authResponse.get('access_token')

		headers = {"Authorization": "Bearer "+accesstoken}

		mojoResponse = requests.post(
		  "https://test.instamojo.com/v2/payment_requests/", 
		  data=details, 
		  headers=headers
		)

		statusCode = mojoResponse.status_code
		
		if statusCode == 201:
			response = mojoResponse.json()

			mojoResInsertQuery = ("""INSERT INTO `instamojo_payment_request`(`instamojo_request_id`, 
				`phone`, `email`, `buyer_name`, `amount`, `purpose`, `status`, `send_sms`, `coupon_code`,
				`send_email`, `sms_status`, `email_status`, `shorturl`, `longurl`, 
				`redirect_url`, `webhook`, `scheduled_at`, `expires_at`, `allow_repeated_payments`, 
				`mark_fulfilled`, `customer_id`, `created_at`, `modified_at`, `resource_uri`, 
				`remarks`,`organisation_id`, `user_id`,`transaction_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
				%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

			created_at = datetime.strptime(response.get('created_at'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
			modified_at = datetime.strptime(response.get('modified_at'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')

			mojoData = (response.get('id'),details.get('phone'),response.get('email'),
				response.get('buyer_name'),response.get('amount'),response.get('purpose'),
				response.get('status'),response.get('send_sms'),coupon_code,response.get('send_email'),response.get('sms_status'),response.get('email_status'),response.get('shorturl'),
				response.get('longurl'),response.get('redirect_url'),response.get('webhook'),
				response.get('scheduled_at'),response.get('expires_at'),response.get('allow_repeated_payments'),
				response.get('mark_fulfilled'),response.get('customer_id'),
				created_at,modified_at,response.get('resource_uri'),response.get('remarks'),organisation_id,userId,transactionId)
			cursor.execute(mojoResInsertQuery,mojoData)

			print(cursor._last_executed)

			requestId = cursor.lastrowid

			response['transactionId'] = transactionId
			response['paymentRequestId'] = requestId

			#createInvoiceURL = BASE_URL + "ecommerce_customer/EcommerceCustomer/createInvoice"

			#invoiceheaders = {'Content-type':'application/json', 'Accept':'application/json'}

			#invoiceData = {
							#"user_id":userId,
							#"transaction_id":transaction_id
						#}

			#requests.post(createInvoiceURL,data=json.dumps(invoiceData), headers=invoiceheaders).json()

			msg = 'Payment Link Created'
		else:
			response = {}
			msg = 'No matching credentials'

		return ({"attributes": {
					"status_desc": "Payment Request",
					"status": "success",
					"msg":msg
				},
					"responseList":response}), status.HTTP_200_OK

#----------------------createPaymentRequest---------------------#


#----------------------updatePaymentDetails---------------------#

@name_space.route("/updatePaymentDetails/<string:payment_id>/<string:payment_status>/<string:payment_request_id>")
class updatePaymentDetails(Resource):
	def put(self,payment_id,payment_status,payment_request_id):
		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		update_status = 'Complete'
		
		updatePaymentQuery = ("""UPDATE `instamojo_payment_request` SET  
			`payment_status` = %s,`payment_id`= %s, `status` = %s WHERE `instamojo_request_id`= %s""")

		paymentData = (payment_status,payment_id,update_status,payment_request_id)

		cursor.execute(updatePaymentQuery,paymentData)

		return ({"attributes": {"status_desc": "Instamojo Payment Details",
							"status": "success"},
			"responseList": 'Payment Details Updated'}), status.HTTP_200_OK

#----------------------updatePaymentDetails---------------------#

#----------------------Order-History---------------------#

@name_space.route("/orderHistory/<int:user_id>")	
class getMetaKeyDetails(Resource):
	def get(self,user_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,
			a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			WHERE  ipr.`user_id` = %s""")

		getData = (user_id)
			
		count = cursor.execute(get_query,getData)

		if count > 0:
			order_data = cursor.fetchall()

			for key,data in enumerate(order_data):
				product_status = "o"
				customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
					pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
					FROM `order_product` op
					INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
					INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
					INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
					where op.`transaction_id` = %s and cpm.`product_status` = %s """)	

				customer_product_data = (data['transaction_id'],product_status)
				cursor.execute(customer_product_query,customer_product_data)

				customer_product = cursor.fetchall()

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

						customer_product[tkey]['met_key_value'] = met_key

					get_query_discount = ("""SELECT `discount`
											FROM `product_meta_discount_mapping` pdm
											INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
											WHERE `product_meta_id` = %s """)
					getdata_discount = (tdata['product_meta_id'])
					count_dicscount = cursor.execute(get_query_discount,getdata_discount)

					if count_dicscount > 0:
						product_meta_discount = cursor.fetchone()
						customer_product[tkey]['discount'] = product_meta_discount['discount']

						discount = (tdata['out_price']/100)*product_meta_discount['discount']
						actual_amount = tdata['out_price'] - discount
						customer_product[tkey]['after_discounted_price'] = round(actual_amount,2)

					else:
						customer_product[tkey]['discount'] = 0
						customer_product[tkey]['after_discounted_price'] = tdata['out_price']

					qty_quey = ("""SELECT `qty` 
						FROM `customer_product_mapping_qty` WHERE `customer_mapping_id` = %s""")
					qty_data = (tdata['mapping_id'])
					rows_count_qty = cursor.execute(qty_quey,qty_data)
					if rows_count_qty > 0:
						qty = cursor.fetchone()
						customer_product[tkey]['qty'] = qty['qty']
					else:
						customer_product[tkey]['qty'] = ""	

				order_data[key]['customer_product'] = customer_product

			return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
					"responseList":order_data}), status.HTTP_200_OK

		else:

			return ({"attributes": {
			    		"status_desc": "order_history",
			    		"status": "success"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

#----------------------Order-History---------------------#

#----------------------search---------------------#
@name_space.route("/Search/<string:product_name>/<int:user_id>")	
class Search(Resource):
	def get(self,product_name,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_meta_query = ("""SELECT `meta_key_id` as `meta_key_value_id`,`meta_key` as `meta_key_value`
			FROM `meta_key_master` WHERE  `meta_key` LIKE %s """)

		getMetaData = ("%"+product_name+"%")
			
		count_meta_data = cursor.execute(get_meta_query,getMetaData)

		if count_meta_data >0:

			search_meta = cursor.fetchall()

			for key,data in enumerate(search_meta):
				get_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_short_description`,
					pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
					FROM `product` p
					INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
					WHERE p.`category_id`= %s """)
				getProductData = (data['meta_key_value_id'])
				count_product_data = cursor.execute(get_product_query,getProductData)

				if count_product_data > 0:
					product_data = cursor.fetchall()

					for pkey,pdata in enumerate(product_data):

						a_string = pdata['meta_key_text']
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

							product_data[pkey]['met_key_value'] = met_key


						get_query_image = ("""SELECT `image`
											FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
						getdata_image = (pdata['product_meta_id'])
						product_image_count = cursor.execute(get_query_image,getdata_image)

						if product_image_count >0 :
							product_image = cursor.fetchone()
							product_data[pkey]['image'] = product_image['image']
						else:
							product_data[pkey]['image'] = ""

						get_query_discount = ("""SELECT `discount`
											FROM `product_meta_discount_mapping` pdm
											INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
											WHERE `product_meta_id` = %s """)
						getdata_discount = (pdata['product_meta_id'])
						count_dicscount = cursor.execute(get_query_discount,getdata_discount)

						if count_dicscount > 0:
							product_meta_discount = cursor.fetchone()
							product_data[pkey]['discount'] = product_meta_discount['discount']

							discount = (pdata['out_price']/100)*product_meta_discount['discount']
							actual_amount = pdata['out_price'] - discount

							product_data[pkey]['after_discounted_price'] = round(actual_amount ,2) 
						else:
							product_data[pkey]['discount'] = 0
							product_data[pkey]['after_discounted_price'] = pdata['out_price']

						product_data[pkey]['rating'] = 4.3
				
						get_favourite = ("""SELECT `product_meta_id`
							FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

						getFavData = (pdata['product_meta_id'],user_id)
				
						count_fav_product = cursor.execute(get_favourite,getFavData)

						if count_fav_product > 0:
							product_data[pkey]['is_favourite'] = "y"
						else:
							product_data[pkey]['is_favourite'] = "n"

						get_cart = ("""SELECT `product_meta_id`
							FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
						getCartData = (pdata['product_meta_id'],user_id)
						count_cart_product = cursor.execute(get_cart,getCartData)

						if count_cart_product > 0:
							product_data[pkey]['is_cart'] = "y"
						else:
							product_data[pkey]['is_cart'] = "n"

					search_meta[key]['product_list'] = product_data
				else:					
					search_meta.pop(key)
					
			
			return ({"attributes": {
					"status_desc": "product_list",
					"status": "success"
				},
					"responseList":search_meta}), status.HTTP_200_OK
		else:
			get_product_query = ("""SELECT m.`meta_key_value_id`,m.`meta_key_value`
			 	FROM `product_brand_mapping` pb 
			 	INNER JOIN `product` p ON p.`product_id` = pb.`product_id` 
			 	INNER JOIN `meta_key_value_master` m ON m.`meta_key_value_id` = pb.`brand_id`
				WHERE m.`meta_key_value` LIKE %s""")
			getProductData = ("%"+product_name+"%")
			count_product_data = cursor.execute(get_product_query,getProductData)

			if count_product_data > 0:
				search_meta = cursor.fetchall()

				for key,data in enumerate(search_meta):
					get_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_short_description`,
						pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
						FROM `product` p
						INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
						WHERE p.`product_name` LIKE %s """)
					getProductData = ("%"+product_name+"%")
					count_product_data = cursor.execute(get_product_query,getProductData)

					if count_product_data > 0:
						product_data = cursor.fetchall()

						for pkey,pdata in enumerate(product_data):

							a_string = pdata['meta_key_text']
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

								product_data[pkey]['met_key_value'] = met_key


							get_query_image = ("""SELECT `image`
												FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
							getdata_image = (pdata['product_meta_id'])
							product_image_count = cursor.execute(get_query_image,getdata_image)

							if product_image_count >0 :
								product_image = cursor.fetchone()
								product_data[pkey]['image'] = product_image['image']
							else:
								product_data[pkey]['image'] = ""

							get_query_discount = ("""SELECT `discount`
												FROM `product_meta_discount_mapping` pdm
												INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
												WHERE `product_meta_id` = %s """)
							getdata_discount = (pdata['product_meta_id'])
							count_dicscount = cursor.execute(get_query_discount,getdata_discount)

							if count_dicscount > 0:
								product_meta_discount = cursor.fetchone()
								product_data[pkey]['discount'] = product_meta_discount['discount']

								discount = (pdata['out_price']/100)*product_meta_discount['discount']
								actual_amount = pdata['out_price'] - discount

								product_data[pkey]['after_discounted_price'] = round(actual_amount ,2) 
							else:
								product_data[pkey]['discount'] = 0
								product_data[pkey]['after_discounted_price'] = pdata['out_price']

							product_data[pkey]['rating'] = 4.3
					
							get_favourite = ("""SELECT `product_meta_id`
								FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

							getFavData = (pdata['product_meta_id'],user_id)
					
							count_fav_product = cursor.execute(get_favourite,getFavData)

							if count_fav_product > 0:
								product_data[pkey]['is_favourite'] = "y"
							else:
								product_data[pkey]['is_favourite'] = "n"

							get_cart = ("""SELECT `product_meta_id`
								FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
							getCartData = (pdata['product_meta_id'],user_id)
							count_cart_product = cursor.execute(get_cart,getCartData)

							if count_cart_product > 0:
								product_data[pkey]['is_cart'] = "y"
							else:
								product_data[pkey]['is_cart'] = "n"

						search_meta[key]['product_list'] = product_data
					else:					
						search_meta.pop(key)

			else:
				get_product_query = ("""SELECT m.`meta_key_value_id`,m.`meta_key_value`
				 	FROM `product_brand_mapping` pb 
				 	INNER JOIN `product` p ON p.`product_id` = pb.`product_id` 
				 	INNER JOIN `meta_key_value_master` m ON m.`meta_key_value_id` = pb.`brand_id`
					WHERE p.`product_name` LIKE %s""")
				getProductData = ("%"+product_name+"%")
				count_product_data = cursor.execute(get_product_query,getProductData)

					
				if count_product_data > 0:
					search_meta = cursor.fetchall()

					for key,data in enumerate(search_meta):
						get_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_short_description`,
							pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
							FROM `product` p
							INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
							WHERE p.`product_name` LIKE %s """)
						getProductData = ("%"+product_name+"%")
						count_product_data = cursor.execute(get_product_query,getProductData)

						if count_product_data > 0:
							product_data = cursor.fetchall()

							for pkey,pdata in enumerate(product_data):

								a_string = pdata['meta_key_text']
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

									product_data[pkey]['met_key_value'] = met_key


								get_query_image = ("""SELECT `image`
													FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
								getdata_image = (pdata['product_meta_id'])
								product_image_count = cursor.execute(get_query_image,getdata_image)

								if product_image_count >0 :
									product_image = cursor.fetchone()
									product_data[pkey]['image'] = product_image['image']
								else:
									product_data[pkey]['image'] = ""

								get_query_discount = ("""SELECT `discount`
													FROM `product_meta_discount_mapping` pdm
													INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
													WHERE `product_meta_id` = %s """)
								getdata_discount = (pdata['product_meta_id'])
								count_dicscount = cursor.execute(get_query_discount,getdata_discount)

								if count_dicscount > 0:
									product_meta_discount = cursor.fetchone()
									product_data[pkey]['discount'] = product_meta_discount['discount']

									discount = (pdata['out_price']/100)*product_meta_discount['discount']
									actual_amount = pdata['out_price'] - discount

									product_data[pkey]['after_discounted_price'] = round(actual_amount ,2) 
								else:
									product_data[pkey]['discount'] = 0
									product_data[pkey]['after_discounted_price'] = pdata['out_price']

								product_data[pkey]['rating'] = 4.3
						
								get_favourite = ("""SELECT `product_meta_id`
									FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

								getFavData = (pdata['product_meta_id'],user_id)
						
								count_fav_product = cursor.execute(get_favourite,getFavData)

								if count_fav_product > 0:
									product_data[pkey]['is_favourite'] = "y"
								else:
									product_data[pkey]['is_favourite'] = "n"

								get_cart = ("""SELECT `product_meta_id`
									FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
								getCartData = (pdata['product_meta_id'],user_id)
								count_cart_product = cursor.execute(get_cart,getCartData)

								if count_cart_product > 0:
									product_data[pkey]['is_cart'] = "y"
								else:
									product_data[pkey]['is_cart'] = "n"

							search_meta[key]['product_list'] = product_data
						else:					
							search_meta.pop(key)
				else:
					get_product_query = ("""SELECT m.`meta_key_value_id`,m.`meta_key_value`
				 	FROM `product_category_mapping` pb 
				 	INNER JOIN `product` p ON p.`product_id` = pb.`product_id` 
				 	INNER JOIN `meta_key_value_master` m ON m.`meta_key_value_id` = pb.`category_id`
					WHERE p.`product_name` LIKE %s""")
					getProductData = ("%"+product_name+"%")
					count_product_data = cursor.execute(get_product_query,getProductData)

						
					if count_product_data > 0:
						search_meta = cursor.fetchall()

						for key,data in enumerate(search_meta):
							get_product_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_short_description`,
								pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
								FROM `product` p
								INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
								WHERE p.`product_name` LIKE %s """)
							getProductData = ("%"+product_name+"%")
							count_product_data = cursor.execute(get_product_query,getProductData)

							if count_product_data > 0:
								product_data = cursor.fetchall()

								for pkey,pdata in enumerate(product_data):

									a_string = pdata['meta_key_text']
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

										product_data[pkey]['met_key_value'] = met_key


									get_query_image = ("""SELECT `image`
														FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
									getdata_image = (pdata['product_meta_id'])
									product_image_count = cursor.execute(get_query_image,getdata_image)

									if product_image_count >0 :
										product_image = cursor.fetchone()
										product_data[pkey]['image'] = product_image['image']
									else:
										product_data[pkey]['image'] = ""

									get_query_discount = ("""SELECT `discount`
														FROM `product_meta_discount_mapping` pdm
														INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
														WHERE `product_meta_id` = %s """)
									getdata_discount = (pdata['product_meta_id'])
									count_dicscount = cursor.execute(get_query_discount,getdata_discount)

									if count_dicscount > 0:
										product_meta_discount = cursor.fetchone()
										product_data[pkey]['discount'] = product_meta_discount['discount']

										discount = (pdata['out_price']/100)*product_meta_discount['discount']
										actual_amount = pdata['out_price'] - discount

										product_data[pkey]['after_discounted_price'] = round(actual_amount ,2) 
									else:
										product_data[pkey]['discount'] = 0
										product_data[pkey]['after_discounted_price'] = pdata['out_price']

									product_data[pkey]['rating'] = 4.3
							
									get_favourite = ("""SELECT `product_meta_id`
										FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

									getFavData = (pdata['product_meta_id'],user_id)
							
									count_fav_product = cursor.execute(get_favourite,getFavData)

									if count_fav_product > 0:
										product_data[pkey]['is_favourite'] = "y"
									else:
										product_data[pkey]['is_favourite'] = "n"

									get_cart = ("""SELECT `product_meta_id`
										FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="c" """)
									getCartData = (pdata['product_meta_id'],user_id)
									count_cart_product = cursor.execute(get_cart,getCartData)

									if count_cart_product > 0:
										product_data[pkey]['is_cart'] = "y"
									else:
										product_data[pkey]['is_cart'] = "n"

								search_meta[key]['product_list'] = product_data
							else:					
								search_meta.pop(key)		
					else:
						search_meta = []	

			return ({"attributes": {
					"status_desc": "product_list",
					"status": "success"
				},
					"responseList":search_meta}), status.HTTP_200_OK

#----------------------search---------------------#


#----------------------Save-Device-Token---------------------#
@name_space.route("/saveDeviceToken")	
class saveDeviceToken(Resource):
	@api.expect(devicetoken_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		organisation_id = 1
		last_update_id = 1

		device_token_query = ("""SELECT `device_type`,`device_token`
				FROM `devices` WHERE `user_id` = %s and device_type = %s""")
		deviceData = (details['user_id'],details['device_type'])
		count_device_token = cursor.execute(device_token_query,deviceData)

		if count_device_token >0 :
			update_query = ("""UPDATE `devices` SET `device_token` = %s
							WHERE `user_id` = %s and `device_type` = %s""")
			update_data = (details['device_token'],details['user_id'],details['device_type'])
			cursor.execute(update_query,update_data)
		else:
			insert_query = ("""INSERT INTO `devices`(`device_type`,`device_token`,`user_id`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s)""")

			insert_data = (details['device_type'],details['device_token'],details['user_id'],organisation_id,last_update_id)
			cursor.execute(insert_query,insert_data)

		return ({"attributes": {
				    		"status_desc": "device_token_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK

#----------------------Save-Device-Token---------------------#

#----------------------Product-Replication---------------------#
@name_space.route("/productReplication")	
class productReplication(Resource):
	@api.expect(productreplication_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()		

		brand_ids = details.get('brand_id',[])

		from_organisation_id = details['from_organisation_id']
		to_organisation_id = details['to_organisation_id']

		coppy_all_product = details['coppy_all_product']

		if coppy_all_product == 1:
			get_query = ("""SELECT *
					FROM  `product` WHERE `organisation_id` = %s""")
			getData = (from_organisation_id)
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:
				product_data = cursor.fetchall()

				for key,data in enumerate(product_data):
					get_query_product_organisation = ("""SELECT *
							FROM  `product_organisation_mapping` WHERE `organisation_id` = %s and `product_id` = %s""")
					getDataProductOrganisation = (to_organisation_id,data['product_id'])
					count_product_organisation = cursor.execute(get_query_product_organisation,getDataProductOrganisation)

					if count_product_organisation > 0: 
						update_query = ("""UPDATE `product_organisation_mapping` SET `product_id` = %s,`organisation_id` = %s
							WHERE `organisation_id` = %s and `product_id` = %s""")
						update_data = (data['product_id'],to_organisation_id,to_organisation_id,data['product_id'])
						cursor.execute(update_query,update_data)

					else:				
						last_update_id = to_organisation_id
						insert_query = ("""INSERT INTO `product_organisation_mapping`(`product_id`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s)""")
						data = (data['product_id'],to_organisation_id,last_update_id)
						cursor.execute(insert_query,data)

					#print(data['product_id'])	
					#get_brand_query = ("""SELECT *
						#FROM  `product_brand_mapping` WHERE `product_id` = %s and `organisation_id` = %s""")
					#getBrandData = (data['product_id'],from_organisation_id)
					#count_brand_product = cursor.execute(get_brand_query,getBrandData)

					#if count_brand_product > 0:
						#product_brand_data = cursor.fetchone()

						#delete_query = ("""DELETE FROM `product_brand_mapping` WHERE `organisation_id` = %s and `brand_id` = %s """)
						#delData = (to_organisation_id,product_brand_data['brand_id'])
						
						#cursor.execute(delete_query,delData)	

						#last_update_id = to_organisation_id
						#insert_product_brnad_mapping_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`)
							#VALUES(%s,%s,%s,%s,%s)""")
						#product_brand_mapping_status = 1
						#product_brand_insert_data = (product_brand_data['brand_id'],data['product_id'],product_brand_mapping_status,to_organisation_id,last_update_id)
						#cursor.execute(insert_product_brnad_mapping_query,product_brand_insert_data)

		else:

			for keyb,brand_id in enumerate(brand_ids):
				last_update_id = to_organisation_id
				insert_brand_query = ("""INSERT INTO `organisation_brand_mapping`(`brand_id`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s)""")
				brand_data = (brand_id,to_organisation_id,last_update_id)
				cursor.execute(insert_brand_query,brand_data)

				get_query = ("""SELECT *
					FROM  `product_brand_mapping` WHERE `brand_id` = %s and `organisation_id` = %s""")
				getData = (brand_id,from_organisation_id)
				count_product = cursor.execute(get_query,getData)

				if count_product > 0:
					product_data = cursor.fetchall()

					for key,data in enumerate(product_data):
						get_query_product_organisation = ("""SELECT *
							FROM  `product_organisation_mapping` WHERE `organisation_id` = %s and `product_id` = %s""")
						getDataProductOrganisation = (to_organisation_id,data['product_id'])
						count_product_organisation = cursor.execute(get_query_product_organisation,getDataProductOrganisation)

						if count_product_organisation > 0: 
							update_query = ("""UPDATE `product_organisation_mapping` SET `product_id` = %s,`organisation_id` = %s
							WHERE `organisation_id` = %s and `product_id` = %s""")
							update_data = (data['product_id'],to_organisation_id,to_organisation_id,data['product_id'])
							cursor.execute(update_query,update_data)

						else:				
							last_update_id = to_organisation_id
							insert_query = ("""INSERT INTO `product_organisation_mapping`(`product_id`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s)""")
							data = (data['product_id'],to_organisation_id,last_update_id)
							cursor.execute(insert_query,data)

						product_id = data['product_id']						

						get_query_product_brand = ("""SELECT *
							FROM  `product_brand_mapping` WHERE `organisation_id` = %s and `product_id` = %s""")
						getDataProductBrand = (to_organisation_id,product_id)
						count_product_brand = cursor.execute(get_query_product_brand,getDataProductBrand)						

						if count_product_brand > 0: 
							update_query = ("""UPDATE `product_brand_mapping` SET `product_id` = %s,`organisation_id` = %s,`brand_id` = %s
							WHERE `organisation_id` = %s and `product_id` = %s and `brand_id` = %s""")
							update_data = (product_id,to_organisation_id,brand_id,to_organisation_id,data['product_id'],brand_id)
							cursor.execute(update_query,update_data)

						else:				
							insert_product_brand_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s)""")
							insert_product_brand_data = (brand_id,product_id,1,to_organisation_id,to_organisation_id)
							cursor.execute(insert_product_brand_query,insert_product_brand_data)

						#delete_query = ("""DELETE FROM `product_brand_mapping` WHERE `organisation_id` = %s and `brand_id` = %s """)
						#delData = (to_organisation_id,brand_id)
						
						#cursor.execute(delete_query,delData)	

						#last_update_id = to_organisation_id
						#insert_product_brnad_mapping_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`)
							#VALUES(%s,%s,%s,%s,%s)""")
						#product_brand_mapping_status = 1
						#productbrand_data = (brand_id,data['product_id'],product_brand_mapping_status,to_organisation_id,last_update_id)
						#cursor.execute(insert_product_brnad_mapping_query,productbrand_data)
						#print(cursor._last_executed)

		connection.commit()
		cursor.close()				

		return ({"attributes": {
				    		"status_desc": "Product Replication",
				    		"status": "success"
				},
				"responseList":details}), status.HTTP_200_OK


#----------------------Send-Push-Notification---------------------#

@name_space.route("/sendAppPushNotifications")
class sendAppPushNotifications(Resource):
	@api.expect(appmsg_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		data_message = {
							"title" : "Order",
							"message": "Order Placed Successfully"
						}
		api_key = details.get('firebase_key')
		device_id = details.get('device_id')
		push_service = FCMNotification(api_key=api_key)
		msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = data_message)
		sent = 'N'
		if msgResponse.get('success') == 1:
			sent = 'Y'
		
		
		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				    	"responseList":msgResponse}), status.HTTP_200_OK
#----------------------Send-Push-Notification---------------------#

#----------------------Send-Push-Notification---------------------#

@name_space.route("/sendAppPushNotificationforloyalityPoint")
class sendAppPushNotificationforloyalityPoint(Resource):
	@api.expect(appmsg_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		data_message = {
							"title" : "loyality Point",
							"message": "New Point Added"
						}
		api_key = details.get('firebase_key')
		device_id = details.get('device_id')
		push_service = FCMNotification(api_key=api_key)
		msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = data_message)
		sent = 'N'
		if msgResponse.get('success') == 1:
			sent = 'Y'
		
		
		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				    	"responseList":msgResponse}), status.HTTP_200_OK
#----------------------Send-Push-Notification---------------------#

#----------------------Send-Email---------------------#
@name_space.route("/send_email_test")
class send_email_test(Resource):
	@api.expect(send_email_model)
	def post(self):

		details = request.get_json()
		res = 'Failure. Wrong MailId or SourceApp.'

		msg = MIMEMultipart()
		msg['Subject'] = details['Subject']
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = details['To']

		html = "hello"
		part1 = MIMEText(html, 'html')
		print(part1)
		msg.attach(part1)

		try:
			smtp = SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, details['To'], msg.as_string())

			res = {"status":'Success'}
			sent = 'Y'

		except Exception as e:
			res = {"status":'Failure'}
			sent = 'N'
		smtp.quit()	

		phone_no = 9674419482

		send_sms(phone_no)

		return ({"attributes": {
				    		"status_desc": "Send Email",
				    		"status": "success"
				    	},
				    	"responseList":res}), status.HTTP_200_OK
#----------------------Send-Email---------------------#

def invoice(data):
	customer_information = {}
	logo = "https://d1o7xhcyswcoe3.cloudfront.net/28/Am_Mobile_logo_crop_NEW.png"
	customer_information['customer_name'] = data['customer_data']['first_name']+''+data['customer_data']['last_name']
	customer_information['customer_address'] = data['customer_data']['address_line_1']+','+data['customer_data']['address_line_2']+','+data['customer_data']['city']+','+data['customer_data']['state']+','+data['customer_data']['country']
	customer_information['coupon_code'] = data['order_data']['coupon_code']	
	customer_information['customer_email'] = data['customer_data']['email']
	customer_information['date'] = data['order_data']['last_update_ts']
	customer_information['order_data'] = data['order_data']
	customer_information['logo'] = logo
	template = env.get_template('index.html')
	output = template.render(customer_information)
	print(output)
	sent_email_status = send_mail(output, data['customer_data']['email'])
	return sent_email_status

#----------------------Exchange-Device-Question---------------------#

@name_space.route("/getExchangeDeviceQuestion/<int:organisation_id>/<int:question_type>")	
class getExchangeDeviceQuestion(Resource):
	def get(self,organisation_id,question_type):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `exchange_device_question` WHERE `organisation_id` = %s and `question_type` = %s""")

		get_data = (organisation_id,question_type)
		cursor.execute(get_query,get_data)

		exchange_device_question_data = cursor.fetchall()

		for key,data in enumerate(exchange_device_question_data):
			get_ans_query = ("""SELECT `question_ans_id`,`ans`,`ans_image`
			FROM `exchange_device_question_ans` WHERE `question_id` = %s """)

			get_ans_data = (data['question_id'])
			cursor.execute(get_ans_query,get_ans_data)

			exchange_device_question_ans_data = cursor.fetchall()

			exchange_device_question_data[key]['ans'] = exchange_device_question_ans_data

			exchange_device_question_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "exchange_device_question_details",
		    		"status": "success"
		    	},
		    	"responseList":exchange_device_question_data}), status.HTTP_200_OK

#----------------------Exchange-Device-Question---------------------#


#----------------------Customer-Exchange-Device-Ans---------------------#
@name_space.route("/customerExchangeDeviceAns")
class customerExchangeDeviceAns(Resource):
	@api.expect(customer_exchange_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		customer_id = details['customer_id']
		amount = details['amount']
		organisation_id = 1
		last_update_id = 1

		insert_query = ("""INSERT INTO `customer_exchange_device`(`customer_id`,`front_image`,`back_image`,`organisation_id`,`last_update_id`) 
			VALUES(%s,%s,%s,%s,%s)""")

		data = (customer_id,front_image,back_image,organisation_id,last_update_id)
		cursor.execute(insert_query,data)

		exchange_id = cursor.lastrowid

		question_ans_ids = details.get('question_ans_id',[])

		for question_ans_id in question_ans_ids: 
			customer_exchange_device_insert_query = ("""INSERT INTO `customer_exchange_device_ans`(`customer_id`,`exchange_id`,`question_ans_id`,`organisation_id`,`last_update_id`) 
			VALUES(%s,%s,%s,%s,%s)""")

			data_customer_exchange_device = (customer_id,exchange_id,question_ans_id,organisation_id,last_update_id)
			cursor.execute(customer_exchange_device_insert_query,data_customer_exchange_device)

		return ({"attributes": {
				    		"status_desc": "customer_exchange_device_ans",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK

#----------------------Customer-Exchange-Device-Ans---------------------#

#----------------------Customer-Exchange---------------------#

@name_space.route("/getCustomerExchange/<int:organisation_id>/<int:user_id>")	
class getCustomerExchange(Resource):
	def get(self,organisation_id,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `customer_exchange_device` WHERE `organisation_id` = %s and `customer_id` = %s""")

		get_data = (organisation_id,user_id)
		cursor.execute(get_query,get_data)

		customer_exchange_data = cursor.fetchall()

		for key,data in enumerate(customer_exchange_data):
			customer_exchange_data[key]['exchange_id'] = "AMEXCHANGE-"+str(data['exchange_id'])
			customer_exchange_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "customer_exchange_data",
		    		"status": "success"
		    	},
		    	"responseList":customer_exchange_data}), status.HTTP_200_OK

#----------------------Customer-Exchange---------------------#

#----------------------Enquiry-Type-List---------------------#

@name_space.route("/getEnquiryTypeList/<int:organisation_id>")	
class getEnquiryTypeList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `enquiry_type_master` WHERE `organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		enquiry_type_data = cursor.fetchall()	

		for key,data in enumerate(enquiry_type_data):
			enquiry_type_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "enquiry_type_details",
		    		"status": "success"
		    	},
		    	"responseList":enquiry_type_data}), status.HTTP_200_OK

#----------------------Enquiry-Type-List---------------------#

#----------------------Create-Enquiery---------------------#

@name_space.route("/createEnquiry")
class createEnquiry(Resource):
	@api.expect(enquiry_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		enquiry_type_id = details['enquiry_type_id']
		user_id = details['user_id']
		organisation_id = 1
		enquirystatus = 1
		last_update_id = 1

		insert_query = ("""INSERT INTO `enquiry_master`(`enquiry_type_id`,`user_id`,`organisation_id`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")

		data = (enquiry_type_id,user_id,organisation_id,enquirystatus,last_update_id)
		cursor.execute(insert_query,data)
		details['enquiry_id'] = cursor.lastrowid

		text = "Welcome! I'm chat assistant. You can start a new chat."
		image = ""
		role = 1

		insert_communication_query = ("""INSERT INTO `enquiry_communication`(`enquiry_id`,`user_id`,`text`,`image`,`role`,`organisation_id`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		communicatio_data = (details['enquiry_id'],user_id,text,image,role,organisation_id,enquirystatus,last_update_id)
		cursor.execute(insert_communication_query,communicatio_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "enquiry_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Create-Enquiery---------------------#

#-----------------------Get-Enquiry-List----------------------#

@name_space.route("/getEnquiryList/<int:organisation_id>/<int:user_id>")	
class getEnquiryList(Resource):
	def get(self,organisation_id,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT em.`enquiry_id`,etm.`enquiry_type`,em.`last_update_ts`
			FROM `enquiry_master` em
			INNER JOIN `enquiry_type_master` etm ON etm.`enquiry_type_id` = em.`enquiry_type_id`
			WHERE em.`organisation_id` = %s and em.`user_id` = %s ORDER BY em.`enquiry_id` DESC""")

		get_data = (organisation_id,user_id)
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


#----------------------Create-Enquiery-Communication---------------------#

@name_space.route("/createEnquiryCommunication")
class createEnquiryCommunication(Resource):
	@api.expect(enquiry_communication_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		enquiry_id = details['enquiry_id']
		user_id = details['user_id']
		image = details['image']
		text = details['text']
		role = 2
		organisation_id = 1
		communication_status = 1
		organisation_id = 1		
		last_update_id = 1

		insert_query = ("""INSERT INTO `enquiry_communication`(`enquiry_id`,`user_id`,`text`,`image`,`role`,`organisation_id`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (enquiry_id,user_id,text,image,role,organisation_id,communication_status,last_update_id)
		cursor.execute(insert_query,data)
		details['enquiry_communication'] = cursor.lastrowid

		get_query = ("""SELECT em.`enquiry_id`,em.`user_id`,etm.`enquiry_type`,em.`last_update_ts`,a.`first_name`,a.`last_name`
			FROM `enquiry_master` em
			INNER JOIN `enquiry_type_master` etm ON etm.`enquiry_type_id` = em.`enquiry_type_id`
			INNER JOIN `admins` a ON a.`admin_id` = em.`user_id`
			WHERE em.`organisation_id` = %s and em.`enquiry_id` = %s""")

		get_data = (organisation_id,enquiry_id)
		cursor.execute(get_query,get_data)
		enquiry_data = cursor.fetchone()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		Url = BASE_URL + "ecommerce_customer/EcommerceCustomer/postCommunication"
		payload = {
  					"sourceapp": "enquiery",
  					"mailParams": {"enquiery_name":enquiry_data['enquiry_type'],"user":enquiry_data['first_name']+" "+enquiry_data['last_name']}
				  }
		sent_enquery_email = requests.post(Url,data=json.dumps(payload), headers=headers).json()

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "enquiry_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Create-Enquiery-Communication---------------------#

@name_space.route("/postCommunication")
class postCommunication(Resource):
	@api.expect(communication_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()	

		details = request.get_json()

		sourceapp = details['sourceapp']
		mailParams = details['mailParams']
		body_text = ''
		FIRST_NAME = "sourav"

		cursor.execute("""SELECT `application_name`,`title`,`Recipient`,`email`,`Email_Body`,`Subject`,`sms`,
			`SMS_Body`,`App_Description`,`from_mailid`,`from_number`,`Dashboard_Id`,`email`,`sms` 
			FROM `configuration` WHERE `application_name` = %s""",(sourceapp))


		config_info = cursor.fetchone()

		mail_body = config_info['Email_Body']

		for k,v in mailParams.items():
			body_text = mail_body.replace('{{'+k+'}}',v)

		body_text = body_text.format(user = FIRST_NAME)		
		config_info['Email_Body'] = body_text

		organisation_id = 1

		cursor.execute("""SELECT `email` as `EMAIL_ID`
			FROM `organisation_master` WHERE `organisation_id` = %s""",(organisation_id))
		user_info = cursor.fetchone()

		#user_info['EMAIL_ID'] = "sutandra.mazumder@gmail.com"
		if config_info['email'] == 1:
				mail_res = send_email(config_info = config_info, user_info = user_info)	

		cursor.close()
		return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":{"mail_res":mail_res}}), status.HTTP_200_OK			

#-----------------------Get-Communication-List----------------------#

@name_space.route("/getCommunicationList/<int:organisation_id>/<int:user_id>/<int:enquiry_id>")	
class getEnquiryList(Resource):
	def get(self,organisation_id,user_id,enquiry_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_user_query = ("""SELECT `first_name`,`last_name`,`profile_image`
			FROM `admins`
			WHERE  `admin_id` = %s""")
		get_user_data = (user_id)
		cursor.execute(get_user_query,get_user_data)
		user_data = cursor.fetchone()

		get_query = ("""SELECT *
			FROM `enquiry_communication`
			WHERE `organisation_id` = %s and `user_id` = %s and enquiry_id =%s""")

		get_data = (organisation_id,user_id,enquiry_id)
		cursor.execute(get_query,get_data)

		communication_data = cursor.fetchall()			

		for key,data in enumerate(communication_data):
			communication_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "communication_details",
		    		"status": "success"
		    	},
		    	"responseList":communication_data,"user":user_data}), status.HTTP_200_OK

#-----------------------Get-Communication-List----------------------#

#----------------------Budet-List---------------------#

@name_space.route("/getBudgetList/<int:organisation_id>/<int:category_id>")	
class getMetaKeyList(Resource):
	def get(self,organisation_id,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `budget` WHERE  `organisation_id` = %s and `category_id` = %s""")

		get_data = (organisation_id,category_id)
		cursor.execute(get_query,get_data)

		meta_key_data = cursor.fetchall()

		for key,data in enumerate(meta_key_data):
			meta_key_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "budget_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_key_data}), status.HTTP_200_OK

#----------------------Budet-List---------------------#

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
										 WHERE  `meta_key` LIKE %s and `organisation_id` = %s """)
				getmetadata = (meta_key,organisation_id)
				count_meta_data = cursor.execute(get_meta_query,getmetadata)
					
				search_meta = cursor.fetchone()
				get_meta_value_query = ("""SELECT `meta_key_value_id` FROM `meta_key_value_master` WHERE `meta_key_id` = %s
							 and `organisation_id` = 1 and `status` = 1 and `meta_key_value` = %s""")
				getdata_meta_data = (search_meta['meta_key_id'],storage_value)
				cursor.execute(get_meta_value_query,getdata_meta_data)

				meta_value_data = cursor.fetchone()

				meta_key_text.append(str(meta_value_data['meta_key_value_id']))				


			if meta_key == "Color" and color_value != "na":
				get_meta_query = ("""SELECT `meta_key_id`,`meta_key` FROM `meta_key_master`
										 WHERE  `meta_key` LIKE %s and `organisation_id` = %s """)
				getmetadata = (meta_key,organisation_id)
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
										 WHERE  `meta_key` LIKE %s and `organisation_id` = %s """)
				getmetadata = (meta_key,organisation_id)
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

def send_mail(bodyContent,toemail):
    to_email = toemail
    print(to_email)
    from_email = 'communications@creamsonservices.com'
    subject = 'Oder Details'
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = from_email
    message['To'] = to_email

    message.attach(MIMEText(bodyContent, "html"))
    msgBody = message.as_string()

    server = SMTP('mail.creamsonservices.com', 587)
    server.starttls()
    server.login(from_email, 'CReam7789%$intELLi')
    server.sendmail(from_email, to_email, msgBody)

    server.quit()

    res = {"status":'Success'}
    return res

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
		