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
import pandas as pd

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

#----------------------database-connection---------------------#
def mysql_connection_myelsa():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

ecommerce_product_export = Blueprint('ecommerce_product_expoty_api', __name__)
api = Api(ecommerce_product_export,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceProductExport',description='Ecommerce Product Export')



#----------------------Product-List---------------------#
@name_space.route("/productList/<int:organisation_id>")	
class productList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		get_query = ("""SELECT p.`product_id`,p.`product_name`,mm.`meta_key` as category,p.`status`,p.`category_id`,pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,mkvm.`meta_key_value` as brand 
				FROM `product` p
				INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
				INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
				INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
				INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`
				INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = pbm.`brand_id`
				WHERE  pom.`organisation_id` = %s and p.`status` = 1 and pbm.`organisation_id` = %s""")
		get_data = (organisation_id,organisation_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			print(data['product_id'])

			if data['meta_key_text']:

				a_string = data['meta_key_text']
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

					product_data[key]['met_key_value'] = met_key
			else:
				product_data[key]['met_key_value'] = ""

		df = pd.DataFrame(product_data)
		df.to_excel('./product.xlsx')

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Customer-List---------------------#
@name_space.route("/customerList/<int:organisation_id>/<int:retailer_store_id>")	
class customerList(Resource):
	def get(self,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_customer_query = ("""SELECT a.`first_name`,a.`phoneno`,a.`loggedin_status`,a.`registration_type`,rss.`store_name`
							 	FROM `admins` a
							 	INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = a.`admin_id`	
							 	INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = urm.`retailer_store_id`						 							 					 			 
								WHERE urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""")
		getCustomerData = (organisation_id,retailer_store_id)
		count_customer_data = cursor.execute(get_customer_query,getCustomerData)

		search_meta = cursor.fetchall()

		for key,data in enumerate(search_meta):				

			if data['loggedin_status'] == 1:
				search_meta[key]['loggedin_status'] = "logged In" 
			else:
				search_meta[key]['loggedin_status'] = "Never Logged In"

			if data['registration_type'] == 4 or data['registration_type'] == 1:
				search_meta[key]['Lead_Source'] = "Online Store"
			else:
				search_meta[key]['Lead_Source'] = "Facebook"

		df = pd.DataFrame(search_meta)
		df.to_excel('./customer_list.xlsx')

		return ({"attributes": {
					"status_desc": "customer_list",
					"status": "success"
				},
				"responseList":search_meta}), status.HTTP_200_OK

#----------------------Customer-List---------------------#

#----------------------Student-List-From-Myelsa--------------------#

@name_space.route("/StudentList")	
class StudentList(Resource):
	def get(self):
		connection = mysql_connection_myelsa()
		cursor = connection.cursor()

		get_query = ("""SELECT iuc.`EMAIL_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`FIRST_NAME`,sdt.`SEC` 
			FROM `student_dtls` sdt 
			INNER JOIN `institution_user_credential` iuc ON iuc.`INSTITUTION_USER_ID` = sdt.`INSTITUTION_USER_ID_STUDENT` 
			WHERE sdt.`INSTITUTION_ID` = 1""")
		cursor.execute(get_query)

		student_data = cursor.fetchall()

		

		df = pd.DataFrame(student_data)
		df.to_excel('./student.xlsx')

		return ({"attributes": {
		    		"status_desc": "student_details",
		    		"status": "success"
		    	},
		    	"responseList":student_data}), status.HTTP_200_OK

#----------------------Student-List-From-Myelsa--------------------#

#----------------------Student-List-From-Myelsa--------------------#

@name_space.route("/TeacherList")	
class TeacherList(Resource):
	def get(self):
		connection = mysql_connection_myelsa()
		cursor = connection.cursor()

		get_query = ("""SELECT iuc.`EMAIL_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`FIRST_NAME`,tds.`SEC`, tds.`SUBJECT`
			FROM `teacher_dtls` tds 
			INNER JOIN `institution_user_credential` iuc ON iuc.`INSTITUTION_USER_ID` = tds.`INSTITUTION_USER_ID_TEACHER` 
			WHERE tds.`INSTITUTION_ID` = 1""")
		cursor.execute(get_query)

		teacher_data = cursor.fetchall()

		

		df = pd.DataFrame(teacher_data)
		df.to_excel('./teacher.xlsx')

		return ({"attributes": {
		    		"status_desc": "teacher_details",
		    		"status": "success"
		    	},
		    	"responseList":teacher_data}), status.HTTP_200_OK

#----------------------Student-List-From-Myelsa--------------------#