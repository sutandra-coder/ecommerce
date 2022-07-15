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
import math

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


ecommerce_product_sync = Blueprint('ecommerce_product_sync_api', __name__)
api = Api(ecommerce_product_sync,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceProductSync',description='Ecommerce Product Sync')

productsynchronization_postmodel = api.model('product_replication_postmodel',{	
	"product_id":fields.List(fields.Integer),
	"brand_id": fields.Integer(required=True),
	"category_id":fields.Integer(required=True),
	"to_organisation_id":fields.Integer(required=True)
})

#----------------------Category-List---------------------#

@name_space.route("/getCategoryList")	
class getCategoryList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query = ("""SELECT *
				FROM `category`
				WHERE `organisation_id` = 1 and status = 1""")		
		cursor.execute(get_query)

		category_data = cursor.fetchall()

		for key,data in enumerate(category_data):			
			category_data[key]['last_update_ts'] = str(data['last_update_ts'])

			get_brand_count_query = ("""SELECT count(*) as brand_count
				FROM `category_brand_mapping` cbm
				INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = cbm.`brand_id`
				WHERE cbm.`organisation_id` = 1 and cbm.`category_id` = %s""")
			brand_count_data = (data['category_id'])
			count_brand_data = cursor.execute(get_brand_count_query,brand_count_data)

			if count_brand_data > 0:
				brand_data = cursor.fetchone()	
				category_data[key]['brand_count'] = brand_data['brand_count']
			else:
				category_data[key]['brand_count'] = 0

			get_product_count_query = ("""SELECT count(*) as product_count
				FROM `product` p 
				WHERE p.`organisation_id` = 1 and p.`category_id` = %s""")
			product_count_data = (data['category_id'])
			count_product_data = cursor.execute(get_product_count_query,product_count_data)

			if count_product_data > 0:
				product_data = cursor.fetchone()
				category_data[key]['product_count'] = product_data['product_count']
			else:
				category_data[key]['product_count'] = 0

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "Category-List",
		    		"status": "success"
		    	},
		    	"responseList":category_data}), status.HTTP_200_OK

#----------------------Category-List---------------------#

#----------------------Category-List-with-sync-and-unsync-product-count---------------------#

@name_space.route("/getCategoryListwithSyncAndUnsyncproductCount/<int:organisation_id>")	
class getCategoryListwithSyncAndUnsyncproductCount(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query = ("""SELECT *
				FROM `category`
				WHERE `organisation_id` = 1 and status = 1""")		
		cursor.execute(get_query)

		category_data = cursor.fetchall()

		for key,data in enumerate(category_data):			
			category_data[key]['last_update_ts'] = str(data['last_update_ts'])

			get_brand_count_query = ("""SELECT count(*) as brand_count
				FROM `category_brand_mapping` cbm
				INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = cbm.`brand_id`
				WHERE cbm.`organisation_id` = 1 and cbm.`category_id` = %s""")
			brand_count_data = (data['category_id'])
			count_brand_data = cursor.execute(get_brand_count_query,brand_count_data)

			if count_brand_data > 0:
				brand_data = cursor.fetchone()	
				category_data[key]['brand_count'] = brand_data['brand_count']
			else:
				category_data[key]['brand_count'] = 0

			get_product_count_query = ("""SELECT count(*) as product_count
				FROM `product` p 
				WHERE p.`organisation_id` = 1 and p.`category_id` = %s""")
			product_count_data = (data['category_id'])
			count_product_data = cursor.execute(get_product_count_query,product_count_data)

			if count_product_data > 0:
				product_data = cursor.fetchone()
				category_data[key]['product_count'] = product_data['product_count']
			else:
				category_data[key]['product_count'] = 0			

			get_sync_product_count_query = ("""SELECT count(*) as product_count
				FROM `product` p 
				INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
				WHERE pom.`organisation_id` = %s and p.`category_id` = %s""")
			sync_product_count_data = (organisation_id,data['category_id'])
			count_sync_product_data = cursor.execute(get_sync_product_count_query,sync_product_count_data)

			if count_sync_product_data > 0:
				sync_product_data = cursor.fetchone()
				category_data[key]['sync_product_count'] = sync_product_data['product_count']				
			else:
				category_data[key]['sync_product_count'] = 0	

			get_unsync_product_count_query = ("""SELECT count(*) as product_count
				FROM `product` p 
				WHERE p.`organisation_id` = 1 and p.`category_id` = %s and p.`product_id` not in(select product_id from product_organisation_mapping where organisation_id = %s)""")
			unsync_product_count_data = (data['category_id'],organisation_id)
			count_unsync_product_data = cursor.execute(get_unsync_product_count_query,unsync_product_count_data)

			if count_unsync_product_data > 0:
				unsync_product_data = cursor.fetchone()
				category_data[key]['unsync_product_count'] = unsync_product_data['product_count']				
			else:
				category_data[key]['unsync_product_count'] = 0			

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "Category-List",
		    		"status": "success"
		    	},
		    	"responseList":category_data}), status.HTTP_200_OK

#----------------------Category-List-with-sync-and-unsync-product-count---------------------#

#----------------------Brand-List-By-Category-Id---------------------#

@name_space.route("/getBrandListByCategoryId/<int:category_id>")	
class getBrandListByCategoryId(Resource):
	def get(self,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query = ("""SELECT mkvm.`meta_key_value_id` as `brand_id`, mkvm.`meta_key_value` as `brand_name`, mkvm.`image`
				FROM `category_brand_mapping` cbm
				INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = cbm.`brand_id`
				WHERE cbm.`organisation_id` = 1 and cbm.`category_id` = %s""")	
		get_data = (category_id)	
		cursor.execute(get_query,get_data)

		brand_data = cursor.fetchall()

		brand_data.append({"brand_id":0,"brand_name":"Others","image":""})

		for key,data in enumerate(brand_data):
			if data['brand_id'] == 0:
				get_product_brand_mapping_count_query = ("""SELECT count(*) product_count
					FROM `product` p			
					WHERE p.`product_id` not in 
					(select product_id from product_brand_mapping where organisation_id = 1) and 
					p.`organisation_id` = 1 and category_id = %s""")
				get_product_brand_mapping_data = (category_id)
			else:
				get_product_brand_mapping_count_query = ("""SELECT count(*) as product_count
						FROM `product_brand_mapping` pbm where `organisation_id` = 1 and `brand_id` = %s""")
				get_product_brand_mapping_data = (data['brand_id'])

			product_brand_mapping_count = cursor.execute(get_product_brand_mapping_count_query,get_product_brand_mapping_data)

			if product_brand_mapping_count > 0:
				product_brand_mapping = cursor.fetchone()
				brand_data[key]['product_count'] = product_brand_mapping['product_count']
			else:
				brand_data[key]['product_count'] = 0

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "Brand-List",
		    		"status": "success"
		    	},
		    	"responseList":brand_data}), status.HTTP_200_OK

#----------------------Brand-List-By-Category-Id---------------------#

#----------------------Brand-List-By-Category-Id-with-sync-and-unsync-Product-Count---------------------#

@name_space.route("/getBrandListByCategoryIdWithSyncAndUnsyncProductCount/<int:category_id>/<int:organisation_id>")	
class getBrandListByCategoryIdWithSyncAndUnsyncProductCount(Resource):
	def get(self,category_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		
		get_query = ("""SELECT mkvm.`meta_key_value_id` as `brand_id`, mkvm.`meta_key_value` as `brand_name`, mkvm.`image`
				FROM `category_brand_mapping` cbm
				INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = cbm.`brand_id`
				WHERE cbm.`organisation_id` = 1 and cbm.`category_id` = %s""")	
		get_data = (category_id)	
		cursor.execute(get_query,get_data)

		brand_data = cursor.fetchall()

		brand_data.append({"brand_id":0,"brand_name":"Others","image":""})

		for key,data in enumerate(brand_data):
			if data['brand_id'] == 0:
				get_product_brand_mapping_count_query = ("""SELECT count(*) product_count
					FROM `product` p			
					WHERE p.`product_id` not in 
					(select product_id from product_brand_mapping where organisation_id = 1) and 
					p.`organisation_id` = 1 and category_id = %s """)
				get_product_brand_mapping_data = (category_id)
			else:
				get_product_brand_mapping_count_query = ("""SELECT count(*) as product_count
						FROM `product_brand_mapping` pbm 
						INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
						where pbm.`organisation_id` = 1 and pbm.`brand_id` = %s and p.`category_id` = %s """)
				get_product_brand_mapping_data = (data['brand_id'],category_id)

			product_brand_mapping_count = cursor.execute(get_product_brand_mapping_count_query,get_product_brand_mapping_data)

			if product_brand_mapping_count > 0:
				product_brand_mapping = cursor.fetchone()
				brand_data[key]['product_count'] = product_brand_mapping['product_count']
			else:
				brand_data[key]['product_count'] = 0
			

			if  data['brand_id'] == 0:
				get_product_brand_mapping_sync_count_query = ("""SELECT count(*) product_count
					FROM `product` p	
					INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`		
					WHERE p.`product_id` not in 
					(select product_id from product_brand_mapping where organisation_id = 1) and p.`category_id` = %s and pom.`organisation_id` = %s""")
				get_product_brand_mapping_sync_data = (category_id,organisation_id)
			else:
				get_product_brand_mapping_sync_count_query = ("""SELECT count(pbm.`product_id`) as product_count
						FROM `product_brand_mapping` pbm
						INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
						INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = pbm.`product_id` 						
						where pbm.`brand_id` = %s and pbm.`organisation_id` = %s and pom.`organisation_id` = %s and p.`category_id` = %s""")
				get_product_brand_mapping_sync_data = (data['brand_id'],organisation_id,organisation_id,category_id)

			product_brand_mapping_sync_count = cursor.execute(get_product_brand_mapping_sync_count_query,get_product_brand_mapping_sync_data)

			if product_brand_mapping_sync_count > 0:
				product_sync_brand_mapping = cursor.fetchone()
				brand_data[key]['sync_product_count'] = product_sync_brand_mapping['product_count']				
			else:
				brand_data[key]['sync_product_count'] = 0


			if  data['brand_id'] == 0:
				get_product_brand_mapping_unsync_count_query = ("""SELECT  count(p.`product_id`) as product_count
					FROM `product` p			
					WHERE p.`product_id` not in 
					(select product_id from product_brand_mapping where organisation_id = 1) and 
					 p.`product_id` not in (select product_id from product_organisation_mapping where organisation_id = %s) and
					p.`organisation_id` = 1 and category_id = %s""")				
				get_product_brand_mapping_unsync_data = (organisation_id,category_id)
			else:
				get_product_brand_mapping_unsync_count_query = ("""SELECT count(p.`product_id`) as product_count
					FROM `product_brand_mapping` pbm
					INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
					WHERE pbm.`organisation_id` = 1 and p.`category_id` = %s and pbm.`brand_id` = %s and p.`product_id` not in (select product_id from product_organisation_mapping where organisation_id = %s)""")
				get_product_brand_mapping_unsync_data = (category_id,data['brand_id'],organisation_id)

			product_brand_mapping_unsync_count = cursor.execute(get_product_brand_mapping_unsync_count_query,get_product_brand_mapping_unsync_data)

			if product_brand_mapping_unsync_count > 0:
				product_unync_brand_mapping = cursor.fetchone()
				brand_data[key]['unsync_product_count'] = product_unync_brand_mapping['product_count']				
			else:
				brand_data[key]['unsync_product_count'] = 0
				



		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "Brand-List",
		    		"status": "success"
		    	},
		    	"responseList":brand_data}), status.HTTP_200_OK

#----------------------Brand-List-By-Category-Id-with-sync-and-unsync-Product-Count---------------------#



#----------------------Product-List-By-Brand-Id-And-Category-Id---------------------#

@name_space.route("/productListByBrandIdAndCategoryId/<int:category_id>/<int:brand_id>")	
class productListByBrandIdAndCategoryId(Resource):
	def get(self,category_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if brand_id == 0:
			get_query = ("""SELECT  p.`product_id`,p.`product_name`
			FROM `product` p			
			WHERE p.`product_id` not in 
			(select product_id from product_brand_mapping where organisation_id = 1) and 
			p.`organisation_id` = 1 and category_id = %s""")
			get_data = (category_id)
		else:
			get_query = ("""SELECT p.`product_id`,p.`product_name`
					FROM `product_brand_mapping` pbm
					INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
					WHERE pbm.`organisation_id` = 1 and p.`category_id` = %s and pbm.`brand_id` = %s """)	
			get_data = (category_id,brand_id)
				
		count_product = cursor.execute(get_query,get_data)

		if count_product > 0:

			product_data = cursor.fetchall()

			for key,data in enumerate(product_data):
				get_product_meta_query = ("""SELECT pm.`product_meta_id` 
					FROM `product_meta` pm where pm.`product_id` = %s""")
				get_product_meta_data = (data['product_id'])
				count_product_meta = cursor.execute(get_product_meta_query,get_product_meta_data)

				if count_product_meta > 0:
					product_meta_data = cursor.fetchone()
					get_product_meta_image_quey = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s order by default_image_flag desc""")
					product_meta_image_data = (product_meta_data['product_meta_id'])
					count_image = cursor.execute(get_product_meta_image_quey,product_meta_image_data)

					if count_image > 0:
						product_mate_image = cursor.fetchone()
						product_data[key]['image'] = product_mate_image['image']
					else:
						product_data[key]['image'] = ''
				else:
					product_data[key]['image'] = ''

		else:
			product_data = []

		connection.commit()
		cursor.close()	
				
		return ({"attributes": {
		    		"status_desc": "product_data",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List-By-Brand-Id-And-Category-Id---------------------#

#----------------------Product-List-By-Brand-Id-And-Category-Id---------------------#

@name_space.route("/unsyncproductListByBrandIdAndCategoryId/<int:category_id>/<int:brand_id>/<int:organisation_id>")	
class unsyncproductListByBrandIdAndCategoryId(Resource):
	def get(self,category_id,brand_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if brand_id == 0:
			get_query = ("""SELECT  p.`product_id`,p.`product_name`
			FROM `product` p			
			WHERE p.`product_id` not in 
			(select product_id from product_brand_mapping where organisation_id = 1) and 
			 p.`product_id` not in (select product_id from product_organisation_mapping where organisation_id = %s) and
			p.`organisation_id` = 1 and category_id = %s""")
			get_data = (organisation_id,category_id)
		else:
			get_query = ("""SELECT p.`product_id`,p.`product_name`
					FROM `product_brand_mapping` pbm
					INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
					WHERE pbm.`organisation_id` = 1 and p.`category_id` = %s and pbm.`brand_id` = %s and p.`product_id` not in (select product_id from product_organisation_mapping where organisation_id = %s)""")	
			get_data = (category_id,brand_id,organisation_id)
				
		count_product = cursor.execute(get_query,get_data)

		if count_product > 0:

			product_data = cursor.fetchall()

			for key,data in enumerate(product_data):
				get_product_meta_query = ("""SELECT pm.`product_meta_id` 
					FROM `product_meta` pm where pm.`product_id` = %s""")
				get_product_meta_data = (data['product_id'])
				count_product_meta = cursor.execute(get_product_meta_query,get_product_meta_data)

				if count_product_meta > 0:
					product_meta_data = cursor.fetchone()
					get_product_meta_image_quey = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s order by default_image_flag desc""")
					product_meta_image_data = (product_meta_data['product_meta_id'])
					count_image = cursor.execute(get_product_meta_image_quey,product_meta_image_data)

					if count_image > 0:
						product_mate_image = cursor.fetchone()
						product_data[key]['image'] = product_mate_image['image']
					else:
						product_data[key]['image'] = ''
				else:
					product_data[key]['image'] = ''

		else:
			product_data = []

		connection.commit()
		cursor.close()	
				
		return ({"attributes": {
		    		"status_desc": "product_data",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List-By-Brand-Id-And-Category-Id---------------------#

#----------------------Product-Synchronization----------------------#
@name_space.route("/productSynchronization")	
class productSynchronization(Resource):
	@api.expect(productsynchronization_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		product_ids = details.get('product_id',[])
		to_organisation_id = details['to_organisation_id']
		brand_id = details['brand_id']
		category_id =  details['category_id']

		if brand_id == 0:
			for key,product_id in enumerate(product_ids):
				get_query_product_organisation = ("""SELECT *
							FROM  `product_organisation_mapping` WHERE `organisation_id` = %s and `product_id` = %s""")
				getDataProductOrganisation = (to_organisation_id,product_id)
				count_product_organisation = cursor.execute(get_query_product_organisation,getDataProductOrganisation)

				if count_product_organisation > 0: 
					update_product_organisation_query = ("""UPDATE `product_organisation_mapping` SET `product_id` = %s,`organisation_id` = %s
							WHERE `organisation_id` = %s and `product_id` = %s""")
					update_product_organisation_data = (product_id,to_organisation_id,to_organisation_id,product_id)
					cursor.execute(update_product_organisation_query,update_product_organisation_data)

				else:				
					last_update_id = to_organisation_id
					product_status = 1
					insert_product_organisation_query = ("""INSERT INTO `product_organisation_mapping`(`product_id`,`organisation_id`,`product_status`,`last_update_id`) 
							VALUES(%s,%s,%s,%s)""")
					product_organisation_data = (product_id,to_organisation_id,product_status,last_update_id)
					cursor.execute(insert_product_organisation_query,product_organisation_data)

				product_id = product_id
				organisation_id = to_organisation_id

				get_product_meta_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,
										pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,mkvm.`meta_key_value` brand,c.`category_name`
							FROM `product_meta` pm						
							INNER JOIN `product` p ON p.`product_id` = pm.`product_id`	
							INNER JOIN `category` c ON c.`category_id` = p.`category_id`					
							INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
							INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = pbm.`brand_id`
							WHERE p.`product_id` = %s and pbm.`organisation_id` = %s and c.`organisation_id` = %s""")
				get_product_meta_data = (product_id,organisation_id,organisation_id)

				product_meta_count =  cursor.execute(get_product_meta_query,get_product_meta_data)

				product_meta_data = cursor.fetchall()

				for key,data in enumerate(product_meta_data):

					if data['meta_key_text'] :
						a_string = data['meta_key_text']
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
							product_meta_data[key]['met_key_value'] = met_key

				for key,data in enumerate(product_meta_data):

					if data['meta_key_text']:

						if data['met_key_value'] and "Storage" in  data['met_key_value']:
							Capacity =  data['met_key_value']['Storage']
						else:
							Capacity = ""

						if data['met_key_value'] and "Color" in  data['met_key_value']:
							Color =  data['met_key_value']['Color']
						else:
							Color = ""

						if data['met_key_value'] and "Ram" in  data['met_key_value']:
							Ram =  data['met_key_value']['Ram']
						else:
							Ram = ""
					else:
						Capacity = ""
						Color = ""
						Ram = ""


					get_zoho_query = ("""SELECT * FROM `organisation_zoho_details` where `organisation_id` = %s""")
					get_zoho_data = (organisation_id)
					zoho_count = cursor.execute(get_zoho_query,get_zoho_data)
					print(cursor._last_executed)

					print(zoho_count)

					if zoho_count > 0:
						zoho_data = cursor.fetchone()

						if zoho_data['Is_active'] == 1:
							headers = {'Content-type':'application/json', 'Accept':'application/json'}
							Url = BASE_URL + "zoho_crm_ecommerce_product/ZohoCrmEcommerceProduct/productImportintoZoho"
							payloadhData = {						
									"organisation_id":organisation_id,
									"Product_Name":data['product_name'],
									"Product_Code":str(data['product_meta_code']),
									"Brand":data['brand'],
									"Product_Category":data['category_name'],
									"Storage":Capacity,
									"Color":Color,
									"Ram":Ram,
									"Unit_Price":str(data['out_price']),												
									"Product_Meta_Id":str(data['product_meta_id']),						
									"Description":data['product_short_description']
							}

							print(Url)
							print(payloadhData)
							create_customer_to_zoho = requests.post(Url,data=json.dumps(payloadhData), headers=headers).json()
							print(create_customer_to_zoho)
		else:

			for key,product_id in enumerate(product_ids):
				

				get_product_brnad_query_from_organisation = ("""SELECT p.`category_id`,pbm.`brand_id`
							FROM  `product_brand_mapping`pbm 
							INNER JOIN `product`p ON p.`product_id` = pbm.`product_id`
							WHERE p.`product_id` = %s and pbm.`organisation_id` = 1 and p.`organisation_id` = 1""")
				get_product_brand_data_from_organisation = (product_id)
				count_product_brand_from_organisation = cursor.execute(get_product_brnad_query_from_organisation,get_product_brand_data_from_organisation)


				if count_product_brand_from_organisation >0:	

					product_brand_data_from_organisation = cursor.fetchone()		
					
					brand_id_from_organisation = product_brand_data_from_organisation['brand_id']
					category_id = product_brand_data_from_organisation['category_id']


					get_query_product_organisation = ("""SELECT *
								FROM  `product_organisation_mapping` WHERE `organisation_id` = %s and `product_id` = %s""")
					getDataProductOrganisation = (to_organisation_id,product_id)
					count_product_organisation = cursor.execute(get_query_product_organisation,getDataProductOrganisation)

					if count_product_organisation > 0: 
						update_product_organisation_query = ("""UPDATE `product_organisation_mapping` SET `product_id` = %s,`organisation_id` = %s
								WHERE `organisation_id` = %s and `product_id` = %s""")
						update_product_organisation_data = (product_id,to_organisation_id,to_organisation_id,product_id)
						cursor.execute(update_product_organisation_query,update_product_organisation_data)

					else:				
						last_update_id = to_organisation_id
						product_status = 1
						insert_product_organisation_query = ("""INSERT INTO `product_organisation_mapping`(`product_id`,`organisation_id`,`product_status`,`last_update_id`) 
								VALUES(%s,%s,%s,%s)""")
						product_organisation_data = (product_id,to_organisation_id,product_status,last_update_id)
						cursor.execute(insert_product_organisation_query,product_organisation_data)

					

					get_product_brand_query_to_organisation = (""" SELECT *
							FROM  `product_brand_mapping` WHERE `product_id` = %s and `organisation_id` = %s""")
					get_product_brand_data_to_organisation = (product_id,to_organisation_id)
					count_product_brand_to_organisation = cursor.execute(get_product_brand_query_to_organisation,get_product_brand_data_to_organisation)

					if count_product_brand_to_organisation > 0:
						update_product_brand_query = ("""UPDATE `product_brand_mapping` SET `brand_id` = %s
								WHERE `product_id` = %s and `organisation_id` = %s""")
						update_product_brand_data = (brand_id_from_organisation,product_id,to_organisation_id)
						cursor.execute(update_product_brand_query,update_product_brand_data)
					else:
						product_brand_mapping_status = 1
						insert_product_brand_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s)""")

						product_brand_data = (brand_id_from_organisation,product_id,product_brand_mapping_status,to_organisation_id,to_organisation_id)
						cursor.execute(insert_product_brand_query,product_brand_data)


					get_organistion_brand_query = ("""SELECT *
							FROM  `organisation_brand_mapping` WHERE `organisation_id` = %s and `brand_id` = %s""")
					get_organisation_brand_data = (to_organisation_id,brand_id_from_organisation)
					count_organisation_brand = cursor.execute(get_organistion_brand_query,get_organisation_brand_data)

					if count_organisation_brand > 0:
						update_organisation_brand_query = ("""UPDATE `organisation_brand_mapping` SET `brand_id` = %s
								WHERE `organisation_id` = %s and `brand_id` = %s""")
						update_organisation_brand_data = (brand_id_from_organisation,to_organisation_id,brand_id_from_organisation)
						cursor.execute(update_organisation_brand_query,update_organisation_brand_data)
					else:
						insert_organisation_brand_query = ("""INSERT INTO `organisation_brand_mapping`(`brand_id`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s)""")

						organisation_brand_data = (brand_id_from_organisation,to_organisation_id,to_organisation_id)
						cursor.execute(insert_organisation_brand_query,organisation_brand_data)

					
						
			get_brand_category_organisation_query = ("""SELECT *
							FROM  `category_brand_mapping` WHERE `brand_id` = %s and `category_id` = %s and `organisation_id` = %s""")
			get_brand_category_organisation_data = (brand_id,category_id,to_organisation_id)
			count_brand_category_organisation_data = cursor.execute(get_brand_category_organisation_query,get_brand_category_organisation_data)
					

			if count_brand_category_organisation_data < 1:													
				insert_brand_category_query = ("""INSERT INTO `category_brand_mapping`(`brand_id`,`category_id`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s)""")

				brand_category_data = (brand_id,category_id,to_organisation_id,to_organisation_id)
				cursor.execute(insert_brand_category_query,brand_category_data)

			product_id = product_id
			organisation_id = to_organisation_id

			get_product_meta_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,
									pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,mkvm.`meta_key_value` brand,c.`category_name`
						FROM `product_meta` pm						
						INNER JOIN `product` p ON p.`product_id` = pm.`product_id`	
						INNER JOIN `category` c ON c.`category_id` = p.`category_id`					
						INNER JOIN `product_brand_mapping` pbm ON pbm.`product_id` = p.`product_id`	
						INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = pbm.`brand_id`
						WHERE p.`product_id` = %s and pbm.`organisation_id` = %s and c.`organisation_id` = %s""")
			get_product_meta_data = (product_id,organisation_id,organisation_id)

			product_meta_count =  cursor.execute(get_product_meta_query,get_product_meta_data)

			product_meta_data = cursor.fetchall()

			for key,data in enumerate(product_meta_data):

				if data['meta_key_text'] :
					a_string = data['meta_key_text']
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
						product_meta_data[key]['met_key_value'] = met_key

			for key,data in enumerate(product_meta_data):

				if data['meta_key_text']:

					if data['met_key_value'] and "Storage" in  data['met_key_value']:
						Capacity =  data['met_key_value']['Storage']
					else:
						Capacity = ""

					if data['met_key_value'] and "Color" in  data['met_key_value']:
						Color =  data['met_key_value']['Color']
					else:
						Color = ""

					if data['met_key_value'] and "Ram" in  data['met_key_value']:
						Ram =  data['met_key_value']['Ram']
					else:
						Ram = ""
				else:
					Capacity = ""
					Color = ""
					Ram = ""


				get_zoho_query = ("""SELECT * FROM `organisation_zoho_details` where `organisation_id` = %s""")
				get_zoho_data = (organisation_id)
				zoho_count = cursor.execute(get_zoho_query,get_zoho_data)
				print(cursor._last_executed)

				print(zoho_count)

				if zoho_count > 0:
					zoho_data = cursor.fetchone()

					if zoho_data['Is_active'] == 1:
						headers = {'Content-type':'application/json', 'Accept':'application/json'}
						Url = BASE_URL + "zoho_crm_ecommerce_product/ZohoCrmEcommerceProduct/productImportintoZoho"
						payloadhData = {						
								"organisation_id":organisation_id,
								"Product_Name":data['product_name'],
								"Product_Code":str(data['product_meta_code']),
								"Brand":data['brand'],
								"Product_Category":data['category_name'],
								"Storage":Capacity,
								"Color":Color,
								"Ram":Ram,
								"Unit_Price":str(data['out_price']),												
								"Product_Meta_Id":str(data['product_meta_id']),						
								"Description":data['product_short_description']
						}

						print(Url)
						print(payloadhData)
						create_customer_to_zoho = requests.post(Url,data=json.dumps(payloadhData), headers=headers).json()
						print(create_customer_to_zoho)	
					

		connection.commit()
		cursor.close()	
				
		return ({"attributes": {
		    		"status_desc": "product_synchronization_data",
		    		"status": "success"
		    	},
		    	"responseList":details}), status.HTTP_200_OK

#----------------------Product-Synchronization----------------------#