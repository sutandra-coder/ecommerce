from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
import requests
import calendar
import json
import moment

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

def mysql_connection_analytics():
	connection_analytics = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='ecommerce_analytics',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection_analytics'''

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

ecommerce_retailer = Blueprint('ecommerce_retailer_api', __name__)
api = Api(ecommerce_retailer,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceRetailer',description='Ecommerce Retailer')

retailer_postmodel = api.model('SelectRetailer', {
	"first_name":fields.String(required=True),
	"last_name":fields.String,
	"email":fields.String(required=True),
	"password":fields.String(required=True),
	"phoneno":fields.Integer(required=True),
	"address_line_1":fields.String(required=True),
	"address_line_2":fields.String,
	"city":fields.String,
	"county":fields.String(required=True),
	"state":fields.String(required=True),
	"pincode":fields.Integer(required=True),
	"emergency_contact":fields.Integer
	})

retailer_putmodel = api.model('UpdateRetailer', {
	"first_name":fields.String(required=True),
	"last_name":fields.String,
	"phoneno":fields.Integer(required=True),
	"address_line_1":fields.String(required=True),
	"address_line_2":fields.String,
	"city":fields.String,
	"county":fields.String(required=True),
	"state":fields.String(required=True),
	"pincode":fields.Integer(required=True),
	"emergency_contact":fields.Integer
	})

#----------------------Add-Retailer---------------------#

@name_space.route("/AddRetailer")
class AddRetailer(Resource):
	@api.expect(retailer_postmodel)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		first_name = details['first_name']
		last_name = details['last_name']
		email = details['email']
		password = details['password']
		phoneno = details['phoneno']
		address_line_1 = details['address_line_1']
		address_line_2 = details['address_line_2']
		city = details['city']
		county = details['county']
		state = details['state']
		pincode = details['pincode']
		emergency_contact = details['emergency_contact']
		role_id = 3
		admin_status = 1

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		get_query = ("""SELECT `email`
			FROM `admins` WHERE `email` = %s """)

		getData = (email)
		
		count_retailer = cursor.execute(get_query,getData)

		if count_retailer > 0:
			return ({"attributes": {
			    		"status_desc": "retailer_details",
			    		"status": "error"
			    	},
			    	"responseList":"Retailer Already Exsits" }), status.HTTP_200_OK

		else:

			insert_query = ("""INSERT INTO `admins`(`first_name`,`last_name`,`email`,`org_password`,
								`phoneno`,`address_line_1`,`address_line_2`,`city`,`county`,
								`state`,`pincode`,`emergency_contact`,`role_id`,`status`,`date_of_creation`) 
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			data = (first_name,last_name,email,password,phoneno,address_line_1,address_line_2,city,county,state,pincode,emergency_contact,role_id,admin_status,date_of_creation)
			cursor.execute(insert_query,data)

			admin_id = cursor.lastrowid
			details['admin_id'] = admin_id

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "retailer_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Retailer---------------------#


#----------------------Delete-Retailer--------------------#

@name_space.route("/deleteRetailer/<int:retailer_id>")
class deleteRetailer(Resource):
	def delete(self, retailer_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		update_query = ("""UPDATE `admins` SET `status` = 0
				WHERE `admin_id` = %s """)
		updateData = (retailer_id)
		
		cursor.execute(update_query,updateData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Retailer",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Retailer---------------------#


#----------------------Update-Retailer--------------------#

@name_space.route("/updateRetailer/<int:retailer_id>")
class updateRetailer(Resource):
	@api.expect(retailer_putmodel)
	def put(self,retailer_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		first_name = details['first_name']
		last_name = details['last_name']		
		phoneno = details['phoneno']
		address_line_1 = details['address_line_1']
		address_line_2 = details['address_line_2']
		city = details['city']
		county = details['county']
		state = details['state']
		pincode = details['pincode']
		emergency_contact = details['emergency_contact']

		connection = mysql_connection()
		cursor = connection.cursor()

		if details and "first_name" in details:
			first_name = details.get('first_name')			

			update_query = ("""UPDATE `admins` SET `first_name` = %s
				WHERE `admin_id` = %s """)
			update_data = (first_name,retailer_id)
			cursor.execute(update_query,update_data)

		if details and "last_name" in details:
			last_name = details.get('last_name')			

			update_query = ("""UPDATE `admins` SET `last_name` = %s
				WHERE `admin_id` = %s """)
			update_data = (last_name,retailer_id)
			cursor.execute(update_query,update_data)

		if details and "phoneno" in details:
			phoneno = details.get('phoneno')			

			update_query = ("""UPDATE `admins` SET `phoneno` = %s
				WHERE `admin_id` = %s """)
			update_data = (phoneno,retailer_id)
			cursor.execute(update_query,update_data)


		if details and "address_line_1" in details:
			address_line_1 = details.get('address_line_1')			

			update_query = ("""UPDATE `admins` SET `address_line_1` = %s
				WHERE `admin_id` = %s """)
			update_data = (address_line_1,retailer_id)
			cursor.execute(update_query,update_data)
		
		if details and "address_line_2" in details:
			address_line_2 = details.get('address_line_2')			

			update_query = ("""UPDATE `admins` SET `address_line_2` = %s
				WHERE `admin_id` = %s """)
			update_data = (address_line_2,retailer_id)
			cursor.execute(update_query,update_data)

		if details and "city" in details:
			city = details.get('city')			

			update_query = ("""UPDATE `admins` SET `city` = %s
				WHERE `admin_id` = %s """)
			update_data = (city,retailer_id)
			cursor.execute(update_query,update_data)

		if details and "county" in details:
			county = details.get('county')			

			update_query = ("""UPDATE `admins` SET `county` = %s
				WHERE `admin_id` = %s """)
			update_data = (county,retailer_id)
			cursor.execute(update_query,update_data)

		if details and "state" in details:
			state = details.get('state')			

			update_query = ("""UPDATE `admins` SET `state` = %s
				WHERE `admin_id` = %s """)
			update_data = (state,retailer_id)
			cursor.execute(update_query,update_data)

		if details and "pincode" in details:
			pincode = details.get('pincode')			

			update_query = ("""UPDATE `admins` SET `pincode` = %s
				WHERE `admin_id` = %s """)
			update_data = (pincode,retailer_id)
			cursor.execute(update_query,update_data)

		if details and "emergency_contact" in details:
			emergency_contact = details.get('emergency_contact')			

			update_query = ("""UPDATE `admins` SET `emergency_contact` = %s
				WHERE `admin_id` = %s """)
			update_data = (emergency_contact,retailer_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
			    		"status_desc": "retailer_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Update-Retailer---------------------#

#----------------------Get-Retailer-List---------------------#

@name_space.route("/getRetailerList/<string:filterkey>/<string:start_date>/<string:end_date>")	
class getRetailerList(Resource):
	def get(self,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if filterkey == 'all':

			get_query = ("""SELECT *
				FROM `organisation_master`""")

			cursor.execute(get_query)

			retailer_data = cursor.fetchall()			

		if filterkey == 'today':
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			get_query = ("""SELECT *
				FROM `organisation_master` WHERE DATE(`last_update_ts`) = %s""")
			get_data = (today_date)

			cursor.execute(get_query,get_data)

			retailer_data = cursor.fetchall()

			for key,data in enumerate(retailer_data):	
				get_customer_count_query = ("""SELECT count(*) as customer_count
					FROM `admins` WHERE `organisation_id`= %s""")
				get_customer_count_data = (data['organisation_id'])
				customer_count = cursor.execute(get_customer_count_query,get_customer_count_data)

				customer_data = cursor.fetchone()

				retailer_data[key]['customer_count'] = customer_data['customer_count']

		if filterkey == 'yesterday':
			
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_query = ("""SELECT *
				FROM `organisation_master` WHERE DATE(`last_update_ts`) = %s""")
			get_data = (yesterday)

			cursor.execute(get_query,get_data)

			retailer_data = cursor.fetchall()

			for key,data in enumerate(retailer_data):	
				get_customer_count_query = ("""SELECT count(*) as customer_count
					FROM `admins` WHERE `organisation_id`= %s""")
				get_customer_count_data = (data['organisation_id'])
				customer_count = cursor.execute(get_customer_count_query,get_customer_count_data)

				customer_data = cursor.fetchone()

				retailer_data[key]['customer_count'] = customer_data['customer_count']

		if filterkey == 'last_7_days':
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_query = ("""SELECT *
				FROM `organisation_master` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
			get_data = (start_date,end_date)

			cursor.execute(get_query,get_data)

			retailer_data = cursor.fetchall()

			for key,data in enumerate(retailer_data):	
				get_customer_count_query = ("""SELECT count(*) as customer_count
					FROM `admins` WHERE `organisation_id`= %s""")
				get_customer_count_data = (data['organisation_id'])
				customer_count = cursor.execute(get_customer_count_query,get_customer_count_data)

				customer_data = cursor.fetchone()

				retailer_data[key]['customer_count'] = customer_data['customer_count']

		if filterkey == 'this_month':
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_query = ("""SELECT *
				FROM `organisation_master` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
			get_data = (start_date,end_date)

			cursor.execute(get_query,get_data)

			retailer_data = cursor.fetchall()

			for key,data in enumerate(retailer_data):	
				get_customer_count_query = ("""SELECT count(*) as customer_count
					FROM `admins` WHERE `organisation_id`= %s""")
				get_customer_count_data = (data['organisation_id'])
				customer_count = cursor.execute(get_customer_count_query,get_customer_count_data)

				customer_data = cursor.fetchone()

				retailer_data[key]['customer_count'] = customer_data['customer_count']

		if filterkey == 'lifetime':
			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_query = ("""SELECT *
				FROM `organisation_master` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
			get_data = (start_date,end_date)

			cursor.execute(get_query,get_data)

			retailer_data = cursor.fetchall()

			for key,data in enumerate(retailer_data):	
				get_customer_count_query = ("""SELECT count(*) as customer_count
					FROM `admins` WHERE `organisation_id`= %s""")
				get_customer_count_data = (data['organisation_id'])
				customer_count = cursor.execute(get_customer_count_query,get_customer_count_data)

				customer_data = cursor.fetchone()

				retailer_data[key]['customer_count'] = customer_data['customer_count']

		if filterkey == 'custom_date':			
			
			end_date = end_date
			
			start_date = start_date

			print(start_date)
			print(end_date)


			get_query = ("""SELECT *
				FROM `organisation_master` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
			get_data = (start_date,end_date)

			cursor.execute(get_query,get_data)

			retailer_data = cursor.fetchall()

			for key,data in enumerate(retailer_data):	
				get_customer_count_query = ("""SELECT count(*) as customer_count
					FROM `admins` WHERE `organisation_id`= %s""")
				get_customer_count_data = (data['organisation_id'])
				customer_count = cursor.execute(get_customer_count_query,get_customer_count_data)

				customer_data = cursor.fetchone()

				retailer_data[key]['customer_count'] = customer_data['customer_count']

		for key,data in enumerate(retailer_data):
			retailer_data[key]['date_of_lastlogin'] = str(data['date_of_lastlogin'])
			retailer_data[key]['last_update_ts'] = str(data['last_update_ts'])

				
		return ({"attributes": {
		    		"status_desc": "Retailer_details",
		    		"status": "success"
		    	},
		    	"responseList":retailer_data}), status.HTTP_200_OK
		
#-----------------------Get-Retailer-List---------------------#

#----------------------Get-Retailer-Count-List---------------------#

@name_space.route("/getRetailerCountList/<string:filterkey>/<string:start_date>/<string:end_date>")	
class getRetailerCountList(Resource):
	def get(self,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if filterkey == 'today':
			now = datetime.now()
			start_date = now.strftime("%Y-%m-%d")
			end_date = now.strftime("%Y-%m-%d")

			sdate = moment.date(start_date)   #start date			
			edate = moment.date(end_date)

			retailer_data = []

			for date in dates_bwn_twodates(sdate,edate):			
				get_query = ("""SELECT count(*) as retailer_count
					FROM `organisation_master` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (date)

				cursor.execute(get_query,get_data)

				retailer_count_data = cursor.fetchone()
				
				retailer_data.append({"date":date,"retailer_cout":retailer_count_data['retailer_count']})

		if filterkey == 'yesterday':
			
			today = datetime.now()

			start_date = today - timedelta(days = 1)
			end_date = start_date			

			sdate = moment.date(start_date)   #start date			
			edate = moment.date(end_date)

			retailer_data = []

			for date in dates_bwn_twodates(sdate,edate):			
				get_query = ("""SELECT count(*) as retailer_count
					FROM `organisation_master` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (date)

				cursor.execute(get_query,get_data)

				retailer_count_data = cursor.fetchone()
				
				retailer_data.append({"date":date,"retailer_cout":retailer_count_data['retailer_count']})

		if filterkey == 'last_7_days':
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = datetime.now()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			sdate = moment.date(start_date)   #start date			
			edate = moment.date(end_date)

			retailer_data = []

			for date in dates_bwn_twodates(sdate,edate):			
				get_query = ("""SELECT count(*) as retailer_count
					FROM `organisation_master` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (date)

				cursor.execute(get_query,get_data)

				retailer_count_data = cursor.fetchone()
				
				retailer_data.append({"date":date,"retailer_cout":retailer_count_data['retailer_count']})

		if filterkey == 'this_month':
			now = datetime.now()			
			day = '01'
			start_date = now.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			sdate = moment.date(start_date)   #start date			
			edate = moment.date(end_date)

			retailer_data = []

			for date in dates_bwn_twodates(sdate,edate):			
				get_query = ("""SELECT count(*) as retailer_count
					FROM `organisation_master` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (date)

				cursor.execute(get_query,get_data)

				retailer_count_data = cursor.fetchone()
				
				retailer_data.append({"date":date,"retailer_cout":retailer_count_data['retailer_count']})

		if filterkey == 'lifetime':
			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			sdate = moment.date(start_date)   #start date			
			edate = moment.date(end_date)

			retailer_data = []

			for date in dates_bwn_twodates(sdate,edate):			
				get_query = ("""SELECT count(*) as retailer_count
					FROM `organisation_master` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (date)

				cursor.execute(get_query,get_data)

				retailer_count_data = cursor.fetchone()
				
				retailer_data.append({"date":date,"retailer_cout":retailer_count_data['retailer_count']})

		if filterkey == 'custom_date':

			sdate = moment.date(start_date)   #start date
			print(sdate)
			edate = moment.date(end_date)

			retailer_data = []

			for date in dates_bwn_twodates(sdate,edate):			
				get_query = ("""SELECT count(*) as retailer_count
					FROM `organisation_master` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (date)

				cursor.execute(get_query,get_data)

				retailer_count_data = cursor.fetchone()
				
				retailer_data.append({"date":date,"retailer_cout":retailer_count_data['retailer_count']})

		return ({"attributes": {
		    		"status_desc": "Retailer_details",
		    		"status": "success"
		    	},
		    	"responseList":retailer_data}), status.HTTP_200_OK

#----------------------Get-Retailer-Count-List---------------------#

#----------------------Get-Retailer-with-cataloge-Count-List---------------------#

@name_space.route("/getRetailerWithCatalougeCountList/<string:retailer>/<string:filterkey>/<string:start_date>/<string:end_date>")	
class getRetailerWithCatalougeCountList(Resource):
	def get(self,retailer,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if retailer == 'all':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (today_date)

				cursor.execute(get_query,get_data)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) = %s  group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (today_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (yesterday)

				cursor.execute(get_query,get_data)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) = %s  group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) >= %s  and DATE(c.`last_update_ts`) <= %s group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				catalouge_data = cursor.fetchone()

				print(cursor._last_executed)

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) >= %s  and DATE(c.`last_update_ts`) <= %s group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) >= %s  and DATE(c.`last_update_ts`) <= %s group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) >= %s  and DATE(c.`last_update_ts`) <= %s group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""
		else:
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) = %s and `organisation_id` = %s""")
				get_data = (today_date,retailer)

				cursor.execute(get_query,get_data)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) = %s  group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (today_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) = %s and `organisation_id` = %s""")
				get_data = (yesterday,retailer)

				cursor.execute(get_query,get_data)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) = %s  group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) >= %s  and DATE(c.`last_update_ts`) <= %s group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) >= %s  and DATE(c.`last_update_ts`) <= %s group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) >= %s  and DATE(c.`last_update_ts`) <= %s group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as catalouge_count
					FROM `catalogs` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				catalouge_data = cursor.fetchone()

				catalouge_count = catalouge_data['catalouge_count']

				get_best_performing_query = ("""SELECT count(*) as catalouge_count,om.`organization_name`
												FROM `catalogs` c
												INNER JOIN `organisation_master` om on om.`organisation_id` = c.`organisation_id`
												WHERE DATE(c.`last_update_ts`) >= %s  and DATE(c.`last_update_ts`) <= %s group by c.`organisation_id` order by catalouge_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_catalouge_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""



		return ({"attributes": {
		    		"status_desc": "Retailer_catalouge_details",
		    		"status": "success",
		    		"best_performing_count":best_performing_count,
		    		"best_performing_organisation":best_performing_organisation
		    	},
		    	"responseList":catalouge_count}), status.HTTP_200_OK


#----------------------Get-Retailer-with-cataloge-Count-List---------------------#

#----------------------Get-Retailer-with-offer-Count-List---------------------#

@name_space.route("/getRetailerWithCatalougeOfferCountList/<string:retailer>/<string:filterkey>/<string:start_date>/<string:end_date>")	
class getRetailerWithCatalougeOfferCountList(Resource):
	def get(self,retailer,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if retailer == 'all':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (today_date)

				cursor.execute(get_query,get_data)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE DATE(o.`last_update_ts`) = %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (today_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (yesterday)

				cursor.execute(get_query,get_data)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE DATE(o.`last_update_ts`) = %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE  DATE(o.`last_update_ts`) >= %s and DATE(o.`last_update_ts`) <= %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE  DATE(o.`last_update_ts`) >= %s and DATE(o.`last_update_ts`) <= %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE  DATE(o.`last_update_ts`) >= %s and DATE(o.`last_update_ts`) <= %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE  DATE(o.`last_update_ts`) >= %s and DATE(o.`last_update_ts`) <= %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""
		else:
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) = %s and `organisation_id` = %s""")
				get_data = (today_date,retailer)

				cursor.execute(get_query,get_data)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE DATE(o.`last_update_ts`) = %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (today_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) = %s and `organisation_id` = %s""")
				get_data = (yesterday,retailer)

				cursor.execute(get_query,get_data)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE DATE(o.`last_update_ts`) = %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE  DATE(o.`last_update_ts`) >= %s and DATE(o.`last_update_ts`) <= %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE  DATE(o.`last_update_ts`) >= %s and DATE(o.`last_update_ts`) <= %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE  DATE(o.`last_update_ts`) >= %s and DATE(o.`last_update_ts`) <= %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as offer_count
					FROM `offer` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				offer_data = cursor.fetchone()

				offer_count = offer_data['offer_count']

				get_best_performing_query = ("""SELECT count(*) as offer_count,om.`organization_name`
												FROM `offer` o
												INNER JOIN `organisation_master` om on om.`organisation_id` = o.`organisation_id`
												WHERE  DATE(o.`last_update_ts`) >= %s and DATE(o.`last_update_ts`) <= %s  group by o.`organisation_id` order by offer_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_count = cursor.execute(get_best_performing_query,get_best_performing_data)

				if best_performig_offer_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""



		return ({"attributes": {
		    		"status_desc": "Retailer_offer_details",
		    		"status": "success",
		    		"best_performing_count":best_performing_count,
		    		"best_performing_organisation":best_performing_organisation
		    	},
		    	"responseList":offer_count}), status.HTTP_200_OK


#----------------------Get-Retailer-with-offer-Count-List---------------------#

#----------------------Get-Retailer-with-Notification-Count-List---------------------#

@name_space.route("/getRetailerWithNotificationCountList/<string:retailer>/<string:filterkey>/<string:start_date>/<string:end_date>")	
class getRetailerWithNotificationCountList(Resource):
	def get(self,retailer,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if retailer == 'all':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`Last_Update_TS`) = %s""")
				get_data = (today_date)

				cursor.execute(get_query,get_data)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) = %s  group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (today_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) = %s""")
				get_data = (yesterday)

				cursor.execute(get_query,get_data)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) = %s  group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) >= %s  and DATE(n.`last_update_ts`) <= %s group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) >= %s  and DATE(n.`last_update_ts`) <= %s group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) >= %s  and DATE(n.`last_update_ts`) <= %s group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) >= %s  and DATE(n.`last_update_ts`) <= %s group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""
		else:
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) = %s and `organisation_id` = %s""")
				get_data = (today_date,retailer)

				cursor.execute(get_query,get_data)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) = %s  group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (today_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) = %s and `organisation_id` = %s""")
				get_data = (yesterday,retailer)

				cursor.execute(get_query,get_data)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']


				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) = %s  group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) >= %s  and DATE(n.`last_update_ts`) <= %s group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) >= %s  and DATE(n.`last_update_ts`) <= %s group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) >= %s  and DATE(n.`last_update_ts`) <= %s group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as notification_count
					FROM `app_notification` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				print(cursor._last_executed)

				notification_data = cursor.fetchone()

				notification_count = notification_data['notification_count']

				get_best_performing_notification_query = ("""SELECT count(*) as notification_count,om.`organization_name`
												FROM `app_notification` n
												INNER JOIN `organisation_master` om on om.`organisation_id` = n.`organisation_id`
												WHERE DATE(n.`last_update_ts`) >= %s  and DATE(n.`last_update_ts`) <= %s group by n.`organisation_id` order by notification_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_notification_count = cursor.execute(get_best_performing_notification_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['notification_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""


		return ({"attributes": {
		    		"status_desc": "Retailer_notification_details",
		    		"status": "success",
		    		"best_performing_count":best_performing_count,
		    		"best_performing_organisation":best_performing_organisation
		    	},
		    	"responseList":notification_count}), status.HTTP_200_OK


#----------------------Get-Retailer-with-Notification-Count-List---------------------#

#----------------------Get-Retailer-with-catalouge-share-Count-List---------------------#

@name_space.route("/getRetailerWithCatalogueShareCountList/<string:retailer>/<string:filterkey>/<string:start_date>/<string:end_date>")	
class getRetailerWithCatalogueShareCountList(Resource):
	def get(self,retailer,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if retailer == 'all':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 2""")
				get_data = (today_date)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (today_date)

				best_performig_catalouge_shar_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_shar_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 2""")
				get_data = (yesterday)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 2""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 2""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 2""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 2""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

		else:
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 2 and `organisation_id` = %s""")
				get_data = (today_date,retailer)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (today_date)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 2 and `organisation_id` = %s""")
				get_data = (yesterday,retailer)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 2 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 2 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 2 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as catalouge_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 2 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				catalouge_share_data = cursor.fetchone()

				catalouge_share_count = catalouge_share_data['catalouge_share_count']

				get_best_performing_catalouge_share_query = ("""SELECT count(*) as catalouge_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 2 group by es.`organisation_id` order by catalouge_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_catalouge_share_count = cursor.execute(get_best_performing_catalouge_share_query,get_best_performing_data)

				if best_performig_catalouge_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['catalouge_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

		return ({"attributes": {
		    		"status_desc": "Retailer_catalouge_share_details",
		    		"status": "success",
		    		"best_performing_count":best_performing_count,
		    		"best_performing_organisation":best_performing_organisation
		    	},
		    	"responseList":catalouge_share_count}), status.HTTP_200_OK


#----------------------Get-Retailer-with-catalouge-share-Count-List---------------------#

#----------------------Get-Retailer-with-Offer-share-Count-List---------------------#

@name_space.route("/getRetailerWithOfferShareCountList/<string:retailer>/<string:filterkey>/<string:start_date>/<string:end_date>")	
class getRetailerWithOfferShareCountList(Resource):
	def get(self,retailer,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if retailer == 'all':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 1""")
				get_data = (today_date)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (today_date)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 1""")
				get_data = (yesterday)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 1""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 1""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_notification_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_notification_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 1""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 1""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

		else:
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 1 and `organisation_id` = %s""")
				get_data = (today_date,retailer)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (today_date)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 1 and `organisation_id` = %s""")
				get_data = (yesterday,retailer)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 1 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 1 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 1 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as offer_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 1 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				offer_share_data = cursor.fetchone()

				offer_share_count = offer_share_data['offer_share_count']

				get_best_performing_offer_share_query = ("""SELECT count(*) as offer_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 1 group by es.`organisation_id` order by offer_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_offer_share_count = cursor.execute(get_best_performing_offer_share_query,get_best_performing_data)

				if best_performig_offer_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['offer_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

		return ({"attributes": {
		    		"status_desc": "Retailer_offer_share_details",
		    		"status": "success",
		    		"best_performing_count":best_performing_count,
		    		"best_performing_organisation":best_performing_organisation
		    	},
		    	"responseList":offer_share_count}), status.HTTP_200_OK


#----------------------Get-Retailer-with-Offer-share-Count-List---------------------#

#----------------------Get-Retailer-with-app-share-Count-List---------------------#

@name_space.route("/getRetailerWithAppShareCountList/<string:retailer>/<string:filterkey>/<string:start_date>/<string:end_date>")	
class getRetailerWithAppShareCountList(Resource):
	def get(self,retailer,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if retailer == 'all':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 3""")
				get_data = (today_date)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (today_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 3""")
				get_data = (yesterday)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 3""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 3""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 3""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 3""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

		else:
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 3 and `organisation_id` = %s""")
				get_data = (today_date,retailer)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (today_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 3 and `organisation_id` = %s""")
				get_data = (yesterday,retailer)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 3 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 3 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 3 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as app_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 3 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				app_share_data = cursor.fetchone()

				app_share_count = app_share_data['app_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as app_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 3 group by es.`organisation_id` order by app_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['app_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

		return ({"attributes": {
		    		"status_desc": "Retailer_offer_share_details",
		    		"status": "success",
		    		"best_performing_count":best_performing_count,
		    		"best_performing_organisation":best_performing_organisation
		    	},
		    	"responseList":app_share_count}), status.HTTP_200_OK


#----------------------Get-Retailer-with-Offer-share-Count-List---------------------#

#----------------------Get-Retailer-with-web-share-Count-List---------------------#

@name_space.route("/getRetailerWithWebShareCountList/<string:retailer>/<string:filterkey>/<string:start_date>/<string:end_date>")	
class getRetailerWithWebShareCountList(Resource):
	def get(self,retailer,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if retailer == 'all':
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 4""")
				get_data = (today_date)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (today_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
			
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 4""")
				get_data = (yesterday)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_web_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_web_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 4""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_web_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_web_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 4""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_web_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_web_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 4""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_web_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_web_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 4""")
				get_data = (start_date,end_date)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and  DATE(es.`last_update_ts`) <= %s and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_web_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_web_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

		else:
			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 4 and `organisation_id` = %s""")
				get_data = (today_date,retailer)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (today_date)

				best_performig_web_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_web_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) = %s and `source_type` = 4 and `organisation_id` = %s""")
				get_data = (yesterday,retailer)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) = %s  and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (yesterday)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'last_7_days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = datetime.now()
				start_date = today - timedelta(days = 7)

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 4 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_web_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_web_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'this_month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 4 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 4 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_web_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_web_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

			if filterkey == 'custom_date':

				end_date = end_date			
				start_date = start_date

				print(start_date)
				print(end_date)

				get_query = ("""SELECT count(*) as web_share_count
					FROM `ecommerce_share` WHERE DATE(`last_update_ts`) >= %s and DATE(`last_update_ts`) <= %s and `source_type` = 4 and `organisation_id` = %s""")
				get_data = (start_date,end_date,retailer)

				cursor.execute(get_query,get_data)

				web_share_data = cursor.fetchone()

				web_share_count = web_share_data['web_share_count']

				get_best_performing_app_share_query = ("""SELECT count(*) as web_share_count,om.`organization_name`
												FROM `ecommerce_share` es
												INNER JOIN `organisation_master` om on om.`organisation_id` =es.`organisation_id`
												WHERE DATE(es.`last_update_ts`) >= %s and DATE(es.`last_update_ts`) <= %s  and es.`source_type` = 4 group by es.`organisation_id` order by web_share_count desc""")
				get_best_performing_data = (start_date,end_date)

				best_performig_app_share_count = cursor.execute(get_best_performing_app_share_query,get_best_performing_data)

				if best_performig_app_share_count > 0:

					best_performing_data = cursor.fetchone()

					best_performing_count = best_performing_data['web_share_count']
					best_performing_organisation = best_performing_data['organization_name']
				else:
					best_performing_count = 0
					best_performing_organisation = ""

		return ({"attributes": {
		    		"status_desc": "Retailer_offer_share_details",
		    		"status": "success",
		    		"best_performing_count":best_performing_count,
		    		"best_performing_organisation":best_performing_organisation
		    	},
		    	"responseList":web_share_count}), status.HTTP_200_OK


#----------------------Get-Retailer-with-web-share-Count-List---------------------#

def dates_bwn_twodates(start_date, end_date):
    diff = abs(start_date.diff(end_date).days)
    
    for n in range(0,diff+1):
        yield start_date.strftime("%Y-%m-%d")
        start_date = (start_date).add(days=1)






