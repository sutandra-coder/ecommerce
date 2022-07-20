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
def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

ecommerce_campaign = Blueprint('ecommerce_campaign_api', __name__)
api = Api(ecommerce_campaign,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceCampaign',description='Ecommerce Campaign')

campaign_postmodel = api.model('campaign', {
	"campaign_name":fields.String(required=True),
	"sms_content":fields.String,
	"email_image":fields.String,
	"email_content":fields.String,
	"app_image":fields.String,
	"app_content":fields.String,
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

audience_postmodel = api.model('audience', {
	"audience_name":fields.String(required=True),
	"audience_user_gretter_value":fields.Integer,
	"audience_user_less_value":fields.Integer,
	"audience_user_brand_id":fields.Integer,
	"audience_user_retailer_id":fields.Integer,
	"audience_last_purchase_date":fields.String,
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

#----------------------Add-Campaign---------------------#

@name_space.route("/AddCampaign")
class AddCampaign(Resource):
	@api.expect(campaign_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		campaign_name = details['campaign_name']		
		sms_content = details['sms_content']
		email_image = details['email_image']
		email_content = details['email_content']
		app_image = details['app_image']
		app_content = details['app_content']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']


		insert_query = ("""INSERT INTO `campaign`(`campaign_name`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s)""")

		data = (campaign_name,organisation_id,last_update_id)
		cursor.execute(insert_query,data)

		campaign_id = cursor.lastrowid

		if campaign_id >0:
			insert_campaing_sms_query = ("""INSERT INTO `campaign_sms`(`campaign_id`,`content`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")

			sms_data = (campaign_id,sms_content,organisation_id,last_update_id)
			cursor.execute(insert_campaing_sms_query,sms_data)

			insert_campaing_email_query = ("""INSERT INTO `campaign_email`(`campaign_id`,`content`,`image`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")

			email_data = (campaign_id,email_content,email_image,organisation_id,last_update_id)
			cursor.execute(insert_campaing_email_query,email_data)

			insert_campaing_app_query = ("""INSERT INTO `campaign_pushnotification`(`campaign_id`,`content`,`image`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")

			app_data = (campaign_id,app_content,app_image,organisation_id,last_update_id)
			cursor.execute(insert_campaing_app_query,app_data)


		return ({"attributes": {
			    		"status_desc": "campaign_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Campaign---------------------#

#----------------------Campaign-List---------------------#
@name_space.route("/getCampaignList/<int:organisation_id>")	
class getCampaignList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT c.`campaign_id`,c.`campaign_name`,cs.`content` sms_content,ce.`content` email_content,
			ce.`image` email_image,cn.`content` app_content,cn.`image` app_image
			FROM `campaign` c 
			INNER JOIN `campaign_sms` cs ON cs.`campaign_id` = c.`campaign_id`
			INNER JOIN `campaign_email` ce ON ce.`campaign_id` = c.`campaign_id`
			INNER JOIN `campaign_pushnotification` cn ON cn.`campaign_id` = c.`campaign_id`
			WHERE  c.`organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		campaign_data = cursor.fetchall()
		
				
		return ({"attributes": {
		    		"status_desc": "campaign_details",
		    		"status": "success"
		    	},
		    	"responseList":campaign_data}), status.HTTP_200_OK

#----------------------Campaign-List---------------------#

#----------------------Campaign-Details--------------------#

@name_space.route("/getCampaignDetails/<int:campaign_id>")	
class getCampaignDetails(Resource):
	def get(self,campaign_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT c.`campaign_id`,c.`campaign_name`,cs.`content` sms_content,ce.`content` email_content,
			ce.`image` email_image,cn.`content` app_content,cn.`image` app_image
			FROM `campaign` c 
			INNER JOIN `campaign_sms` cs ON cs.`campaign_id` = c.`campaign_id`
			INNER JOIN `campaign_email` ce ON ce.`campaign_id` = c.`campaign_id`
			INNER JOIN `campaign_pushnotification` cn ON cn.`campaign_id` = c.`campaign_id`
			WHERE  c.`campaign_id` = %s""")

		get_data = (campaign_id)
		cursor.execute(get_query,get_data)

		campaign_data = cursor.fetchone()		
				
		return ({"attributes": {
		    		"status_desc": "campaign_details",
		    		"status": "success"
		    	},
		    	"responseList":campaign_data}), status.HTTP_200_OK

#----------------------Campaign-Details--------------------#

#----------------------Update-Campaign--------------------#

@name_space.route("/UpdateCampaign/<int:campaign_id>")
class UpdateCampaign(Resource):
	@api.expect(campaign_postmodel)
	def put(self,campaign_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		campaign_name = details['campaign_name']		

		update_campaign_query = ("""UPDATE `campaign` SET `campaign_name` = %s
					WHERE `campaign_id` = %s """)
		update_campaign_data = (campaign_name,campaign_id)
		cursor.execute(update_campaign_query,update_campaign_data)

		if details and "sms_content" in details:
			sms_content = details['sms_content']
			update_campaign_sms_query = ("""UPDATE `campaign_sms` SET `content` = %s
					WHERE `campaign_id` = %s """)
			update_campaign_sms_data = (sms_content,campaign_id)
			cursor.execute(update_campaign_sms_query,update_campaign_sms_data)

		if details and "email_image" in details:
			email_image = details['email_image']				
			update_query = ("""UPDATE `campaign_email` SET `image` = %s
				WHERE `campaign_id` = %s """)
			update_data = (email_image,campaign_id)
			cursor.execute(update_query,update_data)

		if details and "email_content" in details:
			email_content = details['email_content']				
			update_query = ("""UPDATE `campaign_email` SET `content` = %s
				WHERE `campaign_id` = %s """)
			update_data = (email_content,campaign_id)
			cursor.execute(update_query,update_data)

		if details and "app_image" in details:			
			app_image = details['app_image']
			update_campaign_push_query = ("""UPDATE `campaign_pushnotification` SET `image` = %s
						WHERE `campaign_id` = %s """)
			update_campaign_push_data = (app_image,campaign_id)
			cursor.execute(update_campaign_push_query,update_campaign_push_data)

		if details and "app_content" in details:
			app_content = details['app_content']
			update_campaign_push_query = ("""UPDATE `campaign_pushnotification` SET `content` = %s
						WHERE `campaign_id` = %s """)
			update_campaign_push_data = (app_content,campaign_id)
			cursor.execute(update_campaign_push_query,update_campaign_push_data)


		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Campaign",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK



#----------------------Update-Campaign--------------------#

#----------------------Add-Audience---------------------#

@name_space.route("/AddAudience")
class AddAudience(Resource):
	@api.expect(audience_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		audience_name = details['audience_name']		
		audience_user_gretter_value = details['audience_user_gretter_value']
		audience_user_less_value = details['audience_user_less_value']
		audience_user_brand_id = details['audience_user_brand_id']
		audience_user_retailer_id = details['audience_user_retailer_id']
		audience_last_purchase_date = details['audience_last_purchase_date']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']


		insert_query = ("""INSERT INTO `audience`(`audience_name`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s)""")

		data = (audience_name,organisation_id,last_update_id)
		cursor.execute(insert_query,data)

		audience_id = cursor.lastrowid

		if audience_id >0:
			insert_audience_user_value_query = ("""INSERT INTO `audience_user_value`(`audience_id`,`less_value`,`gretter_value`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")

			audience_user_value_data = (audience_id,audience_user_less_value,audience_user_gretter_value,organisation_id,last_update_id)
			cursor.execute(insert_audience_user_value_query,audience_user_value_data)

			insert_audience_user_brand_query = ("""INSERT INTO `audience_user_brand`(`audience_id`,`brand_id`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")

			audience_user_brand_data = (audience_id,audience_user_brand_id,organisation_id,last_update_id)
			cursor.execute(insert_audience_user_brand_query,audience_user_brand_data)

			insert_audience_user_retailer_query = ("""INSERT INTO `audience_user_retailer`(`audience_id`,`retailer_id`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")

			audience_user_retailer_data = (audience_id,audience_user_retailer_id,organisation_id,last_update_id)
			cursor.execute(insert_audience_user_retailer_query,audience_user_retailer_data)

			insert_audience_user_last_purchase_date_query = ("""INSERT INTO `audience_user_last_purchase_date`(`audience_id`,`last_purchase_date`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")

			audience_user_last_purchase_date = (audience_id,audience_last_purchase_date,organisation_id,last_update_id)
			cursor.execute(insert_audience_user_last_purchase_date_query,audience_user_last_purchase_date)


		return ({"attributes": {
			    		"status_desc": "audience_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Audience---------------------#

#----------------------Audience-List---------------------#
@name_space.route("/getAudienceList/<int:organisation_id>")	
class getAudienceList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT a.`audience_id`,a.`audience_name`,au.`less_value`,au.`gretter_value`,
			alpd.`last_purchase_date`
			FROM `audience` a 
			INNER JOIN `audience_user_value` au ON au.`audience_id` = a.`audience_id`
			INNER JOIN `audience_user_brand` ab ON ab.`audience_id` = a.`audience_id`
			INNER JOIN `audience_user_retailer` ar ON ar.`audience_id` = a.`audience_id`			
			INNER JOIN `audience_user_last_purchase_date` alpd ON alpd.`audience_id` = a.`audience_id`
			WHERE  a.`organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		audience_data = cursor.fetchall()

		for key,data in enumerate(audience_data):
			audience_data[key]['last_purchase_date'] = str(data['last_purchase_date'])
		
				
		return ({"attributes": {
		    		"status_desc": "campaign_details",
		    		"status": "success"
		    	},
		    	"responseList":audience_data}), status.HTTP_200_OK

#----------------------Audience-List---------------------#

#----------------------Audience-Details---------------------#
@name_space.route("/getAudienceDetails/<int:audience_id>")	
class getAudienceDetails(Resource):
	def get(self,audience_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT a.`audience_id`,a.`audience_name`,au.`less_value`,au.`gretter_value`,
			alpd.`last_purchase_date`,ab.`brand_id`,ar.`retailer_id`
			FROM `audience` a 
			INNER JOIN `audience_user_value` au ON au.`audience_id` = a.`audience_id`
			INNER JOIN `audience_user_brand` ab ON ab.`audience_id` = a.`audience_id`
			INNER JOIN `audience_user_retailer` ar ON ar.`audience_id` = a.`audience_id`			
			INNER JOIN `audience_user_last_purchase_date` alpd ON alpd.`audience_id` = a.`audience_id`
			WHERE  a.`audience_id` = %s""")

		get_data = (audience_id)
		cursor.execute(get_query,get_data)

		audience_data = cursor.fetchone()
		
		audience_data['last_purchase_date'] = str(audience_data['last_purchase_date'])
		
				
		return ({"attributes": {
		    		"status_desc": "campaign_details",
		    		"status": "success"
		    	},
		    	"responseList":audience_data}), status.HTTP_200_OK

#----------------------Audience-Details---------------------#

#----------------------Update-Campaign--------------------#

@name_space.route("/UpdateAudience/<int:audience_id>")
class UpdateAudience(Resource):
	@api.expect(audience_postmodel)
	def put(self,audience_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		audience_name = details['audience_name']		

		update_audience_query = ("""UPDATE `audience` SET `audience_name` = %s
					WHERE `audience_id` = %s """)
		update_audience_data = (audience_name,audience_id)
		cursor.execute(update_audience_query,update_audience_data)

		if details and "audience_user_less_value" in details:
			audience_user_less_value = details['audience_user_less_value']
			update_audience_less_value_query = ("""UPDATE `audience_user_value` SET `less_value` = %s
					WHERE `audience_id` = %s """)
			update_audienceless_value_data = (audience_user_less_value,audience_id)
			cursor.execute(update_audience_less_value_query,update_audienceless_value_data)

		if details and "audience_user_gretter_value" in details:
			audience_user_gretter_value = details['audience_user_gretter_value']
			update_audience_gretter_value_query = ("""UPDATE `audience_user_value` SET `gretter_value` = %s
					WHERE `audience_id` = %s """)
			update_audiencegretter_value_data = (audience_user_gretter_value,audience_id)
			cursor.execute(update_audience_gretter_value_query,update_audiencegretter_value_data)

		if details and "audience_user_brand_id" in details:
			audience_user_brand_id = details['audience_user_brand_id']				
			update_query = ("""UPDATE `audience_user_brand` SET `brand_id` = %s
				WHERE `audience_id` = %s """)
			update_data = (audience_user_brand_id,audience_id)
			cursor.execute(update_query,update_data)

		if details and "audience_user_retailer_id" in details:
			audience_user_retailer_id = details['audience_user_retailer_id']				
			update_query = ("""UPDATE `audience_user_retailer` SET `retailer_id` = %s
				WHERE `audience_id` = %s """)
			update_data = (audience_user_retailer_id,audience_id)
			cursor.execute(update_query,update_data)

		if details and "audience_last_purchase_date" in details:			
			audience_last_purchase_date = details['audience_last_purchase_date']
			update_query = ("""UPDATE `audience_user_last_purchase_date` SET `last_purchase_date` = %s
						WHERE `audience_id` = %s """)
			update_data = (audience_last_purchase_date,audience_id)
			cursor.execute(update_query,update_data)


		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Adudience",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK



#----------------------Update-Campaign--------------------#

#----------------------Order-History-Full---------------------#

@name_space.route("/orderHistoryFull/<int:brand_id>/<int:greatterthan_value>/<int:lessthan_value>/<int:organisation_id>/<int:retailer_id>/<string:last_purchase_date>")	
class orderHistoryFull(Resource):
	def get(self,brand_id,greatterthan_value,lessthan_value,retailer_id,organisation_id,last_purchase_date):

		connection = mysql_connection()
		cursor = connection.cursor()

		if retailer_id == 0:

			get_query = ("""SELECT DISTINCT ipr.`user_id`,ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,
			a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`,
			a.`email`,a.`admin_id`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE  ipr.`organisation_id` = %s
			and ipr.`amount` >= %s and ipr.`amount` <= %s and DATE(ipr.`last_update_ts`) = %s
			GROUP BY ipr.`user_id` """)

			getData = (organisation_id,greatterthan_value,lessthan_value,last_purchase_date)

		else:
			get_query = ("""SELECT DISTINCT ipr.`user_id`,ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,
			a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`,
			a.`email`,a.`admin_id`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE  ipr.`organisation_id` = %s
			and ipr.`amount` >= %s and ipr.`amount` <= %s and ur.`retailer_id` = %s and DATE(ipr.`last_update_ts`) = %s
			GROUP BY ipr.`user_id` """)

			getData = (organisation_id,greatterthan_value,lessthan_value,retailer_id,last_purchase_date)
			
		count = cursor.execute(get_query,getData)

		new_order_data = []
		if count > 0:
			order_data = cursor.fetchall()

			for key,data in enumerate(order_data):
				product_status = "o"
				if brand_id == 0:
					customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
					pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
					FROM `order_product` op
					INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
					INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
					INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
					where op.`transaction_id` = %s and cpm.`product_status` = %s""")	

					customer_product_data = (data['transaction_id'],product_status)
				else:	
					customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
						pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
						FROM `order_product` op
						INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
						INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
						INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
						INNER JOIN `product_brand_mapping` pb ON pb.`product_id` = p.`product_id`
						where op.`transaction_id` = %s and cpm.`product_status` = %s and pb.`brand_id`=%s""")	

					customer_product_data = (data['transaction_id'],product_status,brand_id)

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

					order_data[key]['customer_product'] = customer_product
					order_data[key]['last_update_ts'] = str(data['last_update_ts'])

			for nkey,ndata in enumerate(order_data):
				if "customer_product" in ndata:
					new_order_data.append(ndata)

			return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
					"responseList":new_order_data}), status.HTTP_200_OK

		else:

			return ({"attributes": {
			    		"status_desc": "order_history",
			    		"status": "success"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

#----------------------Order-History-Full---------------------#

#----------------------Order-History-without-Brand---------------------#

@name_space.route("/orderHistoryWithOutBrand/<int:greatterthan_value>/<int:lessthan_value>/<int:organisation_id>/<int:retailer_id>/<string:last_purchase_date>")	
class orderHistoryWithOutBrand(Resource):
	def get(self,greatterthan_value,lessthan_value,retailer_id,organisation_id,last_purchase_date):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT DISTINCT ipr.`user_id`,ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,
			a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`,
			a.`email`,a.`admin_id`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE  ipr.`organisation_id` = %s
			and ipr.`amount` >= %s and ipr.`amount` <= %s and ur.`retailer_id` = %s and DATE(ipr.`last_update_ts`) = %s
			GROUP BY ipr.`user_id`""")

		getData = (organisation_id,greatterthan_value,lessthan_value,retailer_id,last_purchase_date)
			
		count = cursor.execute(get_query,getData)

		new_order_data = []
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
					where op.`transaction_id` = %s and cpm.`product_status` = %s""")	

				customer_product_data = (data['transaction_id'],product_status)
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

					order_data[key]['customer_product'] = customer_product
					order_data[key]['last_update_ts'] = str(data['last_update_ts'])

			for nkey,ndata in enumerate(order_data):
				if "customer_product" in ndata:
					new_order_data.append(ndata)

			return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
					"responseList":new_order_data}), status.HTTP_200_OK

		else:

			return ({"attributes": {
			    		"status_desc": "order_history",
			    		"status": "success"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

#----------------------Order-History-without-Brand---------------------#

#----------------------Order-History-Full-with-retailer-Id---------------------#

@name_space.route("/orderHistorywithretailerId/<int:organisation_id>/<int:retailer_id>")	
class orderHistorywithretailerId(Resource):
	def get(self,retailer_id,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT DISTINCT ipr.`user_id`,ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,
			a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`,
			a.`email`,a.`admin_id`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE  ipr.`organisation_id` = %s and ur.`retailer_id` = %s 
			GROUP BY ipr.`user_id` """)

		getData = (organisation_id,retailer_id)
			
		count = cursor.execute(get_query,getData)

		new_order_data = []
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
					INNER JOIN `product_brand_mapping` pb ON pb.`product_id` = p.`product_id`
					where op.`transaction_id` = %s and cpm.`product_status` = %s""")	

				customer_product_data = (data['transaction_id'],product_status)

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

					order_data[key]['customer_product'] = customer_product
					order_data[key]['last_update_ts'] = str(data['last_update_ts'])

			for nkey,ndata in enumerate(order_data):
				if "customer_product" in ndata:
					new_order_data.append(ndata)

			return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
					"responseList":new_order_data}), status.HTTP_200_OK

		else:

			return ({"attributes": {
			    		"status_desc": "order_history",
			    		"status": "success"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

#----------------------Order-History-Full-with-retailer-Id---------------------#

#----------------------Order-History-Full-with-brand-Id---------------------#

@name_space.route("/orderHistorywithbrandId/<int:organisation_id>/<int:brand_id>")	
class orderHistorywithbrandId(Resource):
	def get(self,organisation_id,brand_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT DISTINCT ipr.`user_id`,ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,
			a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`,
			a.`email`,a.`admin_id`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE  ipr.`organisation_id` = %s
			GROUP BY ipr.`user_id` """)

		getData = (organisation_id)
			
		count = cursor.execute(get_query,getData)

		new_order_data = []
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
					INNER JOIN `product_brand_mapping` pb ON pb.`product_id` = p.`product_id`
					where op.`transaction_id` = %s and cpm.`product_status` = %s and pb.`brand_id`=%s""")	

				customer_product_data = (data['transaction_id'],product_status,brand_id)

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

					order_data[key]['customer_product'] = customer_product
					order_data[key]['last_update_ts'] = str(data['last_update_ts'])

			for nkey,ndata in enumerate(order_data):
				if "customer_product" in ndata:
					new_order_data.append(ndata)

			return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
					"responseList":new_order_data}), status.HTTP_200_OK

		else:

			return ({"attributes": {
			    		"status_desc": "order_history",
			    		"status": "success"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

#----------------------Order-History-Full-with-brand-Id---------------------#

#----------------------Order-History-with-Value-Range---------------------#

@name_space.route("/orderHistoryWithValueRange/<int:greatterthan_value>/<int:lessthan_value>/<int:organisation_id>")	
class orderHistoryWithValueRange(Resource):
	def get(self,greatterthan_value,lessthan_value,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()		

		get_query = ("""SELECT DISTINCT ipr.`user_id`,ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,
			a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`,
			a.`email`,a.`admin_id`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE  ipr.`organisation_id` = %s
			and ipr.`amount` >= %s and ipr.`amount` <= %s
			GROUP BY ipr.`user_id` """)

		getData = (organisation_id,greatterthan_value,lessthan_value)		
			
		count = cursor.execute(get_query,getData)

		new_order_data = []
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
					where op.`transaction_id` = %s and cpm.`product_status` = %s""")	

				customer_product_data = (data['transaction_id'],product_status)
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

					order_data[key]['customer_product'] = customer_product
					order_data[key]['last_update_ts'] = str(data['last_update_ts'])

			for nkey,ndata in enumerate(order_data):
				if "customer_product" in ndata:
					new_order_data.append(ndata)

			return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
					"responseList":new_order_data}), status.HTTP_200_OK

		else:

			return ({"attributes": {
			    		"status_desc": "order_history",
			    		"status": "success"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

#----------------------Order-History-Full---------------------#
