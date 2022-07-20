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

ecommerce_product_log = Blueprint('ecommerce_product_log_api', __name__)
api = Api(ecommerce_product_log,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceProductLog',description='Ecommerce Product Log')

product_log_postmodel = api.model('SelectProduct', {
	"product_id":fields.Integer,
	"product_name":fields.String,
	"product_long_description":fields.String,
	"product_short_description":fields.String,
	"category_id":fields.String,
	"product_status":fields.String,
	"product_meta_id":fields.Integer,
	"product_meta_code":fields.Integer,
	"meta_key_text":fields.String,
	"other_specification_json":fields.String,
	"in_price":fields.Integer,
	"out_price":fields.Integer,
	"loyalty_points":fields.Integer,
	"product_meta_image_id":fields.Integer,
	"deleted_image_link":fields.String,
	"default_image_flag":fields.Integer,
	"is_gallery":fields.Integer,
	"comments":fields.String,
	"employee_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_updated_ip_address":fields.String
})

#----------------------Add-Product-Log---------------------#

@name_space.route("/AddProductLog")
class AddProductLog(Resource):
	@api.expect(product_log_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "product_id" in details:
			product_id = details['product_id']
		else:
			product_id = 0

		if details and "product_name" in details:
			product_name = details['product_name']
		else:
			product_name = ""

		if details and "product_long_description" in details:
			product_long_description = details['product_long_description']
		else:
			product_long_description = ""

		if details and "product_short_description" in details:
			product_short_description = details['product_short_description']
		else:
			product_short_description = ""

		if details and "category_id" in details:
			category_id = details['category_id']
		else:
			category_id = ""

		if details and "product_status" in details:
			product_status = details['product_status']
		else:
			product_status = ""

		if details and "product_meta_id" in details:
			product_meta_id = details['product_meta_id']
		else:
			product_meta_id = 0

		if details and "product_meta_image_id" in details:
			product_meta_image_id = details['product_meta_image_id']
		else:
			product_meta_image_id = 0

		if details and "default_image_flag" in details:
			default_image_flag = details['default_image_flag']
		else:
			default_image_flag = 0

		if details and "is_gallery" in details:
			is_gallery = details['is_gallery']
		else:
			is_gallery = 0

		if details and "comments" in details: 
			comments =  details['comments']
		else:
			comments = ""

		if details and "deleted_image_link" in details:
			deleted_image_link = details['deleted_image_link']
		else:
			deleted_image_link = ""

		if details and "product_meta_code" in details:
			product_meta_code = details['product_meta_code']
		else:
			product_meta_code = ""	

		if details and "meta_key_text" in details:
			meta_key_text = details['meta_key_text']
		else:
			meta_key_text = ""

		if details and "other_specification_json" in details:
			other_specification_json = details['other_specification_json']
		else:
			other_specification_json = ""

		if details and "in_price" in details:
			in_price = details['in_price']
		else:
			in_price = ""

		if details and "out_price" in details:
			out_price = details['out_price']
		else:
			out_price = ""

		if details and "loyalty_points" in details:
			loyalty_points = details['loyalty_points']
		else:
			loyalty_points = ""

		if details and "last_updated_ip_address" in details:
			last_updated_ip_address = details['last_updated_ip_address']
		else:
			last_updated_ip_address = ""

		employee_id = details['employee_id']
		organisation_id = details['organisation_id']


		insert_query = ("""INSERT INTO `product_log`(`product_id`,`product_name`,`product_long_description`,`product_short_description`,`category_id`,`status`,`product_meta_id`,`product_meta_code`,`meta_key_text`,
			`other_specification_json`,`in_price`,`out_price`,`loyalty_points`,`product_meta_image_id`,
			`default_image_flag`,`is_gallery`,`comments`,`deleted_image_link`,`employee_id`,`organisation_id`,`last_updated_ip_address`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_id,product_name,product_long_description,product_short_description,category_id,product_status,product_meta_id,product_meta_code,meta_key_text,other_specification_json,
			in_price,out_price,loyalty_points,product_meta_image_id,default_image_flag,
				is_gallery,comments,deleted_image_link,employee_id,organisation_id,last_updated_ip_address)
		cursor.execute(insert_query,data)
		log_id = cursor.lastrowid

		details['log_id'] = log_id

		return ({"attributes": {
			    	"status_desc": "product_log_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Add-Product-Log---------------------#
