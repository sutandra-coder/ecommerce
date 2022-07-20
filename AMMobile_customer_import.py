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

AMMobile_customer_import = Blueprint('AMMobile_customer_import_api', __name__)
api = Api(AMMobile_customer_import,  title='AM Mobile Product',description='AM Mobile Customer Import API')
name_space = api.namespace('AMMobileCustomerImport',description='AM Mobile Customer Import')

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

def am_product_mysql_connection():
	connection = pymysql.connect(host='ammobileproduct.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='EKr3RnhsAssFw78a91N5',
	                             db='AMMobileProduct',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection
#----------------------database-connection---------------------#

customer_postmodel = api.model('customer_postmodel', {
	"first_name":fields.String,	
	"email":fields.String,	
	"phoneno":fields.String(required=True),		
	"stock_location":fields.String(required=True),	
	"organisation_id":fields.Integer(required=True)
})

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'
Local_base_url = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/AMMobile_customer_import/'

#----------------------Add-Customer-With-Retail-Store-Id--------------------#

@name_space.route("/AddCustomer")
class AddCustomer(Resource):
	@api.expect(customer_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()			
		details = request.get_json()	

		first_name = details['first_name']		
		last_name = ''
		email = details['email']		
		details['phoneno'] = str(details['phoneno']).replace('0.', '')
		details['phoneno'] = str(details['phoneno']).replace('.', '')
		password = details['phoneno']
		phoneno = details['phoneno']
		emergency_contact = phoneno
		dob = ''
		anniversary = ''
		address_line_1 = ''
		address_line_2 = ''
		
		county = 'India'
		state = 'West Brengal'
		pincode = 0		
		role_id = 4
		admin_status = 1
		organisation_id = details['organisation_id']
		registration_type = 5
		stock_location = details['stock_location']

		if stock_location == 'CITYNPP':
			store_name = 'City Center'
		if stock_location == 'SILIGURI':
			store_name = 'Siliguri'		
		if stock_location == 'HILAND PARK':
			store_name = 'Hiland Park'
		if stock_location == 'DURGAPUR':
			store_name = 'Durgapur'

		get_query_retail_store = ("""SELECT *
					FROM `retailer_store_stores` WHERE `store_name` = %s and organisation_id = %s""")
		getDataRetailStore = (store_name,organisation_id)
		count_Retail_Store = cursor.execute(get_query_retail_store,getDataRetailStore)

		retail_store = cursor.fetchone()

		get_query_city = ("""SELECT *
					FROM `retailer_store` WHERE `retailer_store_id` = %s and organisation_id = %s""")
		getDataCity = (retail_store['retailer_store_id'],organisation_id)
		count_city = cursor.execute(get_query_city,getDataCity)

		city_data = cursor.fetchone()


		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		get_phone_type_query = ("""SELECT *
				FROM `admins` WHERE `phoneno` = %s and `organisation_id` = %s and `registration_type` = %s""")
		get_phone_type_data = (phoneno,organisation_id,registration_type)

		count_phone_type = cursor.execute(get_phone_type_query,get_phone_type_data)

		if count_phone_type > 0:
			date_of_lastlogin = date_of_creation
			loggedin_status = 1

			get_query_login_data = ("""SELECT a.`admin_id` as `user_id`,a.`first_name`,a.`last_name`,a.`email`,a.`org_password`,
						a.`phoneno`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
						a.`pincode`,a.`emergency_contact`,a.`role_id`,a.`wallet`,a.`registration_type`,cr.`referral_code`,
						rs.`retailer_name`,rss.`phoneno` as retailer_phoneno,rss.`address` as retailer_address,rss.`retailer_store_store_id`,rs.`city` as reatiler_city					
						FROM `admins` a
						INNER JOIN `customer_referral` cr ON cr.`customer_id` = a.`admin_id`
						INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
						INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
						INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
						WHERE a.`phoneno` = %s and a.`registration_type` = %s and a.`organisation_id` = %s and rss.`organisation_id` = %s""")
			getDataLogin = (phoneno,registration_type,organisation_id,organisation_id)
			cursor.execute(get_query_login_data,getDataLogin)
			login_data = cursor.fetchone()

			user_id = login_data['user_id']

			get_customer_wallet_transaction_query = ("""SELECT * from `wallet_transaction` where `customer_id` = %s and `transaction_source` = 'signup' ORDER BY `wallet_transaction_id` desc""")
			get_customer_wallet_transaction_data = (user_id)
			customer_wallet_transaction_count = cursor.execute(get_customer_wallet_transaction_query,get_customer_wallet_transaction_data)

			if customer_wallet_transaction_count > 0:
				print('hii')
			else:
				get_general_loyality_query = ("""SELECT `signup_point`
									FROM `general_loyalty_master` WHERE `organisation_id` = %s""")
				getGeneralLoyalityData = (organisation_id)
				count_general_loyality = cursor.execute(get_general_loyality_query,getGeneralLoyalityData)
				general_loyality =  cursor.fetchone()

				get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s""")
				customer_wallet_data = (user_id)
				cursor.execute(get_customer_wallet_query,customer_wallet_data)
				wallet_data = cursor.fetchone()


				wallet = int(general_loyality['signup_point'])+wallet_data['wallet']
				transaction_id = 0
				redeem_history_id = 0

				insert_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
											`updated_value`,`transaction_id`,`redeem_history_id`,`organisation_id`,`status`,`last_update_id`)
														VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				transaction_source = "signup"
				updated_value = wallet
				previous_value = wallet_data['wallet']
				wallet_transation_status = 1
				wallet_transaction_data = (user_id,general_loyality['signup_point'],transaction_source,previous_value,updated_value,transaction_id,redeem_history_id,organisation_id,wallet_transation_status,organisation_id)
				cursor.execute(insert_wallet_transaction_query,wallet_transaction_data)

				update_customer_wallet_transaction_query = ("""UPDATE `admins` SET `wallet` = %s
										WHERE `admin_id` = %s""")
				update_customer_wallet_data = (wallet,user_id)
				cursor.execute(update_customer_wallet_transaction_query,update_customer_wallet_data)

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

			login_data['is_referal'] = is_referal

			connection.commit()
			
		else:
			insert_query = ("""INSERT INTO `admins`(`first_name`,`last_name`,`email`,`org_password`,
										`phoneno`,`address_line_1`,`address_line_2`,`city`,`country`,
										`state`,`pincode`,`emergency_contact`,`role_id`,`registration_type`,`status`,`organisation_id`,`date_of_creation`) 
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			data = (first_name,last_name,email,password,phoneno,address_line_1,address_line_2,city_data['city'],county,state,pincode,emergency_contact,role_id,registration_type,admin_status,organisation_id,date_of_creation)
			cursor.execute(insert_query,data)

			admin_id = cursor.lastrowid				
								

			get_query_city = ("""SELECT *
					FROM `retailer_store` WHERE `city` = %s and organisation_id = %s""")
			getDataCity = (city_data['city'],organisation_id)
			count_city = cursor.execute(get_query_city,getDataCity)

			if count_city > 0:
				city_data = cursor.fetchone()

				get_query_retailer_store = ("""SELECT *
						FROM `retailer_store_stores` WHERE `retailer_store_id` = %s and `organisation_id` = %s and `store_name` = %s""")
				getDataRetailerStore = (city_data['retailer_store_id'],organisation_id,store_name)
				count_retailer_store = cursor.execute(get_query_retailer_store,getDataRetailerStore)
				retailer_store_data = cursor.fetchone()

				insert_mapping_user_retailer = ("""INSERT INTO `user_retailer_mapping`(`user_id`,`retailer_id`,`retailer_store_id`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")
							#organisation_id = 1
				last_update_id = organisation_id
				city_insert_data = (admin_id,city_data['retailer_store_id'],retailer_store_data['retailer_store_store_id'],admin_status,organisation_id,last_update_id)	
				cursor.execute(insert_mapping_user_retailer,city_insert_data)

			insert_customer_referal_code_query = ("""INSERT INTO `customer_referral`(`customer_id`,`referral_code`,`organisation_id`,`status`,`last_update_id`)
						VALUES(%s,%s,%s,%s,%s)""")
				#organisation_id = 1
			last_update_id = 1	

			customer_referral_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

			referal_data = (admin_id,customer_referral_code,organisation_id,admin_status,last_update_id)
			cursor.execute(insert_customer_referal_code_query,referal_data)

			get_loyality_settings_query = ("""SELECT `setting_value`
					FROM `referal_loyality_settings` WHERE `organisation_id` = %s""")
			getLoyalitySettingsData = (organisation_id)
			count_loyality_settings = cursor.execute(get_loyality_settings_query,getLoyalitySettingsData)

			if count_loyality_settings >0:
				loyality_settings = cursor.fetchone()

				if loyality_settings['setting_value'] == 1:

					get_general_loyality_query = ("""SELECT `signup_point`
								FROM `general_loyalty_master` WHERE `organisation_id` = %s""")
					getGeneralLoyalityData = (organisation_id)
					count_general_loyality = cursor.execute(get_general_loyality_query,getGeneralLoyalityData)

					if count_general_loyality > 0:
						general_loyality =  cursor.fetchone()

						if int(general_loyality['signup_point']) > 0:

							get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s""")
							customer_wallet_data = (admin_id)
							cursor.execute(get_customer_wallet_query,customer_wallet_data)
							wallet_data = cursor.fetchone()
							wallet = int(general_loyality['signup_point'])+wallet_data['wallet']
							transaction_id = 0
							redeem_history_id = 0

							insert_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
										`updated_value`,`transaction_id`,`redeem_history_id`,`organisation_id`,`status`,`last_update_id`)
													VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
							transaction_source = "signup"
							updated_value = wallet
							previous_value = wallet_data['wallet']
							wallet_transation_status = 1
							wallet_transaction_data = (admin_id,general_loyality['signup_point'],transaction_source,previous_value,updated_value,transaction_id,redeem_history_id,organisation_id,wallet_transation_status,organisation_id)
							cursor.execute(insert_wallet_transaction_query,wallet_transaction_data)

							update_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s
																		WHERE `admin_id` = %s """)
							update_data = (wallet,admin_id)
							cursor.execute(update_customer_wallet_query,update_data)

							get_device_query = ("""SELECT `device_token`
										FROM `devices` WHERE  `user_id` = %s and `organisation_id` = %s""")

							get_device_data = (admin_id,organisation_id)
							device_token_count = cursor.execute(get_device_query,get_device_data)

							if device_token_count > 0:
								device_token_data = cursor.fetchone()

								get_organisation_firebase_query = ("""SELECT `firebase_key`
											FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
								get_organisation_firebase_data = (organisation_id)
								cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
								firebase_data = cursor.fetchone()

								headers = {'Content-type':'application/json', 'Accept':'application/json'}
								sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer_new/EcommerceCustomerNew/sendAppPushNotificationforloyalityPoint"
								payloadpushData = {
									"device_id":device_token_data['device_token'],
									"firebase_key": firebase_data['firebase_key']
								}

								send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()
		
						
			get_query_login_data = ("""SELECT a.`admin_id` as `user_id`,a.`first_name`,a.`last_name`,a.`email`,a.`org_password`,
				a.`phoneno`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
					a.`pincode`,a.`emergency_contact`,a.`role_id`,a.`wallet`,a.`registration_type`,cr.`referral_code`,rs.`retailer_name`,
					rss.`phoneno` as retailer_phoneno,rss.`address` as retailer_address,rss.`retailer_store_store_id`,rs.`city` as reatiler_city				
					FROM `admins` a
					INNER JOIN `customer_referral` cr ON cr.`customer_id` = a.`admin_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
					INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
					WHERE a.`admin_id` = %s """)
			getDataLogin = (admin_id)
			cursor.execute(get_query_login_data,getDataLogin)
			login_data = cursor.fetchone()

			date_of_lastlogin = date_of_creation
			loggedin_status = 1

			update_query = ("""UPDATE `admins` SET `loggedin_status` = %s, `date_of_lastlogin` = %s
							WHERE `phoneno` = %s and `organisation_id` = %s""")
			update_data = (loggedin_status,date_of_lastlogin,phoneno,organisation_id)
			cursor.execute(update_query,update_data)

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

			login_data['is_referal'] = is_referal

			user_id = admin_id
			organisation_id = organisation_id	

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			LoyalityReferalnUrl = BASE_URL + "ecommerce_customer_new/EcommerceCustomerNew/AddLoyalityReferalCustomer"
			loyalityReferalData = {
							"customer_id":admin_id,						
							"organisation_id": organisation_id
			}

			loyalityReferalResponse = requests.post(LoyalityReferalnUrl,data=json.dumps(loyalityReferalData), headers=headers).json()	

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_details",
				    "status": "success"
				},
				"responseList":login_data}), status.HTTP_200_OK

#----------------------Add-Customer-With-Retail-Store-Id--------------------#


#-----------------------get-Excel-Sheet-Data---------------------#

@name_space.route("/getXcelsheetData/<int:organisation_id>/<int:request_no>")	
class getXcelsheetData(Resource):
	def get(self,organisation_id,request_no):
		connection = am_product_mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `customer_transaction_table_id`,posting_account,mobile,stock_location,rate,qty,ecommerce_product_meta_id
			FROM `customer_transaction` where `request_no` = %s and `status` = 'processing'""")
		get_data = (request_no)
		cursor.execute(get_query,get_data)

		customer_transaction_data = cursor.fetchall()
		for key,data in enumerate(customer_transaction_data):
			if len(data['mobile']) > 9 :
				if ".." in data['mobile']:
					print('hii')
				else:
					phone = str(data['mobile']).replace('0.', '')
					phone = str(phone).replace('.', '')					

					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					customerUrl = Local_base_url + "AMMobileCustomerImport/AddCustomer"
					print(customerUrl)
					AddCustomerData = {
									"first_name":data['posting_account'],	
									"email":"",
									"phoneno": str(data['mobile']).replace('0.', ''),	
									"stock_location":data['stock_location'],											
									"organisation_id": organisation_id
					}

					print(AddCustomerData)

					customerResponse = requests.post(customerUrl,data=json.dumps(AddCustomerData), headers=headers).json()

					user_id = customerResponse['responseList']['user_id']
					print(user_id)

					if user_id:
						transaction_data = {}
						transaction_data['user_id'] = user_id
						transaction_data['amount'] = int(float(data['rate']))
						transaction_data['product_meta_id'] = data['ecommerce_product_meta_id']
						transaction_data['coupon_code'] = ''
						transaction_data['qty'] = int(float(data['qty']))
						transaction_data['organisation_id'] = organisation_id
						transaction_data['order_payment_status'] = 2
						transaction_data['delivery_option'] = 1
						transaction_data['delivery_charges'] = 'Free'

						print(transaction_data)

						headers = {'Content-type':'application/json', 'Accept':'application/json'}
						transactionUrl = BASE_URL + "ecommerce_customer_new/EcommerceCustomerNew/cashonwithqty"

						transaction_response = requests.post(transactionUrl,data=json.dumps(transaction_data), headers=headers).json()

						print(transaction_response['responseList'])


						update_query = ("""UPDATE `customer_transaction` SET `status` = 'done'
							WHERE `customer_transaction_table_id` = %s""")
						update_data = (data['customer_transaction_table_id'])
						cursor.execute(update_query,update_data)

						connection.commit()
		cursor.close()


		return ({"attributes": {
				    "status_desc": "customer_transaction_data",
				    "status": "success"
				},
				"responseList":customer_transaction_data}), status.HTTP_200_OK

#-----------------------get-Excel-Sheet-Data---------------------#




