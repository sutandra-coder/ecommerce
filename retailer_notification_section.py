from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import datetime
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
from pyfcm import FCMNotification
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

retailer_notification_section = Blueprint('retailer_notification_section', __name__)
api = Api(retailer_notification_section, version='1.0', title='Ecommerce API',
    description='Ecommerce API')

name_space = api.namespace('RetailerNotification',description='Retailer Notification')

# BASE_URL = 'http://ec2-3-19-228-138.us-east-2.compute.amazonaws.com/flaskapp/'
BASE_URL = 'http://127.0.0.1:5000/'
#-----------------------------------------------------------------#
add_device = api.model('add_device', {
	"device_type": fields.String(),
	"device_token": fields.String(),
	"organisation_id": fields.Integer()
	})

add_retail_store_device = api.model('add_retail_store_device', {
	"device_type": fields.String(),
	"device_token": fields.String(),
	"retail_store_id": fields.Integer(),
	"organisation_id": fields.Integer()
	})

appmsgmodel = api.model('appmsgmodel', {
	"title": fields.String(),
	"msg": fields.String(),
	"img": fields.String(),
	"organisation_id": fields.Integer()
	})


retailer_notification = api.model('retailer_notification',{
	"title": fields.String(),
	"msg": fields.String(),
	"img": fields.String(),
	"organisation_id": fields.Integer(),
	"retail_store_id": fields.Integer()
})

#----------------------------------------------------------------#
@name_space.route("/AddOrganisationDeviceDetails")
class AddOrganisationDeviceDetails(Resource):
	@api.expect(add_device)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		device_type = details.get('device_type')
		device_token = details.get('device_token')
		organisation_id = details.get('organisation_id')
		
		cursor.execute("""SELECT `device_id` FROM `organisation_devices` 
			WHERE `organisation_id`=%s""",(organisation_id))
		deviceDtls = cursor.fetchone()
		if deviceDtls == None:	
			devicetoken_query = ("""INSERT INTO `organisation_devices`(`device_type`,
				`device_token`,`organisation_id`) VALUES(%s,%s,%s)""")
			insert_data = (device_type,device_token,organisation_id)
			print(insert_data)
			tokendata = cursor.execute(devicetoken_query,insert_data)
			if tokendata:
				msg = "Successfully Added"

			else:
				msg = "Not Added"
		else:
			updatedevicetoken = ("""UPDATE `organisation_devices` SET `device_type`=%s,
			`device_token`=%s WHERE organisation_id= %s""")
			updatetokendata = cursor.execute(updatedevicetoken,(device_type,
				device_token,organisation_id))
			if updatetokendata:
				msg = "Successfully Updated"

			else:
				msg = "Not Updated"

		connection.commit()
		cursor.close()
		return ({"attributes": {
				    		"status_desc": "Organisation Device Details",
				    		"status": "success"
				    	},
				"responseList": msg}), status.HTTP_200_OK

#----------------------------------------------------------------#

#----------------------------------------------------------------#
@name_space.route("/AddRetailStoreDeviceDetails")
class AddRetailStoreDeviceDetails(Resource):
	@api.expect(add_retail_store_device)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		device_type = details.get('device_type')
		device_token = details.get('device_token')
		retail_store_id = details.get('retail_store_id')
		organisation_id = details.get('organisation_id')
		
		cursor.execute("""SELECT `device_id` FROM `retail_store_devices` 
			WHERE `retailer_store_id`=%s and `organisation_id` = %s""",(retail_store_id,organisation_id))
		deviceDtls = cursor.fetchone()
		if deviceDtls == None:	
			devicetoken_query = ("""INSERT INTO `retail_store_devices`(`device_type`,
				`device_token`,`retailer_store_id`,`organisation_id`) VALUES(%s,%s,%s,%s)""")
			insert_data = (device_type,device_token,retail_store_id,organisation_id)
			print(insert_data)
			tokendata = cursor.execute(devicetoken_query,insert_data)
			if tokendata:
				msg = "Successfully Added"

			else:
				msg = "Not Added"
		else:
			updatedevicetoken = ("""UPDATE `retail_store_devices` SET `device_type`=%s,
			`device_token`=%s WHERE `organisation_id` = %s and `retailer_store_id` = %s""")
			updatetokendata = cursor.execute(updatedevicetoken,(device_type,
				device_token,organisation_id,retail_store_id))
			if updatetokendata:
				msg = "Successfully Updated"

			else:
				msg = "Not Updated"

		connection.commit()
		cursor.close()
		return ({"attributes": {
				    		"status_desc": "Organisation Device Details",
				    		"status": "success"
				    	},
				"responseList": msg}), status.HTTP_200_OK

#----------------------------------------------------------------#
@name_space.route("/SendPushNotificationsToOrganisation")
class SendPushNotificationsToOrganisation(Resource):
	@api.expect(appmsgmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		title = details.get('title')
		msg = details.get('msg')
		img = details.get('img')
		organisation_id = details.get('organisation_id')
		

		cursor.execute("""SELECT * FROM `organisation_devices` WHERE 
			organisation_id=%s""",(organisation_id))
		deviceDtls = cursor.fetchone()
		if deviceDtls == None:
			sent = "Not found device token"
		else:
			device_id = deviceDtls['device_token']
			# print(device_id)
			cursor.execute("""SELECT * FROM `organisation_firebase_details` 
				where `organisation_id`=%s""",(organisation_id))
			firebaseDtls = cursor.fetchone()
			if firebaseDtls == None:
				sent = "Not found firebase key"
			else:
				api_key = "AAAASJY2wZ4:APA91bEcDslvSCJVZtVvJI4dDQ_IrpdVB5vaYqfB0OlfI5oQWl40vr1IvkW7PP0_GzUgzCwwll_UKLG6KCVfxJLkzmfK7jyGxZYKFerkbgmNpS0KSGNmqIGB9ZjhT5LvP2lRc82TwA44"

			data_message = {
							"title" : title,
							"message": msg,
							"image-url":img
							}
			
			push_service = FCMNotification(api_key=api_key)
			msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
			sent = 'No'
			if msgResponse.get('success') == 1:
				sent = 'Yes'
				destination_type = 3
				app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
					`U_id`,`Device_ID`,`Sent`,`destination_type`,`organisation_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s)""")
				insert_data = (title,msg,'',device_id,sent,destination_type,organisation_id)
				appdata = cursor.execute(app_query,insert_data)
				

		
		connection.commit()
		cursor.close()
		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				"responseList": sent}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/NotificationHistoryByOrganizationId/<int:organisation_id>")	
class NotificationHistoryByOrganizationId(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `App_Notification_ID`,`title`,`body`,
			`U_id`,`Device_ID`,`Sent`,`organisation_id`,
			`Last_Update_TS` FROM `app_notification` WHERE 
			`U_id`='' and organisation_id=%s""",(organisation_id))

		notifydata = cursor.fetchall()
		if notifydata:
			for i in range(len(notifydata)):
				notifydata[i]['Last_Update_TS'] = notifydata[i]['Last_Update_TS'].isoformat()
		else:
			notifydata = []
	
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Retailer Notification Details",
		    		"status": "success"
		    	},
		    	"responseList": notifydata }), status.HTTP_200_OK

#-----------------------------------------------------------#

#----------------------------------------------------------------#
@name_space.route("/SendPushNotificationsToRetailer")
class SendPushNotificationsToRetailer(Resource):
	@api.expect(retailer_notification)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today()

		title = details.get('title')
		msg = details.get('msg')
		img = details.get('img')
		retail_store_id = details.get('retail_store_id')
		organisation_id = details.get('organisation_id')
		

		cursor.execute("""SELECT * FROM `retail_store_devices` WHERE 
			`organisation_id`=%s and `retailer_store_id` = %s""",(organisation_id,retail_store_id))
		deviceDtls = cursor.fetchone()
		if deviceDtls == None:
			sent = "Not found device token"
		else:
			device_id = deviceDtls['device_token']
			print(device_id)
			cursor.execute("""SELECT * FROM `organisation_firebase_details` 
				where `organisation_id`=%s""",(organisation_id))
			firebaseDtls = cursor.fetchone()
			
			if firebaseDtls == None:
				sent = "Not found firebase key"
			else:
				api_key = "AAAASJY2wZ4:APA91bEcDslvSCJVZtVvJI4dDQ_IrpdVB5vaYqfB0OlfI5oQWl40vr1IvkW7PP0_GzUgzCwwll_UKLG6KCVfxJLkzmfK7jyGxZYKFerkbgmNpS0KSGNmqIGB9ZjhT5LvP2lRc82TwA44"

			data_message = {
							"title" : title,
							"message": msg,
							"image-url":img
							}
			
			push_service = FCMNotification(api_key=api_key)
			msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
			print(msgResponse)
			sent = 'No'
			if msgResponse.get('success') == 1:
				sent = 'Yes'
				destination_type = 3
				app_query = ("""INSERT INTO `app_notification`(`title`,`body`,
					`U_id`,`Device_ID`,`Sent`,`destination_type`,`organisation_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s)""")
				insert_data = (title,msg,'',device_id,sent,destination_type,organisation_id)
				appdata = cursor.execute(app_query,insert_data)
				

		
		connection.commit()
		cursor.close()
		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				"responseList": sent}), status.HTTP_200_OK

#----------------------------------------------------------#
