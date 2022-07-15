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

ecommerce_retailer_loyality = Blueprint('ecommerce_retailer_loyality_api', __name__)
api = Api(ecommerce_retailer_loyality,  title='Ecommerce API',description='Ecommerce API')
name_space = api.namespace('EcommerceRetailerLoyality',description='Ecommerce Retailer Loyality')


general_loyality_postmodel = api.model('SelectGeneralLoyalityPostmodel', {
	"signup_point":fields.String(required=True),
	"per_transaction_percentage":fields.String(required=True),
	"category_id":fields.Integer(required=True),
	"category_percentage":fields.String(required=True),
	"category_high_margine_percentage":fields.String(required=True),
	"category_low_margine_percentage":fields.String(required=True),
	"sub_category_id":fields.Integer(required=True),
	"sub_category_percentage":fields.String(required=True),
	"sub_category_high_margine_percentage":fields.String(required=True),
	"sub_category_low_margine_percentage":fields.String(required=True),
	"birthday_bonus":fields.Integer(required=True),
	"anniversary_bonus":fields.Integer(required=True),
	"first_purchase_bonus":fields.Integer(required=True),
	"customer_review_bonus":fields.Integer(required=True),
	"prebook_loyality_bonus":fields.Integer(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

redeem_settings_postmodel = api.model('RedeemSettingsPostmodel', {
	"is_apply_for_online_user":fields.String(required=True),
	"point":fields.String(required=True),
	"point_value_in_rs":fields.String(required=True),	
	"maximum_amount_percentage":fields.String(required=True),
	"maximum_amount_absolute_value":fields.String(required=True),
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

redeem_customer_wallet_postmodel = api.model('RedeemCustomerWalletPostmodel', {	
	"redeem_amount":fields.Integer(required=True),
	"customer_id":fields.Integer(required=True),	
	"product_id":fields.Integer,
	"product_meta_id":fields.Integer,
	"offer_id":fields.Integer,
	"transaction_id":fields.Integer,
	"image":fields.String,
	"remarks":fields.String,
	"organisation_id":fields.Integer(required=True),
	"last_update_id":fields.Integer(required=True)
})

appmsg_model = api.model('appmsg_model', {	
	"firebase_key":fields.String(),
	"device_id":fields.String()
})

category_loyality_model = api.model('category_model ', {
	"category_id":fields.Integer(required=True),
	"category_percentage": fields.String(required=True),
	"category_high_margine_percentage":fields.String(required=True),
	"category_low_margine_percentage":fields.String(required=True)
})

sub_category_loyality_model =  api.model('sub_category_model ', {
	"sub_category_id":fields.Integer(required=True),
	"sub_category_percentage": fields.String(required=True),
	"sub_category_high_margine_percentage":fields.String(required=True),
	"sub_category_low_margine_percentage":fields.String(required=True)
})

referal_loyality_model = api.model('referal_loyality_model ', {
	"greaterthan_person_count":fields.Integer(required=True),
	"lessthan_person_count":fields.Integer(required=True),
	"referal_bonus":fields.String(required=True)
})

transactional_loyality_model = api.model('transactional_loyality_model ', {
	"greaterthan_transactional_amount":fields.String(required=True),
	"lessthan_transactional_amount":fields.String(required=True),
	"transactional_bonus":fields.String(required=True)
})

buyback_loyality_model =  api.model('buyback_loyality_model ', {
	"greaterthan_transactional_amount":fields.String(required=True),
	"lessthan_transactional_amount":fields.String(required=True),
	"transactional_bonus":fields.String(required=True)
})

loyality_settings_postmodel = api.model('LoyalitySettingPostmodel', {
	"signup_point": fields.String(),
	"per_transaction_percentage":  fields.String(),
	"birthday_bonus":fields.String(),
	"anniversary_bonus":fields.String(),
	"first_purchase_bonus":fields.String(),
	"customer_review_bonus":fields.String(),
	"prebook_loyality_bonus":fields.String(),	
	"e_bill_bonus":fields.String(),
	"category_loyality": fields.List(fields.Nested(category_loyality_model)),
	"sub_category_loyality": fields.List(fields.Nested(sub_category_loyality_model)),
	"referal_loyality": fields.List(fields.Nested(referal_loyality_model)),
	"transactional_loyality": fields.List(fields.Nested(transactional_loyality_model)),
	"buyback_loyality": fields.List(fields.Nested(buyback_loyality_model)),
	"organisation_id":fields.Integer()
})

BASE_URL = 'http://ec2-18-221-89-14.us-east-2.compute.amazonaws.com/flaskapp/'

#--------------------Loyality-Dashboard-------------------------#

@name_space.route("/loyalityDashboard/<string:filterkey>/<int:organisation_id>")	
class loyalityDashboard(Resource):
	def get(self,filterkey,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		credit_data = {}
		redeem_data = {}

		if filterkey == 'today':
			now = datetime.now()
			today_date = now.strftime("%Y-%m-%d")

			get_credited_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and date(`last_update_ts`)=%s and `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty' """)
			get_credited_customer_data = (organisation_id,today_date)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				credit_data['store_data'] = store_data
				for ckey,cdata in enumerate(credit_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and date(wt.`last_update_ts`)=%s and wt.`transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,cdata['retailer_store_id'],cdata['retailer_store_store_id'],today_date)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						credit_data['store_data'][ckey]['customer_count'] = customer_retailer_data['total_user']
					else:
						credit_data['store_data'][ckey]['customer_count'] = 0
					
			else:
				credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and date(`last_update_ts`)=%s and `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,today_date)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				redeem_data['store_data'] = store_data
				for rkey,rdata in enumerate(redeem_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and date(wt.`last_update_ts`)=%s and wt.`transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,rdata['retailer_store_id'],rdata['retailer_store_store_id'],today_date)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						redeem_data['store_data'][rkey]['customer_count'] = customer_retailer_data['total_user']
					else:
						redeem_data['store_data'][rkey]['customer_count'] = 0
			else:
				redeem_data['store_data'] = []


		if filterkey == 'yesterday':
			today = date.today()

			yesterday = today - timedelta(days = 1)

			get_credited_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and date(`last_update_ts`)=%s and `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
			get_credited_customer_data = (organisation_id,yesterday)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				credit_data['store_data'] = store_data
				for ckey,cdata in enumerate(credit_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and date(wt.`last_update_ts`)=%s and wt.`transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,cdata['retailer_store_id'],cdata['retailer_store_store_id'],yesterday)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						credit_data['store_data'][ckey]['customer_count'] = customer_retailer_data['total_user']
					else:
						credit_data['store_data'][ckey]['customer_count'] = 0
					
			else:
				credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and date(`last_update_ts`)=%s and `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,yesterday)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				redeem_data['store_data'] = store_data
				for rkey,rdata in enumerate(redeem_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and date(wt.`last_update_ts`)=%s and wt.`transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,rdata['retailer_store_id'],rdata['retailer_store_store_id'],yesterday)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						redeem_data['store_data'][rkey]['customer_count'] = customer_retailer_data['total_user']
					else:
						redeem_data['store_data'][rkey]['customer_count'] = 0
			else:
				redeem_data['store_data'] = []

		if filterkey == 'last 7 days':
			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			today = date.today()
			start_date = today - timedelta(days = 7)

			print(start_date)
			print(end_date)

			get_credited_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and  date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
			get_credited_customer_data = (organisation_id,start_date,end_date)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				credit_data['store_data'] = store_data
				for ckey,cdata in enumerate(credit_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and  date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and wt.`transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,cdata['retailer_store_id'],cdata['retailer_store_store_id'],start_date,end_date)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						credit_data['store_data'][ckey]['customer_count'] = customer_retailer_data['total_user']
					else:
						credit_data['store_data'][ckey]['customer_count'] = 0
					
			else:
				credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,start_date,end_date)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				redeem_data['store_data'] = store_data
				for rkey,rdata in enumerate(redeem_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and wt.`transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,rdata['retailer_store_id'],rdata['retailer_store_store_id'],start_date,end_date)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						redeem_data['store_data'][rkey]['customer_count'] = customer_retailer_data['total_user']
					else:
						redeem_data['store_data'][rkey]['customer_count'] = 0
			else:
				redeem_data['store_data'] = []

		if filterkey == 'this month':
			today = date.today()
			day = '01'
			start_date = today.replace(day=int(day))

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_credited_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and  date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
			get_credited_customer_data = (organisation_id,start_date,end_date)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				credit_data['store_data'] = store_data
				for ckey,cdata in enumerate(credit_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and  date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and wt.`transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,cdata['retailer_store_id'],cdata['retailer_store_store_id'],start_date,end_date)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						credit_data['store_data'][ckey]['customer_count'] = customer_retailer_data['total_user']
					else:
						credit_data['store_data'][ckey]['customer_count'] = 0
					
			else:
				credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,start_date,end_date)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				redeem_data['store_data'] = store_data
				for rkey,rdata in enumerate(redeem_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and wt.`transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,rdata['retailer_store_id'],rdata['retailer_store_store_id'],start_date,end_date)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						redeem_data['store_data'][rkey]['customer_count'] = customer_retailer_data['total_user']
					else:
						redeem_data['store_data'][rkey]['customer_count'] = 0
			else:
				redeem_data['store_data'] = []

		if filterkey == 'lifetime':
			start_date = '2010-07-10'

			now = datetime.now()
			end_date = now.strftime("%Y-%m-%d")

			print(start_date)
			print(end_date)

			get_credited_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and  date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
			get_credited_customer_data = (organisation_id,start_date,end_date)

			count_credited_customer = cursor.execute(get_credited_customer_query,get_credited_customer_data)

			if count_credited_customer > 0:
				credited_customer = cursor.fetchone()
				credit_data['total_customer_count'] = credited_customer['total']
			else:
				credit_data['total_customer_count'] = 0
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				credit_data['store_data'] = store_data
				for ckey,cdata in enumerate(credit_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and  date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and wt.`transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,cdata['retailer_store_id'],cdata['retailer_store_store_id'],start_date,end_date)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						credit_data['store_data'][ckey]['customer_count'] = customer_retailer_data['total_user']
					else:
						credit_data['store_data'][ckey]['customer_count'] = 0
					
			else:
				credit_data['store_data'] = []

			get_redeem_customer_query = ("""SELECT count(distinct(`customer_id`))as total FROM `wallet_transaction` 
				WHERE `organisation_id`=%s and date(`last_update_ts`) >=%s and date(`last_update_ts`) <=%s and `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
			get_redeem_customer_data = (organisation_id,start_date,end_date)

			count_redeem_customer = cursor.execute(get_redeem_customer_query,get_redeem_customer_data)

			if count_redeem_customer > 0:
				redeem_customer = cursor.fetchone()
				redeem_data['total_customer_count'] = redeem_customer['total']
			else:
				redeem_data['total_customer_count'] = 0	
			

			get_store_query = ("""SELECT rs.`retailer_store_id`,rss.`retailer_store_store_id`,rs.`city`, rss.`address`
							from `retailer_store` rs
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_id` = rs.`retailer_store_id` 
							WHERE rs.`organisation_id` = %s """)
			get_store_data = (organisation_id)

			count_store_data = cursor.execute(get_store_query,get_store_data)

			if count_store_data > 0:
				store_data = cursor.fetchall()
				redeem_data['store_data'] = store_data
				for rkey,rdata in enumerate(redeem_data['store_data']):
					get_customer_retailer_query = ("""SELECT  count(distinct(wt.`customer_id`))as total_user 
					FROM `wallet_transaction` wt 
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE ur.`organisation_id`=%s  and wt.`organisation_id` = %s and ur.`retailer_id` = %s and ur.`retailer_store_id` = %s  and date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and wt.`transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
					get_customer_retailer_data = (organisation_id,organisation_id,rdata['retailer_store_id'],rdata['retailer_store_store_id'],start_date,end_date)

					count_customer_retailer_data = cursor.execute(get_customer_retailer_query,get_customer_retailer_data)

					if count_customer_retailer_data > 0:
						customer_retailer_data = cursor.fetchone()
						redeem_data['store_data'][rkey]['customer_count'] = customer_retailer_data['total_user']
					else:
						redeem_data['store_data'][rkey]['customer_count'] = 0
			else:
				redeem_data['store_data'] = []

		get_loyality_master_query = ("""SELECT * FROM `general_loyalty_master` WHERE `organisation_id` = %s """)
		get_loyality_master_data = (organisation_id)
		loyality_master_count = cursor.execute(get_loyality_master_query,get_loyality_master_data)
		if loyality_master_count > 0:
			loyality_data = cursor.fetchone()
			signup_point = str(loyality_data['signup_point'])
			per_transaction_percentage = str(loyality_data['per_transaction_percentage'])
		else:
			signup_point = ""
			per_transaction_percentage = ""


		get_redeem_settings_query = ("""SELECT * FROM `redeem_setting` WHERE `organisation_id` = %s """)
		get_redeem_master_data = (organisation_id)
		redeem_master_count = cursor.execute(get_redeem_settings_query,get_redeem_master_data)
		if redeem_master_count > 0:
			redeem_master_data = cursor.fetchone()
			is_apply_for_online_user = str(redeem_master_data['is_apply_for_online_user'])
			point = str(redeem_master_data['point'])
			point_value_in_rs = str(redeem_master_data['point_value_in_rs'])
		else:
			is_apply_for_online_user = ""
			point = ""
			point_value_in_rs = ""

		get_redeem_value_query = ("""SELECT * FROM `redeem_value` WHERE `organisation_id` = %s """)
		get_redeem_value_data = (organisation_id)
		redeem_value_count = cursor.execute(get_redeem_value_query,get_redeem_value_data)
		if redeem_value_count > 0:
			redeem_value_data = cursor.fetchone()
			maximum_amount_percentage = str(redeem_value_data['maximum_amount_percentage'])
			maximum_amount_absolute_value = str(redeem_value_data['maximum_amount_absolute_value'])			
		else:
			maximum_amount_percentage = ""
			maximum_amount_absolute_value = ""		


		get_loyality_settings_query = ("""SELECT *
				FROM `referal_loyality_settings` rfl				 
				WHERE `organisation_id` = %s""")
		getLoyalitySettingsData = (organisation_id)
		count_Loyality_settings_data = cursor.execute(get_loyality_settings_query,getLoyalitySettingsData)	

		if count_Loyality_settings_data > 0:
			loyality_settings_data = cursor.fetchone()
			setting_value = loyality_settings_data['setting_value']
		else:
			setting_value = 0


		return ({"attributes": {
		    		"status_desc": "Customer Count Details",
		    		"status": "success"
		    	},
		    	"responseList":{"credit_data":credit_data,"redeem_data":redeem_data,"signup_point":signup_point,"per_transaction_percentage":per_transaction_percentage,"is_apply_for_online_user":is_apply_for_online_user,"point":point,"point_value_in_rs":point_value_in_rs,"maximum_amount_percentage":maximum_amount_percentage,"maximum_amount_absolute_value":maximum_amount_absolute_value,"setting_value":setting_value} }), status.HTTP_200_OK

#--------------------Loyality-Dashboard-------------------------#

#--------------------Customer-List-With-Organisation-And-Retailer-Store-Loyality-Dashboard-------------------------#

@name_space.route("/CustomerListWithOrganisationAndRetailStoreFromLoyalityDashboard/<string:filterkey>/<string:list_type>/<int:retailer_store_store_id>/<int:organisation_id>")	
class CustomerListWithOrganisationAndRetailStoreFromLoyalityDashboard(Resource):
	def get(self,filterkey,list_type,retailer_store_store_id,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if list_type == 'credit_data':			

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) =%s and  ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,today_date,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				print(yesterday)		

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) =%s and  ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,yesterday,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []	

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)		

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []		

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)		

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)		

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` != 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []

		if list_type == 'redeem_data':			

			if filterkey == 'today':
				now = datetime.now()
				today_date = now.strftime("%Y-%m-%d")		

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) =%s and  ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,today_date,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s and `transaction_source` = 'redeem'""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []

			if filterkey == 'yesterday':
				today = date.today()

				yesterday = today - timedelta(days = 1)

				print(yesterday)		

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) =%s and  ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,yesterday,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s and `transaction_source` = 'redeem'""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []	

			if filterkey == 'last 7 days':
				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				today = date.today()
				start_date = today - timedelta(days = 7)

				print(start_date)
				print(end_date)		

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s and `transaction_source` = 'redeem'""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []	

			if filterkey == 'this month':
				today = date.today()
				day = '01'
				start_date = today.replace(day=int(day))

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)		

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s and `transaction_source` = 'redeem'""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []

			if filterkey == 'lifetime':
				start_date = '2010-07-10'

				now = datetime.now()
				end_date = now.strftime("%Y-%m-%d")

				print(start_date)
				print(end_date)		

				get_credited_customer_query = ("""SELECT distinct(`customer_id`) FROM `wallet_transaction` wt
					INNER JOIN `user_retailer_mapping` ur ON ur.`user_id` = wt.`customer_id`
					WHERE wt.`organisation_id`=%s and  date(wt.`last_update_ts`) >=%s and date(wt.`last_update_ts`) <=%s and ur.`organisation_id`=%s and ur.`retailer_store_id` = %s and
					 `transaction_source` = 'redeem' and `transaction_source` != 'product_loyalty'""")
				get_credited_customer_data = (organisation_id,start_date,end_date,organisation_id,retailer_store_store_id)
				count_credited_customer_data =  cursor.execute(get_credited_customer_query,get_credited_customer_data)

				if count_credited_customer_data > 0:
					customer_data = cursor.fetchall()

					for key,data in enumerate(customer_data):

						get_registed_customer_query = ("""SELECT a.`admin_id`,concat(a.`first_name`,' ',a.`last_name`)as
							name, a.`phoneno`,a.`dob`,a.`anniversary`,a.`profile_image`,a.`address_line_1`,a.`address_line_2`,a.`city`,a.`country`,
							a.`state`,a.`pincode`,a.`loggedin_status`,a.`date_of_creation`,a.`wallet`
							FROM `admins` a							
							WHERE a.`role_id`=4 and a.`organisation_id` = %s
							and a.`status`=1 and a.`admin_id` = %s""")
						get_registerd_customer_data = (organisation_id,data['customer_id']) 

						count_registerd_customer = cursor.execute(get_registed_customer_query,get_registerd_customer_data)
						print(cursor._last_executed)
						
						registerd_customer_data = cursor.fetchone()

						customer_data[key]['admin_id'] = registerd_customer_data['admin_id']
						customer_data[key]['name'] = registerd_customer_data['name']
						customer_data[key]['phoneno'] = registerd_customer_data['phoneno']
						customer_data[key]['dob'] = registerd_customer_data['dob']
						customer_data[key]['anniversary'] = registerd_customer_data['anniversary']
						customer_data[key]['profile_image'] = registerd_customer_data['profile_image']
						customer_data[key]['address_line_1'] = registerd_customer_data['address_line_1']
						customer_data[key]['address_line_2'] = registerd_customer_data['address_line_2']
						customer_data[key]['city'] = registerd_customer_data['city']
						customer_data[key]['country'] = registerd_customer_data['country']
						customer_data[key]['state'] = registerd_customer_data['state']
						customer_data[key]['pincode'] = registerd_customer_data['pincode']
						customer_data[key]['loggedin_status'] = registerd_customer_data['loggedin_status']
						customer_data[key]['wallet'] = registerd_customer_data['wallet']
						customer_data[key]['date_of_creation'] = str(registerd_customer_data['date_of_creation'])

						get_city_query = ("""SELECT rs.`city` as retailer_city,rss.`address` as retailer_address
							FROM `user_retailer_mapping` ur 
							INNER JOIN `retailer_store` rs ON rs.`retailer_store_id` = ur.`retailer_id` 
							INNER JOIN `retailer_store_stores` rss ON rss.`retailer_store_store_id` = ur.`retailer_store_id`
							where ur.`user_id` = %s and ur.`organisation_id` = %s""")
						get_city_data = (data['customer_id'],organisation_id)
						count_city = cursor.execute(get_city_query,get_city_data)						

						if count_city > 0:
							city_data = cursor.fetchone()
							customer_data[key]['retailer_city'] = city_data['retailer_city']
							customer_data[key]['retailer_address'] = city_data['retailer_address']
						else:
							customer_data[key]['retailer_city'] = ""
							customer_data[key]['retailer_address'] = ""

						get_exchange_count_query = ("""SELECT count(*) exchane_count
													 FROM customer_exchange_device where `customer_id` = %s and `organisation_id` = %s""")
						get_exchange_count_data = (data['customer_id'],organisation_id)
						exchange_count = cursor.execute(get_exchange_count_query,get_exchange_count_data)						

						if exchange_count > 0:
							exchange_count_data =  cursor.fetchone()
							customer_data[key]['exchange_count'] = exchange_count_data['exchane_count']
						else:
							customer_data[key]['exchange_count'] = 0

						get_enquieycount_query = ("""SELECT count(*) enquiery_count
													 FROM enquiry_master where `user_id` = %s and `organisation_id` = %s""")
						get_enquiery_count_data = (data['customer_id'],organisation_id)
						enquiery_count = cursor.execute(get_enquieycount_query,get_enquiery_count_data)

						if enquiery_count > 0:
							enquiery_count_data = cursor.fetchone()
							customer_data[key]['enquiery_count'] = enquiery_count_data['enquiery_count']
						else:
							customer_data[key]['enquiery_count'] = 0

						get_customer_type = ("""SELECT `customer_type` FROM `customer_type` where`customer_id`=%s and `organisation_id`=%s""")
						get_customer_type_data = (data['customer_id'],organisation_id)
						count_customer_type = cursor.execute(get_customer_type,get_customer_type_data)

						if count_customer_type > 0:
							customer_type_data = cursor.fetchone()
							customer_data[key]['customertype'] = customer_type_data['customer_type']
						else:
							customer_data[key]['customertype'] = ""

						customer_data[key]['outstanding'] = 0

						cursor.execute("""SELECT sum(`amount`)as total FROM 
					 		`instamojo_payment_request` WHERE `user_id`=%s and 
					 		`status`='Complete' and `organisation_id` = %s""",(data['customer_id'],organisation_id))
						costDtls = cursor.fetchone()
					
						if costDtls['total'] != None:
							customer_data[key]['purchase_cost'] = costDtls['total']
						else:
							customer_data[key]['purchase_cost'] = 0

						get_source_query = ("""SELECT * FROM `wallet_transaction` wt where `customer_id` = %s and `organisation_id` = %s and `transaction_source` = 'redeem'""")
						get_source_data = (data['customer_id'],organisation_id)
						count_source =  cursor.execute(get_source_query,get_source_data)

						if count_source > 0:
							source_data = cursor.fetchone()
							customer_data[key]['source'] = source_data['transaction_source']
						else:
							customer_data[key]['source'] = ''
				else:
					customer_data = []

		return ({"attributes": {
		    		"status_desc": "Customer Details",
		    		"status": "success"
		    	},
		    	"responseList":customer_data }), status.HTTP_200_OK		

#--------------------Customer-List-With-Organisation-And-Retailer-Store-Loyality-Dashboard-------------------------#


#--------------------Add-General-Loyality-Point-------------------------#

@name_space.route("/AddGeneralLoyalityPoint")
class AddGeneralLoyalityPoint(Resource):
	@api.expect(general_loyality_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		signup_point = details['signup_point']
		per_transaction_percentage = details['per_transaction_percentage']

		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		if details and "category_id" in details:
			category_id = details['category_id']
		else:
			category_id = 0

		if details and "category_percentage" in details:
			category_percentage = details['category_percentage']
		else:
			category_percentage = 0

		if details and "category_high_margine_percentage" in details:
			category_high_margine_percentage = details['category_high_margine_percentage']
		else:
			category_high_margine_percentage = 0

		if details and "category_low_margine_percentage" in details:
			category_low_margine_percentage = details['category_low_margine_percentage']
		else:
			category_low_margine_percentage = 0

		if details and "category_id" in details:
			category_id = details['category_id']
		else:
			category_id = 0

		if details and "sub_category_percentage" in details:
			sub_category_percentage = details['sub_category_percentage']
		else:
			sub_category_percentage = 0

		if details and "sub_category_high_margine_percentage" in details:
			sub_category_high_margine_percentage = details['sub_category_high_margine_percentage']
		else:
			sub_category_high_margine_percentage = 0

		if details and "sub_category_low_margine_percentage" in details:
			sub_category_low_margine_percentage = details['sub_category_low_margine_percentage']
		else:
			sub_category_low_margine_percentage = 0

		if details and "sub_category_id" in details:
			sub_category_id = details['sub_category_id']
		else:
			sub_category_id = 0


		if details and "birthday_bonus" in details:
			birthday_bonus = details['birthday_bonus']
		else:
			birthday_bonus = 0

		if details and "anniversary_bonus" in details:
			anniversary_bonus = details['anniversary_bonus']
		else:
			anniversary_bonus = 0

		if details and "first_purchase_bonus" in details:
			first_purchase_bonus = details['first_purchase_bonus']
		else:
			first_purchase_bonus = 0

		if details and "customer_review_bonus" in details:
			customer_review_bonus = details['customer_review_bonus']
		else:
			customer_review_bonus = 0

		if details and "prebook_loyality_bonus" in details:
			prebook_loyality_bonus = details['prebook_loyality_bonus']
		else:
			prebook_loyality_bonus = 0

		get_query = ("""SELECT `signup_point`,`per_transaction_percentage`
			FROM `general_loyalty_master` WHERE `last_update_id` = %s and organisation_id = %s""")
		get_data = (last_update_id,organisation_id)

		count_general_loyality = cursor.execute(get_query,get_data)

		if count_general_loyality > 0:
			update_query = ("""UPDATE `general_loyalty_master` SET `signup_point` = %s,`per_transaction_percentage` = %s, `category_id` = %s, `category_percentage` = %s, `category_high_margine_percentage` = %s, `category_low_margine_percentage` = %s,`sub_category_id` = %s, `sub_category_percentage` = %s,  `sub_category_high_margine_percentage` = %s, `sub_category_low_margine_percentage` = %s, `birthday_bonus` = %s, `anniversary_bonus` = %s, `first_purchase_bonus` = %s, `customer_review_bonus` = %s, `prebook_loyality_bonus` = %s
					WHERE `last_update_id` = %s and `organisation_id` = %s""")
			update_data = (signup_point,per_transaction_percentage,category_id,category_percentage,category_high_margine_percentage,category_low_margine_percentage,sub_category_id,sub_category_percentage,sub_category_high_margine_percentage,sub_category_low_margine_percentage,birthday_bonus,anniversary_bonus,first_purchase_bonus,customer_review_bonus,prebook_loyality_bonus,last_update_id,organisation_id)
			cursor.execute(update_query,update_data)

			print(cursor._last_executed)
		else:
			general_loyality_status = 1
			insert_query = ("""INSERT INTO `general_loyalty_master`(`signup_point`,`per_transaction_percentage`,`category_id`,`category_percentage`,`category_high_margine_percentage`,`category_low_margine_percentage`,`sub_category_id`,`sub_category_percentage`,`sub_category_high_margine_percentage`,`sub_category_low_margine_percentage`,`birthday_bonus`,`anniversary_bonus`,`first_purchase_bonus`,`customer_review_bonus`,`prebook_loyality_bonus`,`status`,`last_update_id`,`organisation_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

			data = (signup_point,per_transaction_percentage,category_id,category_percentage,category_high_margine_percentage,category_low_margine_percentage,sub_category_id,sub_category_percentage,sub_category_high_margine_percentage,sub_category_low_margine_percentage,birthday_bonus,anniversary_bonus,first_purchase_bonus,customer_review_bonus,prebook_loyality_bonus,general_loyality_status,organisation_id,last_update_id)
			cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "general_loyality_point",
			    		"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#--------------------Add-General-Loyality-Point-------------------------#

#--------------------Add-redeem-Settings-------------------------#
@name_space.route("/AddRedeemSettings")
class AddRedeemSettings(Resource):
	@api.expect(redeem_settings_postmodel)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		is_apply_for_online_user = details['is_apply_for_online_user']
		point = details['point']
		point_value_in_rs = details['point_value_in_rs']
		maximum_amount_percentage = details['maximum_amount_percentage']
		maximum_amount_absolute_value = details['maximum_amount_absolute_value']
		organisation_id = details['organisation_id']
		last_update_id = details['last_update_id']

		get_redeem_settings_query = ("""SELECT `is_apply_for_online_user`,`point`,`point_value_in_rs`
			FROM `redeem_setting` WHERE `last_update_id` = %s and organisation_id = %s""")
		get_redeem_settings_data = (last_update_id,organisation_id)

		count_redeem_settings = cursor.execute(get_redeem_settings_query,get_redeem_settings_data)

		if count_redeem_settings > 0:
			update_redeem_settings_query = ("""UPDATE `redeem_setting` SET `is_apply_for_online_user` = %s,`point` = %s,`point_value_in_rs` = %s
					WHERE `last_update_id` = %s and `organisation_id` = %s""")
			update_redeem_settings_data = (is_apply_for_online_user,point,point_value_in_rs,last_update_id,organisation_id)
			cursor.execute(update_redeem_settings_query,update_redeem_settings_data)

		else:
			redeem_settings_status = 1
			insert_redeem_settings_query = ("""INSERT INTO `redeem_setting`(`is_apply_for_online_user`,`point`,`point_value_in_rs`,`status`,`last_update_id`,`organisation_id`) 
				VALUES(%s,%s,%s,%s,%s,%s)""")

			redeem_settings_data = (is_apply_for_online_user,point,point_value_in_rs,redeem_settings_status,last_update_id,organisation_id)
			cursor.execute(insert_redeem_settings_query,redeem_settings_data)	

		
		get_redeem_value_query = ("""SELECT `maximum_amount_percentage`,`maximum_amount_percentage`
			FROM `redeem_value` WHERE `last_update_id` = %s and organisation_id = %s""")
		get_redeem_value_data = (last_update_id,organisation_id)

		count_redeem_value = cursor.execute(get_redeem_value_query,get_redeem_value_data)

		if count_redeem_value > 0:
			update_redeem_value_query = ("""UPDATE `redeem_value` SET `maximum_amount_percentage` = %s,`maximum_amount_absolute_value` = %s
					WHERE `last_update_id` = %s and `organisation_id` = %s""")
			update_redeem_value_data = (maximum_amount_percentage,maximum_amount_absolute_value,last_update_id,organisation_id)
			cursor.execute(update_redeem_value_query,update_redeem_value_data)

		else:
			redeem_value_status = 1
			insert_redeem_value_query = ("""INSERT INTO `redeem_value`(`maximum_amount_percentage`,`maximum_amount_absolute_value`,`status`,`last_update_id`,`organisation_id`) 
				VALUES(%s,%s,%s,%s,%s)""")

			redeem_value_data = (maximum_amount_percentage,maximum_amount_absolute_value,redeem_value_status,last_update_id,organisation_id)
			cursor.execute(insert_redeem_value_query,redeem_value_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "redeem_setting",
			    		"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK

#--------------------Add-redeem-Settings-------------------------#


#--------------------Redeem-Customer-Wallet-------------------------#
@name_space.route("/redeemCustomerWallet")
class redeemCustomerWallet(Resource):
	@api.expect(redeem_customer_wallet_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		redeem_amount = details['redeem_amount']
		customer_id = details['customer_id']

		if details and "product_id" in details:
			product_id = details['product_id']
		else:
			product_id = 0

		if details and "product_meta_id" in details:
			product_meta_id = details['product_meta_id']
		else:
			product_meta_id = 0

		if details and "offer_id" in details:
			offer_id = details['offer_id']
		else:
			offer_id = 0

		if details and "transaction_id" in details:
			transaction_id = details['transaction_id']
		else:
			transaction_id = 0

		if details and "image" in details:
			image = details['image']
		else:
			image = ""

		if details and "remarks" in details:
			remarks = details['remarks']
		else:
			remarks = ""

		organisation_id =  details['organisation_id']
		last_update_id = details['last_update_id']

		if details["transaction_id"] > 0:

			get_query = ("""SELECT *
				FROM `redeem_history` WHERE `customer_id` = %s and `organisation_id` = %s and `transaction_id` = %s""")
			getData = (customer_id,organisation_id,transaction_id)
			count_redeem = cursor.execute(get_query,getData)

			if count_redeem >0:
				return ({"attributes": {
				    		"status_desc": "redeem_customer_wallet",
				    		"status": "error",
				    		"message":"You have already redeemed this order please select another one."
				    	},
				    	"responseList":{} }), status.HTTP_200_OK
			else:

				insert_redeem_history_query = ("""INSERT INTO `redeem_history`(`customer_id`,`redeem_point`,`product_id`,`product_meta_id`,`offer_id`,`transaction_id`,`image`,
											`remarks`,`organisation_id`,`last_update_id`)
														VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				insert_redeem_history_data = (customer_id,redeem_amount,product_id,product_meta_id,offer_id,transaction_id,image,remarks,organisation_id,last_update_id)
				cursor.execute(insert_redeem_history_query,insert_redeem_history_data)
				redeem_history_id = cursor.lastrowid


				get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s and `organisation_id` = %s""")
				customer_wallet_data = (customer_id,organisation_id)
				cursor.execute(get_customer_wallet_query,customer_wallet_data)
				wallet_data = cursor.fetchone()

				wallet = wallet_data['wallet'] - redeem_amount

				insert_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
											`updated_value`,`transaction_id`,`redeem_history_id`,`organisation_id`,`status`,`last_update_id`)
														VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				transaction_source = "redeem"
				updated_value = wallet
				previous_value = wallet_data['wallet']
				wallet_transation_status = 1
				redeem_history_id = redeem_history_id				
				wallet_transaction_data = (customer_id,redeem_amount,transaction_source,previous_value,updated_value,transaction_id,redeem_history_id,organisation_id,wallet_transation_status,organisation_id)
				cursor.execute(insert_wallet_transaction_query,wallet_transaction_data)


				update_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s WHERE `admin_id` = %s and `organisation_id` = %s""")
				update_data = (wallet,customer_id,organisation_id)
				cursor.execute(update_customer_wallet_query,update_data)

				get_device_query = ("""SELECT `device_token`
											FROM `devices` WHERE  `user_id` = %s and `organisation_id` = %s""")

				get_device_data = (customer_id,organisation_id)
				device_token_count = cursor.execute(get_device_query,get_device_data)

				if device_token_count > 0:
					device_token_data = cursor.fetchone()

					get_organisation_firebase_query = ("""SELECT `firebase_key`
												FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
					get_organisation_firebase_data = (organisation_id)
					cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
					firebase_data = cursor.fetchone()

					headers = {'Content-type':'application/json', 'Accept':'application/json'}
					sendAppPushNotificationUrl = BASE_URL + "ecommerce_retailer_loyality/EcommerceRetailerLoyality/sendAppPushNotificationforRedeemPoint"
					payloadpushData = {
										"device_id":device_token_data['device_token'],
										"firebase_key": firebase_data['firebase_key']
									}

					send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()

		else:
			insert_redeem_history_query = ("""INSERT INTO `redeem_history`(`customer_id`,`redeem_point`,`product_id`,`product_meta_id`,`offer_id`,`transaction_id`,`image`,
											`remarks`,`organisation_id`,`last_update_id`)
														VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			insert_redeem_history_data = (customer_id,redeem_amount,product_id,product_meta_id,offer_id,transaction_id,image,remarks,organisation_id,last_update_id)
			cursor.execute(insert_redeem_history_query,insert_redeem_history_data)
			redeem_history_id = cursor.lastrowid


			get_customer_wallet_query = ("""SELECT `wallet` from `admins` WHERE `admin_id` = %s and `organisation_id` = %s""")
			customer_wallet_data = (customer_id,organisation_id)
			cursor.execute(get_customer_wallet_query,customer_wallet_data)
			wallet_data = cursor.fetchone()

			wallet = wallet_data['wallet'] - redeem_amount

			insert_wallet_transaction_query = ("""INSERT INTO `wallet_transaction`(`customer_id`,`transaction_value`,`transaction_source`,`previous_value`,
											`updated_value`,`transaction_id`,`redeem_history_id`,`organisation_id`,`status`,`last_update_id`)
														VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			transaction_source = "redeem"
			updated_value = wallet
			previous_value = wallet_data['wallet']
			wallet_transation_status = 1
			redeem_history_id = redeem_history_id
			transaction_id = 0
			wallet_transaction_data = (customer_id,redeem_amount,transaction_source,previous_value,updated_value,transaction_id,redeem_history_id,organisation_id,wallet_transation_status,organisation_id)
			cursor.execute(insert_wallet_transaction_query,wallet_transaction_data)


			update_customer_wallet_query = ("""UPDATE `admins` SET `wallet` = %s WHERE `admin_id` = %s and `organisation_id` = %s""")
			update_data = (wallet,customer_id,organisation_id)
			cursor.execute(update_customer_wallet_query,update_data)

			get_device_query = ("""SELECT `device_token`
											FROM `devices` WHERE  `user_id` = %s and `organisation_id` = %s""")

			get_device_data = (customer_id,organisation_id)
			device_token_count = cursor.execute(get_device_query,get_device_data)

			if device_token_count > 0:
				device_token_data = cursor.fetchone()

				get_organisation_firebase_query = ("""SELECT `firebase_key`
												FROM `organisation_firebase_details` WHERE  `organisation_id` = %s""")
				get_organisation_firebase_data = (organisation_id)
				cursor.execute(get_organisation_firebase_query,get_organisation_firebase_data)
				firebase_data = cursor.fetchone()

				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				sendAppPushNotificationUrl = BASE_URL + "ecommerce_retailer_loyality/EcommerceRetailerLoyality/sendAppPushNotificationforRedeemPoint"
				payloadpushData = {
										"device_id":device_token_data['device_token'],
										"firebase_key": firebase_data['firebase_key']
									}

				send_push_notification = requests.post(sendAppPushNotificationUrl,data=json.dumps(payloadpushData), headers=headers).json()			
		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "redeem_customer_wallet",
			    		"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#----------------------Send-Push-Notification---------------------#

@name_space.route("/sendAppPushNotificationforRedeemPoint")
class sendAppPushNotificationforRedeemPoint(Resource):
	@api.expect(appmsg_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		data_message = {
							"title" : "Redeem Point",
							"message": "Redeem Successfully"
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


#--------------------Add-Loyality-Settings-------------------------#

@name_space.route("/AddLoyalitySettings")
class AddLoyalitySettings(Resource):
	@api.expect(loyality_settings_postmodel)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "signup_point" in details:
			signup_point = details['signup_point']
		else:
			signup_point = ""

		if details and "per_transaction_percentage" in details:
			per_transaction_percentage = details['per_transaction_percentage']
		else:
			per_transaction_percentage = ""

		if details and "birthday_bonus" in details:
			birthday_bonus = details['birthday_bonus']
		else:
			birthday_bonus = 0

		if details and "anniversary_bonus" in details:
			anniversary_bonus = details['anniversary_bonus']
		else:
			anniversary_bonus = 0

		if details and "first_purchase_bonus" in details:
			first_purchase_bonus = details['first_purchase_bonus']
		else:
			first_purchase_bonus = 0

		if details and "customer_review_bonus" in details:
			customer_review_bonus = details['customer_review_bonus']
		else:
			customer_review_bonus = 0

		if details and "prebook_loyality_bonus" in details:
			prebook_loyality_bonus = details['prebook_loyality_bonus']
		else:
			prebook_loyality_bonus = 0	


		if details and "e_bill_bonus" in details:
			e_bill_bonus = details['e_bill_bonus']
		else:
			e_bill_bonus = 0			
		
		
		

		organisation_id = details['organisation_id']

		get_query = ("""SELECT `signup_point`,`per_transaction_percentage`
				FROM `general_loyalty_master` WHERE `organisation_id` = %s""")
		get_data = (organisation_id)

		count_general_loyality = cursor.execute(get_query,get_data)

		if count_general_loyality > 0:
			update_query = ("""UPDATE `general_loyalty_master` SET `signup_point` = %s,`per_transaction_percentage` = %s, `birthday_bonus` = %s, `anniversary_bonus` = %s, `first_purchase_bonus` = %s, `customer_review_bonus` = %s, `prebook_loyality_bonus` = %s,`e_bill_bonus` = %s
						WHERE `last_update_id` = %s and `organisation_id` = %s""")
			update_data = (signup_point,per_transaction_percentage,birthday_bonus,anniversary_bonus,first_purchase_bonus,customer_review_bonus,prebook_loyality_bonus,e_bill_bonus,organisation_id,organisation_id)
			cursor.execute(update_query,update_data)
		else:
			general_loyality_status = 1
			insert_query = ("""INSERT INTO `general_loyalty_master`(`signup_point`,`per_transaction_percentage`,`birthday_bonus`,`anniversary_bonus`,`first_purchase_bonus`,`customer_review_bonus`,`prebook_loyality_bonus`,`e_bill_bonus`,`status`,`last_update_id`,`organisation_id`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

			data = (signup_point,per_transaction_percentage,birthday_bonus,anniversary_bonus,first_purchase_bonus,customer_review_bonus,prebook_loyality_bonus,e_bill_bonus,general_loyality_status,organisation_id,organisation_id)
			cursor.execute(insert_query,data)				

		if details and "transactional_loyality" in details:
			transactional_loyality = details['transactional_loyality']

			delete_transactional_loyality_query = ("""DELETE FROM `total_transactional_loyality_settings` WHERE `organisation_id` = %s """)
			delTransactionalLoyalityData = (organisation_id)
			cursor.execute(delete_transactional_loyality_query,delTransactionalLoyalityData)

			for tkey,tdata in enumerate(transactional_loyality):	
				transactional_loyality_status = 1
				transactional_loyality_query = ("""INSERT INTO `total_transactional_loyality_settings`(`greaterthan_transactional_amount`,`lessthan_transactional_amount`,`transactional_bonus`,`organisation_id`,`status`,`last_update_id`)
															VALUES(%s,%s,%s,%s,%s,%s)""")
				insert_transactional_loyality_data = (tdata['greaterthan_transactional_amount'],tdata['lessthan_transactional_amount'],tdata['transactional_bonus'],organisation_id,transactional_loyality_status,organisation_id)
				cursor.execute(transactional_loyality_query,insert_transactional_loyality_data)		
			

		if details and "category_loyality" in details:
			category_loyality = details['category_loyality']

			delete_category_loyality_query = ("""DELETE FROM `category_loyality_settings` WHERE `organisation_id` = %s """)
			delCategoryLoyalityData = (organisation_id)
			cursor.execute(delete_category_loyality_query,delCategoryLoyalityData)

			for key,data in enumerate(category_loyality):	
				category_loyality_status = 1
				insert_category_loyality_query = ("""INSERT INTO `category_loyality_settings`(`category_id`,`category_percentage`,`category_high_margine_percentage`,`category_low_margine_percentage`,`status`,`organisation_id`,`last_update_id`)
															VALUES(%s,%s,%s,%s,%s,%s,%s)""")
				insert_category_loyality_data = (data['category_id'],data['category_percentage'],data['category_high_margine_percentage'],data['category_low_margine_percentage'],category_loyality_status,organisation_id,organisation_id)
				cursor.execute(insert_category_loyality_query,insert_category_loyality_data)

		if details and "sub_category_loyality" in details:
			sub_category_loyality = details['sub_category_loyality']

			delete_sub_category_loyality_query = ("""DELETE FROM `sub_category_loyality_settings` WHERE `organisation_id` = %s """)
			delSubCategoryLoyalityData = (organisation_id)
			cursor.execute(delete_sub_category_loyality_query,delSubCategoryLoyalityData)

			for sclkey,scldata in enumerate(sub_category_loyality):	
				sub_category_loyality_status = 1
				insert_sub_category_loyality_query = ("""INSERT INTO `sub_category_loyality_settings`(`sub_category_id`,`sub_category_percentage`,`sub_category_high_margine_percentage`,`sub_category_low_margine_percentage`,`status`,`organisation_id`,`last_update_id`)
															VALUES(%s,%s,%s,%s,%s,%s,%s)""")
				insert_sub_category_loyality_data = (scldata['sub_category_id'],scldata['sub_category_percentage'],scldata['sub_category_high_margine_percentage'],scldata['sub_category_low_margine_percentage'],sub_category_loyality_status,organisation_id,organisation_id)
				cursor.execute(insert_sub_category_loyality_query,insert_sub_category_loyality_data)

		if details and "referal_loyality" in details:
			referal_loyality = details['referal_loyality']

			delete_referal_loyality_query = ("""DELETE FROM `referal_loyality_settings_master` WHERE `organisation_id` = %s """)
			delReferalLoyalityData = (organisation_id)
			cursor.execute(delete_referal_loyality_query,delReferalLoyalityData)

			for rkey,rdata in enumerate(referal_loyality):	
				referal_loyality_status = 1
				insert_referal_loyality_query = ("""INSERT INTO `referal_loyality_settings_master`(`greaterthan_person_count`,`lessthan_person_count`,`referal_bonus`,`organisation_id`,`status`,`last_update_id`)
															VALUES(%s,%s,%s,%s,%s,%s)""")
				insert_referal_loyality_data = (rdata['greaterthan_person_count'],rdata['lessthan_person_count'],rdata['referal_bonus'],organisation_id,referal_loyality_status,organisation_id)
				cursor.execute(insert_referal_loyality_query,insert_referal_loyality_data)		

		if details and "buyback_loyality" in details:
			buyback_loyality = details['buyback_loyality']
					
			delete_buyback_loyality_query =  ("""DELETE FROM `buy_back_loyality_settings` WHERE `organisation_id` = %s """)
			delBuyBackLoyalityData = (organisation_id)
			cursor.execute(delete_buyback_loyality_query,delBuyBackLoyalityData)

			for bbkey,bbdata in enumerate(buyback_loyality):	
				buyback_loyality_status = 1
				buyback_loyality_query = ("""INSERT INTO `buy_back_loyality_settings`(`greaterthan_transactional_amount`,`lessthan_transactional_amount`,`transactional_bonus`,`organisation_id`,`status`,`last_update_id`)
															VALUES(%s,%s,%s,%s,%s,%s)""")
				insert_buy_back_loyality_data = (bbdata['greaterthan_transactional_amount'],bbdata['lessthan_transactional_amount'],bbdata['transactional_bonus'],organisation_id,buyback_loyality_status,organisation_id)
				cursor.execute(buyback_loyality_query,insert_buy_back_loyality_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "loyality_point",
			    		"status": "success"
			    },
			    "responseList":details}), status.HTTP_200_OK


#--------------------Add-Loyality-Settings-------------------------#

#---------------------------Get-Loyality-Settings------------------------------------#

@name_space.route("/getLoyalitySettings/<int:organisation_id>")	
class getLoyalitySettings(Resource):
	def get(self,organisation_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_loyality_settings_query = ("""SELECT `signup_point`,`per_transaction_percentage`,`birthday_bonus`,`anniversary_bonus`,`first_purchase_bonus`,
												`customer_review_bonus`,`prebook_loyality_bonus`,`e_bill_bonus` from `general_loyalty_master` WHERE `organisation_id` = %s""")
		get_loyality_settings_data = (organisation_id)
		loyality_settings_count = cursor.execute(get_loyality_settings_query,get_loyality_settings_data)

		if loyality_settings_count > 0:
			loyality_settings_data = cursor.fetchone()			
		else:
			loyality_settings_data = {}

		get_category_loyality_settings_query = ("""SELECT cls.*,mkm.`meta_key` FROM `category_loyality_settings` cls
												 INNER JOIN `meta_key_master` mkm ON mkm.`meta_key_id` = cls.`category_id`
												 where cls.`organisation_id` = %s order by cls.`category_loyality_id` asc""")
		get_category_loyality_settings_data = (organisation_id)
		category_loyality_settings_count = cursor.execute(get_category_loyality_settings_query,get_category_loyality_settings_data)
		if category_loyality_settings_count > 0:
			category_loyality = cursor.fetchall()

			for ckey,cdata in enumerate(category_loyality):
				category_loyality[ckey]['last_update_ts'] = str(cdata['last_update_ts'])

			loyality_settings_data['category_loyality'] = category_loyality
		else:
			loyality_settings_data['category_loyality'] = []

		get_sub_category_loyality_settings_query = ("""SELECT scls.*,mkvm.`meta_key_value` FROM `sub_category_loyality_settings` scls
													INNER JOIN `meta_key_value_master` mkvm ON mkvm.`meta_key_value_id` = scls.`sub_category_id`
													where scls.`organisation_id` = %s order by scls.`sub_category_loyality_id` asc""")
		get_sub_category_loyality_settings_data = (organisation_id)
		sub_category_loyality_settings_count = cursor.execute(get_sub_category_loyality_settings_query,get_sub_category_loyality_settings_data)
		if sub_category_loyality_settings_count > 0:
			sub_category_loyality = cursor.fetchall()

			for sckey,scdata in enumerate(sub_category_loyality):
				sub_category_loyality[sckey]['last_update_ts'] = str(scdata['last_update_ts'])
				
			loyality_settings_data['sub_category_loyality'] = sub_category_loyality
		else:
			loyality_settings_data['sub_category_loyality'] = []



		get_referal_loyality_settings_query = ("""SELECT * FROM `referal_loyality_settings_master` where `organisation_id` = %s order by `referal_loyality_settings_id` asc""")
		get_referal_loyality_settings_data = (organisation_id)
		referal_loyality_settings_count = cursor.execute(get_referal_loyality_settings_query,get_referal_loyality_settings_data)

		if referal_loyality_settings_count > 0:
			referal_loyality = cursor.fetchall()					

			for rkey,rdata in enumerate(referal_loyality):
				referal_loyality[rkey]['last_update_ts'] = str(rdata['last_update_ts'])
				
			loyality_settings_data['referal_loyality'] = referal_loyality
		else:
			loyality_settings_data['referal_loyality'] = []


		get_transactional_loyality_settings_query = ("""SELECT * FROM `total_transactional_loyality_settings` where `organisation_id` = %s order by `total_transactional_loyality_id` asc""")
		get_transactional_loyality_settings_data = (organisation_id)
		transactional_loyality_settings_count = cursor.execute(get_transactional_loyality_settings_query,get_transactional_loyality_settings_data)

		if transactional_loyality_settings_count > 0:
			transactional_loyality = cursor.fetchall()			

			for tkey,tdata in enumerate(transactional_loyality):
				transactional_loyality[tkey]['last_update_ts'] = str(tdata['last_update_ts'])
				
			loyality_settings_data['transactional_loyality'] = transactional_loyality
		else:
			loyality_settings_data['transactional_loyality'] = []

		get_buyback_loyality_settings_query = ("""SELECT * FROM `buy_back_loyality_settings` where `organisation_id` = %s order by `buy_back_loyality_id` asc""")
		get_buyback_loyality_settings_data = (organisation_id)
		buyback_loyality_settings_count = cursor.execute(get_buyback_loyality_settings_query,get_buyback_loyality_settings_data)

		if buyback_loyality_settings_count > 0:
			buyback_loyality = cursor.fetchall()			

			for bbkey,bbdata in enumerate(buyback_loyality):
				buyback_loyality[bbkey]['last_update_ts'] = str(bbdata['last_update_ts'])
				
			loyality_settings_data['buyback_loyality'] = buyback_loyality
		else:
			loyality_settings_data['buyback_loyality'] = []

		get_loyality_sms_query = ("""SELECT count(*) as total_loyality_sms FROM `otp_sms` where `organisation_id` = %s and `title` = 'loyality' """)
		get_loyality_sms_data = (organisation_id)
		loyality_sms_count = cursor.execute(get_loyality_sms_query,get_loyality_sms_data)

		if loyality_sms_count > 0:
			loyality_sms_data = cursor.fetchone()	
			loyality_settings_data['sms_count'] = loyality_sms_data['total_loyality_sms']
		else:
			loyality_settings_data['sms_count'] = 0



		return ({"attributes": {
			    		"status_desc": "loyality_settings",
			    		"status": "success"
			    },
			    "responseList":loyality_settings_data}), status.HTTP_200_OK	

#---------------------------Get-Loyality-Settings------------------------------------#





