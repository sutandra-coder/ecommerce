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
from werkzeug.utils import secure_filename
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

esi_payment = Blueprint('esi_payment_api', __name__)
api = Api(esi_payment,  title='Dms API',description='DMS API')
name_space = api.namespace('EsiPayment',description='Dms Section')

#----------------------database-connection---------------------#

def mysql_connection():
	connection = pymysql.connect(host='dms-project.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='nIfnIEUwhlw0ZNQSpofJ',
	                             db='dms_project',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

read_from_file_and_save_postmodel = api.model('read_from_file_and_save_postmodel', {	
	"request_no":fields.Integer,
	"documentName":fields.String,
	"file_path":fields.String
})

#----------------------Read-From-Text-File-And-Save-Into-Database--------------------#

@name_space.route("/readFromFileDataAndSave")	
class readFromFileDataAndSave(Resource):
	@api.expect(read_from_file_and_save_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		inputFile = open(details['file_path'])
		request_no = details['request_no']
		documentName = details['documentName']

		file_name = documentName.split('/')
		uploading_file_name = file_name[1]

		get_query = ("""SELECT *
			FROM `uploading_track_details` WHERE `request_no` = %s and `uploadig_file_name` = %s""")
		getData = (details['request_no'],uploading_file_name)
		count_track_details = cursor.execute(get_query,getData)
		
		uploading_track_details = cursor.fetchone()		
		uploading_track_details_id = uploading_track_details['uploading_track_details_id']
		last_update_id = uploading_track_details['last_update_id']

		transaction_status = ""
		transaction_status_key = 0
		employeers_code_no_key = 0
		employeer_name_key = 0
		employeers_code_no = ""
		employeer_name = ""
		employeer_name_key = 0
		challan_period_key = 0
		challan_period = ""		
		challan_number_key = 0
		challan_number = ""
		challan_created_date_key = 0
		challan_created_date = ""
		challan_submited_date_key = 0
		challan_submited_date = ""
		amount_paid_key = 0
		amount_paid = ""
		transcation_number_key = 0
		transaction_number = ""


		for key,data in enumerate(inputFile):
			if "Transaction status:" in data:
				transaction_status_key = key+1
				employeers_code_no_key = key+3
				employeer_name_key = key+5
				challan_period_key = key+7
				challan_number_key = key+9
				challan_created_date_key = key+11
				challan_submited_date_key = key+13
				amount_paid_key = key+15
				transcation_number_key = key+17

			if transaction_status_key == key:
				transaction_status = data
			if employeers_code_no_key == key:
				employeers_code_no = data
			if employeer_name_key == key:
				employeer_name = data
			if challan_period_key == key:
				challan_period = data
			if challan_number_key == key:
				challan_number = data
			if challan_created_date_key == key:
				challan_created_date = data		
			if challan_submited_date_key == key:
				challan_submited_date = data
			if amount_paid_key == key:
				amount_paid = data
			if transcation_number_key == key:
				transaction_number = data

		print(transaction_status)
		print(employeers_code_no)
		print(employeer_name)
		print(challan_period)
		print(challan_number)	
		print(challan_created_date)	
		print(challan_submited_date)
		print(amount_paid)
		print(transaction_number)

		insert_query = ("""INSERT INTO `esic_payment`(`uploading_track_details_id`,`transaction_status`,`employers_code_no`,`employers_name`,`challan_period`,`challan_number`,`challan_created_date`,`challan_submited_date`,`amount_paid`,`transaction_number`,`last_update_id`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		data = (uploading_track_details_id,transaction_status,employeers_code_no,employeer_name,challan_period,challan_number,challan_created_date,challan_submited_date,amount_paid,transaction_number,last_update_id)
		cursor.execute(insert_query,data)
		print(cursor._last_executed)

		uploading_data_into_database = 1
		
		update_query = ("""UPDATE `uploading_track_details` SET `uploading_data_into_database` = %s WHERE `uploading_track_details_id` = %s""")
		update_data = (uploading_data_into_database,uploading_track_details_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()


		return ({"attributes": {
				    "status_desc": "esic_payment_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK


#----------------------Read-From-Text-File-And-Save-Into-Database--------------------#
			
