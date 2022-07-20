from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
#import datetime
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

ret_customerdtls = Blueprint('ret_customerdtls', __name__)
api = Api(ret_customerdtls, version='1.0', title='Retailer API',
    description='Retailer API')

name_space = api.namespace('RetailerDashboard',description='Retailer Dashboard')


#-----------------------------------------------------------------#

@name_space.route("/RegisteredRetailerCustomerDtlsByFilerKeyOrganization/<string:filterkey>/<int:organisation_id>")	
class RegisteredRetailerCustomerDtlsByFilerKeyOrganization(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()

		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s""",(organisation_id,today))

			regdata = cursor.fetchone()
			if regdata:
				reg = regdata['total']
			else:
				reg = 0
			
			cursor.execute("""SELECT count(`U_id`)as total FROM `app_notification` 
				WHERE `organisation_id`=%s and date(`Last_Update_TS`)=%s""",(organisation_id,today))

			notifydata = cursor.fetchone()
			if notifydata['total'] !=None:
				sendnotification = notifydata['total']
			else:
				sendnotification = 0

			cur.execute("""SELECT count(distinct(`customer_id`))as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			visitordata = cur.fetchone()
			if visitordata:
				uniquevisitor = visitordata['total']
			else:
				uniquevisitor = 0

			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s""",(organisation_id,today))

			registereddata = cursor.fetchone()
			if registereddata:
				registereduser = registereddata['total']
				if uniquevisitor > registereduser:
					repeatedvisitor = uniquevisitor - registereduser
				else:
					repeatedvisitor = registereduser - uniquevisitor
			else:
				repeatedvisitor = 0

			cur.execute("""SELECT count(`customer_id`)as total FROM 
				`customer_store_analytics` WHERE `customer_id`=0 and 
				`organisation_id`=%s and date(`last_update_ts`)=%s""",(organisation_id,today))

			unregistereddata = cur.fetchone()
			if unregistereddata:
				unregistered = unregistereddata['total']
			else:
				unregistered = 0

		elif filterkey == 'yesterday':
			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			regdata = cursor.fetchone()
			if regdata:
				reg = regdata['total']
			else:
				reg = 0
			
			cursor.execute("""SELECT count(`U_id`)as total FROM `app_notification` 
				WHERE `organisation_id`=%s and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			notifydata = cursor.fetchone()
			if notifydata['total'] !=None:
				sendnotification = notifydata['total']
			else:
				sendnotification = 0

			cur.execute("""SELECT count(distinct(`customer_id`))as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			visitordata = cur.fetchone()
			if visitordata:
				uniquevisitor = visitordata['total']
			else:
				uniquevisitor = 0

			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			registereddata = cursor.fetchone()
			if registereddata:
				registereduser = registereddata['total']

				if uniquevisitor > registereduser:
					repeatedvisitor = uniquevisitor - registereduser
				else:
					repeatedvisitor = registereduser - uniquevisitor
			else:
				repeatedvisitor = 0

			cur.execute("""SELECT count(`customer_id`)as total FROM 
				`customer_store_analytics` WHERE `customer_id`=0 and 
				`organisation_id`=%s and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			unregistereddata = cur.fetchone()
			if unregistereddata:
				unregistered = unregistereddata['total']
			else:
				unregistered = 0

		elif filterkey == 'last 7 days':
			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`date_of_creation`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			regdata = cursor.fetchone()
			if regdata:
				reg = regdata['total']
			else:
				reg = 0
						
			cursor.execute("""SELECT count(`U_id`)as total FROM `app_notification` 
				WHERE `organisation_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			notifydata = cursor.fetchone()
			if notifydata['total'] !=None:
				sendnotification = notifydata['total']
			else:
				sendnotification = 0

			cur.execute("""SELECT count(distinct(`customer_id`))as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			visitordata = cur.fetchone()
			if visitordata:
				uniquevisitor = visitordata['total']
			else:
				uniquevisitor = 0

			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`date_of_creation`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			registereddata = cursor.fetchone()
			if registereddata:
				registereduser = registereddata['total']
				if uniquevisitor > registereduser:
					repeatedvisitor = uniquevisitor - registereduser
				else:
					repeatedvisitor = registereduser - uniquevisitor
			else:
				repeatedvisitor = 0

			cur.execute("""SELECT count(`customer_id`)as total FROM 
				`customer_store_analytics` WHERE `customer_id`=0 and 
				`organisation_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			unregistereddata = cur.fetchone()
			if unregistereddata:
				unregistered = unregistereddata['total']
			else:
				unregistered = 0

		elif filterkey == 'this month':
			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`) between %s and %s""",(organisation_id,stday,today))

			regdata = cursor.fetchone()
			if regdata:
				reg = regdata['total']
			else:
				reg = 0
			
			cursor.execute("""SELECT count(`U_id`)as total FROM `app_notification` 
				WHERE `organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			notifydata = cursor.fetchone()
			if notifydata['total'] !=None:
				sendnotification = notifydata['total']
			else:
				sendnotification = 0

			cur.execute("""SELECT count(distinct(`customer_id`))as total FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			visitordata = cur.fetchone()
			if visitordata:
				uniquevisitor = visitordata['total']
			else:
				uniquevisitor = 0

			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`) between %s and %s""",(organisation_id,stday,today))

			registereddata = cursor.fetchone()
			if registereddata:
				registereduser = registereddata['total']
				if uniquevisitor > registereduser:
					repeatedvisitor = uniquevisitor - registereduser
				else:
					repeatedvisitor = registereduser - uniquevisitor
			else:
				repeatedvisitor = 0


			cur.execute("""SELECT count(`customer_id`)as total FROM 
				`customer_store_analytics` WHERE `customer_id`=0 and 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			unregistereddata = cur.fetchone()
			if unregistereddata:
				unregistered = unregistereddata['total']
			else:
				unregistered = 0

		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			
			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`) between %s and %s""",(organisation_id,slifetime,today))

			regdata = cursor.fetchone()
			if regdata:
				reg = regdata['total']
			else:
				reg = 0
			
			cursor.execute("""SELECT count(`U_id`)as total FROM `app_notification` 
				WHERE `organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			notifydata = cursor.fetchone()
			if notifydata['total'] !=None:
				sendnotification = notifydata['total']
			else:
				sendnotification = 0

			cur.execute("""SELECT count(distinct(`customer_id`))as total FROM 
				`customer_store_analytics` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			visitordata = cur.fetchone()
			if visitordata:
				uniquevisitor = visitordata['total']
			else:
				uniquevisitor = 0

			cursor.execute("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`) between %s and %s""",(organisation_id,slifetime,today))

			registereddata = cursor.fetchone()
			if registereddata:
				registereduser = registereddata['total']
				if uniquevisitor > registereduser:
					repeatedvisitor = uniquevisitor - registereduser
				else:
					repeatedvisitor = registereduser - uniquevisitor
			else:
				repeatedvisitor = 0

			cur.execute("""SELECT count(`customer_id`)as total FROM 
				`customer_store_analytics` WHERE `customer_id`=0 and 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			unregistereddata = cur.fetchone()
			if unregistereddata:
				unregistered = unregistereddata['total']
			else:
				unregistered = 0

		else:
			reg = 0
			sendnotification = 0
			uniquevisitor = 0
			repeatedvisitor = 0
			unregistered = 0
			
		conn.commit()
		cur.close()
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Retailer Dashborad Details",
		    		"status": "success"
		    	},
		    	"responseList":{
		    					 "registration":reg,
		    					 "sendnotification": sendnotification,
		    					 "uniquevisitor":uniquevisitor,
		    					 "repeatedvisitor":repeatedvisitor,
		    					 "unregisteredvisitor": unregistered
						    	}
						    	}), status.HTTP_200_OK

#-----------------------------------------------------------------#

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#

@name_space.route("/CustomerCountWithOrganisationAndRetailStore/<string:filterkey>/<int:organisation_id>")	
class CustomerCountWithOrganisationAndRetailStore(Resource):
	def get(self,filterkey,organisation_id):
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

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,today_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(DISTINCT(`U_id`))as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) = %s """)
			get_notify_customer_data = (organisation_id,today_date)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

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
				get_customer_retailer_query = ("""SELECT  count(DISTINCT(`U_id`))as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and `destination_type` = 2 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0



			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`)=%s""")
			get_loged_In_customer_data = (organisation_id,today_date)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''

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


			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) = %s""")		
			get_demo_given_customer_data = (organisation_id,today_date)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

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
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:

					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0



			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,today_date)

			#get_registed_login_customer_query = ("""SELECT count(distict(`customer_id`))as total FROM `customer_store_analytics` 
				#WHERE `organisation_id`=%s and date(`last_update_ts`)=%s""")
			#get_registerd_login_customer_data = (organisation_id,today_date)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,today_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0
						

		if filterkey == 'yesterday':
			
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,yesterday)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(DISTINCT(`U_id`))as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) = %s """)
			get_notify_customer_data = (organisation_id,yesterday)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

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
				get_customer_retailer_query = ("""SELECT count(DISTINCT(`U_id`))as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and `destination_type` = 2 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0



			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`)=%s""")
			get_loged_In_customer_data = (organisation_id,yesterday)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''

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
								

			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) = %s""")		
			get_demo_given_customer_data = (organisation_id,yesterday)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

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
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0


			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,yesterday)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,yesterday)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0			

		if filterkey == 'last 7 days':
			
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(DISTINCT(`U_id`))as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date)

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
				get_customer_retailer_query = ("""SELECT count(DISTINCT(`U_id`))as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and a.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`) >= %s and date(a.`Last_Update_TS`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0



			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
			get_loged_In_customer_data = (organisation_id,start_date,end_date)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''

			get_loggedin_user_query = ("""SELECT count(distinct(`customer_id`)) as total_user FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0 """)
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


			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

			if count_demo_given_customer > 0:
				print(cursor._last_executed)
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
				get_customer_retailer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 
					FROM `customer_remarks` cr 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >=%s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0


			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				print(cursor._last_executed)
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0


		if filterkey == 'this month':
			
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(distinct(`U_id`))as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				print(cursor._last_executed)
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
				get_customer_retailer_query = ("""SELECT count(distinct(`U_id`))as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and `destination_type` = 2 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`) >= %s and date(a.`Last_Update_TS`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0



			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
			get_loged_In_customer_data = (organisation_id,start_date,end_date)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''


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
					loggedin_data['store_data'][nrlkey]['customer_count'] = 0
					'''get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
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
						loggedin_data['store_data'][nrlkey]['customer_count'] = 0'''


			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

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
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >=%s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0

			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				print(cursor._last_executed)
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0
		
		if filterkey == 'lifetime':

			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(distinct(`U_id`))as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				print(cursor._last_executed)
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
				get_customer_retailer_query = ("""SELECT count(distinct(`U_id`))as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and a.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`) >= %s and date(a.`Last_Update_TS`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0



			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
			get_loged_In_customer_data = (organisation_id,start_date,end_date)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''

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
					loggedin_data['store_data'][nrlkey]['customer_count'] = 0
					'''get_store_analytics_view_query = ("""SELECT distinct(`customer_id`) FROM `customer_store_analytics` where date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s and `organisation_id` = %s and `customer_id`!= 0""")
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
						loggedin_data['store_data'][nrlkey]['customer_count'] = 0'''

			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

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
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >=%s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0	


			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				print(cursor._last_executed)
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0	

		return ({"attributes": {
		    		"status_desc": "Customer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{"registation_data":registation_data,"notification_data":notification_data,"loggedin_data":loggedin_data,"demo_data":demo_data,"total_login_user_from_registration_data":total_login_user_from_registration_data,"total_never_login_user_from_registration_data":total_never_login_user_from_registration_data} }), status.HTTP_200_OK
			

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-With-Date-Range-------------------------#

@name_space.route("/CustomerCountWithOrganisationAndRetailStoreWithDateRange/<string:filterkey>/<int:organisation_id>/<string:start_date>/<string:end_date>")	
class CustomerCountWithOrganisationAndRetailStoreWithDateRange(Resource):
	def get(self,filterkey,organisation_id,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = ecommerce_analytics()
		cur = conn.cursor()

		registation_data = {}
		notification_data = {}
		email_data = {}
		loggedin_data = {}
		demo_data = {}
		total_login_user_from_registration_data = {}
		total_never_login_user_from_registration_data = {}		

		if filterkey == 'today':
			
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,today_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(`U_id`)as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) = %s """)
			get_notify_customer_data = (organisation_id,today_date)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

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
				get_customer_retailer_query = ("""SELECT  count(`U_id`)as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and `destination_type` = 2 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0

			get_email_customer_query = ("""SELECT count(`customer_id`)as total_email_customer FROM `customer_email` 
				WHERE `organisation_id`=%s and date(`Last_Update_TS`) = %s """)
			get_email_customer_data = (organisation_id,today_date)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				email_data['store_data'] = store_data				
			else:
				email_data['store_data'] = []

			for nkey,ndata in enumerate(email_data['store_data']):
				get_customer_retailer_query = ("""SELECT count( ce.`customer_id`) as total_user FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""")
				get_customer_retailer_data = (organisation_id,today_date,organisation_id,ndata['retailer_store_store_id'])

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					email_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					email_data['store_data'][nkey]['customer_count'] = 0



			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`)=%s""")
			get_loged_In_customer_data = (organisation_id,today_date)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''

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


			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) = %s""")		
			get_demo_given_customer_data = (organisation_id,today_date)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

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
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:

					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0



			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,today_date)

			#get_registed_login_customer_query = ("""SELECT count(distict(`customer_id`))as total FROM `customer_store_analytics` 
				#WHERE `organisation_id`=%s and date(`last_update_ts`)=%s""")
			#get_registerd_login_customer_data = (organisation_id,today_date)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,today_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],today_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0
						

		if filterkey == 'yesterday':
			
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s""")
			get_registerd_customer_data = (organisation_id,yesterday)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(`U_id`)as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) = %s """)
			get_notify_customer_data = (organisation_id,yesterday)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

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
				get_customer_retailer_query = ("""SELECT count(`U_id`)as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and `destination_type` = 2 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0


			get_email_customer_query = ("""SELECT count(`customer_id`)as total_email_customer FROM `customer_email` 
				WHERE `organisation_id`=%s and date(`Last_Update_TS`) = %s """)
			get_email_customer_data = (organisation_id,yesterday)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				email_data['store_data'] = store_data				
			else:
				email_data['store_data'] = []

			for nkey,ndata in enumerate(email_data['store_data']):
				get_customer_retailer_query = ("""SELECT count( ce.`customer_id`) as total_user FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) = %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""")
				get_customer_retailer_data = (organisation_id,yesterday,organisation_id,ndata['retailer_store_store_id'])

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					email_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					email_data['store_data'][nkey]['customer_count'] = 0		

			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`)=%s""")
			get_loged_In_customer_data = (organisation_id,yesterday)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''

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
								

			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) = %s""")		
			get_demo_given_customer_data = (organisation_id,yesterday)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

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
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`)=%s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0


			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,yesterday)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,yesterday)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`)=%s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],yesterday)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0			

		if filterkey == 'last 7 days':
			
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(`U_id`)as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date)

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
				get_customer_retailer_query = ("""SELECT count(`U_id`)as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and a.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`) >= %s and date(a.`Last_Update_TS`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0


			get_email_customer_query = ("""SELECT count(`customer_id`)as total_email_customer FROM `customer_email` 
				WHERE `organisation_id`=%s and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s """)
			get_email_customer_data = (organisation_id,start_date,end_date)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				email_data['store_data'] = store_data				
			else:
				email_data['store_data'] = []

			for nkey,ndata in enumerate(email_data['store_data']):
				get_customer_retailer_query = ("""SELECT count( ce.`customer_id`) as total_user FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) >= %s and date(ce.`Last_Update_TS`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""")
				get_customer_retailer_data = (organisation_id,start_date,end_date,organisation_id,ndata['retailer_store_store_id'])

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					email_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					email_data['store_data'][nkey]['customer_count'] = 0		

			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
			get_loged_In_customer_data = (organisation_id,start_date,end_date)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''

			get_loggedin_user_query = ("""SELECT count(distinct(`customer_id`)) as total_user FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0 """)
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


			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

			if count_demo_given_customer > 0:
				print(cursor._last_executed)
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
				get_customer_retailer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 
					FROM `customer_remarks` cr 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >=%s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0


			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				print(cursor._last_executed)
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0


		if filterkey == 'this month':
			
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(`U_id`)as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				print(cursor._last_executed)
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
				get_customer_retailer_query = ("""SELECT count(`U_id`)as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and `destination_type` = 2 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`) >= %s and date(a.`Last_Update_TS`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0

			get_email_customer_query = ("""SELECT count(`customer_id`)as total_email_customer FROM `customer_email` 
				WHERE `organisation_id`=%s and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s """)
			get_email_customer_data = (organisation_id,start_date,end_date)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				email_data['store_data'] = store_data				
			else:
				email_data['store_data'] = []

			for nkey,ndata in enumerate(email_data['store_data']):
				get_customer_retailer_query = ("""SELECT count( ce.`customer_id`) as total_user FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) >= %s and date(ce.`Last_Update_TS`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""")
				get_customer_retailer_data = (organisation_id,start_date,end_date,organisation_id,ndata['retailer_store_store_id'])

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					email_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					email_data['store_data'][nkey]['customer_count'] = 0


			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
			get_loged_In_customer_data = (organisation_id,start_date,end_date)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''


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
					#loggedin_data['store_data'][nrlkey]['customer_count'] = 0
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


			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

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
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >=%s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0

			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				print(cursor._last_executed)
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0
		
		if filterkey == 'lifetime':

			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(`U_id`)as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date)

			count_notify_customer_data = cursor.execute(get_notify_customer_query,get_notify_customer_data)

			if count_notify_customer_data > 0:
				print(cursor._last_executed)
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
				get_customer_retailer_query = ("""SELECT count(`U_id`)as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and a.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`) >= %s and date(a.`Last_Update_TS`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0


			get_email_customer_query = ("""SELECT count(`customer_id`)as total_email_customer FROM `customer_email` 
				WHERE `organisation_id`=%s and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s """)
			get_email_customer_data = (organisation_id,start_date,end_date)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				email_data['store_data'] = store_data				
			else:
				email_data['store_data'] = []

			for nkey,ndata in enumerate(email_data['store_data']):
				get_customer_retailer_query = ("""SELECT count( ce.`customer_id`) as total_user FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) >= %s and date(ce.`Last_Update_TS`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""")
				get_customer_retailer_data = (organisation_id,start_date,end_date,organisation_id,ndata['retailer_store_store_id'])

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					email_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					email_data['store_data'][nkey]['customer_count'] = 0		

			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
			get_loged_In_customer_data = (organisation_id,start_date,end_date)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''

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
					#loggedin_data['store_data'][nrlkey]['customer_count'] = 0
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

			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

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
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >=%s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0	


			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				print(cursor._last_executed)
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0	

		if filterkey == 'custom date':

			start_date = start_date
			
			end_date = end_date

			print(start_date)
			print(end_date)

			get_registed_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <=%s""")
			get_registerd_customer_data = (organisation_id,start_date,end_date)

			count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)

			if count_registerd_customer > 0:
				registed_customer = cursor.fetchone()
				registation_data['total_customer_count'] = registed_customer['total']
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
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >= %s and date(`date_of_creation`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,data['retailer_store_id'],data['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					registation_data['store_data'][key]['customer_count'] = customer_retailer_data['total_user']
				else:
					registation_data['store_data'][key]['customer_count'] = 0


			

			get_notify_customer_query = ("""SELECT count(`U_id`)as total_notify_customer FROM `app_notification` 
				WHERE `organisation_id`=%s and `destination_type` = 2 and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s""")
			get_notify_customer_data = (organisation_id,start_date,end_date)

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
				get_customer_retailer_query = ("""SELECT count(`U_id`)as total_user 
					FROM `app_notification` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`U_id`
					WHERE ur.`organisation_id`=%s and a.`organisation_id` = %s and `destination_type` = 2 and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and date(a.`Last_Update_TS`) >= %s and date(a.`Last_Update_TS`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ndata['retailer_store_id'],ndata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					notification_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					notification_data['store_data'][nkey]['customer_count'] = 0

			get_email_customer_query = ("""SELECT count(`customer_id`)as total_email_customer FROM `customer_email` 
				WHERE `organisation_id`=%s and date(`Last_Update_TS`) >= %s and date(`Last_Update_TS`) <= %s """)
			get_email_customer_data = (organisation_id,start_date,end_date)

			count_email_customer_data = cursor.execute(get_email_customer_query,get_email_customer_data)

			if count_email_customer_data > 0:
				email_customer_data = cursor.fetchone()
				email_data['total_customer_count'] = email_customer_data['total_email_customer']
			else:
				email_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				email_data['store_data'] = store_data				
			else:
				email_data['store_data'] = []

			for nkey,ndata in enumerate(email_data['store_data']):
				get_customer_retailer_query = ("""SELECT count( ce.`customer_id`) as total_user FROM 
				`customer_email` ce
				INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ce.`customer_id`
				WHERE ce.`organisation_id`=%s and date(ce.`Last_Update_TS`) >= %s and date(ce.`Last_Update_TS`) <= %s and urm.`organisation_id` = %s and urm.`retailer_store_id` = %s""")
				get_customer_retailer_data = (organisation_id,start_date,end_date,organisation_id,ndata['retailer_store_store_id'])

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					email_data['store_data'][nkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					email_data['store_data'][nkey]['customer_count'] = 0
							

			'''get_loged_In_customer_query = ("""SELECT count(`admin_id`)as total_login_count FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
			get_loged_In_customer_data = (organisation_id,start_date,end_date)
			count_loged_In_customer_data = cursor.execute(get_loged_In_customer_query,get_loged_In_customer_data)

			if count_loged_In_customer_data > 0:
				loged_In_customer_data = cursor.fetchone()
				loggedin_data['total_customer_count'] = loged_In_customer_data['total_login_count']
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
			else:
				loggedin_data['store_data'] = []

			for lkey,ldata in enumerate(loggedin_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`loggedin_status`=1 and date(`date_of_lastlogin`) >= %s and date(`date_of_lastlogin`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ldata['retailer_store_id'],ldata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					loggedin_data['store_data'][lkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					loggedin_data['store_data'][lkey]['customer_count'] = 0'''

			get_loggedin_user_query = ("""SELECT count(distinct(`customer_id`)) as total_user FROM `customer_store_analytics` WHERE date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `organisation_id` = %s and `customer_id`!= 0 """)
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


			get_demo_given_customer_query = ("""SELECT count(distinct(`customer_id`))as total_user FROM 
				`customer_remarks` WHERE `customer_id`!=0 and `organisation_id`=%s and 
				date(`last_update_ts`) >= %s and date(`last_update_ts`) <= %s""")		
			get_demo_given_customer_data = (organisation_id,start_date,end_date)
			count_demo_given_customer =  cursor.execute(get_demo_given_customer_query,get_demo_given_customer_data)	

			if count_demo_given_customer > 0:
				print(cursor._last_executed)
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
				get_customer_retailer_query = ("""SELECT count(distinct(cr.`customer_id`))as total_user 
					FROM `customer_remarks` cr 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = cr.`customer_id`
					WHERE cr.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					date(cr.`last_update_ts`) >=%s and date(cr.`last_update_ts`) <= %s""")
				get_customer_retailer_data = (organisation_id,organisation_id,ddata['retailer_store_id'],ddata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)				
				if count_customer_retailer_data > 0:					
					customer_retailer_data = cursor.fetchone()
					demo_data['store_data'][dkey]['customer_count'] = customer_retailer_data['total_user']
				else:
					demo_data['store_data'][dkey]['customer_count'] = 0


			get_registed_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
			get_registerd_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_login_customer = cursor.execute(get_registed_login_customer_query,get_registerd_login_customer_data)

			if count_registerd_login_customer > 0:
				registed_login_customer = cursor.fetchone()
				total_login_user_from_registration_data['total_customer_count'] = registed_login_customer['total']
			else:
				total_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_login_user_from_registration_data['store_data'] = []

			for lukey,ludata in enumerate(total_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 1""")
				get_customer_retailer_data = (organisation_id,organisation_id,ludata['retailer_store_id'],ludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_login_user_from_registration_data['store_data'][lukey]['customer_count'] = 0



			get_registed_never_login_customer_query = ("""SELECT count(`admin_id`)as total FROM `admins` 
				WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
			get_registerd_never_login_customer_data = (organisation_id,start_date,end_date)

			count_registerd_never_login_customer = cursor.execute(get_registed_never_login_customer_query,get_registerd_never_login_customer_data)

			if count_registerd_never_login_customer > 0:
				print(cursor._last_executed)
				registed_never_login_customer = cursor.fetchone()
				total_never_login_user_from_registration_data['total_customer_count'] = registed_never_login_customer['total']
			else:
				total_never_login_user_from_registration_data['total_customer_count'] = 0

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				total_never_login_user_from_registration_data['store_data'] = store_data				
			else:
				total_never_login_user_from_registration_data['store_data'] = []

			for nlukey,nludata in enumerate(total_never_login_user_from_registration_data['store_data']):
				get_customer_retailer_query = ("""SELECT count(a.`admin_id`)as total_user 
					FROM `admins` a 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE ur.`organisation_id`=%s and a.`role_id`=4 and a.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s and
					a.`status`=1 and date(`date_of_creation`) >=%s and date(`date_of_creation`) <= %s and `loggedin_status` = 0""")
				get_customer_retailer_data = (organisation_id,organisation_id,nludata['retailer_store_id'],nludata['retailer_store_store_id'],start_date,end_date)

				count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

				if count_customer_retailer_data > 0:
					customer_retailer_data = cursor.fetchone()
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = customer_retailer_data['total_user']
				else:
					total_never_login_user_from_registration_data['store_data'][nlukey]['customer_count'] = 0	

		return ({"attributes": {
		    		"status_desc": "Customer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{"registation_data":registation_data,"notification_data":notification_data,"email_data":email_data,"loggedin_data":loggedin_data,"demo_data":demo_data,"total_login_user_from_registration_data":total_login_user_from_registration_data,"total_never_login_user_from_registration_data":total_never_login_user_from_registration_data} }), status.HTTP_200_OK
			

#--------------------Customer-Count-With-Organisation-And-Retailer-Store-------------------------#



#--------------------------------------------------------------------#
@name_space.route("/CustomerDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class CustomerDetailsByFilerKeyOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,organisation_id,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` WHERE `organisation_id`=%s and `role_id`=4 and 
				`status`=1 and date(`date_of_creation`)=%s""",(organisation_id,today))
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
			cursor.execute("""SELECT  `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,organisation_id,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

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
			cursor.execute("""SELECT  `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,organisation_id,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`date_of_creation`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

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
			cursor.execute("""SELECT  `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,organisation_id,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`) between %s and %s""",(organisation_id,stday,today))

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
			
			cursor.execute("""SELECT  `admin_id`,concat(`first_name`,' ',`last_name`)as
				name,concat('address line1-',`address_line_1`,',','address line2-',
				`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,
				`dob`,anniversary,`phoneno`,profile_image,organisation_id,`pincode`,date_of_creation,loggedin_status,wallet
				FROM `admins` WHERE `organisation_id`=%s and `role_id`=4 and `status`=1 and 
				date(`date_of_creation`) between %s and %s""",(organisation_id,slifetime,today))

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

#--------------------------------------------------------------------#
@name_space.route("/PushNotificatioDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class PushNotificatioDetailsByFilerKeyOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()

		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			
			cursor.execute("""SELECT `App_Notification_ID`,`title`,`body`,
				image,`U_id`,concat(`first_name`,' ',`last_name`)as name,
				anniversary,`phoneno`,`Device_ID`,`Sent`,ad.`organisation_id`,
				`Last_Update_TS` FROM `app_notification` apn inner join 
				`admins` ad on apn.`U_id`=ad.`admin_id` WHERE 
				apn.`organisation_id`=%s and date(`Last_Update_TS`)=%s""",(organisation_id,today))

			notifydata = cursor.fetchall()
			if notifydata:
				for i in range(len(notifydata)):
					notifydata[i]['Last_Update_TS'] = notifydata[i]['Last_Update_TS'].isoformat()
					
					notifydata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(notifydata[i]['U_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						notifydata[i]['customertype'] = customertype['customer_type']
					else:
						notifydata[i]['customertype'] = ''
			else:
				notifydata = []


		elif filterkey == 'yesterday':
			cursor.execute("""SELECT `App_Notification_ID`,`title`,`body`,
				image,`U_id`,concat(`first_name`,' ',`last_name`)as name,
				anniversary,anniversary,`phoneno`,`Device_ID`,`Sent`,ad.`organisation_id`,
				`Last_Update_TS` FROM `app_notification` apn inner join 
				`admins` ad on apn.`U_id`=ad.`admin_id` WHERE 
				apn.`organisation_id`=%s and date(`Last_Update_TS`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			notifydata = cursor.fetchall()
			if notifydata:
				for i in range(len(notifydata)):
					notifydata[i]['Last_Update_TS'] = notifydata[i]['Last_Update_TS'].isoformat()
					
					notifydata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(notifydata[i]['U_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						notifydata[i]['customertype'] = customertype['customer_type']
					else:
						notifydata[i]['customertype'] = ''
			else:
				notifydata = []


		elif filterkey == 'last 7 days':
			cursor.execute("""SELECT `App_Notification_ID`,`title`,`body`,
				image,`U_id`,concat(`first_name`,' ',`last_name`)as name,
				anniversary,`phoneno`,`Device_ID`,`Sent`,ad.`organisation_id`,
				`Last_Update_TS` FROM `app_notification` apn inner join 
				`admins` ad on apn.`U_id`=ad.`admin_id` WHERE 
				apn.`organisation_id`=%s and date(`Last_Update_TS`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`Last_Update_TS`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			notifydata = cursor.fetchall()
			if notifydata:
				for i in range(len(notifydata)):
					notifydata[i]['Last_Update_TS'] = notifydata[i]['Last_Update_TS'].isoformat()
					
					notifydata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(notifydata[i]['U_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						notifydata[i]['customertype'] = customertype['customer_type']
					else:
						notifydata[i]['customertype'] = ''
			else:
				notifydata = []

		
		elif filterkey == 'this month':
			cursor.execute("""SELECT `App_Notification_ID`,`title`,`body`,
				image,`U_id`,concat(`first_name`,' ',`last_name`)as name,
				anniversary,`phoneno`,`Device_ID`,`Sent`,ad.`organisation_id`,
				`Last_Update_TS` FROM `app_notification` apn inner join 
				`admins` ad on apn.`U_id`=ad.`admin_id` WHERE 
				apn.`organisation_id`=%s and date(`Last_Update_TS`) between %s and %s""",(organisation_id,stday,today))

			notifydata = cursor.fetchall()
			if notifydata:
				for i in range(len(notifydata)):
					notifydata[i]['Last_Update_TS'] = notifydata[i]['Last_Update_TS'].isoformat()
					
					notifydata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(notifydata[i]['U_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						notifydata[i]['customertype'] = customertype['customer_type']
					else:
						notifydata[i]['customertype'] = ''
			else:
				notifydata = []


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			
			cursor.execute("""SELECT `App_Notification_ID`,`title`,`body`,
				image,`U_id`,concat(`first_name`,' ',`last_name`)as name,
				anniversary,`phoneno`,`Device_ID`,`Sent`,ad.`organisation_id`,
				`Last_Update_TS` FROM `app_notification` apn inner join 
				`admins` ad on apn.`U_id`=ad.`admin_id` WHERE 
				apn.`organisation_id`=%s and date(`Last_Update_TS`) 
				between %s and %s""",(organisation_id,slifetime,today))

			notifydata = cursor.fetchall()
			if notifydata:
				for i in range(len(notifydata)):
					notifydata[i]['Last_Update_TS'] = notifydata[i]['Last_Update_TS'].isoformat()
					
					notifydata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(notifydata[i]['U_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						notifydata[i]['customertype'] = customertype['customer_type']
					else:
						notifydata[i]['customertype'] = ''
			else:
				notifydata = []

		else:
			notifydata = []
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "App Notification Details",
		    		"status": "success"
		    	},
		    	"responseList": notifydata }), status.HTTP_200_OK

#--------------------------------------------------------------------#
@name_space.route("/UniqueVisitorsDtlsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class UniqueVisitorsDtlsByFilerKeyOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()
		
		details = []
		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cur.execute("""SELECT DISTINCT(date(`last_update_ts`))as last_update_ts,`customer_id`,
				`from_web_or_phone`,organisation_id FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
			else:
				visitordata = []


		elif filterkey == 'yesterday':
			cur.execute("""SELECT DISTINCT(date(`last_update_ts`))as last_update_ts,`customer_id`,
				`from_web_or_phone`,organisation_id FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s  and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
			else:
				visitordata = []

		elif filterkey == 'last 7 days':
			cur.execute("""SELECT DISTINCT(date(`last_update_ts`))as last_update_ts,`customer_id`,
				`from_web_or_phone`,organisation_id FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
			else:
				visitordata = []

		
		elif filterkey == 'this month':
			cur.execute("""SELECT DISTINCT(date(`last_update_ts`))as last_update_ts,`customer_id`,
				`from_web_or_phone`,organisation_id FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
			else:
				visitordata = []


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			
			cur.execute("""SELECT DISTINCT(date(`last_update_ts`))as last_update_ts,`customer_id`,
				`from_web_or_phone`,organisation_id FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
			else:
				visitordata = []

		else:
			visitordata = []
			
		conn.commit()
		cur.close()
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Unique Visitor Details",
		    		"status": "success"
		    	},
		    	"responseList": visitordata}), status.HTTP_200_OK

#--------------------------------------------------------------------#
@name_space.route("/RepeatedVisitorsDtlsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class RepeatedVisitorsDtlsByFilerKeyOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()

		details = []
		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cur.execute("""SELECT `customer_id`,`from_web_or_phone`,
				organisation_id,`last_update_ts` FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
					
			else:
				visitordata = []


		elif filterkey == 'yesterday':
			cur.execute("""SELECT `customer_id`,`from_web_or_phone`,
				organisation_id,`last_update_ts` FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s  and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
			else:
				visitordata = []

		elif filterkey == 'last 7 days':
			cur.execute("""SELECT `customer_id`,`from_web_or_phone`,
				organisation_id,`last_update_ts` FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
			else:
				visitordata = []

		
		elif filterkey == 'this month':
			cur.execute("""SELECT `customer_id`,`from_web_or_phone`,
				organisation_id,`last_update_ts` FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
			else:
				visitordata = []


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			
			cur.execute("""SELECT `customer_id`,`from_web_or_phone`,
				organisation_id,`last_update_ts` FROM `customer_store_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			visitordata = cur.fetchall()
			if visitordata:
				for i in range(len(visitordata)):
					visitordata[i]['last_update_ts'] = visitordata[i]['last_update_ts'].isoformat()
					details.append(visitordata[i]['customer_id'])

					cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name,
						anniversary,`phoneno`,`organisation_id` FROM `admins` WHERE `admin_id`=%s""",(format(details)))

					visitorname = cursor.fetchone()
					if visitorname:
						visitordata[i]['visitorname'] = visitorname['name']
						visitordata[i]['phoneno'] = visitorname['phoneno']
						visitordata[i]['anniversary'] = visitorname['anniversary']
						
					else:
						visitordata[i]['visitorname'] = ''
						visitordata[i]['phoneno'] = ''
						visitordata[i]['anniversary'] = ''
						
					
					visitordata[i]['outstanding'] = 0
					cursor.execute("""SELECT `customer_type` FROM 
						`customer_type` where`customer_id`=%s and 
						`organisation_id`=%s""",(visitordata[i]['customer_id'],organisation_id))
					customertype = cursor.fetchone()
					if customertype:
						visitordata[i]['customertype'] = customertype['customer_type']
					else:
						visitordata[i]['customertype'] = ''
			else:
				visitordata = []

		else:
			visitordata = []
			
			
		conn.commit()
		cur.close()
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Repeated Visitor Details",
		    		"status": "success"
		    	},
		    	"responseList": visitordata }), status.HTTP_200_OK

#--------------------------------------------------------------------#
@name_space.route("/OrderStatusDtlsByOrganisationId/<int:organisation_id>")	
class OrderStatusDtlsByOrganisationId(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `orderstatus_id`,`order_status`,
			color FROM `order_status_master` order by last_update_id asc""")

		statusList = cursor.fetchall()
		for i in range(len(statusList)):

			cursor.execute("""SELECT count(`request_id`)as total FROM 
				`instamojo_payment_request` WHERE `status`=%s and 
				`organisation_id`=%s""",(statusList[i]['order_status'],organisation_id))

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

#-----------------------------------------------------------#
@name_space.route("/OrderDtlsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class OrderDtlsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
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
				FROM `order_product` op INNER join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` INNER join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` INNER join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` INNER join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE 
				op.`organisation_id`=%s and date(op.`last_update_ts`)=%s""",(organisation_id,today))

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
				FROM `order_product` op Left join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` Left join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` Left join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` Left join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE 
				op.`organisation_id`=%s and  
				date(op.`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

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
				FROM `order_product` op INNER join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` INNER join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` INNER join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` INNER join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE 
				op.`organisation_id`=%s and  
				date(op.`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(op.`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

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
				FROM `order_product` op INNER join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` INNER join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` INNER join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` INNER join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE 
				op.`organisation_id`=%s and  
				date(op.`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

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
				FROM `order_product` op INNER join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` INNER join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` INNER join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` INNER join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE 
				op.`organisation_id`=%s and  
				date(op.`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

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

#--------------------------------------------------------------#
@name_space.route("/SalesDtlsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class SalesDtlsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,`amount` as paid_amount,
				concat(`first_name`,' ',`last_name`)as name,anniversary,`phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,ipr.`last_update_ts`
				FROM `order_product` op INNER join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` INNER join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` INNER join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` INNER join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE 
				ipr.`status`='Completed' and
				op.`organisation_id`=%s and date(op.`last_update_ts`)=%s""",(organisation_id,today))

			orderdtls = cursor.fetchall()
			for i in range(len(orderdtls)):
				if orderdtls[i]['transaction_id'] != None:
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

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					else:
						orderdtls[i]['order_payment_status'] = 'Booked'

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					else:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'
				else:
					orderdtls = []
			
		elif filterkey == 'yesterday':
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,`amount` as paid_amount,
				concat(`first_name`,' ',`last_name`)as name,anniversary,`phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,ipr.`last_update_ts`
				FROM `order_product` op INNER join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` INNER join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` INNER join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` INNER join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE 
				ipr.`status`='Completed' and op.`organisation_id`=%s and  
				date(op.`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			orderdtls = cursor.fetchall()
			for i in range(len(orderdtls)):
				if orderdtls[i]['transaction_id'] != None:
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

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					else:
						orderdtls[i]['order_payment_status'] = 'Booked'

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					else:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'
				else:
					orderdtls = []

		elif filterkey == 'last 7 day':
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,`amount` as paid_amount,
				concat(`first_name`,' ',`last_name`)as name,anniversary,`phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,ipr.`last_update_ts`
				FROM `order_product` op INNER join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` INNER join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` INNER join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` INNER join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE ipr.`status`='Completed' and
				op.`organisation_id`=%s and  
				date(op.`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(op.`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			orderdtls = cursor.fetchall()
			for i in range(len(orderdtls)):
				if orderdtls[i]['transaction_id'] != None:
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

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					else:
						orderdtls[i]['order_payment_status'] = 'Booked'

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					else:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'
				else:
					orderdtls = []
			
		
		elif filterkey == 'this month':
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,`amount` as paid_amount,
				concat(`first_name`,' ',`last_name`)as name,anniversary,`phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,ipr.`last_update_ts`
				FROM `order_product` op INNER join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` INNER join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` INNER join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` INNER join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE ipr.`status`='Completed' and
				op.`organisation_id`=%s and date(op.`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			orderdtls = cursor.fetchall()
			for i in range(len(orderdtls)):
				if orderdtls[i]['transaction_id'] != None:
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

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					else:
						orderdtls[i]['order_payment_status'] = 'Booked'

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					else:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'
				else:
					orderdtls = []


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			cursor.execute("""SELECT `order_product_id`,
				op.`transaction_id`,cpm.`customer_id`,`amount` as paid_amount,
				concat(`first_name`,' ',`last_name`)as name,anniversary,`phoneno`,
				`product_name`,`out_price`,ipr.`status`,`order_payment_status`,
				`delivery_option`,op.`organisation_id`,ipr.`last_update_ts`
				FROM `order_product` op INNER join `customer_product_mapping` cpm 
				on op.`customer_mapping_id`=cpm.`mapping_id` INNER join `admins` ad 
				on cpm.`customer_id`=ad.`admin_id` INNER join `product_meta` pm on 
				cpm.`product_meta_id`=pm.`product_meta_id` INNER join `product` pd on 
				pm.`product_id`=pd.`product_id` INNER join 
				`instamojo_payment_request` ipr on 
				op.`transaction_id`=ipr.`transaction_id` WHERE ipr.`status`='Completed' and
				op.`organisation_id`=%s and  
				date(op.`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			orderdtls = cursor.fetchall()
			for i in range(len(orderdtls)):
				if orderdtls[i]['transaction_id'] != None:
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

					if orderdtls[i]['order_payment_status'] == 1:
						orderdtls[i]['order_payment_status'] = 'Partial Payment'
					
					elif orderdtls[i]['order_payment_status'] == 2:
						orderdtls[i]['order_payment_status'] = 'Full Payment'
					
					elif orderdtls[i]['order_payment_status'] == 3:
						orderdtls[i]['order_payment_status'] = 'No Payment'
					
					else:
						orderdtls[i]['order_payment_status'] = 'Booked'

					if orderdtls[i]['delivery_option'] == 1:
						orderdtls[i]['delivery_option'] = 'Pick at Store'
					
					else:
						orderdtls[i]['delivery_option'] = 'Delivery at my location'
				else:
					orderdtls = []

		else:
			orderdtls = []
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Sales Details",
		    		"status": "success"
		    	},
		    	"responseList": orderdtls}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/ProductViewDtlsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class ProductViewDtlsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()
		
		today = date.today()
		day = '01'
		stday = today.replace(day=int(day))
		
		if filterkey == 'today':
			cur.execute("""SELECT `analytics_id`,`customer_id`,`product_id`,
				`from_web_or_phone`,last_update_ts FROM `customer_product_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`)=%s ORDER BY `analytics_id` DESC""",
				(organisation_id,today))
			productviewDtls = cur.fetchall()

			for aid in range(len(productviewDtls)):
				productviewDtls[aid]['last_update_ts'] = productviewDtls[aid]['last_update_ts'].isoformat()
				
				cursor.execute("""SELECT `product_name` FROM `product`
					WHERE `product_id`=%s""",(productviewDtls[aid]['product_id']))

				prdviewdtls = cursor.fetchone()

				if prdviewdtls:
					productviewDtls[aid]['product_name'] = prdviewdtls['product_name']
				
				cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name, 
					`phoneno`,anniversary FROM `admins` WHERE `admin_id`=%s""",(productviewDtls[aid]['customer_id']))
				visitordtls = cursor.fetchone()
				
				if visitordtls:
					productviewDtls[aid]['name'] = visitordtls['name']
					productviewDtls[aid]['phoneno'] = visitordtls['phoneno']
					productviewDtls[aid]['anniversary'] = visitordtls['anniversary']

				else:
					productviewDtls[aid]['name'] = ''
					productviewDtls[aid]['phoneno'] = ''
					productviewDtls[aid]['anniversary'] = ''

				productviewDtls[aid]['outstanding'] = 0
				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(productviewDtls[aid]['customer_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					productviewDtls[aid]['customertype'] = customertype['customer_type']
				else:
					productviewDtls[aid]['customertype'] = ''	
			
		elif filterkey == 'yesterday':
			
			cur.execute("""SELECT `analytics_id`,`customer_id`,`product_id`,
				`from_web_or_phone`,last_update_ts FROM `customer_product_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY ORDER BY `analytics_id` DESC""",(organisation_id))

			productviewDtls = cur.fetchall()

			for aid in range(len(productviewDtls)):
				productviewDtls[aid]['last_update_ts'] = productviewDtls[aid]['last_update_ts'].isoformat()
				
				cursor.execute("""SELECT `product_name` FROM `product`
					WHERE `product_id`=%s""",(productviewDtls[aid]['product_id']))

				prdviewdtls = cursor.fetchone()

				if prdviewdtls:
					productviewDtls[aid]['product_name'] = prdviewdtls['product_name']
				
				cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name, 
					`phoneno`,anniversary FROM `admins` WHERE `admin_id`=%s""",(productviewDtls[aid]['customer_id']))
				visitordtls = cursor.fetchone()
				
				if visitordtls:
					productviewDtls[aid]['name'] = visitordtls['name']
					productviewDtls[aid]['phoneno'] = visitordtls['phoneno']
					productviewDtls[aid]['anniversary'] = visitordtls['anniversary']
					
				else:
					productviewDtls[aid]['name'] = ''
					productviewDtls[aid]['phoneno'] = ''
					productviewDtls[aid]['anniversary'] = ''

				productviewDtls[aid]['outstanding'] = 0
				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(productviewDtls[aid]['customer_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					productviewDtls[aid]['customertype'] = customertype['customer_type']
				else:
					productviewDtls[aid]['customertype'] = ''

		elif filterkey == 'last 7 day':
			
			cur.execute("""SELECT `analytics_id`,`customer_id`,`product_id`,
				`from_web_or_phone`,last_update_ts FROM `customer_product_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY ORDER BY `analytics_id` DESC""",(organisation_id))

			productviewDtls = cur.fetchall()

			for aid in range(len(productviewDtls)):
				productviewDtls[aid]['last_update_ts'] = productviewDtls[aid]['last_update_ts'].isoformat()
				
				cursor.execute("""SELECT `product_name` FROM `product`
					WHERE `product_id`=%s""",(productviewDtls[aid]['product_id']))

				prdviewdtls = cursor.fetchone()

				if prdviewdtls:
					productviewDtls[aid]['product_name'] = prdviewdtls['product_name']
				
				cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name, 
					`phoneno`,anniversary FROM `admins` WHERE `admin_id`=%s""",(productviewDtls[aid]['customer_id']))
				visitordtls = cursor.fetchone()
				
				if visitordtls:
					productviewDtls[aid]['name'] = visitordtls['name']
					productviewDtls[aid]['phoneno'] = visitordtls['phoneno']
					productviewDtls[aid]['anniversary'] = visitordtls['anniversary']
					
				else:
					productviewDtls[aid]['name'] = ''
					productviewDtls[aid]['phoneno'] = ''
					productviewDtls[aid]['anniversary'] = ''

				productviewDtls[aid]['outstanding'] = 0
				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(productviewDtls[aid]['customer_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					productviewDtls[aid]['customertype'] = customertype['customer_type']
				else:
					productviewDtls[aid]['customertype'] = ''
			
		
		elif filterkey == 'this month':
			
			cur.execute("""SELECT `analytics_id`,`customer_id`,`product_id`,
				`from_web_or_phone`,last_update_ts FROM `customer_product_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s ORDER BY `analytics_id` DESC""",
				(organisation_id,stday,today))
			productviewDtls = cur.fetchall()

			for aid in range(len(productviewDtls)):
				productviewDtls[aid]['last_update_ts'] = productviewDtls[aid]['last_update_ts'].isoformat()
				
				cursor.execute("""SELECT `product_name` FROM `product`
					WHERE `product_id`=%s""",(productviewDtls[aid]['product_id']))

				prdviewdtls = cursor.fetchone()

				if prdviewdtls:
					productviewDtls[aid]['product_name'] = prdviewdtls['product_name']
				
				cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name, 
					`phoneno`,anniversary FROM `admins` WHERE `admin_id`=%s""",(productviewDtls[aid]['customer_id']))
				visitordtls = cursor.fetchone()
				
				if visitordtls:
					productviewDtls[aid]['name'] = visitordtls['name']
					productviewDtls[aid]['phoneno'] = visitordtls['phoneno']
					productviewDtls[aid]['anniversary'] = visitordtls['anniversary']
					
				else:
					productviewDtls[aid]['name'] = ''
					productviewDtls[aid]['phoneno'] = ''
					productviewDtls[aid]['anniversary'] = ''

				productviewDtls[aid]['outstanding'] = 0
				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(productviewDtls[aid]['customer_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					productviewDtls[aid]['customertype'] = customertype['customer_type']
				else:
					productviewDtls[aid]['customertype'] = ''


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			
			cur.execute("""SELECT `analytics_id`,`customer_id`,`product_id`,
				`from_web_or_phone`,last_update_ts FROM `customer_product_analytics` WHERE 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s ORDER BY `analytics_id` DESC""",(organisation_id,slifetime,today))

			productviewDtls = cur.fetchall()

			for aid in range(len(productviewDtls)):
				productviewDtls[aid]['last_update_ts'] = productviewDtls[aid]['last_update_ts'].isoformat()
				
				cursor.execute("""SELECT `product_name` FROM `product`
					WHERE `product_id`=%s""",(productviewDtls[aid]['product_id']))

				prdviewdtls = cursor.fetchone()

				if prdviewdtls:
					productviewDtls[aid]['product_name'] = prdviewdtls['product_name']
				
				cursor.execute("""SELECT concat(`first_name`,' ',`last_name`)as name, 
					`phoneno`,anniversary FROM `admins` WHERE `admin_id`=%s""",(productviewDtls[aid]['customer_id']))
				visitordtls = cursor.fetchone()
				
				if visitordtls:
					productviewDtls[aid]['name'] = visitordtls['name']
					productviewDtls[aid]['phoneno'] = visitordtls['phoneno']
					productviewDtls[aid]['anniversary'] = visitordtls['anniversary']
					
				else:
					productviewDtls[aid]['name'] = ''
					productviewDtls[aid]['phoneno'] = ''
					productviewDtls[aid]['anniversary'] = ''

				productviewDtls[aid]['outstanding'] = 0
				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(productviewDtls[aid]['customer_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					productviewDtls[aid]['customertype'] = customertype['customer_type']
				else:
					productviewDtls[aid]['customertype'] = ''

		else:
			productviewDtls = []
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Product View Details",
		    		"status": "success"
		    	},
		    	"responseList": productviewDtls}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/StoreViewDtlsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class StoreViewDtlsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()
		
		today = date.today()
		print(today)
		day = '01'
		stday = today.replace(day=int(day))

		print(stday)
		
		if filterkey == 'today':
			cur.execute("""SELECT DISTINCT `customer_id`,
				`from_web_or_phone` FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=%s ORDER BY `analytics_id` DESC""",(organisation_id,today))		
			print(cur._last_executed)	
			storeviewDtls = cur.fetchall()


			if storeviewDtls:
				for aid in range(len(storeviewDtls)):
					cur.execute("""SELECT `analytics_id`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts`,`organisation_id` FROM `customer_store_analytics` WHERE `customer_id`=%s and `from_web_or_phone` = %s and date(`last_update_ts`)=%s""",(storeviewDtls[aid]['customer_id'],storeviewDtls[aid]['from_web_or_phone'],today))
					storeviewDtlsAnalyticsdata = cur.fetchone()
					storeviewDtls[aid]['last_update_ts'] = str(storeviewDtlsAnalyticsdata['last_update_ts']).replace(' ','T')
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

		elif filterkey == 'yesterday':
			
			cur.execute("""SELECT DISTINCT `customer_id`,
				`from_web_or_phone` FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY ORDER BY `analytics_id` DESC""",(organisation_id))			

			storeviewDtls = cur.fetchall()

			if storeviewDtls:
				for aid in range(len(storeviewDtls)):
					cur.execute("""SELECT `analytics_id`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts`,`organisation_id` FROM `customer_store_analytics` WHERE `customer_id`=%s and `from_web_or_phone` = %s and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(storeviewDtls[aid]['customer_id'],storeviewDtls[aid]['from_web_or_phone']))
					storeviewDtlsAnalyticsdata = cur.fetchone()
					storeviewDtls[aid]['last_update_ts'] = str(storeviewDtlsAnalyticsdata['last_update_ts']).replace(' ','T')
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

		elif filterkey == 'last 7 day':
			
			cur.execute("""SELECT DISTINCT `customer_id`,
				`from_web_or_phone` FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY ORDER BY `analytics_id` DESC""",
        		(organisation_id))

			storeviewDtls = cur.fetchall()

			if storeviewDtls:
				for aid in range(len(storeviewDtls)):
					cur.execute("""SELECT `analytics_id`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts`,`organisation_id` FROM `customer_store_analytics` WHERE `customer_id`=%s and `from_web_or_phone` = %s and date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(storeviewDtls[aid]['customer_id'],storeviewDtls[aid]['from_web_or_phone']))
					storeviewDtlsAnalyticsdata = cur.fetchone()
					storeviewDtls[aid]['last_update_ts'] = str(storeviewDtlsAnalyticsdata['last_update_ts']).replace(' ','T')
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
			
		
		elif filterkey == 'this month':
			
			cur.execute("""SELECT DISTINCT `customer_id`,
				`from_web_or_phone` FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s ORDER BY `analytics_id` DESC""",(organisation_id,stday,today))

			storeviewDtls = cur.fetchall()

			if storeviewDtls:
				for aid in range(len(storeviewDtls)):
					cur.execute("""SELECT `analytics_id`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts`,`organisation_id` FROM `customer_store_analytics` WHERE `customer_id`=%s and `from_web_or_phone` = %s and date(`last_update_ts`) between %s and %s""",(storeviewDtls[aid]['customer_id'],storeviewDtls[aid]['from_web_or_phone'],stday,today))
					storeviewDtlsAnalyticsdata = cur.fetchone()
					storeviewDtls[aid]['last_update_ts'] = str(storeviewDtlsAnalyticsdata['last_update_ts']).replace(' ','T')
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


		elif filterkey == 'lifetime':
			slifetime = '2020-07-10'
			
			cur.execute("""SELECT DISTINCT `customer_id`,
				`from_web_or_phone` FROM 
				`customer_store_analytics` WHERE `organisation_id`=%s 
				and date(`last_update_ts`) between %s and %s ORDER BY `analytics_id` DESC""",(organisation_id,slifetime,today))

			storeviewDtls = cur.fetchall()

			if storeviewDtls:
				for aid in range(len(storeviewDtls)):
					cur.execute("""SELECT `analytics_id`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts`,`organisation_id` FROM `customer_store_analytics` WHERE `customer_id`=%s and `from_web_or_phone` = %s and date(`last_update_ts`) between %s and %s""",(storeviewDtls[aid]['customer_id'],storeviewDtls[aid]['from_web_or_phone'],slifetime,today))
					storeviewDtlsAnalyticsdata = cur.fetchone()
					storeviewDtls[aid]['last_update_ts'] = str(storeviewDtlsAnalyticsdata['last_update_ts']).replace(' ','T')
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

		else:
			storeviewDtls = []
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Store View Details",
		    		"status": "success"
		    	},
		    	"responseList": storeviewDtls}), status.HTTP_200_OK

#-----------------------------------------------------#
@name_space.route("/OfferCountDetailsByDateOrganizationId/<string:filterkey>/<int:organisation_id>")	
class OfferCountDetailsByDateOrganizationId(Resource):
	def get(self,filterkey,organisation_id):
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
			
			cursor.execute("""SELECT count(`transaction_id`)as total FROM 
				`instamojo_payment_request` WHERE `coupon_code`!='' and 
				`organisation_id`=%s and date(`last_update_ts`)=%s""",(organisation_id,today))

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

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_offer_analytics` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=%s""",(organisation_id,today))

			offerviewdata = cur.fetchone()
			if offerviewdata:
				offerview = offerviewdata['total']
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

			cursor.execute("""SELECT count(`transaction_id`)as total FROM 
				`instamojo_payment_request` WHERE `coupon_code`!='' and 
				`organisation_id`=%s and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

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

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_offer_analytics` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",(organisation_id))

			offerviewdata = cur.fetchone()
			if offerviewdata:
				offerview = offerviewdata['total']
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
			
			
			cursor.execute("""SELECT count(`transaction_id`)as total FROM 
				`instamojo_payment_request` WHERE `coupon_code`!='' and 
				`organisation_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

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

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_offer_analytics` WHERE `organisation_id`=%s and 
				date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(organisation_id))

			offerviewdata = cur.fetchone()
			if offerviewdata:
				offerview = offerviewdata['total']
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
			
			
			cursor.execute("""SELECT count(`transaction_id`)as total FROM 
				`instamojo_payment_request` WHERE `coupon_code`!='' and 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

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

			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_offer_analytics` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,stday,today))

			offerviewdata = cur.fetchone()
			if offerviewdata:
				offerview = offerviewdata['total']
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
			
			
			cursor.execute("""SELECT count(`transaction_id`)as total FROM 
				`instamojo_payment_request` WHERE `coupon_code`!='' and 
				`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

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

			
			cur.execute("""SELECT count(`analytics_id`)as total FROM 
				`customer_offer_analytics` WHERE `organisation_id`=%s and 
				date(`last_update_ts`) between %s and %s""",(organisation_id,slifetime,today))

			offerviewdata = cur.fetchone()
			if offerviewdata:
				offerview = offerviewdata['total']
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

#------------------------------------------------------#
@name_space.route("/OrderStatusDtlsByDateOrganisationId/<string:filterkey>/<int:organisation_id>")	
class OrderStatusDtlsByDateOrganisationId(Resource):
	def get(self,filterkey,organisation_id):
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
				cursor.execute("""SELECT count(`request_id`)as total FROM 
					`instamojo_payment_request` WHERE `status`=%s and 
					`organisation_id`=%s and date(`last_update_ts`)=%s""",
					(statusList[i]['order_status'],organisation_id,today))

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
				cursor.execute("""SELECT count(`request_id`)as total FROM 
					`instamojo_payment_request` WHERE `status`=%s and 
					`organisation_id`=%s and date(`last_update_ts`)=DATE(NOW()) + INTERVAL -1 DAY""",
					(statusList[i]['order_status'],organisation_id))

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
				cursor.execute("""SELECT count(`request_id`)as total FROM 
					`instamojo_payment_request` WHERE `status`=%s and 
					`organisation_id`=%s and date(`last_update_ts`)>= DATE(NOW()) + INTERVAL -7 DAY and 
	        		date(`last_update_ts`) < DATE(NOW()) + INTERVAL 0 DAY""",(statusList[i]['order_status'],organisation_id))

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
				cursor.execute("""SELECT count(`request_id`)as total FROM 
					`instamojo_payment_request` WHERE `status`=%s and 
					`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",
					(statusList[i]['order_status'],organisation_id,stday,today))

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
				cursor.execute("""SELECT count(`request_id`)as total FROM 
					`instamojo_payment_request` WHERE `status`=%s and 
					`organisation_id`=%s and date(`last_update_ts`) between %s and %s""",
					(statusList[i]['order_status'],organisation_id,slifetime,today))

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

#---------------------------------------------------------------#
@name_space.route("/OfferCountDetailsByOfferId/<int:offer_id>")	
class OfferCountDetailsByOfferId(Resource):
	def get(self,offer_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = ecommerce_analytics()
		cur = conn.cursor()
		
		cursor.execute("""SELECT count(`transaction_id`)as total FROM 
			`instamojo_payment_request` WHERE `coupon_code` in(SELECT 
			`coupon_code` FROM `offer` WHERE `offer_id`=%s)""",(offer_id))

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

#------------------------------------------------------#
