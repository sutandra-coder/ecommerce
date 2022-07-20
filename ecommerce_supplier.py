from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json
from flask_api import status
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

ecommerce_supplier = Blueprint('ecommerce_supplier_api', __name__)
api = Api(ecommerce_supplier,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceSupplier',description='Ecommerce Supplier')

name_space_supplier_order =  api.namespace('EcommerceSupplierOrder',description='Ecommerce Supplier Order')

name_space_product =  api.namespace('EcommerceProduct',description='Ecommerce Product')
name_space_retailer_store =  api.namespace('EcommerceRetailerStore',description='Ecommerce Retailer Store')

supplier_postmodel = api.model('supplier_postmodel', {
	"supplier_name":fields.String(required=True),
	"address":fields.String(required=True),
	"phoneno":fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

supplier_putmodel = api.model('supplier_putmodel', {
	"supplier_name":fields.String,
	"address":fields.String,
	"phoneno":fields.String,
})

supplier_order_postmodel = api.model('supplier_order_postmodel', {
	"order_name":fields.String(required=True),
	"order_date":fields.String(required=True),
	"supplier_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

supplier_order_putmodel = api.model('supplier_order_putmodel', {
	"order_name":fields.String,
	"order_date":fields.String
})

supplier_order_product_postmodel = api.model('supplier_order_product_postmodel', {
	"supplier_order_id":fields.Integer(required=True),
	"product_meta_id":fields.Integer(required=True),
	"supplier_stock":fields.Integer(required=True),
	"price_per_unit":fields.Integer(required=True),
	"retailer_store_store_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

supplier_order_payment_postmodel = api.model('supplier_order_payment_postmodel', {
	"supplier_order_id":fields.Integer(required=True),
	"amount":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

#--------------------Add-Supplier-------------------------#

@name_space.route("/AddSupplier")
class AddSupplier(Resource):
	@api.expect(supplier_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		supplier_name = details['supplier_name']
		address = details['address']
		phoneno = details['phoneno']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_query = ("""SELECT *
			FROM `supplier` WHERE `phoneno` = %s and `organisation_id` = %s""")
		getData = (phoneno,organisation_id)
		count_supplier = cursor.execute(get_query,getData)

		if count_supplier > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "Supplier_details",
			    		"status": "error",
			    		"message":" Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK
		else:
			supplier_status = 1
			insert_query = ("""INSERT INTO `supplier`(`supplier_name`,`address`,`phoneno`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")
			data = (supplier_name,address,phoneno,supplier_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)
			supplier_id = cursor.lastrowid

		return ({"attributes": {
		    		"status_desc": "supplier_details",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList": details}), status.HTTP_200_OK

#--------------------Add-Supplier-------------------------#

#----------------------Supplier-List---------------------#

@name_space.route("/supplierList/<int:organisation_id>")	
class supplierList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT *
			FROM `supplier`			
			WHERE `organisation_id` = %s """)

		get_data = (organisation_id)
		count_supplier = cursor.execute(get_query,get_data)

		if count_supplier >0:
			supplier_data = cursor.fetchall()
			for key,data in enumerate(supplier_data):
				supplier_data[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			supplier_data = []


		return ({"attributes": {
		    		"status_desc": "supplier_details",
		    		"status": "success"
		    	},
		    	"responseList":supplier_data}), status.HTTP_200_OK

#----------------------Supplier-List---------------------#

#----------------------Supplier-Details---------------------#

@name_space.route("/supplieDetails/<int:supplier_id>")	
class supplieDetails(Resource):
	def get(self,supplier_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT *
			FROM `supplier`			
			WHERE `supplier_id` = %s """)

		get_data = (supplier_id)
		count_supplier = cursor.execute(get_query,get_data)

		if count_supplier >0:
			supplier_data = cursor.fetchone()			
			supplier_data['last_update_ts'] = str(supplier_data['last_update_ts'])
		else:
			supplier_data = []


		return ({"attributes": {
		    		"status_desc": "supplier_details",
		    		"status": "success"
		    	},
		    	"responseList":supplier_data}), status.HTTP_200_OK


#----------------------Supplier-Details---------------------#

#----------------------Update-Supplier---------------------#

@name_space.route("/UpdateSupplier/<int:supplier_id>/<int:organisation_id>")
class UpdateSupplier(Resource):
	@api.expect(supplier_putmodel)
	def put(self,supplier_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		if details and "phoneno" in details:
			phoneno = details['phoneno']

			get_query_with_supplier_id = ("""SELECT *
				FROM `supplier` WHERE `phoneno` = %s and `organisation_id` = %s and `supplier_id` = %s""")
			getDataWithSupplierId = (phoneno,organisation_id,supplier_id)
			count_supplier_with_supplier_id = cursor.execute(get_query_with_supplier_id,getDataWithSupplierId)

			if count_supplier_with_supplier_id > 0:
			 	update_query = ("""UPDATE `supplier` SET `phoneno` = %s
							WHERE `supplier_id` = %s """)
			 	update_data = (phoneno,supplier_id)
			 	cursor.execute(update_query,update_data)
			else:
				get_query = ("""SELECT *
				FROM `supplier` WHERE `phoneno` = %s and `organisation_id` = %s""")
				getData = (phoneno,organisation_id)
				count_supplier = cursor.execute(get_query,getData)

				if count_supplier > 0:
					return ({"attributes": {
					    		"status_desc": "Update Supplier",
					    		"status": "error",
					    		"message":" Phone No Already Exist"
					    	},
					    	"responseList":{} }), status.HTTP_200_OK
				else:
					update_query = ("""UPDATE `supplier` SET `phoneno` = %s
							WHERE `supplier_id` = %s """)
					update_data = (phoneno,supplier_id)
					cursor.execute(update_query,update_data)

		if details and "supplier_name" in details:
			supplier_name = details['supplier_name']
			update_query = ("""UPDATE `supplier` SET `supplier_name` = %s
							WHERE `supplier_id` = %s """)
			update_data = (supplier_name,supplier_id)
			cursor.execute(update_query,update_data)

		if details and "address" in details:
			address = details['address']
			update_query = ("""UPDATE `supplier` SET `address` = %s
							WHERE `supplier_id` = %s """)
			update_data = (address,supplier_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Supplier",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Supplier---------------------#

#----------------------Supplier-Order-List---------------------#

@name_space_supplier_order.route("/supplierOrderList/<int:supplier_id>/<int:organisation_id>")	
class supplierOrderList(Resource):
	def get(self,supplier_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT *
			FROM `supplier_order`			
			WHERE `organisation_id` = %s and `supplier_id` = %s""")

		get_data = (organisation_id,supplier_id)
		count_supplier_order = cursor.execute(get_query,get_data)

		if count_supplier_order >0:
			supplier_order_data = cursor.fetchall()
			for key,data in enumerate(supplier_order_data):
				supplier_order_data[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			supplier_order_data = []


		return ({"attributes": {
		    		"status_desc": "supplier_order_details",
		    		"status": "success"
		    	},
		    	"responseList":supplier_order_data}), status.HTTP_200_OK


#----------------------Supplier-Order-List---------------------#

#----------------------Supplier-Order-Details---------------------#

@name_space_supplier_order.route("/supplieOrderDetails/<int:supplier_order_id>")	
class supplieOrderDetails(Resource):
	def get(self,supplier_order_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT *
			FROM `supplier_order`			
			WHERE `supplier_order_id` = %s """)

		get_data = (supplier_order_id)
		count_supplier = cursor.execute(get_query,get_data)

		if count_supplier >0:
			supplier_order_data = cursor.fetchone()
			get_supplier_query = ("""SELECT *
				FROM `supplier`			
				WHERE `supplier_id` = %s""")	
			get_supplier_data = (supplier_order_data['supplier_id'])		
			count_supplier = cursor.execute(get_supplier_query,get_supplier_data)
			if count_supplier > 0:
				supplier_data = cursor.fetchone()
				supplier_order_data['supplier_name'] = supplier_data['supplier_name']
			supplier_order_data['last_update_ts'] = str(supplier_order_data['last_update_ts'])
		else:
			supplier_order_data = []


		return ({"attributes": {
		    		"status_desc": "supplier_details",
		    		"status": "success"
		    	},
		    	"responseList":supplier_order_data}), status.HTTP_200_OK


#----------------------Supplier-Order-Details---------------------#

#----------------------Update-Supplier-Order---------------------#

@name_space_supplier_order.route("/UpdateSupplierOrder/<int:supplier_order_id>")
class UpdateSupplierOrder(Resource):
	@api.expect(supplier_order_putmodel)
	def put(self,supplier_order_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		if details and "order_name" in details:
			order_name = details['order_name']
			update_query = ("""UPDATE `supplier_order` SET `order_name` = %s
							WHERE `supplier_order_id` = %s """)
			update_data = (order_name,supplier_order_id)
			cursor.execute(update_query,update_data)

		if details and "order_date" in details:
			order_date = details['order_date']
			update_query = ("""UPDATE `supplier_order` SET `order_date` = %s
							WHERE `supplier_order_id` = %s """)
			update_data = (order_date,supplier_order_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Supplier Order",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Supplier-Order---------------------#

#--------------------Add-Supplier-Order-------------------------#

@name_space_supplier_order.route("/AddSupplierOrder")
class AddSupplierOrder(Resource):
	@api.expect(supplier_order_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		order_name = details['order_name']
		order_date = details['order_date']
		supplier_id = details['supplier_id']
		supplier_order_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		
		insert_query = ("""INSERT INTO `supplier_order`(`order_name`,`order_date`,`supplier_id`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")
		data = (order_name,order_date,supplier_id,supplier_order_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		supplier_id = cursor.lastrowid

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "supplier_Order_details",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList": details}), status.HTTP_200_OK

#--------------------Add-Order-Supplier-------------------------#

#----------------------Supplier-Order-Product-List---------------------#

@name_space_supplier_order.route("/supplierOrderProductList/<int:supplier_order_id>/<int:organisation_id>")	
class supplierOrderProductList(Resource):
	def get(self,supplier_order_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT *
			FROM `product_transaction`			
			WHERE `organisation_id` = %s and `supplier_order_id` = %s""")

		get_data = (organisation_id,supplier_order_id)
		count_supplier_order_product = cursor.execute(get_query,get_data)

		if count_supplier_order_product >0:
			supplier_order_product_data = cursor.fetchall()
			for key,data in enumerate(supplier_order_product_data):

				get_product_meta_query = ("""SELECT p.`product_name`,pm.`meta_key_text`
					FROM `product_meta` pm
					INNER JOIN `product` p ON p.`product_id` = pm.`product_id`			
					WHERE `product_meta_id` = %s""")
				get_product_meta_data = (data['product_meta_id'])
				cursor.execute(get_product_meta_query,get_product_meta_data)

				product_data = cursor.fetchone()

				a_string = product_data['meta_key_text']
				a_list = a_string.split(',')

				met_key = {}

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

					met_key.update({met_key_data['meta_key']:met_key_value_data['meta_key_value']})

					supplier_order_product_data[key]['met_key_value'] = met_key

				supplier_order_product_data[key]['product_name'] = product_data['product_name']

				get_city_query =("""SELECT *
					FROM `retailer_store`			
					WHERE `retailer_store_id` = %s""")
				get_city_data = (data['retailer_store_id'])
				cursor.execute(get_city_query,get_city_data)

				city_data = cursor.fetchone()

				supplier_order_product_data[key]['city'] = city_data['city']

				get_retailer_store_query =("""SELECT *
					FROM `retailer_store_stores`			
					WHERE `retailer_store_store_id` = %s""")
				get_retailer_store_data = (data['retailer_store_store_id'])
				cursor.execute(get_retailer_store_query,get_retailer_store_data)

				retailer_store_data = cursor.fetchone()

				supplier_order_product_data[key]['store_name'] = retailer_store_data['store_name']
				supplier_order_product_data[key]['store_address'] = retailer_store_data['address']


				supplier_order_product_data[key]['last_update_ts'] = str(data['last_update_ts'])
		else:
			supplier_order_data = []

		connection.commit()
		cursor.close()
			
		return ({"attributes": {
		    		"status_desc": "supplier_order_details",
		    		"status": "success"
		    	},
		    	"responseList":supplier_order_product_data}), status.HTTP_200_OK

#----------------------Supplier-Order-Product-List---------------------#

#--------------------Add-Supplier-Order-Product-------------------------#

@name_space_supplier_order.route("/AddSupplierOrderProduct")
class AddSupplierOrderProduct(Resource):
	@api.expect(supplier_order_product_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		retailer_store_store_id = details['retailer_store_store_id']

		get_retailer_store_query =("""SELECT *
					FROM `retailer_store_stores`			
					WHERE `retailer_store_store_id` = %s""")
		get_retailer_store_data = (retailer_store_store_id)
		cursor.execute(get_retailer_store_query,get_retailer_store_data)

		retailer_store_data = cursor.fetchone()

		retailer_store_id = retailer_store_data['retailer_store_id']
		product_meta_id = details['product_meta_id']
		supplier_stock = details['supplier_stock']
		price_per_unit = details['price_per_unit']
		supplier_order_id = details['supplier_order_id']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_product_stock_query = ("""SELECT *
			FROM `product_inventory`			
			WHERE `product_meta_id` = %s and `retailer_store_id` = %s and `retailer_store_store_id` = %s and `organisation_id` = %s""")
		get_product_stock_data = (product_meta_id,retailer_store_id,retailer_store_store_id,organisation_id)

		count_product_stock = cursor.execute(get_product_stock_query,get_product_stock_data)

		print(cursor._last_executed)

		if count_product_stock > 0:
			product_stock = cursor.fetchone()
			previous_stock = product_stock['stock']
			updated_stock = previous_stock+supplier_stock
			price_per_unit = price_per_unit
			total_purchase_amount = price_per_unit * supplier_stock

			product_transaction_status = 1

			insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`supplier_stock`,`price_per_unit`,`total_purchase_amount`,`updated_stock`,`retailer_store_id`,`retailer_store_store_id`,`supplier_order_id`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			insert_product_transaction_data = (product_meta_id,previous_stock,supplier_stock,price_per_unit,total_purchase_amount,updated_stock,retailer_store_id,retailer_store_store_id,supplier_order_id,product_transaction_status,organisation_id,last_update_id)
			cursor.execute(insert_product_transaction_query,insert_product_transaction_data)

			update_query = ("""UPDATE `product_inventory` SET `stock` = %s
							WHERE `retailer_store_id` = %s and `retailer_store_store_id` = %s and `organisation_id` = %s""")
			update_data = (updated_stock,retailer_store_id,retailer_store_store_id,organisation_id)
			cursor.execute(update_query,update_data)
		else:
			previous_stock = 0
			updated_stock = previous_stock+supplier_stock
			price_per_unit = price_per_unit
			total_purchase_amount = price_per_unit * supplier_stock
			product_inventory_status = 1
			product_transaction_status = 1

			insert_product_inventory_query = ("""INSERT INTO `product_inventory`(`product_meta_id`,`stock`,`retailer_store_id`,`retailer_store_store_id`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s)""")
			insert_product_inventory_data = (product_meta_id,supplier_stock,retailer_store_id,retailer_store_store_id,product_inventory_status,organisation_id,last_update_id)
			cursor.execute(insert_product_inventory_query,insert_product_inventory_data)

			insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`supplier_stock`,`price_per_unit`,`total_purchase_amount`,`updated_stock`,`retailer_store_id`,`retailer_store_store_id`,`supplier_order_id`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			insert_product_transaction_data = (product_meta_id,previous_stock,supplier_stock,price_per_unit,total_purchase_amount,updated_stock,retailer_store_id,retailer_store_store_id,supplier_order_id,product_transaction_status,organisation_id,last_update_id)
			cursor.execute(insert_product_transaction_query,insert_product_transaction_data)

		get_supplier_order_query = ("""SELECT *
			FROM `supplier_order`			
			WHERE `supplier_order_id` = %s and `organisation_id` = %s""")
		get_supplier_order_data = (supplier_order_id,organisation_id)

		count_supplier_order = cursor.execute(get_supplier_order_query,get_supplier_order_data)		

		if count_supplier_order > 0:
			supplier_order = cursor.fetchone()
			amount = price_per_unit * supplier_stock
			total_purchase_amount = supplier_order['total_purchase_amount'] + amount
		else:
			amount = price_per_unit * supplier_stock
			total_purchase_amount = amount

		print(total_purchase_amount)

		update_query = ("""UPDATE `supplier_order` SET `total_purchase_amount` = %s
							WHERE `supplier_order_id` = %s and `organisation_id` = %s""")
		update_data = (total_purchase_amount,supplier_order_id,organisation_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "supplier_Order_product_details",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList": details}), status.HTTP_200_OK

#--------------------Add-Supplier-Order-Product-------------------------#

#--------------------Add-Supplier-Order-Payment-------------------------#

@name_space_supplier_order.route("/AddSupplierOrderPayment")
class AddSupplierOrderPayment(Resource):
	@api.expect(supplier_order_payment_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		supplier_order_id = details['supplier_order_id']
		amount = details['amount']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		insert_supplier_order_payment_query = ("""INSERT INTO `supplier_order_payment`(`supplier_order_id`,`amount`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")
		insert_supplier_order_payment_data = (supplier_order_id,amount,organisation_id,last_update_id)
		cursor.execute(insert_supplier_order_payment_query,insert_supplier_order_payment_data)

		get_supplier_order_query = ("""SELECT *
			FROM `supplier_order`			
			WHERE `supplier_order_id` = %s and `organisation_id` = %s""")
		get_supplier_order_data = (supplier_order_id,organisation_id)

		count_supplier_order = cursor.execute(get_supplier_order_query,get_supplier_order_data)		

		if count_supplier_order > 0:
			supplier_order = cursor.fetchone()
			total_paid_amount = supplier_order['total_paid_amount'] + amount
		else:
			total_paid_amount = amount

		print(total_paid_amount)	
		
		update_query = ("""UPDATE `supplier_order` SET `total_paid_amount` = %s
							WHERE `supplier_order_id` = %s and `organisation_id` = %s""")
		update_data = (total_paid_amount,supplier_order_id,organisation_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "supplier_Order_payment",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList": details}), status.HTTP_200_OK

#--------------------Add-Supplier-Order-Payment-------------------------#

#--------------------Supplier-Order-Payment-List-------------------------#

@name_space_supplier_order.route("/supplierOrderPyamnetList/<int:supplier_order_id>/<int:organisation_id>")	
class supplierOrderPyamnetList(Resource):
	def get(self,supplier_order_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT sop.*
				FROM `supplier_order_payment` sop			
				INNER JOIN `supplier_order` so ON so.`supplier_order_id` = sop.`supplier_order_id`
				WHERE  sop.`organisation_id` = %s and sop.`supplier_order_id` = %s""")
		get_data = (organisation_id,supplier_order_id)
		cursor.execute(get_query,get_data)

		supplier_order_payment = cursor.fetchall()

		for key,data in enumerate(supplier_order_payment):
			supplier_order_payment[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "grocery_productlist",
		    		"status": "success"
		    	},
		    	"responseList":supplier_order_payment}), status.HTTP_200_OK

#--------------------Supplier-Order-Payment-List-------------------------#

#--------------------Grocery-Product-List-------------------------#

@name_space_product.route("/groceryProductList/<int:organisation_id>")	
class groceryProductList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`
				FROM `product` p				
				INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
				WHERE  pom.`organisation_id` = %s and p.`category_id` = 135""")
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		return ({"attributes": {
		    		"status_desc": "grocery_productlist",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#--------------------Grocery-Product-List-------------------------#

#--------------------Grocery-Product-List-With-Variant-------------------------#

@name_space_product.route("/groceryProductListWithVariant/<int:organisation_id>/<int:product_id>")	
class groceryProductListWithVariant(Resource):
	def get(self,organisation_id,product_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,pm.`meta_key_text`,pm.`product_meta_id`
				FROM `product` p
				INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
				INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
				WHERE  pom.`organisation_id` = %s and p.`category_id` = 135 and p.`product_id` = %s""")
		get_data = (organisation_id,product_id)
		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall() 

		for key,data in enumerate(product_data):

			met_key = {}

			a_string = data['meta_key_text']
			a_list = a_string.split(',')

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

				met_key.update({met_key_data['meta_key']:met_key_value_data['meta_key_value']})

				product_data[key]['met_key_value'] = met_key


		return ({"attributes": {
		    		"status_desc": "supplier_order_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#--------------------Grocery-Product-List-With-Variant-------------------------#

#--------------------Retailer-Store-List-------------------------#

@name_space_retailer_store.route("/retailerStoreList/<int:organisation_id>")	
class retailerStoreList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT rss.`retailer_store_store_id`,rss.`store_name`,rss.`address`,rss.`latitude`,rss.`longitude`,rss.`phoneno`
					FROM `retailer_store_stores` rss 
					where rss.`organisation_id` = %s""")	
		get_data = (organisation_id)
		count_reatiler_store = cursor.execute(get_query,get_data)

		if count_reatiler_store > 0:
			retail_store_data = cursor.fetchall()
		else:
			retail_store_data = []

		return ({"attributes": {
		    		"status_desc": "retail_store_details",
		    		"status": "success"
		    	},
		    	"responseList":retail_store_data}), status.HTTP_200_OK

#--------------------Retailer-Store-List-------------------------#

#--------------------Total-Order-Amount-------------------------#

@name_space_supplier_order.route("/totalOrderAmountByOrderID/<int:organisation_id>/<int:supplier_order_id>")	
class retailerStoreList(Resource):
	def get(self,organisation_id,supplier_order_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query =  ("""SELECT sum(`total_purchase_amount`) as total_pruchase_amount
			FROM `product_transaction`			
			WHERE `organisation_id` = %s and `supplier_order_id` = %s""")

		get_data = (organisation_id,supplier_order_id)
		count_supplier_order_product = cursor.execute(get_query,get_data)

		if count_supplier_order_product >0:			
			supplier_order_product_data = cursor.fetchone()
			total_order_product_amount = supplier_order_product_data['total_pruchase_amount']

		else:
			total_order_product_amount = 0

		return ({"attributes": {
		    		"status_desc": "order_product",
		    		"status": "success"
		    	},
		    	"responseList":total_order_product_amount}), status.HTTP_200_OK	

#--------------------Total-Order-Amount-------------------------#


#--------------------Supllier-Order-History-With-Date-Range-------------------------#

@name_space_supplier_order.route("/SupplierOrderHistorywithDateRange/<int:supplier_id>/<int:organisation_id>/<string:filterkey>/<string:start_date>/<string:end_date>")	
class SupplierOrderHistorywithDateRange(Resource):
	def get(self,supplier_id,organisation_id,filterkey,start_date,end_date):
		connection = mysql_connection()
		cursor = connection.cursor()

		if filterkey == 'today':
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			get_query =  ("""SELECT *
			FROM `supplier_order`			
			WHERE `organisation_id` = %s and `supplier_id` = %s and `order_date` = %s""")

			get_data = (organisation_id,supplier_id,today_date)
			count_supplier_order = cursor.execute(get_query,get_data)

			if count_supplier_order > 0:
				supplier_order_data = cursor.fetchall()
				for key,data in enumerate(supplier_order_data):
					supplier_order_data[key]['last_update_ts'] = str(data['last_update_ts'])
			else:
				supplier_order_data = []

		elif filterkey == 'yesterday':
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_query =  ("""SELECT *
			FROM `supplier_order`			
			WHERE `organisation_id` = %s and `supplier_id` = %s and `order_date` = %s""")

			get_data = (organisation_id,supplier_id,yesterday)
			count_supplier_order = cursor.execute(get_query,get_data)

			if count_supplier_order > 0:
				supplier_order_data = cursor.fetchall()
				for key,data in enumerate(supplier_order_data):
					supplier_order_data[key]['last_update_ts'] = str(data['last_update_ts'])
			else:
				supplier_order_data = []

		elif filterkey == 'last7day':
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_query =  ("""SELECT *
			FROM `supplier_order`			
			WHERE `organisation_id` = %s and `supplier_id` = %s and `order_date` >= %s and `order_date` <= %s """)

			get_data = (organisation_id,supplier_id,start_date,end_date)
			count_supplier_order = cursor.execute(get_query,get_data)

			if count_supplier_order > 0:
				supplier_order_data = cursor.fetchall()
				for key,data in enumerate(supplier_order_data):
					supplier_order_data[key]['last_update_ts'] = str(data['last_update_ts'])
			else:
				supplier_order_data = []

		elif filterkey == 'thismonth':
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_query =  ("""SELECT *
			FROM `supplier_order`			
			WHERE `organisation_id` = %s and `supplier_id` = %s and `order_date` >= %s and `order_date` <= %s """)

			get_data = (organisation_id,supplier_id,start_date,end_date)
			count_supplier_order = cursor.execute(get_query,get_data)

			if count_supplier_order > 0:
				supplier_order_data = cursor.fetchall()
				for key,data in enumerate(supplier_order_data):
					supplier_order_data[key]['last_update_ts'] = str(data['last_update_ts'])
			else:
				supplier_order_data = []

		elif filterkey == 'lifetime':
			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_query =  ("""SELECT *
			FROM `supplier_order`			
			WHERE `organisation_id` = %s and `supplier_id` = %s and `order_date` >= %s and `order_date` <= %s """)

			get_data = (organisation_id,supplier_id,start_date,end_date)
			count_supplier_order = cursor.execute(get_query,get_data)

			if count_supplier_order > 0:
				supplier_order_data = cursor.fetchall()
				for key,data in enumerate(supplier_order_data):
					supplier_order_data[key]['last_update_ts'] = str(data['last_update_ts'])
			else:
				supplier_order_data = []

		elif filterkey == 'custom date':
			if start_date != 'NA' and end_date != 'NA':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)

				get_query =  ("""SELECT *
				FROM `supplier_order`			
				WHERE `organisation_id` = %s and `supplier_id` = %s and `order_date` >= %s and `order_date` <= %s """)

				get_data = (organisation_id,supplier_id,start_date,end_date)
				count_supplier_order = cursor.execute(get_query,get_data)

				if count_supplier_order > 0:
					supplier_order_data = cursor.fetchall()
					for key,data in enumerate(supplier_order_data):
						supplier_order_data[key]['last_update_ts'] = str(data['last_update_ts'])
				else:
					supplier_order_data = []
			else:
				supplier_order_data = []

		return ({"attributes": {
		    		"status_desc": "supplier_order_details",
		    		"status": "success"
		    	},
		    	"responseList":supplier_order_data}), status.HTTP_200_OK

#--------------------Supllier-Order-History-With-Date-Range-------------------------#
