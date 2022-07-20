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
import random
import json
import string
import smtplib
import imghdr
import io
import re
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

app = Flask(__name__)
cors = CORS(app)

ecommerce_organisation_otp = Blueprint('ecommerce_organisation_otp_api', __name__)
api = Api(ecommerce_organisation_otp,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceOrganisationOtp',description='Ecommerce Organisation Otp')

app.config['CORS_HEADERS'] = 'Content-Type'

EMAIL_ADDRESS = 'communications@creamsonservices.com'
EMAIL_PASSWORD = 'CReam7789%$intELLi'
#----------------------------------------------------#
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

#-----------------------------------------------------#

ecommerce_otp = api.model('ecommerce_otp',{
	"USER_ID":fields.Integer(),
	"organisation_id":fields.Integer(),
	"role_id":fields.Integer(),
	"FIRST_NAME":fields.String(),
	"LAST_NAME":fields.String(),
	"MAIL_ID":fields.String(),
	"Address":fields.String(),
	"PHONE_NUMBER":fields.String()
	})

#------------------------------------------------------#
@name_space.route("/GenerateOTP")
class GenerateOTP(Resource):
	@api.expect(ecommerce_otp)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		USER_ID = details.get('USER_ID')
		organisation_id = details['organisation_id']
		role_id = details['role_id']
		FIRST_NAME = details.get('FIRST_NAME')
		LAST_NAME = details.get('LAST_NAME')
		MAIL_ID = details.get('MAIL_ID')
		Address = details.get('Address')
		PHONE_NUMBER = details['PHONE_NUMBER']
		
		if FIRST_NAME == '':
			FIRST_NAME = 'User'
		else:
			FIRST_NAME = FIRST_NAME

		def get_random_digits(stringLength=6):
		    Digits = string.digits
		    return ''.join((random.choice(Digits) for i in range(stringLength)))
		
		otp = get_random_digits()
			
		otp_query = ("""INSERT INTO `organisation_user_otp`(`USER_ID`,
			`organisation_id`,`OTP`,`role_id`,`FIRST_NAME`,`LAST_NAME`,
			`GENERATED_BY`, `MAIL_ID`, `Address`, `PHONE_NUMBER`)  
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		otpdata = cursor.execute(otp_query,(USER_ID,organisation_id,otp,role_id,
			FIRST_NAME,LAST_NAME,'System',MAIL_ID,Address,PHONE_NUMBER))

		if otpdata:
			details['OTP'] = otp 
			#----------------------------sms-----------------------#
			'''url = "http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?"
			user = 'creamsonintelli'
			password = 'denver@1234'
			msisdn = PHONE_NUMBER
			sid = 'CRMLTD'
			msg = 'Hi '+FIRST_NAME+' The OTP for the Online Transaction is '+otp+'. This OTP is valid only for one time use.'
			fl = '0'
			gwid = '2'
			payload ="user={}&password={}&msisdn={}&sid={}&msg={}&fl={}&gwid={}".format(user,password,
				msisdn,sid,msg,fl,gwid)
			postUrl = url+payload
			# print(msg)
			response = requests.request("POST", postUrl)

			if response.text == 'Failed#Invalid LoginThread was being aborted.':
				sent = 'N'
			else:	
				sms_response = json.loads(response.text)['ErrorMessage']
				# print(sms_response)
				res = {"status":sms_response}
				if res['status'] == 'Success':
					sent = 'Y'

					sms_query = ("""INSERT INTO `otp_sms`(`title`,`body`,
						`phone_number`,`Sent`,`organisation_id`)  
						VALUES(%s,%s,%s,%s,%s)""")
					smsdata = cursor.execute(sms_query,('OTP',msg,PHONE_NUMBER,
						'Yes',organisation_id))

				else:
					sent = 'N'			'''

			if PHONE_NUMBER == '9933077180':
				print('hello')
			else:
				url = "https://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage"
				userid = 2000207272
				password = '5thrMk8f4'
				msg = "This OTP is to Validate your mobile phone number is "+otp+". Please do not share your OTP with anyone else. -AM Mobile Telecom Pvt Ltd"
				payload ="&send_to={}&msg={}&msg_type=TEXT&userid={}&auth_scheme=plain&password={}&v=1.1&format=text".format(PHONE_NUMBER,msg,
					userid,password)
				postUrl = url+payload
				print(postUrl)
				# print(msg)
				response = requests.request("GET", postUrl)


				response_text = response.text

				if "error" in response_text:
					sent = 'N'
				else:
					
					sent = 'Y'

					sms_query = ("""INSERT INTO `otp_sms`(`title`,`body`,
							`phone_number`,`Sent`,`organisation_id`)  
							VALUES(%s,%s,%s,%s,%s)""")
					smsdata = cursor.execute(sms_query,('OTP',msg,PHONE_NUMBER,
							'Yes',organisation_id))		

			
			#----------------------------sms-----------------------#

			#----------------------------mail----------------------#
			cursor.execute("""SELECT `email` FROM `organisation_master` 
				WHERE `phoneno`=%s""",(PHONE_NUMBER))
			toMail = cursor.fetchone()

			if toMail == None:
				cursor.execute("""SELECT `email` FROM `admins` WHERE 
					`phoneno`=%s""",(PHONE_NUMBER))
				toMailcus = cursor.fetchone()
				if toMailcus:
					user_info = toMailcus['email']
				else:
					user_info = ''
			else:
				user_info = toMail['email']
			
			if user_info:
				msg = MIMEMultipart()
				msg['Subject'] = 'Verification code'
				msg['From'] = EMAIL_ADDRESS
				msg['To'] = user_info
				html = """<html>
	                        <head>
	                        <title>E-Commerce.com</title>
	                        </head>
	                        <body>
	                        <p>
	                        Dear User,<br> <br>
	                        
	                        Your OTP is %s. This OTP is valid only for one time use.<br><br>
				            
				            Thank you for choosing E-Commerce<br><br><br>
	                        
	                        
	                        
	                        E-Commerce Support Team<br>
	                          E-mail: - support@ecommerce.com<br>
	                          Website: www.ecommerce.com<br>
	                            
	                        </p    
                            </body>
	                        </html>"""
				message = html % (otp)
				# print(message)
				part1 = MIMEText(message, 'html')
				msg.attach(part1)
				try:
					smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
					smtp.starttls()
					smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
					smtp.sendmail(EMAIL_ADDRESS, user_info, msg.as_string())
					
					res = {"status":'Success'}
					sent = 'Y'
					print(sent)
					
				except Exception as e:
					res = {"status":'Failure'}
					sent = 'N'
					print(sent)
					# raise e
				smtp.quit()
			

		#----------------------------mail----------------------#

		else:
			details = []

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "ECommerce OTP",
	                                "status": "success"
	                                },
				"responseList":details}), status.HTTP_200_OK


