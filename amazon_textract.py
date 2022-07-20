from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import requests
import calendar
import json
import random
import json
import string
import smtplib
import imghdr
import io
import re
import math
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from PIL import Image, ImageFile
import PyPDF2 as pypdf
import pandas as pd
from textractcaller.t_call import call_textract
from textractprettyprinter.t_pretty_print import get_lines_string
import boto3
from botocore.config import Config
from pdf2image import convert_from_path

ACCESS_KEY =  'AKIATWWALMDJOK5DMPTP'
SECRET_KEY = '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'

app = Flask(__name__)
cors = CORS(app)

amazon_textract = Blueprint('amazon_textract', __name__)
api = Api(amazon_textract,  title='Amazon Textract',description='Amazon Textract')
name_space = api.namespace('AmazonTextract',description='Amazon Texttract')

upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)
UPLOAD_FOLDER = '/tmp'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

#----------------------Convert-Pdf-To-Image---------------------#
@name_space.route("/ConvertPdfToImage")	
class ConvertPdfToImage(Resource):
	def get(self):
		images = convert_from_path('HDFC-0997_FY-2020-21_NUPUR.pdf',500)
		print(images)

		#for i in range(len(images)):
			#images[i].save('page'+ str(i) +'.jpg', 'JPEG')
    		

#----------------------Convert-Pdf-To-Image---------------------#


#----------------------Upload-Image-To-s3-Bucket---------------------#


@name_space.route("/uploadToS3Bucket/<string:user_id>")
@name_space.expect(upload_parser)
class uploadToS3Bucket(Resource):
	def post(self,user_id):
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
			
		else:
			return {"attributes": {"status": "success"},
						"responseList": [],
						"responseDataTO": {}
					}

#----------------------Upload-Image-To-s3-Bucket---------------------#

#----------------------Get-Image-From-s3-Bucket---------------------#

@name_space.route("/getImage")	
class getImage(Resource):
	def get(self):
		s3BucketName = "dms-project-bucket"
		documentName = "28/051001107012162396_1610034392703_194J_AMMF_Non_company.pdf"

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

		#with open("sample.json", "w") as outfile:
			#outfile.write(json.dumps(response))
		

		#response = call_textract(input_document="s3://amazon-textract-public-content/blogs/Amazon-Textract-Pdf.pdf")
		#print(get_lines_string(response))


		

		return ({"attributes": {"status_desc": "delete_consumer_configuration",
								"status": "success"},
				"responseList": documnet_response}), status.HTTP_200_OK


#----------------------Get-Image-From-s3-Bucket---------------------#

#----------------------Read-File-From-s3-Bucket---------------------#

@name_space.route("/writeFileFromjson")	
class writeFileFromjson(Resource):
	def get(self):		

		ACCESS_KEY =  'AKIATWWALMDJOK5DMPTP'
		SECRET_KEY = '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'

		my_config = Config(
		    region_name = 'us-east-1'
		)

		client = boto3.client('s3',config=my_config,aws_access_key_id=ACCESS_KEY,
			aws_secret_access_key=SECRET_KEY)

		response = client.get_object(
		    Bucket='dms-project-bucket',
		    Key='textract_output/442dc864a204c523ae9c56dfbcaa011c29beff44198407915daddf23be056c2d/1',
		)

		data = response['Body'].read()
		data = json.loads(data)

		for key,filedata in enumerate(data['Blocks']):
			if filedata['BlockType'] == 'LINE':
				print(filedata['Text'])

				f = open("TDS-challan.txt", "a")
				f.write(filedata['Text'])
				f.write("\n")
				f.close()

		
		return ({"attributes": {"status_desc": "Read_File_From_txt",
								"status": "success"},
				"responseList":data['Blocks']}), status.HTTP_200_OK

@name_space.route("/readFromFile")	
class readFromFile(Resource):
	def get(self):
		f = open("esi-doc.txt","r+") 
		contribution_history_data_no = ""
		contribution_history_data_date = ""
		Total_IP_Contribution_data = ""
		Total_IP_Contribution_data_key = 0
		Total_Employer_Contribution_key = 0
		Total_Employer_Contribution_data = 0
		Total_Contribution_key = 0
		Total_Contribution_data = 0
		Total_Government_Contribution_key = 0
		Total_Government_Contribution_data = 0
		Total_Monthly_Wages_key = 0
		Total_Monthly_Wages_data = 0
		is_disable_key = 0
		is_disable_data = 0
		ip_number_key = 0
		ip_number_data = 0
		ip_name_data = 0
		ip_name_key = 0
		no_of_days_key = 0
		no_of_days_data = 0
		ip_contribution_key = 0
		ip_contribution_data = 0
		reason_key = 0
		reason_data = ""

		for x in range(1, 8):
			globals()[f"row_key_{x}"] = 0
			globals()[f"row_data_{x}"] = 0
	
		for key,data in enumerate(f):
			if "Contribution History Of" in data:
				contribution_history = data.split(" ")
				contribution_history_data_no = contribution_history[3]
				contribution_history_data_date = contribution_history[5]
			if "Total IP Contribution" in data:
				Total_IP_Contribution_data_key = key+5
			if Total_IP_Contribution_data_key == key:
				Total_IP_Contribution_data = data
			if "Total Employer Contribution" in data:
				Total_Employer_Contribution_key = key+5
			if 	Total_Employer_Contribution_key == key:
				Total_Employer_Contribution_data = data
			if "Total Contribution" in data:
				Total_Contribution_key = key+5
			if Total_Contribution_key == key:
				Total_Contribution_data = data
			if "Total Government Contribution" in data:
				Total_Government_Contribution_key = key+5
			if Total_Government_Contribution_key == key:
				Total_Government_Contribution_data = data
			if "Total Monthly Wages" in data:
				Total_Monthly_Wages_key = key+5
			if Total_Monthly_Wages_key == key:	
				Total_Monthly_Wages_data = data	



			if 	"SNo." in data:
				array = []
				srno_key = key


				
				for x in range(1, 8):
					globals()[f"row_key_{x}"] = srno_key+11+x						
			
			for x in range(1, 8):	
				if globals()[f"row_key_{x}"] == key:
					globals()[f"row_data_{x}"] = data
			

		print(row_data_1)
		print(row_data_2)	
		print(row_data_3)	
		print(row_data_4)
		print(row_data_5)		
		print(row_data_6)
		print(row_data_7)
						
		

#----------------------Read-File-From-s3-Bucket---------------------#

@name_space.route("/readFile")	
class readFile(Resource):
	def get(self):

		#s3 = boto3.client('s3')
		#data = s3.get_object(Bucket='textract-analysis', Key='textract_output/7edf87e582d400cf6064d7f544fd99807f3195f07ff4685dad600771f8ff4ce1/1',aws_access_key_id=ACCESS_KEY,
			#aws_secret_access_key=SECRET_KEY)
		#contents = data['Body'].read()
		#print(contents)

		s3BucketName = "textract-analysis"
		documentName = "textract_output/7edf87e582d400cf6064d7f544fd99807f3195f07ff4685dad600771f8ff4ce1/1.txt"

		my_config = Config(
		    region_name = 'us-east-2'
		)
		

		#textract = boto3.client('textract', config=my_config,aws_access_key_id=ACCESS_KEY,
			#aws_secret_access_key=SECRET_KEY)

		'''response = textract.detect_document_text(
		    Document={
		        'S3Object': {
		            'Bucket': s3BucketName,
		            'Name': documentName
		        }
		    }
		)'''



		#block_count = process_text_detection(s3BucketName,documentName)
		#print(block_count)

		client = boto3.client('s3',config=my_config,aws_access_key_id=ACCESS_KEY,
			aws_secret_access_key=SECRET_KEY)

		response1 = client.get_object(
		    Bucket='textract-analysis',
		    Key='textract_output/7edf87e582d400cf6064d7f544fd99807f3195f07ff4685dad600771f8ff4ce1/1',
		)

		data1 = response1['Body'].read()

		data1 = json.loads(data1)

		response2 = client.get_object(
		    Bucket='textract-analysis',
		    Key='textract_output/7edf87e582d400cf6064d7f544fd99807f3195f07ff4685dad600771f8ff4ce1/2',
		)

		data2 = response2['Body'].read()

		data2 = json.loads(data2)

		response3 = client.get_object(
		    Bucket='textract-analysis',
		    Key='textract_output/7edf87e582d400cf6064d7f544fd99807f3195f07ff4685dad600771f8ff4ce1/3',
		)

		data3 = response3['Body'].read()

		data3 = json.loads(data3)

		response4 = client.get_object(
		    Bucket='textract-analysis',
		    Key='textract_output/7edf87e582d400cf6064d7f544fd99807f3195f07ff4685dad600771f8ff4ce1/4',
		)

		data4 = response4['Body'].read()

		data4 = json.loads(data4)

		data1['Blocks'].extend(data2['Blocks'])
		data1['Blocks'].extend(data3['Blocks'])		
		data1['Blocks'].extend(data4['Blocks'])

		
		return ({"attributes": {"status_desc": "delete_consumer_configuration",
								"status": "success"},
				"responseList":data1['Blocks']}), status.HTTP_200_OK

@name_space.route("/readJsonFromPDF")	
class readJsonFromPDF(Resource):
	def get(self):	

		bucket = 'dms-project-bucket'
		document = '28/esi-doc.txt'
		#block_count=process_text_analysis(bucket,document)
		#print("Blocks detected: " + str(block_count))

		analyze_id('us-east-1',bucket,document)

		

def process_text_analysis(bucket, document):

    #Get the document from S3

    ACCESS_KEY = 'AKIATWWALMDJOK5DMPTP'
    SECRET_KEY = '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'

    my_config = Config(region_name = 'us-east-1')

    s3_connection = boto3.client('s3',config=my_config,aws_access_key_id=ACCESS_KEY,
			aws_secret_access_key=SECRET_KEY)

    s3_response = s3_connection.get_object(
		Bucket='dms-project-bucket',
		Key='textract_output/dfaad824ec1c46b94377da63cbb9887ec28245d76650eb9a99ca2050bbfd32ab/1',
	)   

    stream = io.BytesIO(s3_response['Body'].read())
    print(stream)
    image=Image.open(stream)

    # Analyze the document
    client = boto3.client('textract',config=my_config,aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
    
    image_binary = stream.getvalue()
    response = client.analyze_document(Document={'Bytes': image_binary},
        FeatureTypes=["TABLES", "FORMS"])

    ### Alternatively, process using S3 object ###
    #response = client.analyze_document(
    #    Document={'S3Object': {'Bucket': bucket, 'Name': document}},
    #    FeatureTypes=["TABLES", "FORMS"])

    ### To use a local file ###
    # with open("pathToFile", 'rb') as img_file:
        ### To display image using PIL ###
    #    image = Image.open()
        ### Read bytes ###
    #    img_bytes = img_file.read()
    #    response = client.analyze_document(Document={'Bytes': img_bytes}, FeatureTypes=["TABLES", "FORMS"])

    
    #Get the text blocks
    blocks=response['Blocks']
    width, height =image.size  
    draw = ImageDraw.Draw(image)  
    print ('Detected Document Text')
   
    # Create image showing bounding box/polygon the detected lines/text
    for block in blocks:

        DisplayBlockInformation(block)
             
        draw=ImageDraw.Draw(image)
        if block['BlockType'] == "KEY_VALUE_SET":
            if block['EntityTypes'][0] == "KEY":
                ShowBoundingBox(draw, block['Geometry']['BoundingBox'],width,height,'red')
            else:
                ShowBoundingBox(draw, block['Geometry']['BoundingBox'],width,height,'green')  
            
        if block['BlockType'] == 'TABLE':
            ShowBoundingBox(draw, block['Geometry']['BoundingBox'],width,height, 'blue')

        if block['BlockType'] == 'CELL':
            ShowBoundingBox(draw, block['Geometry']['BoundingBox'],width,height, 'yellow')
        if block['BlockType'] == 'SELECTION_ELEMENT':
            if block['SelectionStatus'] =='SELECTED':
                ShowSelectedElement(draw, block['Geometry']['BoundingBox'],width,height, 'blue')    
   
            #uncomment to draw polygon for all Blocks
            #points=[]
            #for polygon in block['Geometry']['Polygon']:
            #    points.append((width * polygon['X'], height * polygon['Y']))
            #draw.polygon((points), outline='blue')
            
    # Display the image
    image.show()
    return len(blocks) 
    

#----------------------Read-File-From-s3-Bucket---------------------#

def analyze_id(region, bucket_name, file_name):
	my_config = Config(
		    region_name = 'us-east-1'
	)
	textract_client = boto3.client('textract',config=my_config,aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
	response = textract_client.analyze_document(
	    Document={
	        'Bytes': b'bytes',
	        'S3Object': {
	            'Bucket': bucket_name,
	            'Name': file_name
	        }
	    },
	    FeatureTypes=[
        	'TABLES'
    	]
	)
	print(response)


@name_space.route("/readFromFileData")	
class readFromFileData(Resource):
	def get(self):
		inputFile = open("esi-doc.txt")
		

		# Looping through the file line by line
		#line = inputFile.readline()
		# print(line)
		# Flag Variables
		
		global lineNumber

		for fileLine in inputFile:
		    lineNumber = lineNumber+1

		    # Calling the function for Contribution History
		    if(contributionHistoryFlag == "N"):
		        contributionHistory(fileLine)
		    elif(firstTableFlag == "N"):
		        firstTableData(fileLine)
		    elif(secondTableFlag == "N"):
        		secondTableData(fileLine)

def firstTableData(fileLine):
    global firstTableLineOffset
    if("Total IP Contribution" in fileLine):
        print("starting First Table data" + str(lineNumber))
        global readingFirstTable
        readingFirstTable = "Y"
    if(readingFirstTable == "Y"):
        firstTableLineOffset = firstTableLineOffset+1
        if(firstTableLineOffset == 6):
            print("Total Ip Contribution" + str(fileLine[0:10]))
        elif(firstTableLineOffset == 7):
            print("Total employer Contribution" + str(fileLine[0:10]))
        elif(firstTableLineOffset == 10):
            print(fileLine)
            global firstTableFlag
            firstTableFlag = "Y"
            readingFirstTable = "N"


def secondTableData(fileLine):
    #    print(" In second table")
    global secondTableLineOffset
    global readingSecondTable
    global secondTableDataIgnore
#    print(str(secondTableLineOffset) + readingSecondTable)
    if("SNo." in fileLine):
        print("starting second Table data" + str(lineNumber))
        readingSecondTable = "Y"
    if(readingSecondTable == "Y"):
     #       print(" in the Y if")
        secondTableLineOffset = secondTableLineOffset+1
        if(secondTableLineOffset == 11):
            secondTableLineOffset = 0
            secondTableDataIgnore = "N"
            print("Start")
        if(secondTableLineOffset == 1 and secondTableDataIgnore == "N"):
            print("S.no" + fileLine)
        elif(secondTableLineOffset == 4 and secondTableDataIgnore == "N"):
            print("Name" + fileLine)
        elif(secondTableLineOffset == 8 and secondTableDataIgnore == "N"):
            print("End")
            secondTableLineOffset = 0

def contributionHistory(fileLine):
    #    print("line Number" + str(lineNumber))
    if("Contribution History Of" in fileLine):
        print("in the Contribution history for line number" + str(lineNumber))
# Changing the flag so that the code only runs once
        global contributionHistoryFlag
        contributionHistoryFlag = "Y"
#        print(fileLine)

        accountNumber = fileLine[24:38]
        month = fileLine[45:55]
        print("account Number" + str(accountNumber))
        print("month" + str(month))



		
