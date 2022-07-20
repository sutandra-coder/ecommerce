from pyfcm import FCMNotification
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
import string
import random

ecommerce_emi = Blueprint('ecommerce_emi_api', __name__)
api = Api(ecommerce_emi,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceEmi',description='Ecommerce EMI')

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

copy_finance_model = api.model('SelectFinance',{
	"emi_bank_id":fields.List(fields.Integer),	
	"organisation_id":fields.Integer(required=True)
})

plan_model = api.model('SelectPlan',{
	"emi_bank_name": fields.String(required=True),	
	"organisation_id":fields.Integer(required=True)
})

product_plan_model = api.model('ProductPlan',{
	"plan_id": fields.Integer(required=True),
	"product_meta_id": fields.Integer(required=True),
	"product_id": fields.Integer(required=True),
	"organisation_id": fields.Integer(required=True)
})

finance_putmodel = api.model('finance_putmodel',{
	"status": fields.Integer
})

finance_brand_model = api.model('finance_putmodel',{
	"brand_id":fields.List(fields.Integer),
	"emi_bank_id": fields.Integer(required=True),
	"organisation_id": fields.Integer(required=True)
})

push_notification_model = api.model('push_notification_model',{
	"brand_id":fields.Integer(required=True),
	"emi_bank_id": fields.Integer(required=True),
	"user_id": fields.Integer(required=True),
	"organisation_id": fields.Integer(required=True)
})


appmsg_model = api.model('appmsg_model', {	
	"firebase_key":fields.String(),
	"device_id":fields.String(),
	"organisation_id":fields.Integer(required=True)
})


BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#-----------------------Finance-List-------------------------------#

@name_space.route("/financeList/<int:organisation_id>")	
class financeList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()


		get_query = ("""SELECT * FROM `emi_bank` where `organisation_id` = %s""")
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)
		finance_data = cursor.fetchall()

		for key,data in enumerate(finance_data):
			get_plan_query = ("""SELECT * FROM `plan` where `emi_bank_id` = %s""")
			get_plan_data = (data['emi_bank_id'])
			plan_count = cursor.execute(get_plan_query,get_plan_data)

			if plan_count > 0:
				finance_data[key]['having_plan'] = 1
			else:
				finance_data[key]['having_plan'] = 0
			finance_data[key]['last_update_ts'] = str(data['last_update_ts'])			

		return ({"attributes": {
					    "status_desc": "finance_details",
					    "status": "success"
				},
				"responseList":finance_data}), status.HTTP_200_OK
#-----------------------Finance-List-------------------------------#

#----------------------Update-Finance---------------------#

@name_space.route("/updateFinance/<int:emi_bank_id>")
class updateFinance(Resource):
	@api.expect(finance_putmodel)
	def put(self, emi_bank_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "status" in details:
			update_status = details['status']
			update_query = ("""UPDATE `emi_bank` SET `status` = %s
				WHERE `emi_bank_id` = %s """)
			update_data = (update_status,emi_bank_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Finance",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Finance---------------------#


#-----------------------Plan-List-------------------------------#

@name_space.route("/planListByEmiBankSpecific/<int:emi_bank_id>/<int:organisation_id>/<int:retailer_store_id>")	
class planListByEmiBankSpecific(Resource):
	def get(self,emi_bank_id,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT * FROM `plan` where `retailer_store_id` = %s and `organisation_id` = %s and `emi_bank_id` = %s""")
		get_data = (retailer_store_id,organisation_id,emi_bank_id)
		cursor.execute(get_query,get_data)
		plan_data = cursor.fetchall()

		for key,data in enumerate(plan_data):
			get_product_query = ("""SELECT p.`product_id`,p.`product_name`,pm.`meta_key_text`,pm.`product_meta_id`,pm.`product_meta_code`
									FROM `product_plan_mapping` ppm
									INNER JOIN `product` p ON p.`product_id` = ppm.`product_id`
									INNER JOIN `product_meta` pm ON pm.`product_meta_id` = ppm.`product_meta_id`
									where ppm.`plan_id` = %s""")
			get_product_data = (data['plan_id'])
			product_data_count = cursor.execute(get_product_query,get_product_data)			

			plan_data[key]['validity_date_from'] = str(data['validity_date_from'])
			plan_data[key]['validity_date_to'] = str(data['validity_date_to'])
			plan_data[key]['last_update_ts'] = str(data['last_update_ts'])

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

				plan_data[key]['products'] = product_data
			else:
				plan_data[key]['products']  = []

		return ({"attributes": {
					    "status_desc": "finance_details",
					    "status": "success"
				},
				"responseList":plan_data}), status.HTTP_200_OK

#-----------------------Plan-List-------------------------------#

#-----------------------Product-List-By-Plan-Id-------------------------------#

@name_space.route("/productListByPlanId/<int:plan_id>")	
class productListByPlanId(Resource):
	def get(self,plan_id):
		connection = mysql_connection()
		cursor = connection.cursor()


		get_product_query = ("""SELECT p.`product_id`,p.`product_name`,pm.`meta_key_text`,pm.`product_meta_id`,pm.`product_meta_code`
									FROM `product_plan_mapping` ppm
									INNER JOIN `product` p ON p.`product_id` = ppm.`product_id`
									INNER JOIN `product_meta` pm ON pm.`product_meta_id` = ppm.`product_meta_id`
									where ppm.`plan_id` = %s""")
		get_product_data = (plan_id)
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

#-----------------------Global-Finance-List-------------------------------#

@name_space.route("/globalfinanceList")	
class globalfinanceList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT * FROM `emi_bank` where `organisation_id` = 1""")		
		cursor.execute(get_query)
		finance_data = cursor.fetchall()

		for key,data in enumerate(finance_data):
			finance_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
					    "status_desc": "finance_details",
					    "status": "success"
				},
				"responseList":finance_data}), status.HTTP_200_OK

#-----------------------Global-Finance-List-------------------------------#

#----------------------Add-Finance---------------------#

@name_space.route("/AddFinance")	
class AddFinance(Resource):
	@api.expect(copy_finance_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		organisation_id = details['organisation_id']
		emi_bank_ids = details.get('emi_bank_id',[])
		

		for key,emi_bank_id in enumerate(emi_bank_ids):
			print(emi_bank_id)
			get_emi_bank_query = ("""SELECT * FROM `emi_bank` where `organisation_id` = 1 and `emi_bank_id` = %s""")
			get_emi_bank_data = (emi_bank_id)		
			cursor.execute(get_emi_bank_query,get_emi_bank_data)
			emi_bank_data = cursor.fetchone()

			get_finance_query = ("""SELECT * FROM `emi_bank` where `organisation_id` = %s and `emi_bank_name` = %s""")
			get_finance_data = (organisation_id,emi_bank_data['emi_bank_name'])
			finance_count = cursor.execute(get_finance_query,get_finance_data)

			if finance_count < 1:				
				insert_query = ("""INSERT INTO `emi_bank`(`emi_bank_name`,`emi_bank_image`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")
				insert_data = (emi_bank_data['emi_bank_name'],emi_bank_data['emi_bank_image'],organisation_id,organisation_id)
				cursor.execute(insert_query,insert_data)

				finance_id = cursor.lastrowid

				get_plan_query = ("""SELECT * FROM `plan` where `organisation_id` = 1 and `emi_bank_id` = %s""")
				get_plan_data = (emi_bank_id)
				plan_count = cursor.execute(get_plan_query,get_plan_data)
				print(cursor._last_executed)
				plan_data = cursor.fetchall()

				print(plan_data)

				delete_query = ("""DELETE FROM `plan` WHERE `organisation_id` = %s and `emi_bank_id` = %s """)
				delData = (organisation_id,finance_id)						
				cursor.execute(delete_query,delData)

				for key,data in enumerate(plan_data):
					
					plan_insert_query = ("""INSERT INTO `plan`(`emi_bank_id`,`validity_date_from`,`validity_date_to`,`plan_short_description`,`plan_description`,`installment_count`,`down_payment_installment_count`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
					plan_insert_data = (finance_id,data['validity_date_from'],data['validity_date_to'],data['plan_short_description'],data['plan_description'],data['installment_count'],data['down_payment_installment_count'],organisation_id,organisation_id)
					cursor.execute(plan_insert_query,plan_insert_data)					
			else:
				finance_data = cursor.fetchone()	
				delete_plan_query = ("""DELETE FROM `plan` WHERE `organisation_id` = %s and `emi_bank_id` = %s """)	
				delPlanData = (organisation_id,finance_data['emi_bank_id'])						
				cursor.execute(delete_plan_query,delPlanData)		

				delete_finance_query = ("""DELETE FROM `emi_bank` WHERE `organisation_id` = %s and `emi_bank_name` = %s """)
				delFinanceData = (organisation_id,emi_bank_data['emi_bank_name'])						
				cursor.execute(delete_finance_query,delFinanceData)

				insert_query = ("""INSERT INTO `emi_bank`(`emi_bank_name`,`emi_bank_image`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")
				insert_data = (emi_bank_data['emi_bank_name'],emi_bank_data['emi_bank_image'],organisation_id,organisation_id)
				cursor.execute(insert_query,insert_data)

				finance_id = cursor.lastrowid

				get_plan_query = ("""SELECT * FROM `plan` where `organisation_id` = 1 and `emi_bank_id` = %s""")
				get_plan_data = (emi_bank_id)
				plan_count = cursor.execute(get_plan_query,get_plan_data)
				print(cursor._last_executed)
				plan_data = cursor.fetchall()

				print(plan_data)


				delete_query = ("""DELETE FROM `plan` WHERE `organisation_id` = %s and `emi_bank_id` = %s """)
				delData = (organisation_id,finance_id)						
				cursor.execute(delete_query,delData)

				for key,data in enumerate(plan_data):		

					plan_insert_query = ("""INSERT INTO `plan`(`emi_bank_id`,`validity_date_from`,`validity_date_to`,`plan_short_description`,`plan_description`,`installment_count`,`down_payment_installment_count`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
					plan_insert_data = (finance_id,data['validity_date_from'],data['validity_date_to'],data['plan_short_description'],data['plan_description'],data['installment_count'],data['down_payment_installment_count'],organisation_id,organisation_id)
					cursor.execute(plan_insert_query,plan_insert_data)

						

		return ({"attributes": {
			    	"status_desc": "add_finance",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK			



#----------------------Add-Finance---------------------#

#----------------------Add-Plan---------------------#

@name_space.route("/AddPlan")	
class AddPlan(Resource):
	@api.expect(plan_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		emi_bank_name = details['emi_bank_name']		
		organisation_id = details['organisation_id']

		

		get_emi_bank_query = ("""SELECT * FROM `emi_bank` where `organisation_id` = 1 and `emi_bank_name` = %s""")
		get_emi_bank_data = (emi_bank_name)		
		cursor.execute(get_emi_bank_query,get_emi_bank_data)
		emi_bank_data = cursor.fetchone()

		get_finance_query = ("""SELECT * FROM `emi_bank` where `organisation_id` = %s and `emi_bank_name` = %s""")
		get_finance_data = (organisation_id,emi_bank_data['emi_bank_name'])
		finance_count = cursor.execute(get_finance_query,get_finance_data)
		finance_data = cursor.fetchone()

		#delete_query = ("""DELETE FROM `plan` WHERE `organisation_id` = %s and `emi_bank_id` = %s """)
		#delData = (organisation_id,finance_data['emi_bank_id'])						
		#cursor.execute(delete_query,delData)

		'''get_organised_plan_query = ("""SELECT * FROM `plan` where `organisation_id` = %s and `emi_bank_id` = %s""")
		get_organised_plan_data = (organisation_id,finance_data['emi_bank_id'])
		count_organised_plan_count = cursor.execute(get_organised_plan_query,get_organised_plan_data)

		if count_organised_plan_count > 0:
			organised_plan_data = cursor.fetchall()

			for okey,odata in enumerate(organised_plan_data):
				update_query = ("""UPDATE `plan` SET `plan_status` = %s
					WHERE `organisation_id` = %s and `emi_bank_id` = %s """)
				plan_status = 1
				update_data = (plan_status,organisation_id,finance_data['emi_bank_id'])
				cursor.execute(update_query,update_data)'''


		get_plan_query = ("""SELECT * FROM `plan` where `organisation_id` = 1 and `emi_bank_id` = %s""")
		get_plan_data = (emi_bank_data['emi_bank_id'])
		plan_count = cursor.execute(get_plan_query,get_plan_data)
		print(cursor._last_executed)
		plan_data = cursor.fetchall()

		for key,data in enumerate(plan_data):
					
			plan_insert_query = ("""INSERT INTO `plan`(`emi_bank_id`,`validity_date_from`,`validity_date_to`,`plan_short_description`,`plan_description`,`installment_count`,`down_payment_installment_count`,`organisation_id`,`plan_status`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			plan_insert_data = (finance_data['emi_bank_id'],data['validity_date_from'],data['validity_date_to'],data['plan_short_description'],data['plan_description'],data['installment_count'],data['down_payment_installment_count'],organisation_id,1,organisation_id)
			cursor.execute(plan_insert_query,plan_insert_data)

			new_plan_id = cursor.lastrowid

			get_previous_organised_plan_query = ("""SELECT * FROM `plan` where `organisation_id` = %s and `emi_bank_id` = %s and `plan_status` = 0""")
			get_previous_organised_plan_data = (organisation_id,finance_data['emi_bank_id'])
			previous_organised_plan_count = cursor.execute(get_previous_organised_plan_query,get_previous_organised_plan_data)
			previous_organised_plan_data = cursor.fetchall()

			for pkey,pdata in enumerate(previous_organised_plan_data):
				print(pdata['plan_id'])
				plan_product_query = ("""SELECT * FROM `product_plan_mapping` where `plan_id` = %s """)
				plan_product_data = (pdata['plan_id'])
				plan_product_count = cursor.execute(plan_product_query,plan_product_data)

				plan_product_data = cursor.fetchall()

				for ppkey,ppdata in enumerate(plan_product_data):
					plan_product_insert_query = ("""INSERT INTO `product_plan_mapping`(`plan_id`,`product_meta_id`,`product_id`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s)""")
					plan_product_insert_data = (new_plan_id,ppdata['product_meta_id'],ppdata['product_id'],ppdata['organisation_id'],ppdata['last_update_id'])
					cursor.execute(plan_product_insert_query,plan_product_insert_data)

		return ({"attributes": {
			    	"status_desc": "plan",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Add-Plan---------------------#	

#----------------------Add-Product-Plan---------------------#

@name_space.route("/ProductPlan")	
class ProductPlan(Resource):
	@api.expect(product_plan_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		plan_id = details['plan_id']
		product_meta_id = details['product_meta_id']
		product_id = details['product_id']
		organisation_id = details['organisation_id']

		insert_query = ("""INSERT INTO `product_plan_mapping`(`plan_id`,`product_meta_id`,`product_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
		insert_data = (plan_id,product_meta_id,product_id,organisation_id,organisation_id)
		cursor.execute(insert_query,insert_data)

		return ({"attributes": {
			    	"status_desc": "plan",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Add-Product-Plan---------------------#

#-----------------------Plan-List-------------------------------#

@name_space.route("/planListByEmiBankSpecificWithOutRetailerStore/<int:emi_bank_id>/<int:organisation_id>")	
class planListByEmiBankSpecificWithOutRetailerStore(Resource):
	def get(self,emi_bank_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT * FROM `plan` where `organisation_id` = %s and `emi_bank_id` = %s""")
		get_data = (organisation_id,emi_bank_id)
		cursor.execute(get_query,get_data)
		plan_data = cursor.fetchall()

		for key,data in enumerate(plan_data):
			get_product_query = ("""SELECT p.`product_id`,p.`product_name`,pm.`meta_key_text`,pm.`product_meta_id`,pm.`product_meta_code`
									FROM `product_plan_mapping` ppm
									INNER JOIN `product` p ON p.`product_id` = ppm.`product_id`
									INNER JOIN `product_meta` pm ON pm.`product_meta_id` = ppm.`product_meta_id`
									where ppm.`plan_id` = %s""")
			get_product_data = (data['plan_id'])
			product_data_count = cursor.execute(get_product_query,get_product_data)			

			plan_data[key]['validity_date_from'] = str(data['validity_date_from'])
			plan_data[key]['validity_date_to'] = str(data['validity_date_to'])
			plan_data[key]['last_update_ts'] = str(data['last_update_ts'])

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

				plan_data[key]['products'] = product_data
			else:
				plan_data[key]['products']  = []

		return ({"attributes": {
					    "status_desc": "finance_details",
					    "status": "success"
				},
				"responseList":plan_data}), status.HTTP_200_OK

#-----------------------Plan-List-------------------------------#

#----------------------Delete-Product-From-Plan---------------------#

@name_space.route("/deleteproductFromPlan/<int:plan_id>/<int:product_meta_id>/<int:product_id>")
class deleteproductFromPlan(Resource):
	def delete(self, plan_id,product_meta_id,product_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		delete_query = ("""DELETE FROM `product_plan_mapping` WHERE `plan_id` = %s and `product_meta_id` = %s and `product_id` = %s""")
		delData = (plan_id,product_meta_id,product_id)
		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Product From Plan",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Product-From-Plan---------------------#

#----------------------Banner-Image---------------------#

@name_space.route("/getBannerImage/<int:organisation_id>/<int:retailer_store_store_id>")	
class getEmiList(Resource):
	def get(self,organisation_id,retailer_store_store_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT * FROM `retail_store_banner_image` where `organisation_id` = %s and `status` = 1 and `retailer_store_store_id` = %s""")	
		get_data = (organisation_id,retailer_store_store_id)
		cursor.execute(get_query,get_data)
		banner_data = cursor.fetchone()
		banner_data['last_update_ts'] = str(banner_data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "Banner Data",
		    		"status": "success"
		    	},
		    	"responseList":banner_data}), status.HTTP_200_OK

#----------------------Banner-Image---------------------#

#----------------------Add-Finance-Brand--------------------#

@name_space.route("/AddFinanceBrand")	
class AddFinanceBrand(Resource):
	@api.expect(finance_brand_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		brand_ids = details.get('brand_id',[])
		organisation_id = details['organisation_id']
		emi_bank_id = details['emi_bank_id']

		for key,brand_id in enumerate(brand_ids):
			get_query =  ("""SELECT * FROM `finance_brand_mapping` where `organisation_id` = %s and `brand_id` = %s and `emi_bank_id` = %s""")	
			get_data = (organisation_id,brand_id,emi_bank_id)
			finance_brand_count = cursor.execute(get_query,get_data)
			print(finance_brand_count)

			if finance_brand_count < 1:
				insert_query = ("""INSERT INTO `finance_brand_mapping`(`emi_bank_id`,`brand_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")
				insert_data = (emi_bank_id,brand_id,organisation_id,organisation_id)
				cursor.execute(insert_query,insert_data)

				print(cursor._last_executed)

		connection.commit()
		cursor.close()

		return ({"attributes": {
					    "status_desc": "finance_brand",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Add-Finance-Brand--------------------#

#-----------------------Finance-Brand-List-------------------------------#

@name_space.route("/financeBranList/<int:organisation_id>/<int:emi_bank_id>")	
class financeBranList(Resource):
	def get(self,organisation_id,emi_bank_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT fbm.*,m.`meta_key_value` as `brand_name`,m.`image` FROM `finance_brand_mapping` fbm
						INNER JOIN `meta_key_value_master` m ON m.`meta_key_value_id` = fbm.`brand_id`
		 where fbm.`organisation_id` = %s and fbm.`emi_bank_id` = %s""")	
		get_data = (organisation_id,emi_bank_id)
		finance_brand_mapping_count = cursor.execute(get_query,get_data)

		if finance_brand_mapping_count > 0:
			finance_brand = cursor.fetchall()
			for key,data in enumerate(finance_brand):
				finance_brand[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			finance_brand = []

		return ({"attributes": {
					    "status_desc": "finance_brand",
					    "status": "success"
				},
				"responseList":finance_brand}), status.HTTP_200_OK

#-----------------------Finance-Brand-List-------------------------------#


#----------------------Delete-Brand-From-Finance-Brand-List---------------------#

@name_space.route("/deleteBrandFromFinanceBrandList/<int:brand_id>/<int:emi_bank_id>/<int:organisation_id>")
class deleteBrandFromFinanceBrandList(Resource):
	def delete(self, brand_id,emi_bank_id,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		delete_query = ("""DELETE FROM `finance_brand_mapping` WHERE `emi_bank_id` = %s and `organisation_id` = %s and `brand_id` = %s""")
		delData = (emi_bank_id,organisation_id,brand_id)
		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete brand From Finance Brand List",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Brand-From-Finance-Brand-List---------------------#

@name_space.route("/sendPushAfterChoosingBrand")	
class sendPushAfterChoosingBrand(Resource):
	@api.expect(push_notification_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		organisation_id = details['organisation_id']
		user_id = details['user_id']
		brand_id = details['brand_id']
		emi_bank_id = details['emi_bank_id']

		get_user_retailer_query = (""" SELECT *
			FROM `user_retailer_mapping` WHERE user_id = %s and `organisation_id` = %s""")
		get_user_retailer_data = (user_id,organisation_id)
		cursor.execute(get_user_retailer_query,get_user_retailer_data)

		user_retailer_data = cursor.fetchone()

		cursor.execute("""SELECT * FROM `organisation_firebase_details` 
				where `organisation_id`=%s""",(organisation_id))
		firebaseDtls = cursor.fetchone()

		get_user_device_query = ("""SELECT `device_token`
						FROM `devices` WHERE  `user_id` = %s and `organisation_id` = %s""")

		get_user_device_data = (user_id,organisation_id)
		device_token_count = cursor.execute(get_user_device_query,get_user_device_data)

		if device_token_count > 0:
			
			device_token_data = cursor.fetchone()

			device_id = device_token_data['device_token']
		else:
			device_id = ''

		get_customer_data_query = ("""SELECT `first_name`,`last_name`,`email`,`phoneno`
				FROM `admins` WHERE  `admin_id` = %s""")

		getCustomerData = (user_id)
					
		countCustomerData = cursor.execute(get_customer_data_query,getCustomerData)

		if countCustomerData > 0 :
			customer_data = cursor.fetchone()
			customer_name = customer_data['phoneno']
		else:
			customer_name = ""

		get_brand_query = ("""SELECT * FROM  `meta_key_value_master` where `meta_key_value_id` = %s""")
		get_brand_data = (brand_id)
		brand_count = cursor.execute(get_brand_query,get_brand_data)

		if brand_count > 0:
			brand_data = cursor.fetchone()
			brand_name = brand_data['meta_key_value']
		else:
			brand_name = ''

		now = datetime.now()
		request_date = now.strftime("%Y-%m-%d")

		get_query = ("""SELECT * FROM `user_finance_band_mapping` where `emi_bank_id` = %s and `brand_id` = %s and `user_id` = %s""")
		get_data = (emi_bank_id,brand_id,user_id)
		user_finance_brand_count = cursor.execute(get_query,get_data)

		if user_finance_brand_count < 1:

			insert_query = ("""INSERT INTO `user_finance_band_mapping`(`emi_bank_id`,`brand_id`,`user_id`,`organisation_id`,`request_date`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s)""")
			insert_data = (emi_bank_id,brand_id,user_id,organisation_id,request_date,organisation_id)
			cursor.execute(insert_query,insert_data)

		else:
			update_query = ("""UPDATE `user_finance_band_mapping` SET `request_date` = %s
				where `emi_bank_id` = %s and `brand_id` = %s and `user_id` = %s """)
			update_data = (request_date,emi_bank_id,brand_id,user_id)
			cursor.execute(update_query,update_data)


		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		sndNotificationUrl = BASE_URL + "ret_notification/RetailerNotification/SendPushNotificationsToOrganisation"
		payloadpushData = {
				"title":"EMI Request",
				"msg":customer_name+" has requested for EMI of "+brand_name,
				"img": "",
				"organisation_id": organisation_id
		}

		sndNotificationResponse = requests.post(sndNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		print(sndNotificationResponse)

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		sndNotificationRetailerUrl = BASE_URL + "ret_notification/RetailerNotification/SendPushNotificationsToRetailer"
		payloadpushRetailerData = {
				"title":"EMI Request",
				"msg":customer_name+" has requested for EMI of "+brand_name,
				"img": "",
				"organisation_id": organisation_id,
				"retail_store_id": user_retailer_data['retailer_store_id']
		}

		sndNotificationRetailerResponse = requests.post(sndNotificationRetailerUrl,data=json.dumps(payloadpushRetailerData), headers=headers).json()

		print(sndNotificationRetailerResponse)

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		sndNotificationCustomerUrl = BASE_URL + "ecommerce_emi/EcommerceEmi/sendAppPushNotificationforCustomer"
		payloadpushCustomerData = {
				"firebase_key":firebaseDtls['firebase_key'],
				"device_id":device_id,
				"organisation_id":organisation_id
		}

		print(payloadpushCustomerData)

		sndNotificationRetailerResponse = requests.post(sndNotificationCustomerUrl,data=json.dumps(payloadpushCustomerData), headers=headers).json()

		print(sndNotificationRetailerResponse)

		connection.commit()
		cursor.close()

		return ({"attributes": {
					    "status_desc": "Push Notification",
					    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK



#----------------------Send-Push-Notification---------------------#

@name_space.route("/sendAppPushNotificationforCustomer")
class sendAppPushNotificationforCustomer(Resource):
	@api.expect(appmsg_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		data_message = {
							"title" : "EMI Request",
							"message": "Thank you. Store will contact you shortly",
							"image-url":""
						}
		api_key = details.get('firebase_key')
		device_id = details.get('device_id')
		organisation_id = details.get('organisation_id')
		push_service = FCMNotification(api_key=api_key)
		msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = data_message)
		sent = 'N'
		if msgResponse.get('success') == 1:
			sent = 'Y'
			msg = 'Store will  contact you shortly'
			destination_type = 2
			source_type = 3
			title = 'EMI Request'
			app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
					`U_id`,`Device_ID`,`Sent`,`source_type`,`destination_type`,`organisation_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
			insert_data = (title,msg,'',device_id,sent,source_type,destination_type,organisation_id)
			appdata = cursor.execute(app_query,insert_data)
		
		
		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				    	"responseList":msgResponse}), status.HTTP_200_OK
#----------------------Send-Push-Notification---------------------#

#-----------------------Customer-List-By-brand------------------------------#

@name_space.route("/CustomerListByFinanceBrand/<int:organisation_id>/<int:emi_bank_id>/<int:brand_id>")	
class CustomerListByFinanceBrand(Resource):
	def get(self,organisation_id,emi_bank_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT a.`first_name`,a.`phoneno`,ufbm.`request_date` FROM `user_finance_band_mapping` ufbm
						INNER JOIN `admins` a ON a.`admin_id` = ufbm.`user_id`
		 where ufbm.`organisation_id` = %s and ufbm.`emi_bank_id` = %s and ufbm.`brand_id` = %s order by ufbm.`request_date` desc""")	
		get_data = (organisation_id,emi_bank_id,brand_id)
		finance_brand_mapping_count = cursor.execute(get_query,get_data)

		if finance_brand_mapping_count > 0:
			customer_finanace_brand = cursor.fetchall()
			for key,data in enumerate(customer_finanace_brand):
				customer_finanace_brand[key]['request_date'] = str(data['request_date'])
		else:
			customer_finanace_brand = []

		return ({"attributes": {
					    "status_desc": "customer_finanace_brand",
					    "status": "success"
				},
				"responseList":customer_finanace_brand}), status.HTTP_200_OK

#-----------------------Customer-List-By-brand------------------------------#
				



