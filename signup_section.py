from flask import Flask, request, jsonify, json
from flask_api import status
import datetime
from datetime import datetime,timedelta,date
import pymysql
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
from database_connections import connect_logindb,connect_lab_lang1

app = Flask(__name__)
cors = CORS(app)

signup_section = Blueprint('signup_section_api', __name__)
api = Api(signup_section,  title='Career Modulo API',description='Career Modulo API')
name_space = api.namespace('SignUpController',description='Sign Up')

addUser = api.model('addUserDto', {
					"address": fields.String(),
					"city": fields.String(),
					"dateOfBirth": fields.String(),
					"emailId": fields.String(),
					"firstName": fields.String(),
					"gender": fields.String(),
					"institutionUserName": fields.String(),
					"institutionUserPassword": fields.String(),
					"institutionUserRole": fields.String(),
					"institutionUserStatus": fields.String(),
					"lastName": fields.String(),
					"middleName": fields.String(),
					"pincode": fields.String(),
					"primaryContactNumber": fields.String(),
					"secondaryContactNumber": fields.String(),
					"state": fields.String(),
					"streetAddress": fields.String(),
					"userEndDate": fields.String(),
					"userEnrollDate": fields.String(),
					"userTaxId": fields.String(),
					"userUniqueId": fields.String(),
					"board": fields.String(),
					"studentname": fields.String(),
					"class": fields.String(),
					"institutionName": fields.String(),
					"institutionId": fields.Integer(),
					"licenseKey": fields.String(),
					"fathers_Name":fields.String()
					})


newUser = api.model('newUserDto', {
					"address": fields.String(),
					"city": fields.String(),
					"dateOfBirth": fields.String(),
					"emailId": fields.String(),
					"firstName": fields.String(),
					"gender": fields.String(),
					"institutionUserName": fields.String(),
					"institutionUserPassword": fields.String(),
					"institutionUserRole": fields.String(),
					"institutionUserStatus": fields.String(),
					"lastName": fields.String(),
					"middleName": fields.String(),
					"pincode": fields.String(),
					"primaryContactNumber": fields.String(),
					"secondaryContactNumber": fields.String(),
					"state": fields.String(),
					"streetAddress": fields.String(),
					"userEndDate": fields.String(),
					"userEnrollDate": fields.String(),
					"userTaxId": fields.String(),
					"userUniqueId": fields.String(),
					"board": fields.String(),
					"studentname": fields.String(),
					"class": fields.String(),
					"institutionName": fields.String(),
					"institutionId": fields.Integer(),
					"licenseKey": fields.String(),
					"fathers_Name":fields.String(),
					"image_url":fields.String(),
					"occupation":fields.String(),
					"occupation_explain":fields.String(),
					"aadhaar_no":fields.String(),
					"front_aadhar_img":fields.String(),
					"back_aadhar_img":fields.String(),
					"school_last_studied":fields.String(),
					"college_last_studied":fields.String(),
					"currently_job_detailed":fields.String()
					})


updateUser = api.model('updateUserDto', {
					"address": fields.String(),
					"city": fields.String(),
					"dateOfBirth": fields.String(),
					"emailId": fields.String(),
					"firstName": fields.String(),
					"gender": fields.String(),
					"institutionUserName": fields.String(),
					"institutionUserPassword": fields.String(),
					"institutionUserRole": fields.String(),
					"institutionUserStatus": fields.String(),
					"lastName": fields.String(),
					"middleName": fields.String(),
					"pincode": fields.String(),
					"primaryContactNumber": fields.String(),
					"secondaryContactNumber": fields.String(),
					"state": fields.String(),
					"streetAddress": fields.String(),
					"userEndDate": fields.String(),
					"userEnrollDate": fields.String(),
					"userTaxId": fields.String(),
					"userUniqueId": fields.String(),
					"board": fields.String(),
					"studentname": fields.String(),
					"class": fields.String(),
					"institutionName": fields.String(),
					"institutionId": fields.Integer(),
					"licenseKey": fields.String(),
					"fathers_Name":fields.String(),
					"image_url":fields.String(),
					"user_id":fields.Integer(),
					"section":fields.String(),
					"studentrollnum":fields.String(),
					"student_type":fields.String(),
					"subscriptiontype":fields.String(),
					})

updateUserDtls = api.model('updateUserDtlsDto', {
					"address": fields.String(),
					"city": fields.String(),
					"dateOfBirth": fields.String(),
					"emailId": fields.String(),
					"firstName": fields.String(),
					"gender": fields.String(),
					"institutionUserName": fields.String(),
					"institutionUserPassword": fields.String(),
					"institutionUserRole": fields.String(),
					"institutionUserStatus": fields.String(),
					"lastName": fields.String(),
					"middleName": fields.String(),
					"pincode": fields.String(),
					"primaryContactNumber": fields.String(),
					"secondaryContactNumber": fields.String(),
					"state": fields.String(),
					"streetAddress": fields.String(),
					"userEndDate": fields.String(),
					"userEnrollDate": fields.String(),
					"userTaxId": fields.String(),
					"userUniqueId": fields.String(),
					"board": fields.String(),
					"studentname": fields.String(),
					"class": fields.String(),
					"institutionName": fields.String(),
					"institutionId": fields.Integer(),
					"licenseKey": fields.String(),
					"fathers_Name":fields.String(),
					"image_url":fields.String(),
					"user_id":fields.Integer(),
					"section":fields.String(),
					"studentrollnum":fields.String(),
					"student_type":fields.String(),
					"subscriptiontype":fields.String(),
					"occupation":fields.String(),
					"occupation_explain":fields.String(),
					"aadhaar_no":fields.String(),
					"front_aadhar_img":fields.String(),
					"back_aadhar_img":fields.String(),
					"school_last_studied":fields.String(),
					"college_last_studied":fields.String(),
					"currently_job_detailed":fields.String()
					})

validateUser = api.model('validateUserDto', {
					"institutionUserName": fields.String(),
					"institutionUserPassword": fields.String()
					})


udpate_password_model = api.model('udpate_password_model', {
					"reset": fields.Integer(),
					"institutionUserPassword": fields.String()
					})

institution_otp = api.model('institution_otp',{
	"USER_ID":fields.Integer(),
	"institution_id":fields.Integer(),
	"role_id":fields.String(),
	"FIRST_NAME":fields.String(),
	"LAST_NAME":fields.String(),
	"MAIL_ID":fields.String(),
	"Address":fields.String(),
	"PHONE_NUMBER":fields.String()
	})

forgot_psw = api.model('forgot_psw', {
			"username": fields.String()
			})

reset_psw = api.model('reset_psw', {
			"institutionUserName": fields.String(),
			"institutionUserPassword": fields.String()
			})

firebase_device_model = api.model('firebase_device_model',{
	"INSTITUTION_USER_ID":fields.Integer(),
	"Device_id":fields.String(),
	"Version_Desc":fields.String(),
	"Model_Id":fields.String(),
	"Last_updated_ID":fields.String()
	})

@name_space.route("/userRegistration")
class userRegistration(Resource):
	@api.expect(addUser)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		conn = connect_lab_lang1()
		curlang = conn.cursor()

		details = request.get_json()
		address = details.get('address')
		city = details.get('city')
		dateOfBirth = details.get('dateOfBirth')
		emailId = details.get('emailId')
		firstName = details.get('firstName')
		gender = details.get('gender')
		institutionUserName = details.get('institutionUserName')
		institutionUserPassword = details.get('institutionUserPassword')
		institutionUserRole = details.get('institutionUserRole')
		institutionUserStatus = details.get('institutionUserStatus')
		lastName = details.get('lastName')
		middleName = details.get('middleName')
		pincode = details.get('pincode')
		primaryContactNumber = details.get('primaryContactNumber')
		secondaryContactNumber = details.get('secondaryContactNumber')
		state = details.get('state')
		streetAddress = details.get('streetAddress')
		userTaxId = details.get('userTaxId')
		userUniqueId = details.get('userUniqueId')
		board = details.get('board')
		studentname = details.get('studentname')
		clss = details.get('class')
		institutionName = details.get('institutionName')
		institutionId = details.get('institutionId')
		licenseKey = details.get('licenseKey')
		fathers_Name = details.get('fathers_Name')

		current_date = date.today()
		userEnrollDate = str(current_date)
		nextyear_date = current_date.replace(year=current_date.year + 1)
		userEndDate = str(nextyear_date)

		msg = None

		res_dtls = {"STATUS": "",
					"user_id": 0,
					"RESPONSE": ""
					}

		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_NAME` = %s""",(details.get('institutionUserName')))


		useridDetails = cursor.fetchone()
		print(useridDetails)
		if institutionUserRole in ['S1','T1','TA','A1','G1']:
			if not useridDetails:

				res_dtls = {"STATUS": "User Added",
							"user_id": 0,
								"Response": {
								"status": "Success",
								"UserId": 0
								}
							}

				credentialInsertQuery = ("""INSERT INTO `institution_user_credential`(`CITY`, 
					`DATE_OF_BIRTH`, `EMAIL_ID`, `FIRST_NAME`, `GENDER`, 
					`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`, `LAST_NAME`, `MIDDLE_NAME`, 
					`PINCODE`, `PRIMARY_CONTACT_NUMBER`, `SECONDARY_CONTACT_NUMBER`, `STATE`, 
					`STREET_ADDRESS`, `USER_TAX_ID`, `USER_UNIQUE_ID`, 
					`address`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")


				credentialData = (city,dateOfBirth,emailId,firstName,gender,institutionUserName,institutionUserPassword,
					lastName,middleName,pincode,primaryContactNumber,secondaryContactNumber,state,streetAddress,
					userTaxId,userUniqueId,address)


				cursor.execute(credentialInsertQuery,credentialData)

				InstiUserID = cursor.lastrowid
				details['institution_user_id'] = InstiUserID

				res_dtls['user_id'] = InstiUserID
				res_dtls['Response']['UserId'] = InstiUserID

				credentialMasterQuery = ("""INSERT INTO `institution_user_credential_master`(`INSTITUTION_ID`, 
					`INSTITUTION_USER_ID`, `INSTITUTION_USER_ROLE`, `INSTITUTION_USER_STATUS`, 
					`INSTITUTION_NAME`, `USER_ENROLL_DATE`, 
					`USER_END_DATE`) VALUES (%s,%s,%s,%s,%s,%s,%s)""")


				masterData = (institutionId,InstiUserID,institutionUserRole,institutionUserStatus,institutionName,
					userEnrollDate,userEndDate)

				cursor.execute(credentialMasterQuery,masterData)

				lastUpdateTS = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
				curlang.execute("""INSERT INTO `student`(`Student_ID`, `Student_UserID`, `Class`, 
					`Level`, `Student_Addition_TS`, `Status`, `Last_Update_ID`, `Last_Update_TS`, 
					`Board`) VALUES 
					(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(InstiUserID,InstiUserID,clss,0,lastUpdateTS,
						0,None,lastUpdateTS,board))

				if institutionUserRole == 'S1':
					studentInsertQuery = ("""INSERT INTO `student_dtls`(`INSTITUTION_ID`, 
						`INSTITUTION_USER_ID_STUDENT`,`STUDENT_TYPE`, `CLASS`, 
						`CLASS_START_DATE`, `CLASS_END_DATE`,`STUDENT_NAME`, 
						`Fathers_Name`, `Board`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

					studentData = (institutionId,InstiUserID,'enable',clss,userEnrollDate,userEndDate,
						firstName+' '+lastName,fathers_Name,board)


					cursor.execute(studentInsertQuery,studentData)


				elif institutionUserRole == 'T1' or institutionUserRole == 'TA':

					teacherInsertQuery = ("""INSERT INTO `teacher_dtls`(`INSTITUTION_ID`, 
						`INSTITUTION_USER_ID_TEACHER`) VALUES (%s,%s)""")

					teacherData = (institutionId,InstiUserID)

					cursor.execute(teacherInsertQuery,teacherData)

				elif institutionUserRole == 'A1':
					adminInsertQuery = ("""INSERT INTO `admin_dtls`(`INSTITUTION_ID`, 
						`INSTITUTION_USER_ID_ADMIN`, `ADMIN_TYPE`) VALUES (%s,%s,%s)""")

					adminData = (institutionId,InstiUserID,'A1')

					cursor.execute(adminInsertQuery,adminData)

			else:
				msg = 'User Already exists'
				res_dtls = {"STATUS": "failure",
					"user_id": useridDetails['INSTITUTION_USER_ID'],
					"RESPONSE": msg
					}

		else:
			msg = 'Invalid user role'
			res_dtls = {"STATUS": "failure",
					"user_id": 0,
					"RESPONSE": msg
					}

		connection.commit()
		cursor.close()

		conn.commit()
		curlang.close()
		return ({"attributes": {"status_desc": "Registration Details",
								"status": "success"
								},
				"responseList": res_dtls}), status.HTTP_200_OK



@name_space.route("/ProfileUpdate")
class ProfileUpdate(Resource):
	@api.expect(updateUser)
	def put(self):

		connection = connect_logindb()
		cursor = connection.cursor()
		
		conn = connect_lab_lang1()
		curlang = conn.cursor()

		details = request.get_json()
		user_id = details.get('user_id')

		institutionId = details.get('institutionId')
		if institutionId is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(institutionId,user_id))
			connection.commit()
		address = details.get('address')
		if address is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `address` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(address,user_id))
		city = details.get('city')
		if city is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `CITY` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(city,user_id))
		dateOfBirth = details.get('dateOfBirth')
		if dateOfBirth is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `DATE_OF_BIRTH` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(dateOfBirth,user_id))
		emailId = details.get('emailId')
		if emailId is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `EMAIL_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(emailId,user_id))
		firstName = details.get('firstName')
		if firstName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `FIRST_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(firstName,user_id))
		gender = details.get('gender')
		if gender is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `GENDER` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(gender,user_id))
		institutionUserName = details.get('institutionUserName')
		if institutionUserName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `INSTITUTION_USER_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(institutionUserName,user_id))
		# institutionUserPassword = details.get('institutionUserPassword')
		# if institutionUserPassword is not None:
		# 	cursor.execute("""UPDATE `institution_user_credential` SET `INSTITUTION_USER_PASSWORD` = %s 
		# 		WHERE `INSTITUTION_USER_ID` = %s""",(institutionUserPassword,user_id))
		institutionUserRole = details.get('institutionUserRole')
		if institutionUserRole is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_USER_ROLE` = %s 
				where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionUserRole,
					institutionId,user_id))
		institutionUserStatus = details.get('institutionUserStatus')
		if institutionUserStatus is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_USER_STATUS` = %s 
				where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionUserStatus,
					institutionId,user_id))
		lastName = details.get('lastName')
		if lastName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `LAST_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(lastName,user_id))
		middleName = details.get('middleName')
		if middleName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `MIDDLE_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(middleName,user_id))
		pincode = details.get('pincode')
		if pincode is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `PINCODE` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(pincode,user_id))
		primaryContactNumber = details.get('primaryContactNumber')
		if primaryContactNumber is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `PRIMARY_CONTACT_NUMBER` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(primaryContactNumber,user_id))
		secondaryContactNumber = details.get('secondaryContactNumber')
		if secondaryContactNumber is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `SECONDARY_CONTACT_NUMBER` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(secondaryContactNumber,user_id))
		state = details.get('state')
		if state is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `STATE` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(state,user_id))
		streetAddress = details.get('streetAddress')
		if streetAddress is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `STREET_ADDRESS` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(streetAddress,user_id))
		userTaxId = details.get('userTaxId')
		if userTaxId is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `USER_TAX_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(userTaxId,user_id))
		userUniqueId = details.get('userUniqueId')
		if userUniqueId is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `USER_UNIQUE_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(userUniqueId,user_id))
		board = details.get('board')
		if board is not None:
			cursor.execute("""UPDATE `student_dtls` SET `Board` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(board,institutionId,user_id))
			curlang.execute("""UPDATE `student` SET `Board` = %s WHERE `Student_UserID` = %s""",(board,user_id))
		studentname = details.get('studentname')
		if studentname is not None:
			cursor.execute("""UPDATE `student_dtls` SET `STUDENT_NAME` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(studentname,institutionId,user_id))
		clss = details.get('class')
		if clss is not None:
			cursor.execute("""UPDATE `student_dtls` SET `CLASS` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(clss,institutionId,user_id))
			curlang.execute("""UPDATE `student` SET `Class` = %s WHERE `Student_UserID` = %s""",(clss,user_id))
		institutionName = details.get('institutionName')
		if institutionName is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_NAME` = %s 
				where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionName,
					institutionId,user_id))
		
		# licenseKey = details.get('licenseKey')
		# if licenseKey is not None:
		# 	cursor.execute("""UPDATE `institution_user_credential` SET `address` = %s 
		# 		WHERE `INSTITUTION_USER_ID` = %s""",(licenseKey,user_id))
		fathers_Name = details.get('fathers_Name')
		if fathers_Name is not None:
			cursor.execute("""UPDATE `student_dtls` SET `Fathers_Name` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(fathers_Name,institutionId,user_id))
		image_url = details.get('image_url')
		if image_url is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `IMAGE_URL` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(image_url,user_id))
			cursor.execute("""UPDATE `student_dtls` SET `Image_URL` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(image_url,institutionId,user_id))
		section = details.get('section')
		if section is not None:
			cursor.execute("""UPDATE `student_dtls` SET `SEC` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(section,institutionId,user_id))
		studentrollnum = details.get('studentrollnum')
		if studentrollnum is not None:
			cursor.execute("""UPDATE `student_dtls` SET `STUDENT_ROLL_NUM` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(studentrollnum,institutionId,user_id))
		student_type = details.get('student_type')
		if student_type is not None:
			cursor.execute("""UPDATE `student_dtls` SET `STUDENT_TYPE` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(student_type,institutionId,user_id))
		subscriptiontype = details.get('subscriptiontype')
		if subscriptiontype is not None:
			cursor.execute("""UPDATE `student_dtls` SET `SUBCRIPTION_TYPE` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(subscriptiontype,institutionId,user_id))
		
		connection.commit()
		conn.commit()
		cursor.close()
		curlang.close()

		return ({"attributes": {"status_desc": "Profile Update Details",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK



@name_space.route("/validateUserPassword")
class validateUserPassword(Resource):
	@api.expect(validateUser)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		details = request.get_json()
		username = details.get('institutionUserName')
		password = details.get('institutionUserPassword')
		userInstiDtls = []
		fullUserDtls = {}
		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` WHERE 
			`INSTITUTION_USER_NAME` = %s and `INSTITUTION_USER_PASSWORD` = %s""",(username,password))


		userDtls = cursor.fetchone()

		if not userDtls:
			msg = 'UserId/Password not validated'
		else:
			msg = 'User Exists and Pasword Validated'

			cursor.execute("""SELECT `CITY` as 'city',iuc.`DATE_OF_BIRTH` as 'dateOfBirth',iuc.`EMAIL_ID` as 'emailId',
			`FIRST_NAME` as 'firstName',`GENDER` as 'gender',iuc.`IMAGE_URL` as 'imageUrl',
			iuc.`INSTITUTION_USER_PASSWORD` as 'institutionUserPassword',`RESET` as 'reset',`LAST_NAME` as 'lastName',
			iuc.`LAST_UPDATE_ID` as 'lastUpdateId',iuc.`LAST_UPDATE_TIMESTAMP` as 'lastUpdateTimestamp',
			`MIDDLE_NAME` as 'middleName',`PINCODE` as 'pincode',iuc.`PRIMARY_CONTACT_NUMBER` as 'primaryContactNumber',
			`SECONDARY_CONTACT_NUMBER` as 'secondaryContactNumber',`STATE` as 'state',
			`STREET_ADDRESS` as 'streetAddress',`USER_TAX_ID` as 'userTaxId',occupation,occupation_explain,
			`USER_UNIQUE_ID` as 'userUniqueId',iuc.`address`,iuc.`INSTITUTION_USER_ID` as 'institutionUserId',
			iuc.`INSTITUTION_USER_NAME` as 'institutionUserName',aadhaar_no,front_aadhar_img,back_aadhar_img,
            school_last_studied,college_last_studied,currently_job_detailed
			FROM `creamson_logindb`.`institution_user_credential` iuc left join `institution_user_personal_details` iucp 
            on iuc.`INSTITUTION_USER_ID`=iucp.`institution_user_id` WHERE iuc.`INSTITUTION_USER_ID` =%s""",(userDtls.get('INSTITUTION_USER_ID')))

			fullUserDtls = cursor.fetchone()
			fullUserDtls['lastUpdateTimestamp'] = fullUserDtls['lastUpdateTimestamp'].isoformat()
			if isinstance(fullUserDtls['dateOfBirth'], date):
				fullUserDtls['dateOfBirth'] = fullUserDtls['dateOfBirth'].isoformat()
			fullUserDtls['institutionUserRoles'] = []

			if fullUserDtls['imageUrl'] == None:
				fullUserDtls['imageUrl'] = ""
			if fullUserDtls['occupation'] == None:
				fullUserDtls['occupation'] = ""
			if fullUserDtls['occupation_explain']== None:
				fullUserDtls['occupation_explain'] = ""
			if fullUserDtls['aadhaar_no'] == None:
				fullUserDtls['aadhaar_no'] = ""
			if fullUserDtls['front_aadhar_img']== None:
				fullUserDtls['front_aadhar_img'] = ""
			if fullUserDtls['back_aadhar_img'] == None:
				fullUserDtls['back_aadhar_img'] = ""
			if fullUserDtls['school_last_studied']== None:
				fullUserDtls['school_last_studied'] = ""
			if fullUserDtls['college_last_studied'] == None:
				fullUserDtls['college_last_studied'] = ""
			if fullUserDtls['currently_job_detailed']== None:
				fullUserDtls['currently_job_detailed'] = ""
			cursor.execute("""SELECT `INSTITUTION_ID` as 'institutionId',`INSTITUTION_USER_ROLE` as 'roleId',
				`INSTITUTION_NAME` as 'institutionName'	FROM `institution_user_credential_master` 
				WHERE `INSTITUTION_USER_ID` = %s""",(userDtls.get('INSTITUTION_USER_ID')))

			userInstiDtls = cursor.fetchall()

			for uid, insti in enumerate(userInstiDtls):
				if insti.get('roleId') == 'S1':
					print('if')
					cursor.execute("""SELECT `CLASS` as 'studentClass',`Fathers_Name` as 'fathersName',
						`Board` as 'board' FROM `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` = %s 
						and `INSTITUTION_ID` = %s""",(userDtls.get('INSTITUTION_USER_ID'),insti.get('institutionId')))
					studentdtls = cursor.fetchone()
					insti['studentClass'] = studentdtls.get('studentClass')
					insti['fathersName'] = studentdtls.get('fathersName')
					insti['board'] = studentdtls.get('board')
					insti['description'] = 'Student'
				elif insti.get('roleId') == 'TA':
					print('elif')
					cursor.execute("""SELECT `INSTITUTION_USER_ID_TEACHER` FROM `teacher_dtls` WHERE 
						`INSTITUTION_USER_ID_TEACHER` = %s 
						AND `INSTITUTION_ID` = %s""",(userDtls.get('INSTITUTION_USER_ID'),insti.get('institutionId')))
					
					teacherDtls = cursor.fetchone()
					insti['studentClass'] = None
					insti['fathersName'] = None
					insti['board'] = None
					insti['description'] = None
			fullUserDtls['institutionUserRoles'] = userInstiDtls
			fullUserDtls['avatar'] = None
		return ({"attributes": {"status_desc": msg,
								"student_details":fullUserDtls,
								"status": "success"
								},
				"responseDataTO": {}}), status.HTTP_200_OK


@name_space.route("/updatePassword/<int:user_id>")
class updatePassword(Resource):
	@api.expect(udpate_password_model)
	def put(self,user_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		details = request.get_json()
		# reset = details.get('reset')
		institutionUserPassword = details.get('institutionUserPassword')

		# cursor.execute("""SELECT `RESET` FROM `institution_user_credential` WHERE 
		# 	`INSTITUTION_USER_ID` = %s""",(user_id))

		# resetDtls = cursor.fetchone()

		# reset = int(resetDtls.get('RESET',0)) + 1

		cursor.execute("""UPDATE `institution_user_credential` SET `RESET` = %s, INSTITUTION_USER_PASSWORD = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(1,institutionUserPassword,user_id))

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Password Update Details",
								"status": "success"
								},
				"responseList": 'Password updated'}), status.HTTP_200_OK



@name_space.route("/InstitutionOTP")
class InstitutionOTP(Resource):
	@api.expect(institution_otp)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()
		
		USER_ID = details.get('USER_ID')
		institution_id = details['institution_id']
		role_id = details['role_id']
		FIRST_NAME = details.get('FIRST_NAME')
		LAST_NAME = details.get('LAST_NAME')
		MAIL_ID = details.get('MAIL_ID')
		Address = details.get('Address')
		PHONE_NUMBER = details['PHONE_NUMBER']
		
		name = FIRST_NAME + ' '+ LAST_NAME
		def get_random_digits(stringLength=6):
		    Digits = string.digits
		    return ''.join((random.choice(Digits) for i in range(stringLength)))
		
		otp = get_random_digits()
			
		otp_query = ("""INSERT INTO `institution_user_otp`(`INSTITUTION_USER_ID`,
			`INSTITUTION_ID`,`OTP`,`INSTITUTION_USER_ROLE`,`FIRST_NAME`,`LAST_NAME`,
			`GENERATED_BY`, `MAIL_ID`, `Address`, `PHONE_NUMBER`)  
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		otpdata = cursor.execute(otp_query,(USER_ID,institution_id,otp,role_id,
			FIRST_NAME,LAST_NAME,'System',MAIL_ID,Address,PHONE_NUMBER))

		if otpdata:
			details['OTP'] = otp 
			
			user_info = MAIL_ID
		
			sender = "careermoulders.dipak.singhal@gmail.com"
			recipient = user_info

			msg = MIMEMultipart('alternative')
			msg['Subject'] = "Verification Code"
			msg['From'] = sender
			msg['To'] = recipient

			
			html = """<html>
                    <head>
                    <title>careermoulders.dipak.singhal@gmail.com</title>
                    </head>
                    <body>
                    <p>
                    Dear %s,<br><br> 
                    
                    Your OTP Verification code is %s .<br><br>
                    
                   
                    
                  	Career Moulders Support Team<br>
                       
                    </body>
                    </html>"""
			message = html % (name,otp)
			part2 = MIMEText(message, 'html')

			msg.attach(part2)
			
			mail = smtplib.SMTP('smtp.gmail.com', 587)
			#mail = smtplib.SMTP('mail.creamsonservices.com', 587)

			mail.ehlo()

			mail.starttls()

			mail.login('careermoulders.dipak.singhal@gmail.com', 'CareerMoulders@1967@')
			#mail.login('communications@creamsonservices.com', 'CReam7789%$intELLi')
			mail.sendmail(sender, recipient, msg.as_string())
			mail.quit()
		
		else:
			details = []

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Verification Code",
	                                "status": "success"
	                                },
				"responseList":details}), status.HTTP_200_OK



@name_space.route("/UserRegistration")
class UserRegistration(Resource):
	@api.expect(newUser)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		conn = connect_lab_lang1()
		curlang = conn.cursor()

		details = request.get_json()
		address = details.get('address')
		city = details.get('city')
		dateOfBirth = details.get('dateOfBirth')
		emailId = details.get('emailId')
		firstName = details.get('firstName')
		gender = details.get('gender')
		institutionUserName = details.get('institutionUserName')
		institutionUserPassword = details.get('institutionUserPassword')
		institutionUserRole = details.get('institutionUserRole')
		institutionUserStatus = details.get('institutionUserStatus')
		lastName = details.get('lastName')
		middleName = details.get('middleName')
		pincode = details.get('pincode')
		primaryContactNumber = details.get('primaryContactNumber')
		secondaryContactNumber = details.get('secondaryContactNumber')
		state = details.get('state')
		streetAddress = details.get('streetAddress')
		userTaxId = details.get('userTaxId')
		userUniqueId = details.get('userUniqueId')
		board = details.get('board')
		studentname = details.get('studentname')
		clss = details.get('class')
		institutionName = details.get('institutionName')
		institutionId = details.get('institutionId')
		licenseKey = details.get('licenseKey')
		fathers_Name = details.get('fathers_Name')
		image_url = details.get('image_url')
		occupation = details.get('occupation')
		occupation_explain = details.get('occupation_explain')
		aadhaar_no = details.get('aadhaar_no')
		front_aadhar_img = details.get('front_aadhar_img')
		back_aadhar_img = details.get('back_aadhar_img')
		school_last_studied = details.get('school_last_studied')
		college_last_studied = details.get('college_last_studied')
		currently_job_detailed = details.get('currently_job_detailed')

		current_date = date.today()
		userEnrollDate = str(current_date)
		nextyear_date = current_date.replace(year=current_date.year + 1)
		userEndDate = str(nextyear_date)

		msg = None

		res_dtls = {"STATUS": "",
					"user_id": 0,
					"RESPONSE": ""
					}

		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` 
			WHERE `INSTITUTION_USER_NAME` = %s""",(details.get('institutionUserName')))


		useridDetails = cursor.fetchone()
		# print(useridDetails)
		if institutionUserRole in ['S1','T1','TA','A1','G1']:
			if not useridDetails:

				res_dtls = {"STATUS": "User Added",
							"user_id": 0,
								"Response": {
								"status": "Success",
								"UserId": 0
								}
							}

				credentialInsertQuery = ("""INSERT INTO `institution_user_credential`(`CITY`, 
					`DATE_OF_BIRTH`, `EMAIL_ID`, `FIRST_NAME`, `GENDER`, 
					`INSTITUTION_USER_NAME`, `INSTITUTION_USER_PASSWORD`, `LAST_NAME`, `MIDDLE_NAME`, 
					`PINCODE`, `PRIMARY_CONTACT_NUMBER`, `SECONDARY_CONTACT_NUMBER`, `STATE`, 
					`STREET_ADDRESS`, `USER_TAX_ID`, `USER_UNIQUE_ID`, 
					`address`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")


				credentialData = (city,dateOfBirth,emailId,firstName,gender,institutionUserName,institutionUserPassword,
					lastName,middleName,pincode,primaryContactNumber,secondaryContactNumber,state,streetAddress,
					userTaxId,userUniqueId,address)


				cursor.execute(credentialInsertQuery,credentialData)

				InstiUserID = cursor.lastrowid
				details['institution_user_id'] = InstiUserID

				res_dtls['user_id'] = InstiUserID
				res_dtls['Response']['UserId'] = InstiUserID

				credentialMasterQuery = ("""INSERT INTO `institution_user_credential_master`(`INSTITUTION_ID`, 
					`INSTITUTION_USER_ID`, `INSTITUTION_USER_ROLE`, `INSTITUTION_USER_STATUS`, 
					`INSTITUTION_NAME`, `USER_ENROLL_DATE`, 
					`USER_END_DATE`) VALUES (%s,%s,%s,%s,%s,%s,%s)""")


				masterData = (institutionId,InstiUserID,institutionUserRole,institutionUserStatus,institutionName,
					userEnrollDate,userEndDate)

				cursor.execute(credentialMasterQuery,masterData)

				lastUpdateTS = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
				curlang.execute("""INSERT INTO `student`(`Student_ID`, `Student_UserID`, `Class`, 
					`Level`, `Student_Addition_TS`, `Status`, `Last_Update_ID`, `Last_Update_TS`, 
					`Board`) VALUES 
					(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(InstiUserID,InstiUserID,clss,0,lastUpdateTS,
						0,None,lastUpdateTS,board))

				personalInsertQuery = ("""INSERT INTO `institution_user_personal_details`(institution_id,
					institution_user_id,`name`,`EMAIL_ID`,image_url,`INSTITUTION_USER_NAME`,`INSTITUTION_USER_PASSWORD`, 
					`PRIMARY_CONTACT_NUMBER`,occupation,occupation_explain,aadhaar_no,front_aadhar_img,back_aadhar_img,
					`DATE_OF_BIRTH`,`address`,school_last_studied,college_last_studied,currently_job_detailed) VALUES (%s,
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")


				personalData = (institutionId,InstiUserID,firstName+' '+lastName,emailId,image_url,institutionUserName,
					institutionUserPassword,primaryContactNumber,occupation,occupation_explain,aadhaar_no,front_aadhar_img,
					back_aadhar_img,dateOfBirth,address,school_last_studied,college_last_studied,currently_job_detailed)


				cursor.execute(personalInsertQuery,personalData)

				if institutionUserRole == 'S1':
					studentInsertQuery = ("""INSERT INTO `student_dtls`(`INSTITUTION_ID`, 
						`INSTITUTION_USER_ID_STUDENT`,`STUDENT_TYPE`,`CLASS`, 
						`CLASS_START_DATE`, `CLASS_END_DATE`,`STUDENT_NAME`, 
						`Fathers_Name`, `Board`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

					studentData = (institutionId,InstiUserID,'enable',clss,userEnrollDate,userEndDate,
						firstName+' '+lastName,fathers_Name,board)


					cursor.execute(studentInsertQuery,studentData)


				elif institutionUserRole == 'T1' or institutionUserRole == 'TA':

					teacherInsertQuery = ("""INSERT INTO `teacher_dtls`(`INSTITUTION_ID`, 
						`INSTITUTION_USER_ID_TEACHER`) VALUES (%s,%s)""")

					teacherData = (institutionId,InstiUserID)

					cursor.execute(teacherInsertQuery,teacherData)

				elif institutionUserRole == 'A1':
					adminInsertQuery = ("""INSERT INTO `admin_dtls`(`INSTITUTION_ID`, 
						`INSTITUTION_USER_ID_ADMIN`, `ADMIN_TYPE`) VALUES (%s,%s,%s)""")

					adminData = (institutionId,InstiUserID,'A1')

					cursor.execute(adminInsertQuery,adminData)

			else:
				msg = 'User Already exists'
				res_dtls = {"STATUS": "failure",
					"user_id": useridDetails['INSTITUTION_USER_ID'],
					"RESPONSE": msg
					}

		else:
			msg = 'Invalid user role'
			res_dtls = {"STATUS": "failure",
					"user_id": 0,
					"RESPONSE": msg
					}

		connection.commit()
		cursor.close()

		conn.commit()
		curlang.close()
		return ({"attributes": {"status_desc": "Registration Details",
								"status": "success"
								},
				"responseList": res_dtls}), status.HTTP_200_OK



@name_space.route("/ProfileUpdateV2")
class ProfileUpdateV2(Resource):
	@api.expect(updateUserDtls)
	def put(self):

		connection = connect_logindb()
		cursor = connection.cursor()
		
		conn = connect_lab_lang1()
		curlang = conn.cursor()

		details = request.get_json()
		user_id = details.get('user_id')

		institutionId = details.get('institutionId')
		if institutionId is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(institutionId,user_id))
			connection.commit()
		address = details.get('address')
		if address is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `address` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(address,user_id))
		city = details.get('city')
		if city is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `CITY` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(city,user_id))
		dateOfBirth = details.get('dateOfBirth')
		if dateOfBirth is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `DATE_OF_BIRTH` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(dateOfBirth,user_id))
		emailId = details.get('emailId')
		if emailId is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `EMAIL_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(emailId,user_id))
		firstName = details.get('firstName')
		if firstName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `FIRST_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(firstName,user_id))
		gender = details.get('gender')
		if gender is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `GENDER` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(gender,user_id))
		institutionUserName = details.get('institutionUserName')
		if institutionUserName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `INSTITUTION_USER_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(institutionUserName,user_id))
		# institutionUserPassword = details.get('institutionUserPassword')
		# if institutionUserPassword is not None:
		# 	cursor.execute("""UPDATE `institution_user_credential` SET `INSTITUTION_USER_PASSWORD` = %s 
		# 		WHERE `INSTITUTION_USER_ID` = %s""",(institutionUserPassword,user_id))
		institutionUserRole = details.get('institutionUserRole')
		if institutionUserRole is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_USER_ROLE` = %s 
				where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionUserRole,
					institutionId,user_id))
		institutionUserStatus = details.get('institutionUserStatus')
		if institutionUserStatus is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_USER_STATUS` = %s 
				where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionUserStatus,
					institutionId,user_id))
		lastName = details.get('lastName')
		if lastName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `LAST_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(lastName,user_id))
		middleName = details.get('middleName')
		if middleName is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `MIDDLE_NAME` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(middleName,user_id))
		pincode = details.get('pincode')
		if pincode is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `PINCODE` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(pincode,user_id))
		primaryContactNumber = details.get('primaryContactNumber')
		if primaryContactNumber is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `PRIMARY_CONTACT_NUMBER` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(primaryContactNumber,user_id))
		secondaryContactNumber = details.get('secondaryContactNumber')
		if secondaryContactNumber is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `SECONDARY_CONTACT_NUMBER` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(secondaryContactNumber,user_id))
		state = details.get('state')
		if state is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `STATE` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(state,user_id))
		streetAddress = details.get('streetAddress')
		if streetAddress is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `STREET_ADDRESS` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(streetAddress,user_id))
		userTaxId = details.get('userTaxId')
		if userTaxId is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `USER_TAX_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(userTaxId,user_id))
		userUniqueId = details.get('userUniqueId')
		if userUniqueId is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `USER_UNIQUE_ID` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(userUniqueId,user_id))
		board = details.get('board')
		if board is not None:
			cursor.execute("""UPDATE `student_dtls` SET `Board` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(board,institutionId,user_id))
			curlang.execute("""UPDATE `student` SET `Board` = %s WHERE `Student_UserID` = %s""",(board,user_id))
		studentname = details.get('studentname')
		if studentname is not None:
			cursor.execute("""UPDATE `student_dtls` SET `STUDENT_NAME` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(studentname,institutionId,user_id))
		clss = details.get('class')
		if clss is not None:
			cursor.execute("""UPDATE `student_dtls` SET `CLASS` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(clss,institutionId,user_id))
			curlang.execute("""UPDATE `student` SET `Class` = %s WHERE `Student_UserID` = %s""",(clss,user_id))
		institutionName = details.get('institutionName')
		if institutionName is not None:
			cursor.execute("""UPDATE `institution_user_credential_master` SET `INSTITUTION_NAME` = %s 
				where `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionName,
					institutionId,user_id))
		
		# licenseKey = details.get('licenseKey')
		# if licenseKey is not None:
		# 	cursor.execute("""UPDATE `institution_user_credential` SET `address` = %s 
		# 		WHERE `INSTITUTION_USER_ID` = %s""",(licenseKey,user_id))
		fathers_Name = details.get('fathers_Name')
		if fathers_Name is not None:
			cursor.execute("""UPDATE `student_dtls` SET `Fathers_Name` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(fathers_Name,institutionId,user_id))
		image_url = details.get('image_url')
		if image_url is not None:
			cursor.execute("""UPDATE `institution_user_credential` SET `IMAGE_URL` = %s 
				WHERE `INSTITUTION_USER_ID` = %s""",(image_url,user_id))
			cursor.execute("""UPDATE `student_dtls` SET `Image_URL` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(image_url,institutionId,user_id))
		section = details.get('section')
		if section is not None:
			cursor.execute("""UPDATE `student_dtls` SET `SEC` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(section,institutionId,user_id))
		studentrollnum = details.get('studentrollnum')
		if studentrollnum is not None:
			cursor.execute("""UPDATE `student_dtls` SET `STUDENT_ROLL_NUM` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(studentrollnum,institutionId,user_id))
		student_type = details.get('student_type')
		if student_type is not None:
			cursor.execute("""UPDATE `student_dtls` SET `STUDENT_TYPE` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(student_type,institutionId,user_id))
		subscriptiontype = details.get('subscriptiontype')
		if subscriptiontype is not None:
			cursor.execute("""UPDATE `student_dtls` SET `SUBCRIPTION_TYPE` = %s WHERE `INSTITUTION_ID` = %s 
				and `INSTITUTION_USER_ID_STUDENT` = %s""",(subscriptiontype,institutionId,user_id))
		occupation = details.get('occupation')
		if occupation is not None:
			cursor.execute("""UPDATE `institution_user_personal_details` SET `occupation` = %s 
				WHERE `institution_user_id` = %s""",(occupation,user_id))
		occupation_explain = details.get('occupation_explain')
		if occupation_explain is not None:
			cursor.execute("""UPDATE `institution_user_personal_details` SET `occupation_explain` = %s 
				WHERE `institution_user_id` = %s""",(occupation_explain,user_id))
		
		aadhaar_no = details.get('aadhaar_no')
		if aadhaar_no is not None:
			cursor.execute("""UPDATE `institution_user_personal_details` SET `aadhaar_no` = %s 
				WHERE `institution_user_id` = %s""",(aadhaar_no,user_id))
		front_aadhar_img = details.get('front_aadhar_img')
		if front_aadhar_img is not None:
			cursor.execute("""UPDATE `institution_user_personal_details` SET `front_aadhar_img` = %s 
				WHERE `institution_user_id` = %s""",(front_aadhar_img,user_id))
		back_aadhar_img = details.get('back_aadhar_img')
		if back_aadhar_img is not None:
			cursor.execute("""UPDATE `institution_user_personal_details` SET `back_aadhar_img` = %s 
				WHERE `institution_user_id` = %s""",(back_aadhar_img,user_id))
		school_last_studied = details.get('school_last_studied')
		if school_last_studied is not None:
			cursor.execute("""UPDATE `institution_user_personal_details` SET `school_last_studied` = %s 
				WHERE `institution_user_id` = %s""",(school_last_studied,user_id))
		college_last_studied = details.get('college_last_studied')
		if college_last_studied is not None:
			cursor.execute("""UPDATE `institution_user_personal_details` SET `college_last_studied` = %s 
				WHERE `institution_user_id` = %s""",(college_last_studied,user_id))
		currently_job_detailed = details.get('currently_job_detailed')
		if currently_job_detailed is not None:
			cursor.execute("""UPDATE `institution_user_personal_details` SET `currently_job_detailed` = %s 
				WHERE `institution_user_id` = %s""",(currently_job_detailed,user_id))
		
		connection.commit()
		conn.commit()
		cursor.close()
		curlang.close()

		return ({"attributes": {"status_desc": "Profile Update Details",
								"status": "success"
								},
				"responseList": details}), status.HTTP_200_OK


@name_space.route("/ForgotPassword")
class ForgotPassword(Resource):
	@api.expect(forgot_psw)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()
		
		username = details.get('username')
		
		cursor.execute("""SELECT iuc.`INSTITUTION_USER_ID`,FIRST_NAME,LAST_NAME,EMAIL_ID,`INSTITUTION_ID`,`INSTITUTION_USER_ROLE`,
			PRIMARY_CONTACT_NUMBER,address FROM `institution_user_credential` iuc inner join 
			`institution_user_credential_master` iucm on iuc.`INSTITUTION_USER_ID`=iucm.`INSTITUTION_USER_ID` WHERE 
			`INSTITUTION_USER_NAME`=%s""",(username))
		userexistDtls = cursor.fetchone()

		if userexistDtls:
			name = userexistDtls['FIRST_NAME'] + ' '+ userexistDtls['LAST_NAME']
			def get_random_digits(stringLength=6):
			    Digits = string.digits
			    return ''.join((random.choice(Digits) for i in range(stringLength)))
			
			otp = get_random_digits()
				
			otp_query = ("""INSERT INTO `institution_user_otp`(`INSTITUTION_USER_ID`,
				`INSTITUTION_ID`,`OTP`,`INSTITUTION_USER_ROLE`,`FIRST_NAME`,`LAST_NAME`,
				`GENERATED_BY`, `MAIL_ID`, `Address`, `PHONE_NUMBER`)  
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			otpdata = cursor.execute(otp_query,(userexistDtls['INSTITUTION_USER_ID'],userexistDtls['INSTITUTION_ID'],
				otp,userexistDtls['INSTITUTION_USER_ROLE'],userexistDtls['FIRST_NAME'],userexistDtls['LAST_NAME'],
				'System',userexistDtls['EMAIL_ID'],userexistDtls['address'],userexistDtls['PRIMARY_CONTACT_NUMBER']))

			if userexistDtls['EMAIL_ID'] != "":
				smsg = "exists"
				details['OTP'] = otp 
				
				user_info = userexistDtls['EMAIL_ID']
			
				sender = "careermoulders.dipak.singhal@gmail.com"
				recipient = user_info

				msg = MIMEMultipart('alternative')
				msg['Subject'] = " Password Reset "
				msg['From'] = sender
				msg['To'] = recipient

				
				html = """<html>
	                    <head>
	                    <title>careermoulders.dipak.singhal@gmail.com</title>
	                    </head>
	                    <body>
	                    <p>
	                    Dear %s,<br><br> 
	                    
	                    Your Password reset code is %s .<br><br>
	                    
	                   
	                  	Career Moulders Support Team<br>
	                       
	                    </body>
	                    </html>"""
				message = html % (name,otp)
				part2 = MIMEText(message, 'html')

				msg.attach(part2)
				
				mail = smtplib.SMTP('smtp.gmail.com', 587)

				mail.ehlo()

				mail.starttls()

				mail.login('careermoulders.dipak.singhal@gmail.com', 'CareerMoulders2008@')
				mail.sendmail(sender, recipient, msg.as_string())
				mail.quit()
			else:
				smsg = "exists but email id is empty"
		else:
			smsg = "not exists"
			details['OTP'] = "" 
			details = details

		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Forgot Password",
	                                "status": "success",
	                                "msg": smsg
	                                },
				"responseList":details}), status.HTTP_200_OK


@name_space.route("/ResetPassword")
class ResetPassword(Resource):
	@api.expect(reset_psw)
	def put(self):
		details = request.get_json()
		connection = connect_logindb()
		cursor = connection.cursor()

		institutionUserName = details.get('institutionUserName')
		institutionUserPassword = details.get('institutionUserPassword')

		cursor.execute("""UPDATE `institution_user_credential` SET `INSTITUTION_USER_PASSWORD`=%s, 
	 		`RESET`=1 WHERE `INSTITUTION_USER_NAME`=%s""",(institutionUserPassword,institutionUserName))

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Reset Password",
								"status": "success"
								},
				"responseList": "Reset"}), status.HTTP_200_OK

@name_space.route("/addFirebaseDeviceId")
class addFirebaseDeviceId(Resource):
	@api.expect(firebase_device_model)
	def post(self):
		connection = connect_logindb()
		cursor = connection.cursor()
		details = request.get_json()

		INSTITUTION_USER_ID = details['INSTITUTION_USER_ID']
		Device_id = details['Device_id']
		Version_Desc = details['Version_Desc']
		Model_Id = details['Model_Id']
		Last_updated_ID = details['Last_updated_ID']
		Application_type = "elsa"

		cursor.execute("""SELECT `ID` FROM `firebase_link` WHERE `INSTITUTION_USER_ID` = %s""",(INSTITUTION_USER_ID))
		exist = cursor.fetchone()

		if exist:
			cursor.execute("""UPDATE `firebase_link` SET `Device_id`=%s,`Version_Desc`=%s,`Model_Id`=%s WHERE `ID`=%s""",(Device_id,Version_Desc,Model_Id,exist.get('ID')))
		else:
			cursor.execute("""INSERT INTO `firebase_link`(`INSTITUTION_USER_ID`,`Device_id`,`Version_Desc`,`Application_type`,`Model_Id`,`Last_updated_ID`) VALUES(%s,%s,%s,%s,%s,%s)""",
				(INSTITUTION_USER_ID,Device_id,Version_Desc,Application_type,Model_Id,Last_updated_ID))


		connection.commit()
		cursor.close()

		return ({"attributes": {
			"status_desc": "Device_id Added",
			"status": "success"},
			"responseList":""}), status.HTTP_200_OK