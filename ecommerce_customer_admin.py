from pyfcm import FCMNotification
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
import random, string

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

ecommerce_customer_admin = Blueprint('ecommerce_customer_admin', __name__)
api = Api(ecommerce_customer_admin,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceCustomerAdmin',description='Ecommerce Customer Admin')

customer_postmodel = api.model('SelectCustomer', {
	"first_name":fields.String,	
	"email":fields.String,
	"password":fields.String,
	#"phoneno":fields.Integer(required=True),
	"phoneno":fields.List(fields.String),
	"dob":fields.String,
	"anniversary":fields.String,
	"address_line_1":fields.String,
	"address_line_2":fields.String,
	"city":fields.String,
	"retailer_store":fields.String,
	"county":fields.String,
	"state":fields.String,
	"pincode":fields.Integer,	
	"organisation_id":fields.Integer(required=True)
})

customer_postmodel_with_retail_store = api.model('SelectCustomerWithRetailStore', {
	"first_name":fields.String,	
	"email":fields.String,
	"password":fields.String,
	#"phoneno":fields.Integer(required=True),
	"phoneno":fields.List(fields.String),
	"dob":fields.String,
	"anniversary":fields.String,
	"address_line_1":fields.String,
	"address_line_2":fields.String,
	"retailer_store_store_id":fields.Integer(required=True),
	"county":fields.String,
	"state":fields.String,
	"pincode":fields.Integer,	
	"organisation_id":fields.Integer(required=True)
})

customer_basic_putmodel = api.model('customerBasic',{
	"first_name":fields.String,
	"email":fields.String,
	"password":fields.String,
	"dob":fields.String,
	"anniversary":fields.String,
	"address_line_1":fields.String,
	"address_line_2":fields.String,
	"city":fields.String,
	"retailer_store":fields.String,
	"county":fields.String,
	"state":fields.String,
	"pincode":fields.Integer
})

customer_type_postmodel = api.model('SelectCustomerType', {
	"user_id":fields.Integer(required=True),
	"customer_type":fields.String(required=True),
	"organisation_id":fields.Integer(required=True)
})

customer_type_putmodel = api.model('UpdateCustomerType', {	
	"customer_type":fields.String(required=True)
})

customer_remarks_postmodel = api.model('SelectCustomerRemarks', {
	"user_id":fields.Integer(required=True),
	"product_id":fields.Integer(required=True),
	"remarks":fields.String,
	"organisation_id":fields.Integer(required=True)
})

notification_model = api.model('notification_model', {
	"source_id":fields.Integer(required=True),
	"source_type":fields.Integer(required=True),
	"offer_type":fields.Integer,
	"product_id":fields.Integer,
	"product_meta_code":fields.Integer,
	"product_meta_id":fields.Integer,
	"catalog_name":fields.String,
	"is_landing_page":fields.String,
	"product_name":fields.String,
	"user_id":fields.List(fields.Integer),
	"text":fields.String(),
	"image":fields.String(),
	"title": fields.String(required=True),
	"organisation_id": fields.Integer(required=True)
})

appmsg_model = api.model('appmsg_model', {	
	"firebase_key":fields.String(),
	"device_id":fields.String(),
	"text":fields.String(),
	"image":fields.String(),
	"notification_type":fields.Integer,
	"offer_type":fields.Integer,
	"catalog_id":fields.Integer,
	"offer_id":fields.Integer,
	"product_id":fields.Integer,
	"product_meta_code":fields.Integer,
	"product_meta_id":fields.Integer,
	"catalog_name":fields.String,
	"is_landing_page":fields.Integer,
	"product_name":fields.String,
	"title": fields.String(required=True),
})

customer_zoho_postmodel = api.model('zoho_postmodel',{
	"user_id": fields.Integer(required=True),
	"organisation_id": fields.Integer(required=True)
})

wallet_putmodel = api.model('wallet_putmodel',{
	'wallet': fields.Integer(required=True)
})

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#----------------------Add-Customer---------------------#

@name_space.route("/AddCustomer")
class AddCustomer(Resource):
	@api.expect(customer_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()			
		details = request.get_json()	

		first_name = details['first_name']		
		email = details['email']
		password = details['password']
		phonenos = details.get('phoneno',[])
		#phoneno = details['phoneno']
		dob = details['dob']
		anniversary = details['anniversary']
		address_line_1 = details['address_line_1']
		address_line_2 = details['address_line_2']
		city = details['city']
		retailer_store = details['retailer_store']
		county = details['county']
		state = details['state']
		pincode = details['pincode']		
		role_id = 4
		admin_status = 1
		organisation_id = details['organisation_id']
		registration_type = 5

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		for key,phoneno in enumerate(phonenos):

			get_phone_query = ("""SELECT *
					FROM `admins` WHERE `phoneno` = %s and `organisation_id` = %s""")
			get_phone_data = (phoneno,organisation_id)

			count_phone_data = cursor.execute(get_phone_query,get_phone_data)

			if count_phone_data > 0:

				return ({"attributes": {
				    		"status_desc": "customer_details",
				    		"status": "error",
				    		"message":"Customer Phoneno Already Exist"
				    	},
				    	"responseList":{} }), status.HTTP_200_OK
			else:

				insert_query = ("""INSERT INTO `admins`(`first_name`,`email`,`org_password`,
												`phoneno`,`dob`,`anniversary`,`address_line_1`,`address_line_2`,`city`,`country`,
												`state`,`pincode`,`role_id`,`registration_type`,`status`,`organisation_id`,`date_of_creation`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				data = (first_name,email,password,phoneno,dob,anniversary,address_line_1,address_line_2,city,county,state,pincode,role_id,registration_type,admin_status,organisation_id,date_of_creation)
				cursor.execute(insert_query,data)

				admin_id = cursor.lastrowid	

				details['user_id'] = admin_id

				user_id = admin_id
				organisation_id = organisation_id		

				'''get_customer_query = ("""SELECT a.`First_name`,a.`phoneno`,a.`email`,rs.`city`,rss.`store_name`,a.`loggedin_status`,a.`registration_type`
					FROM `admins` a	
					INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`	
					INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = urm.`retailer_store_id`
					INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = urm.`retailer_id`	
					where a.`organisation_id` = %s and a.`admin_id` = %s and urm.`organisation_id` = %s""")
				get_customer_data = (organisation_id,user_id,organisation_id)
				cursor.execute(get_customer_query,get_customer_data)

				customer_data = cursor.fetchone()

				if customer_data['First_name'] == '':
					customer_data['Last_Name'] = customer_data['store_name']+" Customer"
				else:
					customer_data['Last_Name'] = customer_data['First_name']

				if customer_data['loggedin_status'] == 1:
					customer_data['loggedin_status'] = "logged In" 
				else:
					customer_data['loggedin_status'] = "Never Logged In"

				if customer_data['registration_type'] == 4 or data['registration_type'] == 1:
					customer_data['Lead_Source'] = "Online Store"
				else:
					customer_data['Lead_Source'] = "Facebook"

				get_zoho_query = ("""SELECT * FROM `organisation_zoho_details` where `organisation_id` = %s""")
				get_zoho_data = (organisation_id)
				zoho_count = cursor.execute(get_zoho_query,get_zoho_data)
				print(cursor._last_executed)

				print(zoho_count)

				if zoho_count > 0:
					zoho_data = cursor.fetchone()

					if zoho_data['Is_active'] == 1:
						headers = {'Content-type':'application/json', 'Accept':'application/json'}
						Url = BASE_URL + "zoho_crm_ecommerce_product/ZohoCrmEcommerceProduct/customerImportintoZoho"
						payloadhData = {
								"First_Name":"",
								"Last_Name":  customer_data['Last_Name'],
								"Email": customer_data['email'],
								"store": customer_data['store_name'],
								"City": customer_data['city'],
								"Phone": customer_data['phoneno'],
								"Loggedin_Status":customer_data['loggedin_status'],
								"Lead_Source":customer_data['Lead_Source'],
								"organisation_id":organisation_id
						}

						print(Url)
						print(payloadhData)
						create_customer_to_zoho = requests.post(Url,data=json.dumps(payloadhData), headers=headers).json()'''

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
				"responseList":details}), status.HTTP_200_OK

#----------------------Add-Customer---------------------#

#----------------------Add-Customer-With-Retail-Store-Id--------------------#

@name_space.route("/AddCustomerWithRetailStoreId")
class AddCustomerWithRetailStoreId(Resource):
	@api.expect(customer_postmodel_with_retail_store)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()			
		details = request.get_json()	

		first_name = details['first_name']		
		email = details['email']
		password = details['password']
		phonenos = details.get('phoneno',[])
		#phoneno = details['phoneno']
		dob = details['dob']
		anniversary = details['anniversary']
		address_line_1 = details['address_line_1']
		address_line_2 = details['address_line_2']
		
		county = details['county']
		state = details['state']
		pincode = details['pincode']		
		role_id = 4
		admin_status = 1
		organisation_id = details['organisation_id']
		registration_type = 5

		retailer_store_store_id = details['retailer_store_store_id']

		get_query_retail_store = ("""SELECT *
					FROM `retailer_store_stores` WHERE `retailer_store_store_id` = %s and organisation_id = %s""")
		getDataRetailStore = (retailer_store_store_id,organisation_id)
		count_Retail_Store = cursor.execute(get_query_retail_store,getDataRetailStore)

		retail_store = cursor.fetchone()

		get_query_city = ("""SELECT *
					FROM `retailer_store` WHERE `retailer_store_id` = %s and organisation_id = %s""")
		getDataCity = (retail_store['retailer_store_id'],organisation_id)
		count_city = cursor.execute(get_query_city,getDataCity)

		city_data = cursor.fetchone()


		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		for key,phoneno in enumerate(phonenos):

			get_phone_query = ("""SELECT *
					FROM `admins` WHERE `phoneno` = %s and `organisation_id` = %s""")
			get_phone_data = (phoneno,organisation_id)

			count_phone_data = cursor.execute(get_phone_query,get_phone_data)

			if count_phone_data > 0:

				return ({"attributes": {
				    		"status_desc": "customer_details",
				    		"status": "error",
				    		"message":"Customer Phoneno Already Exist"
				    	},
				    	"responseList":{} }), status.HTTP_200_OK
			else:

				insert_query = ("""INSERT INTO `admins`(`first_name`,`email`,`org_password`,
												`phoneno`,`dob`,`anniversary`,`address_line_1`,`address_line_2`,`city`,`country`,
												`state`,`pincode`,`role_id`,`registration_type`,`status`,`organisation_id`,`date_of_creation`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				data = (first_name,email,password,phoneno,dob,anniversary,address_line_1,address_line_2,city_data['city'],county,state,pincode,role_id,registration_type,admin_status,organisation_id,date_of_creation)
				cursor.execute(insert_query,data)

				admin_id = cursor.lastrowid	

				details['user_id'] = admin_id

				user_id = admin_id
				organisation_id = organisation_id		

				'''get_customer_query = ("""SELECT a.`First_name`,a.`phoneno`,a.`email`,rs.`city`,rss.`store_name`,a.`loggedin_status`,a.`registration_type`
					FROM `admins` a	
					INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`	
					INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = urm.`retailer_store_id`
					INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = urm.`retailer_id`	
					where a.`organisation_id` = %s and a.`admin_id` = %s and urm.`organisation_id` = %s""")
				get_customer_data = (organisation_id,user_id,organisation_id)
				cursor.execute(get_customer_query,get_customer_data)

				customer_data = cursor.fetchone()

				if customer_data['First_name'] == '':
					customer_data['Last_Name'] = customer_data['store_name']+" Customer"
				else:
					customer_data['Last_Name'] = customer_data['First_name']

				if customer_data['loggedin_status'] == 1:
					customer_data['loggedin_status'] = "logged In" 
				else:
					customer_data['loggedin_status'] = "Never Logged In"

				if customer_data['registration_type'] == 4 or data['registration_type'] == 1:
					customer_data['Lead_Source'] = "Online Store"
				else:
					customer_data['Lead_Source'] = "Facebook"

				get_zoho_query = ("""SELECT * FROM `organisation_zoho_details` where `organisation_id` = %s""")
				get_zoho_data = (organisation_id)
				zoho_count = cursor.execute(get_zoho_query,get_zoho_data)
				print(cursor._last_executed)

				print(zoho_count)

				if zoho_count > 0:
					zoho_data = cursor.fetchone()

					if zoho_data['Is_active'] == 1:
						headers = {'Content-type':'application/json', 'Accept':'application/json'}
						Url = BASE_URL + "zoho_crm_ecommerce_product/ZohoCrmEcommerceProduct/customerImportintoZoho"
						payloadhData = {
								"First_Name":"",
								"Last_Name":  customer_data['Last_Name'],
								"Email": customer_data['email'],
								"store": customer_data['store_name'],
								"City": customer_data['city'],
								"Phone": customer_data['phoneno'],
								"Loggedin_Status":customer_data['loggedin_status'],
								"Lead_Source":customer_data['Lead_Source'],
								"organisation_id":organisation_id
						}

						print(Url)
						print(payloadhData)
						create_customer_to_zoho = requests.post(Url,data=json.dumps(payloadhData), headers=headers).json()'''

				insert_customer_referal_code_query = ("""INSERT INTO `customer_referral`(`customer_id`,`referral_code`,`organisation_id`,`status`,`last_update_id`)
					VALUES(%s,%s,%s,%s,%s)""")
			
				last_update_id = organisation_id	

				customer_referral_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

				referal_data = (admin_id,customer_referral_code,organisation_id,admin_status,last_update_id)
				cursor.execute(insert_customer_referal_code_query,referal_data)

				

				insert_mapping_user_retailer = ("""INSERT INTO `user_retailer_mapping`(`user_id`,`retailer_id`,`retailer_store_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s)""")
								#organisation_id = 1
				last_update_id = organisation_id
				city_insert_data = (admin_id,city_data['retailer_store_id'],retail_store['retailer_store_store_id'],admin_status,organisation_id,last_update_id)	
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

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Add-Customer-With-Retail-Store-Id--------------------#

#----------------------Update-Customer-Information---------------------#

@name_space.route("/updateCustomerInfo/<int:user_id>/<int:organisation_id>")
class updateCustomerBasicInfo(Resource):
	@api.expect(customer_basic_putmodel)
	def put(self, user_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "first_name" in details:
			first_name = details['first_name']
			update_query = ("""UPDATE `admins` SET `first_name` = %s
				WHERE `admin_id` = %s """)
			update_data = (first_name,user_id)
			cursor.execute(update_query,update_data)

		if details and "email" in details:
			email = details['email']
			update_query = ("""UPDATE `admins` SET `email` = %s
				WHERE `admin_id` = %s """)
			update_data = (email,user_id)
			cursor.execute(update_query,update_data)

		if details and "password" in details:
			password = details['password']
			update_query = ("""UPDATE `admins` SET `org_password` = %s
				WHERE `admin_id` = %s """)
			update_data = (password,user_id)
			cursor.execute(update_query,update_data)

		if details and "dob" in details:
			dob = details['dob']
			update_query = ("""UPDATE `admins` SET `dob` = %s
				WHERE `admin_id` = %s """)
			update_data = (dob,user_id)
			cursor.execute(update_query,update_data)

		if details and "anniversary" in details:
			anniversary = details['anniversary']
			update_query = ("""UPDATE `admins` SET `anniversary` = %s
				WHERE `admin_id` = %s """)
			update_data = (anniversary,user_id)
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

		if details and "retailer_store" in details:

			get_query_city = ("""SELECT *
				FROM `retailer_store` WHERE `city` = %s and organisation_id = %s""")
			getDataCity = (details['city'],organisation_id)
			count_city = cursor.execute(get_query_city,getDataCity)

			if count_city > 0:
				city_data = cursor.fetchone()

				get_query_retailer_store = ("""SELECT *
						FROM `retailer_store_stores` WHERE `retailer_store_id` = %s and `organisation_id` = %s and `address` = %s""")
				getDataRetailerStore = (city_data['retailer_store_id'],organisation_id,details['retailer_store'])
				count_retailer_store = cursor.execute(get_query_retailer_store,getDataRetailerStore)
				retailer_store_data = cursor.fetchone()

				get_mapping_query = ("""SELECT *
					FROM `user_retailer_mapping` WHERE  `user_id` = %s and `organisation_id` = %s""")

				getMappingData = (user_id,organisation_id)
			
				count_mapping_data = cursor.execute(get_mapping_query,getMappingData)

				if count_mapping_data > 0:

					update_query = ("""UPDATE `user_retailer_mapping` SET `retailer_id` = %s,`retailer_store_id` = %s
								WHERE `user_id` = %s and `organisation_id` = %s""")
					update_data = (city_data['retailer_store_id'],retailer_store_data['retailer_store_store_id'],user_id,organisation_id)
					cursor.execute(update_query,update_data)

					update_user_query = ("""UPDATE `admins` SET `city` = %s
								WHERE `admin_id` = %s""")
					update_user_data = (details['city'],user_id)
					cursor.execute(update_user_query,update_user_data)

				else:
					insert_mapping_user_retailer = ("""INSERT INTO `user_retailer_mapping`(`user_id`,`retailer_id`,`retailer_store_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s)""")
					
					admin_status = 1		
					last_update_id = organisation_id
					city_insert_data = (user_id,city_data['retailer_store_id'],retailer_store_data['retailer_store_store_id'],admin_status,organisation_id,last_update_id)	
					cursor.execute(insert_mapping_user_retailer,city_insert_data)



		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Customer Basic Information",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Customer-Information---------------------#

#-----------------------Customer-Type-List-From-Master---------------------#

@name_space.route("/customerTypeListFromMaster")	
class customerTypeListFromMaster(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `customer_type_master` where `status` = 1""")
		cursor.execute(get_query)

		customer_type_master_data = cursor.fetchall()

		for key,data in enumerate(customer_type_master_data):
			customer_type_master_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "customer_type",
		    		"status": "success"
		    	},
		    	"responseList":customer_type_master_data}), status.HTTP_200_OK

#-----------------------Customer-Type-List-From-Master---------------------#

#----------------------Add-Customer-Type---------------------#

@name_space.route("/AddCustomerType")
class AddCustomerType(Resource):
	@api.expect(customer_type_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()			
		details = request.get_json()

		customer_type = details['customer_type']		
		customer_id = details['user_id']
		organisation_id = details['organisation_id']
		last_update_id = organisation_id

		insert_query = ("""INSERT INTO `customer_type`(`customer_type`,`customer_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")
								
		
		insert_data = (customer_type,customer_id,organisation_id,last_update_id)	
		cursor.execute(insert_query,insert_data)	

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_Type",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK


#----------------------Add-Customer-Type---------------------#

#----------------------Update-Customer-Type---------------------#
@name_space.route("/UpdateCustomerType/<int:organisation_id>/<int:user_id>")
class UpdateCustomerType(Resource):
	@api.expect(customer_type_putmodel)
	def put(self,organisation_id,user_id):

		connection = mysql_connection()
		cursor = connection.cursor()			
		details = request.get_json()

		last_update_id = organisation_id
		customer_type = details['customer_type']

		get_query = ("""SELECT * FROM `customer_type` WHERE `organisation_id` = %s and `customer_id` = %s""")
		getData = (organisation_id,user_id)
		count_customer_type = cursor.execute(get_query,getData)

		if count_customer_type > 0:
			update_query = ("""UPDATE `customer_type` SET `customer_type` = %s
					WHERE `customer_id` = %s and `organisation_id` = %s""")
			update_data = (customer_type,user_id,organisation_id)
			cursor.execute(update_query,update_data)
		else:
			insert_query = ("""INSERT INTO `customer_type`(`customer_type`,`customer_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")
								
		
			insert_data = (customer_type,user_id,organisation_id,last_update_id)	
			cursor.execute(insert_query,insert_data)	

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Customer Type",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Customer-Type---------------------#


#----------------------Add-Customer-Remarks---------------------#

@name_space.route("/AddCustomerRemarks")
class AddCustomerRemarks(Resource):
	@api.expect(customer_remarks_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()			
		details = request.get_json()

		customer_id = details['user_id']		
		product_id = details['product_id']
		remarks = details['remarks']
		organisation_id = details['organisation_id']
		last_update_id = organisation_id

		insert_query = ("""INSERT INTO `customer_remarks`(`customer_id`,`product_id`,`remarks`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")								
		
		insert_data = (customer_id,product_id,remarks,organisation_id,last_update_id)	
		cursor.execute(insert_query,insert_data)	

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_remarks",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK


#----------------------Add-Customer-Remarks---------------------#

#-----------------------Customer-Remarks-List---------------------#

@name_space.route("/customerRemarksList/<int:organisation_id>/<int:user_id>")	
class customerRemarksList(Resource):
	def get(self,organisation_id,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT a.`admin_id` as user_id,cr.`remarks`,p.`product_name`,cr.`last_update_ts`
			FROM `customer_remarks` cr
			INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id` 
			INNER JOIN `product` p ON p.`product_id` = cr.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
			INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = pbm.`brand_id`	
			where cr.`organisation_id` = %s and cr.`customer_id` = %s""")
		get_data = (organisation_id,user_id)
		cursor.execute(get_query,get_data)

		customer_type_master_data = cursor.fetchall()

		for key,data in enumerate(customer_type_master_data):
			customer_type_master_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "customer_type",
		    		"status": "success"
		    	},
		    	"responseList":customer_type_master_data}), status.HTTP_200_OK

#-----------------------Customer-Remarks-List---------------------#

#-----------------------Customer-Detail-For-Zoho---------------------#

@name_space.route("/customerDetailForZoho")	
class customerDetailForZoho(Resource):
	@api.expect(customer_zoho_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		organisation_id = details['organisation_id']
		user_id = details['user_id']

		get_customer_query = ("""SELECT a.`First_name`,a.`phoneno`,a.`email`,rs.`city`,rss.`store_name`,a.`loggedin_status`,a.`registration_type`
			FROM `admins` a	
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`	
			INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = urm.`retailer_store_id`
			INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = urm.`retailer_id`	
			where a.`organisation_id` = %s and a.`admin_id` = %s and urm.`organisation_id` = %s""")
		get_customer_data = (organisation_id,user_id,organisation_id)
		cursor.execute(get_customer_query,get_customer_data)

		customer_data = cursor.fetchone()

		if customer_data['First_name'] == '':
			customer_data['Last_Name'] = customer_data['store_name']+" Customer"
		else:
			customer_data['Last_Name'] = customer_data['First_name']

		if customer_data['loggedin_status'] == 1:
			customer_data['loggedin_status'] = "logged In" 
		else:
			customer_data['loggedin_status'] = "Never Logged In"

		if customer_data['registration_type'] == 4 or data['registration_type'] == 1:
			customer_data['Lead_Source'] = "Online Store"
		else:
			customer_data['Lead_Source'] = "Facebook"

		get_zoho_query = ("""SELECT * FROM `organisation_zoho_details` where `organisation_id` = %s""")
		get_zoho_data = (organisation_id)
		zoho_count = cursor.execute(get_zoho_query,get_zoho_data)
		print(cursor._last_executed)

		print(zoho_count)

		if zoho_count > 0:
			zoho_data = cursor.fetchone()

			if zoho_data['Is_active'] == 1:
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				Url = BASE_URL + "zoho_crm_ecommerce_product/ZohoCrmEcommerceProduct/customerImportintoZoho"
				payloadhData = {
						"First_Name":"",
						"Last_Name":  customer_data['Last_Name'],
						"Email": customer_data['email'],
						"store": customer_data['store_name'],
						"City": customer_data['city'],
						"Phone": customer_data['phoneno'],
						"Loggedin_Status":customer_data['loggedin_status'],
						"Lead_Source":customer_data['Lead_Source'],
						"organisation_id":organisation_id
				}

				print(Url)
				print(payloadhData)
				create_customer_to_zoho = requests.post(Url,data=json.dumps(payloadhData), headers=headers).json()

		return ({"attributes": {
		    		"status_desc": "customer_detail",
		    		"status": "success"
		    	},
		    	"responseList":customer_data}), status.HTTP_200_OK


#-----------------------Customer-Detail-For-Zoho---------------------#

#----------------------Send-Notification---------------------#

@name_space.route("/sendNotifications")
class sendNotifications(Resource):
	@api.expect(notification_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		organisation_id = details['organisation_id']
		source_id = details['source_id']
		source_type = details['source_type']

		if details and "offer_type" in details:
			offer_type = details['offer_type']
		else:
			offer_type = 0

		if details and "product_id" in details:
			product_id = details['product_id']
		else:
			product_id = 0

		if details and "product_meta_code" in details:
			product_meta_code = details['product_meta_code']
		else:
			product_meta_code = 0

		if details and "product_meta_id" in details:
			product_meta_id = details['product_meta_id']
		else:
			product_meta_id = 0

		if details and "catalog_name" in details:
			catalog_name = details['catalog_name']
		else:
			catalog_name = ""

		if details and "is_landing_page" in details:
			is_landing_page = details['is_landing_page']
		else:
			is_landing_page = 0

		if details and "product_name" in details:
			product_name = details['product_name']
		else:
			product_name = ""



		get_organisation_firebase_query = ("""SELECT `firebase_key`
								FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
		get_organisation_firebase_data = (organisation_id)
		cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
		firebase_data = cursor.fetchone()

		user_ids = details.get('user_id',[])

		for ukey,user_id in enumerate(user_ids):

			get_device_query = ("""SELECT *
									FROM `devices` WHERE  `organisation_id` = %s and `user_id` = %s""")
			get_device_data = (organisation_id,user_id)
			cursor.execute(get_device_query,get_device_data)
			device_data = cursor.fetchone()

			if device_data:
			
				if device_data['device_type'] == 2:
					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer_admin/EcommerceCustomerAdmin/sendAppPushNotifications"
					if source_type == 1:
						payloadpushData = {
											"device_id":device_data['device_token'],
											"firebase_key": firebase_data['firebase_key'],
											"image":details['image'],
											"text":details['text'],
											"title":details['title'],
											"notification_type":source_type,
											"offer_type":offer_type,
											"offer_id":source_id,
											"catalog_id":0,
											"product_id":product_id,
											"product_meta_code":0,
											"product_meta_id":0,
											"catalog_name":"",
											"is_landing_page":is_landing_page,
											"product_name":""

										}
					else:
						payloadpushData = {
											"device_id":device_data['device_token'],
											"firebase_key": firebase_data['firebase_key'],
											"image":details['image'],
											"text":details['text'],
											"title":details['title'],
											"notification_type":source_type,
											"offer_type":0,
											"offer_id":0,
											"catalog_id":source_id,
											"product_id":0,
											"product_meta_code":product_meta_code,
											"product_meta_id":product_meta_id,
											"catalog_name":catalog_name,
											"is_landing_page":is_landing_page,
											"product_name":product_name

										}
					#print(payloadpushData)
					send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

					if send_push_notification['responseList']['success'] == 1:
						app_query = ("""INSERT INTO `app_notification`(`title`,`body`,`image`,
						`U_id`,`Device_ID`,`Sent`,`source_id`,`source_type`,`destination_type`,`organisation_id`) 
						VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
						sent = 'Yes'
						destination_type = 2
						insert_data = (details['title'],details['text'],details['image'],user_id,device_data['device_token'],sent,source_id,source_type,destination_type,organisation_id)
						appdata = cursor.execute(app_query,insert_data)
			else:
				print('No Device Found')


		return ({"attributes": {"status_desc": "Push Notification",
									"status": "success"},
					"responseList":details}), status.HTTP_200_OK

#----------------------Send-Notification---------------------#

#----------------------Send-Push-Notification---------------------#

@name_space.route("/sendAppPushNotifications")
class sendAppPushNotifications(Resource):
	@api.expect(appmsg_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		data_message = {
							"title" : details['title'],
							"message": details['text'],
							"image-url":details['image'],
							"notification_type":details['notification_type'],
							"offer_type":details['offer_type'],
							"catalog_id":details['catalog_id'],
							"offer_id":details['offer_id'],
							"product_id":details['product_id'],
							"product_meta_code":details['product_meta_code'],
							"product_meta_id":details['product_meta_id'],
							"catalog_name":details['catalog_name'],
							"is_landing_page":details['is_landing_page'],
							"product_name":details['product_name']
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


#----------------------Update-Wallet---------------------#

@name_space.route("/updateWallet/<int:organisation_id>")
class updateWallet(Resource):
	@api.expect(wallet_putmodel)
	def put(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "wallet" in details:
			wallet = details['wallet']
			update_query = ("""UPDATE `admins` SET `wallet` = %s
				WHERE `organisation_id` = %s and `wallet` < 500 """)
			update_data = (wallet,organisation_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "Wallet",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK

#----------------------Update-Wallet---------------------#
