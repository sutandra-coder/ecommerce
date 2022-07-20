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
import re

app = Flask(__name__)
cors = CORS(app)

ecommerce_transaction = Blueprint('ecommerce_transation_api', __name__)
api = Api(ecommerce_transaction,  title='Ecommerce Transation API',description='Ecommerce Transation API')
name_space = api.namespace('EcommerceTransaction',description='Ecommerce Transation')

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

def ecommerce_analytics():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce_analytics',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

app.config['CORS_HEADERS'] = 'Content-Type'

save_transaction_model = api.model('save_transaction_model', {
	"product_name":fields.String(required=True),	
	"phoneno":fields.String(required=True),
	"city":fields.String(required=True),
	"retailer_store":fields.String(required=True),
	"storage":fields.String(required=True),
	"ram":fields.String(required=True),
	"color":fields.String(required=True),
	"qty":fields.Integer(required=True),
	"amount":fields.Integer(required=True),
	"coupon_code":fields.String,
	"order_payment_status":fields.Integer,
	"delivery_option":fields.Integer,
	"delivery_charges":fields.String
})

upload_transaction_model = api.model('upload_transaction_model', {
	"customer_name":fields.String(required=True),
	"product_name":fields.String(required=True),
	"color":fields.String(required=True)
})


BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#----------------------Save-Transaction---------------------#

@name_space.route("/saveTransaction/<string:api_key>")
class saveTransaction(Resource):
	@api.expect(save_transaction_model)
	def post(self,api_key):

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		api_key = api_key

		amount = details['amount']
		coupon_code = details['coupon_code']
		order_payment_status =  details['order_payment_status']
		delivery_option =  details['delivery_option']
		delivery_charges =  details['delivery_charges']
		purpose = "Buy"

		organisation_id = 93

		if api_key == "lkq1234sfcgrgdg":
			product_name = details['product_name']
			storage = details['storage']
			ram = details['ram']
			color = details['color']

			get_product_name_query = ("""SELECT *
			FROM `product` where `product_name` = %s""")
			get_product_name_data = (product_name)
			product_count = cursor.execute(get_product_name_query,get_product_name_data)

			if product_count > 0:
				product_data = cursor.fetchone()
				get_storage_query = ("""SELECT *
					FROM `meta_key_value_master` where `meta_key_value` = %s and `organisation_id` = 1 and `meta_key_id` = 3""")
				get_storage_data = (details['storage'])
				storage_count = cursor.execute(get_storage_query,get_storage_data)				

				if storage_count > 0 :
					storange_data = cursor.fetchone()
				else:
					storange_data = {}

				get_ram_query = ("""SELECT *
					FROM `meta_key_value_master` where `meta_key_value` = %s and `organisation_id` = 1 and `meta_key_id` = 4""")
				get_ram_data = (details['ram'])
				ram_count = cursor.execute(get_ram_query,get_ram_data)

				if 	ram_count > 0:
					ram_data = cursor.fetchone()
				else:
					ram_data = {}

				get_color_query = ("""SELECT *
					FROM `meta_key_value_master` where `meta_key_value` = %s and `organisation_id` = 1 and `meta_key_id` = 5""")
				get_color_data = (details['color'])
				color_count = cursor.execute(get_color_query,get_color_data)

				if 	color_count > 0:
					color_data = cursor.fetchone()
				else:
					color_data = {}

				if storange_data == {} and ram_data == {} and color_data == {}:
				
					return ({"attributes": {
				    		"status_desc": "payment_details",
				    		"status": "error",
				    		"message":"Wrong storage or Ram or color Selected"
				    	},
				    	"responseList":{} }), status.HTTP_200_OK
				else:

					product_id = product_data['product_id']

					if ram_data == {}:
						meta_key_text_tupple = (str(storange_data['meta_key_value_id']), str(color_data['meta_key_value_id']))

						meta_key_text = ",".join(meta_key_text_tupple)

						print(meta_key_text)

					elif storange_data == {}:
						meta_key_text_tupple = (str(color_data['meta_key_value_id']), str(ram_data['meta_key_value_id']))

						meta_key_text = ",".join(meta_key_text_tupple)

						print(meta_key_text)

					elif color_data == {}:
						meta_key_text_tupple = (str(storange_data['meta_key_value_id']), str(color_data['meta_key_value_id']))

						meta_key_text = ",".join(meta_key_text_tupple)

						print(meta_key_text)

					else:

						meta_key_text_tupple = (str(storange_data['meta_key_value_id']), str(color_data['meta_key_value_id']),str(ram_data['meta_key_value_id']))

						meta_key_text = ",".join(meta_key_text_tupple)

						print(meta_key_text)

					get_product_meta_query = ("""SELECT * FROM 	`product_meta` where `product_id` = %s and `meta_key_text` = %s""")
					get_product_meta_data = (product_id,meta_key_text)
					product_meta_data_count = cursor.execute(get_product_meta_query,get_product_meta_data)

					if product_meta_data_count > 0:
						product_meta_data = cursor.fetchone()	

						product_meta_id = product_meta_data['product_meta_id']

						get_user_data_query = ("""SELECT * FROM `admins` where `phoneno` = %s and `organisation_id` = %s""")
						get_user_data = (details['phoneno'],organisation_id)
						user_data_count =  cursor.execute(get_user_data_query,get_user_data)
						print(cursor._last_executed)

						if user_data_count > 0:
							print('hiii')
							user_data = cursor.fetchone()

							user_id = user_data['admin_id']

						else:
							print('hello')
							first_name = ""
							email = ""
							password = details['phoneno']
							phoneno = details['phoneno']
							dob = ""
							anniversary = ""
							address_line_1 = ""
							address_line_2 = ""
							city = details['city']
							county = ""
							state = ""
							pincode = 0
							role_id = 4
							registration_type = 5
							admin_status = 1

							retailer_store = details['retailer_store']

							now = datetime.now()
							date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

							insert_query = ("""INSERT INTO `admins`(`first_name`,`email`,`org_password`,
												`phoneno`,`dob`,`anniversary`,`address_line_1`,`address_line_2`,`city`,`country`,
												`state`,`pincode`,`role_id`,`registration_type`,`status`,`organisation_id`,`date_of_creation`) 
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
							data = (first_name,email,password,phoneno,dob,anniversary,address_line_1,address_line_2,city,county,state,pincode,role_id,registration_type,admin_status,organisation_id,date_of_creation)
							cursor.execute(insert_query,data)

							print(cursor._last_executed)

							admin_id = cursor.lastrowid	

							print(admin_id)

							details['user_id'] = admin_id

							user_id = admin_id
							organisation_id = organisation_id

							insert_customer_referal_code_query = ("""INSERT INTO `customer_referral`(`customer_id`,`referral_code`,`organisation_id`,`status`,`last_update_id`)
								VALUES(%s,%s,%s,%s,%s)""")
						
							last_update_id = organisation_id	

							customer_referral_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

							referal_data = (admin_id,customer_referral_code,organisation_id,admin_status,last_update_id)
							cursor.execute(insert_customer_referal_code_query,referal_data)

							get_query_city = ("""SELECT *
								FROM `retailer_store` WHERE `city` = %s and organisation_id = %s""")
							getDataCity = (details['city'],organisation_id)
							count_city = cursor.execute(get_query_city,getDataCity)

							if count_city > 0:
								city_data = cursor.fetchone()

								get_query_retailer_store = ("""SELECT *
										FROM `retailer_store_stores` WHERE `retailer_store_id` = %s and `organisation_id` = %s and `address` = %s""")
								getDataRetailerStore = (city_data['retailer_store_id'],organisation_id,retailer_store)
								count_retailer_store = cursor.execute(get_query_retailer_store,getDataRetailerStore)
								retailer_store_data = cursor.fetchone()

								insert_mapping_user_retailer = ("""INSERT INTO `user_retailer_mapping`(`user_id`,`retailer_id`,`retailer_store_id`,`status`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s,%s,%s)""")
											#organisation_id = 1
								last_update_id = organisation_id
								city_insert_data = (admin_id,city_data['retailer_store_id'],retailer_store_data['retailer_store_store_id'],admin_status,organisation_id,last_update_id)	
								cursor.execute(insert_mapping_user_retailer,city_insert_data)

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

										if general_loyality['signup_point'] > 0:

											get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s""")
											customer_wallet_data = (admin_id)
											cursor.execute(get_customer_wallet_query,customer_wallet_data)
											wallet_data = cursor.fetchone()
											wallet = general_loyality['signup_point']+wallet_data['wallet']
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

						initiate_paymengt_status = 1

						last_update_id = organisation_id
							
						initiatePaymentQuery = ("""INSERT INTO `instamojo_initiate_payment`(`user_id`, 
								`status`,`organisation_id`,`last_update_id`) VALUES (%s,%s,%s,%s)""")
						initiateData = (user_id,initiate_paymengt_status,organisation_id,last_update_id)
						cursor.execute(initiatePaymentQuery,initiateData)
						transaction_id = cursor.lastrowid							

						customer_product_status = "o"
						insert_query = ("""INSERT INTO `customer_product_mapping`(`customer_id`,`product_meta_id`,`product_status`,`status`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s,%s,%s)""")

						data = (user_id,product_meta_id,customer_product_status,initiate_paymengt_status,organisation_id,last_update_id)
						cursor.execute(insert_query,data)

						mapping_id = cursor.lastrowid
						details['mapping_id'] = mapping_id

						qty = details['qty']
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

							URL = BASE_URL + "ecommerce_customer_new/EcommerceCustomerNew/createPaymentRequest"

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
											"organisation_id": organisation_id,
											"order_payment_status":order_payment_status,
											"delivery_option":delivery_option,
											"delivery_charges":delivery_charges
									}
						

							mojoResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()

								
							print(mojoResponse['responseList'])		
							if mojoResponse['responseList']['transactionId']:

								payment_status = 'Cod'
								update_status = 'Ordered'
								payment_request_id = mojoResponse['responseList']['transactionId']
							
								updatePaymentQuery = ("""UPDATE `instamojo_payment_request` SET  
										`payment_status` = %s,`status` = %s WHERE `transaction_id`= %s""")

								paymentData = (payment_status,update_status,payment_request_id)
								cursor.execute(updatePaymentQuery,paymentData)

								print(cursor._last_executed)

								get_instamojo_payemnt_request_details_query = ("""SELECT *
													FROM `instamojo_payment_request` WHERE  `transaction_id` = %s""")
								get_instamojo_payemnt_request_details_data = (mojoResponse['responseList']['transactionId'])
								cursor.execute(get_instamojo_payemnt_request_details_query,get_instamojo_payemnt_request_details_data)

								instamojo_payment_data = cursor.fetchone()

								orderHistoryUrl =  BASE_URL + "order_historydtls/EcommerceOrderHistory/OderHistoryDetails"
								payloadDataOrderHistory = {
										  "order_product_id": instamojo_payment_data['transaction_id'],
										  "imageurl": "",
										  "retailer_remarks": "",
										  "updatedorder_status":instamojo_payment_data['status'],
										  "updatedpayment_status": instamojo_payment_data['payment_status'],
										  "updateduser_id": user_id,
										  "organisation_id": organisation_id
								}

								print(payloadDataOrderHistory)

								send_orderhistory = requests.post(orderHistoryUrl,data=json.dumps(payloadDataOrderHistory), headers=headers).json()


								createInvoiceUrl = BASE_URL + "ecommerce_customer_new/EcommerceCustomerNew/createInvoice"
									#createInvoiceUrl = "http://127.0.0.1:5000/ecommerce_customer/EcommerceCustomer/createInvoice"
								payloadData = {
										"user_id":user_id,
										"transaction_id":mojoResponse['responseList']['transactionId']							
								}

								send_invoice = requests.post(createInvoiceUrl,data=json.dumps(payloadData), headers=headers).json()

								headers = {'Content-type':'application/json', 'Accept':'application/json'}
								transactionLoyalityUrl = BASE_URL + "/ecommerce_customer_loyality/EcommerceCustomerLoyality/transactionLoyality"
								transactionLoyalityData = {
															"transaction_id":mojoResponse['responseList']['transactionId'],
															"customer_id":user_id,
															"organisation_id": organisation_id
														}		

								transactionLoyality = requests.post(transactionLoyalityUrl,data=json.dumps(transactionLoyalityData), headers=headers).json()

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

								sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer_new/EcommerceCustomerNew/sendAppPushNotifications"
								payloadpushData = {
										"device_id":device_token_data['device_token'],
										"firebase_key": firebase_data['firebase_key'],
										"update_status":update_status
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


							get_customer_data_query = ("""SELECT `first_name`,`last_name`,`email`,`phoneno`
									FROM `admins` WHERE  `admin_id` = %s""")

							getCustomerData = (user_id)
									
							countCustomerData = cursor.execute(get_customer_data_query,getCustomerData)

							if countCustomerData > 0 :
								cstomerData = cursor.fetchone()

								headers = {'Content-type':'application/json', 'Accept':'application/json'}
								sndNotificationUrl = BASE_URL + "ret_notification/RetailerNotification/SendPushNotificationsToOrganisation"
								payloadpushData = {
											"title":"Request an order",
											"msg":cstomerData['phoneno']+" has initiated Order",
											"img": "",
											"organisation_id": organisation_id
								}

								sndNotificationResponse = requests.post(sndNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

								

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

					else:
						return ({"attributes": {
				    		"status_desc": "payment_details",
				    		"status": "error",
				    		"message":"Wrong product Variant Selected"
				    	},
				    	"responseList":{} }), status.HTTP_200_OK
			else:
				return ({"attributes": {
				    		"status_desc": "payment_details",
				    		"status": "error",
				    		"message":"Wrong product Selected"
				    	},
				    	"responseList":{} }), status.HTTP_200_OK


		else:
			return ({"attributes": {
				    		"status_desc": "payment_details",
				    		"status": "error",
				    		"message":"Wrong Api Key"
				    	},
				    	"responseList":{} }), status.HTTP_200_OK

#----------------------Save-Transaction---------------------#

#----------------------Upload-Transaction---------------------#

@name_space.route("/uploadTransaction")
class uploadTransaction(Resource):
	@api.expect(upload_transaction_model)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_customer_name_string = details['customer_name']
		match_string_in_customer = re.search(r"\(([A-Za-z0-9_]+)\)", get_customer_name_string) 
		phone_no = match_string_in_customer.group(0) 
		customer_name_string = get_customer_name_string.split('(')
		customer_name = customer_name_string[0]
		color = details['color']

		get_product_name_string = details['product_name']
		product_name_strings = get_product_name_string.split(' ')

		meta_key_text = ""

		for key,data in enumerate(product_name_strings):
			find_string = "+"
			if find_string in data:
				storage_ram_array = data.split('+')
				ram = storage_ram_array[0]
				storage = storage_ram_array[1]

				storage_string = re.sub('(\d+(\.\d+)?)', r' \1 ', storage).strip()

				ram_string = ram+" GB"				

				get_storage_id_query = ("""SELECT *
									FROM `meta_key_value_master` WHERE  `meta_key_value` = %s and `organisation_id` = 1""")
				get_storage_id_data = (storage_string)
				storage_id_count = cursor.execute(get_storage_id_query,get_storage_id_data)

				if storage_id_count > 0:
					storage_id_data = cursor.fetchone()

					storage_id = storage_id_data['meta_key_value_id']

				else:
					storage_id = 0

				get_ram_id_query = ("""SELECT *
									FROM `meta_key_value_master` WHERE  `meta_key_value` = %s and `organisation_id` = 1""")
				get_ram_id_data = (ram_string)
				ram_id_count = cursor.execute(get_ram_id_query,get_ram_id_data)

				if ram_id_count > 0:
					ram_id_data = cursor.fetchone()

					ram_id = ram_id_data['meta_key_value_id']

				else:
					ram_id = 0

				get_color_id_query = ("""SELECT *
									FROM `meta_key_value_master` WHERE  `meta_key_value` = %s and `organisation_id` = 1""")
				get_color_id_data = (color)
				color_id_count = cursor.execute(get_color_id_query,get_color_id_data)

				if color_id_count > 0:
					color_id_data = cursor.fetchone()
					color_id = color_id_data['meta_key_value_id']
				else:
					color_id = 0

				meta_key_text = str(storage_id)+","+str(color_id)+","+str(ram_id)
				print(meta_key_text)





		
		

#----------------------Upload-Transaction---------------------#

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
