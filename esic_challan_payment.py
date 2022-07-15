from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json,render_template
from flask_api import status
from jinja2._compat import izip
from jinja2 import Environment, FileSystemLoader
from datetime import datetime,timedelta,date
import pymysql
from smtplib import SMTP
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
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

app = Flask(__name__)
cors = CORS(app)


#----------------------database-connection---------------------#

def mysql_connection():
	connection = pymysql.connect(host='dms-project.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='nIfnIEUwhlw0ZNQSpofJ',
	                             db='dms_project',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/dms_section/DmsSection/'
PAYMENT_BASE_URL = "http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/esi_payment/EsiPayment/"

#----------------------database-connection---------------------#

if __name__ == '__main__':
	connection = mysql_connection()
	cursor = connection.cursor()
	user_id = 6
	get_uploading_track_query = ("""SELECT * from `uploading_track` WHERE `last_update_id` = %s and `status` = 1""")
	get_uploading_track_data = (user_id)
	uploadin_track_count = cursor.execute(get_uploading_track_query,get_uploading_track_data)

	if uploadin_track_count > 0:
		uploading_track_data = cursor.fetchall()
		for key,data in enumerate(uploading_track_data):
			get_uploading_track_details_query = ("""SELECT * from `uploading_track_details` WHERE `request_no` = %s""")
			get_uploading_track_details_data = (data['request_no'])
			uploadin_track_details_count = cursor.execute(get_uploading_track_details_query,get_uploading_track_details_data)

			if uploadin_track_details_count > 0:
				uploading_track_details_data = cursor.fetchall()
				for uploading_track_details_key,uploading_track_details_data in enumerate(uploading_track_details_data):					

					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					checkKeyIsExsitsUrl = BASE_URL + "checkKeyIsExsits"
					checkKeyIsExsitsdata = {
							"job_id":uploading_track_details_data['job_id']
					}

					checkKeyIsExsits_response = requests.post(checkKeyIsExsitsUrl,data=json.dumps(checkKeyIsExsitsdata), headers=headers).json()

					if checkKeyIsExsits_response['responseList']['get_key'] == 1:	

						textfileheaders = {'Content-type':'application/json', 'Accept':'application/json'}
						createTextFileUrl = BASE_URL + "CreateTextFile"
						createTextFileData = {
								"request_no": data['request_no'],
								"documentName": uploading_track_details_data['s3_bucket_file_path'],
								"key": "textract_output/"+uploading_track_details_data['job_id']+"/1",
								"job_id": uploading_track_details_data['job_id']
						}

						createTextFile_response = requests.post(createTextFileUrl,data=json.dumps(createTextFileData), headers=textfileheaders).json()

						if uploading_track_details_data['uploading_data_into_database'] == 0:
							readfileheaders = {'Content-type':'application/json', 'Accept':'application/json'}
							readFileAndSaveData = {
									"request_no":data['request_no'],
									"documentName":uploading_track_details_data['s3_bucket_file_path'],
									"file_path":createTextFile_response['responseList']['text_file_path']
							}
							if data['content_type'] == 'challan':
								readFileAndSaveDataUrl = BASE_URL + "readFromFileDataAndSave"
							else:
								readFileAndSaveDataUrl = PAYMENT_BASE_URL + "readFromFileDataAndSave"
							readFileAndSaveData_response = requests.post(readFileAndSaveDataUrl,data=json.dumps(readFileAndSaveData), headers=readfileheaders).json()

							print(readFileAndSaveData_response)
						else:
							print('No Data Found')
					else:
						print('No Data Found')

			else:
				uploading_track_details_data = []
			
	else:
		uploading_track_data = []

	#print(uploading_track_data)
