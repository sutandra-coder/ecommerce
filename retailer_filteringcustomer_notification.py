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
def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_ecommerce',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

filteringcustomer_notification = Blueprint('filteringcustomer_notification', __name__)
api = Api(filteringcustomer_notification, version='1.0', title='Ecommerce API',
    description='Ecommerce API')

name_space = api.namespace('EcommerceNotification',description='Ecommerce Notification')

# BASE_URL = 'http://ec2-3-19-228-138.us-east-2.compute.amazonaws.com/flaskapp/'

BASE_URL = 'http://127.0.0.1:5000/'

#-----------------------------------------------------------------#
appmsg_model = api.model('appmsg_model', {
	"user_id": fields.Integer()
	})

appmsgmodel = api.model('appmsgmodel', {
	"title": fields.String(),
	"msg": fields.String(),
	"img": fields.String(),
	"sdate": fields.String(),
	"pincode": fields.Integer(),
	"model": fields.String(),
	"brand": fields.String(),
	"pcost": fields.String(),
	"organisation_id": fields.Integer(),
	"appmsg_model":fields.List(fields.Nested(appmsg_model))
	})

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseOrganizationId/<string:sdate>/<string:edate>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseOrganizationId(Resource):
	def get(self,sdate,edate,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		cursor.execute("""SELECT count(`admin_id`)as count FROM `admins`
			WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s""",(organisation_id,sdate,edate))

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
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and `organisation_id`=%s and 
				date(`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",(organisation_id,sdate,edate,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

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

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
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
				FROM `admins` WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s 
				and admin_id>%s and date(`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",
				(organisation_id,start,sdate,edate,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				if customerdata[i]['date_of_creation'] == '0000-00-00 00:00:00':
					customerdata[i]['date_of_creation'] = '0000-00-00 00:00:00'
				else:
					customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

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

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
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
								'next':next_url
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWisePincodeOrganizationId/<string:sdate>/<string:edate>/<int:pincode>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseOrganizationId(Resource):
	def get(self,sdate,edate,pincode,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		cursor.execute("""SELECT count(`admin_id`)as count FROM `admins` ad
			WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s and `pincode` in (%s)""",
			(organisation_id,sdate,edate,pincode))

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
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s  and `pincode` in (%s) order by admin_id ASC limit %s""",
			(organisation_id,sdate,edate,pincode,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

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

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
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
				FROM `admins` WHERE `role_id`=4 and `status`=1 and `organisation_id`=%s 
				and admin_id>%s and date(`date_of_creation`) between %s and %s and 
				pincode in (%s) order by admin_id ASC limit %s""",
				(organisation_id,start,sdate,edate,pincode,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

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
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
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
								'next':next_url
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseBrandOrganizationId/<string:sdate>/<string:edate>/<string:brand>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseBrandOrganizationId(Resource):
	def get(self,sdate,edate,brand,organisation_id):
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

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(`date_of_creation`) BETWEEN %s and %s and `organisation_id`=%s""",
			(brand,organisation_id,organisation_id,sdate,edate,organisation_id))

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
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,organisation_id,sdate,edate,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				prdcusmrDtls[cid]['outstanding'] = 0

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
			 	
				cursor.execute("""SELECT sum(`amount`)as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s and 
					`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
				`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status` FROM 
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,start,organisation_id,sdate,edate,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				prdcusmrDtls[cid]['outstanding'] = 0

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
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseBrandModelOrganizationId/<string:sdate>/<string:edate>/<string:brand>/<string:model>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseBrandModelOrganizationId(Resource):
	def get(self,sdate,edate,brand,model,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in(%s)) 
			and `customer_id` !=0)) and date(`date_of_creation`) BETWEEN %s and %s and 
			`organisation_id`=%s""",
			(brand,organisation_id,model,sdate,edate,organisation_id))

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
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,model,organisation_id,sdate,edate,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				prdcusmrDtls[cid]['outstanding'] = 0

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
			 	
				cursor.execute("""SELECT sum(`amount`)as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s and 
					`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,model,start,organisation_id,sdate,edate,limit))

			prdcusmrDtls = cursor.fetchall()
			
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				prdcusmrDtls[cid]['outstanding'] = 0

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
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK


#-------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWisePurchaseCostOrganizationId/<string:sdate>/<string:edate>/<string:pcost>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWisePurchaseCostOrganizationId(Resource):
	def get(self,sdate,edate,pcost,organisation_id):
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
		
		cursor.execute("""SELECT admin_id FROM `admins`
			WHERE `organisation_id`=%s and date(`date_of_creation`) between %s and %s""",
			(organisation_id,sdate,edate))
		userDtls = cursor.fetchall()
		
		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])
		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT admin_id FROM `admins`
					WHERE `organisation_id`=%s and date(`date_of_creation`) between %s and %s""",
					(organisation_id,sdate,edate))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
					FROM `admins` where 
					`organisation_id`=%s and date(`date_of_creation`) 
					between %s and %s and `admin_id` in %s order by admin_id ASC limit %s""",
					(organisation_id,sdate,edate,customerids,limit))

				prdcusmrDtls = cursor.fetchall()
				
				if prdcusmrDtls != None:
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						prdcusmrDtls[cid]['outstanding'] = 0

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
						
						cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
							WHERE user_id=%s and `organisation_id` =%s and 
							`status`='Complete'""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
						total = costDtls['total']
			
						if total == None:
							prdcusmrDtls[cid]['purchase_cost'] = 0
						else:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
			else:
				cursor.execute("""SELECT admin_id FROM `admins`
					WHERE `organisation_id`=%s and date(`date_of_creation`) between %s and %s""",
					(organisation_id,sdate,edate))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
					if costDtls['total'] != None:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT `admin_id`,
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
					FROM `admins` where `organisation_id`=%s and date(`date_of_creation`) 
					between %s and %s and `admin_id` in %s and `admin_id`>%s order by admin_id ASC
					limit %s""",(organisation_id,sdate,edate,customerids,start,limit))

				prdcusmrDtls = cursor.fetchall()
				if prdcusmrDtls:
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						prdcusmrDtls[cid]['outstanding'] = 0

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
						
						cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
							WHERE user_id=%s and `organisation_id` =%s and 
							`status`='Complete'""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						costDtls = cursor.fetchone()

						if total == None:
							prdcusmrDtls[cid]['purchase_cost'] = 0
						else:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseBrandPurchaseCostOrganizationId/<string:sdate>/<string:edate>/<string:brand>/<string:pcost>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListWiseByDateBrandPurchaseCostOrganizationId(Resource):
	def get(self,sdate,edate,brand,pcost,organisation_id):
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

		cursor.execute("""SELECT distinct(`admin_id`)as 'admin_id' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(`date_of_creation`) BETWEEN %s and %s and `organisation_id`=%s""",
			(brand,organisation_id,organisation_id,sdate,edate,organisation_id))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])
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
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

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
					(brand,organisation_id,customerids,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s and 
				 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,start,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

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
					(brand,organisation_id,start,customerids,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s and 
				 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseBrandModelPurchaseCostOrganizationId/<string:sdate>/<string:edate>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseBrandModelPurchaseCostOrganizationId(Resource):
	def get(self,sdate,edate,brand,model,pcost,organisation_id):
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

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc""",
			(brand,organisation_id,model,organisation_id,sdate,edate))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])

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
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,customerids,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,organisation_id,start,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s limit %s""",
					(brand,organisation_id,model,start,customerids,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s and 
				 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#----------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWisePincodeBrandModelPurchaseCostOrganizationId/<string:sdate>/<string:edate>/<int:pincode>/<string:brand>/<string:model>/<string:pcost>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWisePincodeBrandModelPurchaseCostOrganizationId(Resource):
	def get(self,sdate,edate,pincode,brand,model,pcost,organisation_id):
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

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in(%s)) 
			and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in (%s) and 
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc""",
			(brand,organisation_id,model,pincode,organisation_id,sdate,edate))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])
				
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
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,pincode,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,customerids,pincode,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,start,pincode,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s 
					and ad.`pincode` in(%s) and ad.`organisation_id`=%s and 
					date(`date_of_creation`) BETWEEN %s and %s limit %s""",
					(brand,organisation_id,model,start,customerids,pincode,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s and 
				 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#--------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseCityOrganizationId/<string:sdate>/<string:edate>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseCityOrganizationId(Resource):
	def get(self,sdate,edate,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		today = date.today()
		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city

		cursor.execute("""SELECT count(`admin_id`)as count FROM `admins`
			WHERE `role_id`=4 and `status`=1 and city=%s and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s""",(store,organisation_id,sdate,edate))

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
				`city`as 'retailer_store',`dob`,`phoneno`,profile_image,
				`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and city=%s and `organisation_id`=%s and 
				date(`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",(store,organisation_id,sdate,edate,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

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

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT distinct(`admin_id`)as admin_id,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`city`as 'retailer_store',`dob`,`phoneno`,profile_image,
				`pincode`,date_of_creation,`loggedin_status`,`wallet`
				FROM `admins` WHERE `role_id`=4 and `status`=1 and city=%s and `organisation_id`=%s 
				and admin_id>%s and date(`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",
				(store,organisation_id,start,sdate,edate,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				if customerdata[i]['date_of_creation'] == '0000-00-00 00:00:00':
					customerdata[i]['date_of_creation'] = '0000-00-00 00:00:00'
				else:
					customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

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

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
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
								'next':next_url
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWisePincodeCityOrganizationId/<string:sdate>/<string:edate>/<int:pincode>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWisePincodeCityOrganizationId(Resource):
	def get(self,sdate,edate,pincode,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city

		cursor.execute("""SELECT count(`admin_id`)as count FROM `admins` ad
			WHERE `role_id`=4 and `status`=1 and city=%s and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s and `pincode` in %s""",
			(store,organisation_id,sdate,edate,pincode))

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
				`dob`,`phoneno`,profile_image,`pincode`,date_of_creation,`loggedin_status`,`wallet` FROM `admins` WHERE `role_id`=4 and 
				`status`=1 and city=%s and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s  and `pincode` in %s order by admin_id ASC limit %s""",
			(store,organisation_id,sdate,edate,pincode,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

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

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
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
				FROM `admins` WHERE `role_id`=4 and `status`=1 and city=%s and `organisation_id`=%s 
				and admin_id>%s and date(`date_of_creation`) between %s and %s and 
				pincode in (%s) order by admin_id ASC limit %s""",
				(store,organisation_id,start,sdate,edate,pincode,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()


				customerdata[i]['outstanding'] = 0

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
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
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
								'next':next_url
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseBrandCityOrganizationId/<string:sdate>/<string:edate>/<string:brand>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseBrandCityOrganizationId(Resource):
	def get(self,sdate,edate,brand,city,organisation_id):
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
		store = city

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(`date_of_creation`) BETWEEN %s and %s and city=%s and `organisation_id`=%s""",
			(brand,organisation_id,organisation_id,sdate,edate,store,organisation_id))

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
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and city=%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,store,organisation_id,sdate,edate,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				prdcusmrDtls[cid]['outstanding'] = 0

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
			 	
				cursor.execute("""SELECT sum(`amount`)as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s and 
					`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and city=%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,start,store,organisation_id,sdate,edate,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				prdcusmrDtls[cid]['outstanding'] = 0

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
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseBrandModelCityOrganizationId/<string:sdate>/<string:edate>/<string:brand>/<string:model>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseBrandModelCityOrganizationId(Resource):
	def get(self,sdate,edate,brand,model,city,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		today = date.today()

		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''
		store = city

		cursor.execute("""SELECT count(distinct(`admin_id`))as 'count' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in(%s)) 
			and `customer_id` !=0)) and date(`date_of_creation`) BETWEEN %s and %s and 
			`organisation_id`=%s and city=%s""",
			(brand,organisation_id,model,sdate,edate,organisation_id,store))

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
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and city=%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,model,store,organisation_id,sdate,edate,limit))

			prdcusmrDtls = cursor.fetchall()
			# print(prdcusmrDtls)
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

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
			 	
				cursor.execute("""SELECT sum(`amount`)as total FROM 
					`instamojo_payment_request` WHERE `user_id`=%s and 
					`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
				`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
				product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
				cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and city=%s and
				ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
				(brand,organisation_id,model,start,store,organisation_id,sdate,edate,limit))

			prdcusmrDtls = cursor.fetchall()
			
			for cid in range(len(prdcusmrDtls)):
				prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
				prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

				prdcusmrDtls[cid]['outstanding'] = 0

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
				
				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK


#-------------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWisePurchaseCostCityOrganizationId/<string:sdate>/<string:edate>/<string:pcost>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWisePurchaseCostCityOrganizationId(Resource):
	def get(self,sdate,edate,pcost,city,organisation_id):
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
		store = city

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]
		
		cursor.execute("""SELECT admin_id FROM `admins`
			WHERE `organisation_id`=%s and city=%s and date(`date_of_creation`) between %s and %s""",
			(organisation_id,store,sdate,edate))
		userDtls = cursor.fetchall()
		
		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])
		total_count = len(details)
		# print(total_count)
		cur_count = int(page) * int(limit)
		# print(cur_count)
	
		if total_count == 0:
			prdcusmrDtls = []
		else:
			if start == 0:
				previous_url = ''

				cursor.execute("""SELECT admin_id FROM `admins`
					WHERE `organisation_id`=%s and city=%s and date(`date_of_creation`) between %s and %s""",
					(organisation_id,store,sdate,edate))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
					FROM `admins` where 
					`organisation_id`=%s and date(`date_of_creation`) 
					between %s and %s and `admin_id` in %s order by admin_id ASC limit %s""",
					(organisation_id,sdate,edate,customerids,limit))

				prdcusmrDtls = cursor.fetchall()
				
				if prdcusmrDtls != None:
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						prdcusmrDtls[cid]['outstanding'] = 0

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
						
						cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
							WHERE user_id=%s and `organisation_id` =%s and 
							`status`='Complete'""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						costDtls = cursor.fetchone()
						total = costDtls['total']
			
						if total == None:
							prdcusmrDtls[cid]['purchase_cost'] = 0
						else:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
			else:
				cursor.execute("""SELECT admin_id FROM `admins`
					WHERE `organisation_id`=%s and city=%s and date(`date_of_creation`) between %s and %s""",
					(organisation_id,store,sdate,edate))
				userDtls = cursor.fetchall()
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
					if costDtls['total'] != None:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT `admin_id`,
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` 
					FROM `admins` where `organisation_id`=%s and date(`date_of_creation`) 
					between %s and %s and `admin_id` in %s and `admin_id`>%s order by admin_id ASC
					limit %s""",(organisation_id,sdate,edate,customerids,start,limit))

				prdcusmrDtls = cursor.fetchall()
				if prdcusmrDtls:
					for cid in range(len(prdcusmrDtls)):
						prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
						prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

						prdcusmrDtls[cid]['outstanding'] = 0

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
						
						cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
							WHERE user_id=%s and `organisation_id` =%s and 
							`status`='Complete'""",(prdcusmrDtls[cid]['admin_id'],organisation_id))
						costDtls = cursor.fetchone()

						if total == None:
							prdcusmrDtls[cid]['purchase_cost'] = 0
						else:
							prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseBrandPurchaseCostCityOrganizationId/<string:sdate>/<string:edate>/<string:brand>/<string:pcost>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseBrandPurchaseCostCityOrganizationId(Resource):
	def get(self,sdate,edate,brand,pcost,city,organisation_id):
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
		store = city

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		cursor.execute("""SELECT distinct(`admin_id`)as 'admin_id' FROM `admins` 
			where `admin_id` in(SELECT distinct(`customer_id`) FROM 
			`customer_product_mapping` WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
				`organisation_id` = %s ) and `customer_id` !=0) and `organisation_id`=%s) and 
			date(`date_of_creation`) BETWEEN %s and %s and city=%s and `organisation_id`=%s""",
			(brand,organisation_id,organisation_id,sdate,edate,store,organisation_id))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])
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
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and city=%s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,store,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

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
					(brand,organisation_id,customerids,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s and 
				 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) and 
					`organisation_id` = %s ) and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and city=%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id ASC limit %s""",
					(brand,organisation_id,start,store,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

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
					(brand,organisation_id,start,customerids,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s and 
				 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWiseBrandModelPurchaseCostCityOrganizationId/<string:sdate>/<string:edate>/<string:brand>/<string:model>/<string:pcost>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWiseBrandModelPurchaseCostCityOrganizationId(Resource):
	def get(self,sdate,edate,brand,model,pcost,city,organisation_id):
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
		store = city

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
				`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
				FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
				and `organisation_id` = %s and `product_id` in(%s)) 
				and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and city=%s and
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc""",
			(brand,organisation_id,model,store,organisation_id,sdate,edate))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])

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
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and city=%s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,store,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,customerids,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and city=%s and 
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,organisation_id,start,store,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s limit %s""",
					(brand,organisation_id,model,start,customerids,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s and 
				 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#----------------------------------------------------------------#
@name_space.route("/getCustomerListByDateWisePincodeBrandModelPurchaseCostCityOrganizationId/<string:sdate>/<string:edate>/<int:pincode>/<string:brand>/<string:model>/<string:pcost>/<string:city>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByDateWisePincodeBrandModelPurchaseCostCityOrganizationId(Resource):
	def get(self,sdate,edate,pincode,brand,model,pcost,city,organisation_id):
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
		store = city

		pcostrange = pcost.split("-", 1)
		startingcost = pcostrange[0]
		endingcost = pcostrange[1]

		cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
			`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
			product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
			`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
			FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
			and `organisation_id` = %s and `product_id` in(%s)) 
			and `customer_id` !=0) and 
			cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in (%s) and city=%s and 
			ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s""",
			(brand,organisation_id,model,pincode,store,organisation_id,sdate,edate))

		userDtls = cursor.fetchall()

		for i in range(len(userDtls)):
			cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
				WHERE user_id=%s and `organisation_id` =%s and 
				`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
			costDtls = cursor.fetchone()
			total = costDtls['total']
			
			if total == None:
				total = 0
			else:
				total = total
			scost = float(startingcost)
			ecost = float(endingcost)
			if scost <= total <= ecost:
				details.append(userDtls[i]['admin_id'])
				
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
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`pincode` in(%s) and city=%s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,pincode,store,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)

				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id` in %s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,customerids,pincode,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
			else:
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id' FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`pincode` in(%s) and city=%s and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s order by admin_id Asc limit %s""",
					(brand,organisation_id,model,start,pincode,store,organisation_id,sdate,edate,limit))

				userDtls = cursor.fetchall()
				# print(prdcusmrDtls)
				for i in range(len(userDtls)):
					cursor.execute("""SELECT sum(amount)as total FROM `instamojo_payment_request` 
						WHERE user_id=%s and `organisation_id` =%s and 
						`status`='Complete'""",(userDtls[i]['admin_id'],organisation_id))
					costDtls = cursor.fetchone()
					
					total = costDtls['total']
					if total == None:
						total = 0
					scost = float(startingcost)
					ecost = float(endingcost)
					if scost <= total <= ecost:
						customerids.append(userDtls[i]['admin_id'])
				customerids = tuple(customerids)
				
				cursor.execute("""SELECT distinct(`customer_id`)as 'admin_id',
					concat(`first_name`,' ',`last_name`)as name,
					concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
					`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
					`dob`,`phoneno`,`pincode`,profile_image,date_of_creation,`loggedin_status`,`wallet` FROM 
					`customer_product_mapping` cpm, `admins` ad WHERE `product_meta_id` in(SELECT 
					product_meta_id FROM `product_meta` WHERE `product_id` in(SELECT 
					`product_id` FROM `product_organisation_mapping` WHERE `product_id`in(SELECT product_id 
					FROM `product_brand_mapping` WHERE `brand_id` in (%s)) 
					and `organisation_id` = %s and `product_id` in(%s)) 
					and `customer_id` !=0) and 
					cpm.`customer_id` = ad.`admin_id` and ad.`admin_id`>%s and ad.`admin_id` in %s and ad.`pincode` in(%s) and
					ad.`organisation_id`=%s and date(`date_of_creation`) BETWEEN %s and %s limit %s""",
					(brand,organisation_id,model,start,customerids,pincode,organisation_id,sdate,edate,limit))

				prdcusmrDtls = cursor.fetchall()
				
				for cid in range(len(prdcusmrDtls)):
					prdcusmrDtls[cid]['dob'] = prdcusmrDtls[cid]['dob']
					prdcusmrDtls[cid]['date_of_creation'] = prdcusmrDtls[cid]['date_of_creation'].isoformat()

					prdcusmrDtls[cid]['outstanding'] = 0

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
				 	
					cursor.execute("""SELECT sum(`amount`)as total FROM 
						`instamojo_payment_request` WHERE `user_id`=%s and 
						`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
					costDtls = cursor.fetchone()
					if costDtls['total'] != None:
						prdcusmrDtls[cid]['purchase_cost'] = costDtls['total']
					else:
						prdcusmrDtls[cid]['purchase_cost'] = 0
					
					cursor.execute("""SELECT sum(`amount`)as total FROM 
				 		`instamojo_payment_request` WHERE `user_id`=%s and 
				 		`status`='Complete'""",(prdcusmrDtls[cid]['admin_id']))
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
								'next':next_url
								},
	             "responseList": prdcusmrDtls}), status.HTTP_200_OK

#------------------------------------------------------------------#
@name_space.route("/getCustomerListByStoreOrganizationId/<string:sdate>/<int:store_id>/<int:organisation_id>",
	doc={'params':{'start':'adminId','limit':'limit','page':'pageno'}})
class getCustomerListByStoreOrganizationId(Resource):
	def get(self,sdate,store_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		today = date.today()
		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 10))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		cursor.execute("""SELECT count(`admin_id`)as count FROM 
			`admins` WHERE `admin_id` in(SELECT `user_id` FROM 
			`user_retailer_mapping` where `retailer_store_id`=%s and `organisation_id`=%s) and 
			`role_id`=4 and `status`=1 and `organisation_id`=%s and 
			date(`date_of_creation`) between %s and %s""",
			(store_id,organisation_id,organisation_id,sdate,today))

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
				`dob`,`phoneno`,profile_image, `pincode`,date_of_creation,
				`loggedin_status`,`wallet` FROM `admins` ad,`user_retailer_mapping` urm 
				WHERE `admin_id` in(SELECT `user_id` FROM `user_retailer_mapping` 
				where `retailer_store_id`=%s  and 
				`organisation_id`=%s) and ad.`admin_id`=urm.`user_id` and 
				`role_id`=4 and ad.`status`=1 and ad.`organisation_id`=%s and 
				date(`date_of_creation`) between %s and %s order by admin_id ASC 
				limit %s""",(store_id,organisation_id,organisation_id,sdate,today,limit))

			customerdata = cursor.fetchall()
			# print(customerdata)
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

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

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
				costDtls = cursor.fetchone()
				
				if costDtls['total'] != None:
					customerdata[i]['purchase_cost'] = costDtls['total']
				else:
					customerdata[i]['purchase_cost'] = 0
		else:
			cursor.execute("""SELECT `admin_id`,concat(`first_name`,' ',`last_name`)as name,
				concat('address line1-',`address_line_1`,',','address line2-',`address_line_2`,',','city-',`city`,',','state-',`state`)as address,
				`address_line_1`,`address_line_2`,`city`,`country`,`state`,`anniversary`,
				`dob`,`phoneno`,profile_image, `pincode`,date_of_creation,
				`loggedin_status`,`wallet` FROM `admins` ad,`user_retailer_mapping` urm 
				WHERE `admin_id` in(SELECT `user_id` FROM `user_retailer_mapping` 
				where `retailer_store_id`=%s and 
				`organisation_id`=%s) and ad.`admin_id`=urm.`user_id` and 
				`role_id`=4 and ad.`status`=1 and ad.`organisation_id`=%s
				and admin_id>%s and date(`date_of_creation`) between %s and %s order by admin_id ASC limit %s""",
				(store_id,organisation_id,organisation_id,start,sdate,today,limit))

			customerdata = cursor.fetchall()
			
			for i in range(len(customerdata)):
				customerdata[i]['dob'] = customerdata[i]['dob']
				if customerdata[i]['date_of_creation'] == '0000-00-00 00:00:00':
					customerdata[i]['date_of_creation'] = '0000-00-00 00:00:00'
				else:
					customerdata[i]['date_of_creation'] = customerdata[i]['date_of_creation'].isoformat()

				customerdata[i]['outstanding'] = 0

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

				cursor.execute("""SELECT sum(`amount`)as total FROM 
			 		`instamojo_payment_request` WHERE `user_id`=%s and 
			 		`status`='Complete'""",(customerdata[i]['admin_id']))
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
								'next':next_url
								},
	             "responseList": customerdata}), status.HTTP_200_OK

#---------------------------------------------------------------------#
