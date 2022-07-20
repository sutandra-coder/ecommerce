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

ecommerce_product = Blueprint('ecommerce_product_api', __name__)
api = Api(ecommerce_product,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceProduct',description='Ecommerce Product')


product_meta_key_postmodel = api.model('SelectProductMetaKey', {
	"meta_key":fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

update_product_meta_key_postmodel = api.model('UpdateProductMetaKey', {
	"meta_key":fields.String,
	"organisation_id":fields.Integer,
	"last_update_id":fields.Integer,
	"meta_key_status":fields.Integer
})

update_product_meta_key_value_postmodel = api.model('UpdateProductMetaValueKey', {
	"meta_key_id":fields.Integer,
	"meta_key_value":fields.String,
	"image":fields.String,
	"organisation_id":fields.Integer,
	"last_update_id":fields.Integer,
	"meta_key_status":fields.Integer
})

product_meta_key_value_postmodel = api.model('SelectProductMetaKeyValue', {
	"meta_key_id":fields.Integer(required=True),
	"meta_key_value":fields.String(required=True),
	"image":fields.String,
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

home_category_postmodel = api.model('home_category', {
	"meta_key_value_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

product_postmodel = api.model('SelectProductPost', {
	"product_name":fields.String(required=True),
	"product_long_description":fields.String,
	"product_short_description":fields.String,
	"category_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"product_type":fields.String,
	"employee_id":fields.Integer,
	"brand_id":fields.Integer,
	"last_updated_ip_address":fields.Integer,
	"last_update_id":fields.Integer(required=True)
})

product_putmodel = api.model('SelectProduct', {
	"product_name":fields.String,
	"product_long_description":fields.String,
	"product_short_description":fields.String,
	"category_id":fields.Integer,
	"product_type":fields.String,
	"organisation_id":fields.Integer,
	"last_update_id":fields.Integer,
	"product_status":fields.Integer,
	"brand_id":fields.Integer
})

product_status_putmodel = api.model('SelectProductStatus', {	
	"product_status":fields.Integer
})

product_catalog_postmodel = api.model('SelectProductCatalog', {
	"product_name":fields.String(required=True),
	"product_long_description":fields.String,
	"product_short_description":fields.String,
	"catalog_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

product_catalog_meta_postmodel = api.model('SelectProductCatalogMeta', {
	"product_name":fields.String(required=True),
	"product_long_description":fields.String,
	"product_short_description":fields.String,
	"catalog_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"product_meta_code":fields.Integer(required=True),
	"meta_key_text":fields.String(required=True),
	"in_price":fields.Integer(required=True),
	"out_price":fields.Integer(required=True),
	"image":fields.List(fields.String),
	"product_type":fields.String,
	"product_type_id":fields.Integer,
	"discount":fields.Integer,
	"brand_id":fields.Integer,
	"category_id":fields.Integer,
	"top_selling":fields.Integer(required=True),
	"best_selling":fields.Integer(required=True),
	"latest_product": fields.Integer(required=True)
})

catalog_product_meta_postmodel = api.model('SelectCatalogProductMeta', {
	"product_name":fields.String(required=True),
	"product_long_description":fields.String,
	"product_short_description":fields.String,
	"catalog":fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"product_meta_code":fields.Integer(required=True),
	"meta_key_text":fields.String(required=True),
	"in_price":fields.Integer(required=True),
	"out_price":fields.Integer(required=True),
	"image":fields.List(fields.String),
	"product_type":fields.String,
	"product_type_id":fields.Integer,
	"discount":fields.Integer,
	"brand_id":fields.Integer,
	"category_id":fields.Integer,
	"top_selling":fields.Integer(required=True),
	"best_selling":fields.Integer(required=True),
	"latest_product": fields.Integer(required=True)
})


catalog_postmodel = api.model('SelectCatalog', {
	"catalog_name":fields.String(required=True),	
	"organisation_id":fields.Integer(required=True),
	"sequence":fields.Integer
})

catalog_category_postmodel = api.model('SelectCatalogCategory', {
	"catalog_name":fields.String(required=True),	
	"category_id":fields.List(fields.Integer),
	"organisation_id":fields.Integer(required=True),
	"sequence":fields.Integer,
	"is_home_section":fields.Integer
})

catalog_putmodel = api.model('putcatalog', {
	"catalog_name":fields.String,
	"sequence":	fields.Integer,
	"catalog_status":fields.Integer
})

product_price_meta_postmodel = api.model('product_price_meta', {
	"product_id":fields.Integer(required=True),
	"product_meta_code":fields.Integer(required=True),
	"meta_key_text":fields.String(required=True),
	"in_price":fields.Integer(required=True),
	"out_price":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"employee_id":fields.Integer,
	"last_updated_ip_address":fields.String,
	"last_update_id":fields.Integer(required=True)
})

product_meta_postmodel = api.model('product_meta', {
	"product_id":fields.Integer(required=True),
	"product_meta_code":fields.Integer(required=True),
	"meta_key_text":fields.String(required=True),
	"in_price":fields.Integer(required=True),
	"out_price":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"image":fields.List(fields.String),
	"discount":fields.Integer,
	"brand_id":fields.Integer,
	"category_id": fields.Integer,
	"top_selling": fields.Integer(required=True),
	"best_selling": fields.Integer(required=True),
	"latest_product": fields.Integer(required=True)
})

product_images_postmodel = api.model('SelectProductImage', {
	"product_meta_id":fields.Integer(required=True),
	"image":fields.String(required=True),
	"image_type":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"employee_id":fields.Integer,
	"last_updated_ip_address":fields.String,
	"last_update_id":fields.Integer(required=True)
})


product_images_gallery_postmodel = api.model('SelectProductImageGallery', {
	"product_meta_id":fields.Integer(required=True),
	"image":fields.String(required=True),
	"image_type":fields.Integer(required=True),
	"is_gallery":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"employee_id":fields.Integer,
	"last_update_id":fields.Integer(required=True)
})

discount_postmodel = api.model('SelectDiscount', {
	"discount":fields.Integer(required=True),
	"discount_image":fields.String,
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

discount_putmodel = api.model('discount_putmodel', {
	"discount":fields.Integer(required=True),
	"discount_image":fields.String
})

product_meta_discount_postmodel = api.model('SelectProductMetaDiscount', {
	"product_meta_id":fields.List(fields.Integer(required=True)),
	"discount_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

offer_postmodel = api.model('offer_post',{
	"offer_image":fields.String,
	"coupon_code":fields.String(required=True),
	"discount_percentage":fields.Integer,
	"absolute_price":fields.Integer,
	"discount_value":fields.Integer,
	"product_offer_type":fields.Integer,
	"is_landing_page":fields.Integer,
	"is_online":fields.Integer,
	"instruction":fields.String,
	"validity_date":fields.String,
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True),
	"product_id":fields.List(fields.Integer),
	"image":fields.List(fields.String)
})

product_variant_offer_postmodel = api.model('product_varint_offer_postmomdel',{	
	"offer_image":fields.String,
	"coupon_code":fields.String(required=True),
	"discount_percentage":fields.Integer,
	"absolute_price":fields.Integer,
	"discount_value":fields.Integer,
	"product_offer_type":fields.Integer,
	"is_landing_page":fields.Integer,
	"is_online":fields.Integer,
	"instruction":fields.String,
	"validity_date":fields.String,
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True),
	"product_meta_id":fields.List(fields.Integer),
	"image":fields.List(fields.String)
})

send_offer_postmodel = api.model('send_offer_postmodel',{
	"offer_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

send_catalouge_postmodel = api.model('send_catalouge_postmodel',{
	"catalog_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

offer_image_postmodel = api.model('offer_image',{
	"image":fields.List(fields.String(required=True)),
	"offer_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
})

offer_putmodel = api.model('offer',{
	"offer_image":fields.String,
	"coupon_code":fields.String,
	"discount_percentage":fields.Integer,
	"absolute_price":fields.Integer,
	"discount_value":fields.Integer,
	"product_offer_type":fields.Integer,
	"is_landing_page":fields.Integer,
	"is_online":fields.Integer,
	"instruction":fields.String,
	"product_id":fields.List(fields.Integer),
	"image":fields.List(fields.String),
	"is_show":fields.Integer,
	"validity_date":fields.String,
	"organisation_id":fields.Integer(required=True)
})

offer_productvariant_putmodel = api.model('offer_productvariant_putmodel',{
	"offer_image":fields.String,
	"coupon_code":fields.String,
	"discount_percentage":fields.Integer,
	"absolute_price":fields.Integer,
	"discount_value":fields.Integer,
	"product_offer_type":fields.Integer,
	"is_landing_page":fields.Integer,
	"is_online":fields.Integer,
	"instruction":fields.String,
	"product_meta_id":fields.List(fields.Integer),
	"image":fields.List(fields.String),
	"is_show":fields.Integer,
	"validity_date":fields.String,
	"organisation_id":fields.Integer(required=True)
})


product_offer_postmodel = api.model('product_offer',{
	"product_id":fields.List(fields.Integer(required=True)),
	"offer_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

product_brand_postmodel = api.model('product_brand',{
	"product_id":fields.List(fields.Integer(required=True)),
	"brand_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

product_category_postmodel = api.model('product_category',{
	"product_id":fields.List(fields.Integer(required=True)),
	"category_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

new_arrival_postmodel = api.model('new_arrival',{
	"new_arrival_image":fields.String(required=True),
	"product_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True),
	"image_type":fields.Integer(required=True),
	"language":fields.String(required=True)
})

product_new_arrival_postmodel = api.model('product_new_arrival',{
	"product_id":fields.List(fields.Integer(required=True)),
	"new_arrival_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

product_top_selling_postmodel = api.model('product_top_selling',{
	"product_meta_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

latest_product_postmodel = api.model('latest_product',{
	"product_meta_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

product_best_selling_postmodel = api.model('product_best_selling',{
	"product_meta_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

notification_postmodel = api.model('notification',{
	"text":fields.String(required=True),
	"image":fields.String(required=True),
	"email":fields.Integer,
	"whatsapp":fields.Integer,
	"sms":fields.Integer,
	"app_notification":fields.Integer
})

customer_notification_postmodel = api.model('notification',{
	"notification_id":fields.Integer(required=True),
	"product_id":fields.Integer(required=True),
	"customer_id":fields.Integer(required=True)
})

product_meta_inventory_postmodel = api.model('product_meta_inventory',{
	"product_meta_id":fields.Integer(required=True),
	"stock":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

product_meta_putmodel = api.model('product_meta_price',{	
	"in_price":fields.Integer,
	"out_price":fields.Integer,
	"product_meta_code":fields.Integer,	
	"loyalty_points":fields.Integer,
	"other_specification_json":fields.String
})

product_meta_image_putmodel = api.model('product_meta_image',{	
	"product_name":fields.String,
	"product_long_description":fields.String,
	"product_short_description":fields.String,
	"in_price":fields.Integer,
	"out_price":fields.Integer,
	"product_meta_code":fields.Integer,
	"image":fields.List(fields.String),
	"discount":fields.Integer,
	"organisation_id":fields.Integer(required=True),
	"brand_id":fields.Integer,
	"category_id":fields.Integer,
	"top_selling":fields.Integer(required=True),
	"best_selling":fields.Integer(required=True),
	"latest_product": fields.Integer(required=True)
})

stock_putmodel = api.model('stock_putmodel',{
	"retailer_store_id":fields.Integer(required=True),
	"stock":fields.Integer(required=True),
	"product_meta_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

enquiry_communication_postmodel = api.model('enquiry_communication_postmodel',{
	"enquiry_id":fields.Integer(required=True),
	"user_id":fields.Integer(required=True),
	"image":fields.String,
	"text":fields.String(required=True),
	"organisation_id":fields.Integer(required=True)
})

update_enquiery_type_postmodel = api.model('UpdateEnquieryType', {
	"enquiry_type":fields.String
})

enquiery_putmodel = api.model('UpdateEnquiery', {
	"enquiery_status":fields.Integer(required=True),
	"enquiry_id":fields.Integer(required=True)
})

update_referal_loyalty_putmodel = api.model('UpdateReferalLoyalty', {
	"loyality_amount":fields.Integer
})

enquiery_type_postmodel = api.model('EnquieryType', {
	"enquiry_type":fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"enquiery_type_status":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

upload_invoice_putmodel = api.model('uploadInvoice', {
	"invoice_url":fields.String(required=True)	
})


category_mapping_postmodel = api.model('uploadInvoice', {
	"category_id":fields.Integer(required=True),
	"meta_key_value_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id": fields.Integer(required=True) 	
})

budget_postmodel = api.model('budget_postmodel', {
	"category_id":fields.Integer(required=True),
	"greaterthanvalue":fields.Integer(required=True),
	"lessthanvalue":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)	
})

section_postmodel = api.model('section_postmodel', {
	"offer_section_name":fields.String(required=True),
	"offer_section_type":fields.Integer(required=True),
	"category_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"sequence":fields.Integer	
})

class DictModel(fields.Raw):
	def format(self, value):
		dictmodel = {}
		return dictmodel

referal_program_postmodel = api.model('referalProgram',{	
	"referal_user":DictModel(),
	"reffered_user":DictModel(),
	"organisation_id":fields.Integer(required=True)
})

suggested_accessories_postmodel = api.model('referalProgram',{
	"product_id":fields.Integer(required=True),
	"suggested_product_id":fields.Integer(required=True),
	"suggestion_type":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

retailer_store_postmodel = api.model('retailerStore',{
	"retailer_name": fields.String(required=True),
	"city": fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"image": fields.String(required=True)
})

delivery_question_postmodel = api.model('deliveryQuestionPost',{
	"location": fields.String(required=True),
	"rate": fields.Integer(required=True),
	"organisation_id": fields.Integer(required=True)
})

delivery_question_putmodel = api.model('deliveryQuestionPut',{
	"location": fields.String(required=True),
	"rate": fields.Integer(required=True)
})

checkout_question_postmodel = api.model('checkoutQuestionPost',{
	"question": fields.String(required=True),	
	"organisation_id": fields.Integer(required=True)
})

checkout_question_putmodel = api.model('checkoutQuestionPut',{
	"question": fields.String(required=True)
})

appmsg_model = api.model('appmsg_model', {	
	"firebase_key":fields.String(),
	"device_id":fields.String(),
	"text":fields.String(),
	"image":fields.String(),
	"title": fields.String(required=True),
})

notification_model = api.model('notification_model', {	
	"text":fields.String(),
	"image":fields.String(),
	"title": fields.String(required=True),
	"organisation_id": fields.Integer(required=True)
})

productcatalog_postmodel = api.model('productcatalog_postmodel',{
	"catalog_id": fields.Integer(required=True),	
	"product_id":fields.List(fields.Integer),
	"organisation_id": fields.Integer(required=True)
})

changeorderstatus_putmodel = api.model('changeOrderStatus',{
	"order_status":fields.String(required=True),
	"imageurl":fields.String,
	"retailer_remarks":fields.String,
})

update_offer_section_postmodel = api.model('UpdateOfferSection', {
	"offer_section_name":fields.String(required=True),
	"offer_section_type":fields.Integer(required=True),
	"category_id":fields.Integer(required=True),
	"sequence":fields.Integer

})

offer_section_postmodel = api.model('OfferSection', {
	"offer_id":fields.Integer(required=True),
	"section_id":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True)
})

update_offer_home_section_postmodel = api.model('UpdateOfferHomeSection', {
	"home_section":fields.Integer(required=True)
})

update_status_section_postmodel = api.model('UpdateStatusSection', {
	"section_status":fields.Integer(required=True)
})

compare_features_postmodel = api.model('CompareFeautures',{
	"product_meta_id":fields.Integer(required=True),
	"other_specifications": DictModel()
})

brand_category_postmodel = api.model('brand_category_postmodel',{
	"category_id":fields.Integer(required=True),
	"brand_name":fields.String(required=True),
	"brand_image":fields.String,
	"organisation_id":fields.Integer(required=True)
})

brand_putmodel = api.model('brand_putmodel',{	
	"brand_name":fields.String,
	"brand_image":fields.String,
	"category_id":fields.Integer
})

category_postmodel = api.model('category_postmodel', {
	"category_name":fields.String(required=True),
	"category_image":fields.String,
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

category_putmodel = api.model('category_putmodel',{	
	"category_name":fields.String,
	"category_image":fields.String
})


BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage)


#----------------------Add-Meta-Key---------------------#

@name_space.route("/AddMetaKey")
class AddMetaKey(Resource):
	@api.expect(product_meta_key_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		meta_key = details['meta_key']
		meta_key_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_query = ("""SELECT `meta_key`
			FROM `meta_key_master` WHERE `meta_key` = %s and organisation_id = %s""")

		getData = (meta_key,organisation_id)
		
		count_meta_key = cursor.execute(get_query,getData)

		if count_meta_key > 0:
			return ({"attributes": {
			    		"status_desc": "meta_key_details",
			    		"status": "error"
			    	},
			    	"responseList":"Tag Already Exsits" }), status.HTTP_200_OK

		else:	

			insert_query = ("""INSERT INTO `meta_key_master`(`meta_key`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")

			data = (meta_key,meta_key_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)

			details['meta_key_id'] = cursor.lastrowid

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "meta_key_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Meta-Key---------------------#

#-----------------------Meta-Key-Details---------------------#

@name_space.route("/getMetaKeyDetails/<int:organisation_id>/<int:meta_key_id>")	
class getMetaKeyDetails(Resource):
	def get(self,organisation_id,meta_key_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `meta_key_id`,`meta_key`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
			FROM `meta_key_master` WHERE `organisation_id` = %s and `meta_key_id` = %s""")

		get_data = (organisation_id,meta_key_id)
		cursor.execute(get_query,get_data)

		meta_key_data = cursor.fetchone()

		meta_key_data['last_update_ts'] = str(meta_key_data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "meta_key_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_key_data}), status.HTTP_200_OK

#-----------------------Meta-Key-Details---------------------#

#----------------------Update-Meta-Key---------------------#

@name_space.route("/UpdateMetaKey/<int:meta_key_id>")
class UpdateMetaKey(Resource):
	@api.expect(update_product_meta_key_postmodel)
	def put(self,meta_key_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()
		meta_key = details['meta_key']

		get_query = ("""SELECT `meta_key`
			FROM `meta_key_master` WHERE `meta_key` = %s and `meta_key_id` = %s """)
		getData = (meta_key,meta_key_id)		
		count_meta_key = cursor.execute(get_query,getData)

		if count_meta_key > 0:
			if details and "meta_key" in details:
				meta_key = details['meta_key']
				update_query = ("""UPDATE `meta_key_master` SET `meta_key` = %s
					WHERE `meta_key_id` = %s """)
				update_data = (meta_key,meta_key_id)
				cursor.execute(update_query,update_data)

			if details and "organisation_id" in details:
				organisation_id = details['organisation_id']
				update_query = ("""UPDATE `meta_key_master` SET `organisation_id` = %s
					WHERE `meta_key_id` = %s """)
				update_data = (organisation_id,meta_key_id)
				cursor.execute(update_query,update_data)

			if details and "last_update_id" in details:
				last_update_id = details['last_update_id']
				update_query = ("""UPDATE `meta_key_master` SET `last_update_id` = %s
					WHERE `meta_key_id` = %s """)
				update_data = (last_update_id,meta_key_id)
				cursor.execute(update_query,update_data)

			if details and "meta_key_status" in details:
				meta_key_status = details['meta_key_status']
				update_query = ("""UPDATE `meta_key_master` SET `status` = %s
					WHERE `meta_key_id` = %s """)
				update_data = (meta_key_status,meta_key_id)
				cursor.execute(update_query,update_data)

		else:
			get_query = ("""SELECT `meta_key`
				FROM `meta_key_master` WHERE `meta_key` = %s """)
			getData = (meta_key)		
			count_meta_key = cursor.execute(get_query,getData)

			if count_meta_key > 0:
				return ({"attributes": {
				    		"status_desc": "meta_key_details",
				    		"status": "error"
				    	},
				    	"responseList":"Tag Already Exsits" }), status.HTTP_200_OK
			else:
				if details and "meta_key" in details:
					meta_key = details['meta_key']
					update_query = ("""UPDATE `meta_key_master` SET `meta_key` = %s
						WHERE `meta_key_id` = %s """)
					update_data = (meta_key,meta_key_id)
					cursor.execute(update_query,update_data)

				if details and "organisation_id" in details:
					organisation_id = details['organisation_id']
					update_query = ("""UPDATE `meta_key_master` SET `organisation_id` = %s
						WHERE `meta_key_id` = %s """)
					update_data = (organisation_id,meta_key_id)
					cursor.execute(update_query,update_data)

				if details and "last_update_id" in details:
					last_update_id = details['last_update_id']
					update_query = ("""UPDATE `meta_key_master` SET `last_update_id` = %s
						WHERE `meta_key_id` = %s """)
					update_data = (last_update_id,meta_key_id)
					cursor.execute(update_query,update_data)

				if details and "meta_key_status" in details:
					meta_key_status = details['meta_key_status']
					update_query = ("""UPDATE `meta_key_master` SET `status` = %s
						WHERE `meta_key_id` = %s """)
					update_data = (meta_key_status,meta_key_id)
					cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Tag Key",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Meta-Key---------------------#

#----------------------Update-Meta-Key-status---------------------#
@name_space.route("/UpdateMetaKeyStatus/<int:meta_key_id>")
class UpdateMetaKeyStatus(Resource):
	@api.expect(update_product_meta_key_postmodel)
	def put(self,meta_key_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "meta_key_status" in details:
			meta_key_status = details['meta_key_status']
			update_query = ("""UPDATE `meta_key_master` SET `status` = %s
				WHERE `meta_key_id` = %s """)
			update_data = (meta_key_status,meta_key_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Meta Key",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Meta-Key-status---------------------#

#----------------------Meta-Key-List---------------------#
@name_space.route("/getMetaKeyList/<int:organisation_id>")	
class getMetaKeyList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `meta_key_id`,`meta_key`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
			FROM `meta_key_master` WHERE  `organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		meta_key_data = cursor.fetchall()

		for key,data in enumerate(meta_key_data):
			meta_key_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "meta_key_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_key_data}), status.HTTP_200_OK

#----------------------Meta-Key-List---------------------#

#----------------------Add-Meta-Key-Value---------------------#

@name_space.route("/AddMetaKeyValue")
class AddMetaKeyValue(Resource):
	@api.expect(product_meta_key_value_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		meta_key_id = details['meta_key_id']
		meta_key_value = details['meta_key_value']
		image = details['image']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_query = ("""SELECT `meta_key_id`,`meta_key_value`
			FROM `meta_key_value_master` WHERE `meta_key_id` = %s and `meta_key_value` = %s""")

		getData = (meta_key_id,meta_key_value)
		
		count_meta_key_value = cursor.execute(get_query,getData)

		if count_meta_key_value > 0:
			return ({"attributes": {
			    		"status_desc": "meta_key_value_details",
			    		"status": "error"
			    	},
			    	"responseList":"Meta Key Value Already Exsits" }), status.HTTP_200_OK

		else:	
			meta_key_value_status = 1
			insert_query = ("""INSERT INTO `meta_key_value_master`(`meta_key_id`,`meta_key_value`,`image`,`status`,
				`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

			data = (meta_key_id,meta_key_value,image,meta_key_value_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)

			details['meta_key_value_id'] = cursor.lastrowid

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "meta_key_value_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Meta-Key-Value---------------------#

#-----------------------Meta-Key-Value-Details---------------------#

@name_space.route("/getMetaKeyValueDetails/<int:organisation_id>/<int:meta_key_value_id>")	
class getMetaKeyDetails(Resource):
	def get(self,organisation_id,meta_key_value_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `meta_key_value_id`,`meta_key_id`,`meta_key_value`,`image`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
			FROM `meta_key_value_master` WHERE `organisation_id` = %s and `meta_key_value_id` = %s""")

		get_data = (organisation_id,meta_key_value_id)
		cursor.execute(get_query,get_data)

		meta_key_value_data = cursor.fetchone()

		meta_key_value_data['last_update_ts'] = str(meta_key_value_data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "meta_key_value_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_key_value_data}), status.HTTP_200_OK

#-----------------------Meta-Key-value-Details---------------------#

#----------------------Update-Meta-Key-value---------------------#

@name_space.route("/UpdateMetaKeyValue/<int:meta_key_value_id>")
class UpdateMetaKeyValue(Resource):
	@api.expect(update_product_meta_key_value_postmodel)
	def put(self,meta_key_value_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()
		meta_key_value = details['meta_key_value']
		meta_key_id = details['meta_key_id']

		get_query = ("""SELECT `meta_key_value`
			FROM `meta_key_value_master` WHERE `meta_key_value` = %s and `meta_key_id` = %s and meta_key_value_id = %s""")
		getData = (meta_key_value,meta_key_id,meta_key_value_id)		
		count_meta_key = cursor.execute(get_query,getData)

		if count_meta_key > 0:
			if details and "meta_key_id" in details:
				meta_key_id = details['meta_key_id']
				update_query = ("""UPDATE `meta_key_value_master` SET `meta_key_id` = %s
					WHERE `meta_key_value_id` = %s """)
				update_data = (meta_key_id,meta_key_value_id)
				cursor.execute(update_query,update_data)

			if details and "meta_key_value" in details:
				meta_key_value = details['meta_key_value']
				update_query = ("""UPDATE `meta_key_value_master` SET `meta_key_value` = %s
					WHERE `meta_key_value_id` = %s """)
				update_data = (meta_key_value,meta_key_value_id)
				cursor.execute(update_query,update_data)

			if details and "image" in details:
				image = details['image']
				update_query = ("""UPDATE `meta_key_value_master` SET `image` = %s
					WHERE `meta_key_value_id` = %s """)
				update_data = (image,meta_key_value_id)
				cursor.execute(update_query,update_data)

			if details and "organisation_id" in details:
				organisation_id = details['organisation_id']
				update_query = ("""UPDATE `meta_key_value_master` SET `organisation_id` = %s
					WHERE `meta_key_value_id` = %s """)
				update_data = (organisation_id,meta_key_id)
				cursor.execute(update_query,update_data)

			if details and "last_update_id" in details:
				last_update_id = details['last_update_id']
				update_query = ("""UPDATE `meta_key_value_master` SET `last_update_id` = %s
					WHERE `meta_key_value_id` = %s """)
				update_data = (last_update_id,meta_key_id)
				cursor.execute(update_query,update_data)

			if details and "meta_key_value_status" in details:
				meta_key_value_status = details['meta_key_value_status']
				update_query = ("""UPDATE `meta_key_value_master` SET `status` = %s
					WHERE `meta_key_value_id` = %s """)
				update_data = (meta_key_value_status,meta_key_id)
				cursor.execute(update_query,update_data)

		else:
			get_query = ("""SELECT `meta_key_value`
				FROM `meta_key_value_master` WHERE `meta_key_value` = %s and `meta_key_id` = %s""")
			getData = (meta_key_value,meta_key_id)		
			count_meta_key = cursor.execute(get_query,getData)

			if count_meta_key > 0:
				return ({"attributes": {
				    		"status_desc": "meta_key_value_details",
				    		"status": "error"
				    	},
				    	"responseList":"Tag Value Already Exsits" }), status.HTTP_200_OK
			else:
				if details and "meta_key_id" in details:
					meta_key_id = details['meta_key_id']
					update_query = ("""UPDATE `meta_key_value_master` SET `meta_key_id` = %s
						WHERE `meta_key_value_id` = %s """)
					update_data = (meta_key_id,meta_key_value_id)
					cursor.execute(update_query,update_data)

				if details and "meta_key_value" in details:
					meta_key_value = details['meta_key_value']
					update_query = ("""UPDATE `meta_key_value_master` SET `meta_key_value` = %s
						WHERE `meta_key_value_id` = %s """)
					update_data = (meta_key_value,meta_key_value_id)
					cursor.execute(update_query,update_data)

				if details and "image" in details:
					image = details['image']
					update_query = ("""UPDATE `meta_key_value_master` SET `image` = %s
						WHERE `meta_key_value_id` = %s """)
					update_data = (image,meta_key_value_id)
					cursor.execute(update_query,update_data)

				if details and "organisation_id" in details:
					organisation_id = details['organisation_id']
					update_query = ("""UPDATE `meta_key_value_master` SET `organisation_id` = %s
						WHERE `meta_key_value_id` = %s """)
					update_data = (organisation_id,meta_key_id)
					cursor.execute(update_query,update_data)

				if details and "last_update_id" in details:
					last_update_id = details['last_update_id']
					update_query = ("""UPDATE `meta_key_value_master` SET `last_update_id` = %s
						WHERE `meta_key_value_id` = %s """)
					update_data = (last_update_id,meta_key_id)
					cursor.execute(update_query,update_data)

				if details and "meta_key_value_status" in details:
					meta_key_value_status = details['meta_key_value_status']
					update_query = ("""UPDATE `meta_key_value_master` SET `status` = %s
						WHERE `meta_key_value_id` = %s """)
					update_data = (meta_key_value_status,meta_key_id)
					cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Meta Key Value",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Meta-Key---------------------#

#----------------------Update-Meta-Key-Value-status---------------------#
@name_space.route("/UpdateMetaKeyValueStatus/<int:meta_key_value_id>")
class UpdateMetaKeyValueStatus(Resource):
	@api.expect(update_product_meta_key_value_postmodel)
	def put(self,meta_key_value_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "meta_key_status" in details:
			meta_key_status = details['meta_key_status']
			update_query = ("""UPDATE `meta_key_value_master` SET `status` = %s
				WHERE `meta_key_value_id` = %s """)
			update_data = (meta_key_status,meta_key_value_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Meta Key value",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Meta-Key-Value-status---------------------#

#----------------------Delete-Meta-Key-Value---------------------#	
@name_space.route("/deleteMetaKeyValue/<int:meta_key_value_id>")	
class deleteMetaKeyValue(Resource):
	def delete(self,meta_key_value_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `meta_key_value_master` WHERE `meta_key_value_id` = %s """)
		delData = (meta_key_value_id)		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()


		return ({"attributes": {"status_desc": "delete_Meta_Key_value",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Meta-Key-Value---------------------#

#----------------------Add-Home-Category---------------------#

@name_space.route("/AddHomeCategory")
class AddHomeCategory(Resource):
	@api.expect(home_category_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()
		
		meta_key_value_id = details['meta_key_value_id']
		home_screen_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_query = ("""SELECT `meta_key_value_id`
			FROM `home_category_mapping` WHERE  `meta_key_value_id` = %s and `organisation_id` = %s""")

		getData = (meta_key_value_id,organisation_id)
		
		count_meta_key_value = cursor.execute(get_query,getData)

		if count_meta_key_value > 0:
			return ({"attributes": {
			    		"status_desc": "home_category_details",
			    		"status": "error"
			    	},
			    	"responseList":"Meta Value Already Exsits" }), status.HTTP_200_OK

		else:	

			insert_query = ("""INSERT INTO `home_category_mapping`(`meta_key_value_id`,`status`,
					`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

			data = (meta_key_value_id,home_screen_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)

			connection.commit()
			cursor.close()

			return ({"attributes": {
				    	"status_desc": "home_category_details",
				    	"status": "success"
				    },
				    "responseList":details}), status.HTTP_200_OK	

#----------------------Add-Home-Category---------------------#

#----------------------Add-Home-Brand---------------------#

@name_space.route("/AddHomeBrand")
class AddHomeBrand(Resource):
	@api.expect(home_category_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()
		
		meta_key_value_id = details['meta_key_value_id']
		home_screen_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_query = ("""SELECT `meta_key_value_id`
			FROM `home_brand_mapping` WHERE  `meta_key_value_id` = %s and `organisation_id` = %s""")

		getData = (meta_key_value_id,organisation_id)
		
		count_meta_key_value = cursor.execute(get_query,getData)

		if count_meta_key_value > 0:
			return ({"attributes": {
			    		"status_desc": "home_brand_details",
			    		"status": "error"
			    	},
			    	"responseList":"Meta Value Already Exsits" }), status.HTTP_200_OK

		else:	

			insert_query = ("""INSERT INTO `home_brand_mapping`(`meta_key_value_id`,`status`,
					`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

			data = (meta_key_value_id,home_screen_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)

			connection.commit()
			cursor.close()

			return ({"attributes": {
				    	"status_desc": "home_brand_details",
				    	"status": "success"
				    },
				    "responseList":details}), status.HTTP_200_OK	

#----------------------Add-Home-Brand---------------------#

#----------------------Delete-Home-Category---------------------#	
@name_space.route("/deleteHomeCategory/<int:meta_key_value_id>")	
class deleteHomeCategory(Resource):
	def delete(self,meta_key_value_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `home_category_mapping` WHERE `meta_key_value_id` = %s """)
		delData = (meta_key_value_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_home_category",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Home-Category---------------------#

#----------------------Delete-Home-Brand---------------------#	
@name_space.route("/deleteHomeBrand/<int:meta_key_value_id>")	
class deleteHomeBrand(Resource):
	def delete(self,meta_key_value_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `home_brand_mapping` WHERE `meta_key_value_id` = %s """)
		delData = (meta_key_value_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_home_brand",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Home-Brand---------------------#

#----------------------Meta-Key-value---------------------#
@name_space.route("/getMetaKeyValueList/<int:organisation_id>")	
class getMetaKeyValueList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT mkvm.`meta_key_value_id`,mkvm.`meta_key_id`,mkvm.`meta_key_value`,mkvm.`image`,mkvm.`status`,mkvm.`organisation_id`,
			mkvm.`last_update_id`,mkvm.`last_update_ts`,mkm.`meta_key`
			FROM `meta_key_value_master` mkvm
			INNER JOIN `meta_key_master` mkm ON mkm.`meta_key_id` = mkvm.`meta_key_id`
			 and mkvm.`organisation_id` = %s """)

		getdata = (organisation_id)
		cursor.execute(get_query,getdata)

		meta_value_data = cursor.fetchall()

		for key,data in enumerate(meta_value_data):
			meta_value_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "meta_key_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_value_data}), status.HTTP_200_OK

#----------------------Meta-Key-value---------------------#

#----------------------Meta-Key-value-List-meta-key-id---------------------#
@name_space.route("/getMetaKeyValueListMetaId/<int:meta_key_id>/<int:organisation_id>")	
class getMetaKeyValueListMetaId(Resource):
	def get(self,meta_key_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `meta_key_value_id`,`meta_key_id`,`meta_key_value`,`image`,`status`,`organisation_id`,
			`last_update_id`,`last_update_ts` FROM `meta_key_value_master` WHERE `meta_key_id` = %s
			 and `organisation_id` = %s and `status` = 1 """)

		getdata = (meta_key_id,organisation_id)
		cursor.execute(get_query,getdata)

		meta_value_data = cursor.fetchall()

		for key,data in enumerate(meta_value_data):

			if data['meta_key_id'] == 1:
				get_category_query = 	 ("""SELECT *
				FROM `home_category_mapping`
				WHERE `meta_key_value_id` = %s""")
				get_category_data = (data['meta_key_value_id'])
				rows_count_category = cursor.execute(get_category_query,get_category_data)

				if rows_count_category >0:
					meta_value_data[key]['home_category'] = 1
				else:
					meta_value_data[key]['home_category'] = 0

			else:
				get_brand_query = 	 ("""SELECT *
				FROM `home_brand_mapping`
				WHERE `meta_key_value_id` = %s""")
				get_brand_data = (data['meta_key_value_id'])
				rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

				if rows_count_brand >0:
					meta_value_data[key]['home_brand'] = 1
				else:
					meta_value_data[key]['home_brand'] = 0	

			meta_value_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "meta_key_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_value_data}), status.HTTP_200_OK

#----------------------Meta-Key-value-List-List-meta-key-id---------------------#

#----------------------Meta-Key-value-List-meta-key-id---------------------#
@name_space.route("/getMetaKeyValueListMetaIdWithParingOrganisation/<int:meta_key_id>/<int:organisation_id>/<int:paring_organisation_id>")	
class getMetaKeyValueListMetaIdWithParingOrganisation(Resource):
	def get(self,meta_key_id,organisation_id,paring_organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `meta_key_value_id`,`meta_key_id`,`meta_key_value`,`image`,`status`,`organisation_id`,
			`last_update_id`,`last_update_ts` FROM `meta_key_value_master` WHERE `meta_key_id` = %s
			 and `organisation_id` = %s and `status` = 1 """)

		getdata = (meta_key_id,organisation_id)
		cursor.execute(get_query,getdata)

		meta_value_data = cursor.fetchall()

		for key,data in enumerate(meta_value_data):

			if data['meta_key_id'] == 1:
				get_category_query = 	 ("""SELECT *
				FROM `home_category_mapping`
				WHERE `meta_key_value_id` = %s and `organisation_id` = %s""")
				get_category_data = (data['meta_key_value_id'],paring_organisation_id)
				rows_count_category = cursor.execute(get_category_query,get_category_data)

				if rows_count_category >0:
					meta_value_data[key]['home_category'] = 1
				else:
					meta_value_data[key]['home_category'] = 0

			else:
				get_brand_query = 	 ("""SELECT *
				FROM `home_brand_mapping`
				WHERE `meta_key_value_id` = %s and `organisation_id` = %s""")
				get_brand_data = (data['meta_key_value_id'],paring_organisation_id)
				rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

				if rows_count_brand >0:
					meta_value_data[key]['home_brand'] = 1
				else:
					meta_value_data[key]['home_brand'] = 0	

			meta_value_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "meta_key_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_value_data}), status.HTTP_200_OK

#----------------------Meta-Key-value-List-List-meta-key-id---------------------#

#----------------------Meta-Key-value-List-Like-Meta---------------------#
@name_space.route("/getMetaKeyValueListLikeMeta/<string:meta_key>/<int:organisation_id>")	
class getMetaKeyValueListLikeMeta(Resource):
	def get(self,meta_key,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_meta_query = ("""SELECT `meta_key_id`,`meta_key` FROM `meta_key_master`
							 WHERE  `meta_key` LIKE %s and `organisation_id` = %s """)
		getmetadata = (meta_key,organisation_id)
		count_meta_data = cursor.execute(get_meta_query,getmetadata)

		if count_meta_data >0:
			search_meta = cursor.fetchone()
			get_query = ("""SELECT `meta_key_value_id`,`meta_key_id`,`meta_key_value`,`image`,`status`,`organisation_id`,
				`last_update_id`,`last_update_ts` FROM `meta_key_value_master` WHERE `meta_key_id` = %s
				 and `organisation_id` = %s and `status` = 1 """)

			getdata = (search_meta['meta_key_id'],organisation_id)
			cursor.execute(get_query,getdata)

			meta_value_data = cursor.fetchall()

			for key,data in enumerate(meta_value_data):

				if data['meta_key_id'] == 1:
					get_category_query = 	 ("""SELECT *
					FROM `home_category_mapping`
					WHERE `meta_key_value_id` = %s""")
					get_category_data = (data['meta_key_value_id'])
					rows_count_category = cursor.execute(get_category_query,get_category_data)

					if rows_count_category >0:
						meta_value_data[key]['home_category'] = 1
					else:
						meta_value_data[key]['home_category'] = 0

				else:
					get_brand_query = 	 ("""SELECT *
					FROM `home_brand_mapping`
					WHERE `meta_key_value_id` = %s""")
					get_brand_data = (data['meta_key_value_id'])
					rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

					if rows_count_brand >0:
						meta_value_data[key]['home_brand'] = 1
					else:
						meta_value_data[key]['home_brand'] = 0	

				meta_value_data[key]['last_update_ts'] = str(data['last_update_ts'])

				meta_value_data[key]['meta_key'] = meta_key
		else:
			meta_value_data = []
				
		return ({"attributes": {
		    		"status_desc": "meta_key_details",
		    		"status": "success"
		    	},
		    	"responseList":meta_value_data}), status.HTTP_200_OK

#----------------------Meta-Key-value-List-Like-Meta---------------------#

#----------------------Add-Catalog---------------------#
@name_space.route("/AddCatalog")
class AddCatalog(Resource):
	@api.expect(catalog_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		catalog_name = details['catalog_name']
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']
		catalogstatus = 1

		if details and "sequence" in details:
			sequence = details['sequence']
		else:
			sequence = 1

		insert_query = ("""INSERT INTO `catalogs`(`catalog_name`,`organisation_id`,`status`,`sequence`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")
		data = (catalog_name,organisation_id,catalogstatus,sequence,last_update_id)
		cursor.execute(insert_query,data)
		catalog_id = cursor.lastrowid

		details['catalog_id'] = catalog_id	

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "catalog_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Add-Catalog---------------------#

#----------------------Add-Catalog-With-Category---------------------#
@name_space.route("/AddCatalogWithCategory")
class AddCatalogWithCategory(Resource):
	@api.expect(catalog_category_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		catalog_name = details['catalog_name']
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']		
		category_ids = details.get('category_id',[])

		catalogstatus = 1

		if details and "sequence" in details:
			sequence = details['sequence']
		else:
			sequence = 1

		if details and "is_home_section" in details:
			is_home_section = details['is_home_section']
		else:
			is_home_section = 0

		insert_query = ("""INSERT INTO `catalogs`(`catalog_name`,`organisation_id`,`is_home_section`,`status`,`sequence`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")
		data = (catalog_name,organisation_id,is_home_section,catalogstatus,sequence,last_update_id)
		cursor.execute(insert_query,data)
		catalog_id = cursor.lastrowid

		for key,category_id in enumerate(category_ids):			

			insert_catalog_category_query = ("""INSERT INTO `catalog_category_mapping`(`catalog_id`,`category_id`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

			catalog_category_data = (catalog_id,category_id,organisation_id,last_update_id)
			cursor.execute(insert_catalog_category_query,catalog_category_data)

		details['catalog_id'] = catalog_id

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		createPdfeUrl = BASE_URL + "ecommerce_product_admin/EcommerceProductAdmin/createCatalougePdf"
		payloadData = {
							"catalog_id":catalog_id,
													
					  }

		createPdf = requests.post(createPdfeUrl,data=json.dumps(payloadData), headers=headers).json()	

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "catalog_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Add-Catalog-With-Category---------------------#

#----------------------Send-Catalogue-Notification---------------------#
@name_space.route("/sendcatalogueNotification")	
class sendcatalogueNotification(Resource):
	@api.expect(send_catalouge_postmodel)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		catalog_id = details['catalog_id']
		organisation_id = details['organisation_id']

		get_query = ("""SELECT *
				FROM `catalogs` c				
				WHERE c.`catalog_id` = %s""")
		get_data = (catalog_id)

		cursor.execute(get_query,get_data)
		catalouge_data = cursor.fetchone()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		sendAppPushNotificationUrl = BASE_URL + "ecommerce_product/EcommerceProduct/sendNotifications"
		payloadpushData = {
									"organisation_id": organisation_id,
									"image":"",
									"text": catalouge_data['catalog_name']+" catalogue Created",
									"title": "catalouge"
								}
		print(payloadpushData)
		send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		return ({"attributes": {
				    		"status_desc": "catalouge_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK

#----------------------Send-Catalogue-Notification---------------------#

#----------------------Catalog-List---------------------#
@name_space.route("/catalogList/<int:organisation_id>")	
class catalogList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
				FROM `catalogs`
				WHERE `organisation_id` = %s and `status` = 1 ORDER BY `sequence`""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)
		catalog_data = cursor.fetchall()

		for key,data in enumerate(catalog_data):
			get_product_query = ("""SELECT count(*) as product_count 
				FROM `product_catalog_mapping` pcm 
				INNER JOIN `product` p ON p.`product_id` = pcm .`product_id`
				WHERE pcm.`catalog_id` = %s""")
			get_product_data = (data['catalog_id'])
			cursor.execute(get_product_query,get_product_data)
			catalog_product_count = cursor.fetchone()
			catalog_data[key]['product_count'] = catalog_product_count['product_count']

			get_category_query = ("""SELECT *
				FROM `catalog_category_mapping` ccm
				INNER JOIN `category` c ON c.`category_id` = ccm .`category_id`
				WHERE ccm.`catalog_id` = %s and ccm.`organisation_id` = %s""")
			get_category_data = (data['catalog_id'],organisation_id)
			count_category = cursor.execute(get_category_query,get_category_data)

			if count_category > 0:
				category_data = cursor.fetchone()
				catalog_data[key]['catalog_category'] = category_data['category_name']
			else:
				catalog_data[key]['catalog_category'] = ""

			catalog_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "catalog_details",
		    		"status": "success"
		    	},
		    	"responseList":catalog_data}), status.HTTP_200_OK

#----------------------Catalog-List---------------------#

#----------------------Catalog-Archieve-List---------------------#
@name_space.route("/catalogArchieveList/<int:organisation_id>")	
class catalogArchieveList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
				FROM `catalogs`
				WHERE `organisation_id` = %s and `status` = 0 ORDER BY `sequence`""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)
		catalog_data = cursor.fetchall()

		for key,data in enumerate(catalog_data):
			get_product_query = ("""SELECT count(*) as product_count 
				FROM `product_catalog_mapping` pcm 
				INNER JOIN `product` p ON p.`product_id` = pcm .`product_id`
				WHERE pcm.`catalog_id` = %s""")
			get_product_data = (data['catalog_id'])
			cursor.execute(get_product_query,get_product_data)
			catalog_product_count = cursor.fetchone()
			catalog_data[key]['product_count'] = catalog_product_count['product_count']

			get_category_query = ("""SELECT *
				FROM `catalog_category_mapping` ccm
				INNER JOIN `category` c ON c.`category_id` = ccm .`category_id`
				WHERE ccm.`catalog_id` = %s and ccm.`organisation_id` = %s""")
			get_category_data = (data['catalog_id'],organisation_id)
			count_category = cursor.execute(get_category_query,get_category_data)

			if count_category > 0:
				category_data = cursor.fetchone()
				catalog_data[key]['catalog_category'] = category_data['category_name']
			else:
				catalog_data[key]['catalog_category'] = ""

			catalog_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "catalog_details",
		    		"status": "success"
		    	},
		    	"responseList":catalog_data}), status.HTTP_200_OK

#----------------------Catalog-Archieve-List---------------------#

#----------------------Catalog-List-With-Product---------------------#
@name_space.route("/catalogListWithProduct/<int:organisation_id>")	
class catalogListWithProduct(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
				FROM `catalogs`
				WHERE `organisation_id` = %s""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)
		catalog_data = cursor.fetchall()

		for key,data in enumerate(catalog_data):
			get_product_query = ("""SELECT count(*) as product_count 
				FROM `product_catalog_mapping` pcm 
				INNER JOIN `product` p ON p.`product_id` = pcm .`product_id`
				WHERE pcm.`catalog_id` = %s""")
			get_product_data = (data['catalog_id'])
			cursor.execute(get_product_query,get_product_data)
			catalog_product_count = cursor.fetchone()
			catalog_data[key]['product_count'] = catalog_product_count['product_count']
			catalog_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
		    		"status_desc": "catalog_details",
		    		"status": "success"
		    	},
		    	"responseList":catalog_data}), status.HTTP_200_OK

#----------------------Catalog-List-With-Product---------------------#

#----------------------Catalog-List-With-Category---------------------#
@name_space.route("/catalogListWithategory/<int:organisation_id>/<int:catalog_id>")	
class catalogListWithategory(Resource):
	def get(self,organisation_id,catalog_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `category_id`,`category_name`
				FROM `category` where `organisation_id` = %s""")
		get_data = (organisation_id)		
		cursor.execute(get_query,get_data)
		category_data = cursor.fetchall()

		for key,data in enumerate(category_data):
			get_category_query = ("""SELECT * FROM `catalog_category_mapping` where `catalog_id` = %s and `category_id` = %s and `organisation_id` = %s""")
			get_category_data = (catalog_id,data['category_id'],organisation_id)
			count_category = cursor.execute(get_category_query,get_category_data)

			if count_category > 0:
				category_data[key]['is_category'] = 1

			else:
				category_data[key]['is_category'] = 0

		return ({"attributes": {
		    		"status_desc": "category_details",
		    		"status": "success"
		    	},
		    	"responseList":category_data}), status.HTTP_200_OK

#----------------------Catalog-List-With-Category---------------------#


#----------------------Catalog-Details---------------------#
@name_space.route("/catalogDetails/<int:catalog_id>")	
class catalogDetails(Resource):
	def get(self,catalog_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT catalog_id,catalog_name,pdf_link
				FROM `catalogs`
				WHERE `catalog_id` = %s""")
		get_data = (catalog_id)

		cursor.execute(get_query,get_data)
		catalog_data = cursor.fetchone()	

		return ({"attributes": {
		    		"status_desc": "catalog_details",
		    		"status": "success"
		    	},
		    	"responseList":catalog_data}), status.HTTP_200_OK

#----------------------Catalog-Details---------------------#

#----------------------Add-Catalog-Product---------------------#

@name_space.route("/AddCatalogProduct")
class AddCatalogProdcut(Resource):
	@api.expect(product_catalog_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_name = details['product_name']
		product_long_description = details['product_long_description']
		product_short_description = details['product_short_description']
		catalog_id = details['catalog_id']		
		product_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']

		insert_query = ("""INSERT INTO `product`(`product_name`,`product_long_description`,
			`product_short_description`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

		data = (product_name,product_long_description,product_short_description,
			product_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		product_id = cursor.lastrowid

		insert_product_catalog_query = ("""INSERT INTO `product_catalog_mapping`(`catalog_id`,`product_id`,`organisation_id`) 
				VALUES(%s,%s,%s)""")

		product_catalog_data = (catalog_id,product_id,organisation_id)
		cursor.execute(insert_product_catalog_query,product_catalog_data)		

		details['product_id'] = product_id	

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Add-Catalog-Product---------------------#

#----------------------Add-Product---------------------#

@name_space.route("/AddProduct")
class AddProduct(Resource):
	@api.expect(product_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_name = details['product_name']
		product_long_description = details['product_long_description']
		product_short_description = details['product_short_description']
		category_id = details['category_id']		
		category_id = details['category_id']
		product_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		insert_query = ("""INSERT INTO `product`(`product_name`,`product_long_description`,
			`product_short_description`,`category_id`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_name,product_long_description,product_short_description,category_id,
				product_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		product_id = cursor.lastrowid

		details['product_id'] = product_id	

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Add-Product---------------------#

#----------------------Add-Product---------------------#

@name_space.route("/AddProductFromProductOrganisationMapping")
class AddProductFromProductOrganisationMapping(Resource):
	@api.expect(product_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_name = details['product_name']
		product_long_description = details['product_long_description']
		product_short_description = details['product_short_description']
		category_id = details['category_id']	
		if details and "product_type" in details:	
			product_type = details['product_type']
		else:
			product_type = ""
		product_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		if details and "employee_id" in details:
			employee_id = details['employee_id']
		else:
			employee_id = 0

		if details and "last_updated_ip_address" in details:
			last_updated_ip_address = details['last_updated_ip_address']
		else:
			last_updated_ip_address = ""


		insert_query = ("""INSERT INTO `product`(`product_name`,`product_long_description`,
			`product_short_description`,`category_id`,`product_type`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_name,product_long_description,product_short_description,category_id,product_type,
				product_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		product_id = cursor.lastrowid

		insert_product_organisation_query = ("""INSERT INTO `product_organisation_mapping`(`product_id`,`organisation_id`,
			`last_update_id`) 
				VALUES(%s,%s,%s)""")
		product_organisation_data = (product_id,organisation_id,last_update_id)
		cursor.execute(insert_product_organisation_query,product_organisation_data)

		details['product_id'] = product_id

		if details and "brand_id" in details:
			brand_id = details['brand_id']
			print(brand_id)

			get_query = ("""SELECT *
			FROM `product_brand_mapping` where `product_id` = %s and `organisation_id` = %s""")
			get_data = (product_id,organisation_id)

			count_product_brand = cursor.execute(get_query,get_data)

			if count_product_brand > 0:
				product_brand_data = cursor.fetchone()		
				print(product_brand_data)		

				update_query = ("""UPDATE `product_brand_mapping` SET `brand_id` = %s
				WHERE `product_id` = %s and `organisation_id` = %s""")
				update_data = (brand_id,product_id,organisation_id)
				cursor.execute(update_query,update_data)

			else:
				product_brnad_sttatus = 1
				insert_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (brand_id,product_id,product_brnad_sttatus,organisation_id,organisation_id)
				cursor.execute(insert_query,data)


		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
		payloadData = {
							"product_id":product_id,
							"comments": "Add Product",
							"employee_id":employee_id,
							"organisation_id":organisation_id,
							"last_updated_ip_address":last_updated_ip_address
						}
		print(payloadData)

		requests.post(url,data=json.dumps(payloadData), headers=headers).json()

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Add-Product---------------------#

#----------------------Add-Product-Catalog---------------------#

@name_space.route("/AddProductCatalog")
class AddProductCatalog(Resource):
	@api.expect(productcatalog_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		catalog_id = details['catalog_id']
		product_id = details['product_id']

		product_ids = details.get('product_id',[])

		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id'] 

		for key,product_id in enumerate(product_ids):

			get_query = ("""SELECT `mapping_id`
				FROM `product_catalog_mapping` WHERE  `catalog_id` = %s and `product_id` = %s """)

			getData = (catalog_id,product_id)
			
			count_product = cursor.execute(get_query,getData)			

			if count_product < 1:

				insert_query = ("""INSERT INTO `product_catalog_mapping`(`catalog_id`,`product_id`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

				data = (catalog_id,product_id,organisation_id,last_update_id)
				cursor.execute(insert_query,data)
			

		connection.commit()
		cursor.close()

		return ({"attributes": {
					    		"status_desc": "catalog_product",
					    		"status": "success"
					    	},
					    "responseList":details}), status.HTTP_200_OK	


#----------------------Add-Product-Catalog---------------------#

#----------------------Delete-Catalog-Product---------------------#	
@name_space.route("/deleteCatalogProduct/<int:catalog_id>/<int:product_id>/<int:organisation_id>")	
class deleteCatalogProduct(Resource):
	def delete(self,catalog_id,product_id,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_catalog_mapping` WHERE `catalog_id` = %s and `product_id` = %s and `organisation_id` = %s""")
		delData = (catalog_id,product_id,organisation_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_catalog_product",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Latest-Product---------------------#

#----------------------Product-List-By-Catalog-Id---------------------#
@name_space.route("/productListByCatalogId/<int:organisation_id>/<int:catalog_id>")	
class productListByCatalogId(Resource):
	def get(self,organisation_id,catalog_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,p.`status`,pom.`product_status`,p.`product_type`,p.`category_id` as `product_type_id`
					FROM `product` p
					INNER JOIN `product_catalog_mapping` pcm ON pcm.`product_id` = p.`product_id`
					INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
					WHERE pom.`organisation_id` = %s and pcm.`catalog_id` = %s""")
		get_data = (organisation_id,catalog_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_product_meta = (""" SELECT pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price` FROM `product_meta` pm WHERE 
			`out_price` =  ( SELECT MIN(`out_price`) FROM product_meta  where product_id = %s) and product_id= %s """)
			get_product_meta_data = (data['product_id'],data['product_id'])
			count_product_meta = cursor.execute(get_product_meta,get_product_meta_data)

			

			product_meta_data = cursor.fetchone()

			product_data[key]['product_meta_id'] = product_meta_data['product_meta_id']
			product_data[key]['product_meta_code'] = product_meta_data['product_meta_code']
			product_data[key]['meta_key_text'] = product_meta_data['meta_key_text']
			product_data[key]['in_price'] = product_meta_data['in_price']
			product_data[key]['out_price'] = product_meta_data['out_price']
			#get_product_meta_query = ("""SELECT pm.`product_meta_id`,pm.`product_meta_code`,pm.`out_price`,pm.`product_meta_id`,pm.`meta_key_text`
						#FROM `product_meta` pm WHERE pm.`product_id` = %s""")
			#get_product_data = (data['product_id'])
			#product_meta_count = cursor.execute(get_product_meta_query,get_product_data)

			#if product_meta_count >0:				
			#product_meta = cursor.fetchone()

			#product_data[key]['product_meta_id'] = data['product_meta_id']
			#product_data[key]['product_meta_code'] = product_meta['product_meta_code']
			#product_data[key]['out_price'] = product_meta['out_price']				

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
					

			image_a = []	
			get_query_images = ("""SELECT `image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s """)
			getdata_images = (data['product_meta_id'])
			cursor.execute(get_query_images,getdata_images)
			images = cursor.fetchall()

			for image in images:
				image_a.append(image['image'])

			product_data[key]['images'] = image_a

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
				product_data[key]['after_discounted_price'] = round(actual_amount,2)

			else:
				product_data[key]['discount'] = 0
				product_data[key]['after_discounted_price'] = data['out_price']

			get_brand_mapping_query = ("""SELECT mm.`meta_key_value` as `brand`,  mm.`meta_key_value_id` as `brand_id`
									FROM `product_brand_mapping` pbm
									INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = pbm.`brand_id`
									WHERE pbm.`product_id` = %s
								""")
			get_brand_mapping_data = (data['product_id'])
			count_brand_mapping = cursor.execute(get_brand_mapping_query,get_brand_mapping_data)

			if count_brand_mapping > 0:
				product_brnad = cursor.fetchone() 
				product_data[key]['brand'] = product_brnad['brand']
				product_data[key]['brand_id'] = product_brnad['brand_id']
			else:
				product_data[key]['brand'] = ""	
				product_data[key]['brand_id'] = 0


			get_category_mapping_query = ("""SELECT mm.`meta_key_value` as `category`, mm.`meta_key_value_id` as `category_id`
									FROM `product_category_mapping` pbm
									INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = pbm.`category_id`
									WHERE pbm.`product_id` = %s
								""")
			get_category_mapping_data = (data['product_id'])
			count_category_mapping = cursor.execute(get_category_mapping_query,get_category_mapping_data)

			if count_category_mapping > 0:
				product_category = cursor.fetchone() 
				product_data[key]['category'] = product_category['category']
				product_data[key]['category_id'] = product_category['category_id']
			else:
				product_data[key]['category'] = ""
				product_data[key]['category_id'] = 0

			get_best_sellling_mapping_query = ("""SELECT * from product_best_selling_mapping
											WHERE `product_meta_id` = %s
										""")
			get_best_selling_mapping_data = (data['product_meta_id'])
			count_best_selling = cursor.execute(get_best_sellling_mapping_query,get_best_selling_mapping_data)

			if count_best_selling > 0:
				product_data[key]['best_selling'] = 1
			else:
				product_data[key]['best_selling'] = 0


			get_top_sellling_mapping_query = ("""SELECT * from product_top_selling_mapping
											WHERE `product_meta_id` = %s
										""")
			get_top_sellling_mapping_data = (data['product_meta_id'])
			count_top_selling = cursor.execute(get_top_sellling_mapping_query,get_top_sellling_mapping_data)

			if count_top_selling > 0:
				product_data[key]['top_selling'] = 1
			else:
				product_data[key]['top_selling'] = 0

			get_latest_product_mapping_query = ("""SELECT * from latest_product_mapping
											WHERE `product_meta_id` = %s
										""")
			get_latest_product_mapping_data = (data['product_meta_id'])
			count_latest_product = cursor.execute(get_latest_product_mapping_query,get_latest_product_mapping_data)

			if count_latest_product > 0:
				product_data[key]['latest_product'] = 1
			else:
				product_data[key]['latest_product'] = 0

			get_offer_product =  ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,
				o.`absolute_price`,o.`discount_value`,o.`product_offer_type`,o.`is_landing_page`,o.`is_online`,o.`instruction`,o.`status`
			FROM `product_offer_mapping` pom 
			INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id` 
			WHERE pom.`organisation_id` = %s and pom.`product_id` = %s""")
			get_offer_data = (organisation_id,data['product_id'])
			count_offer_product = cursor.execute(get_offer_product,get_offer_data)
			if count_offer_product > 0:
				offer_product = cursor.fetchall()
				product_data[key]['offer_product'] = offer_product
			else:
				product_data[key]['offer_product'] = []

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List-By-Catalog-Id---------------------#

#----------------------Product-List-With-Out-Meta-By-Catalog-Id---------------------#
@name_space.route("/productListWithOutMetaByCatalogId/<int:catalog_id>")	
class productListWithOutMetaByCatalogId(Resource):
	def get(self,catalog_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`					
					FROM `product` p					
					INNER JOIN `product_catalog_mapping` pcm ON pcm.`product_id` = p.`product_id`
					WHERE p.`status` = 1 and pcm.`catalog_id` = %s""")
		get_data = (catalog_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()	

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List-With-Out-Meta-By-Catalog-Id---------------------#

#----------------------Organisation-Product-List-With-Out-Meta-By-Catalog-Id---------------------#
@name_space.route("/organisationproductListWithOutMetaByCatalogId/<int:catalog_id>/<int:organisation_id>")	
class organisationproductListWithOutMetaByCatalogId(Resource):
	def get(self,catalog_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`					
					FROM `product` p					
					WHERE p.`status` = 1 and p.`organisation_id` = %s""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_product_catalog_query = (""" SELECT * FROM `product_catalog_mapping` WHERE `product_id` = %s and `catalog_id` = %s  """)	
			get_product_catalog_data = (data['product_id'],catalog_id)

			count = cursor.execute(get_product_catalog_query,get_product_catalog_data)

			if count > 0:
				product_data[key]['is_prodcut_catalog'] = 1
			else:
				product_data[key]['is_prodcut_catalog'] = 0

			get_query_meta = (""" SELECT pm.`product_meta_id` from `product_meta` pm where pm.`product_id` = %s""")
			get_data_meta = (data['product_id'])
			count_product_meta = cursor.execute(get_query_meta,get_data_meta)

			if count_product_meta > 0:
				get_data_product_meta = cursor.fetchone()			

				product_data[key]['is_product_meta'] = 1
			else:				
				product_data[key]['is_product_meta'] = 0
				
		new_product_data = []

		for nkey,ndata in enumerate(product_data):
			if ndata['is_product_meta'] == 1:
				new_product_data.append(product_data[nkey])
				
		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":new_product_data}), status.HTTP_200_OK

#----------------------Organisation-Product-List-With-Out-Meta-By-Catalog-Id---------------------#


#----------------------Organisation-Product-List-With-Out-Meta-By-Catalog-Id---------------------#
@name_space.route("/organisationproductListWithOutMetaFromProductOrganisationMappingByCatalogId/<int:catalog_id>/<int:organisation_id>")	
class organisationproductListWithOutMetaFromProductOrganisationMappingByCatalogId(Resource):
	def get(self,catalog_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`					
					FROM `product` p
					INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`					
					WHERE p.`status` = 1 and pom.`organisation_id` = %s""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_product_catalog_query = (""" SELECT * FROM `product_catalog_mapping` WHERE `product_id` = %s and `catalog_id` = %s  """)	
			get_product_catalog_data = (data['product_id'],catalog_id)

			count = cursor.execute(get_product_catalog_query,get_product_catalog_data)

			if count > 0:
				product_data[key]['is_prodcut_catalog'] = 1
			else:
				product_data[key]['is_prodcut_catalog'] = 0
				
		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Organisation-Product-List-With-Out-Meta-By-Catalog-Id---------------------#

#----------------------Product-Details-By-Product-Id---------------------#
@name_space.route("/productDetailsByProductId/<int:product_id>/<int:product_meta_id>")	
class productDetailsByProductId(Resource):
	def get(self,product_id,product_meta_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,p.`product_type`
					FROM `product` p					
					WHERE p.`status` = 1 and p.`product_id` = %s""")
		get_data = (product_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchone()

		
		get_product_meta_query = ("""SELECT pm.`product_meta_id`,pm.`product_meta_code`,pm.`in_price`,pm.`out_price`,pm.`product_meta_id`,pm.`meta_key_text`
					FROM `product_meta` pm WHERE pm.`product_id` = %s and pm.`product_meta_id` =%s""")
		get_product_data = (product_id,product_meta_id)
		product_meta_count = cursor.execute(get_product_meta_query,get_product_data)

		if product_meta_count >0:				
			product_meta = cursor.fetchone()

			product_data['product_meta_id'] = product_meta['product_meta_id']
			product_data['product_meta_code'] = product_meta['product_meta_code']
			product_data['out_price'] = product_meta['out_price']	
			product_data['in_price'] = product_meta['in_price']			

			a_string = product_meta['meta_key_text']
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
					

			image_a = []	
			get_query_images = ("""SELECT `image`
						FROM `product_meta_images` WHERE `product_meta_id` = %s """)
			getdata_images = (product_meta['product_meta_id'])
			cursor.execute(get_query_images,getdata_images)
			images = cursor.fetchall()

			for image in images:
				image_a.append(image['image'])

			product_data['images'] = image_a

			get_query_discount = ("""SELECT `discount`
									FROM `product_meta_discount_mapping` pdm
									INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
									WHERE `product_meta_id` = %s """)
			getdata_discount = (product_meta['product_meta_id'])
			count_dicscount = cursor.execute(get_query_discount,getdata_discount)

			if count_dicscount > 0:
				product_meta_discount = cursor.fetchone()
				product_data['discount'] = product_meta_discount['discount']

				discount = (product_meta['out_price']/100)*product_meta_discount['discount']
				actual_amount = product_meta['out_price'] - discount
				product_data['after_discounted_price'] = round(actual_amount,2)

			else:
				product_data['discount'] = 0
				product_data['after_discounted_price'] = product_meta['out_price']


			get_brand_mapping_query = ("""SELECT mm.`meta_key_value` as `brand`,  mm.`meta_key_value_id` as `brand_id`
									FROM `product_brand_mapping` pbm
									INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = pbm.`brand_id`
									WHERE pbm.`product_id` = %s
								""")
			get_brand_mapping_data = (product_data['product_id'])
			count_brand_mapping = cursor.execute(get_brand_mapping_query,get_brand_mapping_data)

			if count_brand_mapping > 0:
				product_brnad = cursor.fetchone() 
				product_data['brand'] = product_brnad['brand']
				product_data['brand_id'] = product_brnad['brand_id']
			else:
				product_data['brand'] = ""	
				product_data['brand_id'] = 0


			get_category_mapping_query = ("""SELECT mm.`meta_key_value` as `category`, mm.`meta_key_value_id` as `category_id`
									FROM `product_category_mapping` pbm
									INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = pbm.`category_id`
									WHERE pbm.`product_id` = %s
								""")
			get_category_mapping_data = (product_data['product_id'])
			count_category_mapping = cursor.execute(get_category_mapping_query,get_category_mapping_data)

			if count_category_mapping > 0:
				product_category = cursor.fetchone() 
				product_data['category'] = product_category['category']
				product_data['category_id'] = product_category['category_id']
			else:
				product_data['category'] = ""
				product_data['category_id'] = 0

			get_best_sellling_mapping_query = ("""SELECT * from product_best_selling_mapping
											WHERE `product_meta_id` = %s
										""")
			get_best_selling_mapping_data = (product_meta['product_meta_id'])
			count_best_selling = cursor.execute(get_best_sellling_mapping_query,get_best_selling_mapping_data)

			if count_best_selling > 0:
				product_data['best_selling'] = 1
			else:
				product_data['best_selling'] = 0


			get_top_sellling_mapping_query = ("""SELECT * from product_top_selling_mapping
											WHERE `product_meta_id` = %s
										""")
			get_top_sellling_mapping_data = (product_meta['product_meta_id'])
			count_top_selling = cursor.execute(get_top_sellling_mapping_query,get_top_sellling_mapping_data)

			if count_top_selling > 0:
				product_data['top_selling'] = 1
			else:
				product_data['top_selling'] = 0

			get_latest_product_mapping_query = ("""SELECT * from latest_product_mapping
											WHERE `product_meta_id` = %s
										""")
			get_latest_product_mapping_data = (product_meta['product_meta_id'])
			count_latest_product = cursor.execute(get_latest_product_mapping_query,get_latest_product_mapping_data)

			if count_latest_product > 0:
				product_data['latest_product'] = 1
			else:
				product_data['latest_product'] = 0

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-Details-By-Product-Id---------------------#

#----------------------Product-Details-By-Product-Id-With-Organisation-Id---------------------#
@name_space.route("/productDetailsByProductIdWithOrganisationId/<int:product_id>/<int:product_meta_id>/<int:organisation_id>")	
class productDetailsByProductIdWithOrganisationId(Resource):
	def get(self,product_id,product_meta_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,p.`product_type`
					FROM `product` p					
					WHERE p.`status` = 1 and p.`product_id` = %s""")
		get_data = (product_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchone()

		
		get_product_meta_query = ("""SELECT pm.`product_meta_id`,pm.`product_meta_code`,pm.`in_price`,pm.`out_price`,pm.`product_meta_id`,pm.`meta_key_text`
					FROM `product_meta` pm WHERE pm.`product_id` = %s and pm.`product_meta_id` =%s""")
		get_product_data = (product_id,product_meta_id)
		product_meta_count = cursor.execute(get_product_meta_query,get_product_data)

		if product_meta_count >0:				
			product_meta = cursor.fetchone()

			product_data['product_meta_id'] = product_meta['product_meta_id']
			product_data['product_meta_code'] = product_meta['product_meta_code']				
			product_data['in_price'] = product_meta['in_price']

			get_out_price_query = (""" SELECT `out_price` FROM `product_meta_out_price` where `organisation_id` = %s and `status` = 1 and `product_meta_id` = %s""")
			get_out_price_data = (organisation_id, product_meta['product_meta_id'])		

			count_out_price_data = cursor.execute(get_out_price_query,get_out_price_data)
			if count_out_price_data >0:
				out_price_data = cursor.fetchone()
				product_data['out_price'] = out_price_data['out_price']
			else:
				product_data['out_price'] = product_meta['out_price']			

			a_string = product_meta['meta_key_text']
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
					

			image_a = []	
			get_query_images = ("""SELECT `image`
						FROM `product_meta_images` WHERE `product_meta_id` = %s """)
			getdata_images = (product_meta['product_meta_id'])
			cursor.execute(get_query_images,getdata_images)
			images = cursor.fetchall()

			for image in images:
				image_a.append(image['image'])

			product_data['images'] = image_a

			get_query_discount = ("""SELECT `discount`
									FROM `product_meta_discount_mapping` pdm
									INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
									WHERE `product_meta_id` = %s """)
			getdata_discount = (product_meta['product_meta_id'])
			count_dicscount = cursor.execute(get_query_discount,getdata_discount)

			if count_dicscount > 0:
				product_meta_discount = cursor.fetchone()
				product_data['discount'] = product_meta_discount['discount']

				discount = (product_meta['out_price']/100)*product_meta_discount['discount']
				actual_amount = product_meta['out_price'] - discount
				product_data['after_discounted_price'] = round(actual_amount,2)

			else:
				product_data['discount'] = 0
				product_data['after_discounted_price'] = product_meta['out_price']


			get_brand_mapping_query = ("""SELECT mm.`meta_key_value` as `brand`,  mm.`meta_key_value_id` as `brand_id`
									FROM `product_brand_mapping` pbm
									INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = pbm.`brand_id`
									WHERE pbm.`product_id` = %s
								""")
			get_brand_mapping_data = (product_data['product_id'])
			count_brand_mapping = cursor.execute(get_brand_mapping_query,get_brand_mapping_data)

			if count_brand_mapping > 0:
				product_brnad = cursor.fetchone() 
				product_data['brand'] = product_brnad['brand']
				product_data['brand_id'] = product_brnad['brand_id']
			else:
				product_data['brand'] = ""	
				product_data['brand_id'] = 0


			get_category_mapping_query = ("""SELECT mm.`meta_key_value` as `category`, mm.`meta_key_value_id` as `category_id`
									FROM `product_category_mapping` pbm
									INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = pbm.`category_id`
									WHERE pbm.`product_id` = %s
								""")
			get_category_mapping_data = (product_data['product_id'])
			count_category_mapping = cursor.execute(get_category_mapping_query,get_category_mapping_data)

			if count_category_mapping > 0:
				product_category = cursor.fetchone() 
				product_data['category'] = product_category['category']
				product_data['category_id'] = product_category['category_id']
			else:
				product_data['category'] = ""
				product_data['category_id'] = 0

			get_best_sellling_mapping_query = ("""SELECT * from product_best_selling_mapping
											WHERE `product_meta_id` = %s
										""")
			get_best_selling_mapping_data = (product_meta['product_meta_id'])
			count_best_selling = cursor.execute(get_best_sellling_mapping_query,get_best_selling_mapping_data)

			if count_best_selling > 0:
				product_data['best_selling'] = 1
			else:
				product_data['best_selling'] = 0


			get_top_sellling_mapping_query = ("""SELECT * from product_top_selling_mapping
											WHERE `product_meta_id` = %s
										""")
			get_top_sellling_mapping_data = (product_meta['product_meta_id'])
			count_top_selling = cursor.execute(get_top_sellling_mapping_query,get_top_sellling_mapping_data)

			if count_top_selling > 0:
				product_data['top_selling'] = 1
			else:
				product_data['top_selling'] = 0

			get_latest_product_mapping_query = ("""SELECT * from latest_product_mapping
											WHERE `product_meta_id` = %s
										""")
			get_latest_product_mapping_data = (product_meta['product_meta_id'])
			count_latest_product = cursor.execute(get_latest_product_mapping_query,get_latest_product_mapping_data)

			if count_latest_product > 0:
				product_data['latest_product'] = 1
			else:
				product_data['latest_product'] = 0

		get_product_sub_category_query = ("""SELECT mm.`meta_key_value` from product_sub_category_mapping pscm
										INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = pscm.`sub_category_id`
										WHERE `product_id` = %s
										""")
		get_product_sub_category_data = (product_id)
		count_product_sub_category = cursor.execute(get_product_sub_category_query,get_product_sub_category_data)

		if count_product_sub_category > 0:
			product_sub_category = cursor.fetchone()
			product_data['product_sub_category'] = product_sub_category['meta_key_value']
		else:
			product_data['product_sub_category'] = ""


		get_product_section_query = ("""SELECT mm.`meta_key_value` from product_section_mapping psm
										INNER JOIN `meta_key_value_master` mm ON mm.`meta_key_value_id` = psm.`section_id`
										WHERE `product_id` = %s
										""")
		get_product_section_data = (product_id)
		count_product_section = cursor.execute(get_product_section_query,get_product_section_data)

		if count_product_section > 0:
			product_section = cursor.fetchone()
			product_data['product_section'] = product_section['meta_key_value']
		else:
			product_data['product_section'] = ""	

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-Details-By-Product-Id-With-Organisation-Id---------------------#

#----------------------Product-List---------------------#
@name_space.route("/productList/<int:organisation_id>/<int:category_id>")	
class productList(Resource):
	def get(self,organisation_id,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		if category_id == 0:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id`
				FROM `product` p
				INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
				WHERE  p.`organisation_id` = %s""")
			get_data = (organisation_id)			
		else:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`status`,p.`category_id` as `product_type_id`
				FROM `product` p
				WHERE  p.`organisation_id` = %s and p.`category_id` = %s""")
			get_data = (organisation_id,category_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_offer_query = 	 ("""SELECT o.`offer_image`,o.`offer_id`
				FROM `product_offer_mapping` pom
				INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`
				WHERE pom.`product_id` = %s""")
			get_offer_data = (data['product_id'])
			rows_count_offer = cursor.execute(get_offer_query,get_offer_data)

			if rows_count_offer >0:
				product_offer_iamge = cursor.fetchone()
				product_data[key]['offer_id'] = product_offer_iamge['offer_id']				
				product_data[key]['offer_image'] = product_offer_iamge['offer_image']
			else:
				product_data[key]['offer_id'] = ""
				product_data[key]['offer_image'] = ""

			get_new_arrival_query = 	 ("""SELECT n.`new_arrival_image`,n.`new_arrival_id`
				FROM `product_new_arrival_mapping` pnam
				INNER JOIN `new_arrival` n ON n.`new_arrival_id` = pnam.`new_arrival_id`
				WHERE pnam.`product_id` = %s""")
			get_new_arrival_data = (data['product_id'])
			rows_count_new_arrival = cursor.execute(get_new_arrival_query,get_new_arrival_data)

			if rows_count_new_arrival >0:
				product_new_arrival_iamge = cursor.fetchone()
				product_data[key]['new_arrival_id'] = product_new_arrival_iamge['new_arrival_id']
				product_data[key]['new_arrival_image'] = product_new_arrival_iamge['new_arrival_image']
			else:
				product_data[key]['new_arrival_id'] = ""
				product_data[key]['new_arrival_image'] = ""


			get_brand_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_brand_mapping` pbm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pbm.`brand_id`
				WHERE pbm.`product_id` = %s""")
			get_brand_data = (data['product_id'])
			rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

			if rows_count_brand >0:
				product_brand = cursor.fetchone()
				product_data[key]['brand_id'] = product_brand['meta_key_value_id']
				product_data[key]['brand'] = product_brand['meta_key_value']
			else:
				product_data[key]['brand_id'] = ""
				product_data[key]['brand'] = ""

			get_category_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_category_mapping` pcm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pcm.`category_id`
				WHERE pcm.`product_id` = %s""")
			get_category_data = (data['product_id'])
			rows_count_category = cursor.execute(get_category_query,get_category_data)

			if rows_count_category >0:
				product_category = cursor.fetchone()
				product_data[key]['category_id'] = product_category['meta_key_value_id']
				product_data[key]['category'] = product_category['meta_key_value']
			else:
				product_data[key]['category_id'] = ""
				product_data[key]['category'] = ""


		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Product-List---------------------#
@name_space.route("/productListWithBrand/<int:organisation_id>/<int:category_id>/<int:brand_id>")	
class productListWithBrand(Resource):
	def get(self,organisation_id,category_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		if category_id == 0:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id`
				FROM `product_brand_mapping` pbm
				INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
				INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
				WHERE  pbm.`organisation_id` = %s and pbm.`brand_id` = %s""")
			get_data = (organisation_id,brand_id)			
		else:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id`
				FROM `product_brand_mapping` pbm
				INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
				INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`			
				WHERE  pbm.`organisation_id` = %s and p.`category_id` = %s  and pbm.`brand_id` = %s""")
			get_data = (organisation_id,category_id,brand_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_offer_query = 	 ("""SELECT o.`offer_image`,o.`offer_id`
				FROM `product_offer_mapping` pom
				INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`
				WHERE pom.`product_id` = %s and pom.`organisation_id` = %s""")
			get_offer_data = (data['product_id'],organisation_id)
			rows_count_offer = cursor.execute(get_offer_query,get_offer_data)

			if rows_count_offer >0:
				product_offer_iamge = cursor.fetchone()
				product_data[key]['offer_id'] = product_offer_iamge['offer_id']				
				product_data[key]['offer_image'] = product_offer_iamge['offer_image']
			else:
				product_data[key]['offer_id'] = ""
				product_data[key]['offer_image'] = ""

			get_new_arrival_query = 	 ("""SELECT n.`new_arrival_image`,n.`new_arrival_id`
				FROM `product_new_arrival_mapping` pnam
				INNER JOIN `new_arrival` n ON n.`new_arrival_id` = pnam.`new_arrival_id`
				WHERE pnam.`product_id` = %s""")
			get_new_arrival_data = (data['product_id'])
			rows_count_new_arrival = cursor.execute(get_new_arrival_query,get_new_arrival_data)

			if rows_count_new_arrival >0:
				product_new_arrival_iamge = cursor.fetchone()
				product_data[key]['new_arrival_id'] = product_new_arrival_iamge['new_arrival_id']
				product_data[key]['new_arrival_image'] = product_new_arrival_iamge['new_arrival_image']
			else:
				product_data[key]['new_arrival_id'] = ""
				product_data[key]['new_arrival_image'] = ""


			get_brand_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_brand_mapping` pbm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pbm.`brand_id`
				WHERE pbm.`product_id` = %s and pbm.`organisation_id` = %s""")
			get_brand_data = (data['product_id'],organisation_id)
			rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

			if rows_count_brand >0:
				product_brand = cursor.fetchone()
				product_data[key]['brand_id'] = product_brand['meta_key_value_id']
				product_data[key]['brand'] = product_brand['meta_key_value']
			else:
				product_data[key]['brand_id'] = ""
				product_data[key]['brand'] = ""

			get_category_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_category_mapping` pcm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pcm.`category_id`
				WHERE pcm.`product_id` = %s""")
			get_category_data = (data['product_id'])
			rows_count_category = cursor.execute(get_category_query,get_category_data)

			if rows_count_category >0:
				product_category = cursor.fetchone()
				product_data[key]['category_id'] = product_category['meta_key_value_id']
				product_data[key]['category'] = product_category['meta_key_value']
			else:
				product_data[key]['category_id'] = ""
				product_data[key]['category'] = ""


		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Product-List---------------------#
@name_space.route("/productListWithBrandWithProductId/<int:organisation_id>/<int:category_id>/<int:brand_id>/<int:product_id>")	
class productListWithBrandWithProductId(Resource):
	def get(self,organisation_id,category_id,brand_id,product_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		if category_id == 0:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id`
				FROM `product_brand_mapping` pbm
				INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
				INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
				WHERE  pbm.`organisation_id` = %s and pbm.`brand_id` = %s and pbm.`product_id` = %s""")
			get_data = (organisation_id,brand_id,product_id)			
		else:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id`
				FROM `product_brand_mapping` pbm
				INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
				INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`			
				WHERE  pbm.`organisation_id` = %s and p.`category_id` = %s  and pbm.`brand_id` = %s and pbm.`product_id` = %s""")
			get_data = (organisation_id,category_id,brand_id,product_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_offer_query = 	 ("""SELECT o.`offer_image`,o.`offer_id`
				FROM `product_offer_mapping` pom
				INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`
				WHERE pom.`product_id` = %s and pom.`organisation_id` = %s""")
			get_offer_data = (data['product_id'],organisation_id)
			rows_count_offer = cursor.execute(get_offer_query,get_offer_data)

			if rows_count_offer >0:
				product_offer_iamge = cursor.fetchone()
				product_data[key]['offer_id'] = product_offer_iamge['offer_id']				
				product_data[key]['offer_image'] = product_offer_iamge['offer_image']
			else:
				product_data[key]['offer_id'] = ""
				product_data[key]['offer_image'] = ""
			


			get_brand_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_brand_mapping` pbm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pbm.`brand_id`
				WHERE pbm.`product_id` = %s and pbm.`organisation_id` = %s""")
			get_brand_data = (data['product_id'],organisation_id)
			rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

			if rows_count_brand >0:
				product_brand = cursor.fetchone()
				product_data[key]['brand_id'] = product_brand['meta_key_value_id']
				product_data[key]['brand'] = product_brand['meta_key_value']
			else:
				product_data[key]['brand_id'] = ""
				product_data[key]['brand'] = ""

			get_category_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_category_mapping` pcm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pcm.`category_id`
				WHERE pcm.`product_id` = %s""")
			get_category_data = (data['product_id'])
			rows_count_category = cursor.execute(get_category_query,get_category_data)

			if rows_count_category >0:
				product_category = cursor.fetchone()
				product_data[key]['category_id'] = product_category['meta_key_value_id']
				product_data[key]['category'] = product_category['meta_key_value']
			else:
				product_data[key]['category_id'] = ""
				product_data[key]['category'] = ""


		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Product-List-With-Out-Brand---------------------#
@name_space.route("/productListWithOutBrand/<int:organisation_id>/<int:category_id>")	
class productListWithOutBrand(Resource):
	def get(self,organisation_id,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		get_query = ("""SELECT  p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id` 
			FROM `product` p 
			INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
			WHERE product_id not in 
			(select product_id from product_brand_mapping where organisation_id = %s) and 
			p.`organisation_id` = %s and category_id = %s""")
		get_data = (organisation_id,organisation_id,category_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_offer_query = 	 ("""SELECT o.`offer_image`,o.`offer_id`
				FROM `product_offer_mapping` pom
				INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`
				WHERE pom.`product_id` = %s""")
			get_offer_data = (data['product_id'])
			rows_count_offer = cursor.execute(get_offer_query,get_offer_data)

			if rows_count_offer >0:
				product_offer_iamge = cursor.fetchone()
				product_data[key]['offer_id'] = product_offer_iamge['offer_id']				
				product_data[key]['offer_image'] = product_offer_iamge['offer_image']
			else:
				product_data[key]['offer_id'] = ""
				product_data[key]['offer_image'] = ""

			get_new_arrival_query = 	 ("""SELECT n.`new_arrival_image`,n.`new_arrival_id`
				FROM `product_new_arrival_mapping` pnam
				INNER JOIN `new_arrival` n ON n.`new_arrival_id` = pnam.`new_arrival_id`
				WHERE pnam.`product_id` = %s""")
			get_new_arrival_data = (data['product_id'])
			rows_count_new_arrival = cursor.execute(get_new_arrival_query,get_new_arrival_data)

			if rows_count_new_arrival >0:
				product_new_arrival_iamge = cursor.fetchone()
				product_data[key]['new_arrival_id'] = product_new_arrival_iamge['new_arrival_id']
				product_data[key]['new_arrival_image'] = product_new_arrival_iamge['new_arrival_image']
			else:
				product_data[key]['new_arrival_id'] = ""
				product_data[key]['new_arrival_image'] = ""


			get_brand_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_brand_mapping` pbm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pbm.`brand_id`
				WHERE pbm.`product_id` = %s and pbm.`organisation_id` = %s""")
			get_brand_data = (data['product_id'],organisation_id)
			rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

			if rows_count_brand >0:
				product_brand = cursor.fetchone()
				product_data[key]['brand_id'] = product_brand['meta_key_value_id']
				product_data[key]['brand'] = product_brand['meta_key_value']
			else:
				product_data[key]['brand_id'] = ""
				product_data[key]['brand'] = ""

			get_category_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_category_mapping` pcm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pcm.`category_id`
				WHERE pcm.`product_id` = %s""")
			get_category_data = (data['product_id'])
			rows_count_category = cursor.execute(get_category_query,get_category_data)

			if rows_count_category >0:
				product_category = cursor.fetchone()
				product_data[key]['category_id'] = product_category['meta_key_value_id']
				product_data[key]['category'] = product_category['meta_key_value']
			else:
				product_data[key]['category_id'] = ""
				product_data[key]['category'] = ""


		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List-With-Out-Brand---------------------#

#----------------------Product-List-With-Out-Brand---------------------#
@name_space.route("/productListWithOutBrandProductId/<int:organisation_id>/<int:category_id>/<int:product_id>")	
class productListWithOutBrandProductId(Resource):
	def get(self,organisation_id,category_id,product_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		get_query = ("""SELECT  p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id` 
			FROM `product` p 
			INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
			WHERE product_id not in 
			(select product_id from product_brand_mapping where organisation_id = %s) and 
			p.`organisation_id` = %s and category_id = %s and p.`product_id` = %s""")
		get_data = (organisation_id,organisation_id,category_id,product_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_offer_query = 	 ("""SELECT o.`offer_image`,o.`offer_id`
				FROM `product_offer_mapping` pom
				INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`
				WHERE pom.`product_id` = %s""")
			get_offer_data = (data['product_id'])
			rows_count_offer = cursor.execute(get_offer_query,get_offer_data)

			if rows_count_offer >0:
				product_offer_iamge = cursor.fetchone()
				product_data[key]['offer_id'] = product_offer_iamge['offer_id']				
				product_data[key]['offer_image'] = product_offer_iamge['offer_image']
			else:
				product_data[key]['offer_id'] = ""
				product_data[key]['offer_image'] = ""			


			get_brand_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_brand_mapping` pbm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pbm.`brand_id`
				WHERE pbm.`product_id` = %s and pbm.`organisation_id` = %s""")
			get_brand_data = (data['product_id'],organisation_id)
			rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

			if rows_count_brand >0:
				product_brand = cursor.fetchone()
				product_data[key]['brand_id'] = product_brand['meta_key_value_id']
				product_data[key]['brand'] = product_brand['meta_key_value']
			else:
				product_data[key]['brand_id'] = ""
				product_data[key]['brand'] = ""

			get_category_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_category_mapping` pcm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pcm.`category_id`
				WHERE pcm.`product_id` = %s""")
			get_category_data = (data['product_id'])
			rows_count_category = cursor.execute(get_category_query,get_category_data)

			if rows_count_category >0:
				product_category = cursor.fetchone()
				product_data[key]['category_id'] = product_category['meta_key_value_id']
				product_data[key]['category'] = product_category['meta_key_value']
			else:
				product_data[key]['category_id'] = ""
				product_data[key]['category'] = ""


		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List-With-Out-Brand---------------------#

#----------------------Product-List-With-Out-Brand---------------------#
@name_space.route("/productListWithOutBrandFromProductOrganisationMapping/<int:organisation_id>/<int:category_id>")	
class productListWithOutBrandFromProductOrganisationMapping(Resource):
	def get(self,organisation_id,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()		
		get_query = ("""SELECT  p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id` 
			FROM `product` p 
			INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
			INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
			WHERE p.`product_id` not in 
			(select product_id from product_brand_mapping where organisation_id = %s) and 
			pom.`organisation_id` = %s and p.`category_id` = %s""")
		get_data = (organisation_id,organisation_id,category_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_offer_query = 	 ("""SELECT o.`offer_image`,o.`offer_id`
				FROM `product_offer_mapping` pom
				INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`
				WHERE pom.`product_id` = %s and pom.`organisation_id` = %s""")
			get_offer_data = (data['product_id'],organisation_id)
			rows_count_offer = cursor.execute(get_offer_query,get_offer_data)

			if rows_count_offer >0:
				product_offer_iamge = cursor.fetchone()
				product_data[key]['offer_id'] = product_offer_iamge['offer_id']				
				product_data[key]['offer_image'] = product_offer_iamge['offer_image']
			else:
				product_data[key]['offer_id'] = ""
				product_data[key]['offer_image'] = ""

			get_new_arrival_query = 	 ("""SELECT n.`new_arrival_image`,n.`new_arrival_id`
				FROM `product_new_arrival_mapping` pnam
				INNER JOIN `new_arrival` n ON n.`new_arrival_id` = pnam.`new_arrival_id`
				WHERE pnam.`product_id` = %s""")
			get_new_arrival_data = (data['product_id'])
			rows_count_new_arrival = cursor.execute(get_new_arrival_query,get_new_arrival_data)

			if rows_count_new_arrival >0:
				product_new_arrival_iamge = cursor.fetchone()
				product_data[key]['new_arrival_id'] = product_new_arrival_iamge['new_arrival_id']
				product_data[key]['new_arrival_image'] = product_new_arrival_iamge['new_arrival_image']
			else:
				product_data[key]['new_arrival_id'] = ""
				product_data[key]['new_arrival_image'] = ""


			get_brand_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_brand_mapping` pbm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pbm.`brand_id`
				WHERE pbm.`product_id` = %s and pbm.`organisation_id` = %s""")
			get_brand_data = (data['product_id'],organisation_id)
			rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

			if rows_count_brand >0:
				product_brand = cursor.fetchone()
				product_data[key]['brand_id'] = product_brand['meta_key_value_id']
				product_data[key]['brand'] = product_brand['meta_key_value']
			else:
				product_data[key]['brand_id'] = ""
				product_data[key]['brand'] = ""

			get_category_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_category_mapping` pcm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pcm.`category_id`
				WHERE pcm.`product_id` = %s""")
			get_category_data = (data['product_id'])
			rows_count_category = cursor.execute(get_category_query,get_category_data)

			if rows_count_category >0:
				product_category = cursor.fetchone()
				product_data[key]['category_id'] = product_category['meta_key_value_id']
				product_data[key]['category'] = product_category['meta_key_value']
			else:
				product_data[key]['category_id'] = ""
				product_data[key]['category'] = ""


		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List-With-Out-Brand---------------------#

#----------------------Product-List---------------------#
@name_space.route("/productListFromProductOrganisationMapping/<int:organisation_id>/<int:category_id>")	
class productListFromProductOrganisationMapping(Resource):
	def get(self,organisation_id,category_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		if category_id == 0:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id`
				FROM `product` p
				INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
				INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
				WHERE  pom.`organisation_id` = %s""")
			get_data = (organisation_id)			
		else:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`status`,p.`category_id` as `product_type_id`
				FROM `product` p
				INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
				WHERE  pom.`organisation_id` = %s and p.`category_id` = %s""")
			get_data = (organisation_id,category_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_offer_query = 	 ("""SELECT o.`offer_image`,o.`offer_id`
				FROM `product_offer_mapping` pom
				INNER JOIN `offer` o ON o.`offer_id` = pom.`offer_id`
				WHERE pom.`product_id` = %s and pom.`organisation_id` = %s """)
			get_offer_data = (data['product_id'],organisation_id)
			rows_count_offer = cursor.execute(get_offer_query,get_offer_data)

			if rows_count_offer >0:
				product_offer_iamge = cursor.fetchone()
				product_data[key]['offer_id'] = product_offer_iamge['offer_id']				
				product_data[key]['offer_image'] = product_offer_iamge['offer_image']
			else:
				product_data[key]['offer_id'] = ""
				product_data[key]['offer_image'] = ""

			get_new_arrival_query = 	 ("""SELECT n.`new_arrival_image`,n.`new_arrival_id`
				FROM `product_new_arrival_mapping` pnam
				INNER JOIN `new_arrival` n ON n.`new_arrival_id` = pnam.`new_arrival_id`
				WHERE pnam.`product_id` = %s and pnam.`organisation_id` = %s""")
			get_new_arrival_data = (data['product_id'],organisation_id)
			rows_count_new_arrival = cursor.execute(get_new_arrival_query,get_new_arrival_data)

			if rows_count_new_arrival >0:
				product_new_arrival_iamge = cursor.fetchone()
				product_data[key]['new_arrival_id'] = product_new_arrival_iamge['new_arrival_id']
				product_data[key]['new_arrival_image'] = product_new_arrival_iamge['new_arrival_image']
			else:
				product_data[key]['new_arrival_id'] = ""
				product_data[key]['new_arrival_image'] = ""


			get_brand_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_brand_mapping` pbm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pbm.`brand_id`
				WHERE pbm.`product_id` = %s and pbm.`organisation_id` = %s""")
			get_brand_data = (data['product_id'],organisation_id)
			rows_count_brand = cursor.execute(get_brand_query,get_brand_data)

			if rows_count_brand >0:
				product_brand = cursor.fetchone()
				product_data[key]['brand_id'] = product_brand['meta_key_value_id']
				product_data[key]['brand'] = product_brand['meta_key_value']
			else:
				product_data[key]['brand_id'] = ""
				product_data[key]['brand'] = ""

			get_category_query = 	 ("""SELECT mkm.`meta_key_value_id`,mkm.`meta_key_value`
				FROM `product_category_mapping` pcm
				INNER JOIN `meta_key_value_master` mkm ON mkm.`meta_key_value_id` = pcm.`category_id`
				WHERE pcm.`product_id` = %s and pcm.`organisation_id` = %s """)
			get_category_data = (data['product_id'],organisation_id)
			rows_count_category = cursor.execute(get_category_query,get_category_data)

			if rows_count_category >0:
				product_category = cursor.fetchone()
				product_data[key]['category_id'] = product_category['meta_key_value_id']
				product_data[key]['category'] = product_category['meta_key_value']
			else:
				product_data[key]['category_id'] = ""
				product_data[key]['category'] = ""


		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Update-Catalog---------------------#

@name_space.route("/UpdateCatalog/<int:catalog_id>")
class UpdateCatelog(Resource):
	@api.expect(catalog_putmodel)
	def put(self,catalog_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "catalog_name" in details:
			catalog_name = details['catalog_name']
			update_query = ("""UPDATE `catalogs` SET `catalog_name` = %s
				WHERE `catalog_id` = %s """)
			update_data = (catalog_name,catalog_id)
			cursor.execute(update_query,update_data)	

		if details and "sequence" in details:
			sequence = details['sequence']
			update_query = ("""UPDATE `catalogs` SET `sequence` = %s
				WHERE `catalog_id` = %s """)
			update_data = (sequence,catalog_id)
			cursor.execute(update_query,update_data)	

		if details and "catalog_status" in details:
			catalog_status = details['catalog_status']
			update_query = ("""UPDATE `catalogs` SET `status` = %s
				WHERE `catalog_id` = %s """)
			update_data = (catalog_status,catalog_id)
			cursor.execute(update_query,update_data)


		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		createPdfeUrl = BASE_URL + "ecommerce_product_admin/EcommerceProductAdmin/createCatalougePdf"
		payloadData = {
							"catalog_id":catalog_id,
													
					  }

		createPdf = requests.post(createPdfeUrl,data=json.dumps(payloadData), headers=headers).json()

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update_catalog_Informatiom",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Catalog---------------------#

#----------------------Product-Details---------------------#
@name_space.route("/productDetails/<int:product_id>/<int:organisation_id>")	
class productDetails(Resource):
	def get(self,product_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,p.`product_type`,
			p.`category_id`
			FROM `product` p			
			WHERE p.`product_id` = %s and p.`organisation_id` = %s""")
		getdata = (product_id,organisation_id)
		cursor.execute(get_query,getdata)
		product_data = cursor.fetchone()

		get_product_brand_query = (""" SELECT pbm.`brand_id`
			FROM `product_brand_mapping` pbm
			WHERE  pbm.`organisation_id` = %s and pbm.`product_id` = %s""")
		get_product_brand_data = (organisation_id,product_id)
		count_product_brand_data = cursor.execute(get_product_brand_query,get_product_brand_data)

		if count_product_brand_data > 0:
			product_brand_data = cursor.fetchone()
			product_data['brand_id'] = product_brand_data['brand_id']
		else:
			product_data['brand_id'] = 0

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-Details-From-Product-Organisation-Mapping---------------------#
@name_space.route("/productDetailsFromProductOrganisationMapping/<int:product_id>/<int:organisation_id>")	
class productDetailsFromProductOrganisationMapping(Resource):
	def get(self,product_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_long_description`,p.`product_short_description`,
			p.`category_id`
			FROM `product` p
			INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
			WHERE p.`product_id` = %s and pom.`organisation_id` = %s""")
		getdata = (product_id,organisation_id)
		cursor.execute(get_query,getdata)
		product_data = cursor.fetchone()

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-Details-From-Product-Organisation-Mapping---------------------#

#----------------------Update-Product-Information---------------------#

@name_space.route("/UpdateProductInformation/<int:product_id>")
class UpdateProductInformation(Resource):
	@api.expect(product_putmodel)
	def put(self,product_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "product_name" in details:
			product_name = details['product_name']
			update_query = ("""UPDATE `product` SET `product_name` = %s
				WHERE `product_id` = %s """)
			update_data = (product_name,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_long_description" in details:
			product_long_description = details['product_long_description']
			update_query = ("""UPDATE `product` SET `product_long_description` = %s
				WHERE `product_id` = %s """)
			update_data = (product_long_description,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_short_description" in details:
			product_short_description = details['product_short_description']
			update_query = ("""UPDATE `product` SET `product_short_description` = %s
				WHERE `product_id` = %s """)
			update_data = (product_short_description,product_id)
			cursor.execute(update_query,update_data)

		if details and "category_id" in details:
			category_id = details['category_id']
			update_query = ("""UPDATE `product` SET `category_id` = %s
				WHERE `product_id` = %s """)
			update_data = (category_id,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_type" in details:
			product_type = details['product_type']
			update_query = ("""UPDATE `product` SET `product_type` = %s
				WHERE `product_id` = %s """)
			update_data = (product_type,product_id)
			cursor.execute(update_query,update_data)

		if details and "organisation_id" in details:
			organisation_id = details['organisation_id']
			update_query = ("""UPDATE `product` SET `organisation_id` = %s
				WHERE `product_id` = %s """)
			update_data = (organisation_id,product_id)
			cursor.execute(update_query,update_data)

		if details and "last_update_id" in details:
			last_update_id = details['last_update_id']
			update_query = ("""UPDATE `product` SET `last_update_id` = %s
				WHERE `product_id` = %s """)
			update_data = (last_update_id,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_status" in details:
			product_status = details['product_status']
			update_query = ("""UPDATE `product` SET `status` = %s
				WHERE `product_id` = %s """)
			update_data = (product_status,product_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update_Product_Informatiom",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Product-Information---------------------#

#----------------------Update-Product-Status---------------------#

@name_space.route("/UpdateProductStatus/<int:product_id>/<int:organisation_id>")
class UpdateProductStatus(Resource):
	@api.expect(product_status_putmodel)
	def put(self,product_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "product_status" in details:
			product_status = details['product_status']
			update_query = ("""UPDATE `product_organisation_mapping` SET `product_status` = %s
				WHERE `product_id` = %s and `organisation_id` = %s""")
			update_data = (product_status,product_id,organisation_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update_Product_Informatiom",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Product-Status---------------------#

#----------------------Update-Product-Information-With-employee---------------------#

@name_space.route("/UpdateProductInformationWithEmployee/<int:product_id>/<int:employee_id>/<int:organisation_id>/<string:last_updated_ip_address>")
class UpdateProductInformationWithEmployee(Resource):
	@api.expect(product_putmodel)
	def put(self,product_id,employee_id,organisation_id,last_updated_ip_address):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		get_product_query = ("""SELECT *
						FROM `product` WHERE `product_id` = %s""")
		get_product_data = (product_id)		
		cursor.execute(get_product_query,get_product_data)

		product_data = cursor.fetchone()	

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
		payloadData = {
							"product_id":product_data['product_id'],
							"product_name":product_data['product_name'],
							"product_long_description":product_data['product_long_description'],
							"product_short_description":product_data['product_short_description'],
							"category_id":product_data['category_id'],
							"product_status":product_data['status'],
							"comments": "Update Product Information",							
							"employee_id":employee_id,
							"organisation_id":organisation_id,
							"last_updated_ip_address":last_updated_ip_address
					   }
		#print(payloadData)

		requests.post(url,data=json.dumps(payloadData), headers=headers).json()

		if details and "product_name" in details:
			product_name = details['product_name']
			update_query = ("""UPDATE `product` SET `product_name` = %s
				WHERE `product_id` = %s """)
			update_data = (product_name,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_long_description" in details:
			product_long_description = details['product_long_description']
			update_query = ("""UPDATE `product` SET `product_long_description` = %s
				WHERE `product_id` = %s """)
			update_data = (product_long_description,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_short_description" in details:
			product_short_description = details['product_short_description']
			update_query = ("""UPDATE `product` SET `product_short_description` = %s
				WHERE `product_id` = %s """)
			update_data = (product_short_description,product_id)
			cursor.execute(update_query,update_data)

		if details and "category_id" in details:
			category_id = details['category_id']
			update_query = ("""UPDATE `product` SET `category_id` = %s
				WHERE `product_id` = %s """)
			update_data = (category_id,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_type" in details:
			product_type = details['product_type']
			update_query = ("""UPDATE `product` SET `product_type` = %s
				WHERE `product_id` = %s """)
			update_data = (product_type,product_id)
			cursor.execute(update_query,update_data)

		if details and "organisation_id" in details:
			organisation_id = details['organisation_id']
			update_query = ("""UPDATE `product` SET `organisation_id` = %s
				WHERE `product_id` = %s """)
			update_data = (organisation_id,product_id)
			cursor.execute(update_query,update_data)

		if details and "last_update_id" in details:
			last_update_id = details['last_update_id']
			update_query = ("""UPDATE `product` SET `last_update_id` = %s
				WHERE `product_id` = %s """)
			update_data = (last_update_id,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_status" in details:
			product_status = details['product_status']
			update_query = ("""UPDATE `product` SET `status` = %s
				WHERE `product_id` = %s """)
			update_data = (product_status,product_id)
			cursor.execute(update_query,update_data)

		if details and "brand_id" in details:
			brand_id = details['brand_id']
			print(brand_id)

			get_query = ("""SELECT *
			FROM `product_brand_mapping` where `product_id` = %s and `organisation_id` = %s""")
			get_data = (product_id,organisation_id)

			count_product_brand = cursor.execute(get_query,get_data)

			if count_product_brand > 0:
				product_brand_data = cursor.fetchone()		
				print(product_brand_data)		

				update_query = ("""UPDATE `product_brand_mapping` SET `brand_id` = %s
				WHERE `product_id` = %s and `organisation_id` = %s""")
				update_data = (brand_id,product_id,organisation_id)
				cursor.execute(update_query,update_data)

			else:
				product_brnad_sttatus = 1
				insert_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (brand_id,product_id,product_brnad_sttatus,organisation_id,organisation_id)
				cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update_Product_Informatiom",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Product-Information---------------------#

#----------------------Product-meta-List---------------------#

@name_space.route("/productMetaList/<int:product_id>/<int:organisation_id>")	
class productMetaList(Resource):
	def get(self,product_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_long_description`,
			pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,pm.`loyalty_points`
			FROM `product` p
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			WHERE  p.`product_id` = %s and p.`organisation_id` = %s""")
		get_data = (product_id,organisation_id)
		cursor.execute(get_query,get_data)

		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):

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

				product_data[key]['met_key_value'] = met_key

			image_a = []	
			get_query_images = ("""SELECT `image`
						FROM `product_meta_images` WHERE `product_meta_id` = %s """)
			getdata_images = (data['product_meta_id'])
			cursor.execute(get_query_images,getdata_images)
			images = cursor.fetchall()

			for image in images:
				image_a.append(image['image'])

			product_data[key]['images'] = image_a


			get_latest_product_query = ("""SELECT `product_meta_id`
			FROM `latest_product_mapping` WHERE  `product_meta_id` = %s""")

			getLatesProductData = (data['product_meta_id'])
		
			count_latest_product = cursor.execute(get_latest_product_query,getLatesProductData)

			if count_latest_product > 0:
				product_data[key]['latest_product'] = 1
			else:
				product_data[key]['latest_product'] = 0


			get_top_selling_product_query = ("""SELECT `product_meta_id`
			FROM `product_top_selling_mapping` WHERE  `product_meta_id` = %s""")

			getTopSellingData = (data['product_meta_id'])
		
			count_top_selling_product = cursor.execute(get_top_selling_product_query,getTopSellingData)

			if count_top_selling_product > 0:
				product_data[key]['top_selling_product'] = 1
			else:
				product_data[key]['top_selling_product'] = 0


			get_best_selling_product_query = ("""SELECT `product_meta_id`
			FROM `product_best_selling_mapping` WHERE  `product_meta_id` = %s""")

			getBestSellingData = (data['product_meta_id'])
		
			count_best_selling_product = cursor.execute(get_best_selling_product_query,getBestSellingData)

			if count_best_selling_product > 0:
				product_data[key]['best_selling_product'] = 1
			else:
				product_data[key]['best_selling_product'] = 0

			get_product_meta_stock_query = ("""SELECT `product_meta_id`,`stock`
			FROM `product_inventory` WHERE  `product_meta_id` = %s""")
			getProductMetaStockData = (data['product_meta_id'])

			count_product_meta_stock = cursor.execute(get_product_meta_stock_query,getProductMetaStockData)

			if count_product_meta_stock >0:
				product_meta_stock = cursor.fetchone()
				product_data[key]['stock'] = product_meta_stock['stock']
			else:
				product_data[key]['stock'] = 0	

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
				product_data[key]['discount'] = 0
				product_data[key]['after_discounted_price'] = data['out_price']

			get_query_product_images = ("""SELECT count(*) as product_meta_images_count
						FROM `product_meta_images` WHERE `product_meta_id` = %s and `is_gallery` = 0""")
			get_product_data_images = (data['product_meta_id'])
			count_product_data_images = cursor.execute(get_query_product_images,get_product_data_images)

			if count_product_data_images > 0:
				product_meta_images_count = cursor.fetchone()
				product_data[key]['product_image_count'] = product_meta_images_count['product_meta_images_count']
			else:
				product_data[key]['product_image_count'] = 0


			get_query_product_gallery_images = ("""SELECT count(*) as product_meta_gallery_images_count
						FROM `product_meta_images` WHERE `product_meta_id` = %s and `is_gallery` = 1""")
			get_product_gallery_data_images = (data['product_meta_id'])
			count_product_gallery_data_images = cursor.execute(get_query_product_gallery_images,get_product_gallery_data_images)

			if count_product_gallery_data_images > 0:
				product_meta_gallery_images_count = cursor.fetchone()
				product_data[key]['product_gellery_image_count'] = product_meta_gallery_images_count['product_meta_gallery_images_count']
			else:
				product_data[key]['product_gellery_image_count'] = 0


		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-meta-List---------------------#

#----------------------Product-meta-List---------------------#

@name_space.route("/productMetaListFromProductOrganisationMapping/<int:product_id>/<int:organisation_id>")	
class productMetaListFromProductOrganisationMapping(Resource):
	def get(self,product_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_long_description`,
			pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,pm.`loyalty_points`
			FROM `product` p
			INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			WHERE p.`status` = 1 and p.`product_id` = %s and pom.`organisation_id` = %s""")
		get_data = (product_id,organisation_id)
		cursor.execute(get_query,get_data)

		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):

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

				product_data[key]['met_key_value'] = met_key

			image_a = []	
			get_query_images = ("""SELECT `image`
						FROM `product_meta_images` WHERE `product_meta_id` = %s """)
			getdata_images = (data['product_meta_id'])
			cursor.execute(get_query_images,getdata_images)
			images = cursor.fetchall()

			for image in images:
				image_a.append(image['image'])

			product_data[key]['images'] = image_a


			get_latest_product_query = ("""SELECT `product_meta_id`
			FROM `latest_product_mapping` WHERE  `product_meta_id` = %s and `organisation_id` = %s """)

			getLatesProductData = (data['product_meta_id'],organisation_id)
		
			count_latest_product = cursor.execute(get_latest_product_query,getLatesProductData)

			if count_latest_product > 0:
				product_data[key]['latest_product'] = 1
			else:
				product_data[key]['latest_product'] = 0


			get_top_selling_product_query = ("""SELECT `product_meta_id`
			FROM `product_top_selling_mapping` WHERE  `product_meta_id` = %s and `organisation_id` = %s""")

			getTopSellingData = (data['product_meta_id'],organisation_id)
		
			count_top_selling_product = cursor.execute(get_top_selling_product_query,getTopSellingData)

			if count_top_selling_product > 0:
				product_data[key]['top_selling_product'] = 1
			else:
				product_data[key]['top_selling_product'] = 0


			get_best_selling_product_query = ("""SELECT `product_meta_id`
			FROM `product_best_selling_mapping` WHERE  `product_meta_id` = %s and `organisation_id` = %s""")

			getBestSellingData = (data['product_meta_id'],organisation_id)
		
			count_best_selling_product = cursor.execute(get_best_selling_product_query,getBestSellingData)

			if count_best_selling_product > 0:
				product_data[key]['best_selling_product'] = 1
			else:
				product_data[key]['best_selling_product'] = 0

			get_product_meta_stock_query = ("""SELECT `product_meta_id`,`stock`
			FROM `product_inventory` WHERE  `product_meta_id` = %s""")
			getProductMetaStockData = (data['product_meta_id'])

			count_product_meta_stock = cursor.execute(get_product_meta_stock_query,getProductMetaStockData)

			if count_product_meta_stock >0:
				product_meta_stock = cursor.fetchone()
				product_data[key]['stock'] = product_meta_stock['stock']
			else:
				product_data[key]['stock'] = 0	

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
				product_data[key]['discount'] = 0
				product_data[key]['after_discounted_price'] = data['out_price']

		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-meta-List---------------------#

#----------------------Product-meta-Details---------------------#

@name_space.route("/getProductMetaDetails/<int:product_meta_id>/<int:organisation_id>")	
class getProductMetaDetails(Resource):
	def get(self,product_meta_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT pm.`product_id`,pm.`product_meta_id`,
			pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,p.`product_name`,pm.`loyalty_points`,pm.`other_specification_json`
			FROM `product_meta` pm 
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			WHERE  pm.`product_meta_id` = %s and pm.`organisation_id` = %s""")
		get_data = (product_meta_id,organisation_id)
		cursor.execute(get_query,get_data)

		product_meta_data = cursor.fetchone()

		if product_meta_data['other_specification_json'] == '0':
			product_meta_data['other_specification_json'] = {}
		else:
			other_specification_json_1 = json.loads(product_meta_data['other_specification_json'])
			product_meta_data['other_specification_json']= other_specification_json_1
		
		a_string = product_meta_data['meta_key_text']
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

			product_meta_data['met_key_value'] = met_key		

		
		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_meta_data}), status.HTTP_200_OK


#----------------------Product-meta-Details---------------------#

#----------------------Product-meta-Details-From-Product-Organisation-Mapping---------------------#

@name_space.route("/getProductMetaDetailsFromProductOrganisationMapping/<int:product_meta_id>/<int:organisation_id>")	
class getProductMetaDetailsFromProductOrganisationMapping(Resource):
	def get(self,product_meta_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT pm.`product_id`,pm.`product_meta_id`,
			pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,p.`product_name`,pm.`loyalty_points`
			FROM `product_meta` pm 
			INNER JOIN `product` p ON p.`product_id` = pm.`product_id`
			INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id`
			WHERE  pm.`product_meta_id` = %s and pom.`organisation_id` = %s""")
		get_data = (product_meta_id,organisation_id)
		cursor.execute(get_query,get_data)

		product_meta_data = cursor.fetchone()

		a_string = product_meta_data['meta_key_text']
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

			product_meta_data['met_key_value'] = met_key		

		
		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_meta_data}), status.HTTP_200_OK


#----------------------Product-meta-Details-From-Product-Organisation-Mapping---------------------#

#----------------------Delete-Product-meta---------------------#
@name_space.route("/deleteProductMeta/<int:product_meta_id>")	
class deleteProductMeta(Resource):
	def delete(self,product_meta_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_meta` WHERE `product_meta_id` = %s """)
		delData = (product_meta_id)
		
		cursor.execute(delete_query,delData)

		delete_images_query = ("""DELETE FROM `product_meta_images` WHERE `product_meta_id` = %s """)
		delImageData = (product_meta_id)
		
		cursor.execute(delete_images_query,delImageData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_product_meta",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Product-meta---------------------#

#----------------------Delete-Product-meta---------------------#
@name_space.route("/deleteProductMetaWithEmployee/<int:product_meta_id>/<int:employee_id>/<int:organisation_id>/<string:last_updated_ip_address>")	
class deleteProductMetaWithEmployee(Resource):
	def delete(self,product_meta_id,employee_id,organisation_id,last_updated_ip_address):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_product_meta_query = ("""SELECT *
						FROM `product_meta` WHERE `product_meta_id` = %s""")
		get_product_meta_data = (product_meta_id)		
		cursor.execute(get_product_meta_query,get_product_meta_data)

		product_meta_data = cursor.fetchone()	

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
		payloadData = {
							"product_id":product_meta_data['product_id'],
							"product_meta_id":product_meta_data['product_meta_id'],							
							"product_meta_code":product_meta_data['product_meta_code'],
							"meta_key_text":product_meta_data['meta_key_text'],
							"other_specification_json":product_meta_data['other_specification_json'],
							"in_price":product_meta_data['in_price'],
							"out_price":product_meta_data['out_price'],
							"loyalty_points":product_meta_data['loyalty_points'],
							"comments": "Delete Product Variant",							
							"employee_id":employee_id,
							"organisation_id":organisation_id,
							"last_updated_ip_address":last_updated_ip_address
						}

		requests.post(url,data=json.dumps(payloadData), headers=headers).json()		
		

		get_product_meta_images_query = ("""SELECT *
						FROM `product_meta_images` WHERE `product_meta_id` = %s""")
		get_product_meta_images_data = (product_meta_id)

		cursor.execute(get_product_meta_images_query,get_product_meta_images_data)
		product_meta_images_data = cursor.fetchall()

		for key,data in enumerate(product_meta_images_data):

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
			payloadData = {
								"product_id":product_meta_data['product_id'],
								"product_meta_id":product_meta_data['product_meta_id'],
								"product_meta_image_id":data['product_image_id'],
								"deleted_image_link":data['image'],
								"default_image_flag":data['default_image_flag'],
								"is_gallery":data['is_gallery'],
								"comments": "Delete Image while Product Variant Deleted",							
								"employee_id":employee_id,
								"organisation_id":organisation_id,
								"last_updated_ip_address":last_updated_ip_address
							}

			requests.post(url,data=json.dumps(payloadData), headers=headers).json()


		delete_query = ("""DELETE FROM `product_meta` WHERE `product_meta_id` = %s """)
		delData = (product_meta_id)
		
		cursor.execute(delete_query,delData)

		delete_images_query = ("""DELETE FROM `product_meta_images` WHERE `product_meta_id` = %s """)
		delImageData = (product_meta_id)
		
		cursor.execute(delete_images_query,delImageData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_product_meta",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Product-meta---------------------#

#----------------------Delete-Product-meta-Image---------------------#
@name_space.route("/deleteProductMetaImage/<int:product_image_id>")	
class deleteProductMetaImage(Resource):
	def delete(self,product_image_id,employee_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		delete_images_query = ("""DELETE FROM `product_meta_images` WHERE `product_image_id` = %s """)
		delImageData = (product_image_id)
		
		cursor.execute(delete_images_query,delImageData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_product_meta_image",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Product-meta---------------------#

#----------------------Delete-Product-meta-Image---------------------#
@name_space.route("/deleteProductMetaImageWithEmployee/<int:product_image_id>/<int:employee_id>/<int:organisation_id>/<string:last_updated_ip_address>")	
class deleteProductMetaImageWithEmployee(Resource):
	def delete(self,product_image_id,employee_id,organisation_id,last_updated_ip_address):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_product_meta_id_query = ("""SELECT `product_meta_id`,`image`,`default_image_flag`,`is_gallery`
						FROM `product_meta_images` WHERE  `product_image_id` = %s""")
		get_product_meta_id_data = (product_image_id)		
		cursor.execute(get_product_meta_id_query,get_product_meta_id_data)

		product_meta_data = cursor.fetchone()

		get_product_id_query = ("""SELECT `product_id`
						FROM `product_meta` WHERE  `product_meta_id` = %s""")
		get_product_id_data = (product_meta_data['product_meta_id'])
		cursor.execute(get_product_id_query,get_product_id_data)

		product_data = cursor.fetchone()

		if product_meta_data['is_gallery'] == 1:
			comments = "Delete Image From Gallery"
		else:
			if product_meta_data['default_image_flag'] == 1:
				comments = "Delete Default Image"
			else:
				comments = "Delete Image"


		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
		payloadData = {
							"product_id":product_data['product_id'],
							"product_meta_id":product_meta_data['product_meta_id'],
							"product_meta_image_id":product_image_id,
							"deleted_image_link":product_meta_data['image'],
							"default_image_flag":product_meta_data['default_image_flag'],
							"is_gallery":product_meta_data['is_gallery'],
							"comments": comments,							
							"employee_id":employee_id,
							"organisation_id":organisation_id,
							"last_updated_ip_address":last_updated_ip_address
						}

		requests.post(url,data=json.dumps(payloadData), headers=headers).json()

		delete_images_query = ("""DELETE FROM `product_meta_images` WHERE `product_image_id` = %s """)
		delImageData = (product_image_id)
		
		cursor.execute(delete_images_query,delImageData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_product_meta_image",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Product-meta---------------------#

#----------------------Product-List---------------------#
@name_space.route("/getProductList")	
class getProductList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_short_description`,
			pm.`product_meta_id`,pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`
			FROM `product` p
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			WHERE p.`status` = 1 """)

		cursor.execute(get_query)

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

				get_query_all_key_value = ("""SELECT `meta_key_id`,`meta_key_value`
								FROM `meta_key_value_master` WHERE `meta_key_id` = %s """)
				getdata_all_key_value = (met_key_value_data['meta_key_id'])
				cursor.execute(get_query_all_key_value,getdata_all_key_value)
				met_key_value_all_data = cursor.fetchall()

				#product_meta[key][met_key_data['meta_key']] = met_key_value_all_data
				met_key_value_all_data_new = []		

				for key_all,met_key_value_all_data_one in  enumerate(met_key_value_all_data):
					met_key_value_all_data_new.append(met_key_value_all_data_one['meta_key_value'])

				product_data[key][met_key_data['meta_key']] = met_key_value_all_data_new

				image_a = []	
				get_query_images = ("""SELECT `image`
									FROM `product_meta_images` WHERE `product_meta_id` = %s """)
				getdata_images = (data['product_meta_id'])
				cursor.execute(get_query_images,getdata_images)
				images = cursor.fetchall()

				for image in images:
					image_a.append(image['image'])

				product_data[key]['images'] = image_a

				
		return ({"attributes": {
		    		"status_desc": "product_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Product-List---------------------#

#----------------------Update-Product-Meta---------------------#
@name_space.route("/updateProductMeta/<int:product_meta_id>")
class updateProductMeta(Resource):
	@api.expect(product_meta_putmodel)
	def put(self, product_meta_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "in_price" in details:
			in_price = details['in_price']
			update_query = ("""UPDATE `product_meta` SET `in_price` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (in_price,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "out_price" in details:
			out_price = details['out_price']
			update_query = ("""UPDATE `product_meta` SET `out_price` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (out_price,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "product_meta_code" in details:
			product_meta_code = details['product_meta_code']
			update_query = ("""UPDATE `product_meta` SET `product_meta_code` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (product_meta_code,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "other_specification_json" in details:
			other_specification_json = details['other_specification_json']
			update_query = ("""UPDATE `product_meta` SET `other_specification_json` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (other_specification_json,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "loyalty_points" in details:
			loyalty_points = details['loyalty_points']
			update_query = ("""UPDATE `product_meta` SET `loyalty_points` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (loyalty_points,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "organisation_id" in details:
			organisation_id = details['organisation_id']
			update_query = ("""UPDATE `product_meta` SET `organisation_id` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (organisation_id,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "last_update_id" in details:
			last_update_id = details['last_update_id']
			update_query = ("""UPDATE `product_meta` SET `last_update_id` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (last_update_id,product_meta_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Product Meta",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Product-Meta---------------------#

#----------------------Update-Product-Meta-with-Employee---------------------#
@name_space.route("/updateProductMetaWithEmployee/<int:product_meta_id>/<int:employee_id>/<int:organisation_id>/<string:last_updated_ip_address>")
class updateProductMetaWithEmployee(Resource):
	@api.expect(product_meta_putmodel)
	def put(self, product_meta_id,employee_id,organisation_id,last_updated_ip_address):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		get_product_meta_query = ("""SELECT *
						FROM `product_meta` WHERE `product_meta_id` = %s""")
		get_product_meta_data = (product_meta_id)		
		cursor.execute(get_product_meta_query,get_product_meta_data)

		product_meta_data = cursor.fetchone()	

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
		payloadData = {
							"product_id":product_meta_data['product_id'],
							"product_meta_id":product_meta_data['product_meta_id'],							
							"product_meta_code":product_meta_data['product_meta_code'],
							"meta_key_text":product_meta_data['meta_key_text'],
							"other_specification_json":product_meta_data['other_specification_json'],
							"in_price":product_meta_data['in_price'],
							"out_price":product_meta_data['out_price'],
							"loyalty_points":product_meta_data['loyalty_points'],
							"comments": "Update Product Variant",							
							"employee_id":employee_id,
							"organisation_id":organisation_id,
							"last_updated_ip_address":last_updated_ip_address
						}

		requests.post(url,data=json.dumps(payloadData), headers=headers).json()	

		if details and "in_price" in details:
			in_price = details['in_price']
			update_query = ("""UPDATE `product_meta` SET `in_price` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (in_price,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "out_price" in details:
			out_price = details['out_price']
			update_query = ("""UPDATE `product_meta` SET `out_price` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (out_price,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "product_meta_code" in details:
			product_meta_code = details['product_meta_code']
			update_query = ("""UPDATE `product_meta` SET `product_meta_code` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (product_meta_code,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "other_specification_json" in details:
			other_specification_json = details['other_specification_json']
			update_query = ("""UPDATE `product_meta` SET `other_specification_json` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (other_specification_json,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "loyalty_points" in details:
			loyalty_points = details['loyalty_points']
			update_query = ("""UPDATE `product_meta` SET `loyalty_points` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (loyalty_points,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "organisation_id" in details:
			organisation_id = details['organisation_id']
			update_query = ("""UPDATE `product_meta` SET `organisation_id` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (organisation_id,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "last_update_id" in details:
			last_update_id = details['last_update_id']
			update_query = ("""UPDATE `product_meta` SET `last_update_id` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (last_update_id,product_meta_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Product Meta",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Product-Meta-with-Employee---------------------#


#----------------------Update-Product-With-Product-Meta-Image-Discount---------------------#
@name_space.route("/updateProductWithMetaImage/<int:product_id>/<int:product_meta_id>")
class updateProductWithMetaImage(Resource):
	@api.expect(product_meta_image_putmodel)
	def put(self, product_id, product_meta_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		organisation_id = details['organisation_id']
		last_update_id = organisation_id

		if details and "product_name" in details:
			product_name = details['product_name']
			update_query = ("""UPDATE `product` SET `product_name` = %s
				WHERE `product_id` = %s """)
			update_data = (product_name,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_long_description" in details:
			product_long_description = details['product_long_description']
			update_query = ("""UPDATE `product` SET `product_long_description` = %s
				WHERE `product_id` = %s """)
			update_data = (product_long_description,product_id)
			cursor.execute(update_query,update_data)

		if details and "product_short_description" in details:
			product_short_description = details['product_short_description']
			update_query = ("""UPDATE `product` SET `product_short_description` = %s
				WHERE `product_id` = %s """)
			update_data = (product_short_description,product_id)
			cursor.execute(update_query,update_data)		

		if details and "in_price" in details:
			in_price = details['in_price']
			update_query = ("""UPDATE `product_meta` SET `in_price` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (in_price,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "out_price" in details:
			out_price = details['out_price']
			update_query = ("""UPDATE `product_meta` SET `out_price` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (out_price,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "product_meta_code" in details:
			product_meta_code = details['product_meta_code']
			update_query = ("""UPDATE `product_meta` SET `product_meta_code` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (product_meta_code,product_meta_id)
			cursor.execute(update_query,update_data)

		if details and "image" in details:

			delete_image_query = ("""DELETE FROM `product_meta_images` WHERE `product_meta_id` = %s """)
			delImageData = (product_meta_id)		
			cursor.execute(delete_image_query,delImageData)

			images = details.get('image',[])

			for key,image in enumerate(images):
				if key == 0:
					default_image_flag = 1
				else:
					default_image_flag = 0

				product_meta_status_image = 1

				insert_query_image = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`status`,`organisation_id`,last_update_id) 
					VALUES(%s,%s,%s,%s,%s,%s)""")

				data = (product_meta_id,image,default_image_flag,product_meta_status_image,organisation_id,last_update_id)
				cursor.execute(insert_query_image,data)

		if details and "discount" in details:
			discount = details['discount']
			get_discount_master_query = (""" SELECT `discount_id`,`discount` FROM `discount_master` WHERE `discount`=%s and `organisation_id` = %s""")
			get_discount_master_data = (discount,organisation_id)
			count_discount_master = cursor.execute(get_discount_master_query,get_discount_master_data)

			if count_discount_master > 0: 
				discount_master_data = cursor.fetchone()
				discount_id = discount_master_data['discount_id']				
			else:
				discount_status = 1				
				insert_discount_master_query = (""" INSERT INTO `discount_master`(`discount`,`status`,`organisation_id`,`last_update_id`)
					VALUES(%s,%s,%s,%s)""")
				discount_master_data = (discount,discount_status,organisation_id,last_update_id)
				cursor.execute(insert_discount_master_query,discount_master_data)

				discount_id = cursor.lastrowid

			get_discount_query = ("""SELECT  `product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
					FROM `product_meta_discount_mapping` WHERE  `product_meta_id` = %s and `organisation_id` = %s""")

			get_discount_data = (product_meta_id,organisation_id)
			count_product_meta_discount = cursor.execute(get_discount_query,get_discount_data)

			if count_product_meta_discount > 0:

				update_query = ("""UPDATE `product_meta_discount_mapping` SET `discount_id` = %s
				WHERE `product_meta_id` = %s """)
				update_data = (discount_id,product_meta_id)
				cursor.execute(update_query,update_data)

			else:
				product_meta_discount_status = 1
				insert_query = ("""INSERT INTO `product_meta_discount_mapping`(`product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (product_meta_id,discount_id,product_meta_discount_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if details and "brand_id" in details:		
			brand_id = details['brand_id']

			get_query = ("""SELECT *
			FROM `product_brand_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_brand = cursor.execute(get_query,get_data)

			if count_product_brand > 0:
				product_brand_data = cursor.fetchone()
				details['product_brand_id'] = product_brand_data['mapping_id']

				update_query = ("""UPDATE `product_brand_mapping` SET `brand_id` = %s
				WHERE `product_id` = %s """)
				update_data = (brand_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
				product_brand_mapping_status = 1
				data = (brand_id,product_id,product_brand_mapping_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)


		if details and "category_id" in details:		
			category_id = details['category_id']

			get_query = ("""SELECT *
			FROM `product_category_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_category = cursor.execute(get_query,get_data)

			if count_product_category > 0:
				product_category_data = cursor.fetchone()
				details['product_category_id'] = product_category_data['mapping_id']

				update_query = ("""UPDATE `product_category_mapping` SET `category_id` = %s
				WHERE `product_id` = %s """)
				update_data = (category_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_category_mapping`(`category_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
				product_category_mapping_status = 1
				data = (category_id,product_id,product_category_mapping_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)


		top_selling = details['top_selling']		
		if top_selling == 1:

			get_query = ("""SELECT `product_meta_id`
			FROM `product_top_selling_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product == 0:			

				insert_query = ("""INSERT INTO `product_top_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

				top_selling_product_status = 1
				data = (product_meta_id,top_selling_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)
		elif top_selling == 0:

			delete_query = ("""DELETE FROM `product_top_selling_mapping` WHERE `product_meta_id` = %s """)
			delData = (product_meta_id)
		
			cursor.execute(delete_query,delData)


		best_selling = details['best_selling']		
		if best_selling == 1:

			get_query = ("""SELECT `product_meta_id`
			FROM `product_best_selling_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product == 0:

				best_selling_product_status = 1
				insert_query = ("""INSERT INTO `product_best_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

				data = (product_meta_id,best_selling_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		elif best_selling == 0:

			delete_query = ("""DELETE FROM `product_best_selling_mapping` WHERE `product_meta_id` = %s """)
			delData = (product_meta_id)
		
			cursor.execute(delete_query,delData)


		latest_product = details['latest_product']
		if latest_product == 1:	
			get_query = ("""SELECT `product_meta_id`
								FROM `latest_product_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product == 0:
			
				latest_product_status = 1
				insert_query = ("""INSERT INTO `latest_product_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s)""")

				data = (product_meta_id,latest_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)
		elif latest_product ==0:
			delete_query = ("""DELETE FROM `latest_product_mapping` WHERE `product_meta_id` = %s """)
			delData = (product_meta_id)
		
			cursor.execute(delete_query,delData)
		
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Product Meta WIth Images",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Product-With-Product-Meta-Image-Discount---------------------#

#----------------------Add-Product-Meta---------------------#

@name_space.route("/AddProductMeta")
class AddProductMeta(Resource):
	@api.expect(product_price_meta_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_id = details['product_id']
		product_meta_code = details['product_meta_code']
		meta_key_text = details['meta_key_text']
		in_price = details['in_price']
		out_price = details['out_price']
		product_meta_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		other_specification_json = 0

		if details and "employee_id" in details:
			employee_id = details['employee_id']
		else:
			employee_id = 0

		if details and "last_updated_ip_address" in details:
			last_updated_ip_address = details['last_updated_ip_address']
		else:
			last_updated_ip_address = ""

		insert_query = ("""INSERT INTO `product_meta`(`product_id`,`product_meta_code`,`meta_key_text`,`other_specification_json`,`in_price`,`out_price`,`status`,
			`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_id,product_meta_code,meta_key_text,other_specification_json,in_price,out_price,product_meta_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		product_meta_id = cursor.lastrowid

		details['product_meta_id'] = product_meta_id

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
		payloadData = {
							"product_id":product_id,
							"product_meta_id":product_meta_id,
							"comments": "Add Product Variant",
							"employee_id":employee_id,
							"organisation_id":organisation_id,
							"last_updated_ip_address":last_updated_ip_address
						}

		requests.post(url,data=json.dumps(payloadData), headers=headers).json()	

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_meta_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Add-Product-Meta---------------------#

#----------------------Add-Product-Meta-Inventory---------------------#

@name_space.route("/AddProductMetaInventory")
class AddProductMetaInventory(Resource):
	@api.expect(product_meta_inventory_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_meta_id = details['product_meta_id']
		stock = details['stock']
		product_meta_transaction_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_product_inventory_query = ("""SELECT `product_meta_id`,`stock`
			FROM `product_inventory` WHERE  `product_meta_id` = %s""")
		get_prodcut_inventory_Data = (product_meta_id)			
		count_product_inventory = cursor.execute(get_product_inventory_query,get_prodcut_inventory_Data)

		if count_product_inventory >0:
			course_update_query = ("""UPDATE `product_inventory` SET `stock` = %s
				WHERE `product_meta_id` = %s """)
			update_data = (stock,product_meta_id)
			cursor.execute(course_update_query,update_data)
		else:	
			insert_product_inventory_query = ("""INSERT INTO `product_inventory`(`product_meta_id`,`stock`,`status`,
				`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

			insert_product_inventory_data = (product_meta_id,stock,product_meta_transaction_status,organisation_id,last_update_id)
			cursor.execute(insert_product_inventory_query,insert_product_inventory_data)
			product_inventory_id = cursor.lastrowid

		get_product_transaction_query = ("""SELECT `product_meta_id`,`previous_stock`,`updated_stock`
			FROM `product_transaction` WHERE  `product_meta_id` = %s""")
		get_prodcut_transaction_Data = (product_meta_id)		
		count_product_transaction = cursor.execute(get_product_transaction_query,get_prodcut_transaction_Data)
		


		if count_product_transaction > 0:
			product_transaction = cursor.fetchone();
			insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,
			`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

			insert_product_transaction_data = (product_meta_id,product_transaction['updated_stock'],stock,product_meta_transaction_status,organisation_id,last_update_id)
			cursor.execute(insert_product_transaction_query,insert_product_transaction_data)	


		else:
			insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,
			`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")
			previous_stock = 0
			insert_product_transaction_data = (product_meta_id,previous_stock,stock,product_meta_transaction_status,organisation_id,last_update_id)
			cursor.execute(insert_product_transaction_query,insert_product_transaction_data)			


		return ({"attributes": {
			    	"status_desc": "product_meta_inventory_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Add-Product-Meta-Inventory---------------------#

#----------------------Add-Product-Images---------------------#

@name_space.route("/AddProductImages")
class AddProductImages(Resource):
	@api.expect(product_images_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_meta_id = details['product_meta_id']
		image = details['image']
		image_type = details['image_type']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		product_meta_status_image = 1

		if details and "employee_id" in details:
			employee_id = details['employee_id']
		else:
			employee_id = 0

		if details and "last_updated_ip_address" in details:
			last_updated_ip_address = details['last_updated_ip_address']
		else:
			last_updated_ip_address = ""

		
		insert_query_image = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`image_type`,`status`,`organisation_id`,last_update_id) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

		data = (product_meta_id,image,image_type,product_meta_status_image,organisation_id,last_update_id)
		cursor.execute(insert_query_image,data)
		product_meta_image_id = cursor.lastrowid

		get_product_id_query = ("""SELECT `product_id`
						FROM `product_meta` WHERE  `product_meta_id` = %s""")
		get_product_id_data = (product_meta_id)
		cursor.execute(get_product_id_query,get_product_id_data)

		product_data = cursor.fetchone()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
		payloadData = {
							"product_id":product_data['product_id'],
							"product_meta_id":product_meta_id,
							"product_meta_image_id":product_meta_image_id,
							"comments": "Add Product Variant Images",
							"employee_id":employee_id,
							"organisation_id":organisation_id,
							"last_updated_ip_address":last_updated_ip_address
						}

		requests.post(url,data=json.dumps(payloadData), headers=headers).json()

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_image_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Add-Product-Images---------------------#

#----------------------Add-Product-Images---------------------#

@name_space.route("/AddProductImagesGallery")
class AddProductImagesGallery(Resource):
	@api.expect(product_images_gallery_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_meta_id = details['product_meta_id']
		image = details['image']
		image_type = details['image_type']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		is_gallery = details['is_gallery']
		product_meta_status_image = 1

		if details and "employee_id" in details:
			employee_id = details['employee_id']
		else:
			employee_id = 0

		
		insert_query_image = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`is_gallery`,`image_type`,`status`,`organisation_id`,last_update_id) 
				VALUES(%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_meta_id,image,is_gallery,image_type,product_meta_status_image,organisation_id,last_update_id)
		cursor.execute(insert_query_image,data)
		product_meta_image_id = cursor.lastrowid

		get_product_id_query = ("""SELECT `product_id`
						FROM `product_meta` WHERE  `product_meta_id` = %s""")
		get_product_id_data = (product_meta_id)
		cursor.execute(get_product_id_query,get_product_id_data)

		product_data = cursor.fetchone()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
		payloadData = {
							"product_id":product_data['product_id'],
							"product_meta_id":product_meta_id,
							"product_meta_image_id":product_meta_image_id,
							"is_gallery":1,
							"comments": "Add Image Into Gallery",							
							"employee_id":employee_id,
							"organisation_id":organisation_id
						}

		requests.post(url,data=json.dumps(payloadData), headers=headers).json()

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_image_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Add-Product-Images---------------------#



#----------------------Add-Catalog-roduct-Meta---------------------#

@name_space.route("/AddCatalogProductMeta")
class AddCatalogProductMeta(Resource):
	@api.expect(product_meta_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_id = details['product_id']
		product_meta_code = details['product_meta_code']
		meta_key_text = details['meta_key_text']
		in_price = details['in_price']
		out_price = details['out_price']
		product_meta_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']
		images = details.get('image',[])
		discount = details['discount']
		top_selling = details['top_selling']
		best_selling = details['best_selling']
		latest_product = details['latest_product']

		insert_query = ("""INSERT INTO `product_meta`(`product_id`,`product_meta_code`,`meta_key_text`,`in_price`,`out_price`,`status`,
			`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_id,product_meta_code,meta_key_text,in_price,out_price,product_meta_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		product_meta_id = cursor.lastrowid

		

		for key,image in enumerate(images):
			if key == 0:
				default_image_flag = 1
			else:
				default_image_flag = 0

			product_meta_status_image = 1

			insert_query_image = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`status`,`organisation_id`,last_update_id) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

			data = (product_meta_id,image,default_image_flag,product_meta_status_image,organisation_id,last_update_id)
			cursor.execute(insert_query_image,data)


		if discount:
			get_discount_master_query = (""" SELECT `discount_id`,`discount` FROM `discount_master` WHERE `discount`=%s and `organisation_id` = %s""")
			get_discount_master_data = (discount,organisation_id)
			count_discount_master = cursor.execute(get_discount_master_query,get_discount_master_data)

			if count_discount_master > 0: 
				discount_master_data = cursor.fetchone()
				discount_id = discount_master_data['discount_id']				
			else:
				discount_status = 1				
				insert_discount_master_query = (""" INSERT INTO `discount_master`(`discount`,`status`,`organisation_id`,`last_update_id`)
					VALUES(%s,%s,%s,%s)""")
				discount_master_data = (discount,discount_status,organisation_id,last_update_id)
				cursor.execute(insert_discount_master_query,discount_master_data)

				discount_id = cursor.lastrowid

			get_discount_query = ("""SELECT  `product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
					FROM `product_meta_discount_mapping` WHERE  `product_meta_id` = %s and `organisation_id` = %s""")

			get_discount_data = (product_meta_id,organisation_id)
			count_product_meta_discount = cursor.execute(get_discount_query,get_discount_data)

			if count_product_meta_discount > 0:

				update_query = ("""UPDATE `product_meta_discount_mapping` SET `discount_id` = %s
				WHERE `product_meta_id` = %s """)
				update_data = (discount_id,product_meta_id)
				cursor.execute(update_query,update_data)

			else:
				product_meta_discount_status = 1
				insert_query = ("""INSERT INTO `product_meta_discount_mapping`(`product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (product_meta_id,discount_id,product_meta_discount_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if details and "brand_id" in details:		
			brand_id = details['brand_id']

			get_query = ("""SELECT *
			FROM `product_brand_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_brand = cursor.execute(get_query,get_data)

			if count_product_brand > 0:
				product_brand_data = cursor.fetchone()
				details['product_brand_id'] = product_brand_data['mapping_id']

				update_query = ("""UPDATE `product_brand_mapping` SET `brand_id` = %s
				WHERE `product_id` = %s """)
				update_data = (brand_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
				product_brand_mapping_status = 1
				data = (brand_id,product_id,product_brand_mapping_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if details and "category_id" in details:		
			category_id = details['category_id']

			get_query = ("""SELECT *
			FROM `product_category_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_category = cursor.execute(get_query,get_data)

			if count_product_category > 0:
				product_category_data = cursor.fetchone()
				details['product_category_id'] = product_category_data['mapping_id']

				update_query = ("""UPDATE `product_category_mapping` SET `category_id` = %s
				WHERE `product_id` = %s """)
				update_data = (category_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_category_mapping`(`category_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
				product_category_mapping_status = 1
				data = (category_id,product_id,product_category_mapping_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if top_selling == 1:

			get_query = ("""SELECT `product_meta_id`
			FROM `product_top_selling_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:

				connection.commit()
				cursor.close()

				return ({"attributes": {
			    		"status_desc": "product_top_selling",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

			else:

				insert_query = ("""INSERT INTO `product_top_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

				top_selling_product_status = 1
				data = (product_meta_id,top_selling_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if best_selling == 1:

			get_query = ("""SELECT `product_meta_id`
			FROM `product_best_selling_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:

				connection.commit()
				cursor.close()

				return ({"attributes": {
			    		"status_desc": "product_best_selling",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

			else:
				best_selling_product_status = 1
				insert_query = ("""INSERT INTO `product_best_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

				data = (product_meta_id,best_selling_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if latest_product == 1:
			
				get_query = ("""SELECT `product_meta_id`
								FROM `latest_product_mapping` WHERE  `product_meta_id` = %s""")

				getData = (product_meta_id)
		
				count_product = cursor.execute(get_query,getData)

				if count_product > 0:

					connection.commit()
					cursor.close()

					return ({"attributes": {
					    		"status_desc": "latest_product",
					    		"status": "error"
					    	},
					    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

				else:
					latest_product_status = 1
					insert_query = ("""INSERT INTO `latest_product_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s)""")

					data = (product_meta_id,latest_product_status,organisation_id,last_update_id)
					cursor.execute(insert_query,data)

		details['product_meta_id'] = product_meta_id	


		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_meta_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Add-Catalog-roduct-Meta---------------------#

#----------------------Add-Catalog-Product-With-Product-Meta---------------------#

@name_space.route("/AddCatalogProductWithMeta")
class AddCatalogProductWithMeta(Resource):
	@api.expect(product_catalog_meta_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_name = details['product_name']
		product_long_description = details['product_long_description']
		product_short_description = details['product_short_description']
		catalog_id = details['catalog_id']		
		product_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']
		product_meta_code = details['product_meta_code']
		meta_key_text = details['meta_key_text']
		in_price = details['in_price']
		out_price = details['out_price']
		product_meta_status = 1
		images = details.get('image',[])
		product_type = details['product_type']
		product_type_id = details['product_type_id']
		discount = details['discount']
		top_selling = details['top_selling']
		best_selling = details['best_selling']
		latest_product = details['latest_product']


		insert_query = ("""INSERT INTO `product`(`product_name`,`product_long_description`,
			`product_short_description`,`category_id`,`product_type`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_name,product_long_description,product_short_description,product_type_id,product_type,
			product_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		product_id = cursor.lastrowid

		insert_product_catalog_query = ("""INSERT INTO `product_catalog_mapping`(`catalog_id`,`product_id`,`organisation_id`) 
				VALUES(%s,%s,%s)""")

		product_catalog_data = (catalog_id,product_id,organisation_id)
		cursor.execute(insert_product_catalog_query,product_catalog_data)

		insert_query_product_meta = ("""INSERT INTO `product_meta`(`product_id`,`product_meta_code`,`meta_key_text`,`in_price`,`out_price`,`status`,
			`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		product_meta_data = (product_id,product_meta_code,meta_key_text,in_price,out_price,product_meta_status,organisation_id,last_update_id)
		cursor.execute(insert_query_product_meta,product_meta_data)
		product_meta_id = cursor.lastrowid

		for key,image in enumerate(images):
			if key == 0:
				default_image_flag = 1
			else:
				default_image_flag = 0

			product_meta_status_image = 1

			insert_query_image = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`status`,`organisation_id`,last_update_id) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

			data = (product_meta_id,image,default_image_flag,product_meta_status_image,organisation_id,last_update_id)
			cursor.execute(insert_query_image,data)

		if discount:
			get_discount_master_query = (""" SELECT `discount_id`,`discount` FROM `discount_master` WHERE `discount`=%s and `organisation_id` = %s""")
			get_discount_master_data = (discount,organisation_id)
			count_discount_master = cursor.execute(get_discount_master_query,get_discount_master_data)

			if count_discount_master > 0: 
				discount_master_data = cursor.fetchone()
				discount_id = discount_master_data['discount_id']				
			else:
				discount_status = 1				
				insert_discount_master_query = (""" INSERT INTO `discount_master`(`discount`,`status`,`organisation_id`,`last_update_id`)
					VALUES(%s,%s,%s,%s)""")
				discount_master_data = (discount,discount_status,organisation_id,last_update_id)
				cursor.execute(insert_discount_master_query,discount_master_data)

				discount_id = cursor.lastrowid

			get_discount_query = ("""SELECT  `product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
					FROM `product_meta_discount_mapping` WHERE  `product_meta_id` = %s and `organisation_id` = %s""")

			get_discount_data = (product_meta_id,organisation_id)
			count_product_meta_discount = cursor.execute(get_discount_query,get_discount_data)

			if count_product_meta_discount > 0:

				update_query = ("""UPDATE `product_meta_discount_mapping` SET `discount_id` = %s
				WHERE `product_meta_id` = %s """)
				update_data = (discount_id,product_meta_id)
				cursor.execute(update_query,update_data)

			else:
				product_meta_discount_status = 1
				insert_query = ("""INSERT INTO `product_meta_discount_mapping`(`product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (product_meta_id,discount_id,product_meta_discount_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if details and "brand_id" in details:		
			brand_id = details['brand_id']

			get_query = ("""SELECT *
			FROM `product_brand_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_brand = cursor.execute(get_query,get_data)

			if count_product_brand > 0:
				product_brand_data = cursor.fetchone()
				details['product_brand_id'] = product_brand_data['mapping_id']

				update_query = ("""UPDATE `product_brand_mapping` SET `brand_id` = %s
				WHERE `product_id` = %s """)
				update_data = (brand_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
				product_brand_mapping_status = 1
				data = (brand_id,product_id,product_brand_mapping_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if details and "category_id" in details:		
			category_id = details['category_id']

			get_query = ("""SELECT *
			FROM `product_category_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_category = cursor.execute(get_query,get_data)

			if count_product_category > 0:
				product_category_data = cursor.fetchone()
				details['product_category_id'] = product_category_data['mapping_id']

				update_query = ("""UPDATE `product_category_mapping` SET `category_id` = %s
				WHERE `product_id` = %s """)
				update_data = (category_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_category_mapping`(`category_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
				product_category_mapping_status = 1
				data = (category_id,product_id,product_category_mapping_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if top_selling == 1:

			get_query = ("""SELECT `product_meta_id`
			FROM `product_top_selling_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:

				connection.commit()
				cursor.close()

				return ({"attributes": {
			    		"status_desc": "product_top_selling",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

			else:

				insert_query = ("""INSERT INTO `product_top_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

				top_selling_product_status = 1
				data = (product_meta_id,top_selling_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)


		if best_selling == 1:

			get_query = ("""SELECT `product_meta_id`
			FROM `product_best_selling_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:

				connection.commit()
				cursor.close()

				return ({"attributes": {
			    		"status_desc": "product_best_selling",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

			else:
				best_selling_product_status = 1
				insert_query = ("""INSERT INTO `product_best_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

				data = (product_meta_id,best_selling_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)


			if latest_product == 1:
			
				get_query = ("""SELECT `product_meta_id`
								FROM `latest_product_mapping` WHERE  `product_meta_id` = %s""")

				getData = (product_meta_id)
		
				count_product = cursor.execute(get_query,getData)

				if count_product > 0:

					connection.commit()
					cursor.close()

					return ({"attributes": {
					    		"status_desc": "latest_product",
					    		"status": "error"
					    	},
					    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

				else:
					latest_product_status = 1
					insert_query = ("""INSERT INTO `latest_product_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s)""")

					data = (product_meta_id,latest_product_status,organisation_id,last_update_id)
					cursor.execute(insert_query,data)		

		details['product_meta_id'] = product_meta_id		

		details['product_id'] = product_id	

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Add-Catalog-Product-With-Product-Meta---------------------#

#----------------------Add-Catalog-with-Product-With-Product-Meta---------------------#

@name_space.route("/AddCatalogWithProductWithMeta")
class AddCatalogWithProductWithMeta(Resource):
	@api.expect(catalog_product_meta_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_name = details['product_name']
		product_long_description = details['product_long_description']
		product_short_description = details['product_short_description']
		catalog = details['catalog']		
		product_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']
		product_meta_code = details['product_meta_code']
		meta_key_text = details['meta_key_text']
		in_price = details['in_price']
		out_price = details['out_price']
		product_meta_status = 1
		images = details.get('image',[])
		product_type = details['product_type']
		product_type_id = details['product_type_id']
		discount = details['discount']
		top_selling = details['top_selling']
		best_selling = details['best_selling']

		catalogstatus = 1

		insert_query = ("""INSERT INTO `catalogs`(`catalog_name`,`organisation_id`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")
		data = (catalog_name,organisation_id,catalogstatus,last_update_id)
		cursor.execute(insert_query,data)
		catalog_id = cursor.lastrowid

		insert_query = ("""INSERT INTO `product`(`product_name`,`product_long_description`,
			`product_short_description`,`category_id`,`product_type`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (product_name,product_long_description,product_short_description,product_type_id,product_type,
			product_status,organisation_id,last_update_id)
		cursor.execute(insert_query,data)
		product_id = cursor.lastrowid

		insert_product_catalog_query = ("""INSERT INTO `product_catalog_mapping`(`catalog_id`,`product_id`,`organisation_id`) 
				VALUES(%s,%s,%s)""")

		product_catalog_data = (catalog_id,product_id,organisation_id)
		cursor.execute(insert_product_catalog_query,product_catalog_data)

		insert_query_product_meta = ("""INSERT INTO `product_meta`(`product_id`,`product_meta_code`,`meta_key_text`,`in_price`,`out_price`,`status`,
			`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		product_meta_data = (product_id,product_meta_code,meta_key_text,in_price,out_price,product_meta_status,organisation_id,last_update_id)
		cursor.execute(insert_query_product_meta,product_meta_data)
		product_meta_id = cursor.lastrowid

		for key,image in enumerate(images):
			if key == 0:
				default_image_flag = 1
			else:
				default_image_flag = 0

			product_meta_status_image = 1

			insert_query_image = ("""INSERT INTO `product_meta_images`(`product_meta_id`,`image`,`default_image_flag`,`status`,`organisation_id`,last_update_id) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

			data = (product_meta_id,image,default_image_flag,product_meta_status_image,organisation_id,last_update_id)
			cursor.execute(insert_query_image,data)

		if discount:
			get_discount_master_query = (""" SELECT `discount_id`,`discount` FROM `discount_master` WHERE `discount`=%s and `organisation_id` = %s""")
			get_discount_master_data = (discount,organisation_id)
			count_discount_master = cursor.execute(get_discount_master_query,get_discount_master_data)

			if count_discount_master > 0: 
				discount_master_data = cursor.fetchone()
				discount_id = discount_master_data['discount_id']				
			else:
				discount_status = 1				
				insert_discount_master_query = (""" INSERT INTO `discount_master`(`discount`,`status`,`organisation_id`,`last_update_id`)
					VALUES(%s,%s,%s,%s)""")
				discount_master_data = (discount,discount_status,organisation_id,last_update_id)
				cursor.execute(insert_discount_master_query,discount_master_data)

				discount_id = cursor.lastrowid

			get_discount_query = ("""SELECT  `product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
					FROM `product_meta_discount_mapping` WHERE  `product_meta_id` = %s and `organisation_id` = %s""")

			get_discount_data = (product_meta_id,organisation_id)
			count_product_meta_discount = cursor.execute(get_discount_query,get_discount_data)

			if count_product_meta_discount > 0:

				update_query = ("""UPDATE `product_meta_discount_mapping` SET `discount_id` = %s
				WHERE `product_meta_id` = %s """)
				update_data = (discount_id,product_meta_id)
				cursor.execute(update_query,update_data)

			else:
				product_meta_discount_status = 1
				insert_query = ("""INSERT INTO `product_meta_discount_mapping`(`product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (product_meta_id,discount_id,product_meta_discount_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if details and "brand_id" in details:		
			brand_id = details['brand_id']

			get_query = ("""SELECT *
			FROM `product_brand_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_brand = cursor.execute(get_query,get_data)

			if count_product_brand > 0:
				product_brand_data = cursor.fetchone()
				details['product_brand_id'] = product_brand_data['mapping_id']

				update_query = ("""UPDATE `product_brand_mapping` SET `brand_id` = %s
				WHERE `product_id` = %s """)
				update_data = (brand_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
				product_brand_mapping_status = 1
				data = (brand_id,product_id,product_brand_mapping_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if details and "category_id" in details:		
			category_id = details['category_id']

			get_query = ("""SELECT *
			FROM `product_category_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_category = cursor.execute(get_query,get_data)

			if count_product_category > 0:
				product_category_data = cursor.fetchone()
				details['product_category_id'] = product_category_data['mapping_id']

				update_query = ("""UPDATE `product_category_mapping` SET `category_id` = %s
				WHERE `product_id` = %s """)
				update_data = (category_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_category_mapping`(`category_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")
				product_category_mapping_status = 1
				data = (category_id,product_id,product_category_mapping_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if top_selling == 1:

			get_query = ("""SELECT `product_meta_id`
			FROM `product_top_selling_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:

				connection.commit()
				cursor.close()

				return ({"attributes": {
			    		"status_desc": "product_top_selling",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

			else:

				insert_query = ("""INSERT INTO `product_top_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

				top_selling_product_status = 1
				data = (product_meta_id,top_selling_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)


		if best_selling == 1:

			get_query = ("""SELECT `product_meta_id`
			FROM `product_best_selling_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:

				connection.commit()
				cursor.close()

				return ({"attributes": {
			    		"status_desc": "product_best_selling",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

			else:
				best_selling_product_status = 1
				insert_query = ("""INSERT INTO `product_best_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

				data = (product_meta_id,best_selling_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		if latest_product == 1:
			
			get_query = ("""SELECT `product_meta_id`
								FROM `latest_product_mapping` WHERE  `product_meta_id` = %s""")

			getData = (product_meta_id)
		
			count_product = cursor.execute(get_query,getData)

			if count_product > 0:

				connection.commit()
				cursor.close()

				return ({"attributes": {
					    		"status_desc": "latest_product",
					    		"status": "error"
					    	},
					    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

			else:
				latest_product_status = 1
				insert_query = ("""INSERT INTO `latest_product_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s)""")

				data = (product_meta_id,latest_product_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		details['product_meta_id'] = product_meta_id		

		details['product_id'] = product_id	

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#----------------------Add-Catalog-Product-With-Product-Meta---------------------#

#----------------------Set-Product-Default-Image---------------------#

@name_space.route("/productMetaDefaultImage/<int:product_image_id>/<int:product_meta_id>")
class productMetaDefaultImage(Resource):
	def put(self,product_image_id,product_meta_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		product_image_id = product_image_id

		update_query = ("""UPDATE `product_meta_images` SET `default_image_flag` = 1
				WHERE `product_image_id` = %s """)
		update_data = (product_image_id)
		cursor.execute(update_query,update_data)		

		update_product_meta_images_query = ("""UPDATE `product_meta_images` SET `default_image_flag` = 0
				WHERE `product_image_id` <> %s and `product_meta_id` = %s""")
		update_product_meta_data = (product_image_id,product_meta_id)
		cursor.execute(update_product_meta_images_query,update_product_meta_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Product Image Flag",
								"status": "success",
								"message":"Update Image successfully"
									},
				"responseList":product_image_id}), status.HTTP_200_OK

#----------------------Set-Product-Default-Image---------------------#


#----------------------Set-Product-Default-Image---------------------#

@name_space.route("/productMetaDefaultImageWithEmployee/<int:product_image_id>/<int:product_meta_id>/<int:employee_id>/<int:organisation_id>/<string:last_updated_ip_address>")
class productMetaDefaultImageWithEmployee(Resource):
	def put(self,product_image_id,product_meta_id,employee_id,organisation_id,last_updated_ip_address):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		product_image_id = product_image_id

		update_query = ("""UPDATE `product_meta_images` SET `default_image_flag` = 1
				WHERE `product_image_id` = %s """)
		update_data = (product_image_id)
		cursor.execute(update_query,update_data)

		get_product_id_query = ("""SELECT `product_id`
						FROM `product_meta` WHERE  `product_meta_id` = %s""")
		get_product_id_data = (product_meta_id)
		cursor.execute(get_product_id_query,get_product_id_data)

		product_data = cursor.fetchone()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		url = BASE_URL + "ecommerce_product_log/EcommerceProductLog/AddProductLog"
		payloadData = {
							"product_id":product_data['product_id'],
							"product_meta_id":product_meta_id,
							"product_meta_image_id":product_image_id,
							"comments": "Set Default Image",
							"default_image_flag" : 1,
							"employee_id":employee_id,
							"organisation_id":organisation_id,
							"last_updated_ip_address":last_updated_ip_address
					}

		requests.post(url,data=json.dumps(payloadData), headers=headers).json()

		update_product_meta_images_query = ("""UPDATE `product_meta_images` SET `default_image_flag` = 0
				WHERE `product_image_id` <> %s and `product_meta_id` = %s""")
		update_product_meta_data = (product_image_id,product_meta_id)
		cursor.execute(update_product_meta_images_query,update_product_meta_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Product Image Flag",
								"status": "success",
								"message":"Update Image successfully"
									},
				"responseList":product_image_id}), status.HTTP_200_OK

#----------------------Set-Product-Default-Image---------------------#

#----------------------Add-Discount---------------------#

@name_space.route("/AddDiscount")
class AddDiscount(Resource):
	@api.expect(discount_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		discount = details['discount']
		discount_image = details['discount_image']
		discount_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_query = ("""SELECT `discount`
			FROM `discount_master` WHERE `discount` = %s """)

		getData = (discount)
		
		count_meta_key = cursor.execute(get_query,getData)

		if count_meta_key > 0:
			return ({"attributes": {
			    		"status_desc": "discount_details",
			    		"status": "error"
			    	},
			    	"responseList":"Discout Already Exsits" }), status.HTTP_200_OK

		else:	

			insert_query = ("""INSERT INTO `discount_master`(`discount`,`discount_image`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")

			data = (discount,discount_image,discount_status,organisation_id,last_update_id)
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
@name_space.route("/discountList/<int:organisation_id>")	
class discountList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT  `discount_id`,`discount`,`discount_image`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
			FROM `discount_master` WHERE  `organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		discount_data = cursor.fetchall()

		for key,data in enumerate(discount_data):
			discount_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "discount_details",
		    		"status": "success"
		    	},
		    	"responseList":discount_data}), status.HTTP_200_OK

#----------------------Discount-List---------------------#

#----------------------Discount-Details---------------------#
@name_space.route("/discountDetails/<int:discount_id>")	
class discountDetails(Resource):
	def get(self,discount_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT  `discount_id`,`discount`,`discount_image`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
			FROM `discount_master` WHERE  `discount_id` = %s""")

		get_data = (discount_id)
		cursor.execute(get_query,get_data)

		discount_data = cursor.fetchone()
		
		discount_data['last_update_ts'] = str(discount_data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "discount_details",
		    		"status": "success"
		    	},
		    	"responseList":discount_data}), status.HTTP_200_OK

#----------------------Discount-Details---------------------#

#----------------------Update-Discount---------------------#
@name_space.route("/updateDiscount/<int:discount_id>")	
class updateDiscount(Resource):
	@api.expect(discount_putmodel)
	def put(self,discount_id):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()	
		
		if details and "discount" in details:
			discount = details['discount']
			update_query = ("""UPDATE `discount_master` SET `discount` = %s
				WHERE `discount_id` = %s """)
			update_data = (discount,discount_id)
			cursor.execute(update_query,update_data)

		if details and "discount_image" in details:
			discount_image = details['discount_image']
			update_query = ("""UPDATE `discount_master` SET `discount_image` = %s
				WHERE `discount_id` = %s """)
			update_data = (discount_image,discount_id)
			cursor.execute(update_query,update_data)


		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "discount_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK	
#----------------------Update-Offer---------------------#

#----------------------Product-Discount---------------------#

@name_space.route("/ProductMetaDiscount")
class ProductMetaDiscount(Resource):
	@api.expect(product_meta_discount_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		product_meta_ids = details.get('product_meta_id',[])
		product_meta_discount_status = 1
		discount_id = details['discount_id']

		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		for product_meta_id in product_meta_ids:

			get_query = ("""SELECT  `product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`,`last_update_ts`
			FROM `product_meta_discount_mapping` WHERE  `product_meta_id` = %s """)

			get_data = (product_meta_id)
			count_producct_meta_discount = cursor.execute(get_query,get_data)

			if count_producct_meta_discount > 0:

				update_query = ("""UPDATE `product_meta_discount_mapping` SET `discount_id` = %s
				WHERE `product_meta_id` = %s """)
				update_data = (discount_id,product_meta_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_meta_discount_mapping`(`product_meta_id`,`discount_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (product_meta_id,discount_id,product_meta_discount_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    	"status_desc": "product_discount_details",
			    	"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Product-Discount---------------------#

#----------------------Add-Notification---------------------#	

@name_space.route("/addNotification")	
class addNotification(Resource):
	@api.expect(notification_postmodel)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		
		text = details['text']
		image = details['image']
		email = details['email']
		whatsapp = details['whatsapp']
		sms = details['sms']
		app_notification = details['app_notification']

		now = datetime.now()
		date_of_creation = now.strftime("%Y-%m-%d %H:%M:%S")

		insert_query = ("""INSERT INTO `notification`(`text`,`image`,`email`,`whatsapp`,`sms`,`app_notification`,`date_of_creation`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s)""")

		data = (text,image,email,whatsapp,sms,app_notification,date_of_creation)
		cursor.execute(insert_query,data)	

		notification_id = cursor.lastrowid
		details['notification_id'] = notification_id

		connection.commit()
		cursor.close()		
		return ({"attributes": {
				    		"status_desc": "notification_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK		


#----------------------Add-Notification---------------------#

#----------------------Get-Notification-List---------------------#	
@name_space.route("/getNotificationList")	
class getNotificationList(Resource):
	def get(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `notification` """)

		cursor.execute(get_query)

		notification_data = cursor.fetchall()

		for key,data in enumerate(notification_data):
			notification_data[key]['date_of_creation'] = str(data['date_of_creation'])	
			notification_data[key]['date_of_update'] = str(data['date_of_update'])	

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "notification_details",
		    		"status": "success"
		    	},
		    	"responseList":notification_data}), status.HTTP_200_OK

#----------------------Get-Notification-List---------------------#

#----------------------Update-Notification---------------------#
@name_space.route("/updateNotification/<int:notifictaion_id>")	
class updateNotification(Resource):
	@api.expect(notification_postmodel)
	def put(self,notifictaion_id):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		now = datetime.now()
		date_of_update = now.strftime("%Y-%m-%d %H:%M:%S")
		
		if details and "text" in details:
			text = details['text']
			update_query = ("""UPDATE `notification` SET `text` = %s , `date_of_update` = %s
				WHERE `notification_id` = %s """)
			update_data = (text,date_of_update,notifictaion_id)
			cursor.execute(update_query,update_data)

		if details and "image" in details:
			image = details['image']
			update_query = ("""UPDATE `notification` SET `image` = %s , `date_of_update` = %s
				WHERE `notification_id` = %s """)
			update_data = (image,date_of_update,notifictaion_id)
			cursor.execute(update_query,update_data)

		if details and "email" in details:
			email = details['email']
			update_query = ("""UPDATE `notification` SET `email` = %s , `date_of_update` = %s
				WHERE `notification_id` = %s """)
			update_data = (email,date_of_update,notifictaion_id)
			cursor.execute(update_query,update_data)

		if details and "whatsapp" in details:
			whatsapp = details['whatsapp']
			update_query = ("""UPDATE `notification` SET `whatsapp` = %s , `date_of_update` = %s
				WHERE `notification_id` = %s """)
			update_data = (whatsapp,date_of_update,notifictaion_id)
			cursor.execute(update_query,update_data)

		if details and "sms" in details:
			sms = details['sms']
			update_query = ("""UPDATE `notification` SET `sms` = %s , `date_of_update` = %s
				WHERE `notification_id` = %s """)
			update_data = (sms,date_of_update,notifictaion_id)
			cursor.execute(update_query,update_data)

		if details and "app_notification" in details:
			app_notification = details['app_notification']
			update_query = ("""UPDATE `notification` SET `app_notification` = %s , `date_of_update` = %s
				WHERE `notification_id` = %s """)
			update_data = (app_notification,date_of_update,notifictaion_id)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
				    		"status_desc": "notification_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK	
#----------------------Update-Notification---------------------#

#----------------------Delete-Notification---------------------#	
@name_space.route("/deleteNotification/<int:notifictaion_id>")	
class deleteNotification(Resource):
	def delete(self,notifictaion_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `notification` WHERE `notifictaion_id` = %s """)
		delData = (notifictaion_id)		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_notification",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Notification---------------------#	

#----------------------Add-Customer-Notification---------------------#	

@name_space.route("/addCustomerNotification")	
class addCustomerNotification(Resource):
	@api.expect(customer_notification_postmodel)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		
		notification_id = details['notification_id']
		product_id = details['product_id']
		customer_id = details['customer_id']	

		insert_query = ("""INSERT INTO `customer_notification_mapping`(`notification_id`,`product_id`,`customer_id`) 
				VALUES(%s,%s,%s)""")

		data = (notification_id,product_id,customer_id)
		cursor.execute(insert_query,data)	

		customer_notification_id = cursor.lastrowid
		details['customer_notification_id'] = customer_notification_id

		connection.commit()
		cursor.close()		
		return ({"attributes": {
				    		"status_desc": "customer_notification_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK		


#----------------------Add-Customer-Notification---------------------#

#----------------------Delete-Customer-Notification---------------------#	
@name_space.route("/deleteCustomerNotification/<int:customer_notification_id>")	
class deleteCustomerNotification(Resource):
	def delete(self,customer_notification_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `customer_notification_mapping` WHERE `customer_notification_id` = %s """)
		delData = (customer_notification_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_customer_notification",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Customer-Notification---------------------#

#----------------------Add-Offer---------------------#
@name_space.route("/addOffer")	
class addOffer(Resource):
	@api.expect(offer_postmodel)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		
		if details and "offer_image" in details:
			offer_image = details['offer_image']
		else:
			offer_image = ""

		offer_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		coupon_code = details['coupon_code']
		discount_percentage = details['discount_percentage']
		absolute_price = details['absolute_price']
		discount_value = details['discount_value']
		product_offer_type = details['product_offer_type']
		is_landing_page = details['is_landing_page']

		if details and "is_online" in details:
			is_online = details['is_online']
		else:
			is_online = 0

		if details and "instruction" in details:
			instruction = details['instruction']
		else:
			instruction = ""

		if details and "validity_date" in details:
			validity_date = details['validity_date']
		else:
			validity_date = ""

		
		offer_image_type = 1		

		

		products = []		

		if details and "product_id" in details:
			product_ids = details.get('product_id',[])

			for product_id in product_ids:
				product_offer_mapping_query = (""" SELECT *
						FROM `product_offer_mapping` pom where  `organisation_id` = %s and `product_id` = %s""")
				product_offer_mapping_data = (organisation_id,product_id)
				count_product_offer_mapping_data = cursor.execute(product_offer_mapping_query,product_offer_mapping_data)					

				if count_product_offer_mapping_data > 0:
					get_query = ("""SELECT `product_name`
							FROM `product` WHERE  `product_id` = %s """)

					getData = (product_id)
					cursor.execute(get_query,getData)
					product_data = cursor.fetchone()

					products.append(product_data['product_name'])

				else:
					insert_query = ("""INSERT INTO `offer`(`offer_image`,`coupon_code`,`discount_percentage`,`absolute_price`,`discount_value`,`product_offer_type`,`offer_image_type`,`is_landing_page`,`is_online`,`instruction`,`status`,`validity_date`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

					data = (offer_image,coupon_code,discount_percentage,absolute_price,discount_value,product_offer_type,offer_image_type,is_landing_page,is_online,instruction,offer_status,validity_date,organisation_id,last_update_id)
					cursor.execute(insert_query,data)	

					offer_id = cursor.lastrowid
					details['offer_id'] = offer_id

					product_offer_status = 1
					insert_query = ("""INSERT INTO `product_offer_mapping`(`offer_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s)""")

					data = (offer_id,product_id,product_offer_status,organisation_id,last_update_id)
					cursor.execute(insert_query,data)

					if details and "image" in details:
						images = details.get('image',[])

						for image in images:
							insert_query = ("""INSERT INTO `offer_images`(`offer_id`,`offer_image`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s)""")

							data = (offer_id,image,organisation_id,last_update_id)
							cursor.execute(insert_query,data)

		#headers = {'Content-type':'application/json', 'Accept':'application/json'}
		#sendAppPushNotificationUrl = BASE_URL + "ecommerce_product/EcommerceProduct/sendNotifications"
		#payloadpushData = {
									#"organisation_id": organisation_id,
									#"image":offer_image,
									#"text": "Offer Coupon Code:"+str(coupon_code),
									#"title": "Offer"
								#}
		#print(payloadpushData)
		#send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		#print(products)
		connection.commit()
		cursor.close()

		if len(products) == 0:

			return ({"attributes": {
				    		"status_desc": "offer_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK
		else:
			exsits_products = ','.join(products)

			return ({"attributes": {
					    	"status_desc": "Product Already Exsits",
					    	"status": "error"
					},
					"responseList":{"product_name":exsits_products} }), status.HTTP_200_OK


#----------------------Add-Offer---------------------#


#----------------------Add-Offer-with-product-Variant---------------------#
@name_space.route("/addOfferWithProductVariant")	
class addOfferWithProductVariant(Resource):
	@api.expect(product_variant_offer_postmodel)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		
		if details and "offer_image" in details:
			offer_image = details['offer_image']
		else:
			offer_image = ""

		offer_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		coupon_code = details['coupon_code']
		discount_percentage = details['discount_percentage']
		absolute_price = details['absolute_price']
		discount_value = details['discount_value']
		product_offer_type = details['product_offer_type']
		is_landing_page = details['is_landing_page']

		if details and "is_online" in details:
			is_online = details['is_online']
		else:
			is_online = 0

		if details and "instruction" in details:
			instruction = details['instruction']
		else:
			instruction = ""

		if details and "validity_date" in details:
			validity_date = details['validity_date']
		else:
			validity_date = ""

		
		offer_image_type = 1
		is_product_meta_offer = 1	

		

		insert_query = ("""INSERT INTO `offer`(`offer_image`,`coupon_code`,`discount_percentage`,`absolute_price`,`discount_value`,`product_offer_type`,`offer_image_type`,`is_landing_page`,`is_online`,`instruction`,`status`,`organisation_id`,`validity_date`,`is_product_meta_offer`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (offer_image,coupon_code,discount_percentage,absolute_price,discount_value,product_offer_type,offer_image_type,is_landing_page,is_online,instruction,offer_status,organisation_id,validity_date,is_product_meta_offer,last_update_id)
		cursor.execute(insert_query,data)	

		offer_id = cursor.lastrowid
		details['offer_id'] = offer_id

		if offer_id:

			if details and "product_meta_id" in details:
				product_meta_ids = details.get('product_meta_id',[])
				for product_meta_id in product_meta_ids:
					get_product_id_query = ("""SELECT * FROM `product_meta` where `product_meta_id` = %s""")
					get_product_id_data = (product_meta_id)
					cursor.execute(get_product_id_query,get_product_id_data)
					product_id_data = cursor.fetchone()

					product_meta_offer_mapping_query = (""" SELECT *
						FROM `product_meta_offer_mapping` pmom where  `organisation_id` = %s and `product_id` = %s and `product_meta_id` = %s""")
					product_meta_offer_mapping_data = (organisation_id,product_id_data['product_id'],product_meta_id)
					count_product_meta_offer_mapping_data = cursor.execute(product_meta_offer_mapping_query,product_meta_offer_mapping_data)

					if count_product_meta_offer_mapping_data > 0:
						get_query = ("""SELECT `product_name`
							FROM `product` WHERE  `product_id` = %s """)

						getData = (product_id_data['product_id'])
						cursor.execute(get_query,getData)
						product_data = cursor.fetchone()

						return ({"attributes": {
					    	"status_desc": "Product Already Exsits",
					    	"status": "success"
					    },
					    "responseList":{"product_name":product_data['product_name']} }), status.HTTP_200_OK

					else:
						product_offer_status = 1
						insert_query = ("""INSERT INTO `product_meta_offer_mapping`(`offer_id`,`product_id`,`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s,%s,%s)""")

						data = (offer_id,product_id_data['product_id'],product_meta_id,product_offer_status,organisation_id,last_update_id)
						cursor.execute(insert_query,data)

			if details and "image" in details:
				images = details.get('image',[])

				for image in images:
					insert_query = ("""INSERT INTO `offer_images`(`offer_id`,`offer_image`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

					data = (offer_id,image,organisation_id,last_update_id)
					cursor.execute(insert_query,data)

		#headers = {'Content-type':'application/json', 'Accept':'application/json'}
		#sendAppPushNotificationUrl = BASE_URL + "ecommerce_product/EcommerceProduct/sendNotifications"
		#payloadpushData = {
									#"organisation_id": organisation_id,
									#"image":offer_image,
									#"text": "Offer Coupon Code:"+str(coupon_code),
									#"title": "Offer"
								#}
		#print(payloadpushData)
		#send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "offer_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK
#----------------------Add-Offer-with-product-Variant---------------------#

#----------------------Send-Offer-Notification---------------------#
@name_space.route("/sendOfferNotification")	
class sendOfferNotification(Resource):
	@api.expect(send_offer_postmodel)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		offer_id = details['offer_id']
		organisation_id = details['organisation_id']

		get_query = ("""SELECT *
				FROM `offer` o				
				WHERE o.`offer_id` = %s""")
		get_data = (offer_id)

		cursor.execute(get_query,get_data)
		offer_data = cursor.fetchone()

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		sendAppPushNotificationUrl = BASE_URL + "ecommerce_product/EcommerceProduct/sendNotifications"
		payloadpushData = {
									"organisation_id": organisation_id,
									"image":offer_data['offer_image'],
									"text": "Offer Coupon Code:"+str(offer_data['coupon_code']),
									"title": "Offer"
								}
		print(payloadpushData)
		send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		return ({"attributes": {
				    		"status_desc": "offer_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK

#----------------------Send-Offer-Notification---------------------#

#----------------------Add-Offer-Images---------------------#

@name_space.route("/AddOfferImages")	
class AddOfferImages(Resource):
	@api.expect(offer_image_postmodel)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		offer_id = details['offer_id']
		images = details.get('image',[])
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']

		delete_query = ("""DELETE FROM `offer_images` WHERE `offer_id` = %s """)
		delData = (offer_id)
		
		cursor.execute(delete_query,delData)

		for image in images:

			insert_query = ("""INSERT INTO `offer_images`(`offer_id`,`offer_image`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

			data = (offer_id,image,organisation_id,last_update_id)
			cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    	"status_desc": "offer_details",
				    	"status": "success"
				 },
				 "responseList":details}), status.HTTP_200_OK

#----------------------Add-Offer-Images---------------------#


#----------------------Get-Offer-List---------------------#	
@name_space.route("/getOfferList/<int:organisation_id>")	
class getOfferList(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `offer` where `organisation_id` = %s and `status` = 1""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)

		offer_data = cursor.fetchall()

		for key,data in enumerate(offer_data):
			if data['is_product_meta_offer'] == 1:

				product_meta_offer_mapping_query = (""" SELECT p.`product_id`,p.`product_name`,pmom.`product_meta_id`
						FROM `product_meta_offer_mapping` pmom						
						INNER JOIN `product` p ON p.`product_id` = pmom.`product_id` 
						where  pmom.`offer_id` = %s""")
				product_meta_offer_mapping_data = (data['offer_id'])
				count_product_meta_offer_mapping_data = cursor.execute(product_meta_offer_mapping_query,product_meta_offer_mapping_data)

				if count_product_meta_offer_mapping_data > 0:
					offer_product_meta = cursor.fetchall()

					for omkey,omdata in enumerate(offer_product_meta):
						get_product_meta_information_query = ("""SELECT pm.`product_meta_code`,pm.`meta_key_text`,pm.`in_price`,pm.`out_price`,pm.`loyalty_points`
								FROM `product_meta` pm
								WHERE pm.`product_meta_id` = %s""")
						get_product_meta_information_data = (omdata['product_meta_id'])
						cursor.execute(get_product_meta_information_query,get_product_meta_information_data)

						product_meta_data = cursor.fetchone()

						if product_meta_data['meta_key_text'] :
							a_string = product_meta_data['meta_key_text']
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

								product_meta_data['met_key_value'] = met_key

						offer_product_meta[omkey]['in_price'] = product_meta_data['in_price']
						offer_product_meta[omkey]['out_price'] = product_meta_data['out_price']
						offer_product_meta[omkey]['met_key_value'] = product_meta_data['met_key_value']

						get_product_meta_with_image_query = ("""SELECT pmi.`image` 
							FROM  `product_meta_images` pmi
							where pmi.`product_meta_id` = %s and is_gallery = 0  and image_type = 1 order by default_image_flag desc""")
						get_product_meta_with_image_data = (omdata['product_meta_id'])
						count_product_meta_image = cursor.execute(get_product_meta_with_image_query,get_product_meta_with_image_data)

						if count_product_meta_image > 0:

							product_meta_image_data = cursor.fetchone()

							offer_product_meta[omkey]['image'] = product_meta_image_data['image']
						else:
							offer_product_meta[omkey]['image'] = ""

					offer_data[key]['product_data'] = offer_product_meta
				else:
					offer_data[key]['product_data'] = []

			else:
				get_offer_product_query = ("""SELECT p.`product_id`,p.`product_name`
					FROM `product_offer_mapping` pom
					INNER JOIN `product` p ON p.`product_id` = pom.`product_id`
					where pom.`offer_id` = %s""")
				get_product_offer_data = (data['offer_id'])
				count_product_offer  = cursor.execute(get_offer_product_query,get_product_offer_data)

				if count_product_offer > 0:
					product_offer_data = cursor.fetchall()

					for okey,odata in enumerate(product_offer_data):						
						get_product_meta_with_image_query = ("""SELECT pmi.`image` 
							FROM `product_meta` pm
							INNER JOIN `product_meta_images` pmi ON pmi.`product_meta_id` = pm.`product_meta_id`
							where pm.`product_id` = %s and is_gallery = 0  and image_type = 1 order by default_image_flag desc""")
						get_product_meta_with_image_data = (odata['product_id'])
						count_product_meta_image = cursor.execute(get_product_meta_with_image_query,get_product_meta_with_image_data)

						if count_product_meta_image > 0:

							product_meta_image_data = cursor.fetchone()

							product_offer_data[okey]['image'] = product_meta_image_data['image']
						else:
							product_offer_data[okey]['image'] = ""

						product_offer_data[okey]['product_meta_id'] = 0	
						product_offer_data[okey]['in_price'] = 0
						product_offer_data[okey]['out_price'] = 0
						product_offer_data[okey]['met_key_value'] = {}


					offer_data[key]['product_data'] = product_offer_data
				else:
					offer_data[key]['product_data'] = []
		

			get_query_image = ("""SELECT `offer_image` FROM `offer_images` WHERE `offer_id` = %s""")
			getdata_image = (data['offer_id'])
			image_count = cursor.execute(get_query_image,getdata_image)			

			if image_count > 0:
				offer_images = cursor.fetchall()

				image_a = []

				for image in offer_images:
					image_a.append(image['offer_image'])

				offer_data[key]['images'] = image_a
			else:
				offer_data[key]['images'] = []

			offer_data[key]['last_update_ts'] = str(data['last_update_ts'])	
			

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "offer_details",
		    		"status": "success"
		    	},
		    	"responseList":offer_data}), status.HTTP_200_OK

#----------------------Get-Offer-List---------------------#

#----------------------Get-Section-List---------------------#	
@name_space.route("/getSectionList/<int:organisation_id>")	
class getSectionList(Resource):
	def get(self,organisation_id):

		now = datetime.now()
		today_date = now.strftime("%Y-%m-%d")

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `section_master` where `organisation_id` = %s ORDER BY `sequence`""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)

		section_data = cursor.fetchall()

		for key,data in enumerate(section_data):
			get_offer_section_query = ("""SELECT *
				FROM `offer_section_mapping` osm 
				INNER JOIN `offer` o ON o.`offer_id` = osm.`offer_id` 
				WHERE osm.`section_id` = %s and o.`status` = 1 and date(o.`validity_date`) >= %s and o.`is_product_meta_offer` = 0""")
			get_offer_section_data = (data['section_id'],today_date)
			offer_section_count = cursor.execute(get_offer_section_query,get_offer_section_data)

			if offer_section_count > 0:
				section_data[key]['is_valid_offer'] = 1
			else:
				section_data[key]['is_valid_offer'] = 0
						
						
			section_data[key]['last_update_ts'] = str(data['last_update_ts'])	
			

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "section_details",
		    		"status": "success"
		    	},
		    	"responseList":section_data}), status.HTTP_200_OK

#----------------------Get-Section-List---------------------#

#----------------------Get-Section-Offer-List---------------------#	
@name_space.route("/getSectionOfferList/<int:organisation_id>/<int:section_id>")	
class getSectionOfferList(Resource):
	def get(self,organisation_id,section_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `offer` where `organisation_id` = %s and `status` = 1""")
		get_data = (organisation_id)

		cursor.execute(get_query,get_data)

		section_data = cursor.fetchall()

		for key,data in enumerate(section_data):
			get_offer_section_query = (""" SELECT *
				FROM `offer_section_mapping` where `section_id` = %s and `organisation_id` = %s and `offer_id` = %s""")
			get_offer_section_data = (section_id,organisation_id,data['offer_id'])
			count_section_offer = cursor.execute(get_offer_section_query,get_offer_section_data)

			if count_section_offer > 0:
				section_data[key]['is_offer'] = 1
			else:
				section_data[key]['is_offer'] = 0

			get_offer_product =  ("""SELECT p.`product_id`,p.`product_name`,p.`product_short_description`,p.`product_long_description`
				FROM `product_offer_mapping` pom			
				INNER JOIN `product` p ON pom.`product_id` = p.`product_id`  			
				WHERE pom.`offer_id` = %s""")
			get_offer_product_data = (data['offer_id'])
			count_product_offer = cursor.execute(get_offer_product,get_offer_product_data)

			if count_product_offer > 0:
				product_data = cursor.fetchall()
				section_data[key]['product_data'] = product_data
			else:
				section_data[key]['product_data'] = []

			get_query_offer_image = ("""SELECT `offer_image` FROM `offer_images` WHERE `offer_id` = %s""")
			getdata_offer_image = (data['offer_id'])
			image_count = cursor.execute(get_query_offer_image,getdata_offer_image)

			if image_count > 0:
				offer_images = cursor.fetchall()

				image_a = []

				for image_offer in offer_images:
					image_a.append(image_offer['offer_image'])

				section_data[key]['images'] = image_a
			else:
				section_data[key]['images'] = []

			section_data[key]['last_update_ts'] = str(data['last_update_ts'])	
			

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "section_details",
		    		"status": "success"
		    	},
		    	"responseList":section_data}), status.HTTP_200_OK

#----------------------Get-Section-Offer-List---------------------#	

#----------------------Get-Offer-Product-List---------------------#	
@name_space.route("/getOfferProductList/<int:organisation_id>/<int:offer_id>")	
class getSectionOfferList(Resource):
	def get(self,organisation_id,offer_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name`
			FROM `product_offer_mapping` poom
			INNER JOIN `product` p ON p.`product_id` = poom.`product_id`
			INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = p.`product_id` 
			where pom.`organisation_id` = %s and p.`status` = 1 and poom.`offer_id` = %s""")
		get_data = (organisation_id,offer_id)
		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_offer_product =  ("""SELECT *
				FROM `product_offer_mapping` pom			
				WHERE pom.`offer_id` = %s""")
			get_offer_product_data = (offer_id)

			count_offer_product = cursor.execute(get_offer_product,get_offer_product_data)

			if count_offer_product > 0:
				product_data[key]['is_product_offer'] = 1
			else:
				product_data[key]['is_product_offer'] = 0

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "product_offer_details",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK


#----------------------Add-Section-Offer---------------------#

@name_space.route("/addOfferSection")
class addOfferSection(Resource):
	@api.expect(offer_section_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		organisation_id = details['organisation_id']
		section_id = details['section_id']
		offer_id = details['offer_id']
		last_update_id = details['organisation_id']

		get_query = ("""SELECT *
			FROM `offer_section_mapping` where `section_id` = %s and `organisation_id` = %s and `offer_id` = %s""")
		get_data = (section_id,organisation_id,offer_id)

		count_section_offer = cursor.execute(get_query,get_data)

		if count_section_offer > 0:

			connection.commit()
			cursor.close()

			return ({"attributes": {
				    	"status_desc": "offer_section",
				    	"status": "error"
				    },
				    "responseList":"Offer Already Exsits" }), status.HTTP_200_OK

		else:
			insert_query = ("""INSERT INTO `offer_section_mapping`(`offer_id`,`section_id`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

			data = (offer_id,section_id,organisation_id,last_update_id)
			cursor.execute(insert_query,data)		

			section_offer_id = cursor.lastrowid
			details['section_offer_id'] = section_offer_id

		return ({"attributes": {
					    		"status_desc": "section_offer",
					    		"status": "success"
					    	},
					    	"responseList":details}), status.HTTP_200_OK


#----------------------Add-Section-Offer---------------------#


#----------------------Add-Section---------------------#

@name_space.route("/addSection")
class addSection(Resource):
	@api.expect(section_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		offer_section_name = details['offer_section_name']
		offer_section_type = details['offer_section_type']
		category_id = details['category_id']
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']
		section_status = 1

		if details and "sequence" in details:
			sequence = details['sequence']
		else:
			sequence = 1

		get_query = ("""SELECT `offer_section_name`,`offer_section_type`,`category_id`,`organisation_id`
			FROM `section_master` WHERE `offer_section_name` = %s and `organisation_id` = %s and `category_id` = %s""")

		getData = (offer_section_name,organisation_id,category_id)
		
		count_offer_section = cursor.execute(get_query,getData)

		if count_offer_section > 0:
			return ({"attributes": {
			    		"status_desc": "offer_section_details",
			    		"status": "error"
			    	},
			    	"responseList":"Already Exsits" }), status.HTTP_200_OK

		else:	

			insert_query = ("""INSERT INTO `section_master`(`offer_section_name`,`offer_section_type`,`category_id`,`organisation_id`,`sequence`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s)""")

			data = (offer_section_name,offer_section_type,category_id,organisation_id,sequence,section_status,last_update_id)
			cursor.execute(insert_query,data)

			details['section_id'] = cursor.lastrowid

			connection.commit()
			cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "offer_section_details",
		    		"status": "success"
		    	},
		    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Section---------------------#	

#----------------------Update-Section---------------------#

@name_space.route("/UpdateSection/<int:section_id>/<int:organisation_id>")
class UpdateSection(Resource):
	@api.expect(update_offer_section_postmodel)
	def put(self,section_id,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		offer_section_name = details['offer_section_name']
		offer_section_type = details['offer_section_type']
		category_id = details['category_id']

		get_query = ("""SELECT `offer_section_name`
			FROM `section_master` WHERE `section_id` = %s and `offer_section_name` = %s""")
		getData = (section_id,offer_section_name)		
		count_section = cursor.execute(get_query,getData)

		if count_section > 0:
			if details and "offer_section_name" in details:				
				update_query = ("""UPDATE `section_master` SET `offer_section_name` = %s
					WHERE `section_id` = %s """)
				update_data = (offer_section_name,section_id)
				cursor.execute(update_query,update_data)

			if details and "offer_section_type" in details:				
				update_query = ("""UPDATE `section_master` SET `offer_section_type` = %s
					WHERE `section_id` = %s """)
				update_data = (offer_section_type,section_id)
				cursor.execute(update_query,update_data)

			if details and "sequence" in details:
				sequence = details['sequence']				
				update_query = ("""UPDATE `section_master` SET `sequence` = %s
					WHERE `section_id` = %s """)
				update_data = (sequence,section_id)
				cursor.execute(update_query,update_data)

			if details and "category_id" in details:				
				update_query = ("""UPDATE `section_master` SET `category_id` = %s
					WHERE `section_id` = %s """)
				update_data = (category_id,section_id)
				cursor.execute(update_query,update_data)

		else:
			get_query = ("""SELECT `offer_section_name`
				FROM `section_master` WHERE `offer_section_name` = %s and `organisation_id` = %s and `category_id` = %s""")
			getData = (offer_section_name,organisation_id,category_id)		
			count_section = cursor.execute(get_query,getData)

			if count_section > 0:
				return ({"attributes": {
				    		"status_desc": "offer_section_details",
				    		"status": "error"
				    	},
				    	"responseList":"Type Already Exsits" }), status.HTTP_200_OK
			else:
				if details and "offer_section_name" in details:				
					update_query = ("""UPDATE `section_master` SET `offer_section_name` = %s
						WHERE `section_id` = %s """)
					update_data = (offer_section_name,section_id)
					cursor.execute(update_query,update_data)

				if details and "offer_section_type" in details:				
					update_query = ("""UPDATE `section_master` SET `offer_section_type` = %s
						WHERE `section_id` = %s """)
					update_data = (offer_section_type,section_id)
					cursor.execute(update_query,update_data)

				if details and "category_id" in details:				
					update_query = ("""UPDATE `section_master` SET `category_id` = %s
						WHERE `section_id` = %s """)
					update_data = (category_id,section_id)
					cursor.execute(update_query,update_data)

				if details and "sequence" in details:	
					sequence = details['sequence']				
					update_query = ("""UPDATE `section_master` SET `sequence` = %s
						WHERE `section_id` = %s """)
					update_data = (sequence,section_id)
					cursor.execute(update_query,update_data)				

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Offer Section",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Section---------------------#

#----------------------Update-Section---------------------#

@name_space.route("/UpdatOffereHomeSection/<int:section_id>")
class UpdatOffereHomeSection(Resource):
	@api.expect(update_offer_home_section_postmodel)
	def put(self,section_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		home_section = details['home_section']		
					
		update_query = ("""UPDATE `section_master` SET `home_section` = %s
					WHERE `section_id` = %s """)
		update_data = (home_section,section_id)
		cursor.execute(update_query,update_data)						

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Offer Section",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Section---------------------#

#----------------------Update-Section---------------------#

@name_space.route("/UpdatStatusSection/<int:section_id>")
class UpdatStatusSection(Resource):
	@api.expect(update_status_section_postmodel)
	def put(self,section_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		section_status = details['section_status']		
					
		update_query = ("""UPDATE `section_master` SET `is_show` = %s
					WHERE `section_id` = %s """)
		update_data = (section_status,section_id)
		cursor.execute(update_query,update_data)						

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Section status",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Section---------------------#

#----------------------Get-Section-Details---------------------#	
@name_space.route("/getSectionDetails/<int:section_id>")	
class getSectionDetails(Resource):
	def get(self,section_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `section_master` where `section_id` = %s""")
		get_data = (section_id)

		cursor.execute(get_query,get_data)

		section_data = cursor.fetchone()

		
		section_data['last_update_ts'] = str(section_data['last_update_ts'])				

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "section_details",
		    		"status": "success"
		    	},
		    	"responseList":section_data}), status.HTTP_200_OK

#----------------------Get-Section-Details---------------------#

#----------------------Get-Offer-Details---------------------#	
@name_space.route("/getOfferDetails/<int:offer_id>")	
class getOfferDetails(Resource):
	def get(self,offer_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `offer` where `offer_id` = %s""")
		get_data = (offer_id)

		cursor.execute(get_query,get_data)

		offer_data = cursor.fetchone()

		
		offer_data['last_update_ts'] = str(offer_data['last_update_ts'])				

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "offer_details",
		    		"status": "success"
		    	},
		    	"responseList":offer_data}), status.HTTP_200_OK

#----------------------Get-Offer-Details----------------------#


#----------------------Update-Offer---------------------#
@name_space.route("/updateOffer/<int:offer_id>")	
class updateOffer(Resource):
	@api.expect(offer_putmodel)
	def put(self,offer_id):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()	
		organisation_id = details['organisation_id']	
		
		if details and "offer_image" in details:
			offer_image = details['offer_image']
			update_query = ("""UPDATE `offer` SET `offer_image` = %s
				WHERE `offer_id` = %s """)
			update_data = (offer_image,offer_id)
			cursor.execute(update_query,update_data)

		if details and "coupon_code" in details:
			coupon_code = details['coupon_code']
			update_query = ("""UPDATE `offer` SET `coupon_code` = %s
				WHERE `offer_id` = %s """)
			update_data = (coupon_code,offer_id)
			cursor.execute(update_query,update_data)

		if details and "discount_percentage" in details:
			discount_percentage = details['discount_percentage']
			update_query = ("""UPDATE `offer` SET `discount_percentage` = %s
				WHERE `offer_id` = %s """)
			update_data = (discount_percentage,offer_id)
			cursor.execute(update_query,update_data)

		if details and "absolute_price" in details:			
			absolute_price = details['absolute_price']
			update_query = ("""UPDATE `offer` SET `absolute_price` = %s
				WHERE `offer_id` = %s """)
			update_data = (absolute_price,offer_id)
			cursor.execute(update_query,update_data)

		if details and "discount_value" in details:			
			discount_value = details['discount_value']
			update_query = ("""UPDATE `offer` SET `discount_value` = %s
				WHERE `offer_id` = %s """)
			update_data = (discount_value,offer_id)
			cursor.execute(update_query,update_data)

		if details and "product_offer_type" in details:		
			product_offer_type = details['product_offer_type']
			update_query = ("""UPDATE `offer` SET `product_offer_type` = %s
				WHERE `offer_id` = %s """)
			update_data = (product_offer_type,offer_id)
			cursor.execute(update_query,update_data)

		if details and "is_landing_page" in details:		
			is_landing_page = details['is_landing_page']
			update_query = ("""UPDATE `offer` SET `is_landing_page` = %s
				WHERE `offer_id` = %s """)
			update_data = (is_landing_page,offer_id)
			cursor.execute(update_query,update_data)	

		if details and "is_online" in details:		
			is_online = details['is_online']
			update_query = ("""UPDATE `offer` SET `is_online` = %s
				WHERE `offer_id` = %s """)
			update_data = (is_online,offer_id)
			cursor.execute(update_query,update_data)	

		if details and "instruction" in details:		
			instruction = details['instruction']
			update_query = ("""UPDATE `offer` SET `instruction` = %s
				WHERE `offer_id` = %s """)
			update_data = (instruction,offer_id)
			cursor.execute(update_query,update_data)

		if details and "is_show" in details:		
			is_show = details['is_show']
			update_query = ("""UPDATE `offer` SET `is_show` = %s
				WHERE `offer_id` = %s """)
			update_data = (is_show,offer_id)
			cursor.execute(update_query,update_data)

		if details and "validity_date" in details:		
			validity_date = details['validity_date']
			update_query = ("""UPDATE `offer` SET `validity_date` = %s
				WHERE `offer_id` = %s """)
			update_data = (validity_date,offer_id)
			cursor.execute(update_query,update_data)
			
		products = []
			
		if details and "product_id" in details:
			delete_offer_product_query = ("""DELETE FROM `product_offer_mapping` WHERE `offer_id` = %s""")
			del_offer_product_Data = (offer_id)		
			cursor.execute(delete_offer_product_query,del_offer_product_Data)

			product_ids = details.get('product_id',[])

			for product_id in product_ids:

				product_offer_mapping_query = (""" SELECT *
						FROM `product_offer_mapping` pom where  `organisation_id` = %s and `product_id` = %s""")
				product_offer_mapping_data = (organisation_id,product_id)
				count_product_offer_mapping_data = cursor.execute(product_offer_mapping_query,product_offer_mapping_data)

				if count_product_offer_mapping_data > 0:
					get_query = ("""SELECT `product_name`
							FROM `product` WHERE  `product_id` = %s """)

					getData = (product_id)
					cursor.execute(get_query,getData)
					product_data = cursor.fetchone()

					products.append(product_data['product_name'])

				else:				
					product_offer_status = 1
					insert_query = ("""INSERT INTO `product_offer_mapping`(`offer_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s)""")

					data = (offer_id,product_id,product_offer_status,organisation_id,organisation_id)
					cursor.execute(insert_query,data)

		if details and "image" in details:

			delete_offer_image_query = ("""DELETE FROM `offer_images` WHERE `offer_id` = %s""")
			del_offer_image_Data = (offer_id)		
			cursor.execute(delete_offer_image_query,del_offer_image_Data)

			images = details.get('image',[])

			for image in images:
				insert_query = ("""INSERT INTO `offer_images`(`offer_id`,`offer_image`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

				data = (offer_id,image,organisation_id,organisation_id)
				cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		if len(products) == 0:

			return ({"attributes": {
				    		"status_desc": "offer_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK
		else:
			exsits_products = ','.join(products)

			return ({"attributes": {
					    	"status_desc": "Product Already Exsits",
					    	"status": "error"
					},
					"responseList":{"product_name":exsits_products} }), status.HTTP_200_OK
		
#----------------------Update-Offer---------------------#

#----------------------Update-Offer-with-product-variant---------------------#
@name_space.route("/updateOfferWithProductVariant/<int:offer_id>")	
class updateOfferWithProductVariant(Resource):
	@api.expect(offer_productvariant_putmodel)
	def put(self,offer_id):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()	
		organisation_id = details['organisation_id']	
		
		if details and "offer_image" in details:
			offer_image = details['offer_image']
			update_query = ("""UPDATE `offer` SET `offer_image` = %s
				WHERE `offer_id` = %s """)
			update_data = (offer_image,offer_id)
			cursor.execute(update_query,update_data)

		if details and "coupon_code" in details:
			coupon_code = details['coupon_code']
			update_query = ("""UPDATE `offer` SET `coupon_code` = %s
				WHERE `offer_id` = %s """)
			update_data = (coupon_code,offer_id)
			cursor.execute(update_query,update_data)

		if details and "discount_percentage" in details:
			discount_percentage = details['discount_percentage']
			update_query = ("""UPDATE `offer` SET `discount_percentage` = %s
				WHERE `offer_id` = %s """)
			update_data = (discount_percentage,offer_id)
			cursor.execute(update_query,update_data)

		if details and "absolute_price" in details:			
			absolute_price = details['absolute_price']
			update_query = ("""UPDATE `offer` SET `absolute_price` = %s
				WHERE `offer_id` = %s """)
			update_data = (absolute_price,offer_id)
			cursor.execute(update_query,update_data)

		if details and "discount_value" in details:			
			discount_value = details['discount_value']
			update_query = ("""UPDATE `offer` SET `discount_value` = %s
				WHERE `offer_id` = %s """)
			update_data = (discount_value,offer_id)
			cursor.execute(update_query,update_data)

		if details and "product_offer_type" in details:		
			product_offer_type = details['product_offer_type']
			update_query = ("""UPDATE `offer` SET `product_offer_type` = %s
				WHERE `offer_id` = %s """)
			update_data = (product_offer_type,offer_id)
			cursor.execute(update_query,update_data)

		if details and "is_landing_page" in details:		
			is_landing_page = details['is_landing_page']
			update_query = ("""UPDATE `offer` SET `is_landing_page` = %s
				WHERE `offer_id` = %s """)
			update_data = (is_landing_page,offer_id)
			cursor.execute(update_query,update_data)	

		if details and "is_online" in details:		
			is_online = details['is_online']
			update_query = ("""UPDATE `offer` SET `is_online` = %s
				WHERE `offer_id` = %s """)
			update_data = (is_online,offer_id)
			cursor.execute(update_query,update_data)	

		if details and "instruction" in details:		
			instruction = details['instruction']
			update_query = ("""UPDATE `offer` SET `instruction` = %s
				WHERE `offer_id` = %s """)
			update_data = (instruction,offer_id)
			cursor.execute(update_query,update_data)

		if details and "is_show" in details:		
			is_show = details['is_show']
			update_query = ("""UPDATE `offer` SET `is_show` = %s
				WHERE `offer_id` = %s """)
			update_data = (is_show,offer_id)
			cursor.execute(update_query,update_data)

		if details and "validity_date" in details:		
			validity_date = details['validity_date']
			update_query = ("""UPDATE `offer` SET `validity_date` = %s
				WHERE `offer_id` = %s """)
			update_data = (validity_date,offer_id)
			cursor.execute(update_query,update_data)
			

		if details and "product_meta_id" in details:
			delete_offer_product_meta_query = ("""DELETE FROM `product_meta_offer_mapping` WHERE `offer_id` = %s""")
			del_offer_product_meta_Data = (offer_id)		
			cursor.execute(delete_offer_product_meta_query,del_offer_product_meta_Data)

			product_meta_ids = details.get('product_meta_id',[])

			for product_meta_id in product_meta_ids:

				get_product_id_query = ("""SELECT * FROM `product_meta` where `product_meta_id` = %s""")
				get_product_id_data = (product_meta_id)
				cursor.execute(get_product_id_query,get_product_id_data)
				product_id_data = cursor.fetchone()

				product_meta_offer_mapping_query = (""" SELECT *
						FROM `product_meta_offer_mapping` pom where  `organisation_id` = %s and `product_meta_id` = %s""")
				product_meta_offer_mapping_data = (organisation_id,product_meta_id)
				count_product_meta_offer_mapping_data = cursor.execute(product_meta_offer_mapping_query,product_meta_offer_mapping_data)

				if count_product_meta_offer_mapping_data > 0:
					get_query = ("""SELECT `product_name`
							FROM `product` WHERE  `product_id` = %s """)

					getData = (product_id_data['product_id'])
					cursor.execute(get_query,getData)
					product_data = cursor.fetchone()

					return ({"attributes": {
					    	"status_desc": "Product Already Exsits",
					    	"status": "success"
					},
					"responseList":{"product_name":product_data['product_name']} }), status.HTTP_200_OK

				else:				
					product_offer_status = 1
					
					insert_query = ("""INSERT INTO `product_meta_offer_mapping`(`offer_id`,`product_id`,`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s,%s,%s)""")

					data = (offer_id,product_id_data['product_id'],product_meta_id,product_offer_status,organisation_id,organisation_id)
					cursor.execute(insert_query,data)

		if details and "image" in details:

			delete_offer_image_query = ("""DELETE FROM `offer_images` WHERE `offer_id` = %s""")
			del_offer_image_Data = (offer_id)		
			cursor.execute(delete_offer_image_query,del_offer_image_Data)

			images = details.get('image',[])

			for image in images:
				insert_query = ("""INSERT INTO `offer_images`(`offer_id`,`offer_image`,`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s)""")

				data = (offer_id,image,organisation_id,organisation_id)
				cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "offer_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK	

#----------------------Update-Offer-with-product-variant---------------------#

#----------------------Delete-Offer---------------------#	
@name_space.route("/deleteOffer/<int:offer_id>")	
class deleteOffer(Resource):
	def delete(self,offer_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		update_query = ("""UPDATE `offer` SET `status` = 0
				WHERE `offer_id` = %s """)
		update_data = (offer_id)
		cursor.execute(update_query,update_data)

		delete_offer_product_query = ("""DELETE FROM `product_offer_mapping` WHERE `offer_id` = %s""")
		del_offer_product_Data = (offer_id)		
		cursor.execute(delete_offer_product_query,del_offer_product_Data)

		connection.commit()
		cursor.close()


		return ({"attributes": {"status_desc": "delete_Offer",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Offer---------------------#

#----------------------Delete-Offer---------------------#	
@name_space.route("/deleteOfferVariant/<int:offer_id>")	
class deleteOfferVariant(Resource):
	def delete(self,offer_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		update_query = ("""UPDATE `offer` SET `status` = 0
				WHERE `offer_id` = %s """)
		update_data = (offer_id)
		cursor.execute(update_query,update_data)

		delete_offer_product_query = ("""DELETE FROM `product_meta_offer_mapping` WHERE `offer_id` = %s""")
		del_offer_product_Data = (offer_id)		
		cursor.execute(delete_offer_product_query,del_offer_product_Data)

		connection.commit()
		cursor.close()


		return ({"attributes": {"status_desc": "delete_Offer",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Offer---------------------#

#----------------------Add-Product-Offer---------------------#
@name_space.route("/addProductOffer")	
class addProductOffer(Resource):
	@api.expect(product_offer_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()


		offer_id = details['offer_id']
		product_ids = details.get('product_id',[])		
		product_offer_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		for product_id in product_ids:

			get_query = ("""SELECT *
			FROM `product_offer_mapping` where `product_id` = %s and `organisation_id` = %s""")
			get_data = (product_id,organisation_id)

			count_product_offer = cursor.execute(get_query,get_data)

			if count_product_offer > 0:
				product_offer_data = cursor.fetchone()
				details['product_offer_id'] = product_offer_data['mapping_id']

				update_query = ("""UPDATE `product_offer_mapping` SET `offer_id` = %s
				WHERE `product_id` = %s """)
				update_data = (offer_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_offer_mapping`(`offer_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (offer_id,product_id,product_offer_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)		

				product_offer_id = cursor.lastrowid
				details['product_offer_id'] = product_offer_id

		connection.commit()
		cursor.close()


		return ({"attributes": {
				    		"status_desc": "product_offer_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK
#----------------------Add-Product-Offer---------------------#

#----------------------Add-Product-Brand---------------------#
@name_space.route("/addProductBrand")	
class addProductBrand(Resource):
	@api.expect(product_brand_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()


		brand_id = details['brand_id']
		product_ids = details.get('product_id',[])		
		product_offer_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		for product_id in product_ids:

			get_query = ("""SELECT *
			FROM `product_brand_mapping` where `product_id` = %s and `organisation_id` = %s""")
			get_data = (product_id,organisation_id)

			count_product_brand = cursor.execute(get_query,get_data)

			if count_product_brand > 0:
				product_brand_data = cursor.fetchone()
				details['product_brand_id'] = product_brand_data['mapping_id']

				update_query = ("""UPDATE `product_brand_mapping` SET `brand_id` = %s
				WHERE `product_id` = %s and `organisation_id` = %s""")
				update_data = (brand_id,product_id,organisation_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_brand_mapping`(`brand_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (brand_id,product_id,product_offer_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)		

				product_offer_id = cursor.lastrowid
				details['product_brand_id'] = product_offer_id

		connection.commit()
		cursor.close()


		return ({"attributes": {
				    		"status_desc": "product_brand_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK
#----------------------Add-Product-Brand---------------------#

#----------------------Add-Product-Category---------------------#
@name_space.route("/addProductCategory")	
class addProductCategory(Resource):
	@api.expect(product_category_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()


		category_id = details['category_id']
		product_ids = details.get('product_id',[])		
		product_offer_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		for product_id in product_ids:

			get_query = ("""SELECT *
			FROM `product_category_mapping` where `product_id` = %s and `organisation_id` = %s""")
			get_data = (product_id,organisation_id)

			count_product_category = cursor.execute(get_query,get_data)

			if count_product_category > 0:
				product_category_data = cursor.fetchone()
				details['product_category_id'] = product_category_data['mapping_id']

				update_query = ("""UPDATE `product_category_mapping` SET `category_id` = %s
				WHERE `product_id` = %s and `organisation_id` = %s""")
				update_data = (category_id,product_id,organisation_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_category_mapping`(`category_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (category_id,product_id,product_offer_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)		

				product_category_id = cursor.lastrowid
				details['product_category_id'] = product_category_id

		connection.commit()
		cursor.close()


		return ({"attributes": {
				    		"status_desc": "product_brand_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK
#----------------------Add-Product-Category---------------------#


#----------------------Product-Offer-List---------------------#
@name_space.route("/getProductOfferList/<int:organisation_id>")	
class getProductOfferList(Resource):
	def get(self,organisation_id):
		
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT o.`offer_id`,o.`offer_image`,o.`coupon_code`,p.`product_name`
			FROM `offer` o
			INNER JOIN `product_offer_mapping` pom ON pom.`offer_id` = o.`offer_id` 
			INNER JOIN `product` p ON p.`product_id` = pom.`product_id`
			where o.`organisation_id` = %s""")
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		cursor.execute(get_query,organisation_id)

		product_offer_data = cursor.fetchall()		

		connection.commit()
		cursor.close()    
	   		
		return ({"attributes": {
		    		"status_desc": "product_offer_details",
		    		"status": "success"
		    	},
		    	"responseList":product_offer_data}), status.HTTP_200_OK

#----------------------Product-Offer-List---------------------#

#----------------------Delete-Product-Offer---------------------#	
@name_space.route("/deleteProductOffer/<int:product_id>/<int:offer_id>")	
class deleteProductOffer(Resource):
	def delete(self,product_id,offer_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_offer_mapping` WHERE `product_id` = %s and `offer_id` = %s""")
		delData = (product_id,offer_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_product_offer",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Product-Offer---------------------#

#----------------------Delete-Product-Brand---------------------#	
@name_space.route("/deleteProductBrand/<int:product_id>/<int:brand_id>")	
class deleteProductOffer(Resource):
	def delete(self,product_id,brand_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_brand_mapping` WHERE `product_id` = %s and `brand_id` = %s""")
		delData = (product_id,brand_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_product_brand",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Product-Brand---------------------#

#----------------------Delete-Product-Category---------------------#	
@name_space.route("/deleteProductCategory/<int:product_id>/<int:category_id>")	
class deleteProductOffer(Resource):
	def delete(self,product_id,category_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_category_mapping` WHERE `product_id` = %s and `category_id` = %s""")
		delData = (product_id,category_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_product_category",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Product-Category---------------------#

#----------------------Delete-Product-NewArrival-Mapping---------------------#	
@name_space.route("/deleteProductNewArrivale/<int:product_id>/<int:new_arrival_id>")	
class deleteProductNewArrivale(Resource):
	def delete(self,product_id,new_arrival_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_new_arrival_mapping` WHERE `product_id` = %s and `new_arrival_id` = %s """)
		delData = (product_id,new_arrival_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_product_NewArrival",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Product-NewArrival-Mapping---------------------#

#----------------------Add-New-Arrival---------------------#
@name_space.route("/addNewArrival")	
class addNewArrival(Resource):
	@api.expect(new_arrival_postmodel)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		
		new_arrival_image = details['new_arrival_image']
		product_id = details['product_id']
		new_arrival_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		image_type = details['image_type']
		language =  details['language']

		insert_query = ("""INSERT INTO `new_arrival`(`new_arrival_image`,`status`,`image_type`,`organisation_id`,`language`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

		data = (new_arrival_image,new_arrival_status,image_type,organisation_id,language,last_update_id)
		cursor.execute(insert_query,data)

		new_arrival_id = cursor.lastrowid

		insert_mapping_query = ("""INSERT INTO `product_new_arrival_mapping`(`new_arrival_id`,`product_id`,`status`,`organisation_id`,`language`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

		mappig_data = (new_arrival_id,product_id,new_arrival_status,organisation_id,language,last_update_id)
		cursor.execute(insert_mapping_query,mappig_data)

		connection.commit()
		cursor.close()

		new_arrival_id = cursor.lastrowid
		details['new_arrival_id'] = new_arrival_id

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "new_arrival_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK
#----------------------Add-New-Arrivale---------------------#

#----------------------Get-New-Arrival-List---------------------#	
@name_space.route("/getNewArrivalList/<int:organisation_id>")	
class getNewArrivalList(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT na.`new_arrival_id`,na.`new_arrival_image`,p.`product_name`,na.`image_type`,na.`language`
			FROM `new_arrival` na
			INNER JOIN `product_new_arrival_mapping` nam ON nam.`new_arrival_id` = na.`new_arrival_id` 
			INNER JOIN `product` p ON p.`product_id` = nam.`product_id`
			where na.`organisation_id` = %s""")
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		new_arrival_data = cursor.fetchall()		

		connection.commit()
		cursor.close()	
				
		return ({"attributes": {
		    		"status_desc": "new_arrival_details",
		    		"status": "success"
		    	},
		    	"responseList":new_arrival_data}), status.HTTP_200_OK

#----------------------Get-New-Arrival-List---------------------#

#----------------------Get-Category-Mapping-List---------------------#	
@name_space.route("/getCategoryMappingList/<int:organisation_id>")	
class getCategoryMappingList(Resource):
	def get(self,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT cwcm.`mapping_id`,mkvm.`meta_key` as category_name,mkvma.`meta_key_value`
			FROM `category_with_category_mapping` cwcm
			INNER JOIN `meta_key_master` mkvm ON mkvm.`meta_key_id` = cwcm.`category_id` 
			INNER JOIN `meta_key_value_master` mkvma ON mkvma.`meta_key_value_id` = cwcm.`meta_key_value_id`
			where cwcm.`organisation_id` = %s""")
		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		category_mapping_data = cursor.fetchall()		

		connection.commit()
		cursor.close()	
				
		return ({"attributes": {
		    		"status_desc": "category_mapping_details",
		    		"status": "success"
		    	},
		    	"responseList":category_mapping_data}), status.HTTP_200_OK

#----------------------Get-Category-Mapping-List---------------------#

#----------------------Get-ProductList-By-Category-Mapping---------------------#	
@name_space.route("/getProductListByCategoryMapping/<int:organisation_id>/<int:category_id>/<int:product_id>")	
class getProductListByCategoryMapping(Resource):
	def get(self,organisation_id,category_id,product_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_id`,p.`product_name` 
			FROM `category_with_category_mapping` cm			
			INNER JOIN `product_category_mapping` pcm ON pcm.`category_id` = cm.`meta_key_value_id`
			INNER JOIN `product` p ON p.`product_id` = pcm.`product_id`
			INNER JOIN `product_organisation_mapping` pom ON pom.`product_id` = pcm.`product_id`
			where pom.`organisation_id` = %s and cm.`category_id` = %s""")
		get_data = (organisation_id,category_id)
		cursor.execute(get_query,get_data)

		product_data = cursor.fetchall()

		for key,data in enumerate(product_data):
			get_sugested_product_quey = ("""SELECT suggested_product_id 
				FROM `suggested_product_mapping`
				where `product_id` = %s and `suggested_product_id` = %s and `suggestion_type` = 2 and `organisation_id` = %s
				""")
			get_suggested_product_data = (product_id,data['product_id'],organisation_id)
			count_suggested_product = cursor.execute(get_sugested_product_quey,get_suggested_product_data)

			if count_suggested_product > 0:
				product_data[key]['is_accessories'] = 1
			else:
				product_data[key]['is_accessories'] = 0

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "product_data",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK


#----------------------Get-ProductList-By-Category-Mapping---------------------#	

#----------------------Add-Suggested-Accessories--------------------#
@name_space.route("/addSuggestedAccessories")	
class addSuggestedAccessories(Resource):
	@api.expect(suggested_accessories_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		product_id = details['product_id']
		suggested_product_id = details['suggested_product_id']
		suggestion_type = details['suggestion_type']
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']

		get_query = ("""SELECT `suggested_product_id`
			FROM `suggested_product_mapping` 
			WHERE  `product_id` = %s and `suggested_product_id` = %s and `suggestion_type` = %s and `organisation_id` = %s""")

		getData = (product_id,suggested_product_id,suggestion_type,organisation_id)
		
		count_product = cursor.execute(get_query,getData)

		if count_product > 0:

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "Suggested Accessories",
			    		"status": "error"
			    	},
			    	"responseList":"Already Exsits" }), status.HTTP_200_OK

		else:

			insert_query = ("""INSERT INTO `suggested_product_mapping`(`product_id`,`suggested_product_id`,`suggestion_type`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

			data = (product_id,suggested_product_id,suggestion_type,organisation_id,last_update_id)
			cursor.execute(insert_query,data)		

			mapping_id = cursor.lastrowid
			details['mapping_id'] = mapping_id

		return ({"attributes": {
		    		"status_desc": "Suggested Accessories",
		    		"status": "success"
		    	},
		    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Suggested-Accessories--------------------#

#----------------------Delete-Suggested-Accessories---------------------#

@name_space.route("/deleteSuggestedAccessories/<int:product_id>/<int:suggested_product_id>/<int:organisation_id>/<int:suggestion_type>")
class deleteSuggestedAccessories(Resource):
	def delete(self, product_id,suggested_product_id,organisation_id,suggestion_type):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `suggested_product_mapping` WHERE 
			`product_id` = %s and `suggested_product_id` = %s and `organisation_id` = %s and `suggestion_type` = %s""")
		delData = (product_id,suggested_product_id,organisation_id,suggestion_type)		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Suggested Accessories",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Suggested-Accessories---------------------#

#----------------------save-category-mapping---------------------#

@name_space.route("/saveCategoryMapping")
class saveCategoryMapping(Resource):
	@api.expect(category_mapping_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		category_id = details['category_id']
		meta_key_value_id = details['meta_key_value_id']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_query = ("""SELECT `category_id`,`meta_key_value_id`
			FROM `category_with_category_mapping` WHERE `category_id` = %s and `meta_key_value_id` = %s and `organisation_id` = %s""")

		getData = (category_id,meta_key_value_id,organisation_id)
		
		count_meta_key = cursor.execute(get_query,getData)

		if count_meta_key > 0:
			return ({"attributes": {
			    		"status_desc": "meta_key_details",
			    		"status": "error"
			    	},
			    	"responseList":"Already Exsits" }), status.HTTP_200_OK

		else:	

			insert_query = ("""INSERT INTO `category_with_category_mapping`(`category_id`,`meta_key_value_id`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")

			data = (category_id,meta_key_value_id,organisation_id,last_update_id)
			cursor.execute(insert_query,data)

			details['meta_key_id'] = cursor.lastrowid

			connection.commit()
			cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "Category Mapping",
		    		"status": "success"
		    	},
		    	"responseList":details}), status.HTTP_200_OK

#----------------------save-category-mapping---------------------#	



#----------------------delete-category-mapping---------------------#
@name_space.route("/deleteCategoryMapping/<int:mapping_id>")
class deleteCategoryMapping(Resource):
	def delete(self, mapping_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		delete_mapping = ("""DELETE FROM `category_with_category_mapping` WHERE `mapping_id` = %s """)
		delData = (mapping_id)
		
		cursor.execute(delete_mapping,delData)

		return ({"attributes": {"status_desc": "Delete Category Mapping",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------delete-category-mapping---------------------#

#----------------------Get-New-Arrival-Details---------------------#	
@name_space.route("/getNewArrivalDetails/<int:new_arrival_id>")	
class getNewArrivalDetails(Resource):
	def get(self,new_arrival_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `new_arrival` where `new_arrival_id` = %s""")
		get_data = (new_arrival_id)
		cursor.execute(get_query,get_data)

		new_arrival_data = cursor.fetchone()
					
		new_arrival_data['last_update_ts'] = str(new_arrival_data['last_update_ts'])	

		connection.commit()
		cursor.close()	
				
		return ({"attributes": {
		    		"status_desc": "new_arrival_details",
		    		"status": "success"
		    	},
		    	"responseList":new_arrival_data}), status.HTTP_200_OK

#----------------------Get-New-Arrival-Details---------------------#	

#----------------------Update-NewArrival---------------------#
@name_space.route("/updateNewArrival/<int:new_arrival_id>")	
class updateNewArrivale(Resource):
	@api.expect(new_arrival_postmodel)
	def put(self,new_arrival_id):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		now = datetime.now()
		date_of_update = now.strftime("%Y-%m-%d %H:%M:%S")
		
		if details and "new_arrival_image" in details:
			new_arrival_image = details['new_arrival_image']
			update_query = ("""UPDATE `new_arrival` SET `new_arrival_image` = %s , `date_of_update` = %s
				WHERE `new_arrival_id` = %s """)
			update_data = (new_arrival_image,date_of_update,new_arrival_id)
			cursor.execute(update_query,update_data)

		if details and "discount_percentage" in details:
			discount_percentage = details['discount_percentage']
			update_query = ("""UPDATE `new_arrival` SET `discount_percentage` = %s , `date_of_update` = %s
				WHERE `new_arrival_id` = %s """)
			update_data = (discount_percentage,date_of_update,new_arrival_id)
			cursor.execute(update_query,update_data)


		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "new_arrivale_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK	
#----------------------Update-NewArrival---------------------#

#----------------------Delete-NewArrival---------------------#	
@name_space.route("/deleteNewArrivale/<int:new_arrival_id>")	
class deleteNewArrivale(Resource):
	def delete(self,new_arrival_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `new_arrival` WHERE `new_arrival_id` = %s """)
		delData = (new_arrival_id)
		
		cursor.execute(delete_query,delData)

		delete_mapping_query = ("""DELETE FROM `product_new_arrival_mapping` WHERE `new_arrival_id` = %s """)		
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_NewArrival",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-NewArrival---------------------#

#----------------------Add-Product-New-Arrival---------------------#
@name_space.route("/addProductnewArrival")	
class addProductnewArrival(Resource):
	@api.expect(product_new_arrival_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()


		new_arrival_id = details['new_arrival_id']
		product_ids = details.get('product_id',[])		
		product_offer_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		for product_id in product_ids:

			get_query = ("""SELECT *
			FROM `product_new_arrival_mapping` where `product_id` = %s""")
			get_data = (product_id)

			count_product_new_arrival = cursor.execute(get_query,get_data)

			if count_product_new_arrival > 0:
				product_new_arrival_data = cursor.fetchone()
				details['product_new_arrival_id'] = product_new_arrival_data['mapping_id']

				update_query = ("""UPDATE `product_new_arrival_mapping` SET `new_arrival_id` = %s
				WHERE `product_id` = %s """)
				update_data = (new_arrival_id,product_id)
				cursor.execute(update_query,update_data)

			else:
				insert_query = ("""INSERT INTO `product_new_arrival_mapping`(`new_arrival_id`,`product_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s)""")

				data = (new_arrival_id,product_id,product_offer_status,organisation_id,last_update_id)
				cursor.execute(insert_query,data)		

				product_offer_id = cursor.lastrowid
				details['product_new_arrival_id'] = product_new_arrival_id

		connection.commit()
		cursor.close()


		return ({"attributes": {
				    		"status_desc": "product_offer_details",
				    		"status": "success"
				    	},
				    	"responseList":details}), status.HTTP_200_OK
#----------------------Add-Product-New-Arrival---------------------#

#----------------------Product-NewArrivale-list---------------------#
@name_space.route("/getProductNewArrivalelist")	
class getProductNewArrivalelist(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `product_new_arrival_mapping` """)

		cursor.execute(get_query)

		product_new_arrival_data = cursor.fetchall()

		for key,data in enumerate(product_new_arrival_data):
			product_new_arrival_data[key]['Last_update_TS'] = str(data['Last_update_TS'])

			get_offer_query = ("""SELECT *
				FROM `new_arrival` where new_arrival_id = %s""")
			get_offer_data = (data['new_arrival_id'])
			cursor.execute(get_offer_query,get_offer_data)

			offer_data = cursor.fetchone()

			product_new_arrival_data[key]['new_arrival_image'] = offer_data['new_arrival_image']
			product_new_arrival_data[key]['discount_percentage'] = offer_data['discount_percentage']	

		connection.commit()
		cursor.close()  

		return ({"attributes": {
		    		"status_desc": "poduct_new_arrivale_details",
		    		"status": "success"
		    	},
		    	"responseList":product_new_arrival_data}), status.HTTP_200_OK

#----------------------Product-NewArrivale-list---------------------#



#----------------------Add-Product-Top-selling---------------------#
@name_space.route("/addProductTopSelling")	
class addProductTopSelling(Resource):
	@api.expect(product_top_selling_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		
		product_meta_id = details['product_meta_id']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		top_selling_product_status = 1

		get_query = ("""SELECT `product_meta_id`
			FROM `product_top_selling_mapping` WHERE  `product_meta_id` = %s""")

		getData = (product_meta_id)
		
		count_product = cursor.execute(get_query,getData)

		if count_product > 0:

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "product_top_selling",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

		else:

			insert_query = ("""INSERT INTO `product_top_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

			data = (product_meta_id,top_selling_product_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)		

			product_top_selling_id = cursor.lastrowid
			details['product_top_selling_id'] = product_top_selling_id

			connection.commit()
			cursor.close()

			return ({"attributes": {
					    		"status_desc": "product_top_selling",
					    		"status": "success"
					    	},
					    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Product-Top-selling---------------------#

#----------------------Add-Product-Best-selling---------------------#
@name_space.route("/addProductBestSelling")	
class addProductBestSelling(Resource):
	@api.expect(product_best_selling_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		
		product_meta_id = details['product_meta_id']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		best_selling_product_status = 1

		get_query = ("""SELECT `product_meta_id`
			FROM `product_best_selling_mapping` WHERE  `product_meta_id` = %s""")

		getData = (product_meta_id)
		
		count_product = cursor.execute(get_query,getData)

		if count_product > 0:

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "product_best_selling",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

		else:

			insert_query = ("""INSERT INTO `product_best_selling_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

			data = (product_meta_id,best_selling_product_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)		

			product_best_selling_id = cursor.lastrowid
			details['product_best_selling_id'] = product_best_selling_id

			connection.commit()
			cursor.close()

			return ({"attributes": {
					    		"status_desc": "product_top_selling",
					    		"status": "success"
					    	},
					    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Product-Best-selling---------------------#

#----------------------Product-Top-Selling-List---------------------#
@name_space.route("/getProductTopSellingList")	
class getProductTopSellingList(Resource):
	def get(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `product_top_selling_mapping` """)

		cursor.execute(get_query)

		product_top_selling_data = cursor.fetchall()

		for key,data in enumerate(product_top_selling_data):
			product_top_selling_data[key]['Last_update_TS'] = str(data['Last_update_TS'])

			get_product_query = ("""SELECT *
				FROM `product` where product_id = %s""")
			get_product_data = (data['product_id'])
			cursor.execute(get_product_query,get_product_data)

			offer_data = cursor.fetchone()

			product_top_selling_data[key]['product_name'] = offer_data['product_name']
			product_top_selling_data[key]['price'] = offer_data['price']	

		connection.commit()
		cursor.close()  

		return ({"attributes": {
		    		"status_desc": "product_top_selling_detail",
		    		"status": "success"
		    	},
		    	"responseList":product_top_selling_data}), status.HTTP_200_OK

#----------------------Product-Top-Selling-List---------------------#

#----------------------Delete-Product-Top-Selling---------------------#	
@name_space.route("/deleteProductTopSelling/<int:product_meta_id>")	
class deleteProductTopSelling(Resource):
	def delete(self,product_meta_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_top_selling_mapping` WHERE `product_meta_id` = %s """)
		delData = (product_meta_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_product_top_selling",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Product-Top-Selling---------------------#

#----------------------Add-Latest-Product---------------------#
@name_space.route("/addLatestProduct")	
class addLatestProduct(Resource):
	@api.expect(latest_product_postmodel)
	def post(self):	

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		
		product_meta_id = details['product_meta_id']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		latest_product_status = 1

		get_query = ("""SELECT `product_meta_id`
			FROM `latest_product_mapping` WHERE  `product_meta_id` = %s""")

		getData = (product_meta_id)
		
		count_product = cursor.execute(get_query,getData)

		if count_product > 0:

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "latest_product",
			    		"status": "error"
			    	},
			    	"responseList":"Product Already Exsits" }), status.HTTP_200_OK

		else:

			insert_query = ("""INSERT INTO `latest_product_mapping`(`product_meta_id`,`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s)""")

			data = (product_meta_id,latest_product_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)		

			mapping_id = cursor.lastrowid
			details['mapping_id'] = mapping_id

			connection.commit()
			cursor.close()

			return ({"attributes": {
					    		"status_desc": "latest_product",
					    		"status": "success"
					    	},
					    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Latest-Product---------------------#

#----------------------Delete-Latest-Product---------------------#	
@name_space.route("/deleteLatestProduct/<int:product_meta_id>")	
class deleteLatestProduct(Resource):
	def delete(self,product_meta_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `latest_product_mapping` WHERE `product_meta_id` = %s """)
		delData = (product_meta_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_latest_product",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Latest-Product---------------------#


#----------------------Delete-Best-Selling-Product---------------------#	
@name_space.route("/deleteBestSellingProduct/<int:product_meta_id>")	
class deleteBestSellingProduct(Resource):
	def delete(self,product_meta_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_query = ("""DELETE FROM `product_best_selling_mapping` WHERE `product_meta_id` = %s """)
		delData = (product_meta_id)
		
		cursor.execute(delete_query,delData)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "delete_best_selling_product",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Best-Selling-Product---------------------#

#-----------------------Retailer-List-With-Stock---------------------#

@name_space.route("/getRetailerListWithStock/<int:organisation_id>/<int:product_meta_id>")	
class getRetailerListWithStock(Resource):
	def get(self,organisation_id,product_meta_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_retailer_store_query = ("""SELECT rs.`retailer_store_id`,rs.`retailer_name`,rs.`city`
			FROM `retailer_store` rs			
			WHERE rs.`organisation_id` = %s""")

		get_retailer_data = (organisation_id)
		cursor.execute(get_retailer_store_query,get_retailer_data)

		retailer_store_data = cursor.fetchall()

		for key,data in enumerate(retailer_store_data):
			get_product_meta_store_query = ("""SELECT pi.`stock`
			FROM `product_inventory` pi			
			WHERE pi.`retailer_store_id` = %s and pi.`product_meta_id` = %s""")

			get_product_meta_store_data = (data['retailer_store_id'],product_meta_id)
			count = cursor.execute(get_product_meta_store_query,get_product_meta_store_data)

			if count >0: 
				retailer_store_stock_data = cursor.fetchone()
				retailer_store_data[key]['stock'] = retailer_store_stock_data['stock']
			else:
				retailer_store_data[key]['stock'] = 2				
				
		return ({"attributes": {
		    		"status_desc": "retailer_store_details",
		    		"status": "success"
		    	},
		    	"responseList":retailer_store_data}), status.HTTP_200_OK

#-----------------------Retailer-List-With-Stock---------------------#

#-----------------------Update-Stock---------------------#

@name_space.route("/updateStock")	
class updateStock(Resource):
	@api.expect(stock_putmodel)
	def put(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		retailer_store_id = details['retailer_store_id']
		stock = details['stock']
		product_meta_id = details['product_meta_id']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']
		product_meta_transaction_status = 1

		if stock == 1:
			get_product_inventory_query = ("""SELECT `product_meta_id`,`stock`
				FROM `product_inventory` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
			get_prodcut_inventory_Data = (product_meta_id,retailer_store_id,organisation_id)			
			count_product_inventory = cursor.execute(get_product_inventory_query,get_prodcut_inventory_Data)

			if count_product_inventory >0:
				course_update_query = ("""UPDATE `product_inventory` SET `stock` = %s
					WHERE `product_meta_id` = %s and retailer_store_id = %s and `organisation_id` = %s""")
				update_data = (stock,product_meta_id,retailer_store_id,organisation_id)
				cursor.execute(course_update_query,update_data)
			else:	
				insert_product_inventory_query = ("""INSERT INTO `product_inventory`(`product_meta_id`,`stock`,`retailer_store_id`,`status`,
					`organisation_id`,`last_update_id`) 
						VALUES(%s,%s,%s,%s,%s,%s)""")

				insert_product_inventory_data = (product_meta_id,stock,retailer_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				cursor.execute(insert_product_inventory_query,insert_product_inventory_data)
				product_inventory_id = cursor.lastrowid

			get_product_transaction_query = ("""SELECT `product_meta_id`,`previous_stock`,`updated_stock`
				FROM `product_transaction` WHERE  `product_meta_id` = %s and retailer_store_id = %s and organisation_id = %s""")
			get_prodcut_transaction_Data = (product_meta_id,retailer_store_id,organisation_id)		
			count_product_transaction = cursor.execute(get_product_transaction_query,get_prodcut_transaction_Data)
			


			if count_product_transaction > 0:
				product_transaction = cursor.fetchone();
				insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,`retailer_store_id`,
				`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s)""")

				insert_product_transaction_data = (product_meta_id,product_transaction['updated_stock'],stock,retailer_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				cursor.execute(insert_product_transaction_query,insert_product_transaction_data)	


			else:
				insert_product_transaction_query = ("""INSERT INTO `product_transaction`(`product_meta_id`,`previous_stock`,`updated_stock`,`retailer_store_id`,
				`status`,`organisation_id`,`last_update_id`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s)""")
				previous_stock = 0
				insert_product_transaction_data = (product_meta_id,previous_stock,stock,retailer_store_id,product_meta_transaction_status,organisation_id,last_update_id)
				cursor.execute(insert_product_transaction_query,insert_product_transaction_data)

		else:
			delete_product_inventory_query = ("""DELETE FROM `product_inventory` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
			delproductInventoryData = (product_meta_id,retailer_store_id,organisation_id)
		
			cursor.execute(delete_product_inventory_query,delproductInventoryData)

			delete_product_transaction_query = ("""DELETE FROM `product_transaction` WHERE  `product_meta_id` = %s and `retailer_store_id` = %s and `organisation_id` = %s""")
			cursor.execute(delete_product_transaction_query,delproductInventoryData)

		return ({"attributes": {"status_desc": "Update Stock",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#-----------------------Retailer-List-With-Stock---------------------#


#----------------------Order-List---------------------#

@name_space.route("/orderList/<int:brand_id>/<string:ostatus>/<string:start_date>/<string:end_date>/<int:organisation_id>")	
class orderList(Resource):
	def get(self,brand_id,ostatus,start_date,end_date,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`customer_product_json`,ipr.`last_update_ts`,
			a.`first_name`,a.`last_name`,a.`phoneno`,
			a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			WHERE  ipr.`organisation_id` = %s
			and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s
			and ipr.`status` = %s""")

		getData = (organisation_id,start_date,end_date,ostatus)
			
		cursor.execute(get_query,getData)

		order_data = cursor.fetchall()	

		new_order_data = []
		if brand_id == 0:

			for key,data in enumerate(order_data):
				order_data[key]['last_update_ts'] = str(data['last_update_ts'])
				customer_product_json = json.loads(data['customer_product_json'])
				customer_products = customer_product_json['customer_product']
				order_data[key]['customer_product'] = customer_products
				new_order_data = order_data
		else:
				
			for key,data in enumerate(order_data):
				order_data[key]['last_update_ts'] = str(data['last_update_ts'])
				customer_product_json = json.loads(data['customer_product_json'])
				customer_products = customer_product_json['customer_product']
				

				customer_product = json.dumps(customer_products)
				customer_product_s = json.loads(customer_product)

				get_pb_query = ("""SELECT `product_id`
						FROM `product_brand_mapping`
						WHERE  `brand_id` = %s""")

				getpbData = (brand_id)
				cursor.execute(get_pb_query,getpbData)
				pb_data = cursor.fetchall()

				b_ps = []

				for bkey,bdata in enumerate(pb_data):

					b_ps.append(bdata['product_id'])

				for pkey,pdata in enumerate(customer_product_s):
								
					for b_p in b_ps:
						if b_p == pdata['product_id']:
							order_data[key]['customer_product'] = customer_products						
							
			for nkey,ndata in enumerate(order_data):
				if "customer_product" in ndata:
					new_order_data.append(ndata)
				
						
		return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
				"responseList":new_order_data}), status.HTTP_200_OK	

#----------------------Order-List---------------------#

#----------------------Order-History---------------------#

@name_space.route("/orderHistoryWithCity/<int:brand_id>/<string:ostatus>/<string:start_date>/<string:end_date>/<int:organisation_id>/<string:city>")	
class orderHistoryWithCity(Resource):
	def get(self,brand_id,ostatus,start_date,end_date,organisation_id,city):

		connection = mysql_connection()
		cursor = connection.cursor()

		if ostatus == 'NA' and city == 'NA':
			get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
				a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
				FROM `instamojo_payment_request` ipr
				INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
				WHERE  ipr.`organisation_id` = %s
				and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s""")
			getData = (organisation_id,start_date,end_date)

		else:
			if city == 'NA' and ostatus != 'NA':
				print('hello')
				get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
					a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
					FROM `instamojo_payment_request` ipr
					INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
					WHERE  ipr.`organisation_id` = %s
					and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s
					and ipr.`status` = %s""")

				getData = (organisation_id,start_date,end_date,ostatus)
			elif  ostatus == 'NA' and city != 'NA':
				get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
					a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
					FROM `instamojo_payment_request` ipr
					INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
					WHERE  ipr.`organisation_id` = %s and a.`city` = %s
					and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s""")

				getData = (organisation_id,city,start_date,end_date)
			else:
				get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
					a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
					FROM `instamojo_payment_request` ipr
					INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
					WHERE  ipr.`organisation_id` = %s and a.`city` = %s
					and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s and ipr.`status` = %s""")

				getData = (organisation_id,city,start_date,end_date,ostatus)
			
		count = cursor.execute(get_query,getData)
		print(cursor._last_executed)

		new_order_data = []
		if count > 0:
			order_data = cursor.fetchall()

			for key,data in enumerate(order_data):
				product_status = "o"
				if brand_id == 0:
					customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
					pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
					FROM `order_product` op
					INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
					INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
					INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
					where op.`transaction_id` = %s and cpm.`product_status` = %s""")	

					customer_product_data = (data['transaction_id'],product_status)
				else:	
					customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
						pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
						FROM `order_product` op
						INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
						INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
						INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
						INNER JOIN `product_brand_mapping` pb ON pb.`product_id` = p.`product_id`
						where op.`transaction_id` = %s and pb.`organisation_id` = %s and cpm.`product_status` = %s and pb.`brand_id`=%s""")	

					customer_product_data = (data['transaction_id'],organisation_id,product_status,brand_id)

				count_customer_product = cursor.execute(customer_product_query,customer_product_data)

				if count_customer_product > 0:

					customer_product = cursor.fetchall()

					for tkey,tdata in enumerate(customer_product):			
						get_product_meta_image_quey = ("""SELECT `image` as `product_image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
						product_meta_image_data = (tdata['product_meta_id'])
						rows_count_image = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
						if rows_count_image > 0:
							product_meta_image = cursor.fetchone()
							customer_product[tkey]['product_image'] = product_meta_image['product_image']
						else:
							customer_product[tkey]['product_image'] = ""

						if 	tdata['meta_key_text'] :
							a_string = tdata['meta_key_text']
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

								customer_product[tkey]['met_key_value'] = met_key

						get_query_discount = ("""SELECT `discount`
												FROM `product_meta_discount_mapping` pdm
												INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
												WHERE `product_meta_id` = %s """)
						getdata_discount = (tdata['product_meta_id'])
						count_dicscount = cursor.execute(get_query_discount,getdata_discount)

						if count_dicscount > 0:
							product_meta_discount = cursor.fetchone()
							customer_product[tkey]['discount'] = product_meta_discount['discount']

							discount = (tdata['out_price']/100)*product_meta_discount['discount']
							actual_amount = tdata['out_price'] - discount
							customer_product[tkey]['after_discounted_price'] = round(actual_amount,2)

						else:
							customer_product[tkey]['discount'] = 0
							customer_product[tkey]['after_discounted_price'] = tdata['out_price']

						qty_quey = ("""SELECT `qty` 
							FROM `customer_product_mapping_qty` WHERE `customer_mapping_id` = %s""")
						qty_data = (tdata['mapping_id'])
						rows_count_qty = cursor.execute(qty_quey,qty_data)
						if rows_count_qty > 0:
							qty = cursor.fetchone()
							customer_product[tkey]['qty'] = qty['qty']
						else:
							customer_product[tkey]['qty'] = 0

						customer_product[tkey]['actual_price'] = qty['qty'] * tdata['out_price']	

					order_data[key]['customer_product'] = customer_product
					order_data[key]['last_update_ts'] = str(data['last_update_ts'])

			for nkey,ndata in enumerate(order_data):
				if "customer_product" in ndata:
					new_order_data.append(order_data[nkey])

			return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
					"responseList":new_order_data}), status.HTTP_200_OK

		else:

			return ({"attributes": {
			    		"status_desc": "order_history",
			    		"status": "success"
			    	},
			    	"responseList":[] }), status.HTTP_200_OK

#----------------------Order-History---------------------#

#----------------------Order-History-With-Retail-Store---------------------#

@name_space.route("/orderHistoryWithRetailStore/<int:brand_id>/<string:ostatus>/<string:start_date>/<string:end_date>/<int:organisation_id>/<int:retailer_store_id>")	
class orderHistoryWithRetailStore(Resource):
	def get(self,brand_id,ostatus,start_date,end_date,organisation_id,retailer_store_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		if ostatus == 'NA' and retailer_store_id == 0:
			get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
				a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
				FROM `instamojo_payment_request` ipr
				INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
				WHERE  ipr.`organisation_id` = %s
				and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s""")
			getData = (organisation_id,start_date,end_date)

		else:
			if retailer_store_id == 0 and ostatus != 'NA':
				print('hello')
				get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
					a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
					FROM `instamojo_payment_request` ipr
					INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
					WHERE  ipr.`organisation_id` = %s
					and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s
					and ipr.`status` = %s""")

				getData = (organisation_id,start_date,end_date,ostatus)
			elif  ostatus == 'NA' and retailer_store_id != 0:
				get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
					a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
					FROM `instamojo_payment_request` ipr
					INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
					INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id`
					WHERE  ipr.`organisation_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s
					and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s""")

				getData = (organisation_id,retailer_store_id,organisation_id,start_date,end_date)
			else:
				get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
					a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
					FROM `instamojo_payment_request` ipr
					INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
					INNER JOIN `user_retailer_mapping` urm ON urm.`user_id` = ipr.`user_id`
					WHERE  ipr.`organisation_id` = %s and urm.`retailer_store_id` = %s and urm.`organisation_id` = %s
					and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s and ipr.`status` = %s""")

				getData = (organisation_id,retailer_store_id,organisation_id,start_date,end_date,ostatus)
			
		count = cursor.execute(get_query,getData)
		print(cursor._last_executed)

		new_order_data = []
		if count > 0:
			order_data = cursor.fetchall()

			for key,data in enumerate(order_data):
				product_status = "o"
				if brand_id == 0:
					customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
					pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
					FROM `order_product` op
					INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
					INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
					INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
					where op.`transaction_id` = %s and cpm.`product_status` = %s""")	

					customer_product_data = (data['transaction_id'],product_status)
				else:	
					customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
						pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
						FROM `order_product` op
						INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
						INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
						INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
						INNER JOIN `product_brand_mapping` pb ON pb.`product_id` = p.`product_id`
						where op.`transaction_id` = %s and pb.`organisation_id` = %s and cpm.`product_status` = %s and pb.`brand_id`=%s""")	

					customer_product_data = (data['transaction_id'],organisation_id,product_status,brand_id)

				count_customer_product = cursor.execute(customer_product_query,customer_product_data)

				if count_customer_product > 0:

					customer_product = cursor.fetchall()

					for tkey,tdata in enumerate(customer_product):			
						get_product_meta_image_quey = ("""SELECT `image` as `product_image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
						product_meta_image_data = (tdata['product_meta_id'])
						rows_count_image = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
						if rows_count_image > 0:
							product_meta_image = cursor.fetchone()
							customer_product[tkey]['product_image'] = product_meta_image['product_image']
						else:
							customer_product[tkey]['product_image'] = ""

						if 	tdata['meta_key_text'] :
							a_string = tdata['meta_key_text']
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

								customer_product[tkey]['met_key_value'] = met_key

						get_query_discount = ("""SELECT `discount`
												FROM `product_meta_discount_mapping` pdm
												INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
												WHERE `product_meta_id` = %s """)
						getdata_discount = (tdata['product_meta_id'])
						count_dicscount = cursor.execute(get_query_discount,getdata_discount)

						if count_dicscount > 0:
							product_meta_discount = cursor.fetchone()
							customer_product[tkey]['discount'] = product_meta_discount['discount']

							discount = (tdata['out_price']/100)*product_meta_discount['discount']
							actual_amount = tdata['out_price'] - discount
							customer_product[tkey]['after_discounted_price'] = round(actual_amount,2)

						else:
							customer_product[tkey]['discount'] = 0
							customer_product[tkey]['after_discounted_price'] = tdata['out_price']

						qty_quey = ("""SELECT `qty` 
							FROM `customer_product_mapping_qty` WHERE `customer_mapping_id` = %s""")
						qty_data = (tdata['mapping_id'])
						rows_count_qty = cursor.execute(qty_quey,qty_data)
						if rows_count_qty > 0:
							qty = cursor.fetchone()
							customer_product[tkey]['qty'] = qty['qty']
						else:
							customer_product[tkey]['qty'] = 0

						customer_product[tkey]['actual_price'] = qty['qty'] * tdata['out_price']	

					order_data[key]['customer_product'] = customer_product
					order_data[key]['last_update_ts'] = str(data['last_update_ts'])

			for nkey,ndata in enumerate(order_data):
				if "customer_product" in ndata:
					new_order_data.append(order_data[nkey])

			for nnkey,nndata in enumerate(new_order_data):
				get_query_redeem = ("""SELECT `redeem_point`,`remarks`
												FROM `redeem_history` rh												
												WHERE `transaction_id` = %s and `organisation_id` = %s""")
				getdata_redeem = (nndata['transaction_id'],organisation_id)
				count_redeem = cursor.execute(get_query_redeem,getdata_redeem)

				if count_redeem > 0:
					redeem_data = cursor.fetchone()
					new_order_data[nnkey]['remarks'] = redeem_data['remarks']
					new_order_data[nnkey]['redeem_point'] = redeem_data['redeem_point']

				else:
					new_order_data[nnkey]['redeem_point'] = 0
					new_order_data[nnkey]['remarks'] = ""

			return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
					"responseList":new_order_data}), status.HTTP_200_OK

		else:

			return ({"attributes": {
			    		"status_desc": "order_history",
			    		"status": "success"
			    	},
			    	"responseList":[] }), status.HTTP_200_OK

#----------------------Order-History-With-Retail-Store---------------------#

#----------------------Order-History---------------------#

@name_space.route("/orderHistory/<int:brand_id>/<string:ostatus>/<string:start_date>/<string:end_date>/<int:organisation_id>")	
class orderHistory(Resource):
	def get(self,brand_id,ostatus,start_date,end_date,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		if ostatus == 'NA':
			get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
				a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
				FROM `instamojo_payment_request` ipr
				INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
				WHERE  ipr.`organisation_id` = %s
				and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s""")
			getData = (organisation_id,start_date,end_date)

		else:			
			get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,ipr.`order_payment_status`,ipr.`delivery_option`,
					a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
					FROM `instamojo_payment_request` ipr
					INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
					WHERE  ipr.`organisation_id` = %s
					and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s and ipr.`status` = %s""")

			getData = (organisation_id,start_date,end_date,ostatus)
			
		count = cursor.execute(get_query,getData)
		print(cursor._last_executed)

		new_order_data = []
		if count > 0:
			order_data = cursor.fetchall()

			for key,data in enumerate(order_data):
				product_status = "o"
				if brand_id == 0:
					customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
					pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
					FROM `order_product` op
					INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
					INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
					INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
					where op.`transaction_id` = %s and cpm.`product_status` = %s""")	

					customer_product_data = (data['transaction_id'],product_status)
				else:	
					customer_product_query =  ("""SELECT cpm.`mapping_id`,p.`product_id`,p.`product_name`,pm.`product_meta_id`,
						pm.`out_price`,pm.`product_meta_code`,pm.`meta_key_text`
						FROM `order_product` op
						INNER JOIN `customer_product_mapping` cpm ON cpm.`mapping_id` = op.`customer_mapping_id` 
						INNER JOIN `product_meta` pm ON cpm.`product_meta_id` = pm.`product_meta_id`
						INNER JOIN `product` p ON pm.`product_id` = p.`product_id`
						INNER JOIN `product_brand_mapping` pb ON pb.`product_id` = p.`product_id`
						where op.`transaction_id` = %s and pb.`organisation_id` = %s and cpm.`product_status` = %s and pb.`brand_id`=%s""")	

					customer_product_data = (data['transaction_id'],organisation_id,product_status,brand_id)

				count_customer_product = cursor.execute(customer_product_query,customer_product_data)

				if count_customer_product > 0:

					customer_product = cursor.fetchall()

					for tkey,tdata in enumerate(customer_product):			
						get_product_meta_image_quey = ("""SELECT `image` as `product_image`
							FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
						product_meta_image_data = (tdata['product_meta_id'])
						rows_count_image = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
						if rows_count_image > 0:
							product_meta_image = cursor.fetchone()
							customer_product[tkey]['product_image'] = product_meta_image['product_image']
						else:
							customer_product[tkey]['product_image'] = ""

						if 	tdata['meta_key_text'] :
							a_string = tdata['meta_key_text']
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

								customer_product[tkey]['met_key_value'] = met_key

						get_query_discount = ("""SELECT `discount`
												FROM `product_meta_discount_mapping` pdm
												INNER JOIN `discount_master` dm ON dm.`discount_id` = pdm.`discount_id`
												WHERE `product_meta_id` = %s """)
						getdata_discount = (tdata['product_meta_id'])
						count_dicscount = cursor.execute(get_query_discount,getdata_discount)

						if count_dicscount > 0:
							product_meta_discount = cursor.fetchone()
							customer_product[tkey]['discount'] = product_meta_discount['discount']

							discount = (tdata['out_price']/100)*product_meta_discount['discount']
							actual_amount = tdata['out_price'] - discount
							customer_product[tkey]['after_discounted_price'] = round(actual_amount,2)

						else:
							customer_product[tkey]['discount'] = 0
							customer_product[tkey]['after_discounted_price'] = tdata['out_price']

						qty_quey = ("""SELECT `qty` 
							FROM `customer_product_mapping_qty` WHERE `customer_mapping_id` = %s""")
						qty_data = (tdata['mapping_id'])
						rows_count_qty = cursor.execute(qty_quey,qty_data)
						if rows_count_qty > 0:
							qty = cursor.fetchone()
							customer_product[tkey]['qty'] = qty['qty']
						else:
							customer_product[tkey]['qty'] = 0

						customer_product[tkey]['actual_price'] = qty['qty'] * tdata['out_price']	

					order_data[key]['customer_product'] = customer_product
					order_data[key]['last_update_ts'] = str(data['last_update_ts'])

			for nkey,ndata in enumerate(order_data):
				if "customer_product" in ndata:
					new_order_data.append(order_data[nkey])

			return ({"attributes": {
					"status_desc": "order_history",
					"status": "success"
				},
					"responseList":new_order_data}), status.HTTP_200_OK

		else:

			return ({"attributes": {
			    		"status_desc": "order_history",
			    		"status": "success"
			    	},
			    	"responseList":[] }), status.HTTP_200_OK

#----------------------Order-History---------------------#

#----------------------Change-Order-Status---------------------#

@name_space.route("/changeOrderStatus/<int:transaction_id>")
class changeOrderStatus(Resource):
	@api.expect(changeorderstatus_putmodel)
	def put(self,transaction_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()
		order_status = details['order_status']

		update_query = ("""UPDATE `instamojo_payment_request` SET `status` = %s
				WHERE `transaction_id` = %s """)
		update_data = (order_status,transaction_id)
		cursor.execute(update_query,update_data)

		get_instamojo_payemnt_request_details_query = ("""SELECT *
								FROM `instamojo_payment_request` WHERE  `transaction_id` = %s""")
		get_instamojo_payemnt_request_details_data = (transaction_id)
		cursor.execute(get_instamojo_payemnt_request_details_query,get_instamojo_payemnt_request_details_data)

		instamojo_payment_data = cursor.fetchone()

		print(instamojo_payment_data)

		if details and "imageurl" in details:
			imageurl = details['imageurl']
		else:
			imageurl = ""

		if details and "retailer_remarks" in details:
			retailer_remarks = details['retailer_remarks']
		else:
			retailer_remarks = ""

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		orderHistoryUrl =  BASE_URL + "order_historydtls/EcommerceOrderHistory/OderHistoryDetails"
		payloadDataOrderHistory = {
						  "order_product_id": instamojo_payment_data['transaction_id'],
						  "imageurl": imageurl,
						  "retailer_remarks": retailer_remarks,
						  "updatedorder_status":instamojo_payment_data['status'],
						  "updatedpayment_status": instamojo_payment_data['payment_status'],
						  "updateduser_id": instamojo_payment_data['user_id'],
						  "organisation_id": instamojo_payment_data['organisation_id']
		}

		print(payloadDataOrderHistory)

		send_orderhistory = requests.post(orderHistoryUrl,data=json.dumps(payloadDataOrderHistory), headers=headers).json()

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Change Order Status",
								"status": "success",
								"message":"Update successfully"
									},
				"responseList":details}), status.HTTP_200_OK

#----------------------Change-Order-Status---------------------#

#----------------------Order-History-With-Out-Product---------------------#

@name_space.route("/orderHistoryWithOutProuct/<string:start_date>/<string:end_date>/<int:organisation_id>")	
class orderHistoryWithOutProuct(Resource):
	def get(self,start_date,end_date,organisation_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT ipr.`transaction_id`,ipr.`amount`,ipr.`status`,ipr.`invoice_url`,ipr.`coupon_code`,ipr.`last_update_ts`,
			a.`first_name`,a.`last_name`,a.`phoneno`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,a.`state`,a.`pincode`
			FROM `instamojo_payment_request` ipr
			INNER JOIN `admins` a ON a.`admin_id` = ipr.`user_id` 
			WHERE  ipr.`organisation_id` = %s
			and DATE(ipr.`last_update_ts`) >= %s and DATE(ipr.`last_update_ts`) <= %s""")

		getData = (organisation_id,start_date,end_date)		
		cursor.execute(get_query,getData)
		order_data = cursor.fetchall()

		for key,data in enumerate(order_data):
			order_data[key]['last_update_ts'] = str(data['last_update_ts'])

		return ({"attributes": {
			    	"status_desc": "order_history",
			    	"status": "success"
			    },
			    "responseList":order_data }), status.HTTP_200_OK

#----------------------Order-History-With-Out-Product---------------------#

#----------------------User-Referal-History---------------------#

@name_space.route("/userReferalHistory/<int:organisation_id>")	
class userReferalHistory(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT CONCAT(a.`first_name`," ",a.`last_name`) as `referal_customer_name`,cr.`referral_code`,CONCAT(ar.`first_name`," ",ar.`last_name`) as `refferd_customer_name`
						FROM `customer_referral` cr
						INNER JOIN `user_referral_mapping` urm ON urm.`customer_referral_id` = cr.`customer_referral_id`
						INNER JOIN `admins` a ON a.`admin_id` = cr.`customer_id`
						INNER JOIN `admins` ar ON ar.`admin_id` = urm.`customer_id` 
						WHERE cr.`organisation_id` = %s
					""")
		getData = (organisation_id)		
		cursor.execute(get_query,getData)
		referal_data = cursor.fetchall()

		return ({"attributes": {
			    	"status_desc": "referal_history",
			    	"status": "success"
			    },
			    "responseList":referal_data }), status.HTTP_200_OK


#----------------------User-Referal-History---------------------#

#----------------------Upload-Invoice---------------------#

@name_space.route("/uploadInvoice/<int:transaction_id>")
class updateCustomerAddress(Resource):
	@api.expect(upload_invoice_putmodel)
	def put(self, transaction_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "invoice_url" in details:
			invoice_url = details['invoice_url']
			update_query = ("""UPDATE `instamojo_payment_request` SET `invoice_url` = %s
				WHERE `transaction_id` = %s """)
			update_data = (invoice_url,transaction_id)
			cursor.execute(update_query,update_data)

		return ({"attributes": {"status_desc": "Upload Invoice",
								"status": "success"},
				"responseList": 'Upload Successfully'}), status.HTTP_200_OK

#-----------------------Get-Enquiry-List----------------------#

@name_space.route("/getEnquiryList/<int:organisation_id>")	
class getEnquiryList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT em.`enquiry_id`,em.`user_id`,etm.`enquiry_type`,em.`enquiery_status`,em.`date_of_closer`,em.`last_update_ts`,a.`first_name`,a.`last_name`,a.`phoneno`
			FROM `enquiry_master` em
			INNER JOIN `enquiry_type_master` etm ON etm.`enquiry_type_id` = em.`enquiry_type_id`
			INNER JOIN `admins` a ON a.`admin_id` = em.`user_id`
			WHERE em.`organisation_id` = %s ORDER BY em.`enquiry_id` DESC""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		enquiry_data = cursor.fetchall()

		for key,data in enumerate(enquiry_data):
			enquiry_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "enquiery_details",
		    		"status": "success"
		    	},
		    	"responseList":enquiry_data}), status.HTTP_200_OK

#-----------------------Get-Enquiry-List----------------------#

#-----------------------Update-Stock---------------------#

@name_space.route("/updateEnquierystatus")	
class updateEnquierystatus(Resource):
	@api.expect(enquiery_putmodel)
	def put(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		enquiry_id = details['enquiry_id']
		enquiery_status = details['enquiery_status']

		now = datetime.now()
		date_of_closer = now.strftime("%Y-%m-%d %H:%M:%S")

		update_query = ("""UPDATE `enquiry_master` SET `enquiery_status` = %s,date_of_closer = %s
					WHERE `enquiry_id` = %s""")
		update_data = (enquiery_status,date_of_closer,enquiry_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "enquiry_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Create-Enquiery-Communication---------------------#

@name_space.route("/createEnquiryCommunicationAdmin")
class createEnquiryCommunicationAdmin(Resource):
	@api.expect(enquiry_communication_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		enquiry_id = details['enquiry_id']
		user_id = details['user_id']
		image = details['image']
		text = details['text']
		role = 1
		organisation_id = details['organisation_id']
		communication_status = 1
		#organisation_id = 1		
		last_update_id = details['organisation_id']

		insert_query = ("""INSERT INTO `enquiry_communication`(`enquiry_id`,`user_id`,`text`,`image`,`role`,`organisation_id`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		data = (enquiry_id,user_id,text,image,role,organisation_id,communication_status,last_update_id)
		cursor.execute(insert_query,data)
		details['enquiry_communication'] = cursor.lastrowid

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "enquiry_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Create-Enquiery-Communication---------------------#

#----------------------Add-Enquiery-Type---------------------#

@name_space.route("/AddEnquieryType")
class AddEnquieryType(Resource):
	@api.expect(enquiery_type_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		enquiry_type = details['enquiry_type']
		enquiery_type_status = details['enquiery_type_status']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_query = ("""SELECT `enquiry_type`
			FROM `enquiry_type_master` WHERE `enquiry_type` = %s and `organisation_id` = %s""")

		getData = (enquiry_type,organisation_id)
		
		count_enquiry_type = cursor.execute(get_query,getData)

		if count_enquiry_type > 0:
			return ({"attributes": {
			    		"status_desc": "enquiery_type_details",
			    		"status": "error"
			    	},
			    	"responseList":"Type Already Exsits" }), status.HTTP_200_OK

		else:	

			insert_query = ("""INSERT INTO `enquiry_type_master`(`enquiry_type`,`organisation_id`,`status`,`last_update_id`) 
				VALUES(%s,%s,%s,%s)""")

			data = (enquiry_type,organisation_id,enquiery_type_status,last_update_id)
			cursor.execute(insert_query,data)

			connection.commit()
			cursor.close()

			return ({"attributes": {
			    		"status_desc": "enquiery_type_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Meta-Key---------------------#

#----------------------Enquiry-Type-Details---------------------#

@name_space.route("/getEnquiryTypeDetails/<int:organisation_id>/<int:enquiry_type_id>")	
class getEnquiryTypeDetails(Resource):
	def get(self,organisation_id,enquiry_type_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `enquiry_type_master` WHERE `organisation_id` = %s and `enquiry_type_id` = %s""")

		get_data = (organisation_id,enquiry_type_id)
		cursor.execute(get_query,get_data)

		enquiry_type_data = cursor.fetchone()			
		enquiry_type_data['last_update_ts'] = str(enquiry_type_data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "enquiry_type_details",
		    		"status": "success"
		    	},
		    	"responseList":enquiry_type_data}), status.HTTP_200_OK

#----------------------Enquiry-Type-Details---------------------#

#----------------------Update-Enquiery-Type---------------------#

@name_space.route("/UpdateEnquieryType/<int:enquiry_type_id>")
class UpdateEnquieryType(Resource):
	@api.expect(update_enquiery_type_postmodel)
	def put(self,enquiry_type_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()
		enquiry_type = details['enquiry_type']

		get_query = ("""SELECT `enquiry_type`
			FROM `enquiry_type_master` WHERE `enquiry_type` = %s and `enquiry_type_id` = %s """)
		getData = (enquiry_type,enquiry_type_id)		
		count_enquiry_type = cursor.execute(get_query,getData)

		if count_enquiry_type > 0:
			if details and "enquiry_type" in details:				
				update_query = ("""UPDATE `enquiry_type_master` SET `enquiry_type` = %s
					WHERE `enquiry_type_id` = %s """)
				update_data = (enquiry_type,enquiry_type_id)
				cursor.execute(update_query,update_data)

		else:
			get_query = ("""SELECT `enquiry_type`
				FROM `enquiry_type_master` WHERE `enquiry_type` = %s """)
			getData = (enquiry_type)		
			count_enquiry_type = cursor.execute(get_query,getData)

			if count_enquiry_type > 0:
				return ({"attributes": {
				    		"status_desc": "enquiery_type_details",
				    		"status": "error"
				    	},
				    	"responseList":"Type Already Exsits" }), status.HTTP_200_OK
			else:
				if details and "enquiry_type" in details:					
					update_query = ("""UPDATE `enquiry_type_master` SET `enquiry_type` = %s
						WHERE `enquiry_type_id` = %s """)
					update_data = (enquiry_type,enquiry_type_id)
					cursor.execute(update_query,update_data)				

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Enquiery Type",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Enquiery-Type---------------------#

#-----------------------Referal-Loyalty-List----------------------#

@name_space.route("/getReferalLoyaltyList/<int:organisation_id>")	
class getReferalLoyaltyList(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `loyality_master`			
			WHERE `organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		referal_loyalty_data = cursor.fetchall()

		for key,data in enumerate(referal_loyalty_data):
			referal_loyalty_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "referal_loyalty_details",
		    		"status": "success"
		    	},
		    	"responseList":referal_loyalty_data}), status.HTTP_200_OK

#-----------------------Referal-Loyalty-List----------------------#

#-----------------------Referal-Loyalty-List----------------------#

@name_space.route("/getReferalLoyaltyDetails/<int:organisation_id>/<int:loyality_id>")	
class getReferalLoyaltyDetails(Resource):
	def get(self,organisation_id,loyality_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `loyality_master`			
			WHERE `organisation_id` = %s and `loyality_id` = %s""")

		get_data = (organisation_id,loyality_id)
		cursor.execute(get_query,get_data)

		referal_loyalty_data = cursor.fetchone()
		
		referal_loyalty_data['last_update_ts'] = str(referal_loyalty_data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "referal_loyalty_details",
		    		"status": "success"
		    	},
		    	"responseList":referal_loyalty_data}), status.HTTP_200_OK

#-----------------------Referal-Loyalty-List----------------------#

#----------------------Update-Referal-Loyalty---------------------#

@name_space.route("/UpdateReferalLoyalty/<int:loyality_id>")
class UpdateReferalLoyalty(Resource):
	@api.expect(update_referal_loyalty_putmodel)
	def put(self,loyality_id):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()
		loyality_amount = details['loyality_amount']

		
		if details and "loyality_amount" in details:					
			update_query = ("""UPDATE `loyality_master` SET `loyality_amount` = %s
				WHERE `loyality_id` = %s """)
			update_data = (loyality_amount,loyality_id)
			cursor.execute(update_query,update_data)				

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Referal Loyalty",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Referal-Loyalty---------------------#


#----------------------Customer-Exchange-Ans---------------------#
@name_space.route("/getCustomerExchangeAns/<int:organisation_id>")	
class getCustomerExchangeAns(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT ced.`exchange_id`,ced.`amount`,ced.`last_update_ts`,a.`first_name`,a.`last_name`
			FROM `customer_exchange_device` ced
			INNER JOIN `admins` a ON a.`admin_id` = ced.`customer_id` 
			WHERE ced.`organisation_id` = %s """)

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		customer_exchange_ans_data = cursor.fetchall()

		for key,data in enumerate(customer_exchange_ans_data):
			customer_exchange_ans_data[key]['last_update_ts'] = str(data['last_update_ts'])

			get_customer_exchange_device_ans_query = ("""SELECT edqa.`ans`, edqa.`ans_image`,edq.`question`,edq.`question_desc`
				FROM `customer_exchange_device_ans` ceda
				INNER JOIN `exchange_device_question_ans` edqa ON edqa.`question_ans_id` = ceda.`question_ans_id`
				INNER JOIN `exchange_device_question` edq ON edq.`question_id` = edqa.`question_id`
				WHERE ceda.`exchange_id` = %s""")
			get_customer_exchange_device_ans_data = (data['exchange_id'])
			cursor.execute(get_customer_exchange_device_ans_query,get_customer_exchange_device_ans_data)
			customer_exchange_device_ans_query = cursor.fetchall()

			customer_exchange_ans_data[key]['questions'] = customer_exchange_device_ans_query

		return ({"attributes": {
					"status_desc": "customer-exchange-ans",
					"status": "success"
				},
					"responseList":customer_exchange_ans_data}), status.HTTP_200_OK
#----------------------Customer-Exchange-Ans---------------------#

#----------------------Exchange-Device-Question-with-language---------------------#

@name_space.route("/getExchangeDeviceQuestionWithLanguage/<int:organisation_id>/<int:question_type>/<string:language>")	
class getExchangeDeviceQuestionWithLanguage(Resource):
	def get(self,organisation_id,question_type,language):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `exchange_device_question` WHERE `organisation_id` = %s and `question_type` = %s and `language` = %s""")

		get_data = (organisation_id,question_type,language)
		cursor.execute(get_query,get_data)

		exchange_device_question_data = cursor.fetchall()

		for key,data in enumerate(exchange_device_question_data):
			get_ans_query = ("""SELECT `question_ans_id`,`ans`,`ans_image`
			FROM `exchange_device_question_ans` WHERE `question_id` = %s and `language` = %s""")

			get_ans_data = (data['question_id'],language)
			cursor.execute(get_ans_query,get_ans_data)

			exchange_device_question_ans_data = cursor.fetchall()

			exchange_device_question_data[key]['ans'] = exchange_device_question_ans_data

			exchange_device_question_data[key]['last_update_ts'] = str(data['last_update_ts'])
				
		return ({"attributes": {
		    		"status_desc": "exchange_device_question_details",
		    		"status": "success"
		    	},
		    	"responseList":exchange_device_question_data}), status.HTTP_200_OK

#----------------------Exchange-Device-Question-with-language---------------------#

#----------------------Add-Referal-Program---------------------#

@name_space.route("/AddReferalProgram")
class AddReferalProgram(Resource):
	@api.expect(referal_program_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		referal_user = details['referal_user']
		reffered_user = details['reffered_user']

		jsondumployaltyreferaluser = json.dumps(referal_user)	
		jsonloadloyaltyreferaluser = json.loads(jsondumployaltyreferaluser)	

		jsondumployaltyreffereduser = json.dumps(reffered_user)
		jsonloadloyaltyreffereduser = json.loads(jsondumployaltyreffereduser)	

		loyalty_status = 1
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']

		loyality_amount_referal_user = jsonloadloyaltyreferaluser['loyality_amount']
		loyality_type_referal_user = jsonloadloyaltyreferaluser['loyality_type']

		loyality_amount_reffered_user = jsonloadloyaltyreffereduser['loyality_amount']
		loyality_type_reffered_user = jsonloadloyaltyreffereduser['loyality_type']

		get_referal_user_query = ("""SELECT *
				FROM `loyality_master` WHERE `organisation_id` = %s and `loyality_type` = %s""")	
		getDataReferalUser = (organisation_id,loyality_type_referal_user)
		count_referal_user = cursor.execute(get_referal_user_query,getDataReferalUser)

		if count_referal_user == 0:		
			insert_query_referal_user = ("""INSERT INTO `loyality_master`(`loyality_amount`,`loyality_type`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s)""")
			
			data_referal_user = (loyality_amount_referal_user,loyality_type_referal_user,loyalty_status,organisation_id,last_update_id)
			cursor.execute(insert_query_referal_user,data_referal_user)	
		else:
			update_query_referal_user = ("""UPDATE `loyality_master` SET `loyality_amount` = %s
				WHERE `loyality_type` = %s and `organisation_id` = %s""")
			update_data_referal_user = (loyality_amount_referal_user,loyality_type_referal_user,organisation_id)
			cursor.execute(update_query_referal_user,update_data_referal_user)


		get_reffered_user_query = ("""SELECT *
				FROM `loyality_master` WHERE `organisation_id` = %s and `loyality_type` = %s""")	
		getDataRefferedUser = (organisation_id,loyality_type_reffered_user)
		count_refferd_user = cursor.execute(get_reffered_user_query,getDataRefferedUser)

		if count_refferd_user == 0:
			insert_query_reffered_user = ("""INSERT INTO `loyality_master`(`loyality_amount`,`loyality_type`,`status`,`organisation_id`,`last_update_id`) 
							VALUES(%s,%s,%s,%s,%s)""")			
			data_reffered_user = (loyality_amount_reffered_user,loyality_type_reffered_user,loyalty_status,organisation_id,last_update_id)
			cursor.execute(insert_query_reffered_user,data_reffered_user)
		else:
			update_query_reffered_user = ("""UPDATE `loyality_master` SET `loyality_amount` = %s
				WHERE `loyality_type` = %s and `organisation_id` = %s""")
			update_data_reffered_user = (loyality_amount_reffered_user,loyality_type_reffered_user,organisation_id)
			cursor.execute(update_query_reffered_user,update_data_reffered_user)

		connection.commit()
		cursor.close()

		return ({"attributes": {
					"status_desc": "Referal Program",
					"status": "success"
				},
					"responseList":referal_user}), status.HTTP_200_OK

#----------------------Add-Referal-Program---------------------#

#----------------------Add-Retailer-Store---------------------#

@name_space.route("/addRetailerStore")	
class addRetailerStore(Resource):
	@api.expect(retailer_store_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		organisation_id = details['organisation_id']
		retailer_name = details['retailer_name']
		city = details['city']
		last_update_id = details['organisation_id']
		image = details['image']

		get_query = ("""SELECT *
			FROM `retailer_store` WHERE `retailer_name` = %s and `city` = %s and `organisation_id` = %s""")
		getData = (retailer_name,city,organisation_id)
		count_retailer = cursor.execute(get_query,getData)
		
		if count_retailer > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "retailer_details",
			    		"status": "error",
			    		"message":" Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

		else:
			store_status = 1
			insert_query = ("""INSERT INTO `retailer_store`(`retailer_name`,`city`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")
			data = (retailer_name,city,store_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)
			retailer_store_id = cursor.lastrowid

			store_image_status = 1
			insert_store_image_query = ("""INSERT INTO `retailer_store_image`(`retailer_store_id`,`image`,`status`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s) """)
			store_image_data = (retailer_store_id,image,store_image_status,organisation_id,last_update_id)
			cursor.execute(insert_store_image_query,store_image_data)

			return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList": details}), status.HTTP_200_OK

		

#----------------------Add-Retailer-Store---------------------#

#----------------------Product-List-By-Brand---------------------#
@name_space.route("/getProductListByBrand/<int:brand_id>/<int:organisation_id>")	
class getProductListByBrand(Resource):
	def get(self,brand_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT p.`product_name`,p.`product_short_description`,
			p.`product_long_description`,pm.`meta_key_text` 
			FROM `product_brand_mapping` pbm 
			INNER JOIN `product` p ON pbm.`product_id` = p.`product_id`
			INNER JOIN `product_meta` pm ON pm.`product_id` = p.`product_id`
			WHERE pbm.`organisation_id` = %s and pbm.`brand_id` = %s
			""")
		get_data = (organisation_id,brand_id)
		cursor.execute(get_query,get_data)
		product_list = cursor.fetchall()

		for bkey,bdata in enumerate(product_list):

			a_string = bdata['meta_key_text']
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

				product_list[bkey]['met_key_value'] = met_key

			get_product_meta_image_quey = ("""SELECT `image`
			FROM `product_meta_images` WHERE `product_meta_id` = %s and default_image_flag = 1""")
			product_meta_image_data = (bdata['product_meta_id'])
			rows_count_image_best_selling = cursor.execute(get_product_meta_image_quey,product_meta_image_data)
			if rows_count_image_best_selling > 0:
				product_meta_image = cursor.fetchone()
				product_list[bkey]['product_image'] = product_meta_image['image']
			else:
				product_list[bkey]['product_image'] = ""
			

		return ({"attributes": {
		    		"status_desc": "product_list",
		    		"status": "success"
		    	},
		    	"responseList":product_list}), status.HTTP_200_OK		

#----------------------Product-List-By-Brand---------------------#

#----------------------Add-Delivery-Question---------------------#

@name_space.route("/AddDeliveryQuestion")
class AddDeliveryQuestion(Resource):
	@api.expect(delivery_question_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		location = details['location']
		rate = details['rate']
		deliveryQuestionStatus = 1
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']			

		insert_query = ("""INSERT INTO `delivery_question`(`location`,`rate`,`status`,`organisation_id`,`last_update_id`) 
			VALUES(%s,%s,%s,%s,%s)""")

		data = (location,rate,deliveryQuestionStatus,organisation_id,last_update_id)
		cursor.execute(insert_query,data)

		details['delivery_question_id'] = cursor.lastrowid

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "Delivery Question",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Delivery-Question---------------------#


#----------------------Delivery-Question---------------------#

@name_space.route("/getDeliveryQuestion/<int:organisation_id>")	
class getDeliveryQuestion(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `delivery_question_id`,`location`,`rate`
			FROM `delivery_question` WHERE `organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		delivery_question_data = cursor.fetchall()

		return ({"attributes": {
		    		"status_desc": "delivery_question_details",
		    		"status": "success"
		    	},
		    	"responseList":delivery_question_data}), status.HTTP_200_OK

#----------------------Delivery-Question---------------------#

#----------------------Update-Delivery-Question---------------------#

@name_space.route("/updateDeliveryQuestion/<int:delivery_question_id>")
class updateDeliveryQuestion(Resource):
	@api.expect(delivery_question_putmodel)
	def put(self, delivery_question_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		location = details['location']
		rate = details['rate']

		update_query = ("""UPDATE `delivery_question` SET `location` = %s, `rate` = %s
						   WHERE `delivery_question_id` = %s """)
		update_data = (location,rate,delivery_question_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "delivery_question_details",
		    		"status": "success"
		    	},
		    	"responseList":details}), status.HTTP_200_OK

#----------------------Update-Delivery-Question---------------------#


#----------------------Delete-Delivery-Question---------------------#

@name_space.route("/deleteDeliveryQuestion/<string:key>/<int:delivery_question_id>/<int:organisation_id>")
class deleteDeliveryQuestion(Resource):
	def delete(self, key,delivery_question_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if key == 'all':
			delete_query = ("""DELETE FROM `delivery_question` WHERE `organisation_id` = %s""")
			delData = (organisation_id)
		else:
			delete_query = ("""DELETE FROM `delivery_question` WHERE `organisation_id` = %s and `delivery_question_id` = %s""")
			delData = (organisation_id,delivery_question_id)
			
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Delete Delivery Question",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Delivery-Question---------------------#

#----------------------Add-Check-Out-Question---------------------#

@name_space.route("/AddCheckoutQuestion")
class AddCheckoutQuestion(Resource):
	@api.expect(checkout_question_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		question = details['question']		
		organisation_id = details['organisation_id']
		last_update_id = details['organisation_id']			

		insert_query = ("""INSERT INTO `checkout_question`(`question`,`organisation_id`,`last_update_id`) 
			VALUES(%s,%s,%s)""")

		data = (question,organisation_id,last_update_id)
		cursor.execute(insert_query,data)

		details['check_out_question_id'] = cursor.lastrowid

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "Checkout Question",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#----------------------Add-Check-Out-Question---------------------#

#----------------------get-Checkout-Question---------------------#

@name_space.route("/getCheckoutQuestion/<int:organisation_id>")	
class getCheckoutQuestion(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `check_out_question_id`,`question`
			FROM `checkout_question` WHERE `organisation_id` = %s""")

		get_data = (organisation_id)
		cursor.execute(get_query,get_data)

		checkout_question_data = cursor.fetchall()

		return ({"attributes": {
		    		"status_desc": "delivery_question_details",
		    		"status": "success"
		    	},
		    	"responseList":checkout_question_data}), status.HTTP_200_OK

#----------------------Delivery-Question---------------------#

#----------------------Update-Checkout-Question---------------------#

@name_space.route("/updateCheckoutQuestion/<int:check_out_question_id>")
class updateCheckoutQuestion(Resource):
	@api.expect(checkout_question_putmodel)
	def put(self, check_out_question_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		question = details['question']		

		update_query = ("""UPDATE `checkout_question` SET `question` = %s
						   WHERE `check_out_question_id` = %s """)
		update_data = (question,check_out_question_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "checkout_question_details",
		    		"status": "success"
		    	},
		    	"responseList":details}), status.HTTP_200_OK

#----------------------Update-Checkout-Question---------------------#

#----------------------Delete-Checkout-Question---------------------#

@name_space.route("/deleteCheckoutQuestion/<string:key>/<int:check_out_question_id>/<int:organisation_id>")
class deleteCheckoutQuestion(Resource):
	def delete(self, key,check_out_question_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if key == 'all':
			delete_query = ("""DELETE FROM `checkout_question` WHERE `organisation_id` = %s""")
			delData = (organisation_id)
		else:
			delete_query = ("""DELETE FROM `checkout_question` WHERE `organisation_id` = %s and `check_out_question_id` = %s""")
			delData = (organisation_id,check_out_question_id)
			
		cursor.execute(delete_query,delData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Delete Checkout Question",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Checkout-Question---------------------#

#----------------------Send-Notification---------------------#

@name_space.route("/sendNotifications")
class sendNotifications(Resource):
	@api.expect(notification_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		organisation_id = details['organisation_id']

		get_organisation_firebase_query = ("""SELECT `firebase_key`
								FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
		get_organisation_firebase_data = (organisation_id)
		cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
		firebase_data = cursor.fetchone()

		get_devices_query = ("""SELECT *
								FROM `devices` WHERE  `organisation_id` = %s""")
		get_devices_data = (organisation_id)
		cursor.execute(get_devices_query,get_devices_data)
		devices_data = cursor.fetchall()

		for key,data in enumerate(devices_data):	
			if data['device_type'] == 2:
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				sendAppPushNotificationUrl = BASE_URL + "ecommerce_product/EcommerceProduct/sendAppPushNotifications"
				payloadpushData = {
									"device_id":data['device_token'],
									"firebase_key": firebase_data['firebase_key'],
									"image":details['image'],
									"text":details['text'],
									"title":details['title']
								}
				print(payloadpushData)
				send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		return ({"attributes": {"status_desc": "Push Notification",
									"status": "success"},
					"responseList":{}}), status.HTTP_200_OK

#----------------------Send-Notification---------------------#
							
#----------------------Send-Push-Notification---------------------#

@name_space.route("/sendAppPushNotifications")
class sendAppPushNotifications(Resource):
	@api.expect(appmsg_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		data_message = {
							"title" : details['title'],
							"message": details['text'],
							"image-url":details['image']
						}
		api_key = details.get('firebase_key')
		device_id = details.get('device_id')
		push_service = FCMNotification(api_key=api_key)
		msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = data_message)
		sent = 'N'
		if msgResponse.get('success') == 1:
			sent = 'Y'
		
		
		connection.commit()
		cursor.close()

		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    	},
				    	"responseList":msgResponse}), status.HTTP_200_OK
#----------------------Send-Push-Notification---------------------#

#----------------------Get-Product-Meta-Images---------------------#
@name_space.route("/getProductMetaImages/<int:product_meta_id>")	
class getProductMetaImages(Resource):
	def get(self,product_meta_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `product_image_id`,`image`,`default_image_flag`,`image_type`
										FROM `product_meta_images` WHERE `product_meta_id` = %s and is_gallery <> 1 """)
		getdata = (product_meta_id)
		product_image_count = cursor.execute(get_query,getdata)

		if product_image_count >0 :
			product_image = cursor.fetchall()
		else:
			product_image = []

		return ({"attributes": {
		    	"status_desc": "image_details",
		    	"status": "success"
		    },
		    "responseList":{"product_image":product_image}}), status.HTTP_200_OK


#----------------------Get-Product-Meta-Images---------------------#

#----------------------Get-Product-Meta-Images-For-Gallery---------------------#
@name_space.route("/getProductMetaImagesForGallery/<int:product_meta_id>")	
class getProductMetaImagesForGallery(Resource):
	def get(self,product_meta_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `product_image_id`,`image`,`default_image_flag`,`image_type`
										FROM `product_meta_images` WHERE `product_meta_id` = %s and `is_gallery` = 1""")
		getdata = (product_meta_id)
		product_image_count = cursor.execute(get_query,getdata)

		if product_image_count >0 :
			product_image = cursor.fetchall()
		else:
			product_image = []

		return ({"attributes": {
		    	"status_desc": "image_details",
		    	"status": "success"
		    },
		    "responseList":{"product_image":product_image}}), status.HTTP_200_OK


#----------------------Get-Product-Meta-Images---------------------#

#----------------------Get-Device-Details-By-UserId---------------------#
@name_space.route("/getDeviceDetailsByUserId/<int:user_id>")	
class getDeviceDetailsByUserId(Resource):
	def get(self,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `device_id`,`device_type`,`device_token`
										FROM `devices` WHERE `user_id` = %s """)
		getdata = (user_id)
		count = cursor.execute(get_query,getdata)

		if count >0 :
			device_data = cursor.fetchone()
		else:
			device_data = {}

		return ({"attributes": {
		    	"status_desc": "device_details",
		    	"status": "success"
		    },
		    "responseList":device_data}), status.HTTP_200_OK


#----------------------Get-Device-Details-By-UserId---------------------#


#----------------------Get-Firebase-Details-By-OrganisationId---------------------#
@name_space.route("/getFirebaseDetailsByOrganisationId/<int:organisation_id>")	
class getFirebaseDetailsByOrganisationId(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT `organisation_firebase_id`,`firebase_key`
										FROM `organisation_firebase_details` WHERE `organisation_id` = %s """)
		getdata = (organisation_id)
		count = cursor.execute(get_query,getdata)

		if count >0 :
			firebase_data = cursor.fetchone()
		else:
			firebase_data = {}

		return ({"attributes": {
		    	"status_desc": "device_details",
		    	"status": "success"
		    },
		    "responseList":firebase_data}), status.HTTP_200_OK

#----------------------Get-Firebase-Details-By-OrganisationId---------------------#

#----------------------Add-Budget---------------------#

@name_space.route("/AddBudget")	
class AddBudget(Resource):
	@api.expect(budget_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		category_id = details['category_id']
		greaterthanvalue = details['greaterthanvalue']
		lessthanvalue = details['lessthanvalue']		
		last_update_id = details['organisation_id']
		organisation_id = details['organisation_id']	

		get_query = ("""SELECT *
			FROM `budget` WHERE `greaterthanvalue` = %s and `lessthanvalue` = %s and `category_id` = %s and `organisation_id` = %s""")
		getData = (greaterthanvalue,lessthanvalue,category_id,organisation_id)
		count_retailer = cursor.execute(get_query,getData)
		
		if count_retailer > 0:
			data = cursor.fetchone()
			return ({"attributes": {
			    		"status_desc": "budget_details",
			    		"status": "error",
			    		"message":" Already Exist"
			    	},
			    	"responseList":{} }), status.HTTP_200_OK

		else:
			store_status = 1
			insert_query = ("""INSERT INTO `budget`(`greaterthanvalue`,`lessthanvalue`,`category_id`,`organisation_id`,`last_update_id`) 
				VALUES(%s,%s,%s,%s,%s)""")
			data = (greaterthanvalue,lessthanvalue,category_id,organisation_id,last_update_id)
			cursor.execute(insert_query,data)						

			return ({"attributes": {
		    		"status_desc": "customer_details",
		    		"status": "success",
		    		"message":""
		    	},
		    	"responseList": details}), status.HTTP_200_OK

		

#----------------------Add-Budget---------------------#

#----------------------Add-Compare-Feature---------------------#
@name_space.route("/AddCompareProductFeatures")	
class AddCompareProductFeatures(Resource):
	@api.expect(compare_features_postmodel)
	def post(self):	
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		other_specifications = json.dumps(details['other_specifications'])
		product_meta_id = details['product_meta_id']

		update_query = ("""UPDATE `product_meta` SET `other_specification_json` = %s
				WHERE `product_meta_id` = %s """)
		update_data = (other_specifications,product_meta_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Other Specifications",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Add-Compare-Feature---------------------#

#----------------------Product-List-By-Category-Id-And-Brnad-Id---------------------#
@name_space.route("/productListByCategoryIdAndBrandId/<int:organisation_id>/<int:category_id>/<int:brand_id>")	
class productListByCategoryIdAndBrandId(Resource):
	def get(self,organisation_id,category_id,brand_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if brand_id == 0:
			get_query = ("""SELECT  p.`product_id`,p.`product_name`,mm.`meta_key`,p.`status`,p.`category_id` as `product_type_id` 
				FROM `product` p 
				INNER JOIN `meta_key_master` mm ON mm.`meta_key_id` = p.`category_id`
				WHERE product_id not in 
				(select product_id from product_brand_mapping where organisation_id = %s) and 
				p.`organisation_id` = %s and category_id = %s""")
			get_data = (organisation_id,organisation_id,category_id)
		else:
			get_query = ("""SELECT p.`product_id`,p.`product_name`,p.`status`,p.`category_id`,pbm.`brand_id`
				FROM `product_brand_mapping` pbm
				INNER JOIN `product` p ON p.`product_id` = pbm.`product_id`
				WHERE  pbm.`organisation_id` = %s and p.`category_id` = %s and pbm.`brand_id` = %s""")
			get_data = (organisation_id,category_id,brand_id)

		cursor.execute(get_query,get_data)
		product_data = cursor.fetchall()

		return ({"attributes": {
		    		"status_desc": "Product Data",
		    		"status": "success"
		    	},
		    	"responseList":product_data}), status.HTTP_200_OK

#----------------------Create-Brand-with-respect-Category-Id---------------------#

@name_space.route("/AddBrandWithRespectCategoryId")
class AddBrandWithRespectCategoryId(Resource):
	@api.expect(brand_category_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		category_id = details['category_id']
		brand_name =  details['brand_name']

		if details and "brand_image" in details:
			brand_image = details['brand_image']
		else:
			brand_image = ""

		organisation_id = details['organisation_id']

		meta_key_id = 2
		brand_status = 1
		brand_organisation_id = 1

		insert_query = ("""INSERT INTO `meta_key_value_master`(`meta_key_id`,`meta_key_value`,`image`,`status`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s,%s,%s)""")
		data = (meta_key_id,brand_name,brand_image,brand_status,brand_organisation_id,brand_organisation_id)
		cursor.execute(insert_query,data)
		brand_id = cursor.lastrowid

		insert_brand_category_mapping_query = ("""INSERT INTO `category_brand_mapping`(`brand_id`,`category_id`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s)""")
		brand_category_data = (brand_id,category_id,organisation_id,organisation_id)
		cursor.execute(insert_brand_category_mapping_query,brand_category_data)

		insert_brand_organisation_mapping_query_for_1 = ("""INSERT INTO `organisation_brand_mapping`(`brand_id`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
		brand_organisation_mapping_data_for_1 = (brand_id,1,1)
		cursor.execute(insert_brand_organisation_mapping_query_for_1,brand_organisation_mapping_data_for_1)

		insert_brand_organisation_mapping_query = ("""INSERT INTO `organisation_brand_mapping`(`brand_id`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s)""")
		brand_organisation_mapping_data = (brand_id,organisation_id,organisation_id)
		cursor.execute(insert_brand_organisation_mapping_query,brand_organisation_mapping_data)

		return ({"attributes": {
		    		"status_desc": "brand_details",
		    		"status": "success"
		    	},
		    	"responseList": details}), status.HTTP_200_OK


#----------------------Create-Brand-with-respect-Category-Id---------------------#

#----------------------Update-Brand---------------------#
@name_space.route("/updateBrand/<int:brand_id>/<int:organisation_id>")	
class updateBrand(Resource):
	@api.expect(brand_putmodel)
	def put(self,brand_id,organisation_id):	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()		

		if details and "brand_name" in details:
			brand_name = details['brand_name']
			update_query = ("""UPDATE `meta_key_value_master` SET `meta_key_value` = %s
				WHERE `meta_key_value_id` = %s """)
			update_data = (brand_name,brand_id)
			cursor.execute(update_query,update_data)

		if details and "brand_image" in details:
			brand_image = details['brand_image']
			update_query = ("""UPDATE `meta_key_value_master` SET `image` = %s
				WHERE `meta_key_value_id` = %s """)
			update_data = (brand_image,brand_id)
			cursor.execute(update_query,update_data)


		if details and "category_id" in details:
			category_id = details['category_id']
			delete_brand_category_mapping_query = ("""DELETE FROM `category_brand_mapping` WHERE `category_id` = %s and `brand_id` = %s and `organisation_id` = %s""")
			delBrandCategoryData = (category_id,brand_id,organisation_id)		
			cursor.execute(delete_brand_category_mapping_query,delBrandCategoryData)

			insert_brand_category_mapping_query = ("""INSERT INTO `category_brand_mapping`(`brand_id`,`category_id`,`organisation_id`,`last_update_id`) 
								VALUES(%s,%s,%s,%s)""")
			brand_category_data = (brand_id,category_id,organisation_id,organisation_id)
			cursor.execute(insert_brand_category_mapping_query,brand_category_data)

		return ({"attributes": {"status_desc": "Update Brand",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK	

#----------------------Update-Brand---------------------#

#----------------------Delete-Brand-From-Brand-Category-Mapping---------------------#

@name_space.route("/deleteBrandFromBrandCategoryMapping/<int:brand_id>/<int:organisation_id>")
class deleteBrandFromBrandCategoryMapping(Resource):
	def delete(self, brand_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_brand_category_mapping_query = ("""DELETE FROM `category_brand_mapping` WHERE `brand_id` = %s and `organisation_id` = %s""")
		delBrandCategoryData = (brand_id,organisation_id)
		
		cursor.execute(delete_brand_category_mapping_query,delBrandCategoryData)

		delete_brand_organisation_mapping_query = ("""DELETE FROM `organisation_brand_mapping` where `brand_id` = %s and `organisation_id` = %s""")		
		delBrandOrganisationData = (brand_id,organisation_id)
		cursor.execute(delete_brand_organisation_mapping_query,delBrandOrganisationData)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Brand",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Brand-From-Brand-Category-Mapping---------------------#

#----------------------Create-Category----------------------#

@name_space.route("/AddCategory")
class AddCategory(Resource):
	@api.expect(category_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		category_name = details['category_name']

		if details and "category_image" in details:
			category_image = details['category_image']
		else:
			category_image = ""

		meta_key_status = 1
		global_category_status = 1
		local_category_status = 1

		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_meta_key_query = ("""SELECT * from `meta_key_master` WHERE `meta_key` = %s and `organisation_id` = 1""")
		get_meta_key_data = (category_name)
		cout_get_meta_key = cursor.execute(get_meta_key_query,get_meta_key_data)

		if cout_get_meta_key < 1:

			insert_meta_key_query = ("""INSERT INTO `meta_key_master`(`meta_key`,`status`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s)""")
			meta_key_organisation_id = 1
			meta_key_last_update_id = 1
			meta_key_data = (category_name,meta_key_status,meta_key_organisation_id,meta_key_last_update_id)
			cursor.execute(insert_meta_key_query,meta_key_data)
			category_id = cursor.lastrowid

			insert_category_global_query = ("""INSERT INTO `category`(`category_id`,`category_name`,`category_image`,`status`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s,%s)""")
			global_category_organisaton_id = 1
			global_category_last_update_id = 1
			category_global_data = (category_id,category_name,category_image,global_category_status,global_category_organisaton_id,global_category_last_update_id)
			cursor.execute(insert_category_global_query,category_global_data)

			insert_category_local_query = ("""INSERT INTO `category`(`category_id`,`category_name`,`category_image`,`status`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s,%s)""")
			category_local_data = (category_id,category_name,category_image,local_category_status,organisation_id,last_update_id)
			cursor.execute(insert_category_local_query,category_local_data)

		else:
			meta_key_data = cursor.fetchone()
			get_category_local_query = ("""SELECT * from `category` WHERE `category_name` = %s and `organisation_id` = %s""")
			get_category_local_data = (category_name,organisation_id)
			count_local_category = cursor.execute(get_category_local_query,get_category_local_data)

			if count_local_category < 1:
				insert_category_local_query = ("""INSERT INTO `category`(`category_id`,`category_name`,`category_image`,`status`,`organisation_id`,`last_update_id`) 
									VALUES(%s,%s,%s,%s,%s,%s)""")
				category_local_data = (meta_key_data['meta_key_id'],category_name,category_image,local_category_status,organisation_id,last_update_id)
				cursor.execute(insert_category_local_query,category_local_data)


		return ({"attributes": {
		    		"status_desc": "category_details",
		    		"status": "success"
		    	},
		    	"responseList": details}), status.HTTP_200_OK


#----------------------Create-Category----------------------#

#----------------------Update-Category---------------------#
@name_space.route("/updateCategory/<int:category_id>/<int:organisation_id>")	
class updateCategory(Resource):
	@api.expect(category_putmodel)
	def put(self,category_id,organisation_id):	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()	

		if details and "category_name" in details:
			category_name = details['category_name']
			update_query = ("""UPDATE `category` SET `category_name` = %s
				WHERE `category_id` = %s and `organisation_id` = %s""")
			update_data = (category_name,category_id,organisation_id)
			cursor.execute(update_query,update_data)

		if details and "category_image" in details:
			category_image = details['category_image']
			update_query = ("""UPDATE `category` SET `category_image` = %s
				WHERE `category_id` = %s and `organisation_id` = %s""")
			update_data = (category_image,category_id,organisation_id)
			cursor.execute(update_query,update_data)	

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Category",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Update-Category---------------------#

#----------------------Delete-Category---------------------#

@name_space.route("/deleteCategory/<int:category_id>/<int:organisation_id>")
class deleteCategory(Resource):
	def delete(self, category_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		delete_category_query = ("""DELETE FROM `category` WHERE `category_id` = %s and `organisation_id` = %s""")
		delCategoryData = (category_id,organisation_id)
		
		cursor.execute(delete_category_query,delCategoryData)		

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Category",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Category---------------------#

