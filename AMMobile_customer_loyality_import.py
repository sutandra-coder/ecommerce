from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json,render_template
from flask_api import status
from jinja2 import Environment, FileSystemLoader
from datetime import datetime,timedelta,date
import pymysql
from smtplib import SMTP
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
from werkzeug import secure_filename
import requests
import calendar
import json
from instamojoConfig import CLIENT_ID,CLIENT_SECRET,referrer
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import os
import hashlib
import random, string
import math
from datetime import datetime
import boto3
from botocore.config import Config
import csv
import re
from decimal import Decimal

AMMobile_customer_loyality_import = Blueprint('AMMobile_customer_loyality_import_api', __name__)
api = Api(AMMobile_customer_loyality_import,  title='AM Mobile Customer Loyality',description='AM Mobile Customer Loyality Import API')
name_space = api.namespace('AMMobileCustomerLoyalityImport',description='AM Mobile Customer Loyality Import')

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'
Local_base_url = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/AMMobile_customer_import/'

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

def am_product_mysql_connection():
	connection = pymysql.connect(host='ammobileproduct.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='EKr3RnhsAssFw78a91N5',
	                             db='AMMobileProduct',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection
#----------------------database-connection---------------------#

#-----------------------get-Excel-Sheet-Data---------------------#

@name_space.route("/getXcelsheetData/<int:organisation_id>/<int:request_no>")	
class getXcelsheetData(Resource):
	def get(self,organisation_id,request_no):
		connection = am_product_mysql_connection()
		cursor = connection.cursor()

		connection_ecommerce = mysql_connection()
		cursor_ecommerce = connection_ecommerce.cursor()		

		registration_type = 5
		organisation_id = organisation_id

		get_query = ("""SELECT *
			FROM `customer_transaction` where `request_no` = %s and `status` = 'done'""")
		get_data = (request_no)
		cursor.execute(get_query,get_data)

		customer_transaction_data = cursor.fetchall()

		for key,data in enumerate(customer_transaction_data):

			customer_transaction_data[key]['last_update_ts'] = str(data['last_update_ts'])

			get_phone_type_query = ("""SELECT *
					FROM `admins` WHERE `phoneno` = %s and `organisation_id` = %s and `registration_type` = %s""")
			get_phone_type_data = (data['mobile'],organisation_id,registration_type)

			count_phone_type = cursor_ecommerce.execute(get_phone_type_query,get_phone_type_data)


			if count_phone_type > 0:

				login_data = cursor_ecommerce.fetchone()
				user_id = login_data['admin_id']

				get_customer_wallet_transaction_query = ("""SELECT * from `wallet_transaction` where `customer_id` = %s and `transaction_source` = 'signup' ORDER BY `wallet_transaction_id` desc""")
				get_customer_wallet_transaction_data = (user_id)
				customer_wallet_transaction_count = cursor_ecommerce.execute(get_customer_wallet_transaction_query,get_customer_wallet_transaction_data)

				if customer_wallet_transaction_count > 0:
					print('hii')
				else:
					get_general_loyality_query = ("""SELECT `signup_point`
									FROM `general_loyalty_master` WHERE `organisation_id` = %s""")
					getGeneralLoyalityData = (organisation_id)
					count_general_loyality = cursor_ecommerce.execute(get_general_loyality_query,getGeneralLoyalityData)
					general_loyality =  cursor_ecommerce.fetchone()

					get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s""")
					customer_wallet_data = (user_id)
					cursor_ecommerce.execute(get_customer_wallet_query,customer_wallet_data)
					wallet_data = cursor_ecommerce.fetchone()


					wallet = int(general_loyality['signup_point'])+wallet_data['wallet']
					transaction_id = 0
					redeem_history_id = 0

					insert_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
											`updated_value`,`transaction_id`,`redeem_history_id`,`organisation_id`,`status`,`last_update_id`)
														VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
					transaction_source = "signup"
					updated_value = wallet
					previous_value = wallet_data['wallet']
					wallet_transation_status = 1
					wallet_transaction_data = (user_id,general_loyality['signup_point'],transaction_source,previous_value,updated_value,transaction_id,redeem_history_id,organisation_id,wallet_transation_status,organisation_id)
					cursor_ecommerce.execute(insert_wallet_transaction_query,wallet_transaction_data)

					connection_ecommerce.commit()
			else:
				print('No Record Found')
		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_details",
				    "status": "success"
				},
				"responseList":customer_transaction_data}), status.HTTP_200_OK


#-----------------------get-Excel-Sheet-Data-For-Wallet---------------------#

@name_space.route("/getXcelsheetDataForWallet/<int:organisation_id>/<int:request_no>")	
class getXcelsheetDataForWallet(Resource):
	def get(self,organisation_id,request_no):
		connection = am_product_mysql_connection()
		cursor = connection.cursor()

		connection_ecommerce = mysql_connection()
		cursor_ecommerce = connection_ecommerce.cursor()		

		registration_type = 5
		organisation_id = organisation_id

		get_query = ("""SELECT *
			FROM `customer_transaction` where `request_no` = %s and `status` = 'done'""")
		get_data = (request_no)
		cursor.execute(get_query,get_data)

		customer_transaction_data = cursor.fetchall()

		for key,data in enumerate(customer_transaction_data):
			customer_transaction_data[key]['last_update_ts'] = str(data['last_update_ts'])

			get_phone_type_query = ("""SELECT *
					FROM `admins` WHERE `phoneno` = %s and `organisation_id` = %s and `registration_type` = %s""")
			get_phone_type_data = (data['mobile'],organisation_id,registration_type)

			count_phone_type = cursor_ecommerce.execute(get_phone_type_query,get_phone_type_data)

			if count_phone_type > 0:
				login_data = cursor_ecommerce.fetchone()
				user_id = login_data['admin_id']

				get_customer_wallet_transaction_query = ("""SELECT sum(`transaction_value`) as customer_wallet from `wallet_transaction` where `customer_id` = %s""")
				get_customer_wallet_transaction_data = (user_id)
				customer_wallet_transaction_count = cursor_ecommerce.execute(get_customer_wallet_transaction_query,get_customer_wallet_transaction_data)

				if customer_wallet_transaction_count > 0:
					customer_wallet = cursor_ecommerce.fetchone()
					update_customer_wallet_transaction_query = ("""UPDATE `admins` SET `wallet` = %s
										WHERE `admin_id` = %s""")
					update_customer_wallet_data = (customer_wallet['customer_wallet'],user_id)
					cursor_ecommerce.execute(update_customer_wallet_transaction_query,update_customer_wallet_data)
					print(cursor_ecommerce._last_executed)
				else:
					print('No Record Found')

				connection_ecommerce.commit()

			else:
				print('No Record Found')

		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_details",
				    "status": "success"
				},
				"responseList":customer_transaction_data}), status.HTTP_200_OK

#-----------------------get-Excel-Sheet-Data-For-Wallet---------------------#

#-----------------------get-Excel-Sheet-Data-For-Wallet---------------------#

@name_space.route("/getXcelsheetDataForWalletPurchase/<int:organisation_id>/<int:request_no>")	
class getXcelsheetDataForWalletPurchase(Resource):
	def get(self,organisation_id,request_no):
		connection = am_product_mysql_connection()
		cursor = connection.cursor()

		connection_ecommerce = mysql_connection()
		cursor_ecommerce = connection_ecommerce.cursor()		

		registration_type = 5
		organisation_id = organisation_id

		get_query = ("""SELECT *
			FROM `customer_transaction` where `request_no` = %s and `status` = 'done'""")
		get_data = (request_no)
		cursor.execute(get_query,get_data)

		customer_transaction_data = cursor.fetchall()

		for key,data in enumerate(customer_transaction_data):
			customer_transaction_data[key]['last_update_ts'] = str(data['last_update_ts'])

			get_phone_type_query = ("""SELECT *
					FROM `admins` WHERE `phoneno` = %s and `organisation_id` = %s and `registration_type` = %s and `wallet` = 100""")
			get_phone_type_data = (data['mobile'],organisation_id,registration_type)

			count_phone_type = cursor_ecommerce.execute(get_phone_type_query,get_phone_type_data)

			if count_phone_type > 0:
				login_data = cursor_ecommerce.fetchone()
				user_id = login_data['admin_id']

				insert_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
											`updated_value`,`transaction_id`,`redeem_history_id`,`organisation_id`,`status`,`last_update_id`)
														VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				transaction_source = "first_purchase_bonus"
				updated_value = 1100
				previous_value = 100
				wallet_transation_status = 1
				transaction_id = 0
				redeem_history_id = 0

				wallet_transaction_data = (user_id,1000,transaction_source,previous_value,updated_value,transaction_id,redeem_history_id,organisation_id,wallet_transation_status,organisation_id)
				cursor_ecommerce.execute(insert_wallet_transaction_query,wallet_transaction_data)

				print(cursor._last_executed)

				update_customer_wallet_transaction_query = ("""UPDATE `admins` SET `wallet` = %s
										WHERE `admin_id` = %s""")
				update_customer_wallet_data = (updated_value,user_id)
				cursor_ecommerce.execute(update_customer_wallet_transaction_query,update_customer_wallet_data)

				connection_ecommerce.commit()

			else:
				print('No Record Found')

		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_details",
				    "status": "success"
				},
				"responseList":customer_transaction_data}), status.HTTP_200_OK

#-----------------------get-Excel-Sheet-Data-For-Wallet---------------------#
