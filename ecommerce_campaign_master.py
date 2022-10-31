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
def mysql_connection():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def mysql_connection_analytics():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce_analytics',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

ecommerce_campaign_master = Blueprint('ecommerce_campaign_master_api', __name__)
api = Api(ecommerce_campaign_master,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceCampaignMaster',description='Ecommerce Campaign Master')

campaign_postmodel = api.model('campaign_postmodel', {
	"campaign_name":fields.String(required=True),
	"content_type":fields.Integer(required=True),
	"content_text":fields.String(required=True),
	"whatsapp":fields.Integer(required=True),
	"email":fields.Integer(required=True),
	"notification":fields.Integer(required=True),
	"sms":fields.Integer(required=True),
	"state":fields.Integer(required=True),
	"shedule_date":fields.String,
	"shedule_time":fields.String,
	"retailer_store_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

campaign_putmodel = api.model('campaign_putmodel', {
	"campaign_name":fields.String,
	"content_type":fields.Integer,
	"content_text":fields.String,
	"whatsapp":fields.Integer,
	"email":fields.Integer,
	"notification":fields.Integer,
	"sms":fields.Integer,
	"state":fields.Integer,
	"shedule_date":fields.String,
	"shedule_time":fields.String,
})

audience_postmodel = api.model('audience_postmodel', {
	"audience_name":fields.String(required=True),
	"customer_creation_date":fields.String(required=True),
	"pincode":fields.String(required=True),
	"model":fields.String(required=True),
	"brand":fields.String(required=True),
	"purchase_cost":fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"retailer_store_id":fields.Integer(required=True),
	"purchase_date_range":fields.String(required=True),
	"category_id":fields.Integer,
	"product_type":fields.String
})

audience_putmodel = api.model('audience_putmodel', {
	"audience_name":fields.String(required=True),
	"customer_creation_date":fields.String(required=True),
	"pincode":fields.String(required=True),
	"model":fields.String(required=True),
	"brand":fields.String(required=True),
	"purchase_cost":fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"retailer_store_id":fields.Integer(required=True),
	"purchase_date_range":fields.String(required=True),
	"category_id":fields.Integer,
	"product_type":fields.String
})

campaign_audience_mapping_postmodel = api.model('campaign_audience_mapping_postmodel', {
	"campaign_id":fields.Integer(required=True),
	"audience_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"retailer_store_id":fields.Integer(required=True)
})

notification_model = api.model('notification_model', {	
	"text":fields.String(),
	"image":fields.String(),
	"title": fields.String(required=True),
	"customer_id": fields.Integer(required=True),
	"organisation_id": fields.Integer(required=True)
})

copy_campaign_postmodel = api.model('copy_campaign_model', {	
	"campaign_id":fields.Integer(required=True)
})

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#----------------------Add-Campaign---------------------#

@name_space.route("/AddCampaign")
class AddCampaign(Resource):
	@api.expect(campaign_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		campaign_name = details['campaign_name']		
		content_type = details['content_type']
		content_text = details['content_text']
		whatsapp = details['whatsapp']
		email = details['email']
		notification = details['notification']
		sms = details['sms']
		state = details['state']

		if details and "shedule_date" in details:
			shedule_date = details['shedule_date']
		else:
			shedule_date = ''

		if details and "shedule_time" in details:
			shedule_time = details['shedule_time']
		else:
			shedule_time = ''

		retailer_store_id = details['retailer_store_id']
		organisation_id = details['organisation_id']
		last_update_id = retailer_store_id

		insert_query = ("""INSERT INTO `campaign_master`(`campaign_name`,`content_type`,`content_text`,`whatsapp`,`email`,`notification`,`sms`,`state`,`shedule_date`,`shedule_time`,`retailer_store_id`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (campaign_name,content_type,content_text,whatsapp,email,notification,sms,state,shedule_date,shedule_time,retailer_store_id,organisation_id,last_update_id)
		cursor.execute(insert_query,data)

		campaign_id = cursor.lastrowid
		details['campaign_id'] = campaign_id

		return ({"attributes": {
			    		"status_desc": "campaign_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Campaign---------------------#

#----------------------Add-Campaign---------------------#

@name_space.route("/CopyCampaign")
class CopyCampaign(Resource):
	@api.expect(copy_campaign_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		campaign_id = details['campaign_id']

		get_query = ("""SELECT *
			FROM `campaign_master`
			WHERE  `campaing_id` = %s""")
		get_data = (campaign_id)
		cursor.execute(get_query,get_data)

		get_campaign_data = cursor.fetchone()

		campaign_insert_query = ("""INSERT INTO `campaign_master`(`campaign_name`,`content_type`,`content_text`,`whatsapp`,`email`,`notification`,`sms`,`state`,`shedule_date`,`shedule_time`,`retailer_store_id`,`organisation_id`,`last_update_id`)
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		campaign_insert_data = (get_campaign_data['campaign_name'],get_campaign_data['content_type'],get_campaign_data['content_text'],get_campaign_data['whatsapp'],get_campaign_data['email'],get_campaign_data['notification'],get_campaign_data['sms'],get_campaign_data['state'],get_campaign_data['shedule_date'],get_campaign_data['shedule_time'],get_campaign_data['retailer_store_id'],get_campaign_data['organisation_id'],get_campaign_data['last_update_id'])
		cursor.execute(campaign_insert_query,campaign_insert_data)
		campaign_id = cursor.lastrowid

		'''get_campaign_audience_query = ("""SELECT *
			FROM `campaing_audience_mapping`
			WHERE  `campaign_id` = %s""")
		get_campaign_audience_data = (campaign_id)
		campaing_audience_count = cursor.execute(get_campaign_audience_query,get_campaign_audience_data)

		if campaing_audience_count > 0:
			get_campaign_audience_data = cursor.fetchone()
			get_audience_query = ("""SELECT * FROM `audience_master`  where `audience_id` = %s""")
			get_audience_data = (get_campaign_audience_data['audience_id'])
			audience_count = cursor.execute(get_audience_query,get_audience_data)
			if audience_count > 0:
				audience_data = cursor.fetchone()
				audience_insert_query = ("""INSERT INTO `audience_master`(`audience_name`,`customer_creation_date`,`pincode`,`model`,`brand`,`purchase_cost`,`retailer_store_id`,`purchase_date_range`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				audience_insert_data = (audience_data['audience_name'],audience_data['customer_creation_date'],audience_data['pincode'],audience_data['model'],audience_data['brand'],audience_data['purchase_cost'],audience_data['retailer_store_id'],audience_data['purchase_date_range'],audience_data['organisation_id'],audience_data['last_update_id'])
				cursor.execute(audience_insert_query,audience_insert_data)
				audience_id = cursor.lastrowid
				print(audience_id)

				campaign_insert_query = ("""INSERT INTO `campaign_master`(`campaign_name`,`content_type`,`content_text`,`whatsapp`,`email`,`notification`,`sms`,`state`,`shedule_date`,`shedule_time`,`retailer_store_id`,`organisation_id`,`last_update_id`)
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				campaign_insert_data = (get_campaign_data['campaign_name'],get_campaign_data['content_type'],get_campaign_data['content_text'],get_campaign_data['whatsapp'],get_campaign_data['email'],get_campaign_data['notification'],get_campaign_data['sms'],get_campaign_data['state'],get_campaign_data['shedule_date'],get_campaign_data['shedule_time'],get_campaign_data['retailer_store_id'],get_campaign_data['organisation_id'],get_campaign_data['last_update_id'])
				cursor.execute(campaign_insert_query,campaign_insert_data)
				campaign_id = cursor.lastrowid

				campaign_audience_mapping_insert_query = ("""INSERT INTO `campaing_audience_mapping`(`campaign_id`,`audience_id`,`retailer_store_id`,`organisation_id`,`last_update_id`)
					VALUES(%s,%s,%s,%s,%s)""")
				campaign_audience_mapping_insert_data = (campaign_id,audience_id,get_campaign_data['retailer_store_id'],get_campaign_data['organisation_id'],get_campaign_data['last_update_id'])
				cursor.execute(campaign_audience_mapping_insert_query,campaign_audience_mapping_insert_data)
			else:
				print('No Record Found')
		else:
			print('No Record Found')'''

		return ({"attributes": {
			    		"status_desc": "copy_campaign_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK



#----------------------Campaign-List---------------------#
@name_space.route("/getCampaignListByOrganisationId/<int:organisation_id>")	
class getCampaignListByOrganisationId(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `campaign_master` c 
			WHERE  c.`organisation_id` = %s order by `campaing_id` desc""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		campaign_data = cursor.fetchall()

		for key,data in enumerate(campaign_data):			
			campaign_data[key]['last_update_ts'] = str(data['last_update_ts'])
			get_audience_query = ("""SELECT a.*
				FROM `campaing_audience_mapping` cam 
				INNER JOIN `audience_master` a ON a.`audience_id` = cam.`audience_id`
				WHERE  cam.`organisation_id` = %s and cam.`campaign_id` = %s""")
			get_audience_data = (organisation_id,data['campaing_id'])
			audience_count = cursor.execute(get_audience_query,get_audience_data)

			if audience_count > 0:
				audience_data = cursor.fetchone()				
				'''filterURL = BASE_URL + "ecommerce_campaign_master/EcommerceCampaignMaster/getCustomerCount/{}/{}/{}/{}/{}/{}/{}/{}/{}".format(audience_data['customer_creation_date'],audience_data['pincode'],audience_data['model'],audience_data['brand'],audience_data['purchase_cost'],audience_data['organisation_id'],audience_data['retailer_store_id'],audience_data['purchase_date_range'],audience_data['category_id'])
				
				print(filterURL)
				filterRes = requests.get(filterURL).json()
				total = filterRes['responseList']['customer_count']

				campaign_data[key]['customer_count'] = total'''
				campaign_data[key]['customer_count'] = 0

			else:
				campaign_data[key]['customer_count'] = 0
		
				
		return ({"attributes": {
		    		"status_desc": "campaign_details",
		    		"status": "success"
		    	},
		    	"responseList":campaign_data}), status.HTTP_200_OK

#----------------------Campaign-List---------------------#

#----------------------Campaign-List---------------------#
@name_space.route("/getCampaignListByOrganisationIdWithLimit/<int:organisation_id>/<int:limit>")	
class getCampaignListByOrganisationIdWithLimit(Resource):
	def get(self,organisation_id,limit):
		connection = mysql_connection()
		cursor = connection.cursor()

		if limit == 0:

			get_query = ("""SELECT *
				FROM `campaign_master` c 
				WHERE  c.`organisation_id` = %s order by `campaing_id` desc""")
			get_data = (organisation_id)
		else:
			get_query = ("""SELECT *
				FROM `campaign_master` c 
				WHERE  c.`organisation_id` = %s order by `campaing_id` desc limit %s""")

			get_data = (organisation_id,limit)
		cursor.execute(get_query,get_data)

		campaign_data = cursor.fetchall()

		for key,data in enumerate(campaign_data):			
			campaign_data[key]['last_update_ts'] = str(data['last_update_ts'])
			get_audience_query = ("""SELECT a.*
				FROM `campaing_audience_mapping` cam 
				INNER JOIN `audience_master` a ON a.`audience_id` = cam.`audience_id`
				WHERE  cam.`organisation_id` = %s and cam.`campaign_id` = %s""")
			get_audience_data = (organisation_id,data['campaing_id'])
			audience_count = cursor.execute(get_audience_query,get_audience_data)

			if audience_count > 0:
				audience_data = cursor.fetchone()				
				'''filterURL = BASE_URL + "ecommerce_campaign_master/EcommerceCampaignMaster/getCustomerCount/{}/{}/{}/{}/{}/{}/{}/{}/{}".format(audience_data['customer_creation_date'],audience_data['pincode'],audience_data['model'],audience_data['brand'],audience_data['purchase_cost'],audience_data['organisation_id'],audience_data['retailer_store_id'],audience_data['purchase_date_range'],audience_data['category_id'])
				
				print(filterURL)
				filterRes = requests.get(filterURL).json()
				total = filterRes['responseList']['customer_count']

				campaign_data[key]['customer_count'] = total'''
				campaign_data[key]['customer_count'] = 0

			else:
				campaign_data[key]['customer_count'] = 0
		
				
		return ({"attributes": {
		    		"status_desc": "campaign_details",
		    		"status": "success"
		    	},
		    	"responseList":campaign_data}), status.HTTP_200_OK

#----------------------Campaign-List---------------------#

#----------------------Campaign-List---------------------#
@name_space.route("/getCampaignListByOrganisationIdAndRetailStoreId/<int:organisation_id>/<int:retailer_store_id>")	
class getCampaignListByOrganisationIdAndRetailStoreId(Resource):
	def get(self,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `campaign_master` c 
			WHERE  c.`organisation_id` = %s and c.`retailer_store_id` = %s order by `campaing_id` desc""")

		get_data = (organisation_id,retailer_store_id)
		cursor.execute(get_query,get_data)

		campaign_data = cursor.fetchall()

		for key,data in enumerate(campaign_data):
			campaign_data[key]['last_update_ts'] = str(data['last_update_ts'])

			get_audience_query = ("""SELECT a.*
				FROM `campaing_audience_mapping` cam 
				INNER JOIN `audience_master` a ON a.`audience_id` = cam.`audience_id`
				WHERE cam.`campaign_id` = %s""")
			get_audience_data = (data['campaing_id'])
			audience_count = cursor.execute(get_audience_query,get_audience_data)

			if audience_count > 0:
				audience_data = cursor.fetchone()				
				'''filterURL = BASE_URL + "ecommerce_campaign_master/EcommerceCampaignMaster/getCustomerCount/{}/{}/{}/{}/{}/{}/{}/{}/{}".format(audience_data['customer_creation_date'],audience_data['pincode'],audience_data['model'],audience_data['brand'],audience_data['purchase_cost'],audience_data['organisation_id'],audience_data['retailer_store_id'],audience_data['purchase_date_range'],audience_data['category_id'])
				
				print(filterURL)
				filterRes = requests.get(filterURL).json()
				total = filterRes['responseList']['customer_count']

				campaign_data[key]['customer_count'] = total'''
				campaign_data[key]['customer_count'] = 0 
			else:
				campaign_data[key]['customer_count'] = 0
		
				
		return ({"attributes": {
		    		"status_desc": "campaign_details",
		    		"status": "success"
		    	},
		    	"responseList":campaign_data}), status.HTTP_200_OK

#----------------------Campaign-List---------------------#

#----------------------Campaign-List---------------------#
@name_space.route("/getCampaignListByOrganisationIdAndRetailStoreIdWithLimit/<int:organisation_id>/<int:retailer_store_id>/<int:limit>")	
class getCampaignListByOrganisationIdAndRetailStoreIdWithLimit(Resource):
	def get(self,organisation_id,retailer_store_id,limit):
		connection = mysql_connection()
		cursor = connection.cursor()

		if limit == 0:

			get_query = ("""SELECT *
				FROM `campaign_master` c 
				WHERE  c.`organisation_id` = %s and c.`retailer_store_id` = %s order by `campaing_id` desc""")

			get_data = (organisation_id,retailer_store_id)
		else:
			get_query = ("""SELECT *
				FROM `campaign_master` c 
				WHERE  c.`organisation_id` = %s and c.`retailer_store_id` = %s order by `campaing_id` desc limit %s""")

			get_data = (organisation_id,retailer_store_id,limit)
		cursor.execute(get_query,get_data)

		campaign_data = cursor.fetchall()

		for key,data in enumerate(campaign_data):
			campaign_data[key]['last_update_ts'] = str(data['last_update_ts'])

			get_audience_query = ("""SELECT a.*
				FROM `campaing_audience_mapping` cam 
				INNER JOIN `audience_master` a ON a.`audience_id` = cam.`audience_id`
				WHERE cam.`campaign_id` = %s""")
			get_audience_data = (data['campaing_id'])
			audience_count = cursor.execute(get_audience_query,get_audience_data)

			if audience_count > 0:
				audience_data = cursor.fetchone()				
				'''filterURL = BASE_URL + "ecommerce_campaign_master/EcommerceCampaignMaster/getCustomerCount/{}/{}/{}/{}/{}/{}/{}/{}/{}".format(audience_data['customer_creation_date'],audience_data['pincode'],audience_data['model'],audience_data['brand'],audience_data['purchase_cost'],audience_data['organisation_id'],audience_data['retailer_store_id'],audience_data['purchase_date_range'],audience_data['category_id'])
				
				print(filterURL)
				filterRes = requests.get(filterURL).json()
				total = filterRes['responseList']['customer_count']

				campaign_data[key]['customer_count'] = total'''
				campaign_data[key]['customer_count'] = 0 
			else:
				campaign_data[key]['customer_count'] = 0
		
				
		return ({"attributes": {
		    		"status_desc": "campaign_details",
		    		"status": "success"
		    	},
		    	"responseList":campaign_data}), status.HTTP_200_OK

#----------------------Campaign-List---------------------#

#----------------------Update-Campaign--------------------#

@name_space.route("/UpdateCampaign/<int:campaing_id>")
class UpdateCampaign(Resource):
	@api.expect(campaign_putmodel)
	def put(self,campaing_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		campaign_name = details['campaign_name']		
		content_type = details['content_type']
		content_text = details['content_text']
		whatsapp = details['whatsapp']
		email = details['email']
		notification = details['notification']
		sms = details['sms']
		state = details['state']

		if details and "campaign_name" in details:
			campaign_name = details['campaign_name']
			update_query = ("""UPDATE `campaign_master` SET `campaign_name` = %s
					WHERE `campaing_id` = %s """)
			update_data = (campaign_name,campaing_id)
			cursor.execute(update_query,update_data)

		if details and "content_type" in details:
			content_type = details['content_type']
			update_query = ("""UPDATE `campaign_master` SET `content_type` = %s
					WHERE `campaing_id` = %s """)
			update_data = (content_type,campaing_id)
			cursor.execute(update_query,update_data)

		if details and "content_text" in details:
			content_text = details['content_text']
			update_query = ("""UPDATE `campaign_master` SET `content_text` = %s
					WHERE `campaing_id` = %s """)
			update_data = (content_text,campaing_id)
			cursor.execute(update_query,update_data)

		if details and "whatsapp" in details:
			whatsapp = details['whatsapp']
			update_query = ("""UPDATE `campaign_master` SET `whatsapp` = %s
					WHERE `campaing_id` = %s """)
			update_data = (whatsapp,campaing_id)
			cursor.execute(update_query,update_data)

		if details and "email" in details:
			email = details['email']
			update_query = ("""UPDATE `campaign_master` SET `email` = %s
					WHERE `campaing_id` = %s """)
			update_data = (email,campaing_id)
			cursor.execute(update_query,update_data)

		if details and "notification" in details:
			notification = details['notification']
			update_query = ("""UPDATE `campaign_master` SET `notification` = %s
					WHERE `campaing_id` = %s """)
			update_data = (notification,campaing_id)
			cursor.execute(update_query,update_data)

		if details and "sms" in details:
			sms = details['sms']
			update_query = ("""UPDATE `campaign_master` SET `sms` = %s
					WHERE `campaing_id` = %s """)
			update_data = (sms,campaing_id)
			cursor.execute(update_query,update_data)

		if details and "state" in details:
			state = details['state']
			update_query = ("""UPDATE `campaign_master` SET `state` = %s
					WHERE `campaing_id` = %s """)
			update_data = (state,campaing_id)
			cursor.execute(update_query,update_data)

		if details and "shedule_date" in details:
			shedule_date = details['shedule_date']
			update_query = ("""UPDATE `campaign_master` SET `shedule_date` = %s
					WHERE `campaing_id` = %s """)
			update_data = (shedule_date,campaing_id)
			cursor.execute(update_query,update_data)

		if details and "shedule_time" in details:
			shedule_time = details['shedule_time']
			update_query = ("""UPDATE `campaign_master` SET `shedule_time` = %s
					WHERE `campaing_id` = %s """)
			update_data = (shedule_time,campaing_id)
			cursor.execute(update_query,update_data)

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
		customer_creation_date = details['customer_creation_date']
		pincode = details['pincode']
		model = details['model']
		brand = details['brand']
		purchase_cost = details['purchase_cost']
		organisation_id = details['organisation_id']
		retailer_store_id = details['retailer_store_id']
		purchase_date_range = details['purchase_date_range']
		last_update_id = details['retailer_store_id']

		if details and "category_id" in details:
			category_id = details['category_id']
		else:
			category_id = 0

		if details and "product_type" in details:
			product_type = details['product_type']
		else:
			product_type = 'n'

		insert_query = ("""INSERT INTO `audience_master`(`audience_name`,`customer_creation_date`,`pincode`,`model`,`brand`,`purchase_cost`,`organisation_id`,`retailer_store_id`,`purchase_date_range`,`last_update_id`,`category_id`,`product_type`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (audience_name,customer_creation_date,pincode,model,brand,purchase_cost,organisation_id,retailer_store_id,purchase_date_range,last_update_id,category_id,product_type)
		cursor.execute(insert_query,data)

		audience_id = cursor.lastrowid
		details['audience_id'] = audience_id

		return ({"attributes": {
			    		"status_desc": "audience_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK



#----------------------Add-Audience---------------------#

#----------------------Audience-List---------------------#
@name_space.route("/getAudienceListWithRetailerStoreId/<int:organisation_id>/<int:retailer_store_id>")	
class getAudienceListWithRetailerStoreId(Resource):
	def get(self,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `audience_master` a
			WHERE  a.`organisation_id` = %s and `retailer_store_id` = %s order by `audience_id` desc""")
		get_data = (organisation_id,retailer_store_id)
		cursor.execute(get_query,get_data)

		audience_data = cursor.fetchall()

		for key,data in enumerate(audience_data):			
			audience_data[key]['last_update_ts'] = str(data['last_update_ts'])
			#audience_data[key]['customer_count'] = 10

			'''filterURL = BASE_URL + "ecommerce_campaign_master/EcommerceCampaignMaster/getCustomerCount/{}/{}/{}/{}/{}/{}/{}/{}/{}".format(data['customer_creation_date'],data['pincode'],data['model'],data['brand'],data['purchase_cost'],data['organisation_id'],data['retailer_store_id'],data['purchase_date_range'],audience_data['category_id'])
				
			print(filterURL)
			filterRes = requests.get(filterURL).json()
			total = filterRes['responseList']['customer_count']

			audience_data[key]['customer_count'] = total'''
			audience_data[key]['customer_count'] = 0



		return ({"attributes": {
		    		"status_desc": "audience_details",
		    		"status": "success"
		    	},
		    	"responseList":audience_data}), status.HTTP_200_OK

#----------------------Audience-List---------------------#

#----------------------Update-Audience--------------------#

@name_space.route("/UpdateAudience/<int:audience_id>")
class UpdateAudience(Resource):
	@api.expect(audience_putmodel)
	def put(self,audience_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "audience_name" in details:
			audience_name = details['audience_name']
			update_query = ("""UPDATE `audience_master` SET `audience_name` = %s
					WHERE `audience_id` = %s """)
			update_data = (audience_name,audience_id)
			cursor.execute(update_query,update_data)

		if details and "customer_creation_date" in details:
			customer_creation_date = details['customer_creation_date']
			update_query = ("""UPDATE `audience_master` SET `customer_creation_date` = %s
					WHERE `audience_id` = %s """)
			update_data = (customer_creation_date,audience_id)
			cursor.execute(update_query,update_data)

		if details and "pincode" in details:
			pincode = details['pincode']
			update_query = ("""UPDATE `audience_master` SET `pincode` = %s
					WHERE `audience_id` = %s """)
			update_data = (pincode,audience_id)
			cursor.execute(update_query,update_data)

		if details and "model" in details:
			model = details['model']
			update_query = ("""UPDATE `audience_master` SET `model` = %s
					WHERE `audience_id` = %s """)
			update_data = (model,audience_id)
			cursor.execute(update_query,update_data)

		if details and "brand" in details:
			brand = details['brand']
			update_query = ("""UPDATE `audience_master` SET `brand` = %s
					WHERE `audience_id` = %s """)
			update_data = (brand,audience_id)
			cursor.execute(update_query,update_data)

		if details and "purchase_cost" in details:
			purchase_cost = details['purchase_cost']
			update_query = ("""UPDATE `audience_master` SET `purchase_cost` = %s
					WHERE `audience_id` = %s """)
			update_data = (purchase_cost,audience_id)
			cursor.execute(update_query,update_data)

		if details and "organisation_id" in details:
			organisation_id = details['organisation_id']
			update_query = ("""UPDATE `audience_master` SET `organisation_id` = %s
					WHERE `audience_id` = %s """)
			update_data = (organisation_id,audience_id)
			cursor.execute(update_query,update_data)

		if details and "retailer_store_id" in details:
			retailer_store_id = details['retailer_store_id']
			update_query = ("""UPDATE `audience_master` SET `retailer_store_id` = %s
					WHERE `audience_id` = %s """)
			update_data = (retailer_store_id,audience_id)
			cursor.execute(update_query,update_data)

		if details and "retailer_store_id" in details:
			retailer_store_id = details['retailer_store_id']
			update_query = ("""UPDATE `audience_master` SET `retailer_store_id` = %s
					WHERE `audience_id` = %s """)
			update_data = (retailer_store_id,audience_id)
			cursor.execute(update_query,update_data)

		if details and "purchase_date_range" in details:
			purchase_date_range = details['purchase_date_range']
			update_query = ("""UPDATE `audience_master` SET `purchase_date_range` = %s
					WHERE `audience_id` = %s """)
			update_data = (purchase_date_range,audience_id)
			cursor.execute(update_query,update_data)

		if details and "category_id" in details:
			category_id = details['category_id']
			update_query = ("""UPDATE `audience_master` SET `category_id` = %s
					WHERE `audience_id` = %s """)
			update_data = (category_id,audience_id)
			cursor.execute(update_query,update_data)

		if details and "product_type" in details:
			product_type = details['product_type']
			update_query = ("""UPDATE `audience_master` SET `product_type` = %s
					WHERE `audience_id` = %s """)
			update_data = (product_type,audience_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Audience",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Audience--------------------#

#----------------------Delete-Audience---------------------#

@name_space.route("/deleteAudience/<int:audience_id>")
class deleteAudience(Resource):
	def delete(self, audience_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		delete_query = ("""DELETE FROM `audience_master` WHERE `audience_id` = %s """)
		delData = (audience_id)
		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Delete Audience",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Audience---------------------#

#----------------------Create-Campaign-Audience-Mapping--------------------#

@name_space.route("/createCampaignAudienceMapping")
class createCampaignAudienceMapping(Resource):
	@api.expect(campaign_audience_mapping_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		campaign_id = details['campaign_id']		
		audience_id = details['audience_id']
		organisation_id = details['organisation_id']
		retailer_store_id = details['retailer_store_id']

		get_query = ("""SELECT * from `campaing_audience_mapping` WHERE `campaign_id` = %s and `audience_id` = %s and `organisation_id` = %s""")
		get_data = (campaign_id,audience_id,organisation_id)
		count_data = cursor.execute(get_query,get_data)

		if count_data > 0:
			return ({"attributes": {
				    		"status_desc": "campaign_audience_details",
				    		"status": "error",
				    		"message": "Already Exsits Audience With Campaign"
				    	},
				    	"responseList":details}), status.HTTP_200_OK

		else:

			insert_query = ("""INSERT INTO `campaing_audience_mapping`(`campaign_id`,`audience_id`,`organisation_id`,`retailer_store_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

			data = (campaign_id,audience_id,organisation_id,retailer_store_id,organisation_id)
			cursor.execute(insert_query,data)

			mapping_id = cursor.lastrowid
			details['mapping_id'] = mapping_id

			return ({"attributes": {
				    		"status_desc": "campaign_audience_details",
				    		"status": "success",
				    		"message": "Successfully Connected"
				    	},
				    	"responseList":details}), status.HTTP_200_OK

#----------------------Create-Campaign-Audience-Mapping--------------------#

#----------------------Delete-Audience---------------------#

@name_space.route("/deleteCampaignAudienceMapping/<int:campaign_id>/<int:audience_id>/<int:organisation_id>/<int:retailer_store_id>")
class deleteCampaignAudienceMapping(Resource):
	def delete(self, campaign_id,audience_id,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		delete_query = ("""DELETE FROM `campaing_audience_mapping` WHERE `campaign_id` = %s and `audience_id` = %s and `organisation_id` = %s and `retailer_store_id` = %s""")
		delData = (campaign_id,audience_id,organisation_id,retailer_store_id)
		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Delete Campaign Audience Mapping",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Audience---------------------#

#----------------------Audience-List---------------------#
@name_space.route("/getAudienceListByCampaignId/<int:organisation_id>/<int:campaign_id>")	
class getAudienceListByCampaignId(Resource):
	def get(self,organisation_id,campaign_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT a.*
			FROM `campaing_audience_mapping` cam
			INNER JOIN `audience_master` a ON a.`audience_id` = cam.`audience_id` 
			WHERE  cam.`organisation_id` = %s and cam.`campaign_id` = %s order by mapping_id desc""")
		get_data = (organisation_id,campaign_id)
		cursor.execute(get_query,get_data)

		audience_data = cursor.fetchall()

		for key,data in enumerate(audience_data):
			audience_data[key]['last_update_ts'] = str(data['last_update_ts'])
			'''filterURL = BASE_URL + "ecommerce_campaign_master/EcommerceCampaignMaster/getCustomerCount/{}/{}/{}/{}/{}/{}/{}/{}/{}".format(data['customer_creation_date'],data['pincode'],data['model'],data['brand'],data['purchase_cost'],data['organisation_id'],data['retailer_store_id'],data['purchase_date_range'],audience_data['category_id'])
				
			print(filterURL)
			filterRes = requests.get(filterURL).json()
			total = filterRes['responseList']['customer_count']

			audience_data[key]['customer_count'] = total'''
			audience_data[key]['customer_count'] =  0

		return ({"attributes": {
		    		"status_desc": "audience_details",
		    		"status": "success"
		    	},
		    	"responseList":audience_data}), status.HTTP_200_OK

#----------------------Audience-List---------------------#

#----------------------Customer-List-By-Audience-Id---------------------#
@name_space.route("/getCustomerListByAudienceId/<int:audience_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})	
class getCustomerListByAudienceId(Resource):
	def get(self,audience_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		get_query = ("""SELECT *
			FROM `audience_master` a
			WHERE  a.`audience_id` = %s""")
		get_data = (audience_id)
		cursor.execute(get_query,get_data)

		data = cursor.fetchone()

		organisation_id = data['organisation_id']

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		print(data)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateOrganizationId/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],organisation_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n': 
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePincodeOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],organisation_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and  data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],organisation_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandModelOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			print('hiii') 
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePurchaseCostOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],organisation_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandPurchaseCostOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],organisation_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,start,limit,page)	

		if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],organisation_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStore/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],organisation_id,data['retailer_store_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],organisation_id,data['retailer_store_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],organisation_id,data['retailer_store_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['retailer_store_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],organisation_id,data['retailer_store_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],organisation_id,retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],organisation_id,retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and  data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDate/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],organisation_id, data['purchase_date_range'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n': 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDate/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],organisation_id, data['purchase_date_range'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDate/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],brand,organisation_id, data['purchase_date_range'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDate/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['purchase_date_range'],start,limit,page)

		if  data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],organisation_id,data['purchase_date_range'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and  data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],organisation_id,purchase_date_range,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,purchase_date_range,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],organisation_id,purchase_date_range,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n': 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model'] != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and  data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)




		

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdCategoryId/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['category_id'],start,limit,page)
			
			
		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n': 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
		

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
			
		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStoreCatgoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStoreCatgoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
			#filterRes = requests.get(filterURL).json()
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n': 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateateCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n': 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['purchase_date_range'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		



		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdProductType/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['category_id'],start,limit,page)
			
			
		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n': 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdProductType/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdProductType/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdProductType/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdProductType/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdProductType/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
		

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStoreProductType/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
			
		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStoreProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStoreProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStoreProductType/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStoreProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
			#filterRes = requests.get(filterURL).json()
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStoreProductType/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStoreProductType/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStoreProductType/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateProductType/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateateProductType/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateProductType/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateProductType/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateProductType/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateRetailStoreProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStoreProductType/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStoreProductType/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStoreProductType/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['purchase_date_range'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStoreProductType/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStoreProductType/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreProductType/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreProductType/{}/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)



		


		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdProductTypeCategoryId/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['category_id'],start,limit,page)
			
			
		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n': 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdProductTypeCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdProductTypeCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdProductTypeCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdProductTypeCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
		

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStoreProductTypeCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
			
		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
			#filterRes = requests.get(filterURL).json()
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
		
		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateProductTypeCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateateProductTypeCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateProductTypeCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['purchase_date_range'],retailer_store_id,data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['retailer_store_id'],data['category_id'],start,limit,page)

		if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreProductTypeCategoryId/{}/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)	

		print(filterURL)

		filterRes = requests.get(filterURL).json()
		connection.commit()
		cursor.close()
		return filterRes

#----------------------Customer-List-By-Audience-Id---------------------#

#----------------------Campaign-Audienece-List---------------------#
@name_space.route("/getCampaignAndAudienceMapping/<int:organisation_id>/<int:retailer_store_id>")	
class getCampaignAndAudienceMapping(Resource):
	def get(self,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_campaing_audience_mapping_query = ("""SELECT cm.`campaign_name`,cm.`content_type`,cm.`content_text`,cm.`whatsapp`,cm.`email`,cm.`notification`,cm.`sms`,
			cm.`last_update_ts`,am.`audience_name`,am.`customer_creation_date`,am.`pincode`,am.`model`,am.`brand`,am.`purchase_cost`,am.`purchase_date_range`,am.`organisation_id`,am.`retailer_store_id`,am.`category_id`,am.`product_type`
			FROM `campaing_audience_mapping` cam 
			INNER JOIN `campaign_master` cm ON cm.`campaing_id` = cam.`campaign_id`
			INNER JOIN `audience_master` am ON am.`audience_id` = cam.`audience_id`
			WHERE  cam.`organisation_id` = %s and cam.`retailer_store_id` = %s order by mapping_id desc""")
		get_campaign_audience_mapping_data = (organisation_id,retailer_store_id)

		campaign_audience_count = cursor.execute(get_campaing_audience_mapping_query,get_campaign_audience_mapping_data)

		campaign_audience_data = cursor.fetchall()

		for key,data in enumerate(campaign_audience_data):
			print(data)				
			start = 0
			limit = 10
			page = 1	

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateOrganizationId/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],organisation_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n': 
				filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePincodeOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],organisation_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and  data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],organisation_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandModelOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				print('hiii') 
				filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePurchaseCostOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],organisation_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandPurchaseCostOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],organisation_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,start,limit,page)	

			if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],organisation_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStore/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],organisation_id,data['retailer_store_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],organisation_id,data['retailer_store_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],organisation_id,data['retailer_store_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['retailer_store_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],organisation_id,data['retailer_store_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],organisation_id,retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],organisation_id,retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and  data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDate/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],organisation_id, data['purchase_date_range'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n': 
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDate/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],organisation_id, data['purchase_date_range'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDate/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],brand,organisation_id, data['purchase_date_range'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDate/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['purchase_date_range'],start,limit,page)

			if  data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],organisation_id,data['purchase_date_range'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and  data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],organisation_id,purchase_date_range,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,purchase_date_range,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],organisation_id,purchase_date_range,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n': 
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model'] != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != '0' and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and  data['purchase_date_range'] != 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],organisation_id,data['purchase_date_range'],retailer_store_id,start,limit,page)




			

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdCategoryId/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['category_id'],start,limit,page)
				
				
			if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n': 
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['category_id'],start,limit,page)
				
			
			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['category_id'],start,limit,page)
				
			
			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],data['category_id'],start,limit,page)
				
			
			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
				
			
			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
				
			
			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
				

			if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['category_id'],start,limit,page)
			

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
				
			if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
			
			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStoreCatgoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] == 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStoreCatgoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
			
			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
				#filterRes = requests.get(filterURL).json()
			
			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)
			
			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] == 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],retailer_store_id,data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n': 
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateateCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] == 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n': 
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] == '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],organisation_id,data['purchase_date_range'],retailer_store_id,data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] == 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  == 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  == 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['retailer_store_id'],data['category_id'],start,limit,page)

			if data['customer_creation_date'] != '' and data['pincode']  != 0 and data['model']  != 'n' and data['brand'] != 'n' and data['purchase_cost'] != '0' and data['organisation_id'] != None and data['retailer_store_id'] != 0 and data['purchase_date_range'] != 'n' and data['category_id'] != 0 and data['product_type'] == 'n':
				filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(data['customer_creation_date'],data['pincode'],data['brand'],data['model'],data['purchase_cost'],data['organisation_id'],data['purchase_date_range'],data['retailer_store_id'],data['category_id'],start,limit,page)
				
			print(filterURL)

			filterRes = requests.get(filterURL).json()
			customer_list = filterRes['attributes']['customer_list']
			user_ids = []
			print(customer_list)
			for ckey,cdata in enumerate(customer_list):
				print(cdata['admin_id'])
				user_ids.append(str(cdata['admin_id']))
			print(user_ids)
			user_id = ",".join(user_ids)
			if data['content_type'] == 1:
				source_type = 1

				get_offer_query = ("""SELECT * from `offer` WHERE `offer_id` = %s""")
				get_offer_data = (data['content_text'])
				offer_count = cursor.execute(get_offer_query,get_offer_data)

				if offer_count > 0:
					offer_data = cursor.fetchone()
					if offer_data['is_product_meta_offer'] == 1:							
						product_meta_offer_mapping_query = (""" SELECT p.`product_id`,p.`product_name`,pmom.`product_meta_id`,pmom.`product_meta_code`
								FROM `product_meta_offer_mapping` pmom						
								INNER JOIN `product` p ON p.`product_id` = pmom.`product_id` 
								where  pmom.`offer_id` = %s""")
						product_meta_offer_mapping_data = (offer_data['offer_id'])
						count_product_meta_offer_mapping_data = cursor.execute(product_meta_offer_mapping_query,product_meta_offer_mapping_data)

						if count_product_meta_offer_mapping_data > 0:
							offer_product_meta = cursor.fetchone()
							product_id = offer_product_meta['product_id']
							product_meta_id = offer_product_meta['product_meta_id']
							product_meta_code = offer_product_meta['product_meta_code']
							product_name = offer_product_meta['product_name']								
						else:
							product_id = 0
							product_meta_id = 0
							product_meta_code = 0
							product_name = ''
					else:
						get_offer_product_query = ("""SELECT p.`product_id`,p.`product_name`
								FROM `product_offer_mapping` pom
								INNER JOIN `product` p ON p.`product_id` = pom.`product_id`
								where pom.`offer_id` = %s""")
						get_product_offer_data = (offer_data['offer_id'])
						count_product_offer  = cursor.execute(get_offer_product_query,get_product_offer_data)

						if count_product_offer > 0:
							product_offer_data = cursor.fetchone()
							product_id = product_offer_data['product_id']
							product_meta_id = 0
							product_meta_code = 0
							product_name = ''
						else:
							product_id = 0
							product_meta_id = 0
							product_meta_code = 0
							product_name = ''

						
					offer_type = offer_data['offer_type']
					is_landing_page = offer_data['is_landing_page']						
					text = offer_data['coupon_code']
					image = offer_data['offer_image']
				else:
					offer_type = 0
					is_landing_page = 0
					text = ''
					image = ''
					product_id = 0
					product_meta_id = 0
					product_meta_code = 0
					product_name = ''

				catalog_name = ''
				title = "offer"

			elif data['content_type'] == 2:
				source_type = 2

				get_catalogue_query = ("""SELECT * from `catalogs` WHERE `catalog_id` = %s""")
				get_catalogue_data = (catalog_id)
				catalogue_count = cursor.execute(get_catalogue_query,get_catalogue_data)

				if catalogue_count > 0:
					catalogue_data = cursor.fetchone()
					catalog_name = catalogue_data['catalog_name']	
					text = 	catalogue_data['catalog_name']					
				else:
					catalog_name = ''

				offer_type = 0
				is_landing_page = 0
				image = ''
				product_id = 0
				product_meta_id = 0
				product_meta_code = 0
				product_name = ''
				title = "catalogue"

			elif data['content_type'] == 3:				
				text = 'Image Link'
				image = data['content_text']				
				title = "Image"

			elif data['content_type'] == 4:				
				text = data['content_text']	
				organisation_id = organisation_id								
				title = "text"

			elif data['content_type'] == 5:
				source_type = 3
				text = 'Video Link'	
				image = data['content_text']				
				offer_type = 0
				is_landing_page = 0
				catalog_name = ''
				product_id = 0
				product_meta_id = 0
				product_meta_code = 0
				product_name = ''
				title = "Video"

				
			if data['content_type'] == 1 or data['content_type'] == 2:

				payloadpushData = {
						"source_id":int(data['content_text']),
						"source_type":source_type,
						"offer_type":offer_type,
						"product_id":product_id,
						"product_meta_code": product_meta_code,
						"product_meta_id": product_meta_id,
						"catalog_name":catalog_name,
						"is_landing_page":is_landing_page,
						"product_name":product_name,
						"user_id":[user_id],
						"text":text,
						"image":image,
						"title":title,	
						"organisation_id":organisation_id					
				}					

				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				sendAppPushNotificationUrl = BASE_URL + "ecommerce_customer_admin/EcommerceCustomerAdmin/sendNotifications"	
				print(sendAppPushNotificationUrl)
				send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

				print(send_push_notification)

			elif data['content_type'] == 4:
				for ckey,cdata in enumerate(customer_list):
					customer_id = cdata['admin_id']
					payloadpushData = {						
						"customer_id":customer_id,
						"text":text,						
						"title":title,	
						"organisation_id":organisation_id					
					}
					headers = {'Content-type':'application/json', 'Accept':'application/json'}		
					sendAppPushNotificationUrl = BASE_URL + "ecommerce_product_admin/EcommerceProductAdmin/sendNotifications"
					print(sendAppPushNotificationUrl)
					send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()
					print(send_push_notification)

			elif data['content_type'] == 3:
				for ckey,cdata in enumerate(customer_list):
					customer_id = cdata['admin_id']
					payloadpushData = {						
						"customer_id":customer_id,
						"text":text,						
						"title":title,
						"image":image,	
						"organisation_id":organisation_id					
					}
					headers = {'Content-type':'application/json', 'Accept':'application/json'}		
					sendAppPushNotificationUrl = BASE_URL + "ecommerce_campaign_master/EcommerceCampaignMaster/sendNotifications"
					print(sendAppPushNotificationUrl)
					send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()
					print(send_push_notification)



			campaign_audience_data[key]['last_update_ts'] = str(data['last_update_ts'])


		return ({"attributes": {
			    		"status_desc": "campaign_audience_details",
			    		"status": "success"
			    	},
			    	"responseList":campaign_audience_data}), status.HTTP_200_OK

#----------------------Campaign-Audienece-List---------------------#

#----------------------Send-Notification---------------------#

@name_space.route("/sendNotifications")
class sendNotifications(Resource):
	@api.expect(notification_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		organisation_id = details['organisation_id']
		customer_id = details['customer_id']


		get_organisation_firebase_query = ("""SELECT `firebase_key`
								FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
		get_organisation_firebase_data = (organisation_id)
		cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
		firebase_data = cursor.fetchone()

		get_devices_query = ("""SELECT *
								FROM `devices` WHERE  `organisation_id` = %s and `user_id` = %s""")
		get_devices_data = (organisation_id,customer_id)
		cursor.execute(get_devices_query,get_devices_data)
		devices_data = cursor.fetchall()

		for key,data in enumerate(devices_data):	
			if data['device_type'] == 2:
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				sendAppPushNotificationUrl = BASE_URL + "ecommerce_product/EcommerceProduct/sendAppPushNotifications"
				payloadpushData = {
									"device_id":data['device_token'],
									"firebase_key": firebase_data['firebase_key'],
									"image":details['image'],
									"text":details['text'],
									"title":details['title']
								}
				print(payloadpushData)
				send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		return ({"attributes": {"status_desc": "Push Notification",
									"status": "success"},
					"responseList":{}}), status.HTTP_200_OK

#----------------------Send-Notification---------------------#

#----------------------Customer-Count---------------------#
@name_space.route("/getCustomerCount/<string:customer_creation_date>/<int:pincode>/<string:model>/<string:brand>/<string:pcost>/<int:organisation_id>/<int:retailer_store_id>/<string:purchase_date_range>/<int:category_id>")	
class getCustomerCount(Resource):
	def get(self,customer_creation_date,pincode,model,brand,pcost,organisation_id,retailer_store_id,purchase_date_range,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		start = 0
		limit = 10
		page = 1	
		purchase_cost = pcost
		sdate = customer_creation_date

		if sdate != '' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateOrganizationId/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,start,limit,page)
			
			
		if sdate != '' and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id == 0: 
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePincodeOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,start,limit,page)
			
		
		if sdate != '' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,start,limit,page)
			
		
		if sdate != '' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandModelOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,start,limit,page)
			
		
		if sdate != '' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePurchaseCostOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,start,limit,page)
			
		
		if sdate != '' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandPurchaseCostOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,start,limit,page)
			
		
		if sdate != '' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,start,limit,page)
			

		if sdate != '' and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,start,limit,page)
		

		if sdate != '' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStore/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,retailer_store_id,start,limit,page)
			
		if sdate != '' and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,retailer_store_id,start,limit,page)
		
		if sdate != '' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,retailer_store_id,start,limit,page)
		
		if sdate != '' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,retailer_store_id,start,limit,page)
			#filterRes = requests.get(filterURL).json()
		
		if sdate != '' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,retailer_store_id,start,limit,page)
		
		if sdate != '' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDate/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,purchase_date_range,start,limit,page)

		if sdate != '' and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id == 0: 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDate/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,purchase_date_range,start,limit,page)

		if sdate != '' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDate/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,purchase_date_range,start,limit,page)

		if sdate != '' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDate/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,purchase_date_range,start,limit,page)

		if sdate != '' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,purchase_date_range,start,limit,page)

		if sdate != '' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,purchase_date_range,start,limit,page)

		if sdate != '' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,purchase_date_range,start,limit,page)

		if sdate != '' and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,purchase_date_range,start,limit,page)

		if sdate != '' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id == 0: 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if sdate != '' and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)


		



		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdCategoryId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,category_id,start,limit,page)
			
			
		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id != 0: 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,category_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,category_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,category_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,category_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,category_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,category_id,start,limit,page)
			

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,category_id,start,limit,page)
		

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,retailer_store_id,category_id,start,limit,page)
			
		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,retailer_store_id,category_id,start,limit,page)
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStoreCatgoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id == 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStoreCatgoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,retailer_store_id,category_id,start,limit,page)
		
		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,retailer_store_id,category_id,start,limit,page)
			#filterRes = requests.get(filterURL).json()
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,retailer_store_id,category_id,start,limit,page)
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,purchase_date_range,category_id,start,limit,page)

		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id != 0: 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,purchase_date_range,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,purchase_date_range,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateateCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,purchase_date_range,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,purchase_date_range,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,purchase_date_range,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,purchase_date_range,category_id,start,limit,page)

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,purchase_date_range,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,purchase_date_range,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id != 0: 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,purchase_date_range,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,purchase_date_range,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,purchase_date_range,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,purchase_date_range,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,purchase_date_range,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,purchase_date_range,retailer_store_id,category_id,start,limit,page)

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n' and category_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStoreCategoryId/{}/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,purchase_date_range,retailer_store_id,category_id,start,limit,page)

		print(filterURL)

		filterRes = requests.get(filterURL).json()
		total = filterRes['attributes']['total']

		return ({"attributes": {
		    		"status_desc": "Customer_count",
		    		"status": "success"
		    	},
		    	"responseList":{"customer_count":total}}), status.HTTP_200_OK



#----------------------Customer-Count---------------------#