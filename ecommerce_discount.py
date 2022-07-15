from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
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
	connection = pymysql.connect(host='localhost',
	                             user='root',
	                             password='',
	                             db='ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

ecommerce_discount = Blueprint('ecommerce_discount_api', __name__)
api = Api(ecommerce_discount,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceDiscount',description='Ecommerce Discount')

discount_postmodel = api.model('SelectDiscount', {
	"discount":fields.Integer(required=True)
})


#----------------------Add-Discount---------------------#

@name_space.route("/AddDiscount")
class AddDiscount(Resource):
	@api.expect(discount_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		discount = details['discount']
		discount_status = 1
		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		get_query = ("""SELECT `discount`
			FROM `discount_master` WHERE `discount` = %s """)

		getData = (discount)
		
		count_discount = cursor.execute(get_query,getData)

		if count_discount > 0:
			return ({"attributes": {
			    		"status_desc": "discount_details",
			    		"status": "error"
			    	},
			    	"responseList":"Discount Already Exsits" }), status.HTTP_200_OK

		else:	

			insert_query = ("""INSERT INTO `discount_master`(`discount`,`status`,`date_of_creation`) 
				VALUES(%s,%s,%s)""")

			data = (discount,discount_status,date_of_creation)
			cursor.execute(insert_query,data)

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "discount_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Discount---------------------#

#----------------------Discount-List---------------------#
@name_space.route("/getDiscountList")	
class getDiscountList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `discount_id`,`discount`,`status`,`date_of_creation`
			FROM `discount_master` WHERE `status` = 1 """)

		cursor.execute(get_query)

		discount_data = cursor.fetchall()

		for key,data in enumerate(discount_data):
			discount_data[key]['date_of_creation'] = str(data['date_of_creation'])
				
		return ({"attributes": {
		    		"status_desc": "meta_key_details",
		    		"status": "success"
		    	},
		    	"responseList":discount_data}), status.HTTP_200_OK

#----------------------Discount-List---------------------#