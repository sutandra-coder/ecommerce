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

ecommerce_organisation = Blueprint('ecommerce_organisation_api', __name__)
api = Api(ecommerce_organisation,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceOrganisation',description='Ecommerce Organisation')


checkphoneno_postmodel = api.model('checkPhone',{
	"phoneno":fields.String(required=True),
})

organisation_postmodel = api.model('SelectOrganisation', {	
	"phoneno":fields.Integer,
	"email":fields.String,
	"device_token":fields.String,
	"registration_type":fields.Integer(required=True)
})

organisation_login_postmodel = api.model('SelectOrganisationLogin', {	
	"phoneno":fields.String(required=True),
	"device_token":fields.String
})


organisation_putmodel = api.model('updateOrganisation',{	
	"organization_name":fields.String,
	"server_name":fields.String(required=True),
	"logo":fields.String,
	"email":fields.String,
	"phone":fields.String,
	"area":fields.String,
	"city":fields.String,
	"pincode":fields.Integer,
	"gst_number":fields.String,
	"currency": fields.String,
	"facebook_link":fields.String,
	"instragram_link":fields.String,
	"privacy_and_return_policy":fields.String,
	"about_user":fields.String,
	"ask_for_phone_no":fields.Integer,
	"allow_order_in_whats_app":fields.Integer,
	"app_link":fields.String,
	"whatsapp_no":fields.String
})

organisation_details_postmodel = api.model('organisationDetails',{	
	"phoneno":fields.Integer(required=True),
	"organization_name":fields.String(required=True),
	"owner_name":fields.String,
	"address":fields.String,
	"email":fields.String(required=True),
	"retailer_code":fields.String(required=True),
	"slab":fields.String,
	"slab_amount":fields.Integer,
	"days":fields.String,
	"activation_volume":fields.String,
	"customize_mobile_protection_app":fields.String,
	"customize_web_portal":fields.String,
	"app_notification_to_customer":fields.String,
	"email_to_customer":fields.String,
	"sms_to_customer":fields.String,
	"personal_website_1_page":fields.String,	
	"one_logo_one_time": fields.String,
	"enroll_attachment": fields.String
})

update_stock_management_settings_model = api.model('update_stock_management_settings_model',{
	"setting_value":fields.Integer
})

update_signup_settings_model = api.model('signup_settings_postmodel',{	
	"is_mandatory":fields.Integer
})

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#----------------------Check-Phone-No-Exist---------------------#

@name_space.route("/CheckPhoneno")	
class CheckPhoneno(Resource):
	@api.expect(checkphoneno_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `organisation_master` WHERE `phoneno` = %s """)
		getData = (details['phoneno'])
		count_customer = cursor.execute(get_query,getData)

		connection.commit()
		cursor.close()

		if count_customer > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "organisation_details",
			    		"status": "error",
			    		"message":"Organisation Already Exist"
			    	},
			    	"responseList":{"phoneno":details['phoneno']} }), status.HTTP_200_OK

		else:
			return ({"attributes": {
		    		"status_desc": "organization_details",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList":{"phoneno":details['phoneno']}}), status.HTTP_200_OK

		

#----------------------Check-Phone-No-Exist---------------------#

#----------------------Add-Organisation---------------------#

@name_space.route("/AddOrganisation")
class AddOrganisation(Resource):
	@api.expect(organisation_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		email = details['email']
		phoneno = details['phoneno']	
		organisation_status = 1	
		registration_type = details['registration_type']

		if registration_type == 4:
			get_phone_query = ("""SELECT *
					FROM `organisation_master` WHERE `phoneno` = %s and `registration_type` = %s""")
			get_phone_data = (phoneno,registration_type)

			count_phone = cursor.execute(get_phone_query,get_phone_data)

			if count_phone > 0:
				get_query_login_data = ("""SELECT *					
						FROM `organisation_master`					
						WHERE `phoneno` = %s """)
				getDataLogin = (phoneno)
				cursor.execute(get_query_login_data,getDataLogin)
				login_data = cursor.fetchone()

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

				login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
				login_data['last_update_ts'] = str(login_data['last_update_ts'])

				if login_data['organization_name'] :
					login_data['personal_website_link'] = login_data['personal_website_link']
				else:
					login_data['personal_website_link'] = ""

				login_data['is_head_office_login'] = 1

				get_retail_store_query = ("""SELECT * FROM `retailer_store_stores` rss								
										where rss.`organisation_id` = %s""")
				get_retail_store_data = (login_data['organisation_id'])
				count_retail_store_data =  cursor.execute(get_retail_store_query,get_retail_store_data)

				if count_retail_store_data > 0:
					login_data['is_retail_store'] = 1
				else:
					login_data['is_retail_store'] = 0

			else:

				insert_query = ("""INSERT INTO `organisation_master`(`phoneno`,`status`,`registration_type`) 
								VALUES(%s,%s,%s)""")
				data = (phoneno,organisation_status,registration_type)
				cursor.execute(insert_query,data)
				organisation_id = cursor.lastrowid	

				otp_setting_value = 1
				insert_query_otp_settings = ("""INSERT INTO `otp_settings`(`otp_setting_value`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
				data_otp_settings = (otp_setting_value,organisation_id,organisation_id)
				cursor.execute(insert_query_otp_settings,data_otp_settings)

				is_mandatory = 0
				insert_query_signup_settings = ("""INSERT INTO `signup_settings`(`is_mandatory`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
				data_signup_settings = (is_mandatory,organisation_id,organisation_id)
				cursor.execute(insert_query_signup_settings,data_signup_settings)

				get_query_login_data = ("""SELECT *				
									FROM `organisation_master`						
									WHERE `organisation_id` = %s """)
				getDataLogin = (organisation_id)
				cursor.execute(get_query_login_data,getDataLogin)
				login_data = cursor.fetchone()

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

				login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
				login_data['last_update_ts'] = str(login_data['last_update_ts'])
				login_data['personal_website_link'] = login_data['personal_website_link']
				login_data['is_head_office_login'] = 1

				login_data['is_head_office_login'] = 1

				get_retail_store_query = ("""SELECT * FROM `retailer_store_stores` rss								
										where rss.`organisation_id` = %s""")
				get_retail_store_data = (organisation_id)
				count_retail_store_data =  cursor.execute(get_retail_store_query,get_retail_store_data)

				if count_retail_store_data > 0:
					login_data['is_retail_store'] = 1
				else:
					login_data['is_retail_store'] = 0
		else:
			get_query = ("""SELECT `email`
				FROM `organisation_master` WHERE `email` = %s """)

			getData = (email)
			
			count_email = cursor.execute(get_query,getData)			

			if count_email > 0:
				connection.commit()
				cursor.close()

				return ({"attributes": {
				    		"status_desc": "organisation_details",
				    		"status": "error",
				    		"message":"Email Already Exist"
				    	},
				    	"responseList":{} }), status.HTTP_200_OK
			else:
				get_query_phone = ("""SELECT *
				FROM `organisation_master` WHERE `phoneno` = %s""")
				getDataPhone = (details['phoneno'])
				count_customer_phone = cursor.execute(get_query_phone,getDataPhone)

				
				if count_customer_phone > 0:
					connection.commit()
					cursor.close()

					return ({"attributes": {
					    		"status_desc": "organisation_details",
					    		"status": "error",
					    		"message":"Phone No Already Exist"
					    	},
					    	"responseList":{} }), status.HTTP_200_OK
				else:
					insert_query = ("""INSERT INTO `organisation_master`(`email`,`phoneno`,`status`,`registration_type`) 
								VALUES(%s,%s,%s,%s)""")
					data = (email,phoneno,organisation_status,registration_type)
					cursor.execute(insert_query,data)
					organisation_id = cursor.lastrowid	

					otp_setting_value = 1
					insert_query_otp_settings = ("""INSERT INTO `otp_settings`(`otp_setting_value`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
					data_otp_settings = (otp_setting_value,organisation_id,organisation_id)
					cursor.execute(insert_query_otp_settings,data_otp_settings)

					get_query_login_data = ("""SELECT *				
										FROM `organisation_master`						
										WHERE `organisation_id` = %s """)
					getDataLogin = (organisation_id)
					cursor.execute(get_query_login_data,getDataLogin)
					login_data = cursor.fetchone()

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

					login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
					login_data['last_update_ts'] = str(login_data['last_update_ts'])

					if login_data['organization_name'] :
						login_data['personal_website_link'] = login_data['personal_website_link']
					else:
						login_data['personal_website_link'] = ""

					login_data['is_head_office_login'] = 1

					get_retail_store_query = ("""SELECT * FROM `retailer_store_stores` rss								
										where rss.`organisation_id` = %s""")
					get_retail_store_data = (organisation_id)
					count_retail_store_data =  cursor.execute(get_retail_store_query,get_retail_store_data)

					if count_retail_store_data > 0:
						login_data['is_retail_store'] = 1
					else:
						login_data['is_retail_store'] = 0



		if details and "device_token" in details:
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			saveDeviceTokenUrl = BASE_URL + "ret_notification/RetailerNotification/AddOrganisationDeviceDetails"
			payloadpushData = {
				"device_type":"android",
				"device_token":details['device_token'],
				"organisation_id": login_data['organisation_id']
			}

			saveDeviceToken = requests.post(saveDeviceTokenUrl,data=json.dumps(payloadpushData), headers=headers).json()
					
		if 	login_data['organisation_id']:
			url = BASE_URL+"ecommerce_autopopulation/EcommerceAutopopulation/copyLocation"
			post_data = {
						  "organisation_id": login_data['organisation_id']
						}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(url, data=json.dumps(post_data), headers=headers).json()

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "organisation_details",
				    "status": "success"
				},
				"responseList":login_data}), status.HTTP_200_OK	

#----------------------Add-Organisation---------------------#	

#----------------------Add-Organisation-Details----------------------#

@name_space.route("/AddOrganisationDetails")
class AddOrganisationDetails(Resource):
	@api.expect(organisation_details_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		phoneno = details['phoneno']
		organization_name = details['organization_name']
		organisation_status = 1
		registration_type = 4
		email = details['email']
		org_password = details['phoneno']
		slab = details['slab']
		slab_amount = details['slab_amount']
		days = details['days']
		activation_volume = details['activation_volume']
		customize_mobile_protection_app = details['customize_mobile_protection_app']
		customize_web_portal = details['customize_web_portal']
		app_notification_to_customer =  details['app_notification_to_customer']
		email_to_customer = details['email_to_customer']
		sms_to_customer =  details['sms_to_customer']
		personal_website_1_page =  details['personal_website_1_page']
		retailer_code = details['retailer_code']
		enroll_attachment = details['enroll_attachment']
		one_logo_one_time = details['one_logo_one_time']
		owner_name = details['owner_name']
		address = details['address']

		get_phone_query = ("""SELECT *
					FROM `organisation_master` WHERE `phoneno` = %s and `registration_type` = %s""")
		get_phone_data = (phoneno,registration_type)

		count_phone = cursor.execute(get_phone_query,get_phone_data)

		if count_phone > 0:
			return ({"attributes": {
			    		"status_desc": "organisation_details",
			    		"status": "error",
			    		"message":"Phone No Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK
		else:
			insert_query = ("""INSERT INTO `organisation_master`(`organization_name`,`email`,`org_password`,`phoneno`,`status`,`registration_type`) 
								VALUES(%s,%s,%s,%s,%s,%s)""")
			data = (organization_name,email,phoneno,phoneno,organisation_status,registration_type)
			cursor.execute(insert_query,data)
			organisation_id = cursor.lastrowid

			insert_detail_query = ("""INSERT INTO `organisation_details`(`organisation_id`,`owner_name`,`address`,`slab`,`slab_amount`,`days`,`activation_volume`,`customize_mobile_protection_app`,`customize_web_portal`,
				`app_notification_to_customer`,`email_to_customer`,`sms_to_customer`,`personal_website_1_page`,`enroll_attachment`,`one_logo_one_time`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			data_detail = (organisation_id,owner_name,address,slab,slab_amount,days,activation_volume,customize_mobile_protection_app,customize_web_portal,app_notification_to_customer,email_to_customer,sms_to_customer,personal_website_1_page,enroll_attachment,one_logo_one_time)
			cursor.execute(insert_detail_query,data_detail)

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		Url = "http://techdrive.xyz/ecommerce-app/test.php?organisation_id="+str(organisation_id)
		payload = {  					
  					"organization_name": organization_name  					
				  }
		update_organisation = requests.post(Url,data=json.dumps(payload), headers=headers).json()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		Urlt = "http://meprotectwebsrvc.techdrive.xyz/register.php?action=retailerLogin&ret_id="+retailer_code+"&username="+email+"&password="+str(phoneno)+"&ret_name="+organization_name+"&dis_phone="+str(phoneno)
		
		regis_tech = requests.get(Urlt).json()

		print(regis_tech)

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "organisation_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK	

#----------------------Add-Organisation-Details----------------------#


#----------------------Update-Organisation-Information---------------------#

@name_space.route("/updateOrganisationInformation/<int:organisation_id>")
class updateOrganisationInformation(Resource):
	@api.expect(organisation_putmodel)
	def put(self, organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()


		if details and "organization_name" in details:
			organization_name = details['organization_name']
			get_organisation_query = ("""SELECT *
					FROM `organisation_master` WHERE `organization_name` = %s""")
			get_organisation_data = (organization_name)
			count_organisation = cursor.execute(get_organisation_query,get_organisation_data)

			if count_organisation > 0:
				get_organisation_query_with_id = ("""SELECT *
					FROM `organisation_master` WHERE `organization_name` = %s and `organisation_id` = %s""")
				get_organisation_data_with_id = (organization_name,organisation_id)
				count_organisation_with_id = cursor.execute(get_organisation_query_with_id,get_organisation_data_with_id)

				if count_organisation_with_id > 0:
					server_name = details['server_name']
					organisation_code = organization_name.replace(" ","-")
					personal_website_link = server_name+"/ecommerce-app/"+organisation_code
					update_query = ("""UPDATE `organisation_master` SET `organization_name` = %s, `organisation_code` = %s, `personal_website_link` = %s
					WHERE `organisation_id` = %s """)
					update_data = (organization_name,organisation_code,personal_website_link,organisation_id)
					cursor.execute(update_query,update_data)
				else:
					return ({"attributes": {
					    		"status_desc": "organisation_details",
					    		"status": "error",
					    		"message":"Organisation Name Already Exist"
					    	},
					    	"responseList":{} }), status.HTTP_200_OK
			else:
				server_name = details['server_name']
				organisation_code = organization_name.replace(" ","-")
				personal_website_link = server_name+"/ecommerce-app/"+organisation_code
				update_query = ("""UPDATE `organisation_master` SET `organization_name` = %s, `organisation_code` = %s, `personal_website_link` = %s
					WHERE `organisation_id` = %s """)
				update_data = (organization_name,organisation_code,personal_website_link,organisation_id)
				cursor.execute(update_query,update_data)

		if details and "logo" in details:
			logo = details['logo']
			update_query = ("""UPDATE `organisation_master` SET `logo` = %s
				WHERE `organisation_id` = %s """)
			update_data = (logo,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "phoneno" in details:
			phoneno = details['phoneno']
			update_query = ("""UPDATE `organisation_master` SET `phoneno` = %s
				WHERE `organisation_id` = %s """)
			update_data = (phoneno,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "email" in details:
			email = details['email']
			update_query = ("""UPDATE `organisation_master` SET `email` = %s
				WHERE `organisation_id` = %s """)
			update_data = (email,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "area" in details:
			area = details['area']
			update_query = ("""UPDATE `organisation_master` SET `area` = %s
				WHERE `organisation_id` = %s """)
			update_data = (area,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "city" in details:
			city = details['city']
			update_query = ("""UPDATE `organisation_master` SET `city` = %s
				WHERE `organisation_id` = %s """)
			update_data = (city,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "pincode" in details:
			pincode = details['pincode']
			update_query = ("""UPDATE `organisation_master` SET `pincode` = %s
				WHERE `organisation_id` = %s """)
			update_data = (pincode,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "gst_number" in details:
			gst_number = details['gst_number']
			update_query = ("""UPDATE `organisation_master` SET `gst_number` = %s
				WHERE `organisation_id` = %s """)
			update_data = (gst_number,organisation_id)
			cursor.execute(update_query,update_data)		

		if details and "currency" in details:
			currency = details['currency']
			update_query = ("""UPDATE `organisation_master` SET `currency` = %s
				WHERE `organisation_id` = %s """)
			update_data = (currency,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "facebook_link" in details:
			facebook_link = details['facebook_link']
			update_query = ("""UPDATE `organisation_master` SET `facebook_link` = %s
				WHERE `organisation_id` = %s """)
			update_data = (facebook_link,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "instragram_link" in details:
			instragram_link = details['instragram_link']
			update_query = ("""UPDATE `organisation_master` SET `instragram_link` = %s
				WHERE `organisation_id` = %s """)
			update_data = (instragram_link,organisation_id)
			cursor.execute(update_query,update_data)	

		if details and "privacy_and_return_policy" in details:
			privacy_and_return_policy = details['privacy_and_return_policy']
			update_query = ("""UPDATE `organisation_master` SET `privacy_and_return_policy` = %s
				WHERE `organisation_id` = %s """)
			update_data = (privacy_and_return_policy,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "about_user" in details:
			about_user = details['about_user']
			update_query = ("""UPDATE `organisation_master` SET `about_user` = %s
				WHERE `organisation_id` = %s """)
			update_data = (about_user,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "ask_for_phone_no" in details:
			ask_for_phone_no = details['ask_for_phone_no']
			update_query = ("""UPDATE `organisation_master` SET `ask_for_phone_no` = %s
				WHERE `organisation_id` = %s """)
			update_data = (ask_for_phone_no,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "allow_order_in_whats_app" in details:
			allow_order_in_whats_app = details['allow_order_in_whats_app']
			update_query = ("""UPDATE `organisation_master` SET `allow_order_in_whats_app` = %s
				WHERE `organisation_id` = %s """)
			update_data = (allow_order_in_whats_app,organisation_id)
			cursor.execute(update_query,update_data)		

		if details and "app_link" in details:
			app_link = details['app_link']
			update_query = ("""UPDATE `organisation_master` SET `app_link` = %s
				WHERE `organisation_id` = %s """)
			update_data = (app_link,organisation_id)
			cursor.execute(update_query,update_data)	

		if details and "whatsapp_no" in details:
			whatsapp_no = details['whatsapp_no']
			update_query = ("""UPDATE `organisation_master` SET `whatsapp_no` = %s
				WHERE `organisation_id` = %s """)
			update_data = (whatsapp_no,organisation_id)
			cursor.execute(update_query,update_data)

		get_query_login_data = ("""SELECT *				
									FROM `organisation_master`						
									WHERE `organisation_id` = %s """)
		getDataLogin = (organisation_id)
		cursor.execute(get_query_login_data,getDataLogin)
		login_data = cursor.fetchone()

		login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
		login_data['last_update_ts'] = str(login_data['last_update_ts'])

		if login_data['organization_name'] :
			login_data['personal_website_link'] = login_data['personal_website_link']
		else:
			login_data['personal_website_link'] = ""
		

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "organisation_details",
				    "status": "success"
				},
				"responseList":login_data}), status.HTTP_200_OK

#----------------------Update-Organisation-Information---------------------#	

#----------------------Update-Organisation-Information---------------------#

@name_space.route("/updateOrganisationInformationtest/<int:organisation_id>")
class updateOrganisationInformationtest(Resource):
	@api.expect(organisation_putmodel)
	def put(self, organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()


		if details and "organization_name" in details:
			organization_name = details['organization_name']
			get_organisation_query = ("""SELECT *
					FROM `organisation_master` WHERE `organization_name` = %s""")
			get_organisation_data = (organization_name)
			count_organisation = cursor.execute(get_organisation_query,get_organisation_data)

			if count_organisation > 0:
				get_organisation_query_with_id = ("""SELECT *
					FROM `organisation_master` WHERE `organization_name` = %s and `organisation_id` = %s""")
				get_organisation_data_with_id = (organization_name,organisation_id)
				count_organisation_with_id = cursor.execute(get_organisation_query_with_id,get_organisation_data_with_id)

				if count_organisation_with_id > 0:
					server_name = details['server_name']
					organisation_code = organization_name.replace(" ","-")
					personal_website_link = server_name+"/ecommerce-webapp/"+organisation_code
					update_query = ("""UPDATE `organisation_master` SET `organization_name` = %s, `organisation_code` = %s, `personal_website_link` = %s
					WHERE `organisation_id` = %s """)
					update_data = (organization_name,organisation_code,personal_website_link,organisation_id)
					cursor.execute(update_query,update_data)
				else:
					return ({"attributes": {
					    		"status_desc": "organisation_details",
					    		"status": "error",
					    		"message":"Organisation Name Already Exist"
					    	},
					    	"responseList":{} }), status.HTTP_200_OK
			else:
				server_name = details['server_name']
				organisation_code = organization_name.replace(" ","-")
				personal_website_link = server_name+"/ecommerce-webapp/"+organisation_code
				update_query = ("""UPDATE `organisation_master` SET `organization_name` = %s, `organisation_code` = %s, `personal_website_link` = %s
					WHERE `organisation_id` = %s """)
				update_data = (organization_name,organisation_code,personal_website_link,organisation_id)
				cursor.execute(update_query,update_data)

		if details and "logo" in details:
			logo = details['logo']
			update_query = ("""UPDATE `organisation_master` SET `logo` = %s
				WHERE `organisation_id` = %s """)
			update_data = (logo,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "phoneno" in details:
			phoneno = details['phoneno']
			update_query = ("""UPDATE `organisation_master` SET `phoneno` = %s
				WHERE `organisation_id` = %s """)
			update_data = (phoneno,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "email" in details:
			email = details['email']
			update_query = ("""UPDATE `organisation_master` SET `email` = %s
				WHERE `organisation_id` = %s """)
			update_data = (email,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "area" in details:
			area = details['area']
			update_query = ("""UPDATE `organisation_master` SET `area` = %s
				WHERE `organisation_id` = %s """)
			update_data = (area,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "city" in details:
			city = details['city']
			update_query = ("""UPDATE `organisation_master` SET `city` = %s
				WHERE `organisation_id` = %s """)
			update_data = (city,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "pincode" in details:
			pincode = details['pincode']
			update_query = ("""UPDATE `organisation_master` SET `pincode` = %s
				WHERE `organisation_id` = %s """)
			update_data = (pincode,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "gst_number" in details:
			gst_number = details['gst_number']
			update_query = ("""UPDATE `organisation_master` SET `gst_number` = %s
				WHERE `organisation_id` = %s """)
			update_data = (gst_number,organisation_id)
			cursor.execute(update_query,update_data)		

		if details and "currency" in details:
			currency = details['currency']
			update_query = ("""UPDATE `organisation_master` SET `currency` = %s
				WHERE `organisation_id` = %s """)
			update_data = (currency,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "facebook_link" in details:
			facebook_link = details['facebook_link']
			update_query = ("""UPDATE `organisation_master` SET `facebook_link` = %s
				WHERE `organisation_id` = %s """)
			update_data = (facebook_link,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "instragram_link" in details:
			instragram_link = details['instragram_link']
			update_query = ("""UPDATE `organisation_master` SET `instragram_link` = %s
				WHERE `organisation_id` = %s """)
			update_data = (instragram_link,organisation_id)
			cursor.execute(update_query,update_data)	

		if details and "privacy_and_return_policy" in details:
			privacy_and_return_policy = details['privacy_and_return_policy']
			update_query = ("""UPDATE `organisation_master` SET `privacy_and_return_policy` = %s
				WHERE `organisation_id` = %s """)
			update_data = (privacy_and_return_policy,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "about_user" in details:
			about_user = details['about_user']
			update_query = ("""UPDATE `organisation_master` SET `about_user` = %s
				WHERE `organisation_id` = %s """)
			update_data = (about_user,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "ask_for_phone_no" in details:
			ask_for_phone_no = details['ask_for_phone_no']
			update_query = ("""UPDATE `organisation_master` SET `ask_for_phone_no` = %s
				WHERE `organisation_id` = %s """)
			update_data = (ask_for_phone_no,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "allow_order_in_whats_app" in details:
			allow_order_in_whats_app = details['allow_order_in_whats_app']
			update_query = ("""UPDATE `organisation_master` SET `allow_order_in_whats_app` = %s
				WHERE `organisation_id` = %s """)
			update_data = (allow_order_in_whats_app,organisation_id)
			cursor.execute(update_query,update_data)			

		get_query_login_data = ("""SELECT *				
									FROM `organisation_master`						
									WHERE `organisation_id` = %s """)
		getDataLogin = (organisation_id)
		cursor.execute(get_query_login_data,getDataLogin)
		login_data = cursor.fetchone()

		login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
		login_data['last_update_ts'] = str(login_data['last_update_ts'])

		if login_data['organization_name'] :
			login_data['personal_website_link'] = login_data['personal_website_link']
		else:
			login_data['personal_website_link'] = ""
		

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "organisation_details",
				    "status": "success"
				},
				"responseList":login_data}), status.HTTP_200_OK

#----------------------Update-Organisation-Information---------------------#	


#----------------------Get-Organisation---------------------#
@name_space.route("/organisationDetails/<int:organisation_id>")	
class organisationDetails(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query_login_data = ("""SELECT *				
									FROM `organisation_master`						
									WHERE `organisation_id` = %s """)
		getDataLogin = (organisation_id)
		cursor.execute(get_query_login_data,getDataLogin)
		login_data = cursor.fetchone()

		get_otp_settings_query = ("""SELECT *				
									FROM `otp_settings`						
									WHERE `organisation_id` = %s """)
		count_otp_setings = cursor.execute(get_otp_settings_query,getDataLogin)

		if count_otp_setings > 0:
			otp_settings_data = cursor.fetchone()
			login_data['otp_sent'] = otp_settings_data['otp_setting_value']
		else:
			login_data['otp_sent'] = 0

		login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
		login_data['last_update_ts'] = str(login_data['last_update_ts'])

		if login_data['organization_name'] :
			login_data['organisation_profile_complete_status'] = 1
			login_data['personal_website_link'] = login_data['personal_website_link']
		else:
			login_data['organisation_profile_complete_status'] = 0
			login_data['personal_website_link'] = ""

		get_query =  ("""SELECT rss.`retailer_store_store_id`,rs.`city`,rsi.`image`,rss.`store_name`,rss.`address`,rss.`latitude`,rss.`longitude`,rss.`phoneno`
			FROM `retailer_store_stores` rss 
			INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = rss.`retailer_store_id`
			INNER JOIN `retailer_store_image` rsi ON rsi.`retailer_store_id` = rss.`retailer_store_id`
			where rss.`organisation_id` = %s""")	
		get_data = (organisation_id)
		count_retailer = cursor.execute(get_query,get_data)

		if count_retailer > 0:
			retailer_data = cursor.fetchall()
			login_data['retail_store'] = retailer_data
		else:
			retailer_data = []
			login_data['retail_store'] = retailer_data

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


		return ({"attributes": {
				    "status_desc": "organisation_details",
				    "status": "success"
				},
				"responseList":login_data}), status.HTTP_200_OK
#----------------------Get-Organisation---------------------#	

#----------------------Get-Organisation---------------------#
@name_space.route("/organisationList")	
class organisationList(Resource):
	def get(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *				
									FROM `organisation_master`""")		
		cursor.execute(get_query)
		organisation_data = cursor.fetchall()

		for key,data in enumerate(organisation_data):
			organisation_data[key]['date_of_lastlogin'] = str(data['date_of_lastlogin'])
			organisation_data[key]['last_update_ts'] = str(data['last_update_ts'])	


		return ({"attributes": {
				    "status_desc": "organisation_details",
				    "status": "success"
				},
				"responseList":organisation_data}), status.HTTP_200_OK
#----------------------Get-Organisation---------------------#	


#----------------------Get-Currency-List---------------------#
@name_space.route("/currencyList")	
class currencyList(Resource):
	def get(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *				
									FROM `currency_master`""")
		cursor.execute(get_query)
		currency_data = cursor.fetchall()

		for key,data in  enumerate(currency_data):		
			currency_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
				    "status_desc": "currency_list",
				    "status": "success"
				},
				"responseList":currency_data}), status.HTTP_200_OK
#----------------------Get-Currency-List---------------------#	

#----------------------Update-Otp-Settings---------------------#

@name_space.route("/UpdateStockManagementSettings/<int:organisation_id>")
class UpdateOtpSettings(Resource):
	@api.expect(update_stock_management_settings_model)
	def put(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "setting_value" in details:
			setting_value = details['setting_value']
			get_stock_management_settings_query = ("""SELECT *				
									FROM `stock_management_settings`						
									WHERE `organisation_id` = %s """)
			getDataStockManagementSettings = (organisation_id)
			count_stock_management_setings = cursor.execute(get_stock_management_settings_query,getDataStockManagementSettings)

			if count_stock_management_setings > 0:									
				update_query = ("""UPDATE `stock_management_settings` SET `setting_value` = %s
						WHERE `organisation_id` = %s """)
				update_data = (setting_value,organisation_id)
				cursor.execute(update_query,update_data)
			else:
				if setting_value == 1:
					insert_query = ("""INSERT INTO `stock_management_settings`(`setting_value`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
					data = (setting_value,organisation_id,organisation_id)
					cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Otp Settings",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Otp-Settings---------------------#

#----------------------Organisation-Login---------------------#

@name_space.route("/organisationLogin")
class organisationLogin(Resource):
	@api.expect(organisation_login_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()
		
		phoneno = details['phoneno']
		
		get_phone_query = ("""SELECT *
					FROM `organisation_master` WHERE `phoneno` = %s """)
		get_phone_data = (phoneno)

		count_phone = cursor.execute(get_phone_query,get_phone_data)

		if count_phone > 0:
			get_query_login_data = ("""SELECT *					
						FROM `organisation_master`					
						WHERE `phoneno` = %s """)
			getDataLogin = (phoneno)
			cursor.execute(get_query_login_data,getDataLogin)
			login_data = cursor.fetchone()

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

			login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
			login_data['last_update_ts'] = str(login_data['last_update_ts'])

			if login_data['organization_name'] :
				login_data['personal_website_link'] = login_data['personal_website_link']
			else:
				login_data['personal_website_link'] = ""

			if details and "device_token" in details:
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				saveDeviceTokenUrl = BASE_URL + "ret_notification/RetailerNotification/AddOrganisationDeviceDetails"
				payloadpushData = {
					"device_type":"android",
					"device_token":details['device_token'],
					"organisation_id": login_data['organisation_id']
				}

				saveDeviceToken = requests.post(saveDeviceTokenUrl,data=json.dumps(payloadpushData), headers=headers).json()
		

			connection.commit()
			cursor.close()

			return ({"attributes": {
					    "status_desc": "organisation_details",
					    "status": "success"
					},
					"responseList":login_data}), status.HTTP_200_OK
		else:

			login_data = {}

			return ({"attributes": {
					    "status_desc": "organisation_details",
					    "status": "error"
					},
					"responseList":login_data}), status.HTTP_200_OK

#----------------------Organisation-Login---------------------#


#----------------------Update-SignUp-Settings---------------------#

@name_space.route("/UpdateSignUpSettings/<int:organisation_id>")
class UpdateSignUpSettings(Resource):
	@api.expect(update_signup_settings_model)
	def put(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "is_mandatory" in details:
			is_mandatory = details['is_mandatory']
			get_signup_settings_query = ("""SELECT *				
									FROM `signup_settings`						
									WHERE `organisation_id` = %s """)
			getData = (organisation_id)
			count_signup_setings = cursor.execute(get_signup_settings_query,getData)

			if count_signup_setings > 0:									
				update_query = ("""UPDATE `signup_settings` SET `is_mandatory` = %s
						WHERE `organisation_id` = %s """)
				update_data = (is_mandatory,organisation_id)
				cursor.execute(update_query,update_data)
			else:
				if is_mandatory == 1:
					insert_query = ("""INSERT INTO `signup_settings`(`is_mandatory`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
					data = (is_mandatory,organisation_id,organisation_id)
					cursor.execute(insert_query,data)
				else:
					is_mandatory = 0
					insert_query = ("""INSERT INTO `signup_settings`(`is_mandatory`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
					data = (is_mandatory,organisation_id,organisation_id)
					cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Signup Settings",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Otp-Settings---------------------#

