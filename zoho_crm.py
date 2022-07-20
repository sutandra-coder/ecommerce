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
from werkzeug.utils import secure_filename
import requests
import calendar
import json
from zcrmsdk import ZCRMRestClient, ZohoOAuth, ZCRMRecord, ZCRMOrganization, ZCRMModule, ZCRMUser, ZCRMException
#import zcrmsdk




config = {
	"sandbox":"True",
	"applicationLogFilePath":"./Log",
	"client_id":"1000.NA65BVNJ4FV739VJIK2B6UPAM502ZR",
	"client_secret":"36e3a79d9e6b0e108e0f5712a95f512365a9d3c1e5",
	"redirect_uri":"http://www.retail360.in/",
	"accounts_url":"https://accounts.zoho.in",
	"apiBaseUrl":"https://www.zohoapis.in",
	"token_persistence_path":".",
	"currentUserEmail":"sklcard2@gmail.com"
}

app = Flask(__name__)
cors = CORS(app)

zoho_crm = Blueprint('zoho_crm_api', __name__)
api = Api(zoho_crm,  title='Zoho Crm API',description='Zoho Crm API')
name_space = api.namespace('ZohoCrm',description='Zoho Crm')

record_postmodel = api.model('record_postmodel',{	
	"First_Name":fields.String(required=True),	
	"Last_Name":fields.String(required=True),
	"Company":fields.String(required=True)
})

record_putmodel = api.model('record_putmodel',{	
	"First_Name":fields.String(required=True),	
	"Last_Name":fields.String(required=True),
	"Company":fields.String(required=True),
	"Email":fields.String(required=True)
})

#----------------------Get-Record---------------------#

@name_space.route("/getRecordByLeadId")	
class getRecordByLeadId(Resource):
	def get(self):
		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.3d176a55695026573c83c59f269d8c25.5acb817847ac5c51359593142781b611"
		#oauth_tokens = oauth_client.generate_access_token(grant_token)
		userEmail = "sanjoy@myelsa.io"

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)
		#ZCRMRestClient.initialize(config)
		#oAuth_client = ZohoOAuth.get_client_instance()
		#resp = ZCRMOrganization.get_all_users(1,20)

		lead_record_instance = ZCRMRecord.get_instance('Leads',4780282000000333418)
		lead_response = lead_record_instance.get()
		print(lead_response.data)
		print(lead_response.data.field_data)
		print(json.dumps(lead_response.data.field_data))
		#print(resp)

		#resp = ZCRMOrganization.get_instance().get_user(4780282000000333418)
		#print(resp.data)

#----------------------Get-Record---------------------#


#----------------------Create-Record---------------------#

@name_space.route("/createRecord")
class createRecord(Resource):
	@api.expect(record_postmodel)
	def post(self):
		try:
			details = request.get_json()

			ZCRMRestClient.initialize(config)
			oauth_client = ZohoOAuth.get_client_instance()
			grant_token = "1000.d2e01f70fc1edfd654c16c6ffa260505.f0edc9c2ebea9fbdf8a0cff351d21b15"
			
			userEmail = "ojha.rk79@gmail.com"

			#oauth_tokens = oauth_client.generate_access_token(grant_token)

			oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

			print(oauth_tokens)

			First_Name = "Pramit"
			Last_Name = "Ghosh"			

			record = ZCRMRecord.get_instance('Contacts')  # Module API Name
			record.set_field_value('First_Name', First_Name)		
			record.set_field_value('Last_Name', Last_Name)			

			resp = record.create()

			print(resp.details)			

			return ({"attributes": {
			    		"status_desc": "product_details",
			    		"status": "success"
			    	},
			    	"responseList":resp.details}), status.HTTP_200_OK

		except ZCRMException as ex:
			print(ex.status_code)
			print(ex.error_message)
			print(ex.error_code)
			print(ex.error_details)
			print(ex.error_content)


#----------------------Create-Record---------------------#

#----------------------Delete-Record---------------------#

@name_space.route("/deleteRecord")	
class deleteMetaKeyValue(Resource):
	def delete(self):
		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.422b499937c547e035175f3b96a846a9.79514312409a12abb68e42449f6178a9"

		userEmail = "sutandra.mazumder@gmail.com"

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)
		record = ZCRMRecord.get_instance('Leads', 4819682000000363001) # module api name and record id

		resp = record.delete()
		print(resp.status_code)
		print(resp.code)
		print(resp.details)
		print(resp.message)
		print(resp.status)


#----------------------Delete-Record---------------------#

#----------------------Update-Record---------------------#

@name_space.route("/updateRecord")	
class updateRecord(Resource):
	@api.expect(record_putmodel)
	def put(self):
		details = request.get_json()

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.422b499937c547e035175f3b96a846a9.79514312409a12abb68e42449f6178a9"
		
		userEmail = "sutandra.mazumder@gmail.com"

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)
		First_Name = details['First_Name']
		Last_Name = details['Last_Name']
		Company = details['Company']
		Email = details['Email']

		record = ZCRMRecord.get_instance('Leads', 4819682000000363001)  # Module API Name
		#record.set_field_value('id', 4819682000000363001)
		record.set_field_value('Email', Email)
		record.set_field_value('Last_Name', Last_Name)
		record.set_field_value('Company', Company)

		# Actions to be triggered
		trigger = ["approval", "workflow", "blueprint"]
		# Process to be run
		process = ["review_process"]

		resp = record.update()
		print(resp.status_code)
		print(resp.code)
		print(resp.details)
		print(resp.message)
		print(resp.status)
		print(resp.data.entity_id)
		print(resp.data.created_by.id)
		print(resp.data.created_time)


#----------------------Update-Record---------------------#

#----------------------Get-Record---------------------#

@name_space.route("/getAllRecords")	
class getAllRecords(Resource):
	def get(self):
		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.422b499937c547e035175f3b96a846a9.79514312409a12abb68e42449f6178a9"
		userEmail = "sutandra.mazumder@gmail.com"

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)
		#ZCRMRestClient.initialize(config)
		#oAuth_client = ZohoOAuth.get_client_instance()
		#resp = ZCRMOrganization.get_all_users(1,20)

		#lead_record_instance = ZCRMRecord.get_instance('Leads')
		#lead_response = lead_record_instance.get_records()
		#print(lead_response.data)
		#print(lead_response.data.field_data)
		#print(json.dumps(lead_response.data.field_data))
		#print(resp)

		#resp = ZCRMOrganization.get_instance().get_user(4780282000000333418)
		#print(resp.data)

		module_ins = ZCRMModule.get_instance('Leads')

		request_headers = dict()
		request_headers['If-Modified-Since'] = '2019-10-10T10:10:10+05:30'
		
		additional_parameters = dict()
		additional_parameters['approved'] = 'true'
		
		resp = module_ins.get_records(custom_headers=request_headers, custom_parameters=additional_parameters)  # Adding custom headers and parameters
		print(resp.status_code)

		record_ins_arr = resp.data

		response = []

		for key,record_ins in enumerate(record_ins_arr):		
			response.append({'Full_Name':record_ins.get_field_value('Full_Name')})



		return ({"attributes": {
			    		"status_desc": "Record List",
			    		"status": "success",
			    		"message":""
			    	},
			    	"responseList": response}), status.HTTP_200_OK

		#for record_ins in record_ins_arr:
			 #print(record_ins.get_field_value('Full_Name'))

#----------------------Get-Record---------------------#

#----------------------Create-Invoice---------------------#

@name_space.route("/createInvoice")
class createInvoice(Resource):
	@api.expect(record_postmodel)
	def post(self):
		details = request.get_json()

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.422b499937c547e035175f3b96a846a9.79514312409a12abb68e42449f6178a9"
		
		userEmail = "sutandra.mazumder@gmail.com"

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)		

		record = ZCRMRecord.get_instance('Invoices')  # Module API Name
		record.set_field_value('Subject','Invoice name')  # This method use to set FieldApiName and value similar to all other FieldApis and Custom field
		record.set_field_value('Account_Name', 'account_name')
		record.set_field_value('Price_Book_Name', 'book_name')
		record.set_field_value('Pricing_Model', 'Flat')
		record.set_field_value('Event_Title', 'Title')
		record.set_field_value('Start_DateTime', '2018-09-04T15:52:21+05:30')
		record.set_field_value('End_DateTime', '2019-01-04T15:52:21+05:30')
		record.set_field_value('Product_Name', 'product_name1')
		#user = ZCRMUser.get_instance(4819682000000365005, 'user name')  # user id and user name
		#record.set_field_value('Owner', user)		

		resp = record.create()
		print(resp.status_code)
		print(resp.code)
		print(resp.details)
		print(resp.message)
		print(resp.status)

#----------------------Create-Invoice---------------------#

#----------------------Create-Product---------------------#

@name_space.route("/createProduct")
class createInvoice(Resource):
	@api.expect(record_postmodel)
	def post(self):
		details = request.get_json()

		ZCRMRestClient.initialize(config)
		oauth_client = ZohoOAuth.get_client_instance()
		grant_token = "1000.b528706bbf9c39b9ec5ab17e20305faf.33614f846260714cffe3e3a01db50808"
		
		userEmail = "sutandra.mazumder@gmail.com"
		#oauth_tokens = oauth_client.generate_access_token(grant_token)

		oauth_tokens = oauth_client.generate_access_token_from_refresh_token(grant_token,userEmail)

		print(oauth_tokens)
