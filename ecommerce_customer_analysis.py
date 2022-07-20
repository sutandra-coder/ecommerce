from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2 import Environment, FileSystemLoader
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
import math
import os

env = Environment(
    loader=FileSystemLoader('%s/templates/' % os.path.dirname(__file__)))

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

'''def ecommerce_analytics():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='ecommerce_analytics',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def ecommerce_analytics():
	connection = pymysql.connect(host='ecommerce.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='oxjkW0NuDtjKfEm5WZuP',
	                             db='ecommerce_analytics',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

ecommerce_customer_analysis = Blueprint('ecommerce_customer_analysis_api', __name__)
api = Api(ecommerce_customer_analysis,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceCustomerAnalysis',description='Ecommerce Customer Analysis')

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#

@name_space.route("/CustomerCountWithOrganisationAndRetailStore/<string:filterkey>/<int:organisation_id>")	
class CustomerCountWithOrganisationAndRetailStore(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = ecommerce_analytics()
		cur = conn.cursor()

		loggedin_data = {}		

		if filterkey == 'today':
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			get_loggedin_user_query = ("""SELECT count(distinct(`customer_id`)) as total_user FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (today_date,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchone()
				loggedin_data['total_customer_count'] = loggedin_user_data['total_user']
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
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`)=%s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (today_date,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
							get_customer_retailer_data = (organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'])

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

		if filterkey == 'yesterday':
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_loggedin_user_query = ("""SELECT count(distinct(`customer_id`)) as total_user FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (yesterday,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchone()
				loggedin_data['total_customer_count'] = loggedin_user_data['total_user']
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
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` WHERE date(`last_update_ts`)=%s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (yesterday,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
							get_customer_retailer_data = (organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'])

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

		if filterkey == 'last 7 days':
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_loggedin_user_query = ("""SELECT count(distinct(`customer_id`)) as total_user FROM `customer_store_analytics` where date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (start_date,end_date,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchone()
				loggedin_data['total_customer_count'] = loggedin_user_data['total_user']
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
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (start_date,end_date,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
							get_customer_retailer_data = (organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'])

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
			
		if filterkey == 'this month':
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_loggedin_user_query = ("""SELECT count(distinct(`customer_id`)) as total_user FROM `customer_store_analytics` where date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (start_date,end_date,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchone()
				loggedin_data['total_customer_count'] = loggedin_user_data['total_user']
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
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (start_date,end_date,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
							get_customer_retailer_data = (organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'])

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

		if filterkey == 'lifetime':
			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_loggedin_user_query = ("""SELECT count(distinct(`customer_id`)) as total_user FROM `customer_store_analytics` where date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0 """)
			get_loggedin_user_data = (start_date,end_date,organisation_id)
			count_loggedin_user = cur.execute(get_loggedin_user_query,get_loggedin_user_data)

			if count_loggedin_user > 0:
				loggedin_user_data = cur.fetchone()
				loggedin_data['total_customer_count'] = loggedin_user_data['total_user']
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
					get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
					store_analytics_view_data = (start_date,end_date,organisation_id)
					count_store_analytics_view = cur.execute(get_store_analytics_view_query,store_analytics_view_data)

					if count_store_analytics_view > 0:
						store_analytics_view = cur.fetchall()

						for sakey,sadata in enumerate(store_analytics_view):

							get_customer_retailer_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s""")	
							get_customer_retailer_data = (organisation_id,nrldata['retailer_store_id'],nrldata['retailer_store_store_id'],sadata['customer_id'])

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

		return ({"attributes": {
		    		"status_desc": "Customer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{"loggedin_data":loggedin_data} }), status.HTTP_200_OK

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#

#--------------------Customer-List-With-Organisation-And-Retailer-Store-------------------------#

@name_space.route("/CustomerListWithOrganisationAndRetailStore/<string:filterkey>/<string:list_type>/<int:retailer_store_store_id>/<int:organisation_id>")	
class CustomerListWithOrganisationAndRetailStore(Resource):
	def get(self,filterkey,list_type,retailer_store_store_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = ecommerce_analytics()
		cur = conn.cursor()

		if list_type == 'loggedin_data':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (today_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (yesterday,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []



				if len(customer_data) >0:
					for fkey,fdata in enumerate(customer_data):
						get_customer_detail_information_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation` FROM `admins` a where a.`admin_id` = %s""")
						get_customer_detail_data = (fdata['customer_id'])

						count_customer_detail_data = cursor.execute(get_customer_detail_information_query,get_customer_detail_data)

						if count_customer_detail_data > 0:
							user_data = cursor.fetchone()
							customer_data[fkey]['admin_id'] = user_data['admin_id']
							customer_data[fkey]['name'] = user_data['name']
							customer_data[fkey]['phoneno'] = user_data['phoneno']
							customer_data[fkey]['dob'] = user_data['dob']
							customer_data[fkey]['anniversary'] = user_data['anniversary']
							customer_data[fkey]['profile_image'] = user_data['profile_image']
							customer_data[fkey]['address_line_1'] = user_data['address_line_1']
							customer_data[fkey]['address_line_2'] = user_data['address_line_2']
							customer_data[fkey]['city'] = user_data['city']
							customer_data[fkey]['country'] = user_data['country']
							customer_data[fkey]['state'] = user_data['state']
							customer_data[fkey]['pincode'] = user_data['pincode']
							customer_data[fkey]['loggedin_status'] = user_data['loggedin_status']
							customer_data[fkey]['date_of_creation'] = str(user_data['date_of_creation'])

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (user_data['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								customer_data[fkey]['retailer_city'] = city_data['retailer_city']
								customer_data[fkey]['retailer_address'] = city_data['retailer_address']
							else:
								customer_data[fkey]['retailer_city'] = ""
								customer_data[fkey]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (user_data['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								customer_data[fkey]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								customer_data[fkey]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (user_data['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								customer_data[fkey]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								customer_data[fkey]['enquiery_count'] = 0

							get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
							get_customer_type_data = (user_data['admin_id'],organisation_id)
							count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

							if count_customer_type > 0:
								customer_type_data = cursor.fetchone()
								customer_data[fkey]['customertype'] = customer_type_data['customer_type']
							else:
								customer_data[fkey]['customertype'] = ""

							customer_data[fkey]['outstanding'] = 0

							cursor.execute("""SELECT sum(`amount`)as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and 
						 		`status`='Complete' and `organisation_id` = %s""",(user_data['admin_id'],organisation_id))
							costDtls = cursor.fetchone()
						
							if costDtls['total'] != None:
								customer_data[fkey]['purchase_cost'] = costDtls['total']
							else:
								customer_data[fkey]['purchase_cost'] = 0


		return ({"attributes": {
		    		"status_desc": "Customer Details",
		    		"status": "success"
		    	},
		    	"responseList":customer_data }), status.HTTP_200_OK


#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#

@name_space.route("/CustomerCountWithOrganisationAndRetailStorewithRetailerStoreId/<string:list_type>/<string:filterkey>/<int:organisation_id>/<int:retailer_store_id>")	
class CustomerCountWithOrganisationAndRetailStorewithRetailerStoreId(Resource):
	def get(self,list_type,filterkey,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = ecommerce_analytics()
		cur = conn.cursor()

		if list_type == 'loggedin_data':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")
				print(today_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (today_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []
					

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`)= %s and `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (yesterday,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []


			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and  date(`last_update_ts`) <= %sand `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []


			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and  date(`last_update_ts`) <= %sand `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []


			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_loged_In_customer_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and  date(`last_update_ts`) <= %sand `organisation_id` = %s and `customer_id`!= 0""")
				get_loged_In_customer_data = (start_date,end_date,organisation_id)
				count_loged_In_customer_data = cur.execute(get_loged_In_customer_query,get_loged_In_customer_data)
				print(cur._last_executed)

				if count_loged_In_customer_data > 0:
					
					loggedin_customer_data = cur.fetchall()
					for key,data in enumerate(loggedin_customer_data):
						get_user_store_query = ("""SELECT * 
								FROM `user_retailer_mapping` ur
								WHERE ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and ur.`user_id` = %s """)
						get_user_store_data = (organisation_id,retailer_store_id,data['customer_id'])
						count_user_store_data = cursor.execute(get_user_store_query,get_user_store_data)

						if count_user_store_data > 0:
							loggedin_customer_data[key]['s_view'] = 1
						else:
							loggedin_customer_data[key]['s_view'] = 0

					customer_data = []
					for nkey,ndata in  enumerate(loggedin_customer_data):
						if ndata['s_view'] == 1:
							customer_data.append(loggedin_customer_data[nkey])
					print(customer_data)
				else:
					customer_data = []

		else:
			customer_data = []			

		return ({"attributes": {
		    		"status_desc": "Customer Details",
		    		"status": "success"
		    	},
		    	"responseList": {"customer_count":len(customer_data)}}), status.HTTP_200_OK


