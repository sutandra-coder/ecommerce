from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from database_connections import study_break
import requests
import calendar
import json
from threading import Thread
import time

app = Flask(__name__)
cors = CORS(app)

signup_section = Blueprint('studybreak_api', __name__)
api = Api(signup_section,  title='StudyBreak API',description='StudyBreak API')
name_space = api.namespace('StudyBreak',description='StudyBreak')


usersignup = api.model('usersignup', {
	"name":fields.String(),
	"user_role":fields.String(),
	"email_id":fields.String(),
	"phone_no":fields.Integer(),
	"password":fields.String(),
	"exam":fields.String(),
	"experience":fields.String(),
	"qualification":fields.String(),
	"videolink":fields.String()
    })

usersignin = api.model('usersignin', {
	"username":fields.String(),
	"password":fields.String()
	})


# BASE_URL = "http://ec2-18-191-151-105.us-east-2.compute.amazonaws.com/flaskapp/"

#---------------------------------------------------------------------------#
# @name_space.route("/SignUp")
# class SignUp(Resource):
# 	@api.expect(usersignup)
# 	def post(self):
# 		connection = connect_recess()
# 		cursor = connection.cursor()
# 		details = request.get_json()
		
# 		name = details.get('name')
# 		user_role = details.get('user_role')
# 		email_id = details.get('email_id')
# 		ph_no = details.get('phone_no')
# 		password = details.get('password')
# 		exam = details.get('exam')
# 		experience = details.get('experience')
# 		qualification = details.get('qualification')
# 		videolink = details.get('videolink')
			
# 		if len(name.split(" ")) < 2:
# 			first_name = name
# 			middle_name = ''
# 			last_name = ''
			
# 		elif len(name.split(" ")) == 2:
# 			parsed_name = name.split(" ", 1)
# 			first_name = parsed_name[0]
# 			middle_name = ''
# 			last_name = parsed_name[1]
			
# 		else:
# 			parsed_name = name.split(" ", 2)
# 			first_name = parsed_name[0]
# 			middle_name = parsed_name[1]
# 			last_name = parsed_name[2]
			
# 		cursor.execute("""SELECT `user_id`,CONCAT(first_name , ' ' , middle_name , ' ' , last_name)as name,
# 			`user_role`,`email_id`,`phone_no`,`password`,`exam` FROM 
# 			`user_credential` WHERE `phone_no`=%s or `email_id`=%s""",
# 			(ph_no,email_id))
# 		userCredentialDtls = cursor.fetchone()

# 		if userCredentialDtls == None:
# 			if user_role == 'T1':
# 				credential_query = ("""INSERT INTO `user_credential`(`first_name`, 
# 					`middle_name`, `last_name`, `user_role`,`flag`,`email_id`, `phone_no`, 
# 					`password`, `exam`,`experience`,`qualification`,`videolink`)VALUES 
# 					(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
# 				credential_data = (first_name,middle_name,last_name,user_role,'Pending',
# 					email_id,ph_no,password,exam,experience,qualification,videolink)
# 				credentialdata = cursor.execute(credential_query,credential_data)

# 				teacher_id = cursor.lastrowid
# 				details['user_id'] = teacher_id

# 			if user_role == 'S1':
# 				credential_query = ("""INSERT INTO `user_credential`(`first_name`, 
# 					`middle_name`, `last_name`, `user_role`,`flag`,`email_id`, `phone_no`, 
# 					`password`, `exam`,`experience`,`qualification`,`videolink`)VALUES 
# 					(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
# 				credential_data = (first_name,middle_name,last_name,user_role,'',
# 					email_id,ph_no,password,exam,experience,qualification,videolink)
# 				credentialdata = cursor.execute(credential_query,credential_data)

# 				student_id = cursor.lastrowid
# 				details['user_id'] = student_id

# 				wallet_query = ("""INSERT INTO `student_wallet`(student_id,
# 				    update_amount)VALUES (%s,%s)""")
# 				wallet_data = (student_id,3)
# 				walletdata = cursor.execute(wallet_query,wallet_data)

# 				transQuery = ("""INSERT INTO `student_wallet_transaction`(`student_id`,
# 					`previous_balance`,`added_balance`,`updated_balance`) VALUES (%s,
# 					%s,%s,%s)""")
				
# 				transData = cursor.execute(transQuery,(student_id,0,
# 					3,3))

# 			connection.commit()
# 			cursor.close()

# 			return ({"attributes": {"status_desc": "User Signup Details",
# 	                                "status": "success"
# 		                                },
# 		             "responseList": details}), status.HTTP_200_OK
# 		else:
# 			return ({"attributes": {"status_desc": "User Signup Details",
# 	                                "status": "not success"
# 		                                },
# 		             "responseList": "Already Registered Email Id Or Phone No"}), status.HTTP_200_OK

#--------------------------------------------------------#			
@name_space.route("/SignIn")
class Signin(Resource):
	@api.expect(usersignin)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		username = details.get('username')
		password = details.get('password')
		
		
		cursor.execute("""SELECT `user_id`,CONCAT(first_name, ' ' ,middle_name , ' ' ,last_name)as name,
			`user_role`,`email_id`,`phone_no`,username,`password`,
			imageurl,address,last_update_ts FROM `user_credential` WHERE 
			`username`=%s and `password`=%s""",(username,password))
		userCredentialDtls = cursor.fetchone()
		if userCredentialDtls:
			userCredentialDtls['last_update_ts'] = userCredentialDtls['last_update_ts'].isoformat()

			return ({"attributes": {
									"status_desc": "User Signin Details",
									"status": "success"
									},
			"responseList": userCredentialDtls}), status.HTTP_200_OK
	
		else:
			return ({"attributes": {
									"status_desc": "User Signin Details",
									"status": "success"
								},
				"responseList": "Invalid Username/Password"}), status.HTTP_200_OK

		