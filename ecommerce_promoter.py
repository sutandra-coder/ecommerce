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

ecommerce_promoter = Blueprint('ecommerce_promoter_api', __name__)
api = Api(ecommerce_promoter,  title='Ecommerce Promoter API',description='Ecommerce Promoter API')

name_space = api.namespace('EcommercePromoter',description='Ecommerce Promoter')
name_space_order_history = api.namespace('OrderHistoryWithPromoter',description='Order History With Promoter')
name_space_loyality_dashboard = api.namespace('LoyalityDashboardWithPromoter',description='Loyality Dashboard With Promoter')
name_space_offer = api.namespace('OfferWithPromoter',description='Offer With Promoter')
name_space_enquiry = api.namespace('EnquiryWithPromoter',description='Enquiry With Promoter')
name_space_exchange = api.namespace('ExchangeWithPromoter',description='Exchange With Promoter')
name_space_missopportunity = api.namespace('MissopportunityWithPromoter',description='Miss Opportunity With Promoter')
name_space_emi = api.namespace('EmiWithPromoter',description='Emi With Promoter')
name_space_catalouge = api.namespace('CatalougeWithPromoter',description='Catalouge With Promoter')
name_space_product = api.namespace('ProductWithPromoter',description='Product With Promoter')

login_postmodel = api.model('loginPostmodel',{
	"phoneno":fields.String(required=True)
})

promoter_login_postmodel = api.model('promoterloginPostmodel',{
	"phoneno":fields.String(required=True)
})


promoter_postmodel = api.model('promoter_postmodel',{
	"promoter_name":fields.String(required=True),
	"phoneno":fields.String(required=True),
	"brand_id":fields.Integer(required=True),
	"brand_name":fields.String(required=True),
	"retailer_store_store_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

promoter_putmodel = api.model('promoter_putmodel',{
	"pstatus": fields.Integer(required=True)
})


#----------------------Promoter-Login---------------------#

@name_space.route("/Login")	
class Login(Resource):
	@api.expect(login_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		phoneno = details['phoneno']

		get_query = ("""SELECT * FROM `promoter` where `phoneno` = %s and `status` = 1""")
		get_data = (phoneno)
		count_promoter = cursor.execute(get_query,get_data)

		if count_promoter >0:
			login_data = cursor.fetchone()
			print(login_data)

			get_store_query = ("""SELECT * FROM `retailer_store_stores` rss
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = rs.`retailer_store_id`
								INNER JOIN `retailer_store_image` rsi ON rsi.`retailer_store_id` = rs.`retailer_store_id`
								where rss.`retailer_store_store_id` = %s""")
			get_store_data = (login_data['retailer_store_store_id'])
			count_store_data =  cursor.execute(get_store_query,get_store_data)
			if count_store_data > 0:
				store_data = cursor.fetchone()
				login_data['retailer_store_id'] = store_data['retailer_store_id']
				login_data['store_name'] = store_data['store_name']
				login_data['address'] = store_data['address']
				login_data['latitude'] = store_data['latitude']
				login_data['longitude'] = store_data['longitude']
				login_data['store_phoneno'] = store_data['phoneno']
				login_data['store_city'] = store_data['city']
				login_data['image'] = store_data['image']
			else:
				login_data['city'] = ""
				login_data['image'] = ""

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
			login_data['facebook_link'] = organisation_login_data['facebook_link']
			login_data['instragram_link'] = organisation_login_data['instragram_link']
			login_data['privacy_and_return_policy'] = organisation_login_data['privacy_and_return_policy']
			login_data['about_user'] = organisation_login_data['about_user']
			login_data['ask_for_phone_no'] = organisation_login_data['ask_for_phone_no']
			login_data['allow_order_in_whats_app'] = organisation_login_data['allow_order_in_whats_app']
			login_data['registration_type'] = organisation_login_data['registration_type']
			login_data['organisation_code'] = organisation_login_data['organisation_code']
			login_data['whatsapp_no'] = organisation_login_data['whatsapp_no']
			login_data['app_link'] = organisation_login_data['app_link']
			login_data['is_head_office_login'] = 0

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

			login_data['last_update_ts'] = str(login_data['last_update_ts'])
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
			
#----------------------Promoter-Login---------------------#

#----------------------Promoter-Login---------------------#

@name_space.route("/PromoterLogin")	
class PromoterLogin(Resource):
	@api.expect(promoter_login_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		phoneno = details['phoneno']

		get_query = ("""SELECT * FROM `promoter` where `phoneno` = %s and `status` = 1""")
		get_data = (phoneno)
		count_promoter = cursor.execute(get_query,get_data)

		if count_promoter >0:
			login_data = cursor.fetchone()
			print(login_data)

			get_store_query = ("""SELECT * FROM `retailer_store_stores` rss
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = rss.`retailer_store_id`
								INNER JOIN `retailer_store_image` rsi ON rsi.`retailer_store_id` = rs.`retailer_store_id`
								where rss.`retailer_store_store_id` = %s""")
			get_store_data = (login_data['retailer_store_store_id'])
			count_store_data =  cursor.execute(get_store_query,get_store_data)
			if count_store_data > 0:
				store_data = cursor.fetchone()
				login_data['retailer_store_id'] = store_data['retailer_store_id']
				login_data['store_name'] = store_data['store_name']
				login_data['address'] = store_data['address']
				login_data['latitude'] = store_data['latitude']
				login_data['longitude'] = store_data['longitude']
				login_data['store_phoneno'] = store_data['phoneno']
				login_data['store_city'] = store_data['city']
				login_data['image'] = store_data['image']
			else:
				login_data['city'] = ""
				login_data['image'] = ""

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
			login_data['facebook_link'] = organisation_login_data['facebook_link']
			login_data['instragram_link'] = organisation_login_data['instragram_link']
			login_data['privacy_and_return_policy'] = organisation_login_data['privacy_and_return_policy']
			login_data['about_user'] = organisation_login_data['about_user']
			login_data['ask_for_phone_no'] = organisation_login_data['ask_for_phone_no']
			login_data['allow_order_in_whats_app'] = organisation_login_data['allow_order_in_whats_app']
			login_data['registration_type'] = organisation_login_data['registration_type']
			login_data['organisation_code'] = organisation_login_data['organisation_code']
			login_data['whatsapp_no'] = organisation_login_data['whatsapp_no']
			login_data['app_link'] = organisation_login_data['app_link']
			login_data['is_head_office_login'] = 3

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

			login_data['last_update_ts'] = str(login_data['last_update_ts'])
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
			
#----------------------Promoter-Login---------------------#

#----------------------Promoter-List---------------------#

@name_space.route("/gePromoterListByOrganisationIdAndRetailStoreId/<int:organisation_id>/<int:retailer_store_store_id>")	
class gePromoterListByOrganisationIdAndRetailStoreId(Resource):
	def get(self,organisation_id,retailer_store_store_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT * FROM `promoter` where `organisation_id` = %s and `retailer_store_store_id` = %s""")	
		get_data = (organisation_id,retailer_store_store_id)
		cursor.execute(get_query,get_data)
		promoter_data = cursor.fetchall()

		for key,data in enumerate(promoter_data):
			promoter_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "promoter_details",
		    		"status": "success"
		    	},
		    	"responseList":promoter_data}), status.HTTP_200_OK	

#----------------------Promoter-List---------------------#

#----------------------Promoter-List---------------------#

@name_space.route("/gePromoterListByOrganisationId/<int:organisation_id>")	
class gePromoterListByOrganisationId(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT p.*,rss.`store_name`,rss.`address` FROM `promoter` p
						INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = p.`retailer_store_store_id`
			where p.`organisation_id` = %s """)	
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)
		promoter_data = cursor.fetchall()

		for key,data in enumerate(promoter_data):
			promoter_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "promoter_details",
		    		"status": "success"
		    	},
		    	"responseList":promoter_data}), status.HTTP_200_OK	

#----------------------Promoter-List---------------------#

#----------------------Add-Promoter---------------------#

@name_space.route("/addPromoter")	
class addPromoter(Resource):
	@api.expect(promoter_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		promoter_name = details['promoter_name']
		phoneno =  details['phoneno']
		brand_name =  details['brand_name']
		brand_id = details['brand_id']
		retailer_store_store_id = details['retailer_store_store_id']
		organisation_id = details['organisation_id']
		pstatus = 1

		get_query = ("""SELECT *
			FROM `promoter` WHERE `phoneno` = %s """)
		getData = (phoneno)
		count_promoter = cursor.execute(get_query,getData)

		if count_promoter > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "promoter_details",
			    		"status": "error",
			    		"message":"Phone No Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK
		else:
			insert_query = ("""INSERT INTO `promoter`(`promoter_name`,`phoneno`,`brand_id`,`brand_name`,`retailer_store_store_id`,`organisation_id`,`status`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
			data = (promoter_name,phoneno,brand_id,brand_name,retailer_store_store_id,organisation_id,pstatus,organisation_id)
			cursor.execute(insert_query,data)

			return ({"attributes": {
			    		"status_desc": "promoter_details",
			    		"status": "success",
			    		"message":""
			    	},
			    	"responseList": details}), status.HTTP_200_OK

#----------------------Add-Promoter---------------------#

#----------------------Update-Promoter-Info---------------------#

@name_space.route("/updatePromoterInfo/<int:promoter_id>")
class updatePromoterInfo(Resource):
	@api.expect(promoter_putmodel)
	def put(self,promoter_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()
		pstatus = details['pstatus']

		update_query = ("""UPDATE `promoter` SET `status` = %s
				WHERE `promoter_id` = %s """)
		update_data = (pstatus,promoter_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Promoter",
								"status": "success",
								"message":"Update successfully"
									},
				"responseList":details}), status.HTTP_200_OK

#----------------------Update-Promoter-Info---------------------#

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-With-Date-Range-------------------------#

@name_space.route("/CustomerCountWithOrganisationAndRetailStoreWithDateRange/<string:filterkey>/<int:organisation_id>/<int:brand_id>/<string:start_date>/<string:end_date>")	
class CustomerCountWithOrganisationAndRetailStoreWithDateRange(Resource):
	def get(self,filterkey,organisation_id,brand_id,start_date,end_date):
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

			get_registed_customer_query = ("""SELECT * FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,today_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				new_registed_customer = 0
				print(cursor._last_executed)
				registed_customer = cursor.fetchall()					
				for key,data in enumerate(registed_customer):
					print(data['admin_id'])			
					get_braned_customer_query = ("""SELECT DISTINCT `customer_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,data['admin_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						print(cursor._last_executed)						

						new_registed_customer += 1

				registation_data['total_customer_count'] = new_registed_customer

			else:
				registation_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				registation_data['store_data'] = store_data				
			else:
				registation_data['store_data'] = []

			for key,data in enumerate(registation_data['store_data']):

				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as `total_user`
					FROM `admins` a 
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and  date(`date_of_creation`) =%s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],today_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0

			get_notify_customer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_notify_customer 
				FROM `app_notification` apn
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`				
				WHERE apn.`organisation_id`=%s and `destination_type` = 2 and date(apn.`Last_Update_TS`) = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
			get_notify_customer_data = (organisation_id,today_date,organisation_id,brand_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			print(cursor._last_executed)

			if count_notify_customer_data > 0:				
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				notification_data['store_data'] = store_data				
			else:
				notification_data['store_data'] = []

			for nkey,ndata in enumerate(notification_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_user 
					FROM `app_notification` apn
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = apn.`U_id`
					WHERE ur.`organisation_id`=%s and apn.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(apn.`Last_Update_TS`) = %s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],today_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0

			get_loggedin_user_query = ("""SELECT DISTINCT `customer_id` FROM `customer_store_analytics` where date(`last_update_ts`) = %s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (today_date,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)
			print(cur._last_executed)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchall()
				new_loggedin_user = 0
				for lukey,ludata in enumerate(loggedin_user_data):
					get_braned_customer_query = ("""SELECT DISTINCT cpm.`mapping_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,ludata['customer_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						new_loggedin_user += 1	

				loggedin_data['total_customer_count'] = new_loggedin_user
			else:
				loggedin_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				loggedin_data['store_data'] = store_data			

				for nrlkey,nrldata in enumerate(loggedin_data['store_data']):
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) = %s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (today_date,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `customer_product_mapping` cpm								
								INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
								INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cpm.`customer_id`
								WHERE ur.`organisation_id` = %s and cpm.`organisation_id`=%s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and cpm.`customer_id` = %s and pbm.`brand_id` = %s""")	
							get_customer_retailer_data = (organisation_id,organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'],brand_id)

							count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

							if count_customer_retailer_data > 0:
								store_analytics_view[sakey]['s_view'] = 1
							else:
								store_analytics_view[sakey]['s_view'] = 0
						print(store_analytics_view)		
						new_store_analytics_view = []
						for nsakey,nsadata in enumerate(store_analytics_view):
							if nsadata['s_view'] == 1:
								new_store_analytics_view.append(store_analytics_view[nsakey])
						loggedin_data['store_data'][nrlkey]['customer_count'] = len(new_store_analytics_view)
					else:
						loggedin_data['store_data'][nrlkey]['customer_count'] = 0

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 
				FROM `customer_remarks` cr
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
				WHERE `customer_id`!=0 and cr.`organisation_id`=%s and pbm.`organisation_id` = %s and
				date(cr.`last_update_ts`) = %s and pbm.`brand_id`= %s""")		
			get_demo_given_customer_data = (organisation_id,organisation_id,today_date,brand_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)
			print(cursor._last_executed)	

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				demo_data['store_data'] = store_data				
			else:
				demo_data['store_data'] = []

			for dkey,ddata in enumerate(demo_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cr.`customer_id`)) as total_user 
					FROM `customer_remarks` cr 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:

					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0

		if filterkey == 'yesterday':
			
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_registed_customer_query = ("""SELECT * FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,yesterday)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				new_registed_customer = 0
				print(cursor._last_executed)
				registed_customer = cursor.fetchall()					
				for key,data in enumerate(registed_customer):
					print(data['admin_id'])			
					get_braned_customer_query = ("""SELECT DISTINCT `customer_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,data['admin_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						print(cursor._last_executed)						

						new_registed_customer += 1

				registation_data['total_customer_count'] = new_registed_customer

			else:
				registation_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				registation_data['store_data'] = store_data				
			else:
				registation_data['store_data'] = []

			for key,data in enumerate(registation_data['store_data']):

				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as `total_user`
					FROM `admins` a 
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and  date(`date_of_creation`) =%s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],yesterday,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0

			get_notify_customer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_notify_customer 
				FROM `app_notification` apn
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`				
				WHERE apn.`organisation_id`=%s and `destination_type` = 2 and date(apn.`Last_Update_TS`) = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
			get_notify_customer_data = (organisation_id,yesterday,organisation_id,brand_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			print(cursor._last_executed)

			if count_notify_customer_data > 0:				
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				notification_data['store_data'] = store_data				
			else:
				notification_data['store_data'] = []

			for nkey,ndata in enumerate(notification_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_user 
					FROM `app_notification` apn
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = apn.`U_id`
					WHERE ur.`organisation_id`=%s and apn.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(apn.`Last_Update_TS`) = %s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],yesterday,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0

			get_loggedin_user_query = ("""SELECT DISTINCT `customer_id` FROM `customer_store_analytics` where date(`last_update_ts`) = %s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (yesterday,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)
			print(cur._last_executed)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchall()
				new_loggedin_user = 0
				for lukey,ludata in enumerate(loggedin_user_data):
					get_braned_customer_query = ("""SELECT DISTINCT cpm.`mapping_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,ludata['customer_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						new_loggedin_user += 1	

				loggedin_data['total_customer_count'] = new_loggedin_user
			else:
				loggedin_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				loggedin_data['store_data'] = store_data			

				for nrlkey,nrldata in enumerate(loggedin_data['store_data']):
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) = %s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (yesterday,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `customer_product_mapping` cpm								
								INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
								INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cpm.`customer_id`
								WHERE ur.`organisation_id` = %s and cpm.`organisation_id`=%s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and cpm.`customer_id` = %s and pbm.`brand_id` = %s""")	
							get_customer_retailer_data = (organisation_id,organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'],brand_id)

							count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

							if count_customer_retailer_data > 0:
								store_analytics_view[sakey]['s_view'] = 1
							else:
								store_analytics_view[sakey]['s_view'] = 0
						print(store_analytics_view)		
						new_store_analytics_view = []
						for nsakey,nsadata in enumerate(store_analytics_view):
							if nsadata['s_view'] == 1:
								new_store_analytics_view.append(store_analytics_view[nsakey])
						loggedin_data['store_data'][nrlkey]['customer_count'] = len(new_store_analytics_view)
					else:
						loggedin_data['store_data'][nrlkey]['customer_count'] = 0

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 
				FROM `customer_remarks` cr
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
				WHERE `customer_id`!=0 and cr.`organisation_id`=%s and pbm.`organisation_id` = %s and
				date(cr.`last_update_ts`) = %s and pbm.`brand_id`= %s""")		
			get_demo_given_customer_data = (organisation_id,organisation_id,yesterday,brand_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)
			print(cursor._last_executed)	

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				demo_data['store_data'] = store_data				
			else:
				demo_data['store_data'] = []

			for dkey,ddata in enumerate(demo_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cr.`customer_id`)) as total_user 
					FROM `customer_remarks` cr 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:

					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0

		if filterkey == 'last 7 days':
			
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT * FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				new_registed_customer = 0
				print(cursor._last_executed)
				registed_customer = cursor.fetchall()					
				for key,data in enumerate(registed_customer):
					print(data['admin_id'])			
					get_braned_customer_query = ("""SELECT DISTINCT `customer_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,data['admin_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						print(cursor._last_executed)						

						new_registed_customer += 1

				registation_data['total_customer_count'] = new_registed_customer

			else:
				registation_data['total_customer_count'] = 0



			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				registation_data['store_data'] = store_data				
			else:
				registation_data['store_data'] = []

			for key,data in enumerate(registation_data['store_data']):

				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as `total_user`
					FROM `admins` a 
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and  date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0

			get_notify_customer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_notify_customer 
				FROM `app_notification` apn
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`				
				WHERE apn.`organisation_id`=%s and `destination_type` = 2 and date(apn.`Last_Update_TS`) >= %s and date(apn.`Last_Update_TS`) <= %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,brand_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			print(cursor._last_executed)

			if count_notify_customer_data > 0:				
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				notification_data['store_data'] = store_data				
			else:
				notification_data['store_data'] = []

			for nkey,ndata in enumerate(notification_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_user 
					FROM `app_notification` apn
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = apn.`U_id`
					WHERE ur.`organisation_id`=%s and apn.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(apn.`Last_Update_TS`) >= %s and date(apn.`Last_Update_TS`) <= %s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0

			get_loggedin_user_query = ("""SELECT DISTINCT `customer_id` FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (start_date,end_date,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)
			print(cur._last_executed)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchall()
				new_loggedin_user = 0
				for lukey,ludata in enumerate(loggedin_user_data):
					get_braned_customer_query = ("""SELECT DISTINCT cpm.`mapping_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,ludata['customer_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						new_loggedin_user += 1	

				loggedin_data['total_customer_count'] = new_loggedin_user
			else:
				loggedin_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				loggedin_data['store_data'] = store_data			

				for nrlkey,nrldata in enumerate(loggedin_data['store_data']):
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (start_date,end_date,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `customer_product_mapping` cpm								
								INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
								INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cpm.`customer_id`
								WHERE ur.`organisation_id` = %s and cpm.`organisation_id`=%s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and cpm.`customer_id` = %s and pbm.`brand_id` = %s""")	
							get_customer_retailer_data = (organisation_id,organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'],brand_id)

							count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

							if count_customer_retailer_data > 0:
								store_analytics_view[sakey]['s_view'] = 1
							else:
								store_analytics_view[sakey]['s_view'] = 0
						print(store_analytics_view)		
						new_store_analytics_view = []
						for nsakey,nsadata in enumerate(store_analytics_view):
							if nsadata['s_view'] == 1:
								new_store_analytics_view.append(store_analytics_view[nsakey])
						loggedin_data['store_data'][nrlkey]['customer_count'] = len(new_store_analytics_view)
					else:
						loggedin_data['store_data'][nrlkey]['customer_count'] = 0

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 
				FROM `customer_remarks` cr
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
				WHERE `customer_id`!=0 and cr.`organisation_id`=%s and pbm.`organisation_id` = %s and
				date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s and pbm.`brand_id`= %s""")		
			get_demo_given_customer_data = (organisation_id,organisation_id,start_date,end_date,brand_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)
			print(cursor._last_executed)	

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				demo_data['store_data'] = store_data				
			else:
				demo_data['store_data'] = []

			for dkey,ddata in enumerate(demo_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cr.`customer_id`)) as total_user 
					FROM `customer_remarks` cr 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:

					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0

		if filterkey == 'this month':
			
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT * FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				new_registed_customer = 0
				print(cursor._last_executed)
				registed_customer = cursor.fetchall()					
				for key,data in enumerate(registed_customer):
					print(data['admin_id'])			
					get_braned_customer_query = ("""SELECT DISTINCT `customer_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,data['admin_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						print(cursor._last_executed)						

						new_registed_customer += 1

				registation_data['total_customer_count'] = new_registed_customer

			else:
				registation_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				registation_data['store_data'] = store_data				
			else:
				registation_data['store_data'] = []

			for key,data in enumerate(registation_data['store_data']):

				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as `total_user`
					FROM `admins` a 
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and  date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0

			get_notify_customer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_notify_customer 
				FROM `app_notification` apn
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`				
				WHERE apn.`organisation_id`=%s and `destination_type` = 2 and date(apn.`Last_Update_TS`) >= %s and date(apn.`Last_Update_TS`) <= %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,brand_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			print(cursor._last_executed)

			if count_notify_customer_data > 0:				
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				notification_data['store_data'] = store_data				
			else:
				notification_data['store_data'] = []

			for nkey,ndata in enumerate(notification_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_user 
					FROM `app_notification` apn
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = apn.`U_id`
					WHERE ur.`organisation_id`=%s and apn.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(apn.`Last_Update_TS`) >= %s and date(apn.`Last_Update_TS`) <= %s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0

			get_loggedin_user_query = ("""SELECT DISTINCT `customer_id` FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (start_date,end_date,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)
			print(cur._last_executed)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchall()
				new_loggedin_user = 0
				for lukey,ludata in enumerate(loggedin_user_data):
					get_braned_customer_query = ("""SELECT DISTINCT cpm.`mapping_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,ludata['customer_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						new_loggedin_user += 1	

				loggedin_data['total_customer_count'] = new_loggedin_user
			else:
				loggedin_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				loggedin_data['store_data'] = store_data			

				for nrlkey,nrldata in enumerate(loggedin_data['store_data']):
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (start_date,end_date,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `customer_product_mapping` cpm								
								INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
								INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cpm.`customer_id`
								WHERE ur.`organisation_id` = %s and cpm.`organisation_id`=%s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and cpm.`customer_id` = %s and pbm.`brand_id` = %s""")	
							get_customer_retailer_data = (organisation_id,organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'],brand_id)

							count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

							if count_customer_retailer_data > 0:
								store_analytics_view[sakey]['s_view'] = 1
							else:
								store_analytics_view[sakey]['s_view'] = 0
						print(store_analytics_view)		
						new_store_analytics_view = []
						for nsakey,nsadata in enumerate(store_analytics_view):
							if nsadata['s_view'] == 1:
								new_store_analytics_view.append(store_analytics_view[nsakey])
						loggedin_data['store_data'][nrlkey]['customer_count'] = len(new_store_analytics_view)
					else:
						loggedin_data['store_data'][nrlkey]['customer_count'] = 0

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 
				FROM `customer_remarks` cr
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
				WHERE `customer_id`!=0 and cr.`organisation_id`=%s and pbm.`organisation_id` = %s and
				date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s and pbm.`brand_id`= %s""")		
			get_demo_given_customer_data = (organisation_id,organisation_id,start_date,end_date,brand_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)
			print(cursor._last_executed)	

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				demo_data['store_data'] = store_data				
			else:
				demo_data['store_data'] = []

			for dkey,ddata in enumerate(demo_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cr.`customer_id`)) as total_user 
					FROM `customer_remarks` cr 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:

					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0


		if filterkey == 'lifetime':
			
			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT * FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				new_registed_customer = 0
				print(cursor._last_executed)
				registed_customer = cursor.fetchall()					
				for key,data in enumerate(registed_customer):
					print(data['admin_id'])			
					get_braned_customer_query = ("""SELECT DISTINCT `customer_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,data['admin_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						print(cursor._last_executed)						

						new_registed_customer += 1	

				registation_data['total_customer_count'] = new_registed_customer				

			else:
				registation_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				registation_data['store_data'] = store_data				
			else:
				registation_data['store_data'] = []

			for key,data in enumerate(registation_data['store_data']):

				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as `total_user`
					FROM `admins` a 
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and  date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0

			get_notify_customer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_notify_customer 
				FROM `app_notification` apn
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`				
				WHERE apn.`organisation_id`=%s and `destination_type` = 2 and date(apn.`Last_Update_TS`) >= %s and date(apn.`Last_Update_TS`) <= %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,brand_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			print(cursor._last_executed)

			if count_notify_customer_data > 0:				
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				notification_data['store_data'] = store_data				
			else:
				notification_data['store_data'] = []

			for nkey,ndata in enumerate(notification_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_user 
					FROM `app_notification` apn
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = apn.`U_id`
					WHERE ur.`organisation_id`=%s and apn.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(apn.`Last_Update_TS`) >= %s and date(apn.`Last_Update_TS`) <= %s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0

			get_loggedin_user_query = ("""SELECT DISTINCT `customer_id` FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (start_date,end_date,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)
			print(cur._last_executed)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchall()
				new_loggedin_user = 0
				for lukey,ludata in enumerate(loggedin_user_data):
					get_braned_customer_query = ("""SELECT DISTINCT cpm.`mapping_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,ludata['customer_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						new_loggedin_user += 1	

				loggedin_data['total_customer_count'] = new_loggedin_user
			else:
				loggedin_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				loggedin_data['store_data'] = store_data			

				for nrlkey,nrldata in enumerate(loggedin_data['store_data']):
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (start_date,end_date,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `customer_product_mapping` cpm								
								INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
								INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cpm.`customer_id`
								WHERE ur.`organisation_id` = %s and cpm.`organisation_id`=%s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and cpm.`customer_id` = %s and pbm.`brand_id` = %s""")	
							get_customer_retailer_data = (organisation_id,organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'],brand_id)

							count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

							if count_customer_retailer_data > 0:
								store_analytics_view[sakey]['s_view'] = 1
							else:
								store_analytics_view[sakey]['s_view'] = 0
						print(store_analytics_view)		
						new_store_analytics_view = []
						for nsakey,nsadata in enumerate(store_analytics_view):
							if nsadata['s_view'] == 1:
								new_store_analytics_view.append(store_analytics_view[nsakey])
						loggedin_data['store_data'][nrlkey]['customer_count'] = len(new_store_analytics_view)
					else:
						loggedin_data['store_data'][nrlkey]['customer_count'] = 0

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 
				FROM `customer_remarks` cr
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
				WHERE `customer_id`!=0 and cr.`organisation_id`=%s and pbm.`organisation_id` = %s and
				date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s and pbm.`brand_id`= %s""")		
			get_demo_given_customer_data = (organisation_id,organisation_id,start_date,end_date,brand_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)
			print(cursor._last_executed)	

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				demo_data['store_data'] = store_data				
			else:
				demo_data['store_data'] = []

			for dkey,ddata in enumerate(demo_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cr.`customer_id`)) as total_user 
					FROM `customer_remarks` cr 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:

					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0


		if filterkey == 'custom date':

			start_date = start_date
			
			end_date = end_date

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT * FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				new_registed_customer = 0
				print(cursor._last_executed)
				registed_customer = cursor.fetchall()					
				for key,data in enumerate(registed_customer):
					print(data['admin_id'])			
					get_braned_customer_query = ("""SELECT DISTINCT cpm.`mapping_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,data['admin_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)


					if brand_customer_count > 0:
						print(cursor._last_executed)						

						new_registed_customer += 1	
				registation_data['total_customer_count'] = new_registed_customer

			else:
				registation_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				registation_data['store_data'] = store_data				
			else:
				registation_data['store_data'] = []

			for key,data in enumerate(registation_data['store_data']):

				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as `total_user`
					FROM `admins` a 
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and  date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0

			get_notify_customer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_notify_customer 
				FROM `app_notification` apn
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`				
				WHERE apn.`organisation_id`=%s and `destination_type` = 2 and date(apn.`Last_Update_TS`) >= %s and date(apn.`Last_Update_TS`) <= %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date,organisation_id,brand_id)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			print(cursor._last_executed)

			if count_notify_customer_data > 0:				
				notify_customer_data = cursor.fetchone()
				notification_data['total_customer_count'] = notify_customer_data['total_notify_customer']
			else:
				notification_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				notification_data['store_data'] = store_data				
			else:
				notification_data['store_data'] = []

			for nkey,ndata in enumerate(notification_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cpm.`customer_id`)) as total_user 
					FROM `app_notification` apn
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= apn.`U_id`
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = apn.`U_id`
					WHERE ur.`organisation_id`=%s and apn.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(apn.`Last_Update_TS`) >= %s and date(apn.`Last_Update_TS`) <= %s and pbm.`brand_id` = %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date,brand_id)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0

			get_loggedin_user_query = ("""SELECT DISTINCT `customer_id` FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (start_date,end_date,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)
			print(cur._last_executed)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchall()
				new_loggedin_user = 0
				for lukey,ludata in enumerate(loggedin_user_data):
					get_braned_customer_query = ("""SELECT DISTINCT cpm.`mapping_id` FROM `customer_product_mapping` cpm
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE pbm.`brand_id` = %s and cpm.`organisation_id` = %s and cpm.`customer_id` = %s and cpm.`product_status` = 'o'""")
					get_brand_customer_data = (brand_id,organisation_id,ludata['customer_id'])
					brand_customer_count = cursor.execute(get_braned_customer_query,get_brand_customer_data)

					if brand_customer_count > 0:
						new_loggedin_user += 1	

				loggedin_data['total_customer_count'] = new_loggedin_user
			else:
				loggedin_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				loggedin_data['store_data'] = store_data			

				for nrlkey,nrldata in enumerate(loggedin_data['store_data']):
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (start_date,end_date,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `customer_product_mapping` cpm								
								INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
								INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cpm.`customer_id`
								WHERE ur.`organisation_id` = %s and cpm.`organisation_id`=%s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and cpm.`customer_id` = %s and pbm.`brand_id` = %s""")	
							get_customer_retailer_data = (organisation_id,organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'],brand_id)

							count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

							if count_customer_retailer_data > 0:
								store_analytics_view[sakey]['s_view'] = 1
							else:
								store_analytics_view[sakey]['s_view'] = 0
						print(store_analytics_view)		
						new_store_analytics_view = []
						for nsakey,nsadata in enumerate(store_analytics_view):
							if nsadata['s_view'] == 1:
								new_store_analytics_view.append(store_analytics_view[nsakey])
						loggedin_data['store_data'][nrlkey]['customer_count'] = len(new_store_analytics_view)
					else:
						loggedin_data['store_data'][nrlkey]['customer_count'] = 0

			get_demo_given_customer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 
				FROM `customer_remarks` cr
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
				WHERE `customer_id`!=0 and cr.`organisation_id`=%s and pbm.`organisation_id` = %s and
				date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s and pbm.`brand_id`= %s""")		
			get_demo_given_customer_data = (organisation_id,organisation_id,start_date,end_date,brand_id)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)
			print(cursor._last_executed)	

			if count_demo_given_customer > 0:
				demo_given_data = cursor.fetchone()
				demo_data['total_customer_count'] = demo_given_data['total_user']
			else:
				demo_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				demo_data['store_data'] = store_data				
			else:
				demo_data['store_data'] = []

			for dkey,ddata in enumerate(demo_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(distinct(cr.`customer_id`)) as total_user 
					FROM `customer_remarks` cr 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = cr.`product_id`
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >= %s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:

					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0

		return ({"attributes": {
		    		"status_desc": "Customer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{"registation_data":registation_data,"notification_data":notification_data,"loggedin_data":loggedin_data,"demo_data":demo_data,"total_login_user_from_registration_data":total_login_user_from_registration_data,"total_never_login_user_from_registration_data":total_never_login_user_from_registration_data} }), status.HTTP_200_OK

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-With-Date-Range-------------------------#

#--------------------------------Customer-Details-By-Date-Organisation-Id------------------------------------#
@name_space.route("/CustomerDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>/<int:brand_id>")	
class CustomerDetailsByFilerKeyOrganizationId(Resource):
	def get(self,filterkey,organisation_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))


		if filterkey == 'today':
			cursor.execute("""SELECT DISTINCT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
				name,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
				a.`dob`,a.`anniversary`,a.`phoneno`,a.`profile_image`,a.`organisation_id`,a.`pincode`,a.`date_of_creation`,a.`loggedin_status`,a.`wallet`
				FROM `admins` a
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id` 
				WHERE a.`organisation_id`=%s and `role_id`=4 and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				a.`status`=1 and date(`date_of_creation`)=%s and `brand_id` = %s and cpm.`product_status` = 'o' """,(organisation_id,organisation_id,organisation_id,today,brand_id))
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
			cursor.execute("""SELECT  DISTINCT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
				name,
				a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
				a.`dob`,a.`anniversary`,a.`phoneno`,a.`profile_image`,a.`organisation_id`,a.`pincode`,a.`date_of_creation`,a.`loggedin_status`,a.`wallet`
				FROM `admins` a
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE a.`organisation_id`=%s and `role_id`=4 and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and 
				date(`date_of_creation`)=DATE(NOW()) + INTERVAL -1 DAY and cpm.`product_status` = 'o'""",(organisation_id,organisation_id,organisation_id))

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
			cursor.execute("""SELECT  DISTINCT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
				name,
				a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
				a.`dob`,a.`anniversary`,a.`phoneno`,a.`profile_image`,a.`organisation_id`,a.`pincode`,a.`date_of_creation`,a.`loggedin_status`,a.`wallet`
				FROM `admins` a
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE a.`organisation_id`=%s and `role_id`=4 and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and a.`status`=1 and 
				date(`date_of_creation`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`date_of_creation`) < DATE(NOW()) + INTERVAL 0 DAY and cpm.`product_status` = 'o'""",(organisation_id,organisation_id,organisation_id))

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
			cursor.execute("""SELECT  DISTINCT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
				name,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
				a.`dob`,a.`anniversary`,a.`phoneno`,a.`profile_image`,a.`organisation_id`,a.`pincode`,a.`date_of_creation`,a.`loggedin_status`,a.`wallet`
				FROM `admins` a
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id` 
				WHERE a.`organisation_id`=%s and `role_id`=4 and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and a.`status`=1 and 
				date(`date_of_creation`) between %s and %s and cpm.`product_status` = 'o'""",(organisation_id,organisation_id,organisation_id,stday,today))

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
			
			cursor.execute("""SELECT  DISTINCT  a.`admin_id`,concat(`first_name`,' ',`last_name`)as
				name,
				a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,
				a.`dob`,a.`anniversary`,a.`phoneno`,a.`profile_image`,a.`organisation_id`,a.`pincode`,a.`date_of_creation`,a.`loggedin_status`,a.`wallet`
				FROM `admins` a
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id`= a.`admin_id`
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`  
				WHERE a.`organisation_id`=%s and `role_id`=4 and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and a.`status`=1 and 
				date(`date_of_creation`) between %s and %s and cpm.`product_status` = 'o'""",(organisation_id,organisation_id,organisation_id,slifetime,today))

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

#--------------------------------Customer-Details-By-Date-Organisation-Id------------------------------------#


#----------------------------Store-View-Dtls-By-Date-Organization------------------------------#
@name_space.route("/StoreViewDtlsByDateOrganizationId/<string:filterkey>/<int:organisation_id>/<int:brand_id>")	
class StoreViewDtlsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()
		
		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cur.execute("""SELECT DISTINCT `customer_id`,
				`from_web_or_phone` FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=%s ORDER BY `analytics_id` DESC""",(organisation_id,today))		
			print(cur._last_executed)	
			storeviewDtls = cur.fetchall()


			if storeviewDtls:
				for aid in range(len(storeviewDtls)):
					cur.execute("""SELECT `analytics_id`,`last_update_ts`,`organisation_id` FROM `customer_store_analytics` WHERE `customer_id`=%s and `from_web_or_phone` = %s""",(storeviewDtls[aid]['customer_id'],storeviewDtls[aid]['from_web_or_phone']))
					storeviewDtlsAnalyticsdata = cur.fetchone()
					storeviewDtls[aid]['last_update_ts'] = storeviewDtlsAnalyticsdata['last_update_ts'].isoformat()
					storeviewDtls[aid]['analytics_id'] = storeviewDtlsAnalyticsdata['analytics_id']
					storeviewDtls[aid]['organisation_id'] = storeviewDtlsAnalyticsdata['organisation_id']
					
					if storeviewDtls[aid]['from_web_or_phone'] == 1:
						storeviewDtls[aid]['from_web_or_phone'] = 'From Web'
					else:
						storeviewDtls[aid]['from_web_or_phone'] = 'From Mobile'

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						`phoneno`,anniversary FROM `admins` WHERE `admin_id`=%s""",(storeviewDtls[aid]['customer_id']))
					visitordtls = cursor.fetchone()
					
					if visitordtls:
						storeviewDtls[aid]['name'] = visitordtls['name']
						storeviewDtls[aid]['phoneno'] = visitordtls['phoneno']
						storeviewDtls[aid]['anniversary'] = visitordtls['anniversary']
					
					else:
						storeviewDtls[aid]['name'] = ''
						storeviewDtls[aid]['phoneno'] = ''
						storeviewDtls[aid]['anniversary'] = ''

					storeviewDtls[aid]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(storeviewDtls[aid]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						storeviewDtls[aid]['customertype'] = customertype['customer_type']
					else:
						storeviewDtls[aid]['customertype'] = ''
			else:
				storeviewDtls = []

#----------------------------Store-View-Dtls-By-Date-Organization------------------------------#

#---------------------------Retailer-Dashboard-Dtls-By-FilterKey-And-Retailer-Id-------------------------#
@name_space.route("/RetailerDashboardDtlsByFilerKeyOrganizationwithdaterange/<string:filterkey>/<int:retailer_store_id>/<int:brand_id>/<int:organisation_id>/<string:start_date>/<string:end_date>")	
class RetailerDashboardDtlsByFilerKeyOrganizationwithdaterange(Resource):
	def get(self,filterkey,retailer_store_id,brand_id,organisation_id,start_date,end_date):
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
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) = %s
								""")
			get_oder_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,today_date)

			order_count = cursor.execute(get_order_query,get_oder_data)
			order_data = cursor.fetchone()

			if order_data:				
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) = %s""")
			get_sales_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,today_date)

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
					get_user_retailer_query = ("""SELECT * 
						FROM `user_retailer_mapping` urm
						INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
						INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
						WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
												INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
												INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
												INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
												INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
												WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) = %s
								""")
			get_oder_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,yesterday)

			order_count = cursor.execute(get_order_query,get_oder_data)
			order_data = cursor.fetchone()

			if order_data:				
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) = %s""")
			get_sales_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,yesterday)

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
					get_user_retailer_query = ("""SELECT * 
						FROM `user_retailer_mapping` urm
						INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
						INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
						WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
												INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
												INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
												INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
												INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
												WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s
								""")
			get_oder_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,start_date,end_date)

			order_count = cursor.execute(get_order_query,get_oder_data)
			order_data = cursor.fetchone()

			if order_data:				
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s""")
			get_sales_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,start_date,end_date)

			sales_count = cursor.execute(get_sales_query,get_sales_data)

			sales_data = cursor.fetchone()

			if sales_data['total'] !=None:
				sales = sales_data['total']
			else:
				sales = 0


			get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s """)
			get_product_view_data =(organisation_id,start_date,end_date)	
			product_view_count = cur.execute(get_product_view_query,get_product_view_data)

			if product_view_count > 0:
				product_view_data = cur.fetchall()
				for key,data in enumerate(product_view_data):
					get_user_retailer_query = ("""SELECT * 
						FROM `user_retailer_mapping` urm
						INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
						INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
						WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
												INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
												INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
												INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
												INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
												WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s
								""")
			get_oder_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,start_date,end_date)

			order_count = cursor.execute(get_order_query,get_oder_data)
			order_data = cursor.fetchone()

			if order_data:				
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s""")
			get_sales_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,start_date,end_date)

			sales_count = cursor.execute(get_sales_query,get_sales_data)

			sales_data = cursor.fetchone()

			if sales_data['total'] !=None:
				sales = sales_data['total']
			else:
				sales = 0


			get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s """)
			get_product_view_data =(organisation_id,start_date,end_date)	
			product_view_count = cur.execute(get_product_view_query,get_product_view_data)

			if product_view_count > 0:
				product_view_data = cur.fetchall()
				for key,data in enumerate(product_view_data):
					get_user_retailer_query = ("""SELECT * 
						FROM `user_retailer_mapping` urm
						INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
						INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
						WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
												INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
												INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
												INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
												INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
												WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s
								""")
			get_oder_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,start_date,end_date)

			order_count = cursor.execute(get_order_query,get_oder_data)
			order_data = cursor.fetchone()

			if order_data:				
				orders = order_data['total']
			else:
				orders = 0

			get_sales_query = ("""SELECT SUM(`amount`)as total
								  FROM `instamojo_payment_request` ipr 
								  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s""")
			get_sales_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,start_date,end_date)

			sales_count = cursor.execute(get_sales_query,get_sales_data)

			sales_data = cursor.fetchone()

			if sales_data['total'] !=None:
				sales = sales_data['total']
			else:
				sales = 0


			get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s """)
			get_product_view_data =(organisation_id,start_date,end_date)	
			product_view_count = cur.execute(get_product_view_query,get_product_view_data)

			if product_view_count > 0:
				product_view_data = cur.fetchall()
				for key,data in enumerate(product_view_data):
					get_user_retailer_query = ("""SELECT * 
						FROM `user_retailer_mapping` urm
						INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
						INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
						WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
												INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
												INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
												INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
												INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
												WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
								  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
								  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
								  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
								  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
								  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
								  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s
								""")
				get_oder_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,start_date,end_date)

				order_count = cursor.execute(get_order_query,get_oder_data)
				order_data = cursor.fetchone()

				if order_data:				
					orders = order_data['total']
				else:
					orders = 0

				get_sales_query = ("""SELECT SUM(`amount`)as total
									  FROM `instamojo_payment_request` ipr 
									  INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ipr.`user_id`
									  INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = ur.`user_id` 
									  INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
									  INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
									  INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
									  WHERE  ur.`organisation_id`=%s and ipr.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s
									  and ur.`retailer_store_id` = %s and date(ipr.`last_update_ts`) >= %s and date(ipr.`last_update_ts`) <= %s""")
				get_sales_data = (organisation_id,organisation_id,organisation_id,brand_id,retailer_store_id,start_date,end_date)

				sales_count = cursor.execute(get_sales_query,get_sales_data)

				sales_data = cursor.fetchone()

				if sales_data['total'] !=None:
					sales = sales_data['total']
				else:
					sales = 0


				get_product_view_query = ("""SELECT * FROM `customer_product_analytics` WHERE `organisation_id` = %s and date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s """)
				get_product_view_data =(organisation_id,start_date,end_date)	
				product_view_count = cur.execute(get_product_view_query,get_product_view_data)

				if product_view_count > 0:
					product_view_data = cur.fetchall()
					for key,data in enumerate(product_view_data):
						get_user_retailer_query = ("""SELECT * 
							FROM `user_retailer_mapping` urm
							INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
							INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
							INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
							INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
							WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
						get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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
						get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
													INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
													INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
													INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
													INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
													WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`brand_id` = %s""")
						get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,brand_id)
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

@name_space_order_history.route("/searchorderHistory/<string:searchkey>/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>/<int:page>")	
class searchorderHistory(Resource):
	def get(self,searchkey,organisation_id,retailer_store_id,brand_id,page):
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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE  ipr.`organisation_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and urm.`retailer_store_id` = %s and pbm.`brand_id` = %s and ( ipr.`transaction_id` LIKE %s or a.`first_name` LIKE %s or a.`phoneno` LIKE %s or a.`last_name` LIKE %s or ipr.`delivery_option` LIKE %s or `order_payment_status` LIKE %s) LIMIT %s,20""")

		get_data = (organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%",offset)
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
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					where op.`transaction_id` = %s and cpm.`product_status` = %s and pbm.`brand_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s""")	

			customer_product_data = (data['transaction_id'],product_status,brand_id,organisation_id,organisation_id)
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
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id` 
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE  ipr.`organisation_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and urm.`retailer_store_id` = %s and pbm.`brand_id` = %s and ( ipr.`transaction_id` LIKE %s or a.`first_name` LIKE %s or a.`phoneno` LIKE %s or a.`last_name` LIKE %s or ipr.`delivery_option` LIKE %s or `order_payment_status` LIKE %s)""")

		get_data_count = (organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%")
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

#----------------------------Order-Status-Details-By-Organisation_Id-And-Retail-Store--------------------------#
@name_space_order_history.route("/OrderStatusDtlsByDateOrganisationId/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>")	
class OrderStatusDtlsByDateOrganisationId(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id,brand_id):
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
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					WHERE ipr.`status`=%s and 
					ipr.`organisation_id`=%s and date(ipr.`last_update_ts`)=%s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id`= %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s""",
					(statusList[i]['order_status'],organisation_id,today,retailer_store_id,organisation_id,organisation_id,organisation_id,brand_id))

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
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					WHERE ipr.`status`=%s 
					and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
					ipr.`organisation_id`=%s and cpm.`organisation_id`= %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s and date(ipr.`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",
					(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,brand_id))
				print(cursor._last_executed)
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
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					WHERE ipr.`status`=%s 
					and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
					ipr.`organisation_id`=%s and cpm.`organisation_id`= %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s and date(ipr.`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
	        		date(ipr.`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,brand_id))

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
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					WHERE ipr.`status`=%s and 
					urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
					ipr.`organisation_id`=%s and cpm.`organisation_id`= %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s and date(ipr.`last_update_ts`) between %s and %s""",
					(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,brand_id,stday,today))

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
					INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
					INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					WHERE ipr.`status`=%s 
					and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
					ipr.`organisation_id`=%s and cpm.`organisation_id`= %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s and date(ipr.`last_update_ts`) between %s and %s""",
					(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,brand_id,slifetime,today))

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

#------------------------------Order-Detail-By-Date-And-Organisation-And-Store----------------------------#
@name_space_order_history.route("/OrderDtlsByDateOrganizationId/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>")	
class OrderDtlsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id,brand_id):
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
				INNER join `product_brand_mapping` pbm on pbm.`product_id`=pd.`product_id`
				INNER join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` 
				WHERE op.`organisation_id`=%s and date(op.`last_update_ts`)=%s and urm.`organisation_id` = %s and pbm.`organisation_id` = %s and urm.`retailer_store_id` = %s and pbm.`brand_id` = %s""",(organisation_id,today,organisation_id,organisation_id,retailer_store_id,brand_id))

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
				INNER join `product_brand_mapping` pbm on pbm.`product_id`=pd.`product_id`
				Left join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` 
				WHERE op.`organisation_id`=%s and  urm.`organisation_id` = %s and pbm.`organisation_id` = %s and urm.`retailer_store_id` = %s and pbm.`brand_id` = %s and
				date(op.`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id))

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
				INNER join `product_brand_mapping` pbm on pbm.`product_id`=pd.`product_id`
				INNER join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` WHERE 
				op.`organisation_id`=%s and urm.`organisation_id` = %s and pbm.`organisation_id` = %s and urm.`retailer_store_id` = %s and `brand_id` = %s and
				date(op.`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(op.`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id))

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
				INNER join `product_brand_mapping` pbm on pbm.`product_id`=pd.`product_id`
				INNER join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` 
				WHERE op.`organisation_id`=%s and urm.`organisation_id` = %s and pbm.`organisation_id` = %s and urm.`retailer_store_id` = %s and `brand_id` = %s and
				date(op.`last_update_ts`) between %s and %s""",(organisation_id,organisation_id,organisation_id,retailer_store_id,stday,brand_id,today))

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
				INNER join `product_brand_mapping` pbm on pbm.`product_id`=pd.`product_id` 
				INNER join `instamojo_payment_request` ipr on op.`transaction_id`=ipr.`transaction_id` 
				WHERE op.`organisation_id`=%s and  urm.`organisation_id` = %s and pbm.`organisation_id` = %s and urm.`retailer_store_id` = %s and `brand_id` = %s and
				date(op.`last_update_ts`) between %s and %s""",(organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id,slifetime,today))

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

#--------------------------------Order-Status-Details-By-Organisation-Id------------------------------------#
@name_space_order_history.route("/OrderStatusDtlsByOrganisationId/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>")	
class OrderStatusDtlsByOrganisationId(Resource):
	def get(self,organisation_id,retailer_store_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `orderstatus_id`,`order_status`,
			color FROM `order_status_master` order by last_update_id asc""")

		statusList = cursor.fetchall()
		for i in range(len(statusList)):

			cursor.execute("""SELECT count(ipr.`request_id`)as total 
				FROM `instamojo_payment_request` ipr
				INNER JOIN `user_retailer_mapping` urm on urm.`user_id` = ipr.`user_id`
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE ipr.`status`=%s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and 
				ipr.`organisation_id`=%s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s""",(statusList[i]['order_status'],retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,brand_id))

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

#--------------------Loyality-Dashboard-------------------------#

@name_space_loyality_dashboard.route("/loyalityDashboard/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>")	
class loyalityDashboard(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id,brand_id):
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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`)=%s and 
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty' and `brand_id` = %s""")
			get_credited_customer_data = (organisation_id,today_date,organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id)

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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`)=%s and 
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and				 
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty' and `brand_id` = %s""")
			get_redeem_customer_data = (organisation_id,today_date,organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id)

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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`)=%s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty' and `brand_id` = %s""")
			get_credited_customer_data = (organisation_id,yesterday,organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id)

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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`)=%s and 
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty' and `brand_id` = %s""")
			get_redeem_customer_data = (organisation_id,yesterday,organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id)

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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >= %s and				
				date(wt.`last_update_ts`) <= %s and urm.`organisation_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s
				and urm.`retailer_store_id` = %s and wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty' and `brand_id` = %s""")
			get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id)

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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <= %s 
				and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty' and `brand_id` = %s""")
			get_redeem_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id)

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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >= %s and date(wt.`last_update_ts`) <= %s 
				and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty'  and `brand_id` = %s""")
			get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id)

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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <= %s 
				and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty' and `brand_id` = %s""")
			get_redeem_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id)

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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >= %s and date(wt.`last_update_ts`) <= %s 
				and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				wt.`transaction_source` != 'redeem' and wt.`transaction_source` != 'product_loyalty' and `brand_id` = %s""")
			get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id)

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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE wt.`organisation_id`=%s and date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <= %s 
				and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				wt.`transaction_source` = 'redeem' and wt.`transaction_source` != 'product_loyalty' and `brand_id` = %s""")
			get_redeem_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id)

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

#--------------------------Offer-Count-Detaile-By-Date-And-Organisation-And-Retail-Store-Id---------------------------#
@name_space_offer.route("/OfferCountDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>")	
class OfferCountDetailsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id,brand_id):
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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`)=%s and pbm.`brand_id` = %s""",(retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,today,brand_id))

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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
												INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
												INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
												INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
												INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
												WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,organisation_id,brand_id)
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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY and pbm.`brand_id` = %s""",(retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,brand_id))

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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm 
						INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
						INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
						WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pnm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,organisation_id,brand_id)
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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY and pbm.`brand_id` = %s""",(retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,brand_id))

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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
						INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
						INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
						WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,organisation_id,brand_id)
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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`) between %s and %s and pbm.`brand_id` = %s""",(retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,stday,today,brand_id))

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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
						INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
						INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`							
						WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,organisation_id,brand_id)
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
				INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
				INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
				INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE ipr.`coupon_code`!='' and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and
				cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and
				ipr.`organisation_id`=%s and date(ipr.`last_update_ts`) between %s and %s and pbm.`brand_id` = %s""",(retailer_store_id,organisation_id,organisation_id,organisation_id,organisation_id,slifetime,today,brand_id))

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
					get_user_retailer_query = ("""SELECT * FROM `user_retailer_mapping` urm
						INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
						INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id` 
						WHERE urm.`user_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s""")
					get_user_retailer_data = (data['customer_id'],retailer_store_id,organisation_id,organisation_id,organisation_id,brand_id)
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
@name_space_offer.route("/OfferCountDetailsByOfferId/<int:offer_id>/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>")	
class OfferCountDetailsByOfferId(Resource):
	def get(self,offer_id,organisation_id,retailer_store_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()
		
		cursor.execute("""SELECT count(ipr.`transaction_id`)as total FROM 
			`instamojo_payment_request` ipr
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id` 
			WHERE ipr.`coupon_code` in(SELECT 
			`coupon_code` FROM `offer` o WHERE o.`offer_id`=%s and o.`organisation_id` = %s) and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s""",(offer_id,organisation_id,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id))

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

@name_space_enquiry.route("/getEnquiryList/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>")	
class getEnquiryList(Resource):
	def get(self,organisation_id,retailer_store_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT em.`enquiry_id`,em.`user_id`,etm.`enquiry_type`,em.`enquiery_status`,em.`date_of_closer`,em.`last_update_ts`,a.`first_name`,a.`last_name`,a.`phoneno`
			FROM `enquiry_master` em
			INNER JOIN `enquiry_type_master` etm ON etm.`enquiry_type_id` = em.`enquiry_type_id`
			INNER JOIN `admins` a ON a.`admin_id` = em.`user_id`
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id` 
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE em.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			ORDER BY em.`enquiry_id` DESC""")

		get_data = (organisation_id,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id)
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

@name_space_exchange.route("/getCustomerExchangeWithPagination/<int:organisation_id>/<int:page>/<int:final_submission_status>/<int:exchange_status>/<string:start_date>/<string:end_date>/<int:retailer_store_id>/<int:brand_id>")	
class getCustomerExchangeWithPagination(Resource):
	def get(self,organisation_id,page,final_submission_status,exchange_status,start_date,end_date,retailer_store_id,brand_id):
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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = %s and ced.`status` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and urm.`retailer_store_id` = %s and pbm.`brand_id` = %s
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s
			LIMIT %s,20""")

		get_data = (organisation_id,final_submission_status,exchange_status,organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id,start_date,end_date,offset)
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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and ced.`final_submission_status` = %s and ced.`status` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and urm.`retailer_store_id` = %s and pbm.`brand_id` = %s
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s""")

		get_data_count = (organisation_id,final_submission_status,exchange_status,organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id,start_date,end_date)
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
@name_space_exchange.route("/CustomerExchangeSearch/<string:searchkey>/<int:organisation_id>/<int:page>/<int:retailer_store_id>/<int:brand_id>")	
class CustomerExchangeSearch(Resource):
	def get(self,searchkey,organisation_id,page,retailer_store_id,brand_id):
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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and urm.`retailer_store_id` = %s and pbm.`brand_id` = %s
			and (a.`first_name` LIKE %s or a.`last_name` LIKE %s or ced.`exchange_id` LIKE %s or a.`phoneno` LIKE %s or ced.`device_model` LIKE %s) LIMIT %s,20
			""")
		get_customer_exchange_data = (organisation_id,organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%",offset)

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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s  and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and urm.`retailer_store_id` = %s and pbm.`brand_id` = %s
			and (a.`first_name` LIKE %s or a.`last_name` LIKE %s or ced.`exchange_id` LIKE %s or a.`phoneno` LIKE %s or ced.`device_model` LIKE %s)""")

		get_data_count = (organisation_id,organisation_id,organisation_id,organisation_id,retailer_store_id,brand_id,"%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%","%"+searchkey+"%")
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
@name_space_exchange.route("/ExhcnageCountDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>")	
class ExhcnageCountDetailsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id,retailer_store_id,brand_id):
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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s and
			ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) = %s""")

			get_data = (organisation_id,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id,today_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) = %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) = %s """)

			get_data = (organisation_id,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id,yesterday)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) = %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s  and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			get_data = (organisation_id,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id,start_date,end_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			get_data = (organisation_id,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id,start_date,end_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
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
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 0 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)

			get_data = (organisation_id,organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id,start_date,end_date)
			cursor.execute(get_active_exchange_query_count,get_data)
			exchange_active_data = cursor.fetchone()
			active_count = exchange_active_data['exchange_count']


			get_complete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			and ced.`final_submission_status` = 1 and ced.`status` = 1 
			and DATE(ced.`last_update_ts`) >= %s and DATE(ced.`last_update_ts`) <= %s """)
			
			cursor.execute(get_complete_exchange_query_count,get_data)
			exchange_complete_data = cursor.fetchone()

			complete_count = exchange_complete_data['exchange_count']

			get_incolplete_exchange_query_count = ("""SELECT count(*) as exchange_count
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s
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

#--------------------miss-opportunity-List-------------------------#

@name_space_missopportunity.route("/missOpportunityList/<int:organisation_id>/<int:retailer_store_id>/<int:page>/<int:brand_id>")	
class missOpportunityList(Resource):
	def get(self,organisation_id,retailer_store_id,page,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT mo.`miss_opportunity_id`,mo.`customer_id`,mo.`product_id`,mo.`product_meta_id`,mo.`missopprtunity_product_name`,mo.`name_of_customer`,mo.`mobile_no`,mo.`email_id`,mo.`demo_given_by`,mo.`reason_for_non_closure`,mo.`follow_up_1`,mo.`follow_up_2`,mo.`remarks`,a.`first_name`,a.`phoneno`
			FROM `miss_opportunity` mo 	
			INNER JOIN `admins` a ON a.`admin_id` = mo.`customer_id`			
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = mo.`product_id`	
			WHERE mo.`organisation_id` = %s and mo.`retailer_store_store_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s""")

		get_data = (organisation_id,retailer_store_id,organisation_id,brand_id)
		cursor.execute(get_query,get_data)
		missopportunity_data = cursor.fetchall()

		for key,data in enumerate(missopportunity_data):
			if data['product_meta_id'] == 0:
				missopportunity_data[key]['product_name'] = ''
				missopportunity_data[key]['met_key_value'] = {}
			else:
				get_product_meta_query = ("""SELECT p.`product_name`,pm.`meta_key_text`
					FROM `product_meta` pm 		
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`	
					WHERE pm.`product_meta_id` = %s""")
				get_product_meta_data = (data['product_meta_id'])
				cursor.execute(get_product_meta_query,get_product_meta_data)
				product_meta_data = cursor.fetchone()
				missopportunity_data[key]['product_name'] = product_meta_data['product_name']

				if product_meta_data['meta_key_text'] :
					a_string = product_meta_data['meta_key_text']
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

						missopportunity_data[key]['met_key_value'] = met_key

		return ({"attributes": {
		    		"status_desc": "miss_opportunity_details",
		    		"status": "success"
		    	},
		    	"responseList":missopportunity_data}), status.HTTP_200_OK

#--------------------miss-opportunity-List-------------------------#

#-----------------------Product-List-By-Plan-Id-------------------------------#

@name_space_emi.route("/productListByPlanId/<int:plan_id>/<int:brad_id>")	
class productListByPlanId(Resource):
	def get(self,plan_id,brad_id):
		connection = mysql_connection()
		cursor = connection.cursor()


		get_product_query = ("""SELECT p.`product_id`,p.`product_name`,pm.`meta_key_text`,pm.`product_meta_id`,pm.`product_meta_code`
									FROM `product_plan_mapping` ppm
									INNER JOIN `product` p ON p.`product_id` = ppm.`product_id`
									INNER JOIN `product_meta` pm ON pm.`product_meta_id` = ppm.`product_meta_id`
									INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
									where ppm.`plan_id` = %s and pbm.`brand_id` = %s""")
		get_product_data = (plan_id,brad_id)
		product_data_count = cursor.execute(get_product_query,get_product_data)

		if product_data_count > 0:
			product_data = cursor.fetchall()
			for pkey,pdata in enumerate(product_data):

				get_query_images = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s order by default_image_flag desc """)
				getdata_images = (pdata['product_meta_id'])
				image_count = cursor.execute(get_query_images,getdata_images)
				image = cursor.fetchone()

				if image_count > 0:
					product_data[pkey]['image'] = image['image']
				else:
					product_data[pkey]['image'] = ""

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
			
		else:
			product_data  = []

		return ({"attributes": {
					    "status_desc": "finance_details",
					    "status": "success"
				},
				"responseList":product_data}), status.HTTP_200_OK

#-----------------------Product-List-By-Plan-Id-------------------------------#

#----------------------Catalog-List---------------------#
@name_space_catalouge.route("/catalogList/<int:organisation_id>/<int:brand_id>")	
class catalogList(Resource):
	def get(self,organisation_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
				FROM `catalogs`
				WHERE `organisation_id` = %s and `status` = 1 ORDER BY `sequence`""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)
		catalog_data = cursor.fetchall()

		for key,data in enumerate(catalog_data):
			get_product_query = ("""SELECT count(*) as product_count 
				FROM `product_catalog_mapping` pcm 
				INNER JOIN `product` p ON p.`product_id` = pcm .`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p .`product_id`
				WHERE pcm.`catalog_id` = %s and pbm.`brand_id` = %s""")
			get_product_data = (data['catalog_id'],brand_id)
			cursor.execute(get_product_query,get_product_data)
			catalog_product_count = cursor.fetchone()
			catalog_data[key]['product_count'] = catalog_product_count['product_count']

			get_category_query = ("""SELECT *
				FROM `catalog_category_mapping` ccm
				INNER JOIN `category` c ON c.`category_id` = ccm .`category_id`
				WHERE ccm.`catalog_id` = %s and ccm.`organisation_id` = %s""")
			get_category_data = (data['catalog_id'],organisation_id)
			count_category = cursor.execute(get_category_query,get_category_data)

			if count_category > 0:
				category_data = cursor.fetchone()
				catalog_data[key]['catalog_category'] = category_data['category_name']
			else:
				catalog_data[key]['catalog_category'] = ""

			catalog_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "catalog_details",
		    		"status": "success"
		    	},
		    	"responseList":catalog_data}), status.HTTP_200_OK

#----------------------Catalog-List---------------------#

#----------------------Get-Offer-List---------------------#	
@name_space_offer.route("/getOfferList/<int:organisation_id>/<int:brand_id>")	
class getOfferList(Resource):
	def get(self,organisation_id,brand_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `offer` where `organisation_id` = %s and `status` = 1""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)

		offer_data = cursor.fetchall()

		new_offer_data = []

		for key,data in enumerate(offer_data):
			if data['is_product_meta_offer'] == 1:

				product_meta_offer_mapping_query = (""" SELECT p.`product_id`,p.`product_name`,pmom.`product_meta_id`
						FROM `product_meta_offer_mapping` pmom						
						INNER JOIN `product` p ON p.`product_id` = pmom.`product_id` 
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
						where  pmom.`offer_id` = %s and p.`brand_id` = %s""")
				product_meta_offer_mapping_data = (data['offer_id'],brand_id)
				count_product_meta_offer_mapping_data = cursor.execute(product_meta_offer_mapping_query,product_meta_offer_mapping_data)

				if count_product_meta_offer_mapping_data > 0:
					offer_product_meta = cursor.fetchall()

					for omkey,omdata in enumerate(offer_product_meta):
						get_product_meta_information_query = ("""SELECT pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,pm.`loyalty_points`
								FROM `product_meta` pm
								WHERE pm.`product_meta_id` = %s""")
						get_product_meta_information_data = (omdata['product_meta_id'])
						cursor.execute(get_product_meta_information_query,get_product_meta_information_data)

						product_meta_data = cursor.fetchone()

						if product_meta_data['meta_key_text'] :
							a_string = product_meta_data['meta_key_text']
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

								product_meta_data['met_key_value'] = met_key

						offer_product_meta[omkey]['in_price'] = product_meta_data['in_price']
						offer_product_meta[omkey]['out_price'] = product_meta_data['out_price']
						offer_product_meta[omkey]['met_key_value'] = product_meta_data['met_key_value']

						get_product_meta_with_image_query = ("""SELECT pmi.`image` 
							FROM  `product_meta_images` pmi
							where pmi.`product_meta_id` = %s and is_gallery = 0  and image_type = 1 order by default_image_flag desc""")
						get_product_meta_with_image_data = (omdata['product_meta_id'])
						count_product_meta_image = cursor.execute(get_product_meta_with_image_query,get_product_meta_with_image_data)

						if count_product_meta_image > 0:

							product_meta_image_data = cursor.fetchone()

							offer_product_meta[omkey]['image'] = product_meta_image_data['image']
						else:
							offer_product_meta[omkey]['image'] = ""

					offer_data[key]['product_data'] = offer_product_meta
				else:
					offer_data[key]['product_data'] = []

			else:
				get_offer_product_query = ("""SELECT p.`product_id`,p.`product_name`
					FROM `product_offer_mapping` pom
					INNER JOIN `product` p ON p.`product_id` = pom.`product_id`
					INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
					where pom.`offer_id` = %s and pbm.`brand_id` = %s""")
				get_product_offer_data = (data['offer_id'],brand_id)
				count_product_offer  = cursor.execute(get_offer_product_query,get_product_offer_data)

				if count_product_offer > 0:
					product_offer_data = cursor.fetchall()

					for okey,odata in enumerate(product_offer_data):						
						get_product_meta_with_image_query = ("""SELECT pmi.`image` 
							FROM `product_meta` pm
							INNER JOIN `product_meta_images` pmi ON pmi.`product_meta_id` = pm.`product_meta_id`
							where pm.`product_id` = %s and is_gallery = 0  and image_type = 1 order by default_image_flag desc""")
						get_product_meta_with_image_data = (odata['product_id'])
						count_product_meta_image = cursor.execute(get_product_meta_with_image_query,get_product_meta_with_image_data)

						if count_product_meta_image > 0:

							product_meta_image_data = cursor.fetchone()

							product_offer_data[okey]['image'] = product_meta_image_data['image']
						else:
							product_offer_data[okey]['image'] = ""

						product_offer_data[okey]['product_meta_id'] = 0	
						product_offer_data[okey]['in_price'] = 0
						product_offer_data[okey]['out_price'] = 0
						product_offer_data[okey]['met_key_value'] = {}


					offer_data[key]['product_data'] = product_offer_data
				else:
					offer_data[key]['product_data'] = []
		

			get_query_image = ("""SELECT `offer_image` FROM `offer_images` WHERE `offer_id` = %s""")
			getdata_image = (data['offer_id'])
			image_count = cursor.execute(get_query_image,getdata_image)			

			if image_count > 0:
				offer_images = cursor.fetchall()

				image_a = []

				for image in offer_images:
					image_a.append(image['offer_image'])

				offer_data[key]['images'] = image_a
			else:
				offer_data[key]['images'] = []

			offer_data[key]['last_update_ts'] = str(data['last_update_ts'])	


		for key,data in enumerate(offer_data):
			if data['product_data']:
				new_offer_data.append(offer_data[key])	

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "offer_details",
		    		"status": "success"
		    	},
		    	"responseList":new_offer_data}), status.HTTP_200_OK

#----------------------Get-Offer-List---------------------#

#----------------------Recent-Product-List---------------------#
@name_space_product.route("/RectproductListFromProductOrganisationMapping/<int:organisation_id>/<int:brand_id>")	
class RecentproductListFromProductOrganisationMapping(Resource):	
	def get(self,organisation_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		get_query = ("""SELECT p.`product_id`,p.`product_name`,pom.`product_status`
				FROM `product_organisation_mapping` pom				
				INNER JOIN `product` p ON p.`product_id` = pom.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE  pom.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s ORDER BY p.`product_id` DESC limit 10""")
		get_data = (organisation_id,organisation_id,brand_id)
		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()		

		for key,data in enumerate(product_data):
			get_query_meta = (""" SELECT pm.`product_meta_id` from `product_meta` pm where pm.`product_id` = %s""")
			get_data_meta = (data['product_id'])
			count_product_meta = cursor.execute(get_query_meta,get_data_meta)

			if count_product_meta > 0:
				get_data_product_meta = cursor.fetchone()

				get_query_meta_count = ("""SELECT count(*) as `product_meta_count`  from `product_meta` pm where pm.`product_id` = %s""")
				get_data_meta_count = (data['product_id'])
				cursor.execute(get_query_meta_count,get_data_meta_count)
				product_meta = cursor.fetchone()
				product_data[key]['product_meta_count'] = product_meta['product_meta_count']									

				get_query_images = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s """)
				getdata_images = (get_data_product_meta['product_meta_id'])
				image_count = cursor.execute(get_query_images,getdata_images)
				image = cursor.fetchone()

				if image_count > 0:
					product_data[key]['image'] = image['image']
				else:
					product_data[key]['image'] = ""
			else:
				product_data[key]['product_meta_count'] = 0
				product_data[key]['image'] = ""

			get_offer_product =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,
				o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`is_online`,o.`instruction`,o.`status`
			FROM `product_offer_mapping` pom 
			INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id` 
			WHERE pom.`organisation_id` = %s and pom.`product_id` = %s""")
			get_offer_data = (organisation_id,data['product_id'])
			count_offer_product = cursor.execute(get_offer_product,get_offer_data)
			if count_offer_product > 0:
				offer_product = cursor.fetchall()
				product_data[key]['offer_product'] = offer_product
			else:
				product_data[key]['offer_product'] = []

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Recent-Product-List---------------------#

#----------------------Get-Brnad-List---------------------#
@name_space_product.route("/getBrandListByCategoryId/<int:organisation_id>/<int:category_id>/<int:brand_id>")	
class getBrandListByCategoryId(Resource):
	def get(self,organisation_id,category_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_brand_query = ("""SELECT `brand_id`
			FROM `category_brand_mapping`  WHERE `organisation_id` = %s and `category_id` = %s and `brand_id` = %s""")
		get_brand_data = (organisation_id,category_id,brand_id)

		count_category_brand = cursor.execute(get_brand_query,get_brand_data)

		if count_category_brand > 0:

			brand_data = cursor.fetchall()
			brand_data.append({"brand_id":0})

			for hkey,hdata in enumerate(brand_data):
				if hdata['brand_id'] == 0:
					brand_data[hkey]['meta_key_value'] = "Others"
					brand_data[hkey]['image'] = ""

					get_product_brand_query = ("""SELECT count(pom.`product_id`) as product_brand_count 
						FROM `product_organisation_mapping` pom 
						INNER JOIN `product` p ON p.`product_id` = pom.`product_id` 
						WHERE pom.`product_id` not in (select `product_id` from product_brand_mapping where organisation_id = %s) 
						and pom.`organisation_id` = %s and p.`category_id` = %s""")
					get_product_brand_data = (organisation_id,organisation_id,category_id)
					cursor.execute(get_product_brand_query,get_product_brand_data)
					product_brand_data = cursor.fetchone()
					brand_data[hkey]['product_count'] = product_brand_data['product_brand_count']

				else:
					get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
					FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

					getdata_key_value = (hdata['brand_id'])
					cursor.execute(get_key_value_query,getdata_key_value)

					key_value_data = cursor.fetchone()

					brand_data[hkey]['meta_key_value'] = key_value_data['meta_key_value']
					brand_data[hkey]['image'] = key_value_data['image']

					get_product_brand_query = (""" SELECT count(*) as product_brand_count
				 	FROM `product_brand_mapping` pbm 
				 	INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`			 	
				 	where pbm.`organisation_id` = %s and pbm.`brand_id` = %s and p.`category_id` = %s""")
					get_product_brand_data = (organisation_id,hdata['brand_id'],category_id)
					cursor.execute(get_product_brand_query,get_product_brand_data)

					product_brand_data = cursor.fetchone()

					brand_data[hkey]['product_count'] = product_brand_data['product_brand_count']


		else:
			brand_data = []

		return ({"attributes": {
		    	"status_desc": "offer_details",
		    	"status": "success"
		    },
		    "responseList":brand_data}), status.HTTP_200_OK


#----------------------Get-Brnad-List---------------------#

#----------------------Product-List---------------------#
@name_space_product.route("/RectproductListByCategoryIdFromProductOrganisationMapping/<int:organisation_id>/<int:category_id>/<int:brand_id>")	
class RectproductListByCategoryIdFromProductOrganisationMapping(Resource):	
	def get(self,organisation_id,category_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		get_query = ("""SELECT p.`product_id`,p.`product_name`,pom.`product_status`
				FROM `product_organisation_mapping` pom				
				INNER JOIN `product` p ON p.`product_id` = pom.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				WHERE  pom.`organisation_id` = %s  and p.`category_id` = %s and pbm.`brand_id` = %s and pbm.`organisation_id` = %s ORDER BY p.`product_id` DESC limit 10""")
		get_data = (organisation_id,category_id,brand_id,organisation_id)
		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()		

		for key,data in enumerate(product_data):
			get_query_meta = (""" SELECT pm.`product_meta_id` from `product_meta` pm where pm.`product_id` = %s""")
			get_data_meta = (data['product_id'])
			count_product_meta = cursor.execute(get_query_meta,get_data_meta)

			if count_product_meta > 0:
				get_data_product_meta = cursor.fetchone()

				get_query_meta_count = ("""SELECT count(*) as `product_meta_count`  from `product_meta` pm where pm.`product_id` = %s""")
				get_data_meta_count = (data['product_id'])
				cursor.execute(get_query_meta_count,get_data_meta_count)
				product_meta = cursor.fetchone()
				product_data[key]['product_meta_count'] = product_meta['product_meta_count']									

				get_query_images = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s """)
				getdata_images = (get_data_product_meta['product_meta_id'])
				image_count = cursor.execute(get_query_images,getdata_images)
				image = cursor.fetchone()

				if image_count > 0:
					product_data[key]['image'] = image['image']
				else:
					product_data[key]['image'] = ""
			else:
				product_data[key]['product_meta_count'] = 0
				product_data[key]['image'] = ""

			get_offer_product =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,
				o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`is_online`,o.`instruction`,o.`status`
			FROM `product_offer_mapping` pom 
			INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id` 
			WHERE pom.`organisation_id` = %s and pom.`product_id` = %s""")
			get_offer_data = (organisation_id,data['product_id'])
			count_offer_product = cursor.execute(get_offer_product,get_offer_data)
			if count_offer_product > 0:
				offer_product = cursor.fetchall()
				product_data[key]['offer_product'] = offer_product
			else:
				product_data[key]['offer_product'] = []

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Customer-Exchange---------------------#

@name_space_exchange.route("/getCustomerExchangeWithOutPagination/<int:organisation_id>/<int:retailer_store_id>/<int:brand_id>")	
class getCustomerExchangeWithOutPagination(Resource):
	def get(self,organisation_id,retailer_store_id,brand_id):	

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT ced.`exchange_id`,ced.`amount`,ced.`front_image`,ced.`back_image`,ced.`device_model`,ced.`last_update_ts`,a.`first_name`,a.`last_name`,ced.`status`,a.`admin_id` as `user_id`,a.`phoneno`,ced.`final_submission_status`,ced.`Is_clone`
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`
			INNER JOIN `customer_product_mapping` cpm ON cpm.`customer_id` = urm.`user_id` 
			INNER JOIN `product_meta` pm ON pm.`product_meta_id` = cpm.`product_meta_id`
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
			WHERE ced.`organisation_id` = %s and urm.`retailer_store_id` = %s and cpm.`organisation_id` = %s and pbm.`organisation_id` = %s and pbm.`brand_id` = %s and
			ced.`final_submission_status` = 1 ORDER BY ced.`exchange_id` DESC LIMIT 10 """)

		get_data = (organisation_id,retailer_store_id,organisation_id,organisation_id,brand_id)
		cursor.execute(get_query,get_data)

		print(cursor._last_executed)

		customer_exchange_data = cursor.fetchall()

		for key,data in enumerate(customer_exchange_data):
			#customer_exchange_data[key]['exchange_id'] = "AMEXCHANGE-"+str(data['exchange_id'])
			customer_exchange_data[key]['last_update_ts'] = str(data['last_update_ts'])		
				
		return ({"attributes": {
		    		"status_desc": "customer_exchange_data",
		    		"status": "success"	
		    	},
		    	"responseList":customer_exchange_data}), status.HTTP_200_OK

#----------------------Customer-Exchange---------------------#
