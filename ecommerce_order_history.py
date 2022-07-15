from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
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
ecommerce_order_history = Blueprint('ecommerce_order_history_api', __name__)
api = Api(ecommerce_order_history,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceOrderHistory',description='Ecommerce Order History')

#-----------------------------------------------------------------#
order_history = api.model('order_history', {
	"order_product_id": fields.Integer(),
	"imageurl": fields.String(),
    "retailer_remarks": fields.String(),
    "updatedorder_status": fields.String(),
    "updatedpayment_status": fields.String(),
    "updateduser_id": fields.Integer(),
    "organisation_id": fields.Integer()
    })

#-------------------------------------------------------------#
@name_space.route("/OderHistoryDetails")
class OderHistoryDetails(Resource):
	@api.expect(order_history)
	def post(self):
		conn = mysql_connection()
		cur = conn.cursor()
		details = request.get_json()
		
		order_product_id = details.get('order_product_id')
		imageurl = details.get('imageurl')
		retailer_remarks = details.get('retailer_remarks')
		updatedorder_status = details.get('updatedorder_status')
		updatedpayment_status = details.get('updatedpayment_status')
		updateduser_id = details.get('updateduser_id')
		organisation_id = details.get('organisation_id')
		
		historyquery = ("""INSERT INTO `order_history`(`order_product_id`,
			`organisation_id`,`imageurl`,`retailer_remarks`,`updatedorder_status`,
			`updatedpayment_status`,`last_update_id`) VALUES (%s,%s,%s,%s,%s,%s,%s)""")
		historydata = cur.execute(historyquery,(order_product_id,organisation_id,
			imageurl,retailer_remarks,updatedorder_status,updatedpayment_status,updateduser_id))

		orderhistory_id = cur.lastrowid
		details['orderhistory_id'] = orderhistory_id

		conn.commit()
		cur.close()

		return ({"attributes": {"status_desc": "Order History Details",
                                "status": "success"
	                            },
	            "responseList": details}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/OrderHistoryDtlsByOrderId/<int:order_id>")	
class OrderHistoryDtlsByOrderId(Resource):
	def get(self,order_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `orderhistory_id`,`order_product_id`,
			`organisation_id`,`imageurl`,`retailer_remarks`,`updatedorder_status`,
			`updatedpayment_status`,`last_update_id`,`last_update_ts`
			FROM `order_history` WHERE `order_product_id`=%s""",(order_id))

		historydtls = cursor.fetchall()
		for i in range(len(historydtls)):

			if historydtls:
				historydtls[i]['last_update_ts'] = historydtls[i]['last_update_ts'].isoformat()
			else:
				historydtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Order History Details",
		    		"status": "success"
		    	},
		    	"responseList":historydtls}), status.HTTP_200_OK
