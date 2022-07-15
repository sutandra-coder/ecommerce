from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import datetime
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
from pyfcm import FCMNotification
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

ecommerce_customer_filteration = Blueprint('ecommerce_customer_filteration', __name__)
api = Api(ecommerce_customer_filteration, version='1.0', title='Ecommerce API',
    description='Ecommerce API')

name_space = api.namespace('EcommerceCustomerFilteration',description='Ecommerce Customer Filteration')

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#-----------------------------------------------------------------#

#--------------------------------------------------------------------#
@name_space.route("/getCustomerListByFilter/<string:sdate>/<int:pincode>/<string:model>/<string:brand>/<string:pcost>/<int:organisation_id>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByFilter(Resource):
	def get(self,sdate,pincode,model,brand,pcost,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateOrganizationId/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,start,limit,page)
			
			
		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePincodeOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandModelOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePurchaseCostOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandPurchaseCostOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,start,limit,page)
			

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0:
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,start,limit,page)
		

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStore/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,retailer_store_id,start,limit,page)
			
		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,retailer_store_id,start,limit,page)
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,retailer_store_id,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,retailer_store_id,start,limit,page)
		
		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,retailer_store_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,retailer_store_id,start,limit,page)
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,retailer_store_id,start,limit,page)

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0:
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,retailer_store_id,start,limit,page)

		
		print(filterURL)	
		filterRes = requests.get(filterURL).json()	
		connection.commit()
		cursor.close()
		return filterRes

		#---------------------------------------------------------------------#

#--------------------------------------------------------------------#
@name_space.route("/getCustomerListByFilterNew/<string:sdate>/<int:pincode>/<string:model>/<string:brand>/<string:pcost>/<int:organisation_id>/<int:retailer_store_id>/<string:purchase_date_range>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByFilterNew(Resource):
	def get(self,sdate,pincode,model,brand,pcost,organisation_id,retailer_store_id,purchase_date_range):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateOrganizationId/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,start,limit,page)
			
			
		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n': 
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePincodeOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandModelOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDatePurchaseCostOrganizationId/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByDateBrandPurchaseCostOrganizationId/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,start,limit,page)
			
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,start,limit,page)
			

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "retcustomer_notify/EcommerceNotification/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,start,limit,page)
		

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdRetailStore/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,retailer_store_id,start,limit,page)
			
		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,retailer_store_id,start,limit,page)
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,retailer_store_id,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,retailer_store_id,start,limit,page)
		
		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,retailer_store_id,start,limit,page)
			filterRes = requests.get(filterURL).json()
		
		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,retailer_store_id,start,limit,page)
		
		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,retailer_store_id,start,limit,page)

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range == 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,retailer_store_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDate/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,purchase_date_range,start,limit,page)

		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n': 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDate/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,purchase_date_range,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDate/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,purchase_date_range,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDate/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,purchase_date_range,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,purchase_date_range,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,purchase_date_range,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDate/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,purchase_date_range,start,limit,page)

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id == 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationId/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,purchase_date_range,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if date != None and pincode  != 0 and model  == 'n' and brand == 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n': 
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost == '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand == 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pcost,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if date != None and pincode  == 0 and model  == 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,pcost,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if date != None and pincode  == 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,brand,model,pcost,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)

		if date != None and pincode  != 0 and model  != 'n' and brand != 'n' and pcost != '0' and organisation_id != None and retailer_store_id != 0 and purchase_date_range != 'n':
			filterURL = BASE_URL + "ecommerce_customer_filteration/EcommerceCustomerFilteration/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/{}/{}/{}/{}/{}/{}/{}/{}?start={}&limit={}&page={}".format(sdate,pincode,brand,model,pcost,organisation_id,purchase_date_range,retailer_store_id,start,limit,page)


		
		print(filterURL)	
		filterRes = requests.get(filterURL).json()	
		connection.commit()
		cursor.close()
		return filterRes

		#---------------------------------------------------------------------#

@name_space.route("/getCustomerListByDateOrganizationIdRetailStore/<string:sdate>/<int:organisation_id>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateOrganizationIdRetailStore(Resource):
	def get(self,sdate,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		print('hiii')

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT `admin_id` FROM `admins` a
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
			date(`date_of_creation`) between %s and %s""",(organisation_id,organisation_id,retailer_store_id,sdate,today))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(`admin_id`)as count FROM `admins` a
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
			date(`date_of_creation`) between %s and %s""",(organisation_id,organisation_id,retailer_store_id,sdate,today))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` a
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
				WHERE `role_id`=4 and 
				a.`status`=1 and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
				date(a.`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",(organisation_id,organisation_id,retailer_store_id,sdate,today,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
				WHERE `role_id`=4 a.`status`=1 and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and 
				and admin_id>%s and date(a.`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",
				(organisation_id,organisation_id,retailer_store_id,sdate,today,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				if customerdata[i]['date_of_creation'] == '0000-00-00 00:00:00':
					customerdata[i]['date_of_creation'] = '0000-00-00 00:00:00'
				else:
					customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''
					
				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePincodeOrganizationIdRetailStore/<string:sdate>/<int:pincode>/<int:organisation_id>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePincodeOrganizationIdRetailStore(Resource):
	def get(self,sdate,pincode,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT a.`admin_id` FROM `admins` a
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
			date(a.`date_of_creation`) between %s and %s and a.`pincode` in (%s)""",(organisation_id,organisation_id,retailer_store_id,sdate,today,pincode))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(a.`admin_id`)as count FROM `admins` a
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
			date(a.`date_of_creation`) between %s and %s and a.`pincode` in (%s)""",
			(organisation_id,organisation_id,retailer_store_id,sdate,today,pincode))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` a
				 INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
				 WHERE a.`role_id`=4 and 
				a.`status`=1 and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and
			date(`date_of_creation`) between %s and %s  and `pincode` in (%s) order by admin_id ASC limit %s""",
			(organisation_id,organisation_id,retailer_store_id,sdate,today,pincode,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` a
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id` 
				WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
				and a.`admin_id`>%s and date(a.`date_of_creation`) between %s and %s and 
				pincode in (%s) order by admin_id ASC limit %s""",
				(organisation_id,organisation_id,retailer_store_id,start,sdate,today,pincode,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s """,(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandOrganizationIdRetailStore/<string:sdate>/<string:brand>/<int:organisation_id>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandOrganizationIdRetailStore(Resource):
	def get(self,sdate,brand,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		adminid = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT distinct(`admin_id`) FROM `admins` a
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			where a.`admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(a.`date_of_creation`) BETWEEN %s and %s and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
			(brand,organisation_id,organisation_id,sdate,today,organisation_id,organisation_id,retailer_store_id))

		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` a
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			where a.`admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(a.`date_of_creation`) BETWEEN %s and %s and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
			(brand,organisation_id,organisation_id,sdate,today,organisation_id,organisation_id,retailer_store_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ad.`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,organisation_id,organisation_id,retailer_store_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`) as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ad.`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,organisation_id,organisation_id,retailer_store_id,start,organisation_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0

		if prdcusmrDtls:

			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandModelOrganizationIdRetailStore/<string:sdate>/<string:brand>/<string:model>/<int:organisation_id>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandModelOrganizationIdRetailStore(Resource):
	def get(self,sdate,brand,model,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		split_model = model.split(',')

		customerList_query = cursor.execute("""SELECT distinct(ad.`admin_id`)as 'count' FROM `admins` ad	
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`		
			where ad.`admin_id` in(SELECT distinct(`customer_id`) FROM `customer_product_mapping` cpm		 
			WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0)) and date(ad.`date_of_creation`) BETWEEN %s and %s and 
			ad.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
			(brand,organisation_id,split_model,sdate,today,organisation_id,organisation_id,retailer_store_id))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(ad.`admin_id`))as 'count' FROM `admins` ad	
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`		
			where ad.`admin_id` in(SELECT distinct(`customer_id`) FROM `customer_product_mapping` cpm		 
			WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0)) and date(ad.`date_of_creation`) BETWEEN %s and %s and 
			ad.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
			(brand,organisation_id,split_model,sdate,today,organisation_id,organisation_id,retailer_store_id))

		print(cursor._last_executed)

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ad.`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,split_model,organisation_id,organisation_id,retailer_store_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`) as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:			
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(ad.`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,split_model,start,organisation_id,organisation_id,retailer_store_id,sdate,today,limit))

			prdcusmrDtls = cursor.fetchall()
			
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0

		if next_url:
			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK


#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePurchaseCostOrganizationIdRetailStore/<string:sdate>/<string:pcost>/<int:organisation_id>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePurchaseCostOrganizationIdRetailStore(Resource):
	def get(self,sdate,pcost,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		scost = float(startingcost)
		ecost = float(endingcost)
		
		cursor.execute("""SELECT admin_id FROM `admins` a
			INNER JOIN `instamojo_payment_request` ipr on ipr.`user_id` = a.`admin_id`
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
			and date(`date_of_creation`) between %s and %s and ipr.`organisation_id` = %s and amount BETWEEN %s and %s""",
			(organisation_id,organisation_id,retailer_store_id,sdate,today,organisation_id,scost,ecost))
		userDtls = cursor.fetchall()		
		
		total_count = len(userDtls)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT admin_id FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
					and date(`date_of_creation`) between %s and %s""",
					(organisation_id,organisation_id,retailer_store_id,sdate,today))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))				

					if payment_count > 0:	
						customer_list_data.append({'admin_id':userDtls[i]['admin_id']})				
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:
				
					cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
						FROM `admins` where 
						`organisation_id`=%s and date(`date_of_creation`) 
						between %s and %s and `admin_id` in %s order by admin_id ASC limit %s""",
						(organisation_id,sdate,today,customerids,limit))

					prdcusmrDtls = cursor.fetchall()
					
					if prdcusmrDtls != None:
						for cid in range(len(prdcusmrDtls)):
							prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
							prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

							cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
							customertype = cursor.fetchone()
							if customertype:
								prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
							else:
								prdcusmrDtls[cid]['customertype'] = ''

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
								prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
							else:
								prdcusmrDtls[cid]['retailer_city'] = ""
								prdcusmrDtls[cid]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								prdcusmrDtls[cid]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								prdcusmrDtls[cid]['enquiery_count'] = 0
							
							scost = float(startingcost)
							ecost = float(endingcost) 

							cursor.execute("""SELECT `amount`as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
							print(cursor._last_executed)
							costDtls = cursor.fetchone()
							if costDtls['total'] != None:
								prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
							else:
								prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT admin_id FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s and date(`date_of_creation`) between %s and %s""",
					(organisation_id,organisation_id,retailer_store_id,sdate,today))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))				

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:
				
					cursor.execute("""SELECT `admin_id`,
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
						FROM `admins` where `organisation_id`=%s and date(`date_of_creation`) 
						between %s and %s and `admin_id` in %s and `admin_id`>%s order by admin_id ASC
						limit %s""",(organisation_id,sdate,today,customerids,start,limit))

					prdcusmrDtls = cursor.fetchall()
					if prdcusmrDtls:
						for cid in range(len(prdcusmrDtls)):
							prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
							prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

							cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
							customertype = cursor.fetchone()
							if customertype:
								prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
							else:
								prdcusmrDtls[cid]['customertype'] = ''

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
								prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
							else:
								prdcusmrDtls[cid]['retailer_city'] = ""
								prdcusmrDtls[cid]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								prdcusmrDtls[cid]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								prdcusmrDtls[cid]['enquiery_count'] = 0
							
							scost = float(startingcost)
							ecost = float(endingcost) 

							cursor.execute("""SELECT `amount`as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
							print(cursor._last_executed)
							costDtls = cursor.fetchone()
							if costDtls['total'] != None:
								prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
							else:
								prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []

			if prdcusmrDtls:

				page_next = page + 1			
				if cur_count < total_count:
					next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
				else:
					next_url = ''
			else:
				next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandPurchaseCostOrganizationIdRetailStore/<string:sdate>/<string:brand>/<string:pcost>/<int:organisation_id>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandPurchaseCostOrganizationId(Resource):
	def get(self,sdate,brand,pcost,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
					(brand,organisation_id,organisation_id,sdate,today,organisation_id,retailer_store_id))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			scost = float(startingcost)
			ecost = float(endingcost) 

			payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))		

			if payment_count > 0:
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})					
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hiii')

		total_count = len(details)
		print(total_count)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		
		else:
		
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id ASC limit %s""",
					(brand,organisation_id,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					
					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:

					print(customerids)

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
						`organisation_id` = %s ) and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
						(brand,organisation_id,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id ASC limit %s""",
					(brand,organisation_id,start,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					
					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
						`organisation_id` = %s ) and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and 
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
						(brand,organisation_id,start,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:
			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStore/<string:sdate>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByBrandModelPurchaseCostOrganizationIdRetailStore(Resource):
	def get(self,sdate,brand,model,pcost,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		split_model = model.split(',')

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
			WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id Asc""",
			(brand,organisation_id,split_model,organisation_id,sdate,today,organisation_id,retailer_store_id))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			scost = float(startingcost)
			ecost = float(endingcost)

			payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
			
			if payment_count > 0:
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})					
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hii')

		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id` 
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and `amount` BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					if payment_count > 0:						
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')	

					print(customerids)

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
						(brand,organisation_id,split_model,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost) 
					 	
						cursor.execute("""SELECT `amount` as total FROM 
							`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []
			else:

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,start,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				print(userDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and `amount` BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					if payment_count > 0:											
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')	

					print(customerids)

				if customerids:
				
					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
						ad.`admin_id` in %s and ad.`organisation_id`=%s and 
						date(`date_of_creation`) BETWEEN %s and %s limit %s""",
						(brand,organisation_id,split_model,start,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost) 
					 	
						cursor.execute("""SELECT `amount` as total FROM 
							`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0						
						
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:

			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#----------------------------------------------------------------#

#----------------------------------------------------------------#
@name_space.route("/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStore/<string:sdate>/<int:pincode>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdRetailStore(Resource):
	def get(self,sdate,pincode,brand,model,pcost,organisation_id,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		split_model = model.split(',')

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id` 
			WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in (%s) and 
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id Asc""",
			(brand,organisation_id,split_model,pincode,organisation_id,sdate,today,organisation_id,retailer_store_id))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			scost = float(startingcost)
			ecost = float(endingcost) 

			payment_count =  cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))
			
			if payment_count > 0:					
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hiii')
				
		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id` 
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,pincode,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost)
					payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					
					if payment_count > 0:						
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and ad.`pincode` in(%s) and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
						(brand,organisation_id,split_model,customerids,pincode,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						cscost = float(startingcost)
						ecost = float(endingcost)
					 	
						cursor.execute("""SELECT `amount` as total FROM 
							`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0			 	
						
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id` 
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,start,pincode,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost)
					payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s """,(userDtls[i]['admin_id'],organisation_id,scost,ecost))
					
					if payment_count > 0:
					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids :
				
					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s 
						and ad.`pincode` in(%s) and ad.`organisation_id`=%s and 
						date(`date_of_creation`) BETWEEN %s and %s limit %s""",
						(brand,organisation_id,split_model,start,customerids,pincode,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''
							
						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost)
					 	
						cursor.execute("""SELECT `amount` as total FROM 
							`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0						
						
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:

			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#--------------------------------------------------------------------#

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateOrganizationIdPurchaseDate/<string:sdate>/<int:organisation_id>/<string:purchase_date>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateOrganizationIdPurchaseDate(Resource):
	def get(self,sdate,organisation_id,purchase_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT distinct(a.`admin_id`) FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id` 
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`= %s and iip.`organisation_id` = %s and
			date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s""",(organisation_id,organisation_id,sdate,today,start_date,end_date))

		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(a.`admin_id`))as count FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id` 
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`= %s and iip.`organisation_id` = %s and
			date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s""",(organisation_id,organisation_id,sdate,today,start_date,end_date))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` a 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
				WHERE a.`role_id`=4 and 
				a.`status`=1 and a.`organisation_id`=%s and iip.`organisation_id` = %s and
				date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s order by admin_id ASC limit %s""",(organisation_id,organisation_id,sdate,today,start_date,end_date,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` a 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
				WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and iip.`organisation_id` = %s
				and admin_id>%s and date(`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s order by admin_id ASC limit %s""",
				(organisation_id,organisation_id,start,sdate,today,start_date,end_date,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				if customerdata[i]['date_of_creation'] == '0000-00-00 00:00:00':
					customerdata[i]['date_of_creation'] = '0000-00-00 00:00:00'
				else:
					customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''
					
				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT `amount` as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s """,(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePincodeOrganizationIdPurchaseDate/<string:sdate>/<int:pincode>/<int:organisation_id>/<string:purchase_date>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePincodeOrganizationIdPurchaseDate(Resource):
	def get(self,sdate,pincode,organisation_id,purchase_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT distinct(a.`admin_id`) FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id` 
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`= %s and iip.`organisation_id` = %s and
			date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and `pincode` in (%s) """,
			(organisation_id,organisation_id,sdate,today,start_date,end_date,pincode))

		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(a.`admin_id`))as count FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id` 
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`= %s and iip.`organisation_id` = %s and
			date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and `pincode` in (%s) """,
			(organisation_id,organisation_id,sdate,today,start_date,end_date,pincode))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` a 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
				WHERE a.`role_id`=4 and 
				a.`status`=1 and a.`organisation_id`=%s and iip.`organisation_id` = %s and
				date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and `pincode` in (%s) order by admin_id ASC limit %s""",
			(organisation_id,organisation_id,sdate,today,start_date,end_date,pincode,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` a 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
				WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and iip.`organisation_id` = %s
				and admin_id>%s and date(`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and
				pincode in (%s) order by admin_id ASC limit %s""",
				(organisation_id,organisation_id,start,sdate,today,start_date,end_date,pincode,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s """,(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandOrganizationIdPurchaseDate/<string:sdate>/<string:brand>/<int:organisation_id>/<string:purchase_date>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandOrganizationId(Resource):
	def get(self,sdate,brand,organisation_id,purchase_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		adminid = []

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT distinct(`admin_id`) FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(a.`date_of_creation`) BETWEEN %s and %s and a.`organisation_id`=%s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s""",
			(brand,organisation_id,organisation_id,sdate,today,organisation_id,organisation_id,start_date,end_date))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(a.`date_of_creation`) BETWEEN %s and %s and a.`organisation_id`=%s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s""",
			(brand,organisation_id,organisation_id,sdate,today,organisation_id,organisation_id,start_date,end_date))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,organisation_id,sdate,today,organisation_id,start_date,end_date,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`) as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,start,organisation_id,sdate,today,organisation_id,start_date,end_date,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandModelOrganizationIdPurchaseDate/<string:sdate>/<string:brand>/<string:model>/<int:organisation_id>/<string:purchase_date>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandModelOrganizationIdPurchaseDate(Resource):
	def get(self,sdate,brand,model,organisation_id,purchase_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		split_model = model.split(',')

		customerList_query = cursor.execute("""SELECT distinct(`admin_id`) FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
			where a.`admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0)) and date(a.`date_of_creation`) BETWEEN %s and %s and 
			a.`organisation_id`=%s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s""",
			(brand,organisation_id,split_model,sdate,today,organisation_id,organisation_id,start_date,end_date))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
			where a.`admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0)) and date(a.`date_of_creation`) BETWEEN %s and %s and 
			a.`organisation_id`=%s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s""",
			(brand,organisation_id,split_model,sdate,today,organisation_id,organisation_id,start_date,end_date))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s and 
				iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s
				order by admin_id ASC limit %s""",
				(brand,organisation_id,split_model,organisation_id,sdate,today,organisation_id,start_date,end_date,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`) as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s
				and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s
				order by admin_id ASC limit %s""",
				(brand,organisation_id,split_model,start,organisation_id,sdate,today,organisation_id,start_date,end_date,limit))

			prdcusmrDtls = cursor.fetchall()
			
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0


		if prdcusmrDtls:			
			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK


#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDate/<string:sdate>/<string:pcost>/<int:organisation_id>/<string:purchase_date>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePurchaseCostOrganizationIdPurchaseDate(Resource):
	def get(self,sdate,pcost,organisation_id,purchase_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))		

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		scost = float(startingcost)
		ecost = float(endingcost) 

		customerList_query = cursor.execute("""SELECT distinct(admin_id) FROM `admins` a
			INNER JOIN `instamojo_payment_request` ipr on ipr.`user_id` = a.`admin_id`
			WHERE a.`organisation_id`=%s and date(a.`date_of_creation`) between %s and %s and ipr.`organisation_id` = %s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",
			(organisation_id,sdate,today,organisation_id,scost,ecost,start_date,end_date))
		customer_list_data = cursor.fetchall()

		payment_count = cursor.execute("""SELECT distinct(admin_id) FROM `admins` a
			INNER JOIN `instamojo_payment_request` ipr on ipr.`user_id` = a.`admin_id`
			WHERE a.`organisation_id`=%s and date(a.`date_of_creation`) between %s and %s and ipr.`organisation_id` = %s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",
			(organisation_id,sdate,today,organisation_id,scost,ecost,start_date,end_date))
		userDtls = cursor.fetchall()		
		
		total_count = len(userDtls)
		print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT admin_id FROM `admins` a
					WHERE a.`organisation_id`=%s and date(a.`date_of_creation`) between %s and %s""",
					(organisation_id,sdate,today))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:
				
					cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
						FROM `admins` where 
						`organisation_id`=%s and date(`date_of_creation`) 
						between %s and %s and `admin_id` in %s order by admin_id ASC limit %s""",
						(organisation_id,sdate,today,customerids,limit))

					prdcusmrDtls = cursor.fetchall()
					
					if prdcusmrDtls != None:
						for cid in range(len(prdcusmrDtls)):
							prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
							prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

							cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
							customertype = cursor.fetchone()
							if customertype:
								prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
							else:
								prdcusmrDtls[cid]['customertype'] = ''

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
								prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
							else:
								prdcusmrDtls[cid]['retailer_city'] = ""
								prdcusmrDtls[cid]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								prdcusmrDtls[cid]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								prdcusmrDtls[cid]['enquiery_count'] = 0
							
							scost = float(startingcost)
							ecost = float(endingcost) 

							cursor.execute("""SELECT `amount`as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
							print(cursor._last_executed)
							costDtls = cursor.fetchone()
							if costDtls['total'] != None:
								prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
							else:
								prdcusmrDtls[cid]['purchase_cost'] = 0
					else:
						prdcusmrDtls =[]
			else:
				cursor.execute("""SELECT admin_id FROM `admins` a
					WHERE a.`organisation_id`=%s and date(a.`date_of_creation`) between %s and %s""",
					(organisation_id,sdate,today))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					print(cursor._last_executed)

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print(userDtls[i]['admin_id'])				

				if customerids:
				
					cursor.execute("""SELECT `admin_id`,
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
						FROM `admins` where `organisation_id`=%s and date(`date_of_creation`) 
						between %s and %s and `admin_id` in %s and `admin_id`>%s order by admin_id ASC
						limit %s""",(organisation_id,sdate,today,customerids,start,limit))

					prdcusmrDtls = cursor.fetchall()
					if prdcusmrDtls:
						for cid in range(len(prdcusmrDtls)):
							prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
							prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

							cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
							customertype = cursor.fetchone()
							if customertype:
								prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
							else:
								prdcusmrDtls[cid]['customertype'] = ''

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
								prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
							else:
								prdcusmrDtls[cid]['retailer_city'] = ""
								prdcusmrDtls[cid]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								prdcusmrDtls[cid]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								prdcusmrDtls[cid]['enquiery_count'] = 0
							
							scost = float(startingcost)
							ecost = float(endingcost) 

							cursor.execute("""SELECT `amount`as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
							print(cursor._last_executed)
							costDtls = cursor.fetchone()
							if costDtls['total'] != None:
								prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
							else:
								prdcusmrDtls[cid]['purchase_cost'] = 0
					else:
						prdcusmrDtls = []
				print(cursor._last_executed)

		if prdcusmrDtls:
			page_next = page + 1			
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDate/<string:sdate>/<string:brand>/<string:pcost>/<int:organisation_id>/<string:purchase_date>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDate(Resource):
	def get(self,sdate,brand,pcost,organisation_id,purchase_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		cursor.execute("""SELECT distinct(`admin_id`)as 'admin_id' FROM `admins` a			
			where a.`admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(a.`date_of_creation`) BETWEEN %s and %s and a.`organisation_id`=%s""",
			(brand,organisation_id,organisation_id,sdate,today,organisation_id))		

		userDtls = cursor.fetchall()		

		for i in range(len(userDtls)):			
			scost = float(startingcost)
			ecost = float(endingcost) 

			payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
			

			if payment_count > 0:	
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})				
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hiii')
		
		total_count = len(details)
		print(total_count)
		cur_count = int(page) * int(limit)		
	
		if total_count == 0:
			prdcusmrDtls = []
		
		else:
		
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):					
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				print(customerids)		

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
						`organisation_id` = %s ) and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and 
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
						(brand,organisation_id,customerids,organisation_id,sdate,today,limit))

					print(cursor._last_executed)

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,start,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
						`organisation_id` = %s ) and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and 
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
						(brand,organisation_id,start,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:
			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDate/<string:sdate>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>/<string:purchase_date>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDate(Resource):
	def get(self,sdate,brand,model,pcost,organisation_id,purchase_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		split_model = model.split(',')

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc""",
			(brand,organisation_id,split_model,organisation_id,sdate,today))

		userDtls = cursor.fetchall()

		print(userDtls)

		for i in range(len(userDtls)):
			print(userDtls[i]['admin_id'])
			scost = float(startingcost)
			ecost = float(endingcost)

			payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
			
			if payment_count > 0:
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})					
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hii')

		total_count = len(details)
		print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and `amount` BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')	

					print(customerids)			

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
						(brand,organisation_id,split_model,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,start,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				print(userDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					print(cursor._last_executed)
					if payment_count > 0:						
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print(userDtls[i]['admin_id'])	
				print(customerids)									

				if customerids:
				
					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s limit %s""",
						(brand,organisation_id,split_model,start,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
					
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:

			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#----------------------------------------------------------------#

@name_space.route("/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDate/<string:sdate>/<int:pincode>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>/<string:purchase_date>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDate(Resource):
	def get(self,sdate,pincode,brand,model,pcost,organisation_id,purchase_date):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		split_model = model.split(',')

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in (%s) and 
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc""",
			(brand,organisation_id,split_model,pincode,organisation_id,sdate,today))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			scost = float(startingcost)
			ecost = float(endingcost) 

			payment_count =  cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
			
			if payment_count > 0:
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})					
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hiii')
				
		total_count = len(details)
		print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,pincode,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost)
					payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					
					if payment_count > 0:
					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')			

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and ad.`pincode` in(%s) and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
						(brand,organisation_id,split_model,customerids,pincode,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				 	
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,start,pincode,organisation_id,sdate,today,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost)

					payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					
					if payment_count > 0:						
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				if customerids:
				
					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s 
						and ad.`pincode` in(%s) and ad.`organisation_id`=%s and 
						date(`date_of_creation`) BETWEEN %s and %s limit %s""",
						(brand,organisation_id,split_model,start,customerids,pincode,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''
							
						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0			 	
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:

			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateOrganizationIdPurchaseDateRetailStore/<string:sdate>/<int:organisation_id>/<string:purchase_date>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateOrganizationIdPurchaseDate(Resource):
	def get(self,sdate,organisation_id,purchase_date,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT distinct(a.`admin_id`) FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id` 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`= %s and iip.`organisation_id` = %s and
			date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",(organisation_id,organisation_id,sdate,today,start_date,end_date,organisation_id,retailer_store_id))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(a.`admin_id`)) as count FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id` 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`= %s and iip.`organisation_id` = %s and
			date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",(organisation_id,organisation_id,sdate,today,start_date,end_date,organisation_id,retailer_store_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` a 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
				WHERE a.`role_id`=4 and 
				a.`status`=1 and a.`organisation_id`=%s and iip.`organisation_id` = %s and
				date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id ASC limit %s""",(organisation_id,organisation_id,sdate,today,start_date,end_date,organisation_id,retailer_store_id,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` a 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
				WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and iip.`organisation_id` = %s
				and admin_id>%s and date(`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id ASC limit %s""",
				(organisation_id,organisation_id,start,sdate,today,start_date,end_date,organisation_id,retailer_store_id,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				if customerdata[i]['date_of_creation'] == '0000-00-00 00:00:00':
					customerdata[i]['date_of_creation'] = '0000-00-00 00:00:00'
				else:
					customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''
					
				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT `amount` as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s """,(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStore/<string:sdate>/<int:pincode>/<int:organisation_id>/<string:purchase_date>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePincodeOrganizationIdPurchaseDateRetailStore(Resource):
	def get(self,sdate,pincode,organisation_id,purchase_date,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT distinct(a.`admin_id`) FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id` 
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`= %s and iip.`organisation_id` = %s and
			date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and `pincode` in (%s) and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s """,
			(organisation_id,organisation_id,sdate,today,start_date,end_date,pincode,organisation_id,retailer_store_id))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(a.`admin_id`)) as count FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id` 
			WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`= %s and iip.`organisation_id` = %s and
			date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and `pincode` in (%s) and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s """,
			(organisation_id,organisation_id,sdate,today,start_date,end_date,pincode,organisation_id,retailer_store_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` a 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
				WHERE a.`role_id`=4 and 
				a.`status`=1 and a.`organisation_id`=%s and iip.`organisation_id` = %s and
				date(a.`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and `pincode` in (%s)  and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id ASC limit %s""",
			(organisation_id,organisation_id,sdate,today,start_date,end_date,pincode,organisation_id,retailer_store_id,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0

				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` a 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
				WHERE a.`role_id`=4 and a.`status`=1 and a.`organisation_id`=%s and iip.`organisation_id` = %s
				and admin_id>%s and date(`date_of_creation`) between %s and %s and date(iip.`last_update_ts`) between %s and %s and
				pincode in (%s) and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id ASC limit %s""",
				(organisation_id,organisation_id,start,sdate,today,start_date,end_date,pincode,organisation_id,retailer_store_id,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(customerdata[i]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					customerdata[i]['customertype'] = customertype['customer_type']
				else:
					customerdata[i]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (customerdata[i]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					customerdata[i]['retailer_city'] = city_data['retailer_city']
					customerdata[i]['retailer_address'] = city_data['retailer_address']
				else:
					customerdata[i]['retailer_city'] = ""
					customerdata[i]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (customerdata[i]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					customerdata[i]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					customerdata[i]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (customerdata[i]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					customerdata[i]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[i]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s """,(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(customerdata[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStore/<string:sdate>/<string:brand>/<int:organisation_id>/<string:purchase_date>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandOrganizationIdPurchaseDateRetailStore(Resource):
	def get(self,sdate,brand,organisation_id,purchase_date,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		adminid = []

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		customerList_query = cursor.execute("""SELECT distinct(`admin_id`) FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(a.`date_of_creation`) BETWEEN %s and %s and a.`organisation_id`=%s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s """,
			(brand,organisation_id,organisation_id,sdate,today,organisation_id,organisation_id,start_date,end_date,organisation_id,retailer_store_id))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(a.`date_of_creation`) BETWEEN %s and %s and a.`organisation_id`=%s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s """,
			(brand,organisation_id,organisation_id,sdate,today,organisation_id,organisation_id,start_date,end_date,organisation_id,retailer_store_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = ad.`admin_id`
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id` 
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id ASC limit %s""",
				(brand,organisation_id,organisation_id,sdate,today,organisation_id,start_date,end_date,organisation_id,retailer_store_id,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					customerdata[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`) as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = ad.`admin_id`
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id ASC limit %s""",
				(brand,organisation_id,start,organisation_id,sdate,today,organisation_id,start_date,end_date,organisation_id,retailer_store_id,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStore/<string:sdate>/<string:brand>/<string:model>/<int:organisation_id>/<string:purchase_date>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandModelOrganizationIdPurchaseDateRetailStore(Resource):
	def get(self,sdate,brand,model,organisation_id,purchase_date,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		split_model = model.split(',')

		customerList_query = cursor.execute("""SELECT distinct(`admin_id`) FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			where a.`admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0)) and date(a.`date_of_creation`) BETWEEN %s and %s and 
			a.`organisation_id`=%s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s """,
			(brand,organisation_id,split_model,sdate,today,organisation_id,organisation_id,start_date,end_date,organisation_id,retailer_store_id))
		customer_list_data = cursor.fetchall()

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` a
			INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = a.`admin_id`
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			where a.`admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0)) and date(a.`date_of_creation`) BETWEEN %s and %s and 
			a.`organisation_id`=%s and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s """,
			(brand,organisation_id,split_model,sdate,today,organisation_id,organisation_id,start_date,end_date,organisation_id,retailer_store_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = ad.`admin_id`
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s and 
				iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
				order by admin_id ASC limit %s""",
				(brand,organisation_id,split_model,organisation_id,sdate,today,organisation_id,start_date,end_date,organisation_id,retailer_store_id,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
			 	
				cursor.execute("""SELECT sum(`amount`) as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
				concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
				`customer_product_mapping` cpm, `admins` ad 
				INNER JOIN `instamojo_initiate_payment` iip ON iip.`user_id` = ad.`admin_id`
				INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
				WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s)
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s
				and iip.`organisation_id` = %s and date(iip.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
				order by admin_id ASC limit %s""",
				(brand,organisation_id,split_model,start,organisation_id,sdate,today,organisation_id,start_date,end_date,organisation_id,retailer_store_id,limit))

			prdcusmrDtls = cursor.fetchall()
			
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				cursor.execute("""SELECT `customer_type` FROM 
					`customer_type` where`customer_id`=%s and 
					`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
				customertype = cursor.fetchone()
				if customertype:
					prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
				else:
					prdcusmrDtls[cid]['customertype'] = ''

				get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
				get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				count_city = cursor.execute(get_city_query,get_city_data)						

				if count_city > 0:
					city_data = cursor.fetchone()
					prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
					prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
				else:
					prdcusmrDtls[cid]['retailer_city'] = ""
					prdcusmrDtls[cid]['retailer_address'] = ""

				get_exchange_count_query = ("""SELECT count(*) exchane_count
														 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
				get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

				if exchange_count > 0:
					exchange_count_data =  cursor.fetchone()
					prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
				else:
					prdcusmrDtls[cid]['exchange_count'] = 0

				get_enquieycount_query = ("""SELECT count(*) enquiery_count
														 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
				get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
				enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

				if enquiery_count > 0:
					enquiery_count_data = cursor.fetchone()
					prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
				else:
					prdcusmrDtls[cid]['enquiery_count'] = 0
				
				cursor.execute("""SELECT sum(`amount`) as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s""",(prdcusmrDtls[cid]['admin_id']))
				costDtls = cursor.fetchone()
				if costDtls['total'] != None:
					prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
				else:
					prdcusmrDtls[cid]['purchase_cost'] = 0


		if prdcusmrDtls:			
			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK


#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
@name_space.route("/getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStore/<string:sdate>/<string:pcost>/<int:organisation_id>/<string:purchase_date>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDatePurchaseCostOrganizationIdPurchaseDateRetailStore(Resource):
	def get(self,sdate,pcost,organisation_id,purchase_date,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))		

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		scost = float(startingcost)
		ecost = float(endingcost) 

		customerList_query = cursor.execute("""SELECT distinct(admin_id) FROM `admins` a
			INNER JOIN `instamojo_payment_request` ipr on ipr.`user_id` = a.`admin_id`
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE a.`organisation_id`=%s and date(a.`date_of_creation`) between %s and %s and ipr.`organisation_id` = %s and amount BETWEEN %s and %s and date(ipr.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
			(organisation_id,sdate,today,organisation_id,scost,ecost,start_date,end_date,organisation_id,retailer_store_id))
		customer_list_data = cursor.fetchall()

		payment_count = cursor.execute("""SELECT distinct(admin_id) FROM `admins` a
			INNER JOIN `instamojo_payment_request` ipr on ipr.`user_id` = a.`admin_id`
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
			WHERE a.`organisation_id`=%s and date(a.`date_of_creation`) between %s and %s and ipr.`organisation_id` = %s and amount BETWEEN %s and %s and date(ipr.`last_update_ts`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
			(organisation_id,sdate,today,organisation_id,scost,ecost,start_date,end_date,organisation_id,retailer_store_id))
		userDtls = cursor.fetchall()		
		
		total_count = len(userDtls)
		print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT admin_id FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and date(a.`date_of_creation`) between %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
					(organisation_id,sdate,today,organisation_id,retailer_store_id))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				if customerids:
				
					cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
						FROM `admins` where 
						`organisation_id`=%s and date(`date_of_creation`) 
						between %s and %s and `admin_id` in %s order by admin_id ASC limit %s""",
						(organisation_id,sdate,today,customerids,limit))

					prdcusmrDtls = cursor.fetchall()
					
					if prdcusmrDtls != None:
						for cid in range(len(prdcusmrDtls)):
							prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
							prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

							cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
							customertype = cursor.fetchone()
							if customertype:
								prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
							else:
								prdcusmrDtls[cid]['customertype'] = ''

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
								prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
							else:
								prdcusmrDtls[cid]['retailer_city'] = ""
								prdcusmrDtls[cid]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								prdcusmrDtls[cid]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								prdcusmrDtls[cid]['enquiery_count'] = 0
							
							scost = float(startingcost)
							ecost = float(endingcost) 

							cursor.execute("""SELECT `amount`as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
							print(cursor._last_executed)
							costDtls = cursor.fetchone()
							if costDtls['total'] != None:
								prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
							else:
								prdcusmrDtls[cid]['purchase_cost'] = 0
					else:
						prdcusmrDtls =[]
			else:
				cursor.execute("""SELECT admin_id FROM `admins` a
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`
					WHERE a.`organisation_id`=%s and date(a.`date_of_creation`) between %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
					(organisation_id,sdate,today,organisation_id,retailer_store_id))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					print(cursor._last_executed)

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print(userDtls[i]['admin_id'])				

				if customerids:
				
					cursor.execute("""SELECT `admin_id`,
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
						FROM `admins` where `organisation_id`=%s and date(`date_of_creation`) 
						between %s and %s and `admin_id` in %s and `admin_id`>%s order by admin_id ASC
						limit %s""",(organisation_id,sdate,today,customerids,start,limit))

					prdcusmrDtls = cursor.fetchall()
					if prdcusmrDtls:
						for cid in range(len(prdcusmrDtls)):
							prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
							prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

							cursor.execute("""SELECT `customer_type` FROM 
								`customer_type` where`customer_id`=%s and 
								`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
							customertype = cursor.fetchone()
							if customertype:
								prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
							else:
								prdcusmrDtls[cid]['customertype'] = ''

							get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
							get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							count_city = cursor.execute(get_city_query,get_city_data)						

							if count_city > 0:
								city_data = cursor.fetchone()
								prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
								prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
							else:
								prdcusmrDtls[cid]['retailer_city'] = ""
								prdcusmrDtls[cid]['retailer_address'] = ""

							get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
							get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

							if exchange_count > 0:
								exchange_count_data =  cursor.fetchone()
								prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
							else:
								prdcusmrDtls[cid]['exchange_count'] = 0

							get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
							get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
							enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

							if enquiery_count > 0:
								enquiery_count_data = cursor.fetchone()
								prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
							else:
								prdcusmrDtls[cid]['enquiery_count'] = 0
							
							scost = float(startingcost)
							ecost = float(endingcost) 

							cursor.execute("""SELECT `amount`as total FROM 
						 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
							print(cursor._last_executed)
							costDtls = cursor.fetchone()
							if costDtls['total'] != None:
								prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
							else:
								prdcusmrDtls[cid]['purchase_cost'] = 0
					else:
						prdcusmrDtls = []
				print(cursor._last_executed)

		if prdcusmrDtls:
			page_next = page + 1			
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStore/<string:sdate>/<string:brand>/<string:pcost>/<int:organisation_id>/<string:purchase_date>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateBrandPurchaseCostOrganizationIdPurchaseDateRetailStore(Resource):
	def get(self,sdate,brand,pcost,organisation_id,purchase_date,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		cursor.execute("""SELECT distinct(`admin_id`)as 'admin_id' FROM `admins` a	
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = a.`admin_id`		
			where a.`admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(a.`date_of_creation`) BETWEEN %s and %s and a.`organisation_id`=%s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s""",
			(brand,organisation_id,organisation_id,sdate,today,organisation_id,organisation_id,retailer_store_id))		

		userDtls = cursor.fetchall()		

		for i in range(len(userDtls)):			
			scost = float(startingcost)
			ecost = float(endingcost) 

			payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
			

			if payment_count > 0:	
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})				
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hiii')
		
		total_count = len(details)
		print(total_count)
		cur_count = int(page) * int(limit)		
	
		if total_count == 0:
			prdcusmrDtls = []
		
		else:
		
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(ad.`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s order by admin_id ASC limit %s""",
					(brand,organisation_id,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):					
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')

				print(customerids)		

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
						`organisation_id` = %s ) and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and 
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
						(brand,organisation_id,customerids,organisation_id,sdate,today,limit))

					print(cursor._last_executed)

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
					order by admin_id ASC limit %s""",
					(brand,organisation_id,start,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					

					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						details.append(userDtls[i]['admin_id'])		
					else:
						print('hiii')

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
						`organisation_id` = %s ) and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and 
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
						(brand,organisation_id,start,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:
			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/<string:sdate>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>/<string:purchase_date>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore(Resource):
	def get(self,sdate,brand,model,pcost,organisation_id,purchase_date,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		split_model = model.split(',')

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
			WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in %s) 
				and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s 
			order by admin_id Asc""",
			(brand,organisation_id,split_model,organisation_id,sdate,today,organisation_id,retailer_store_id))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			print(userDtls[i]['admin_id'])
			scost = float(startingcost)
			ecost = float(endingcost)

			payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
			
			if payment_count > 0:	
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})				
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hii')

		total_count = len(details)
		print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
					order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and `amount` BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					if payment_count > 0:					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')	

					print(customerids)			

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
						(brand,organisation_id,split_model,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						print(cursor._last_executed)
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id` 
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
					order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,start,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost) 

					payment_count = cursor.execute("""SELECT user_id FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))

					if payment_count > 0:						
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')										

				if customerids:
				
					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s limit %s""",
						(brand,organisation_id,split_model,start,customerids,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
					
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:

			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#----------------------------------------------------------------#

#----------------------------------------------------------------#

@name_space.route("/getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore/<string:sdate>/<int:pincode>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>/<string:purchase_date>/<int:retailer_store_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByPincodeBrandModelPurchaseCostOrganizationIdPurchaseDateRetailStore(Resource):
	def get(self,sdate,pincode,brand,model,pcost,organisation_id,purchase_date,retailer_store_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()
		details = []
		customerids = []
		customer_list_data = []

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		purchase_date_range = purchase_date.split(",", 1)
		start_date = purchase_date_range[0]
		end_date = purchase_date_range[1]

		split_model = model.split(',')

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad 
			INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
			WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in %s) 
			and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in (%s) and 
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s 
			order by admin_id Asc""",
			(brand,organisation_id,split_model,pincode,organisation_id,sdate,today,organisation_id,retailer_store_id))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			scost = float(startingcost)
			ecost = float(endingcost) 

			payment_count =  cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
			
			if payment_count > 0:
				customer_list_data.append({'admin_id':userDtls[i]['admin_id']})					
				print(userDtls[i]['admin_id'])
				details.append(userDtls[i]['admin_id'])		
			else:
				print('hiii')
				
		total_count = len(details)
		print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
		
		if total_count == 0:
			prdcusmrDtls = []

		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
					order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,pincode,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost)
					payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					
					if payment_count > 0:
					
						print(userDtls[i]['admin_id'])
						customerids.append(userDtls[i]['admin_id'])		
					else:
						print('hello')			

				if customerids:

					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and ad.`pincode` in(%s) and
						ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
						(brand,organisation_id,split_model,customerids,pincode,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					# print(prdcusmrDtls)
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0
					 	
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				 	
				else:
					prdcusmrDtls = []
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = ad.`admin_id`
					WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in %s) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s and ur.`organisation_id` = %s and ur.`retailer_store_id` = %s
					order by admin_id Asc limit %s""",
					(brand,organisation_id,split_model,start,pincode,organisation_id,sdate,today,organisation_id,retailer_store_id,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					scost = float(startingcost)
					ecost = float(endingcost)

					payment_count = cursor.execute("""SELECT `user_id` FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and amount BETWEEN %s and %s and date(`last_update_ts`) BETWEEN %s and %s""",(userDtls[i]['admin_id'],organisation_id,scost,ecost,start_date,end_date))
					
					if payment_count > 0:						
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				if customerids:
				
					cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
						concat(`first_name`,' ',`last_name`)as name,
						concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
						`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
						`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
						`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
						product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
						`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
						FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
						and `organisation_id` = %s and `product_id` in %s) 
						and `customer_id` !=0) and 
						cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s 
						and ad.`pincode` in(%s) and ad.`organisation_id`=%s and 
						date(`date_of_creation`) BETWEEN %s and %s limit %s""",
						(brand,organisation_id,split_model,start,customerids,pincode,organisation_id,sdate,today,limit))

					prdcusmrDtls = cursor.fetchall()
					
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						cursor.execute("""SELECT `customer_type` FROM 
							`customer_type` where`customer_id`=%s and 
							`organisation_id`=%s""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						customertype = cursor.fetchone()
						if customertype:
							prdcusmrDtls[cid]['customertype'] = customertype['customer_type']
						else:
							prdcusmrDtls[cid]['customertype'] = ''
							
						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
								FROM `user_retailer_mapping` ur 
								INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
								INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
								where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							prdcusmrDtls[cid]['retailer_city'] = city_data['retailer_city']
							prdcusmrDtls[cid]['retailer_address'] = city_data['retailer_address']
						else:
							prdcusmrDtls[cid]['retailer_city'] = ""
							prdcusmrDtls[cid]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
																	 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							prdcusmrDtls[cid]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							prdcusmrDtls[cid]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
																	 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (prdcusmrDtls[cid]['admin_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							prdcusmrDtls[cid]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							prdcusmrDtls[cid]['enquiery_count'] = 0			 	
						
						scost = float(startingcost)
						ecost = float(endingcost) 

						cursor.execute("""SELECT `amount`as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and `amount` BETWEEN %s and %s""",(prdcusmrDtls[cid]['admin_id'],scost,ecost))
						costDtls = cursor.fetchone()
						if costDtls['total'] != None:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
						else:
							prdcusmrDtls[cid]['purchase_cost'] = 0
				else:
					prdcusmrDtls = []

		if prdcusmrDtls:

			page_next = page + 1
			if cur_count < total_count:
				next_url = '?start={}&limit={}&page={}'.format(prdcusmrDtls[-1].get('admin_id'),limit,page_next)
			else:
				next_url = ''
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Customer List",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url,
								'customer_list':customer_list_data
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------------#

