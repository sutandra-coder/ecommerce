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

ecommerce_login = Blueprint('ecommerce_login_api', __name__)
api = Api(ecommerce_login,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceLogin',description='Ecommerce Login')

#----------------------Admin-Login---------------------#

login_postmodel = api.model('loginCustomer',{
	"email":fields.String(required=True),
	"password":fields.String(required=True)
})

@name_space.route("/Login")	
class Login(Resource):
	@api.expect(login_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		email = details['email']
		password = details['password']

		get_query = ("""SELECT *
			FROM `organisation_master` WHERE `email` = %s and `org_password` = %s""")
		getData = (email,password)
		count = cursor.execute(get_query,getData)

		if count >0 :
			now = datetime.now()
			date_of_lastlogin = now.strftime("%Y-%m-%d %H:%M:%S")
			
			login_data = cursor.fetchone()

			update_query = ("""UPDATE `organisation_master` SET `date_of_lastlogin` = %s
				WHERE `organisation_id` = %s """)
			update_data = (date_of_lastlogin,login_data['organisation_id'])
			cursor.execute(update_query,update_data)

			

			login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
			login_data['last_update_ts'] = str(login_data['last_update_ts'])
		else:
			login_data = {}

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "login_details",
		    		"status": "success"
		    	},
		    	"responseList":login_data}), status.HTTP_200_OK

#----------------------Admin-Login---------------------#


@name_space.route("/Loginwithemployee")	
class Loginwithemployee(Resource):
	@api.expect(login_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		email = details['email']
		password = details['password']

		get_query = ("""SELECT *
			FROM `organisation_master` WHERE `email` = %s and `org_password` = %s""")
		getData = (email,password)
		count = cursor.execute(get_query,getData)

		if count >0 :
			now = datetime.now()
			date_of_lastlogin = now.strftime("%Y-%m-%d %H:%M:%S")
			
			login_data = cursor.fetchone()

			update_query = ("""UPDATE `organisation_master` SET `date_of_lastlogin` = %s
				WHERE `organisation_id` = %s """)
			update_data = (date_of_lastlogin,login_data['organisation_id'])
			cursor.execute(update_query,update_data)

			

			login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
			login_data['last_update_ts'] = str(login_data['last_update_ts'])
			login_data['employee_id'] = 0
		else:
			get_query = ("""SELECT o.*,e.`employee_id`
					FROM `employee` e
					INNER JOIN `organisation_master`o on o.`organisation_id` = e.`organisation_id`
					WHERE e.`phoneno` = %s and e.`password` = %s""")
			getData = (email,password)
			count = cursor.execute(get_query,getData)

			if count >0 :
				now = datetime.now()
				date_of_lastlogin = now.strftime("%Y-%m-%d %H:%M:%S")

				login_data = cursor.fetchone()

				update_query = ("""UPDATE `organisation_master` SET `date_of_lastlogin` = %s
				WHERE `organisation_id` = %s """)
				update_data = (date_of_lastlogin,login_data['organisation_id'])
				cursor.execute(update_query,update_data)


				login_data['date_of_lastlogin'] = str(login_data['date_of_lastlogin'])
				login_data['last_update_ts'] = str(login_data['last_update_ts'])

			else:
				login_data = {}

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "login_details",
		    		"status": "success"
		    	},
		    	"responseList":login_data}), status.HTTP_200_OK
