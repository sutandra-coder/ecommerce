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


ecommerce_customer_loyality = Blueprint('ecommerce_customer_loyality_api', __name__)
api = Api(ecommerce_customer_loyality,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceCustomerLoyality',description='Ecommerce Customer Loyality')

referal_loyality_postmodel = api.model('SelectReferalLoyalityPostmodel', {
	"referal_code":fields.String(required=True),	
	"customer_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

signup_loyality_postmodel = api.model('SelectSignUpLoyalityPostmodel', {	
	"customer_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

transaction_loyality_postmodel = api.model('SelectTransactionLoyalityPostmodel', {
	"transaction_id":fields.Integer(required=True),
	"customer_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#----------------------referal-loyality---------------------#

@name_space.route("/referalLoyality")
class referalLoyality(Resource):
	@api.expect(referal_loyality_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		referal_code = details['referal_code']
		referral_user_id = details['customer_id']
		organisation_id = details['organisation_id']


		get_loyality_settings_query = ("""SELECT `setting_value`
					FROM `referal_loyality_settings` WHERE `organisation_id` = %s""")
		getLoyalitySettingsData = (organisation_id)
		count_loyality_settings = cursor.execute(get_loyality_settings_query,getLoyalitySettingsData)

		if count_loyality_settings > 0:
			loyality_settings = cursor.fetchone()

			if loyality_settings['setting_value'] == 1:

				get_referal_query = ("""SELECT `customer_referral_id`,`referral_code`,`customer_id`
							FROM `customer_referral` WHERE `referral_code` = %s and `organisation_id` = %s""")
				getReferalData = (details['referal_code'],organisation_id)
				count_referal = cursor.execute(get_referal_query,getReferalData)

				if count_referal > 0:
					referal = cursor.fetchone()

					reffered_user_id = referal['customer_id']

					customer_referral_id = referal['customer_referral_id']

					user_referal_status = 1

					insert_user_referal_code_query = ("""INSERT INTO `user_referral_mapping`(`customer_referral_id`,`customer_id`,`organisation_id`,`status`,`last_update_id`)
								VALUES(%s,%s,%s,%s,%s)""")
					user_referal_data = (customer_referral_id,details['customer_id'],details['organisation_id'],user_referal_status,details['organisation_id'])

					cursor.execute(insert_user_referal_code_query,user_referal_data)

					referal_user_loyality_type = 1
					get_referal_loyality_query = ("""SELECT *
									FROM `loyality_master`
						 			WHERE `organisation_id` = %s and loyality_type =%s """)

					get_referal_loyality_data = (organisation_id,referal_user_loyality_type)
					count_referal_loyality = cursor.execute(get_referal_loyality_query,get_referal_loyality_data)

					if count_referal_loyality > 0:
						referal_loyality_data = cursor.fetchone()

						if referal_loyality_data['loyality_amount'] > 0:

							get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s""")
							customer_wallet_data = (referral_user_id)
							cursor.execute(get_customer_wallet_query,customer_wallet_data)
							wallet_data = cursor.fetchone()

							wallet = referal_loyality_data['loyality_amount']+wallet_data['wallet']
							transaction_id = 0
							redeem_history_id = 0
							

							insert_referal_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
									`updated_value`,`transaction_id`,`redeem_history_id`,`organisation_id`,`status`,`last_update_id`)
												VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
							transaction_source = "referal"
							updated_value = wallet
							previous_value = wallet_data['wallet']
							wallet_transation_status = 1
							referal_wallet_transaction_data = (referral_user_id,referal_loyality_data['loyality_amount'],transaction_source,previous_value,updated_value,transaction_id,redeem_history_id,organisation_id,wallet_transation_status,organisation_id)

							cursor.execute(insert_referal_wallet_transaction_query,referal_wallet_transaction_data)

							update_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s
																	WHERE `admin_id` = %s """)
							update_data = (wallet,referral_user_id)
							cursor.execute(update_customer_wallet_query,update_data)

							get_user_device_query = ("""SELECT `device_token`
									FROM `devices` WHERE  `user_id` = %s and `organisation_id` = %s""")

							get_user_device_data = (referral_user_id,organisation_id)
							device_token_count = cursor.execute(get_user_device_query,get_user_device_data)

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

					referred_user_loyality_type = 2
					get_refferd_user_loyality_query = ("""SELECT *
									FROM `loyality_master`
						 			WHERE `organisation_id` = %s and loyality_type =%s""")
					get_reffered_loyality_data = (organisation_id,referred_user_loyality_type)
					count_refferd_loyality = cursor.execute(get_refferd_user_loyality_query,get_reffered_loyality_data)

					if count_refferd_loyality > 0 :
						refered_loyality_data = cursor.fetchone()

						if refered_loyality_data['loyality_amount'] > 0:
						
							get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s""")
							customer_wallet_data = (reffered_user_id)
							cursor.execute(get_customer_wallet_query,customer_wallet_data)
							wallet_data = cursor.fetchone()

							wallet = refered_loyality_data['loyality_amount']+wallet_data['wallet']
							transaction_id = 0
							redeem_history_id = 0

							insert_referal_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
									`updated_value`,`transaction_id`,`redeem_history_id`,`organisation_id`,`status`,`last_update_id`)
												VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
							transaction_source = "referal"
							updated_value = wallet
							previous_value = wallet_data['wallet']
							wallet_transation_status = 1
							referal_wallet_transaction_data = (reffered_user_id,refered_loyality_data['loyality_amount'],transaction_source,previous_value,updated_value,transaction_id,redeem_history_id,organisation_id,wallet_transation_status,organisation_id)

							cursor.execute(insert_referal_wallet_transaction_query,referal_wallet_transaction_data)

							update_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s
																	WHERE `admin_id` = %s """)
							update_data = (wallet,reffered_user_id)
							cursor.execute(update_customer_wallet_query,update_data)

							get_refferd_user_device_query = ("""SELECT `device_token`
									FROM `devices` WHERE  `user_id` = %s and `organisation_id` = %s""")

							get_refferd_user_device_data = (reffered_user_id,organisation_id)
							reffred_user_device_token_count = cursor.execute(get_refferd_user_device_query,get_refferd_user_device_data)	

							if reffred_user_device_token_count > 0:
								refferd_user_device_token_data = cursor.fetchone()

								get_organisation_firebase_query = ("""SELECT `firebase_key`
										FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
								get_organisation_firebase_data = (organisation_id)
								cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
								firebase_data = cursor.fetchone()

								headers = {'Content-type':'application/json', 'Accept':'application/json'}
								sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer_new/EcommerceCustomerNew/sendAppPushNotificationforloyalityPoint"
								payloadpushData = {
									"device_id":refferd_user_device_token_data['device_token'],
									"firebase_key": firebase_data['firebase_key']
								}

								send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()
				else:
					referal = {}				
			else:
				referal = {}					
		else:
			referal = {}

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "referal_loyality",
			    		"status": "success"
			    },
			    "responseList":referal}), status.HTTP_200_OK

#----------------------referal-loyality---------------------#

#----------------------Signup-loyality---------------------#

@name_space.route("/signupLoyality")
class signupLoyality(Resource):
	@api.expect(signup_loyality_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		organisation_id = details['organisation_id']
		customer_id = details['customer_id']

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
						customer_wallet_data = (customer_id)
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
						wallet_transaction_data = (customer_id,general_loyality['signup_point'],transaction_source,previous_value,updated_value,transaction_id,redeem_history_id,organisation_id,wallet_transation_status,organisation_id)
						cursor.execute(insert_wallet_transaction_query,wallet_transaction_data)

						update_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s
																	WHERE `admin_id` = %s """)
						update_data = (wallet,customer_id)
						cursor.execute(update_customer_wallet_query,update_data)

						get_device_query = ("""SELECT `device_token`
									FROM `devices` WHERE  `user_id` = %s and `organisation_id` = %s""")

						get_device_data = (customer_id,organisation_id)
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

					else:
						general_loyality = {}
				else:
					general_loyality = {}			

			else:
				general_loyality = {}				

		else:
			general_loyality = {}

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "signup_loyality",
			    		"status": "success"
			    },
			    "responseList":general_loyality}), status.HTTP_200_OK

#----------------------Signup-loyality---------------------#

#----------------------Transaction-loyality---------------------#

@name_space.route("/transactionLoyality")
class transactionLoyality(Resource):
	@api.expect(transaction_loyality_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		transaction_id = details['transaction_id']
		customer_id = details['customer_id']
		organisation_id = details['organisation_id']

		get_loyality_settings_query = ("""SELECT `setting_value`
					FROM `referal_loyality_settings` WHERE `organisation_id` = %s""")
		getLoyalitySettingsData = (organisation_id)
		count_loyality_settings = cursor.execute(get_loyality_settings_query,getLoyalitySettingsData)

		if count_loyality_settings > 0:
			loyality_settings = cursor.fetchone()

			if loyality_settings['setting_value'] == 1:

				get_general_loyality_query = ("""SELECT `per_transaction_percentage`
							FROM `general_loyalty_master` WHERE `organisation_id` = %s""")
				getGeneralLoyalityData = (organisation_id)
				count_general_loyality = cursor.execute(get_general_loyality_query,getGeneralLoyalityData)

				if count_general_loyality > 0:
					general_loyality =  cursor.fetchone()

					if general_loyality['per_transaction_percentage'] >0:

						get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s and `organisation_id` = %s""")
						customer_wallet_data = (customer_id,organisation_id)
						cursor.execute(get_customer_wallet_query,customer_wallet_data)
						wallet_data = cursor.fetchone()

						get_transaction_query = ("""SELECT `amount` from `instamojo_payment_request` WHERE `transaction_id` = %s and `organisation_id` = %s and `user_id` = %s""")
						get_transaction_data = (transaction_id,organisation_id,customer_id)
						cursor.execute(get_transaction_query,get_transaction_data)
						transaction_data = cursor.fetchone()

						transaction_wallet = round((transaction_data['amount'] * general_loyality['per_transaction_percentage'])/100)

						wallet = transaction_wallet+wallet_data['wallet']

						insert_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
									`updated_value`,`transaction_id`,`organisation_id`,`status`,`last_update_id`)
												VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
						transaction_source = "transactional"
						updated_value = wallet
						previous_value = wallet_data['wallet']
						wallet_transation_status = 1
						wallet_transaction_data = (customer_id,transaction_wallet,transaction_source,previous_value,updated_value,transaction_id,organisation_id,wallet_transation_status,organisation_id)
						cursor.execute(insert_wallet_transaction_query,wallet_transaction_data)

						update_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s
																	WHERE `admin_id` = %s and `organisation_id` = %s""")
						update_data = (wallet,customer_id,organisation_id)
						cursor.execute(update_customer_wallet_query,update_data)

						get_device_query = ("""SELECT `device_token`
									FROM `devices` WHERE  `user_id` = %s and `organisation_id` = %s""")

						get_device_data = (customer_id,organisation_id)
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
					
					else:
						general_loyality = {}
				else:
					general_loyality = {}		
			
			else:
				general_loyality = {}			
		
		else:
			general_loyality = {}


		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "transaction_loyality",
			    		"status": "success"
			    },
			    "responseList":general_loyality}), status.HTTP_200_OK

#----------------------Transaction-loyality---------------------#


#----------------------Wallet-History---------------------#

@name_space.route("/walletHistoryByCustomerId/<int:customer_id>/<int:organisation_id>")	
class walletHistoryByCustomerId(Resource):
	def get(self,customer_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_customer_wallet_query = ("""SELECT * from `admins` WHERE `admin_id` = %s and `organisation_id` = %s""")
		get_customer_wallet_data = (customer_id,organisation_id)
		customer_wallet_count = cursor.execute(get_customer_wallet_query,get_customer_wallet_data)
		if customer_wallet_count > 0:
			customer_wallet_data = cursor.fetchone()
			wallet = customer_wallet_data['wallet']
		else:
			wallet = 0

		get_customer_wallet_transaction_query = ("""SELECT * from `wallet_transaction` WHERE `customer_id` = %s and `organisation_id` = %s and `transaction_source` != 'product_loyalty'""")
		get_customer_wallet_transaction_data = (customer_id,organisation_id)
		count_customer_wallet_transaction = cursor.execute(get_customer_wallet_transaction_query,get_customer_wallet_transaction_data)

		if count_customer_wallet_transaction > 0:
			customer_wallet_transaction_data = cursor.fetchall()
			for key,data in enumerate(customer_wallet_transaction_data):
				if data['redeem_history_id'] >0:				
					get_redeem_history_query = ("""SELECT * from `redeem_history` WHERE `redeem_history_id` = %s""")
					get_redeem_history_data = (data['redeem_history_id'])
					count_redeem_history = cursor.execute(get_redeem_history_query,get_redeem_history_data)					

					if count_redeem_history > 0:
						redeem_history_data = cursor.fetchone()
						customer_wallet_transaction_data[key]['redeem_transaction_id'] = redeem_history_data['transaction_id']
						customer_wallet_transaction_data[key]['redeem_point'] = redeem_history_data['redeem_point']
						customer_wallet_transaction_data[key]['offer_id'] = redeem_history_data['offer_id']
						customer_wallet_transaction_data[key]['produt_id'] = redeem_history_data['product_id']
						customer_wallet_transaction_data[key]['produt_meta_id'] = redeem_history_data['product_meta_id']
						customer_wallet_transaction_data[key]['image'] = redeem_history_data['image']
						customer_wallet_transaction_data[key]['remarks'] = redeem_history_data['remarks']
					else:
						customer_wallet_transaction_data[key]['redeem_transaction_id'] = 0
						customer_wallet_transaction_data[key]['redeem_point'] = 0
						customer_wallet_transaction_data[key]['offer_id'] = 0
						customer_wallet_transaction_data[key]['produt_id'] = 0
						customer_wallet_transaction_data[key]['produt_meta_id'] = 0
						customer_wallet_transaction_data[key]['image'] = ""
						customer_wallet_transaction_data[key]['remarks'] = ""
				else:
					customer_wallet_transaction_data[key]['redeem_transaction_id'] = 0
					customer_wallet_transaction_data[key]['redeem_point'] = 0
					customer_wallet_transaction_data[key]['offer_id'] = 0
					customer_wallet_transaction_data[key]['produt_id'] = 0
					customer_wallet_transaction_data[key]['produt_meta_id'] = 0
					customer_wallet_transaction_data[key]['image'] = ""
					customer_wallet_transaction_data[key]['remarks'] = ""

				customer_wallet_transaction_data[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			customer_wallet_transaction_data = []

		return ({"attributes": {
		    		"status_desc": "Customer Wallet History",
		    		"status": "success",
		    		"wallet":wallet
		    	},
		    	"responseList":{"wallet_data":customer_wallet_transaction_data,"wallet":wallet} }), status.HTTP_200_OK

#----------------------Wallet-History---------------------#

