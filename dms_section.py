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

dms_section = Blueprint('dms_section_api', __name__)
api = Api(dms_section,  title='Dms API',description='DMS API')
name_space = api.namespace('DmsSection',description='Dms Section')

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

user_postmodel = api.model('SelectUser', {	
	"user_name":fields.String,
	"phoneno":fields.String,
	"password":fields.String
})

user_login_postmodel = api.model('SelectUserLogin', {	
	"phoneno":fields.String,
	"password":fields.String
})

UploadingTrack_postmodel = api.model('UploadingTrack', {	
	"uploading_file_count":fields.Integer,
	"file_type":fields.String,
	"content_type":fields.String,
	"last_update_id":fields.Integer
})

convertjson_postmodel = api.model('convertjson_postmodel', {
	"document_name":fields.String,
	"user_id":fields.Integer,
	"request_no":fields.Integer
})

create_text_postmodel = api.model('create_text_postmodel', {	
	"request_no":fields.Integer,
	"key":fields.String,
	"job_id":fields.String,
	"documentName":fields.String
})

read_from_file_and_save_postmodel = api.model('read_from_file_and_save_postmodel', {	
	"request_no":fields.Integer,
	"documentName":fields.String,
	"file_path":fields.String
})

key_postmodel = api.model('key_postmodel', {	
	"job_id":fields.String
})

esic_table_putmodel = api.model('esic_table_putmodel',{
	"is_disable":fields.String,
	"ip_number":fields.String,
	"ip_name":fields.String,
	"no_of_days":fields.String,
	"total_wages":fields.String,
	"ip_contribution":fields.String,
	"reason":fields.String
})

esic_basic_putmodel = api.model('esic_basic_putmodel',{
	"history_no":fields.String,
	"challan_date":fields.String,
	"total_ip_contribution":fields.String,
	"total_employee_contribution":fields.String,
	"total_contribution":fields.String,
	"total_goverment_contribution":fields.String,
	"total_month_wages":fields.String
})

esic_table_postmodel = api.model('esic_table_postmodel',{
	"esic_basic_data_id":fields.Integer,
	"is_disable":fields.String,
	"ip_number":fields.String,
	"ip_name":fields.String,
	"no_of_days":fields.String,
	"total_wages":fields.String,
	"ip_contribution":fields.String,
	"reason":fields.String,
	"user_id":fields.Integer
})

esic_payment_putmodel = api.model('esic_payment_putmodel',{
	"transaction_status":fields.String,
	"employers_code_no":fields.String,
	"employers_name":fields.String,
	"challan_period":fields.String,
	"challan_number":fields.String,
	"challan_created_date":fields.String,
	"challan_submited_date":fields.String,
	"amount_paid":fields.String,
	"transaction_number":fields.String
})



upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)
UPLOAD_FOLDER = '/tmp'

app = Flask(__name__)
cors = CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ACCESS_KEY =  'AKIATWWALMDJOK5DMPTP'
SECRET_KEY = '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'


contributionHistoryFlag = "N"
firstTableFlag = "N"
secondTableFlag = "N"
readingFirstTable = "N"
readingSecondTable = "N"
secondTableDataIgnore = "Y"


# Generic Variables
fileLine = ""
lineNumber = 0
firstTableLineOffset = 0
secondTableLineOffset = 0
secondTableDataIgnore = "Y"

#----------------------Add-User---------------------#

@name_space.route("/AddUser")
class AddUser(Resource):
	@api.expect(user_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		user_name = details['user_name']
		phoneno = details['phoneno']
		password = details['password']

		insert_query = ("""INSERT INTO `user`(`user_name`,`phoneno`,`password`) 
								VALUES(%s,%s,%s)""")
		data = (user_name,phoneno,password)
		cursor.execute(insert_query,data)
		print(cursor._last_executed)
		user_id = cursor.lastrowid	

		details['user_id'] = user_id

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "user_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK	

#----------------------Add-User---------------------#

#----------------------Login-User---------------------#

@name_space.route("/LoginUser")	
class LoginUser(Resource):
	@api.expect(user_login_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `user` WHERE `phoneno` = %s and `password` = %s""")
		getData = (details['phoneno'],details['password'])
		count_user = cursor.execute(get_query,getData)

		if count_user > 0:
			user_details = cursor.fetchone()
		else:
			user_details = {}

		return ({"attributes": {
				    "status_desc": "user_details",
				    "status": "success"
				},
				"responseList":user_details}), status.HTTP_200_OK

#----------------------Login-User---------------------#

@name_space.route("/UploadingTrack")
class UploadingTrack(Resource):
	@api.expect(UploadingTrack_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		uploading_file_count = details['uploading_file_count']
		file_type = details['file_type']
		content_type = details['content_type']
		last_update_id = details['last_update_id']
		uploading_track_status = 1

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		insert_query = ("""INSERT INTO `uploading_track`(`uploading_file_count`,`file_type`,`content_type`,`status`,`last_update_id`,`last_update_ts`) 
								VALUES(%s,%s,%s,%s,%s,%s)""")
		data = (uploading_file_count,file_type,content_type,uploading_track_status,last_update_id,date_of_creation)
		cursor.execute(insert_query,data)
		print(cursor._last_executed)
		request_no  = cursor.lastrowid	

		details['request_no'] = request_no

		connection.commit()
		cursor.close()


		return ({"attributes": {
				    "status_desc": "track_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK


#----------------------Upload-To-S3-Bucket---------------------#

@name_space.route("/uploadToS3Bucket/<string:user_id>/<int:request_no>")
@name_space.expect(upload_parser)
class uploadToS3Bucket(Resource):
	def post(self,user_id,request_no):
		connection = mysql_connection()
		cursor = connection.cursor()

		bucket_name = "dms-project-bucket"
		s3 = boto3.client(
			"s3",
			aws_access_key_id=ACCESS_KEY,
			aws_secret_access_key=SECRET_KEY
			)
		bucket_resource = s3
		uploadedfile = request.files['file']
		print(uploadedfile)
		filename = ''
		userKey = user_id+'/'
		fpath = ''
		FileSize = None
		if uploadedfile:
			filename = secure_filename(uploadedfile.filename)
			keyname = userKey+filename
			uploadRes = bucket_resource.upload_fileobj(
				Bucket = bucket_name,
				Fileobj=uploadedfile,
				Key=keyname)
			print(uploadRes)
			# result = bucket_resource.list_objects(Bucket=bucket_name, Prefix=userKey)
			# absfilepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
			# # print(absfilepath)
			# uploadedfile.save(absfilepath)
			# 
			# uploadReq = (filename,absfilepath,keyname)
			# thread_a = Compute(uploadReq,'uploadToS3Bucket')
			# thread_a.start()

			file_type = filename.split('.')
			uploading_file_type = file_type[1]

			now = datetime.now()
			date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

			s3_bucket_file_path = user_id+"/"+filename

			insert_query = ("""INSERT INTO `uploading_track_details`(`request_no`,`uploadig_file_name`,`uploading_file_type`,`uploading_into_s3_bucket`,`s3_bucket_file_path`,`last_update_id`,`last_update_ts`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s)""")
			uploading_into_s3_bucket = 1
			data = (request_no,filename,uploading_file_type,uploading_into_s3_bucket,s3_bucket_file_path,user_id,date_of_creation)
			cursor.execute(insert_query,data)
			
			connection.commit()
			cursor.close()

			return {"attributes": {"status": "success"},
				"responseList": [{
				  "FileName": filename,
				  "FileSize": FileSize,
				  "FilePath": user_id+"/"+filename,
				  "request_no": request_no
				  }],
				"responseDataTO": {}
				}
		else:
			return {"attributes": {"status": "success"},
						"responseList": [],
						"responseDataTO": {}
					}

#----------------------Upload-To-S3-Bucket---------------------#

#----------------------Convert-Json-from-Uploading-File---------------------#

@name_space.route("/ConvetJsonFromUploadinFile")	
class ConvetJsonFromUploadinFile(Resource):
	@api.expect(convertjson_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		s3BucketName = "dms-project-bucket"
		documentName = details['document_name']
		request_no = details['request_no']

		file_name = documentName.split('/')
		uploading_file_name = file_name[1]

		my_config = Config(
		    region_name = 'us-east-1'
		)
		

		textract = boto3.client('textract', config=my_config,aws_access_key_id=ACCESS_KEY,
			aws_secret_access_key=SECRET_KEY)

		print(textract)

		# Amazon Textract client


		# Call Amazon Textract
		response = textract.start_document_text_detection(
		    DocumentLocation={
		        'S3Object': {
		            'Bucket': s3BucketName,
		            'Name': documentName
		        }
		    },
		    NotificationChannel={
		        'SNSTopicArn': 'arn:aws:sns:us-east-1:732633173404:textract.fifo',
		        'RoleArn': 'arn:aws:iam::732633173404:role/@textract'
		    },
		    OutputConfig = { 
		      "S3Bucket": s3BucketName
		   }
		)
		print(response['JobId'])
		documnet_response = textract.get_document_text_detection(
			JobId=response['JobId'],
		    MaxResults=123
		)

		get_query = ("""SELECT *
			FROM `uploading_track_details` WHERE `request_no` = %s and `uploadig_file_name` = %s""")
		getData = (details['request_no'],uploading_file_name)
		count_track_details = cursor.execute(get_query,getData)

		if count_track_details > 0:
			converting_json_from_upoading_file = 1
			update_query = ("""UPDATE `uploading_track_details` SET `converting_json_from_upoading_file` = %s, `job_id` = %s
					WHERE `request_no` = %s and `uploadig_file_name` = %s""")
			update_data = (converting_json_from_upoading_file,response['JobId'],request_no,uploading_file_name)
			cursor.execute(update_query,update_data)

		key = "textract_output/"+response['JobId']+"/1"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Convert-Json-from-Uploading-File",
								"status": "success"},
				"responseList": {"key":key,"documentName":documentName,"request_no":request_no,"JobId":response['JobId']}}), status.HTTP_200_OK

#----------------------Convert-Json-from-Uploading-File---------------------#


#----------------------Check-key-Is-Exsits--------------------#

@name_space.route("/checkKeyIsExsits")	
class checkKeyIsExsits(Resource):
	@api.expect(key_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		job_id = details['job_id']

		key = "textract_output/"+str(job_id)+"/1"

		s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

		result = s3_client.list_objects_v2(Bucket='dms-project-bucket', Prefix=key)

		if 'Contents' in result:
			get_key = 1
			update_query = ("""UPDATE `uploading_track_details` SET `get_key` = %s
					WHERE `job_id` = %s """)
			update_data = (get_key,job_id)
			cursor.execute(update_query,update_data)

			connection.commit()
			cursor.close()
			details['get_key'] = 1

			return ({"attributes": {
				    "status_desc": "track_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

		else:		
			details['get_key'] = 0
			return ({"attributes": {
				    "status_desc": "track_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK		


#----------------------Check-key-Is-Exsits--------------------#

#----------------------Create-Text-File---------------------#

@name_space.route("/CreateTextFile")	
class CreateTextFile(Resource):
	@api.expect(create_text_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		request_no  = details['request_no']
		documentName = details['documentName']		

		file_name = documentName.split('/')
		uploading_file_name = file_name[1]

		uploading_file = uploading_file_name.split('.')

		key = details['key']
		job_id = details['job_id']

		get_job_status_query = ("""SELECT *
				FROM `uploading_track_details` WHERE `job_id` = %s""")
		get_job_status_data = (job_id)
		job_status_count = cursor.execute(get_job_status_query,get_job_status_data)

		job_status = cursor.fetchone()

		if job_status['get_key'] == 1:
			my_config = Config(
			    region_name = 'us-east-1'
			)

			client = boto3.client('s3',config=my_config,aws_access_key_id=ACCESS_KEY,
				aws_secret_access_key=SECRET_KEY)

			response = client.get_object(
			    Bucket='dms-project-bucket',
			    Key= key,
			)

			data = response['Body'].read()
			data = json.loads(data)

			for key,filedata in enumerate(data['Blocks']):
				if filedata['BlockType'] == 'LINE':
					f = open("/home/ubuntu/flaskapp/dms-project/"+uploading_file[0]+".txt", "a")
					#f = open(uploading_file[0]+".txt", "a")
					content = str(filedata['Text'].encode('utf-8'))
					split_main_content = content.split('\'')
					main_content = split_main_content[1]
					f.write(main_content)
					f.write("\n")
					f.close()

			get_query = ("""SELECT *
				FROM `uploading_track_details` WHERE `request_no` = %s and `uploadig_file_name` = %s""")
			getData = (details['request_no'],uploading_file_name)
			count_track_details = cursor.execute(get_query,getData)
			print(cursor._last_executed)

			if count_track_details > 0:
				create_text_file = 1
				update_query = ("""UPDATE `uploading_track_details` SET `create_text_file` = %s
						WHERE `request_no` = %s and `uploadig_file_name` = %s""")
				update_data = (create_text_file,request_no,uploading_file_name)
				cursor.execute(update_query,update_data)

				print(cursor._last_executed)

			connection.commit()
			cursor.close()

			text_file_path = "/home/ubuntu/flaskapp/dms-project/"+uploading_file[0]+".txt"
			#text_file_path = uploading_file[0]+".txt"

			return ({"attributes": {"status_desc": "create_text_file",
									"status": "success"},
					"responseList":{"text_file_path":text_file_path,"request_no":request_no,"documentName":documentName}}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "create_text_file",
											"status": "success"},
							"responseList":{"text_file_path":"","request_no":request_no,"documentName":documentName}}), status.HTTP_200_OK

#----------------------Create-Text-File---------------------#


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
		print(uploading_track_details)
		uploading_track_details_id = uploading_track_details['uploading_track_details_id']
		last_update_id = uploading_track_details['last_update_id']
		

		# Looping through the file line by line
		#line = inputFile.readline()
		# print(line)
		# Flag Variables

		is_disable = "" 
		ip_number = "" 
		ip_name = "" 
		no_of_days = ""
		total_wages = ""
		ip_contribution = ""
		reason = ""
		total_ip_contribution = ""
		employer_contribution = ""
		total_contribution = ""
		total_goverment_contribution = ""
		total_monthly_wagees = ""

		global lineNumber

		for fileLine in inputFile:
		    lineNumber = lineNumber+1

		    # Calling the function for Contribution History
		    if(contributionHistoryFlag == "N"):
		        contributionHistory(fileLine,uploading_track_details_id,last_update_id)
		    elif(firstTableFlag == "N"):
		        firstTableData(fileLine,uploading_track_details_id,last_update_id)
		    elif(secondTableFlag == "N"):
        		secondTableData(fileLine,uploading_track_details_id,last_update_id)

		return ({"attributes": {"status_desc": "Read_File_From_txt",
								"status": "success"},
				"responseList":details}), status.HTTP_200_OK


def firstTableData(fileLine,uploading_track_details_id,last_update_id):
    global firstTableLineOffset
    if("Total IP Contribution" in fileLine):
        print("starting First Table data" + str(lineNumber))
        global readingFirstTable
        readingFirstTable = "Y"
    global total_ip_contribution
    global employer_contribution
    global total_contribution
    global total_goverment_contribution
    global total_monthly_wagees

    connection = mysql_connection()
    cursor = connection.cursor()

    get_query = ("""SELECT *
			FROM `esic_basic_data` WHERE `uploading_track_details_id` = %s""")
    getData = (uploading_track_details_id)
    esi_basic_data_count = cursor.execute(get_query,getData)
    esi_basic_data = cursor.fetchone()
    esic_basic_data_id = esi_basic_data['esic_basic_data_id']

    if(readingFirstTable == "Y"):
        firstTableLineOffset = firstTableLineOffset+1
        if(firstTableLineOffset == 6):        	
        	total_ip_contribution = fileLine
        elif(firstTableLineOffset == 7):
        	employer_contribution = fileLine        	
        elif(firstTableLineOffset == 8):
        	total_contribution = fileLine
        elif(firstTableLineOffset == 9):
        	total_goverment_contribution = fileLine
        elif(firstTableLineOffset == 10):
            total_monthly_wagees = fileLine
            global firstTableFlag
            firstTableFlag = "Y"

            print(total_ip_contribution)
            print(employer_contribution)

            update_query = ("""UPDATE `esic_basic_data` SET `total_ip_contribution` = %s,`total_employee_contribution` = %s, 
        						`total_contribution` = %s, `total_goverment_contribution` = %s,`total_month_wages` = %s
													WHERE `esic_basic_data_id` = %s """)
            update_data = (total_ip_contribution,employer_contribution,total_contribution,total_goverment_contribution,total_monthly_wagees,esic_basic_data_id)
            cursor.execute(update_query,update_data)

            connection.commit()
            cursor.close()

            readingFirstTable = "N"


def secondTableData(fileLine,uploading_track_details_id,last_update_id):

    #    print(" In second table")
    global secondTableLineOffset
    global readingSecondTable
    global secondTableDataIgnore
    global secondTableFlag
#    print(str(secondTableLineOffset) + readingSecondTable)
    if("SNo." in fileLine):
        print("starting second Table data" + str(lineNumber))
        readingSecondTable = "Y"
    

    connection = mysql_connection()
    cursor = connection.cursor()

    get_query = ("""SELECT *
			FROM `esic_basic_data` WHERE `uploading_track_details_id` = %s""")
    getData = (uploading_track_details_id)
    esi_basic_data_count = cursor.execute(get_query,getData)
    esi_basic_data = cursor.fetchone()
    esic_basic_data_id = esi_basic_data['esic_basic_data_id']		

    global is_disable
    global ip_number
    global ip_name
    global no_of_days
    global total_wages
    global ip_contribution
    global reason

    if("Page of 1" in fileLine):
        secondTableFlag = "Y"

    if(readingSecondTable == "Y" and secondTableFlag == "N"):
     #       print(" in the Y if")
        secondTableLineOffset = secondTableLineOffset+1
        if(secondTableLineOffset == 11):
            secondTableLineOffset = 0
            secondTableDataIgnore = "N"            
        if(secondTableLineOffset == 2 and secondTableDataIgnore == "N"):
        	is_disable = fileLine
        	#print(is_disable)
        elif(secondTableLineOffset == 3 and secondTableDataIgnore == "N"):
        	ip_number = fileLine
        	#print(ip_number)
        elif(secondTableLineOffset == 4 and secondTableDataIgnore == "N"):
        	ip_name = fileLine  
        	#print(ip_name)
        elif(secondTableLineOffset == 5 and secondTableDataIgnore == "N"):
        	no_of_days = fileLine
        	#print(no_of_days)
        elif(secondTableLineOffset == 6 and secondTableDataIgnore == "N"):
        	total_wages = fileLine 
        	#print(total_wages)
        elif(secondTableLineOffset == 7 and secondTableDataIgnore == "N"):
        	ip_contribution = fileLine 
        	#print(ip_contribution)          

        elif(secondTableLineOffset == 8 and secondTableDataIgnore == "N"):
        	reason = fileLine
        	insert_query = ("""INSERT INTO `esic_table_data`(`esic_basic_data_id`,`is_disable`,`ip_number`,`ip_name`,`no_of_days`,`total_wages`,`ip_contribution`,`reason`,`last_update_id`) 
								VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
        	data = (esic_basic_data_id,is_disable,ip_number,ip_name,no_of_days,total_wages,ip_contribution,reason,last_update_id)
        	cursor.execute(insert_query,data)
        	

        	uploading_data_into_database = 1

        	update_query = ("""UPDATE `uploading_track_details` SET `uploading_data_into_database` = %s
						WHERE `uploading_track_details_id` = %s""")
        	update_data = (uploading_data_into_database,uploading_track_details_id)
        	cursor.execute(update_query,update_data)


        	print(cursor._last_executed)

        	connection.commit()
        	cursor.close()

        	secondTableLineOffset = 0       



def contributionHistory(fileLine,uploading_track_details_id,last_update_id):
    #    print("line Number" + str(lineNumber))
    if("Contribution History Of" in fileLine):
        print("in the Contribution history for line number" + str(lineNumber))
# Changing the flag so that the code only runs once
        global contributionHistoryFlag
        contributionHistoryFlag = "Y"
        connection = mysql_connection()
        cursor = connection.cursor()

        accountNumber = fileLine[24:38]
        month = fileLine[45:55]
        print("account Number" + str(accountNumber))
        print("month" + str(month))

        month = str(month)        

        insert_query = ("""INSERT INTO `esic_basic_data`(`history_no`,`challan_date`,`uploading_track_details_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s)""")
        data = (accountNumber,month,uploading_track_details_id,last_update_id)
        cursor.execute(insert_query,data)

        print(cursor._last_executed)

        connection.commit()
        cursor.close()




#----------------------Read-From-Text-File-And-Save-Into-Database--------------------#

#----------------------Uploading-Track-List--------------------#

@name_space.route("/UploadingTrackList/<int:user_id>/<string:start_date>/<string:end_date>/<string:content_type>")	
class UploadingTrackList(Resource):
	def get(self,user_id,start_date,end_date,content_type):
		connection = mysql_connection()
		cursor = connection.cursor()

		if start_date == 'NA' and end_date == 'NA' and content_type == 'NA':

			get_uploading_track_query = ("""SELECT ut.`request_no`,ut.`uploading_file_count`,ut.`file_type`,ut.`content_type`,ut.`status`,ut.`last_update_id`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts` from `uploading_track` ut WHERE `last_update_id` = %s and `status` = 1""")
			get_uploading_track_data = (user_id)
			uploadin_track_count = cursor.execute(get_uploading_track_query,get_uploading_track_data)

			if uploadin_track_count > 0:
				uploading_track_data = cursor.fetchall()
				for key,data in enumerate(uploading_track_data):				
					last_update_ts = data['last_update_ts'].strftime("%d-%m-%Y %H:%M:%S")
					uploading_track_data[key]['last_update_ts'] = last_update_ts
			else:
				uploading_track_data = []
		else:
			if content_type == 'NA':
				get_uploading_track_query = ("""SELECT ut.`request_no`,ut.`uploading_file_count`,ut.`file_type`,ut.`content_type`,ut.`status`,ut.`last_update_id`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts` from `uploading_track` ut WHERE `last_update_id` = %s and `status` = 1 
					and  date(ut.`last_update_ts`) >= %s and date(ut.`last_update_ts`) <= %s""")
				get_uploading_track_data = (user_id,start_date,end_date)
				uploadin_track_count = cursor.execute(get_uploading_track_query,get_uploading_track_data)

				if uploadin_track_count > 0:
					uploading_track_data = cursor.fetchall()
					for key,data in enumerate(uploading_track_data):				
						last_update_ts = data['last_update_ts'].strftime("%d-%m-%Y %H:%M:%S")
						uploading_track_data[key]['last_update_ts'] = last_update_ts
				else:
					uploading_track_data = []
			elif start_date == 'NA' and end_date == 'NA':
				get_uploading_track_query = ("""SELECT ut.`request_no`,ut.`uploading_file_count`,ut.`file_type`,ut.`content_type`,ut.`status`,ut.`last_update_id`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts` from `uploading_track` ut WHERE `last_update_id` = %s and `status` = 1 
					and  ut.`content_type` = %s""")
				get_uploading_track_data = (user_id,content_type)
				uploadin_track_count = cursor.execute(get_uploading_track_query,get_uploading_track_data)

				if uploadin_track_count > 0:
					uploading_track_data = cursor.fetchall()
					for key,data in enumerate(uploading_track_data):				
						last_update_ts = data['last_update_ts'].strftime("%d-%m-%Y %H:%M:%S")
						uploading_track_data[key]['last_update_ts'] = last_update_ts
				else:
					uploading_track_data = []
			else:
				get_uploading_track_query = ("""SELECT ut.`request_no`,ut.`uploading_file_count`,ut.`file_type`,ut.`content_type`,ut.`status`,ut.`last_update_id`,DATE_ADD(last_update_ts, INTERVAL 330 MINUTE) as `last_update_ts` from `uploading_track` ut WHERE `last_update_id` = %s and `status` = 1 
					and  date(ut.`last_update_ts`) >= %s and date(ut.`last_update_ts`) <= %s and `content_type` = %s""")
				get_uploading_track_data = (user_id,start_date,end_date,content_type)
				uploadin_track_count = cursor.execute(get_uploading_track_query,get_uploading_track_data)

				if uploadin_track_count > 0:
					uploading_track_data = cursor.fetchall()
					for key,data in enumerate(uploading_track_data):				
						last_update_ts = data['last_update_ts'].strftime("%d-%m-%Y %H:%M:%S")
						uploading_track_data[key]['last_update_ts'] = last_update_ts
				else:
					uploading_track_data = []

		return ({"attributes": {
			    		"status_desc": "uploading_track",
			    		"status": "success"
			    },
			    "responseList":uploading_track_data}), status.HTTP_200_OK	

#----------------------Uploading-Track-List--------------------#

#----------------------Uploading-Track-Details-List--------------------#

@name_space.route("/UploadingTrackDetailsList/<int:request_no>")	
class UploadingTrackDetailsList(Resource):
	def get(self,request_no):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_uploading_track_query = ("""SELECT * from `uploading_track` WHERE `request_no` = %s""")
		get_uploading_track_data = (request_no)
		uploading_track_count = cursor.execute(get_uploading_track_query,get_uploading_track_data)

		if uploading_track_count > 0:
			uploadin_track = cursor.fetchone()
			content_type = uploadin_track['content_type']
		else:
			content_type = 0

		get_uploading_track_details_query = ("""SELECT * from `uploading_track_details` WHERE `request_no` = %s""")
		get_uploading_track_details_data = (request_no)
		uploadin_track_details_count = cursor.execute(get_uploading_track_details_query,get_uploading_track_details_data)

		if uploadin_track_details_count > 0:
			uploading_track_details_data = cursor.fetchall()
			for key,data in enumerate(uploading_track_details_data):
				uploading_track_details_data[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			uploading_track_details_data = []

		return ({"attributes": {
			    		"status_desc": "uploading_track_details",
			    		"status": "success",
			    		"content_type":content_type
			    },
			    "responseList":uploading_track_details_data}), status.HTTP_200_OK	

#----------------------Uploading-Track-Details-List--------------------#

#----------------------Esic-Details--------------------#

@name_space.route("/esicDetails/<int:uploading_track_details_id>")	
class esicDetails(Resource):
	def get(self,uploading_track_details_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_esic_basic_details_query = ("""SELECT * from `esic_basic_data` WHERE `uploading_track_details_id` = %s""")
		get_esic_basic_details_data = (uploading_track_details_id)
		esic_basic_details_count = cursor.execute(get_esic_basic_details_query,get_esic_basic_details_data)

		if esic_basic_details_count > 0:
			esic_basic_details = cursor.fetchone()
			esic_basic_details['last_update_ts'] = str(esic_basic_details['last_update_ts'])
			get_esic_table_details_quey = ("""SELECT * from `esic_table_data` WHERE `esic_basic_data_id` = %s""")
			get_esic_table_details_data = (esic_basic_details['esic_basic_data_id'])
			get_esic_table_details_count = cursor.execute(get_esic_table_details_quey,get_esic_table_details_data)

			if get_esic_table_details_count > 0:
				esic_table_data = cursor.fetchall()
				for key,data in enumerate(esic_table_data):
					esic_table_data[key]['last_update_ts'] = str(esic_table_data[key]['last_update_ts'])
				esic_basic_details['esic_table_data'] = esic_table_data
			else:
				esic_basic_details['esic_table_data'] = []
		else:
			esic_basic_details = {}

		return ({"attributes": {
			    		"status_desc": "uploading_track_details",
			    		"status": "success"
			    },
			    "responseList":esic_basic_details}), status.HTTP_200_OK


#----------------------Esic-Details--------------------#

#----------------------Esic-Payment-Details--------------------#

@name_space.route("/esicPaymnetDetails/<int:uploading_track_details_id>")	
class esicPaymnetDetails(Resource):
	def get(self,uploading_track_details_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_esic_payment_details_query = ("""SELECT * from `esic_payment` WHERE `uploading_track_details_id` = %s""")
		get_esic_payment_details_data = (uploading_track_details_id)
		get_esic_payment_details_count = cursor.execute(get_esic_payment_details_query,get_esic_payment_details_data)

		if get_esic_payment_details_count > 0:
			esic_payment_details_data = cursor.fetchone()
			esic_payment_details_data['last_update_ts'] = str(esic_payment_details_data['last_update_ts'])
		else:
			esic_payment_details_data = {}

		return ({"attributes": {
			    		"status_desc": "esic_payment_details",
			    		"status": "success"
			    },
			    "responseList":esic_payment_details_data}), status.HTTP_200_OK
			    	
#----------------------Esic-Payment-Details--------------------#

#----------------------Esic-Table-Details--------------------#

@name_space.route("/esicTableDetails/<int:esic_table_data_id>")	
class esicTableDetails(Resource):
	def get(self,esic_table_data_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_esic_table_query = ("""SELECT * from `esic_table_data` WHERE `esic_table_data_id` = %s""")
		get_esic_table_data = (esic_table_data_id)
		get_esic_table_details_count = cursor.execute(get_esic_table_query,get_esic_table_data)

		if get_esic_table_details_count > 0:
			esic_table_details_data = cursor.fetchone()
			esic_table_details_data['last_update_ts'] = str(esic_table_details_data['last_update_ts'])
		else:
			esic_table_details_data = {}

		return ({"attributes": {
			    		"status_desc": "esic_table_details",
			    		"status": "success"
			    },
			    "responseList":esic_table_details_data}), status.HTTP_200_OK

#----------------------Esic-Table-Details--------------------#

#----------------------Uploading-Track--------------------#

@name_space.route("/uploadingTrackByUploadingTrackDetailsId/<int:uploading_track_details_id>")	
class uploadingTrackByUploadingTrackDetailsId(Resource):
	def get(self,uploading_track_details_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_uploading_track_details_query = ("""SELECT * from `uploading_track_details` WHERE `uploading_track_details_id` = %s""")
		get_uploading_track_details_data = (uploading_track_details_id)
		get_uploading_track_details_count = cursor.execute(get_uploading_track_details_query,get_uploading_track_details_data)

		if get_uploading_track_details_count > 0:
			uploading_track_details_data = cursor.fetchone()

			get_uploading_track_query = ("""SELECT * from `uploading_track` WHERE `request_no` = %s""")
			get_uploading_track_data = (uploading_track_details_data['request_no'])
			get_uploading_track_data_count = cursor.execute(get_uploading_track_query,get_uploading_track_data)

			if get_uploading_track_data_count > 0:
				uploading_track_data = cursor.fetchone()
				uploading_track_data['last_update_ts'] = str(uploading_track_data['last_update_ts'])
			else:
				uploading_track_data = {}

		else:
			uploading_track_data = {}

		return ({"attributes": {
			    		"status_desc": "uploading_track_details",
			    		"status": "success"
			    },
			    "responseList":uploading_track_data}), status.HTTP_200_OK

#----------------------Uploading-Track--------------------#

#----------------------Update-Esic-Table-Data---------------------#

@name_space.route("/updateEsicTableData/<int:esic_table_data_id>")
class updateEsicTableData(Resource):
	@api.expect(esic_table_putmodel)
	def put(self, esic_table_data_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "is_disable" in details:
			is_disable = details['is_disable']
			update_query = ("""UPDATE `esic_table_data` SET `is_disable` = %s
				WHERE `esic_table_data_id` = %s """)
			update_data = (is_disable,esic_table_data_id)
			cursor.execute(update_query,update_data)

		if details and "ip_number" in details:
			ip_number = details['ip_number']
			update_query = ("""UPDATE `esic_table_data` SET `ip_number` = %s
				WHERE `esic_table_data_id` = %s """)
			update_data = (ip_number,esic_table_data_id)
			cursor.execute(update_query,update_data)

		if details and "ip_number" in details:
			ip_name = details['ip_name']
			update_query = ("""UPDATE `esic_table_data` SET `ip_name` = %s
				WHERE `esic_table_data_id` = %s """)
			update_data = (ip_name,esic_table_data_id)
			cursor.execute(update_query,update_data)

		if details and "no_of_days" in details:
			no_of_days = details['no_of_days']
			update_query = ("""UPDATE `esic_table_data` SET `no_of_days` = %s
				WHERE `esic_table_data_id` = %s """)
			update_data = (no_of_days,esic_table_data_id)
			cursor.execute(update_query,update_data)

		if details and "total_wages" in details:
			total_wages = details['total_wages']
			update_query = ("""UPDATE `esic_table_data` SET `total_wages` = %s
				WHERE `esic_table_data_id` = %s """)
			update_data = (total_wages,esic_table_data_id)
			cursor.execute(update_query,update_data)

		if details and "ip_contribution" in details:
			ip_contribution = details['ip_contribution']
			update_query = ("""UPDATE `esic_table_data` SET `ip_contribution` = %s
				WHERE `esic_table_data_id` = %s """)
			update_data = (ip_contribution,esic_table_data_id)
			cursor.execute(update_query,update_data)

		if details and "reason" in details:
			reason = details['reason']
			update_query = ("""UPDATE `esic_table_data` SET `reason` = %s
				WHERE `esic_table_data_id` = %s """)
			update_data = (reason,esic_table_data_id)
			cursor.execute(update_query,update_data)

		get_esic_table_query = ("""SELECT * from `esic_table_data` WHERE `esic_table_data_id` = %s""")
		get_esic_table_data = (esic_table_data_id)
		get_esic_table_details_count = cursor.execute(get_esic_table_query,get_esic_table_data)

		if get_esic_table_details_count > 0:
			esic_table_details_data = cursor.fetchone()
			esic_table_details_data['last_update_ts'] = str(esic_table_details_data['last_update_ts'])
		else:
			esic_table_details_data = {}

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Esic Table Data",
								"status": "success"},
				"responseList": esic_table_details_data}), status.HTTP_200_OK

#----------------------Update-Esic-Table-Data---------------------#


#----------------------Update-Esic-Basic-Data---------------------#

@name_space.route("/updateEsicBasicData/<int:esic_basic_data_id>")
class updateEsicBasicData(Resource):
	@api.expect(esic_basic_putmodel)
	def put(self, esic_basic_data_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "history_no" in details:
			history_no = details['history_no']
			update_query = ("""UPDATE `esic_basic_data` SET `history_no` = %s
				WHERE `esic_basic_data_id` = %s """)
			update_data = (history_no,esic_basic_data_id)
			cursor.execute(update_query,update_data)

		if details and "challan_date" in details:
			challan_date = details['challan_date']
			update_query = ("""UPDATE `esic_basic_data` SET `challan_date` = %s
				WHERE `esic_basic_data_id` = %s """)
			update_data = (challan_date,esic_basic_data_id)
			cursor.execute(update_query,update_data)

		if details and "total_ip_contribution" in details:
			total_ip_contribution = details['total_ip_contribution']
			update_query = ("""UPDATE `esic_basic_data` SET `total_ip_contribution` = %s
				WHERE `esic_basic_data_id` = %s """)
			update_data = (total_ip_contribution,esic_basic_data_id)
			cursor.execute(update_query,update_data)

		if details and "total_employee_contribution" in details:
			total_employee_contribution = details['total_employee_contribution']
			update_query = ("""UPDATE `esic_basic_data` SET `total_employee_contribution` = %s
				WHERE `esic_basic_data_id` = %s """)
			update_data = (total_employee_contribution,esic_basic_data_id)
			cursor.execute(update_query,update_data)

		if details and "total_contribution" in details:
			total_contribution = details['total_contribution']
			update_query = ("""UPDATE `esic_basic_data` SET `total_contribution` = %s
				WHERE `esic_basic_data_id` = %s """)
			update_data = (total_contribution,esic_basic_data_id)
			cursor.execute(update_query,update_data)

		if details and "total_goverment_contribution" in details:
			total_goverment_contribution = details['total_goverment_contribution']
			update_query = ("""UPDATE `esic_basic_data` SET `total_goverment_contribution` = %s
				WHERE `esic_basic_data_id` = %s """)
			update_data = (total_goverment_contribution,esic_basic_data_id)
			cursor.execute(update_query,update_data)

		if details and "total_month_wages" in details:
			total_month_wages = details['total_month_wages']
			update_query = ("""UPDATE `esic_basic_data` SET `total_month_wages` = %s
				WHERE `esic_basic_data_id` = %s """)
			update_data = (total_month_wages,esic_basic_data_id)
			cursor.execute(update_query,update_data)

		get_esic_basic_query = ("""SELECT * from `esic_basic_data` WHERE `esic_basic_data_id` = %s""")
		get_esic_basic_data = (esic_basic_data_id)
		get_esic_basic_details_count = cursor.execute(get_esic_basic_query,get_esic_basic_data)

		if get_esic_basic_details_count > 0:
			esic_basic_details_data = cursor.fetchone()
			esic_basic_details_data['last_update_ts'] = str(esic_basic_details_data['last_update_ts'])
		else:
			esic_basic_details_data = {}

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Esic Basic Data Successfully",
								"status": "success"},
				"responseList": esic_basic_details_data}), status.HTTP_200_OK

#----------------------Update-Esic-Basic-Data---------------------#

#----------------------Update-Esic-Basic-Data---------------------#

@name_space.route("/updateEsicPaymentData/<int:esic_payment_id>")
class updateEsicPaymentData(Resource):
	@api.expect(esic_payment_putmodel)
	def put(self, esic_payment_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "transaction_status" in details:
			transaction_status = details['transaction_status']
			update_query = ("""UPDATE `esic_payment` SET `transaction_status` = %s
				WHERE `esic_payment_id` = %s """)
			update_data = (transaction_status,esic_payment_id)
			cursor.execute(update_query,update_data)

		if details and "employers_code_no" in details:
			employers_code_no = details['employers_code_no']
			update_query = ("""UPDATE `esic_payment` SET `employers_code_no` = %s
				WHERE `esic_payment_id` = %s """)
			update_data = (employers_code_no,esic_payment_id)
			cursor.execute(update_query,update_data)

		if details and "employers_name" in details:
			employers_name = details['employers_name']
			update_query = ("""UPDATE `esic_payment` SET `employers_name` = %s
				WHERE `esic_payment_id` = %s """)
			update_data = (employers_name,esic_payment_id)
			cursor.execute(update_query,update_data)

		if details and "challan_period" in details:
			challan_period = details['challan_period']
			update_query = ("""UPDATE `esic_payment` SET `challan_period` = %s
				WHERE `esic_payment_id` = %s """)
			update_data = (challan_period,esic_payment_id)
			cursor.execute(update_query,update_data)

		if details and "challan_number" in details:
			challan_number = details['challan_number']
			update_query = ("""UPDATE `esic_payment` SET `challan_number` = %s
				WHERE `esic_payment_id` = %s """)
			update_data = (challan_number,esic_payment_id)
			cursor.execute(update_query,update_data)

		if details and "challan_created_date" in details:
			challan_created_date = details['challan_created_date']
			update_query = ("""UPDATE `esic_payment` SET `challan_created_date` = %s
				WHERE `esic_payment_id` = %s """)
			update_data = (challan_created_date,esic_payment_id)
			cursor.execute(update_query,update_data)

		if details and "challan_submited_date" in details:
			challan_submited_date = details['challan_submited_date']
			update_query = ("""UPDATE `esic_payment` SET `challan_submited_date` = %s
				WHERE `esic_payment_id` = %s """)
			update_data = (challan_submited_date,esic_payment_id)
			cursor.execute(update_query,update_data)

		if details and "amount_paid" in details:
			amount_paid = details['amount_paid']
			update_query = ("""UPDATE `esic_payment` SET `amount_paid` = %s
				WHERE `esic_payment_id` = %s """)
			update_data = (amount_paid,esic_payment_id)
			cursor.execute(update_query,update_data)

		if details and "transaction_number" in details:
			transaction_number = details['transaction_number']
			update_query = ("""UPDATE `esic_payment` SET `transaction_number` = %s
				WHERE `esic_payment_id` = %s """)
			update_data = (transaction_number,esic_payment_id)
			cursor.execute(update_query,update_data)


		get_esic_payment_query = ("""SELECT * from `esic_payment` WHERE `esic_payment_id` = %s""")
		get_esic_payment_data = (esic_payment_id)
		get_esic_payment_details_count = cursor.execute(get_esic_payment_query,get_esic_payment_data)

		if get_esic_payment_details_count > 0:
			esic_paymengt_details_data = cursor.fetchone()
			esic_paymengt_details_data['last_update_ts'] = str(esic_paymengt_details_data['last_update_ts'])
		else:
			esic_paymengt_details_data = {}

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Esic Payment Data Successfully",
								"status": "success"},
				"responseList": esic_paymengt_details_data}), status.HTTP_200_OK

#----------------------Add-Esic-Table-Data---------------------#

@name_space.route("/AddEsicTableData")
class AddEsicTableData(Resource):
	@api.expect(esic_table_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		esic_basic_data_id = details['esic_basic_data_id']
		is_disable = details['is_disable']
		ip_number = details['ip_number']
		ip_name = details['ip_name']
		no_of_days = details['no_of_days']
		total_wages = details['total_wages']
		ip_contribution = details['ip_contribution']
		reason = details['reason']
		user_id = details['user_id']

		insert_query = ("""INSERT INTO `esic_table_data`(`esic_basic_data_id`,`is_disable`,`ip_number`,`ip_name`,`no_of_days`,`total_wages`,`ip_contribution`,`reason`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (esic_basic_data_id,is_disable,ip_number,ip_name,no_of_days,total_wages,ip_contribution,reason,user_id)
		cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Add Esic Table Data Successfully",
								"status": "success"},
				"responseList": details}), status.HTTP_200_OK

#----------------------Add-Esic-Table-Data---------------------#

#----------------------Delete-Esic-Table-Data--------------------#

@name_space.route("/deleteEsicTableData/<int:esic_table_data_id>/<int:esic_basic_data_id>")
class deleteEsicTableData(Resource):
	def delete(self, esic_table_data_id,esic_basic_data_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		delete_query = ("""DELETE FROM `esic_table_data` WHERE `esic_table_data_id` = %s""")
		delData = (esic_table_data_id)
		
		cursor.execute(delete_query,delData)		

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Delete Esic Table",
								"status": "success"},
				"responseList": {"esic_basic_data_id":esic_basic_data_id}}), status.HTTP_200_OK

#----------------------Delete-Esic-Table-Data--------------------#

#----------------------Delete-Uploading-Track-------------------#

@name_space.route("/deleteUploadingTrack/<int:request_no>")
class deleteUploadingTrack(Resource):
	def delete(self, request_no):
		connection = mysql_connection()
		cursor = connection.cursor()

		uploading_track_status = 0

		update_query = ("""UPDATE `uploading_track` SET `status` = %s WHERE `request_no` = %s""")
		update_data = (uploading_track_status,request_no)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "uploading_track_details",
				    "status": "success"
				},
				"responseList":"Deleted Successfuly"}), status.HTTP_200_OK

#----------------------Delete-Uploading-Track-------------------#

#----------------------Dms-Dashboard--------------------#

@name_space.route("/dmsDashboard/<int:user_id>")	
class dmsDashboard(Resource):
	def get(self,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		dashboard_data = {}

		get_esic_challan_count_query = ("""SELECT count(*) as total_challan_count from `uploading_track` WHERE `content_type` = 'challan' and status = 1 and `last_update_id` = %s""")
		get_esic_challan_count_data = (user_id)
		esic_challan_count = cursor.execute(get_esic_challan_count_query,get_esic_challan_count_data)

		if esic_challan_count > 0:
			esic_challan = cursor.fetchone()
			dashboard_data['esic_challan_couunt'] = esic_challan['total_challan_count']
		else:
			dashboard_data['esic_challan_couunt'] = 0

		get_esic_payment_count_query = ("""SELECT count(*) as total_payment_count from `uploading_track` WHERE `content_type` = 'payment' and status = 1 and `last_update_id` = %s""")
		get_esic_payment_count_data = (user_id)
		esic_payment_count = cursor.execute(get_esic_payment_count_query,get_esic_payment_count_data)

		if esic_payment_count > 0:
			esic_payment = cursor.fetchone()
			dashboard_data['total_payment_count'] = esic_payment['total_payment_count']
		else:
			dashboard_data['total_payment_count'] = 0

		return ({"attributes": {"status_desc": "Dashboard Data",
								"status": "success"},
				"responseList": dashboard_data}), status.HTTP_200_OK



#----------------------Dms-Dashboard--------------------#


