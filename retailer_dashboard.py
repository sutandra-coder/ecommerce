from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import datetime
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

retailer_dashboard = Blueprint('retailer_dashboard', __name__)
api = Api(retailer_dashboard, version='1.0', title='Retailer API',
    description='Retailer API')

name_space = api.namespace('RetailerDashboard',description='Retailer Dashboard')

# BASE_URL = 'http://ec2-3-19-228-138.us-east-2.compute.amazonaws.com/flaskapp/'
BASE_URL = 'http://127.0.0.1:5000/'
#-----------------------------------------------------------------#
storeview_analytics = api.model('storeview_analytics', {
	"customer_id": fields.Integer(),
	"product_meta_id": fields.Integer(),
    "from_web_or_phone": fields.Integer(),
    "organisation_id": fields.Integer()
    })

offerview_analytics = api.model('offerview_analytics', {
	"customer_id": fields.Integer(),
	"offer_id": fields.Integer(),
    "from_web_or_phone": fields.Integer(),
    "organisation_id": fields.Integer()
    })

ordersettings = api.model('ordersettings', {
	"tax_rate": fields.Float(),
	"shipping_charges": fields.String(),
    "checkout_value": fields.Float(),
    "business_hour":fields.String(),
    "organisation_id": fields.Integer()
    })		

updateordersetting = api.model('updateordersetting', {
	"tax_rate": fields.Float(),
	"shipping_charges": fields.String(),
    "checkout_value": fields.Float(),
    "business_hour":fields.String(),
    "organisation_id": fields.Integer()
    })

paymentsettings = api.model('paymentsettings', {
	"accept_online": fields.String(),
	"direct_pament": fields.String(),
    "allow_cod": fields.String(),
    "payment_instructions":fields.String(),
    "asked_questions":fields.String(),
    "organisation_id": fields.Integer()
    })

updatepaymentsetting = api.model('updatepaymentsetting', {
	"accept_online": fields.String(),
	"direct_pament": fields.String(),
    "allow_cod": fields.String(),
    "payment_instructions":fields.String(),
    "asked_questions":fields.String(),
    "organisation_id": fields.Integer()
    })

appsettings = api.model('appsettings', {
	"language": fields.String(),
	"new_views_notifications": fields.String(),
    "new_msg_notifications": fields.String(),
    "long_notification_tone":fields.String(),
    "organisation_id": fields.Integer()
    })

updateappsetting = api.model('updateappsetting', {
	"language": fields.String(),
	"new_views_notifications": fields.String(),
    "new_msg_notifications": fields.String(),
    "long_notification_tone":fields.String(),
    "organisation_id": fields.Integer()
    })

#----------------------------------------------------#
@name_space.route("/RetailerDashboardDtlsByFilerKeyOrganization/<string:filterkey>/<int:organisation_id>")	
class RetailerDashboardDtls(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()

		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=%s""",(organisation_id,today))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=%s""",(organisation_id,today))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'yesterday':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0


			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'last 7 day':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		
		elif filterkey == 'this month':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		else:
			orders = 0
			sales = 0
			prodview = 0
			storeview = 0
			
		conn.commit()
		cur.close()
		connection.commit()
		cursor.close()

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

#--------------------------------------------------------------#


#----------------------------------------------------#
@name_space.route("/RetailerDashboardDtlsByFilerKeyOrganizationwithdaterange/<string:filterkey>/<int:organisation_id>/<string:start_date>/<string:end_date>")	
class RetailerDashboardDtlsByFilerKeyOrganizationwithdaterange(Resource):
	def get(self,filterkey,organisation_id,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()

		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=%s""",(organisation_id,today))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=%s""",(organisation_id,today))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'yesterday':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0


			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'last 7 day':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		
		elif filterkey == 'this month':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'custom date':
			if start_date != 'NA' and end_date != 'NA':			
				cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
					`order_product` WHERE `organisation_id`=%s and 
					date(`last_update_ts`) between %s and %s""",(organisation_id,start_date,end_date))

				orderdata = cursor.fetchone()
				if orderdata:
					orders = orderdata['total']
				else:
					orders = 0
				
				cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
					WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
					WHERE `organisation_id` = %s) and `status`='Completed' and 
					date(`last_update_ts`) between %s and %s""",(organisation_id,start_date,end_date))

				salesdata = cursor.fetchone()
				if salesdata['total'] !=None:
					sales = salesdata['total']
				else:
					sales = 0

				cur.execute("""SELECT count(`analytics_id`)as total FROM 
					`customer_product_analytics` WHERE `organisation_id`=%s 
					and date(`last_update_ts`) between %s and %s""",(organisation_id,start_date,end_date))

				prodviewdata = cur.fetchone()
				if prodviewdata:
					prodview = prodviewdata['total']
				else:
					prodview = 0

				cur.execute("""SELECT count(`analytics_id`)as total FROM 
					`customer_store_analytics` WHERE `organisation_id`=%s 
					and date(`last_update_ts`) between %s and %s""",(organisation_id,start_date,end_date))

				storeviewdata = cur.fetchone()
				if storeviewdata:
					storeview = storeviewdata['total']
				else:
					storeview = 0
			else:
				orders = 0
				sales = 0
				prodview = 0
				storeview = 0

		else:
			orders = 0
			sales = 0
			prodview = 0
			storeview = 0
			
		conn.commit()
		cur.close()
		connection.commit()
		cursor.close()

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

#--------------------------------------------------------------#


#----------------------------------------------------#
@name_space.route("/RetailerDashboardDtlsByFilerKeyOrganizationwithdaterangeweb/<string:filterkey>/<int:organisation_id>/<string:start_date>/<string:end_date>")	
class RetailerDashboardDtlsByFilerKeyOrganizationwithdaterangeweb(Resource):
	def get(self,filterkey,organisation_id,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()

		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=%s""",(organisation_id,today))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=%s""",(organisation_id,today))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'yesterday':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0


			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'last_7_day':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		
		elif filterkey == 'this_month':
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
				`order_product` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			orderdata = cursor.fetchone()
			if orderdata:
				orders = orderdata['total']
			else:
				orders = 0
			
			cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
				WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
				WHERE `organisation_id` = %s) and `status`='Completed' and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			salesdata = cursor.fetchone()
			if salesdata['total'] !=None:
				sales = salesdata['total']
			else:
				sales = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_product_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			prodviewdata = cur.fetchone()
			if prodviewdata:
				prodview = prodviewdata['total']
			else:
				prodview = 0

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			storeviewdata = cur.fetchone()
			if storeviewdata:
				storeview = storeviewdata['total']
			else:
				storeview = 0

		elif filterkey == 'custom_date':
			if start_date != 'NA' and end_date != 'NA':			
				cursor.execute("""SELECT count(`order_product_id`)as total  FROM 
					`order_product` WHERE `organisation_id`=%s and 
					date(`last_update_ts`) between %s and %s""",(organisation_id,start_date,end_date))

				orderdata = cursor.fetchone()
				if orderdata:
					orders = orderdata['total']
				else:
					orders = 0
				
				cursor.execute("""SELECT SUM(`amount`)as total FROM `instamojo_payment_request` 
					WHERE `transaction_id` in(SELECT `transaction_id` FROM `order_product` 
					WHERE `organisation_id` = %s) and `status`='Completed' and 
					date(`last_update_ts`) between %s and %s""",(organisation_id,start_date,end_date))

				salesdata = cursor.fetchone()
				if salesdata['total'] !=None:
					sales = salesdata['total']
				else:
					sales = 0

				cur.execute("""SELECT count(`analytics_id`)as total FROM 
					`customer_product_analytics` WHERE `organisation_id`=%s 
					and date(`last_update_ts`) between %s and %s""",(organisation_id,start_date,end_date))

				prodviewdata = cur.fetchone()
				if prodviewdata:
					prodview = prodviewdata['total']
				else:
					prodview = 0

				cur.execute("""SELECT count(`analytics_id`)as total FROM 
					`customer_store_analytics` WHERE `organisation_id`=%s 
					and date(`last_update_ts`) between %s and %s""",(organisation_id,start_date,end_date))

				storeviewdata = cur.fetchone()
				if storeviewdata:
					storeview = storeviewdata['total']
				else:
					storeview = 0
			else:
				orders = 0
				sales = 0
				prodview = 0
				storeview = 0

		else:
			orders = 0
			sales = 0
			prodview = 0
			storeview = 0
			
		conn.commit()
		cur.close()
		connection.commit()
		cursor.close()

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

#--------------------------------------------------------------#



@name_space.route("/ContentDtlsByOrganization/<int:organisation_id>")	
class ContentDtlsByOrganization(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `retailer_content_library` WHERE 
			`organization_id`=%s""",(organisation_id))

		contentdtls = cursor.fetchall()
		if contentdtls:
			for i in range(len(contentdtls)):
				contentdtls[i]['last_update_ts'] = contentdtls[i]['last_update_ts'].isoformat()
		else:
			contentdtls = []
			
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Content Details",
		    		"status": "success"
		    	},
		    	"responseList":contentdtls}), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/AddStoreViewDetails")
class AddStoreViewDetails(Resource):
	@api.expect(storeview_analytics)
	def post(self):
		conn = ecommerce_analytics()
		cur = conn.cursor()

		details = request.get_json()
		today = date.today()

		customer_id = details.get('customer_id')
		product_meta_id = details.get('product_meta_id')
		from_web_or_phone = details.get('from_web_or_phone')
		organisation_id = details.get('organisation_id')
		

		storeviewquery = ("""INSERT INTO `customer_store_analytics`(`customer_id`, 
			`product_meta_id`, `from_web_or_phone`, `organisation_id`) VALUES (%s,
			%s,%s,%s)""")
		storeviewdata = cur.execute(storeviewquery,(customer_id,product_meta_id,
			from_web_or_phone,organisation_id))

		storeview_id = cur.lastrowid
		details['storeview_id'] = storeview_id

		conn.commit()
		cur.close()

		return ({"attributes": {"status_desc": "Store View Details",
                                "status": "success"
	                            },
	            "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/AddOfferViewDetails")
class AddOfferViewDetails(Resource):
	@api.expect(offerview_analytics)
	def post(self):
		conn = ecommerce_analytics()
		cur = conn.cursor()

		details = request.get_json()
		today = date.today()

		customer_id = details.get('customer_id')
		offer_id = details.get('offer_id')
		from_web_or_phone = details.get('from_web_or_phone')
		organisation_id = details.get('organisation_id')
		

		offerviewquery = ("""INSERT INTO `customer_offer_analytics`(`customer_id`,
			`offer_id`, `from_web_or_phone`, `organisation_id`) VALUES (%s,
			%s,%s,%s)""")
		offerviewdata = cur.execute(offerviewquery,(customer_id,offer_id,
			from_web_or_phone,organisation_id))

		offerview_id = cur.lastrowid
		details['offerview_id'] = offerview_id

		conn.commit()
		cur.close()

		return ({"attributes": {"status_desc": "Offer View Details",
                                "status": "success"
	                            },
	            "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------------#



#--------------------------------------------------------------#
@name_space.route("/CategoryDtlsByOrganisationId/<int:organisation_id>")	
class CategoryDtlsByOrganisationId(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_category_query = ("""SELECT *
				FROM `category`
				WHERE `organisation_id` = %s""")	
		get_category_data = (organisation_id)
		cursor.execute(get_category_query,get_category_data)
		categorydtls = cursor.fetchall()

		if categorydtls:
			for i in range(len(categorydtls)):
				categorydtls[i]['last_update_ts'] = categorydtls[i]['last_update_ts'].isoformat()

				get_product_query = ("""SELECT count(*) as product_count
					FROM `product` p 
					INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
					WHERE pom.`organisation_id` = %s and p.`category_id` = %s""")
				get_product_data = (organisation_id,categorydtls[i]['category_id'])
				count_product_data = cursor.execute(get_product_query,get_product_data)

				if count_product_data > 0:
					product_data = cursor.fetchone()					
					categorydtls[i]['no_of_product'] = product_data['product_count']
				else:
					categorydtls[i]['no_of_product'] = 0

				get_product_meta_query = ("""SELECT count(*) as product_meta_count
					FROM `product` p 
					INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
					INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
					WHERE pom.`organisation_id` = %s and p.`category_id` = %s""")
				get_product_meta_data = (organisation_id,categorydtls[i]['category_id'])
				count_product_meta_data = cursor.execute(get_product_meta_query,get_product_meta_data)

				if count_product_meta_data > 0:
					product_meta_data = cursor.fetchone()					
					categorydtls[i]['no_of_productvariant'] = product_meta_data['product_meta_count']
				else:
					categorydtls[i]['no_of_productvariant'] = 0
		else:
			categorydtls[i]['no_of_product'] = 0
			categorydtls[i]['no_of_productvariant'] = 0

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Category Details",
		    		"status": "success"
		    	},
		    	"responseList":categorydtls}), status.HTTP_200_OK

#------------------------------------------------------------------#
@name_space.route("/AddOrderSettingsDetails")
class AddOrderSettingsDetails(Resource):
	@api.expect(ordersettings)
	def post(self):
		conn = mysql_connection()
		cur = conn.cursor()

		details = request.get_json()
		today = date.today()

		tax_rate = details.get('tax_rate')
		shipping_charges = details.get('shipping_charges')
		checkout_value = details.get('checkout_value')
		business_hour = details.get('business_hour')
		organisation_id = details.get('organisation_id')
		
		cur.execute("""SELECT `ordersetting_id`,`tax_rate`,`shipping_charges`,
			`checkout_value`,`business_hour`,`organisation_id` FROM `order_settings` 
			WHERE `organisation_id`=%s""",(organisation_id))

		settingsdtls = cur.fetchone()

		if settingsdtls:
			details = settingsdtls
		else:
			settingquery = ("""INSERT INTO `order_settings`(`tax_rate`, 
				`shipping_charges`, `checkout_value`, `business_hour`,`organisation_id`) 
				VALUES (%s,%s,%s,%s,%s)""")
			settingdata = cur.execute(settingquery,(tax_rate,shipping_charges,
				checkout_value,business_hour,organisation_id))

			ordersetting_id = cur.lastrowid
			details['ordersetting_id'] = ordersetting_id

		conn.commit()
		cur.close()

		return ({"attributes": {"status_desc": "Order Settingsdtls Details",
                                "status": "success"
	                            },
	            "responseList": details}), status.HTTP_200_OK

#-------------------------------------------------------------#
@name_space.route("/OrderSettingsDtlsByOrganizationId/<int:organisation_id>")	
class OrderSettingsDtlsByOrganizationId(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `order_settings` WHERE 
			`organisation_id`=%s""",(organisation_id))

		settingsdtls = cursor.fetchone()
		if settingsdtls:
			settingsdtls['last_update_ts'] = settingsdtls['last_update_ts'].isoformat()
		else:
			settingsdtls = {}
			
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Order Settingsdtls Details",
		    		"status": "success"
		    	},
		    	"responseList":settingsdtls}), status.HTTP_200_OK

#-----------------------------------------------------------#
@name_space.route("/UpdateOrderSettingsDtlsByOrganizationId")
class UpdateOrderSettingsDtlsByOrganizationId(Resource):
	@api.expect(updateordersetting)
	def put(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		Tax_rate = details.get('tax_rate')
		Shipping_charges = details.get('shipping_charges')
		Checkout_value = details.get('checkout_value')
		Business_hour = details.get('business_hour')
		organisation_id = details.get('organisation_id')

		cursor.execute("""SELECT * FROM `order_settings` WHERE 
			`organisation_id`=%s""",(organisation_id))
		ordersettingDtls = cursor.fetchone()
		
		if ordersettingDtls:
			if not Tax_rate:
				Tax_rate = ordersettingDtls.get('tax_rate')

			if not Shipping_charges:
				Shipping_charges = ordersettingDtls.get('shipping_charges')

			if not Checkout_value:
				Checkout_value = ordersettingDtls.get('checkout_value')

			if not Business_hour:
				Business_hour = ordersettingDtls.get('business_hour')

			
			updatesetDtls = ("""UPDATE `order_settings` SET `tax_rate`=%s,
				`shipping_charges`=%s,`checkout_value`=%s,`business_hour`=%s WHERE 
				organisation_id= %s""")
			updatesetdata = cursor.execute(updatesetDtls,(Tax_rate,
				Shipping_charges,Checkout_value,Business_hour,organisation_id))
			if updatesetdata:
				msg = "Successfully Updated"

			else:
				msg = "Not Updated"

		else:
			msg = "User Not Exists"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Order Settings Details",
                                "status": "success",
                                "msg": msg
                                },
	            "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/AddPaymentSettingsDetails")
class AddPaymentSettingsDetails(Resource):
	@api.expect(paymentsettings)
	def post(self):
		conn = mysql_connection()
		cur = conn.cursor()

		details = request.get_json()
		today = date.today()

		accept_online = details.get('accept_online')
		direct_pament = details.get('direct_pament')
		allow_cod = details.get('allow_cod')
		payment_instructions = details.get('payment_instructions')
		asked_questions = details.get('asked_questions')
		organisation_id = details.get('organisation_id')
		
		cur.execute("""SELECT `paymentsetting_id`,`accept_online`,`direct_pament`,
			`allow_cod`,`payment_instructions`,`asked_questions`,`organisation_id` 
			FROM `payment_settings` WHERE `organisation_id`=%s""",(organisation_id))

		settingsdtls = cur.fetchone()

		if settingsdtls:
			details = settingsdtls
		else:
			settingquery = ("""INSERT INTO `payment_settings`(`accept_online`,
				`direct_pament`,`allow_cod`,`payment_instructions`,`asked_questions`,
				`organisation_id`) VALUES (%s,%s,%s,%s,%s,%s)""")
			settingdata = cur.execute(settingquery,(accept_online,direct_pament,
				allow_cod,payment_instructions,asked_questions,organisation_id))

			ordersetting_id = cur.lastrowid
			details['ordersetting_id'] = ordersetting_id

		conn.commit()
		cur.close()

		return ({"attributes": {"status_desc": "Payment Settingsdtls Details",
                                "status": "success"
	                            },
	            "responseList": details}), status.HTTP_200_OK

#-------------------------------------------------------------#
@name_space.route("/PaymentSettingsDtlsByOrganizationId/<int:organisation_id>")	
class PaymentSettingsDtlsByOrganizationId(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `payment_settings` WHERE 
			`organisation_id`=%s""",(organisation_id))

		settingsdtls = cursor.fetchone()
		if settingsdtls:
			settingsdtls['last_update_ts'] = settingsdtls['last_update_ts'].isoformat()
		else:
			settingsdtls = {}
			
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Payment Settingsdtls Details",
		    		"status": "success"
		    	},
		    	"responseList":settingsdtls}), status.HTTP_200_OK

#-----------------------------------------------------------#
@name_space.route("/UpdatePaymentSettingsDtlsByOrganizationId")
class UpdatePaymentSettingsDtlsByOrganizationId(Resource):
	@api.expect(updatepaymentsetting)
	def put(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		Accept_online = details.get('accept_online')
		Direct_pament = details.get('direct_pament')
		Allow_cod = details.get('allow_cod')
		Payment_instructions = details.get('payment_instructions')
		Asked_questions = details.get('asked_questions')
		organisation_id = details.get('organisation_id')

		cursor.execute("""SELECT * FROM `payment_settings` WHERE 
			`organisation_id`=%s""",(organisation_id))
		ordersettingDtls = cursor.fetchone()
		
		if ordersettingDtls:
			if not Accept_online:
				Accept_online = ordersettingDtls.get('accept_online')

			if not Direct_pament:
				Direct_pament = ordersettingDtls.get('direct_pament')

			if not Allow_cod:
				Allow_cod = ordersettingDtls.get('allow_cod')

			if not Payment_instructions:
				Payment_instructions = ordersettingDtls.get('payment_instructions')

			if not Asked_questions:
				Asked_questions = ordersettingDtls.get('asked_questions')

			
			updatesetDtls = ("""UPDATE `payment_settings` SET `accept_online`=%s,
				`direct_pament`=%s,`allow_cod`=%s,`payment_instructions`=%s,
				`asked_questions`=%s WHERE organisation_id= %s""")
			updatesetdata = cursor.execute(updatesetDtls,(Accept_online,
				Direct_pament,Allow_cod,Payment_instructions,Asked_questions,organisation_id))
			if updatesetdata:
				msg = "Successfully Updated"

			else:
				msg = "Not Updated"

		else:
			msg = "User Not Exists"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Order Settings Details",
                                "status": "success",
                                "msg": msg
                                },
	            "responseList": details}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/AddAppSettingsDetails")
class AddAppSettingsDetails(Resource):
	@api.expect(appsettings)
	def post(self):
		conn = mysql_connection()
		cur = conn.cursor()
		details = request.get_json()

		language = details.get('language')
		new_views_notifications = details.get('new_views_notifications')
		new_msg_notifications = details.get('new_msg_notifications')
		long_notification_tone = details.get('long_notification_tone')
		organisation_id = details.get('organisation_id')
		
		cur.execute("""SELECT `appsetting_id`,`language`,`new_views_notifications`,
			`new_msg_notifications`,`long_notification_tone`,`organisation_id` FROM 
			`app_settings` WHERE `organisation_id`=%s""",(organisation_id))

		settingsdtls = cur.fetchone()

		if settingsdtls:
			details = settingsdtls
		else:
			settingquery = ("""INSERT INTO `app_settings`(`language`,
				`new_views_notifications`,`new_msg_notifications`,
				`long_notification_tone`,`organisation_id`) VALUES (%s,%s,%s,%s,%s)""")
			settingdata = cur.execute(settingquery,(language,new_views_notifications,
				new_msg_notifications,long_notification_tone,organisation_id))

			appsetting_id = cur.lastrowid
			details['appsetting_id'] = appsetting_id

		conn.commit()
		cur.close()

		return ({"attributes": {"status_desc": "App Settingsdtls Details",
                                "status": "success"
	                            },
	            "responseList": details}), status.HTTP_200_OK

#-------------------------------------------------------------#
@name_space.route("/AppSettingsDtlsByOrganizationId/<int:organisation_id>")	
class AppSettingsDtlsByOrganizationId(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `app_settings` WHERE 
			`organisation_id`=%s""",(organisation_id))

		settingsdtls = cursor.fetchone()
		if settingsdtls:
			settingsdtls['last_update_ts'] = settingsdtls['last_update_ts'].isoformat()
		else:
			settingsdtls = {}
			
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "App Settingsdtls Details",
		    		"status": "success"
		    	},
		    	"responseList":settingsdtls}), status.HTTP_200_OK

#-----------------------------------------------------------#
@name_space.route("/UpdateAppSettingsDtlsByOrganizationId")
class UpdateAppSettingsDtlsByOrganizationId(Resource):
	@api.expect(updateappsetting)
	def put(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		Language = details.get('language')
		New_views_notifications = details.get('new_views_notifications')
		New_msg_notifications = details.get('new_msg_notifications')
		Long_notification_tone = details.get('long_notification_tone')
		organisation_id = details.get('organisation_id')

		cursor.execute("""SELECT * FROM `app_settings` WHERE 
			`organisation_id`=%s""",(organisation_id))
		ordersettingDtls = cursor.fetchone()
		
		if ordersettingDtls:
			if not Language:
				Language = ordersettingDtls.get('language')

			if not New_views_notifications:
				New_views_notifications = ordersettingDtls.get('new_views_notifications')

			if not New_msg_notifications:
				New_msg_notifications = ordersettingDtls.get('new_msg_notifications')

			if not Long_notification_tone:
				Long_notification_tone = ordersettingDtls.get('long_notification_tone')

			
			updatesetDtls = ("""UPDATE `app_settings` SET `language`=%s,
				`new_views_notifications`=%s,`new_msg_notifications`=%s,
				`long_notification_tone`=%s WHERE organisation_id= %s""")
			updatesetdata = cursor.execute(updatesetDtls,(Language,
				New_views_notifications,New_msg_notifications,Long_notification_tone,organisation_id))
			if updatesetdata:
				msg = "Successfully Updated"

			else:
				msg = "Not Updated"

		else:
			msg = "User Not Exists"

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "App Settings Details",
                                "status": "success",
                                "msg": msg
                                },
	            "responseList": details}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/PrivacyPolicyDtlsByOrganizationId/<int:organisation_id>")	
class PrivacyPolicyDtlsByOrganizationId(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `retailer_privacypolicy` WHERE 
			`organisation_id`=%s""",(organisation_id))

		policydtls = cursor.fetchone()
		if policydtls:
			policydtls['last_update_ts'] = policydtls['last_update_ts'].isoformat()
		else:
			policydtls = {}
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Privacy Policy Details",
		    		"status": "success"
		    	},
		    	"responseList":policydtls}), status.HTTP_200_OK

#-------------------------------------------------------------#
@name_space.route("/DeleteOfferSectionMapping/<int:section_id>/<int:offer_id>/<int:organisation_id>")
class DeleteOfferSectionMapping(Resource):
    def delete(self,section_id,offer_id,organisation_id):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        delete_query = ("""DELETE FROM `offer_section_mapping` 
        	WHERE `section_id`=%s and `offer_id`=%s and `organisation_id`=%s""")
        cursor.execute(delete_query,(section_id,offer_id,organisation_id))
        
        connection.commit()
        cursor.close()
        
        return ({"attributes": {"status_desc": "Delete Offer Section Mapping",
                                "status": "success"},
                "responseList": 'Deleted Successfully'}), status.HTTP_200_OK


#-------------------------------------------------------------------------------#
@name_space.route("/DeleteProductCatalogMapping/<int:catalog_id>/<int:product_id>/<int:organisation_id>")
class DeleteProductCatalogMapping(Resource):
    def delete(self,catalog_id,product_id,organisation_id):
        connection = mysql_connection()
        cursor = connection.cursor()
        
        delete_query = ("""DELETE FROM `product_catalog_mapping` WHERE 
        	`catalog_id`=%s and `product_id`=%s and `organisation_id`=%s""")
        cursor.execute(delete_query,(catalog_id,product_id,organisation_id))
        
        connection.commit()
        cursor.close()
        
        return ({"attributes": {"status_desc": "Delete Product Catalog Mapping",
                                "status": "success"},
                "responseList": 'Deleted Successfully'}), status.HTTP_200_OK


#-------------------------------------------------------------------------------#
@name_space.route("/RemoveCatalogByCatalogIdOrganizationId/<int:catalog_id>/<int:organisation_id>")
class RemoveCatalogByCatalogIdOrganizationId(Resource):
	@api.expect()
	def put(self,catalog_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		updateDtls = (""" UPDATE `catalogs` SET `status`=0 WHERE 
			`catalog_id`=%s and `organisation_id`=%s""")
		updatedata = cursor.execute(updateDtls,(catalog_id,organisation_id))
		if updatedata:
			msg = "Successfully Removed"

		else:
			msg = "Not Removed"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Catalog Details",
                                "status": "success"
                                },
	            "responseList": msg}), status.HTTP_200_OK

#-------------------------------------------------------------------------------#
@name_space.route("/RemoveOfferSectionBySectionIdOrganizationId/<int:section_id>/<int:organisation_id>")
class RemoveOfferSectionBySectionIdOrganizationId(Resource):
	@api.expect()
	def put(self,section_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		updateDtls = (""" UPDATE `section_master` SET `status`=0 WHERE 
			`section_id`=%s and `organisation_id`=%s""")
		updatedata = cursor.execute(updateDtls,(section_id,organisation_id))
		if updatedata:
			msg = "Successfully Removed"

		else:
			msg = "Not Removed"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Offer Section Details",
                                "status": "success"
                                },
	            "responseList": msg}), status.HTTP_200_OK

#------------------------------------------------------------#
@name_space.route("/RemoveOfferByOfferIdOrganizationId/<int:offer_id>/<int:organisation_id>")
class RemoveOfferByOfferIdOrganizationId(Resource):
	@api.expect()
	def put(self,offer_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		updateDtls = (""" UPDATE `offer` SET `status`=0 WHERE 
			`offer_id`=%s and `organisation_id`=%s""")
		updatedata = cursor.execute(updateDtls,(offer_id,organisation_id))
		if updatedata:
			msg = "Successfully Removed"

		else:
			msg = "Not Removed"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Offer Details",
                                "status": "success"
                                },
	            "responseList": msg}), status.HTTP_200_OK

#---------------------------------------------------------------#
