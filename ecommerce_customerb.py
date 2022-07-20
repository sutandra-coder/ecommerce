from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
import requests
import calendar
import json

app = Flask(__name__)
cors = CORS(app)

#----------------------database-connection---------------------#
def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

ecommerce_customer = Blueprint('ecommerce_customer_api', __name__)
api = Api(ecommerce_customer,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceCustomer',description='Ecommerce Customer')

customer_postmodel = api.model('SelectCustomer', {
	"first_name":fields.String(required=True),
	"last_name":fields.String,
	"email":fields.String(required=True),
	"password":fields.String(required=True),
	"phoneno":fields.Integer(required=True),
	"address_line_1":fields.String(required=True),
	"address_line_2":fields.String,
	"city":fields.String,
	"county":fields.String(required=True),
	"state":fields.String(required=True),
	"pincode":fields.Integer(required=True),
	"emergency_contact":fields.Integer
})

checkemail_postmodel = api.model('checkEmail',{
	"email":fields.String(required=True),
})

checkphoneno_postmodel = api.model('checkPhone',{
	"phoneno":fields.String(required=True),
})

login_postmodel = api.model('loginCustomer',{
	"email":fields.String(required=True),
	"password":fields.String(required=True)
})

changepassword_putmodel = api.model('changePasswod',{
	"new_password":fields.String(required=True),
})

checkotp_postmodel = api.model('checkOtp',{
	"phoneno":fields.String(required=True),
	"otp":fields.String(required=True)
})

customer_product_postmodel = api.model('customerproduct',{
	"customer_id":fields.Integer(required=True),
	"product_meta_id":fields.Integer(required=True),
	"is_favourite":fields.String(required=True)
})


customer_stories_postmodel = api.model('customerstories',{
	"user_id":fields.Integer(required=True),
	"review":fields.String(required=True),
	"ratting":fields.Integer(required=True)
})

#----------------------Check-Email-Exist---------------------#

@name_space.route("/CheckEmail")	
class CheckEmail(Resource):
	@api.expect(checkemail_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `admins` WHERE `email` = %s and `role_id` = 4""")
		getData = (details['email'])
		count_customer = cursor.execute(get_query,getData)

		connection.commit()
		cursor.close()

		if count_customer > 0:
			return ({"attributes": {
			    		"status_desc": "customer_details",
			    		"status": "error",
			    		"message":"Customer Email Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

		else:
			return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success",
		    		"message":"Email Id not Exist"
		    	},
		    	"responseList":{"email":details['email']}}), status.HTTP_200_OK

		

#----------------------Check-Email-Exist---------------------#

#----------------------Check-Phone-No-Exist---------------------#

@name_space.route("/CheckPhoneno")	
class CheckPhoneno(Resource):
	@api.expect(checkphoneno_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `admins` WHERE `phoneno` = %s and `role_id` = 4""")
		getData = (details['phoneno'])
		count_customer = cursor.execute(get_query,getData)

		connection.commit()
		cursor.close()

		if count_customer > 0:
			return ({"attributes": {
			    		"status_desc": "customer_details",
			    		"status": "error",
			    		"message":"Customer Phoneno Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

		else:
			return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList":{"phoneno":details['phoneno']}}), status.HTTP_200_OK

		

#----------------------Check-Phone-No-Exist---------------------#

#----------------------Add-Customer---------------------#

@name_space.route("/AddCustomer")
class AddCustomer(Resource):
	@api.expect(customer_postmodel)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		first_name = details['first_name']
		last_name = details['last_name']
		email = details['email']
		password = details['password']
		phoneno = details['phoneno']
		address_line_1 = details['address_line_1']
		address_line_2 = details['address_line_2']
		city = details['city']
		county = details['county']
		state = details['state']
		pincode = details['pincode']
		emergency_contact = details['emergency_contact']
		role_id = 4
		admin_status = 1

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		get_query = ("""SELECT `email`
			FROM `admins` WHERE `email` = %s """)

		getData = (email)
		
		count_retailer = cursor.execute(get_query,getData)

		if count_retailer > 0:
			return ({"attributes": {
			    		"status_desc": "customer_details",
			    		"status": "error",
			    		"message":"Customer Phoneno Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

		else:

			get_query_phone = ("""SELECT *
			FROM `admins` WHERE `phoneno` = %s and `role_id` = 4""")
			getDataPhone = (details['phoneno'])
			count_customer_phone = cursor.execute(get_query_phone,getDataPhone)

			
			if count_customer_phone > 0:
				return ({"attributes": {
				    		"status_desc": "customer_details",
				    		"status": "error",
				    		"message":"Customer Phoneno Already Exist"
				    	},
				    	"responseList":{} }), status.HTTP_200_OK

			else:
				
				insert_query = ("""INSERT INTO `admins`(`first_name`,`last_name`,`email`,`org_password`,
									`phoneno`,`address_line_1`,`address_line_2`,`city`,`county`,
									`state`,`pincode`,`emergency_contact`,`role_id`,`status`,`date_of_creation`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				data = (first_name,last_name,email,password,phoneno,address_line_1,address_line_2,city,county,state,pincode,emergency_contact,role_id,admin_status,date_of_creation)
				cursor.execute(insert_query,data)

				admin_id = cursor.lastrowid
				details['user_id'] = admin_id

				connection.commit()
				cursor.close()

				return ({"attributes": {
				    		"status_desc": "customer_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Customer---------------------#

#----------------------Customer-Login---------------------#

@name_space.route("/Login")	
class Login(Resource):
	@api.expect(login_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_emiail_query = ("""SELECT *
			FROM `admins` WHERE `email` = %s and `role_id` = 4""")
		getDataEmail = (details['email'])

		count_customer = cursor.execute(get_emiail_query,getDataEmail)

		if count_customer > 0:
			
			get_query = ("""SELECT `admin_id` as `user_id`,`first_name`,`last_name`,`email`,`org_password`,
			`phoneno`,`address_line_1`,`address_line_2`,`city`,`county`,`state`,`pincode`,`emergency_contact`,`role_id`
				FROM `admins` WHERE `email` = %s and `org_password` = %s""")
			getData = (details['email'],details['password'])
			count_customer_email_password = cursor.execute(get_query,getData)			

			if count_customer_email_password > 0:
				login_data = cursor.fetchone()
				return ({"attributes": {
				    		"status_desc": "login_details",
				    		"status": "success",
				    		"message":"Login Successfully"
				    	},
				    	"responseList":login_data}), status.HTTP_200_OK
			else:
				return ({"attributes": {
				    		"status_desc": "login_details",
				    		"status": "error",
				    		"message":"Email id and password does't match"
				    	},
				    	"responseList":{}}), status.HTTP_200_OK
		else:		
			return ({"attributes": {
			    		"status_desc": "customer_details",
			    		"status": "error",
			    		"message":"We cannot find an account with that email address"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK
				    		

#----------------------Customer-Login---------------------#

#----------------------Forgotpassword---------------------#

@name_space.route("/Forgotpassword")	
class Forgotpassword(Resource):
	@api.expect(checkphoneno_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		get_query = ("""SELECT *
			FROM `admins` WHERE `phoneno` = %s and `role_id` = 4""")
		getData = (details['phoneno'])
		count_customer = cursor.execute(get_query,getData)

		connection.commit()
		cursor.close()

		if count_customer > 0:
			login_data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "customer_details",
			    		"status": "success",
			    		"mesaage":"Exist"
			    	},
			    	"responseList":{"user_id": login_data['admin_id']}}), status.HTTP_200_OK

		else:
			return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success",
		    		"message":"Did not Exist"
		    	},
		    	"responseList":{"phoneno":details['phoneno']}}), status.HTTP_200_OK

		

#----------------------Forgotpassword---------------------#

#----------------------Change-Password---------------------#

@name_space.route("/changePasswod/<int:user_id>")
class changePasswod(Resource):
	@api.expect(changepassword_putmodel)
	def put(self,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()

		update_query = ("""UPDATE `admins` SET `org_password` = %s
				WHERE `admin_id` = %s """)
		update_data = (details['new_password'],user_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Change Password",
								"status": "success",
								"message":"Password set successfully"
									},
				"responseList":details}), status.HTTP_200_OK

#----------------------Change-Password---------------------#

#----------------------Send-Otp---------------------#

@name_space.route("/sendOtp")	
class sendOtp(Resource):
	@api.expect(checkphoneno_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		url = "http://creamsonservices.com:8080/NewSignUpService/postInstitutionUserOtp"
		post_data = {
					  "firstName": "string",
					  "generatedBy": "string",
					  "institutionId": 1,
					  "institutionUserId": 0,
					  "institutionUserRole": "S1",
					  "lastName": "string",
					  "mailId": "string",
					  "otp": 123456,
					  "phoneNumber": details['phoneno']
					}

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		post_response = requests.post(url, data=json.dumps(post_data), headers=headers)

		my_json_string = post_response.json()

		s1 = json.dumps(my_json_string['responseList'][0])
		s2 = json.loads(s1)

		InstitutionUserOtp = json.dumps(s2['InstitutionUserOtp '])
		otpjson = json.loads(InstitutionUserOtp)

		if otpjson :
			return ({"attributes": {"status_desc": "Send Otp",
								"status": "success",
								"message":"Send Otp Successfully"
									},
				"responseList":{"otp":otpjson['otp'],"phoneno":otpjson['phoneNumber']}}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Send Otp",
								"status": "error",
								"message":"Having Issue"
									},
				"responseList":{}}), status.HTTP_200_OK	
#----------------------Send-Otp---------------------#

#----------------------Check-Otp---------------------#

@name_space.route("/checkOtp")	
class checkOtp(Resource):
	@api.expect(checkotp_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = 'http://creamsonservices.com:8080/NewSignUpService/validateOtpByPhone/{}/{}'.format(details['otp'],details['phoneno'])

		getResponse = requests.get(url, headers=headers)

		my_json_string = getResponse.json()

		check_response = json.dumps(my_json_string['attributes'])

		response = json.loads(check_response)

		if(response['status'] == 'success'):

			responselist = json.dumps(my_json_string['responseList'][0])
			responselistjson = json.loads(responselist)

			InstitutionUserOtp = json.dumps(responselistjson['InstitutionUserOtp '])
			otpjson = json.loads(InstitutionUserOtp)

			if otpjson :
				return ({"attributes": {"status_desc": "Check Otp",
									"status": "success",
									"message":"Outhenticate Successfully"
										},
					"responseList":{"otp":otpjson['otp'],"phoneno":otpjson['phoneNumber']}}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Check Otp",
								"status": "error",
								"message":"Otp Not Validated"
									},
				"responseList":{}}), status.HTTP_200_OK	

#----------------------Check-Otp---------------------#


#----------------------Get-Customer-Notification---------------------#	

@name_space.route("/getCustomerNotificationList/<int:user_id>")	
class getCustomerNotificationList(Resource):
	def get(self,user_id):
		
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `customer_notification_mapping` where `customer_id` = %s""")
		get_data = (user_id)
		cursor.execute(get_query,get_data)

		cusomer_notification_data = cursor.fetchall()

		for key,data in enumerate(cusomer_notification_data):
			cusomer_notification_data[key]['Last_update_TS'] = str(data['Last_update_TS'])

			get_product_query = ("""SELECT `product_id`,`product_name`,`product_long_description`,`product_short_description`,`price`
			FROM `product` WHERE `product_id` = %s """)
			get_product_data = (data['product_id'])
			cursor.execute(get_product_query,get_product_data)
			product_data = cursor.fetchone()

			get_notification_query = ("""SELECT `notification_id`,`text`,`image`,`email`,`whatsapp`
			FROM `notification` WHERE `notification_id` = %s """)
			get_notification_data = (data['notification_id'])
			cursor.execute(get_notification_query,get_notification_data)
			notification_data = cursor.fetchone()

			cusomer_notification_data[key]['product_name'] = product_data['product_name']
			cusomer_notification_data[key]['notification_id'] = notification_data['notification_id']	
			cusomer_notification_data[key]['text'] = notification_data['text']
			cusomer_notification_data[key]['image'] = notification_data['image']
			cusomer_notification_data[key]['email'] = notification_data['email']
			cusomer_notification_data[key]['whatsapp'] = notification_data['whatsapp']
		return ({"attributes": {
		    		"status_desc": "customer_notification_details",
		    		"status": "success"
		    	},
		    	"responseList":cusomer_notification_data}), status.HTTP_200_OK

#----------------------Get-Customer-Notification---------------------#	

#----------------------Get-Customer-List---------------------#

@name_space.route("/getCustomerList")	
class getCustomerList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `admin_id`,`first_name`,`last_name`,`email`,`org_password`,`phoneno`,
			`address_line_1`,`address_line_2`,`city`,`county`,`state`,`pincode`,`emergency_contact`,
			`status`
			FROM `admins` WHERE `role_id` = 4 """)

		cursor.execute(get_query)

		data = cursor.fetchall()
				
		return ({"attributes": {
		    		"status_desc": "Customer_details",
		    		"status": "success"
		    	},
		    	"responseList":data}), status.HTTP_200_OK
		
#-----------------------Get-Customer-List---------------------#

#----------------------Add-Customer-Stories---------------------#

@name_space.route("/AddCustomerStories")
class AddCustomerStories(Resource):
	@api.expect(customer_stories_postmodel)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		customer_id = details['user_id']
		review = details['review']
		ratting = details['ratting']

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		insert_query = ("""INSERT INTO `customer_stories`(`customer_id`,`review`,`ratting`,`date_of_creation`) 
				VALUES(%s,%s,%s,%s)""")
		data = (customer_id,review,ratting,date_of_creation)
		cursor.execute(insert_query,data)

		customer_story_id = cursor.lastrowid
		details['customer_story_id'] = customer_story_id

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "customer_story_details",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#----------------------Add-Customer-Stories---------------------#

#----------------------Get-Customer-Stories---------------------#

@name_space.route("/getCustomerStoryList")	
class getCustomerStoryList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `customer_stories`""")

		cursor.execute(get_query)

		story_data = cursor.fetchall()

		for key,data in enumerate(story_data):
			story_data[key]['date_of_creation'] = str(data['date_of_creation'])

			get_customer_query = ("""SELECT `first_name`,`last_name`
			FROM `admins` WHERE `admin_id` = %s """)
			customer_data = (data['customer_id'])
			cursor.execute(get_customer_query,customer_data)

			customer_data_result = cursor.fetchone()

			story_data[key]['first_name'] = customer_data_result['first_name']
			story_data[key]['last_name'] = customer_data_result['last_name']

				
		return ({"attributes": {
		    		"status_desc": "Customer_stories",
		    		"status": "success"
		    	},
		    	"responseList":story_data}), status.HTTP_200_OK
		
#-----------------------Get-Customer-Stories---------------------#

#----------------------Add-Customer-Product---------------------#
@name_space.route("/addCustomerProduct")	
class addCustomerProduct(Resource):
	@api.expect(customer_product_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		product_meta_id = details['product_meta_id']
		customer_id = details['customer_id']
		organisation_id = 1
		last_update_id = 1
		product_status = "w"
		customer_prodcut_status = 1

		is_favourite = details['is_favourite']

		if is_favourite == "y":

			get_query = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s""")

			getData = (product_meta_id,customer_id)
			
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:

				connection.commit()
				cursor.close()

				return ({"attributes": {
				    		"status_desc": "customer_product_details",
				    		"status": "error"
				    	},
				    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

			else:

				insert_query = ("""INSERT INTO `customer_product_mapping`(`customer_id`,`product_meta_id`,`product_status`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s)""")

				data = (customer_id,product_meta_id,product_status,customer_prodcut_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)		

				mapping_id = cursor.lastrowid
				details['mapping_id'] = mapping_id

				connection.commit()
				cursor.close()

			return ({"attributes": {
					    		"status_desc": "customer_product_details",
					    		"status": "success"
					    	},
					    	"responseList":"Product Added Successfully"}), status.HTTP_200_OK
		else:
			delete_query = ("""DELETE FROM `customer_product_mapping` WHERE `product_meta_id` = %s and `customer_id` = %s""")
			delData = (product_meta_id,customer_id)
			
			cursor.execute(delete_query,delData)
			connection.commit()
			cursor.close()

			return ({"attributes": {"status_desc": "customer_product_details",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK		


#----------------------Add-Customer-Product---------------------#


#----------------------Product-Customer-List---------------------#

@name_space.route("/getProductCustomerList/<string:key>/<int:user_id>")	
class getProductCustomerList(Resource):
	def get(self,key,user_id):
		if key == "c" or key == "w" or key == "o":
			product_data = 	[
								{
									"user_id":user_id,
									"product_id":1,
									"product_name": "Test Product1",
								    "image": "https://d1lwvo1ffrod0a.cloudfront.net/117/drive.png",
								    "price": 9999.00
	        					},
	        					{
	        						"user_id":user_id,
	        						"product_id":2,
									"text": "Test Product2",
								    "image": "https://d1lwvo1ffrod0a.cloudfront.net/117/image2.png",
								    "price": 10000.00
	        					},
	        					{
	        						"user_id":user_id,
	        						"product_id":3,
									"text": "Test Product3",
								    "image": "https://d1lwvo1ffrod0a.cloudfront.net/117/memorycard.png",
								    "price": 11000.00
								},
								{
	        						"user_id":user_id,
	        						"product_id":4,
									"text": "Test Product4",
								    "image": "https://d1lwvo1ffrod0a.cloudfront.net/117/phone.jpg",
								    "price": 11000.00
								}
							]  					    
	   		
		return ({"attributes": {
		    		"status_desc": "customer_product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK


#----------------------Product-Customer-List---------------------#

#----------------------Dashboard---------------------#
@name_space.route("/dashboard/<int:category_id>/<int:user_id>")	
class dashboard(Resource):
	def get(self,category_id,user_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_category_query = ("""SELECT meta_key_value_id
			FROM `home_category_mapping` """)

		cursor.execute(get_category_query)

		home_category_data = cursor.fetchall()

		for key,data in enumerate(home_category_data):
			get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
			FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

			getdata_key_value = (data['meta_key_value_id'])
			cursor.execute(get_key_value_query,getdata_key_value)

			key_value_data = cursor.fetchone()

			home_category_data[key]['meta_key_value'] = key_value_data['meta_key_value']
			home_category_data[key]['image'] = key_value_data['image']

		get_brand_query = ("""SELECT meta_key_value_id
			FROM `home_brand_mapping` """)

		cursor.execute(get_brand_query)

		home_brand_data = cursor.fetchall()

		for hkey,hdata in enumerate(home_brand_data):
			get_key_value_query = ("""SELECT `meta_key_value_id`,`meta_key_value`,`image`
			FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)

			getdata_key_value = (hdata['meta_key_value_id'])
			cursor.execute(get_key_value_query,getdata_key_value)

			key_value_data = cursor.fetchone()

			home_brand_data[hkey]['meta_key_value'] = key_value_data['meta_key_value']
			home_brand_data[hkey]['image'] = key_value_data['image']

		get_top_selling_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`
			FROM `product_top_selling_mapping` pts 
			INNER JOIN `product_meta` pm ON pts.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id`""")		
		cursor.execute(get_top_selling_product)
		top_selling_product = cursor.fetchall()

		for tkey,tdata in enumerate(top_selling_product):			
			get_product_meta_image_quey = ("""SELECT `image` as `product_image`
			FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
			product_meta_image_data = (tdata['product_meta_id'])
			rows_count_image_top_selling = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
			if rows_count_image_top_selling > 0:
				product_meta_image = cursor.fetchone()
				top_selling_product[tkey]['product_image'] = product_meta_image['product_image']
			else:
				top_selling_product[tkey]['product_image'] = ""	

			get_product_meta_inventory_stock_quey = ("""SELECT `stock`
			FROM `product_inventory` WHERE `product_meta_id` = %s """)
			product_meta_inventory_stock_data = (tdata['product_meta_id'])
			row_count_stock = cursor.execute(get_product_meta_inventory_stock_quey,product_meta_inventory_stock_data)

			if row_count_stock > 0:
				product_meta_inventory_stock = cursor.fetchone()

				top_selling_product[tkey]['totalproduct'] = product_meta_inventory_stock['stock']
			else:
				top_selling_product[tkey]['totalproduct'] = ""

		get_best_selling_product =  ("""SELECT p.`product_id`,p.`product_name`,pm.`product_meta_id`,pm.`out_price`
			FROM `product_best_selling_mapping` pbsm 
			INNER JOIN `product_meta` pm ON pbsm.`product_meta_id` = pm.`product_meta_id`
			INNER JOIN `product` p ON pm.`product_id` = p.`product_id` """)
		cursor.execute(get_best_selling_product)
		best_selling_product = cursor.fetchall()

		for bkey,bdata in enumerate(best_selling_product):
			get_product_meta_image_quey = ("""SELECT `image`
			FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
			product_meta_image_data = (bdata['product_meta_id'])
			rows_count_image_best_selling = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
			if rows_count_image_best_selling > 0:
				product_meta_image = cursor.fetchone()
				best_selling_product[bkey]['image'] = product_meta_image['image']
			else:
				best_selling_product[bkey]['image'] = ""

		get_offer_product =  ("""SELECT pom.`product_id`,o.`offer_id`,o.`offer_image`,o.`discount_percentage`
			FROM `product_offer_mapping` pom 
			INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`""")
		cursor.execute(get_offer_product)
		offer_product = cursor.fetchall()

		get_new_arrival_product =  ("""SELECT pnm.`product_id`,n.`new_arrival_id`,n.`new_arrival_image` as `offer_image`,n.`discount_percentage`
			FROM `product_new_arrival_mapping` pnm 
			INNER JOIN `new_arrival` n ON n.`new_arrival_id` = pnm.`new_arrival_id`""")
		cursor.execute(get_new_arrival_product)
		new_arrival_product = cursor.fetchall()
			
		connection.commit()
		cursor.close()	

		offer_data = 	[
							{
								"offer_id":1,
								"product_id":1,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/home_banner1.png",
								"discount_percentage":10
	        				},
	        				{
	        					"offer_id":2,
	        					"product_id":2,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/home_banner2.png",
								"discount_percentage":10
	        				},
	        				{
	        					"offer_id":3,
	        					"product_id":3,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/home_banner3.png",
								"discount_percentage":10
							}

						]  	

		new_arrivale = 	[
							{
								"new_arrivale_id":1,
								"product_id":4,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/home_1.png",
								"discount_percentage":10
	        				},
	        				{
	        					"new_arrivale_id":2,
	        					"product_id":5,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/images1.jpg",
								"discount_percentage":10
	        				},
	        				{
	        					"new_arrivale_id":3,
	        					"product_id":6,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/images2.jpg",
								"discount_percentage":10
							},
							{
	        					"new_arrivale_id":4,
	        					"product_id":7,
								"offer_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/images3.jpg",
								"discount_percentage":10
							}
						]	

		top_selling = 	[
							{
								"top_selling_id":1,
								"product_id":8,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/drive.png",
								"product_name":"test Product1",
								"totalproduct":1
	        				},
	        				{
	        					"top_selling_id":2,
	        					"product_id":9,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/image2.png",
								"product_name":"test Product2",
								"totalproduct":2
	        				},
	        				{
	        					"top_selling_id":3,
	        					"product_id":10,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/memorycard.png",
								"product_name":"test Product3",
								"totalproduct":3
							},
							{
	        					"top_selling_id":4,
	        					"product_id":11,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/phone.jpg",
								"product_name":"test Product3",
								"totalproduct":3
							}

						]

		best_selling = 	[
							{
								"product_id":12,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/image2.png",
								"product_name":"i phone 11",
								"price":79999
	        				},
	        				{	        					
	        					"product_id":13,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/81T7lVQGdxL._SY606_.jpg",
								"product_name":"MI A3",
								"price":16999
	        				},
	        				{	        					
	        					"product_id":14,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/3e97ce53c0a379894aff19753b7fa70c34f71e9256d725e07acdaf60458ab96e.jpg",
								"product_name":"Nokia 6.1",
								"price":13999
							},
							{	        					
	        					"product_id":15,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/01_Samsung-galaxy-a50-.png",
								"product_name":"Samsung Galaxy A50",
								"price":15499
							},
							{	        					
	        					"product_id":16,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/S_mdr.png",
								"product_name":"Sony MDR",
								"price":2199
							},
							{	        					
	        					"product_id":16,
								"product_image": "https://d1lwvo1ffrod0a.cloudfront.net/117/memorycard.png",
								"product_name":"Sandisk 16GB Micro SD",
								"price":899
							}

						]				

	   		
		return ({"attributes": {
		    		"status_desc": "customer_product_details",
		    		"status": "success"
		    	},
		    	"responseList":{"offer_data":offer_product,"new_arrivale":new_arrival_product,"top_selling":top_selling_product,"home_category_data":home_category_data,
		    					"home_brand_data":home_brand_data,"best_selling":best_selling}}), status.HTTP_200_OK

#----------------------Dashboard---------------------#

#----------------------Product-List---------------------#
@name_space.route("/getProductList/<int:product_id>/<int:user_id>")	
class getProductList(Resource):
	def get(self,product_id,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_long_description`,
			pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
			FROM `product` p
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			WHERE p.`status` = 1 and p.`product_id` = %s""")
		get_data = (product_id)
		cursor.execute(get_query,get_data)

		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):

			a_string = data['meta_key_text']
			a_list = a_string.split(',')

			met_key = []

			for a in a_list:
				get_query_key_value = ("""SELECT `meta_key_id`,`meta_key_value`
								FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)
				getdata_key_value = (a)
				cursor.execute(get_query_key_value,getdata_key_value)
				met_key_value_data = cursor.fetchone()

				get_query_key = ("""SELECT `meta_key`
								FROM `meta_key_master` WHERE `meta_key_id` = %s """)
				getdata_key = (met_key_value_data['meta_key_id'])
				cursor.execute(get_query_key,getdata_key)
				met_key_data = cursor.fetchone()

				met_key.append({met_key_data['meta_key']:met_key_value_data['meta_key_value']})

				product_data[key]['met_key_value'] = met_key
			
			get_query_image = ("""SELECT `image`
										FROM `product_meta_images` WHERE `product_meta_id` = %s and `default_image_flag` = 1""")
			getdata_image = (data['product_meta_id'])
			cursor.execute(get_query_image,getdata_image)
			product_image = cursor.fetchone()

			get_query_discount = ("""SELECT `discount`
										FROM `product_meta_discount_mapping` pdm
										INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
										WHERE `product_meta_id` = %s """)
			getdata_discount = (data['product_meta_id'])
			count_dicscount = cursor.execute(get_query_discount,getdata_discount)

			if count_dicscount > 0:
				product_meta_discount = cursor.fetchone()
				product_data[key]['discount'] = product_meta_discount['discount']

				discount = (data['out_price']/100)*product_meta_discount['discount']
				actual_amount = data['out_price'] - discount

				product_data[key]['after_discounted_price'] = actual_amount  
			else:
				product_data[key]['discount'] = ""
				product_data[key]['after_discounted_price'] = ""

			product_data[key]['rating'] = 4.3

			product_data[key]['image'] = product_image['image']

			
			get_favourite = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)

			getFavData = (data['product_meta_id'],user_id)
			
			count_fav_product = cursor.execute(get_favourite,getFavData)

			if count_fav_product > 0:
				product_data[key]['is_favourite'] = "y"
			else:
				product_data[key]['is_favourite'] = "n"

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Product-Details---------------------#
@name_space.route("/productDetails/<int:product_id>/<int:product_meta_code>/<int:user_id>")	
class productDetails(Resource):
	def get(self,product_id,product_meta_code,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
			pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
			FROM `product` p
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			WHERE p.`product_id` = %s and `product_meta_code` = %s""")
		getdata = (product_id,product_meta_code)
		cursor.execute(get_query,getdata)
		product_data = cursor.fetchone()

		
		a_string = product_data['meta_key_text']
		a_list = a_string.split(',')
			
		met_key = []
		for a in a_list:
			get_query_key_value = ("""SELECT `meta_key_id`,`meta_key_value`
					FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)
			getdata_key_value = (a)
			cursor.execute(get_query_key_value,getdata_key_value)
			met_key_value_data = cursor.fetchone()

			get_query_key = ("""SELECT `meta_key`
							FROM `meta_key_master` WHERE `meta_key_id` = %s """)
			getdata_key = (met_key_value_data['meta_key_id'])
			cursor.execute(get_query_key,getdata_key)
			met_key_data = cursor.fetchone()

			met_key.append({met_key_data['meta_key']:met_key_value_data['meta_key_value']})

			product_data['met_key_value'] = met_key

			get_query_all_key_value = ("""SELECT `meta_key_id`,`meta_key_value`,`meta_key_value_id`
					FROM `meta_key_value_master` WHERE `meta_key_id` = %s """)
			getdata_all_key_value = (met_key_value_data['meta_key_id'])
			cursor.execute(get_query_all_key_value,getdata_all_key_value)
			met_key_value_all_data = cursor.fetchall()

				#product_meta[key][met_key_data['meta_key']] = met_key_value_all_data
			met_key_value_all_data_new = []		

			for key_all,met_key_value_all_data_one in  enumerate(met_key_value_all_data):
				met_key_value_all_data_new.append({met_key_value_all_data_one['meta_key_value_id']:met_key_value_all_data_one['meta_key_value']})

			product_data[met_key_data['meta_key']] = met_key_value_all_data_new

		image_a = []	
		get_query_images = ("""SELECT `image`
					FROM `product_meta_images` WHERE `product_meta_id` = %s """)
		getdata_images = (product_data['product_meta_id'])
		cursor.execute(get_query_images,getdata_images)
		images = cursor.fetchall()

		for image in images:
			image_a.append(image['image'])

		product_data['images'] = image_a

		get_product_meta_key_query = ("""SELECT `product_meta_id`,`product_meta_code`,`meta_key_text`,`in_price`,`out_price`
			FROM `product_meta`
			WHERE `product_id` = %s""")
		getProductMetadata = (product_id)
		cursor.execute(get_product_meta_key_query,getProductMetadata)
		product_meta_key_data = cursor.fetchall()

		product_met_key = []
		for key,data in enumerate(product_meta_key_data):
			a_string = data['meta_key_text']
			a_list = a_string.split(',')

			get_query_key_value = ("""SELECT `meta_key_id`,`meta_key_value`
					FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)
			getdata_key_value = (a)
			cursor.execute(get_query_key_value,getdata_key_value)
			met_key_value_data = cursor.fetchone()

			get_query_key = ("""SELECT `meta_key`
							FROM `meta_key_master` WHERE `meta_key_id` = %s """)
			getdata_key = (met_key_value_data['meta_key_id'])
			cursor.execute(get_query_key,getdata_key)
			met_key_data = cursor.fetchone()

			product_met_key.append({met_key_data['meta_key']:met_key_value_data['meta_key_value']})

			product_meta_key_data['met_key_value'] = product_met_key

			product_data[met_key_data['meta_key']] = product_meta_key_data

		get_query_discount = ("""SELECT `discount`
									FROM `product_meta_discount_mapping` pdm
									INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
									WHERE `product_meta_id` = %s """)
		getdata_discount = (product_data['product_meta_id'])
		count_dicscount = cursor.execute(get_query_discount,getdata_discount)

		if count_dicscount > 0:
			product_meta_discount = cursor.fetchone()
			product_data['discount'] = product_meta_discount['discount']

			discount = (product_data['out_price']/100)*product_meta_discount['discount']
			actual_amount = product_data['out_price'] - discount
			product_data['after_discounted_price'] = actual_amount

		else:
			product_data['discount'] = ""
			product_data['after_discounted_price'] = ""

		get_favourite = ("""SELECT `product_meta_id`
				FROM `customer_product_mapping` WHERE  `product_meta_id` = %s and `customer_id` = %s and product_status ="w" """)
		getFavData = (product_data['product_meta_id'],user_id)
		count_fav_product = cursor.execute(get_favourite,getFavData)

		if count_fav_product > 0:
			product_data['is_favourite'] = "y"
		else:
			product_data['is_favourite'] = "n"
		

		product_data['rating'] = 4.3

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-Details---------------------#




