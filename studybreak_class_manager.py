from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from database_connections import study_break
import requests
import calendar
import json
from threading import Thread
import time

app = Flask(__name__)
cors = CORS(app)

class_manager_section = Blueprint('class_manager_api', __name__)
api = Api(class_manager_section,  title='StudyBreak API',description='StudyBreak API')
name_space = api.namespace('StudyBreak',description='StudyBreak')


create_group_model = api.model('create_group_model',{
	"institution_id":fields.Integer(),
	"group_name":fields.String(),
	"last_update_id":fields.Integer()
	})

update_group_model = api.model('update_group_model',{
	"group_id":fields.Integer(),
	"group_name":fields.String(),
	"last_update_id":fields.Integer()
	})

delete_group_model = api.model('delete_group_model',{
	"group_id":fields.Integer()
	})

student_id_model = api.model('student_id_model',{
	"student_id":fields.Integer()
	})
add_student_to_group_model = api.model('add_student_to_group_model',{
	"group_id":fields.Integer(),
	"last_update_id":fields.Integer(),
	"student_ids":fields.List(fields.Nested(student_id_model))
	})

@name_space.route("/createGroup")
class createGroup(Resource):
	@api.expect(create_group_model)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		institution_id = details.get('institution_id')
		group_name = details.get('group_name')
		last_update_id = details.get('last_update_id')

		data = cursor.execute("""INSERT INTO `group_master`(`institution_id`,`group_name`,`last_update_id`) VALUES(%s,%s,%s)""",
			(institution_id,group_name,last_update_id))
		if data:
			details['group_id'] = cursor.lastrowid
			msg = "Created"
		else:
			details['group_id'] = 0
			msg = "Not Created"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Group Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

@name_space.route("/getGroups/<int:institution_id>")
class getGroups(Resource):
	def get(self, institution_id):
		connection = study_break()
		cursor = connection.cursor()

		qry = ("""SELECT `group_id`,`group_name`,`last_update_ts` as 'created_on' FROM `group_master` WHERE `institution_id` = %s""")
		cursor.execute(qry,(institution_id))

		data = cursor.fetchall()
		for group in data:
			group['created_on'] = group['created_on'].isoformat()
			cursor.execute("""SELECT COUNT(`mapping_id`) as 'count' FROM `group_student_mapping` WHERE `group_id` = %s""",group['group_id'])
			group['total_students'] = cursor.fetchone()['count']

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Group Details",
                                "status": "success",
	                                },
	             "responseList": data}), status.HTTP_200_OK

@name_space.route("/updateGroup")
class updateGroup(Resource):
	@api.expect(update_group_model)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		group_id = details.get('group_id')
		group_name = details.get('group_name')
		last_update_id = details.get('last_update_id')

		data = cursor.execute("""UPDATE `group_master` SET `group_name`=%s,`last_update_id`=%s WHERE `group_id` = %s""",
			(group_name,last_update_id,group_id))
		if data:
			msg = "Updated"
		else:
			msg = "Not Updated"
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Group Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

@name_space.route("/deleteGroup")
class deleteGroup(Resource):
	@api.expect(delete_group_model)
	def delete(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		group_id = details.get('group_id')
		data = cursor.execute("""DELETE FROM `group_master` WHERE `group_id`=%s""",(group_id))

		if data:
			msg = "Deleted"
		else:
			msg = "Not Deleted"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Group Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

@name_space.route("/addStudentToGroup")
class addStudentToGroup(Resource):
	@api.expect(add_student_to_group_model)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		group_id = details.get('group_id')
		last_update_id = details.get('last_update_id')
		student_list = details.get('student_ids')
		for student in student_list:
			cursor.execute("""SELECT `mapping_id` FROM `group_student_mapping` WHERE `group_id`=%s AND `student_id`=%s""",(group_id,student['student_id']))
			temp = cursor.fetchone()
			#print(temp)
			if temp == None:
				cursor.execute("""INSERT INTO `group_student_mapping`(`group_id`,`student_id`,`last_update_id`) VALUES(%s,%s,%s)""",
					(group_id,student['student_id'],last_update_id))

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Group Details",
                                "status": "success",
	                                },
	             "responseList": details}), status.HTTP_200_OK


@name_space.route("/getGroupStudents/<int:group_id>")
class getGroupStudents(Resource):
	def get(self, group_id):
		connection = study_break()
		cursor = connection.cursor()

		qry = ("""SELECT gsm.`mapping_id`,gsm.`student_id`,CONCAT(uc.`first_name`,' ',uc.`last_name`) as 'name',uc.`email_id`,uc.`phone_no`,
			uc.`imageurl`,uc.`address` FROM `group_student_mapping` gsm INNER JOIN `user_credential` uc ON 
			gsm.`student_id` = uc.`user_id` WHERE `group_id`=%s""")

		cursor.execute(qry,(group_id))
		data = cursor.fetchall()

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Group Student Details",
                                "status": "success",
	                                },
	             "responseList": data}), status.HTTP_200_OK
last_update_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

add_student_model = api.model('add_student_model',{
	"first_name":fields.String(),
	"middle_name":fields.String(),
	"last_name":fields.String(),
	"user_role":fields.String(),
	"email_id":fields.String(),
	"phone_no":fields.String(),
	"username":fields.String(),
	"password":fields.String(),
	"imageurl":fields.String(),
	"address":fields.String(),
	"last_update_id":fields.Integer()
	})

@name_space.route("/addStudent")
class addStudent(Resource):
	@api.expect(add_student_model)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		first_name = details.get("first_name")
		middle_name = details.get("middle_name")
		last_name = details.get("last_name")
		user_role = details.get("user_role")
		email_id = details.get("email_id")
		phone_no = details.get("phone_no")
		username = details.get("username")
		password = details.get("password")
		imageurl = details.get("imageurl")
		address = details.get("address")
		last_update_id = details.get("last_update_id")

		qry = ("""INSERT INTO `user_credential`(`first_name`,`middle_name`,`last_name`,`user_role`,`email_id`,`phone_no`,`username`,`password`,`imageurl`,
			`address`,`addition_last_update_ts`,`last_update_id`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		qrydata = (first_name,middle_name,last_name,user_role,email_id,phone_no,username,password,imageurl,address,last_update_ts,last_update_id)

		checkdata = cursor.execute(qry,qrydata)

		if checkdata:
			msg = "Added"
		else:
			msg = "Not Added"
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Add Student Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

@name_space.route("/getStudents/<int:institution_id>")
class getStudents(Resource):
	def get(self,institution_id):
		connection = study_break()
		cursor = connection.cursor()

		qry = ("""SELECT `user_id`,`first_name`,`middle_name`,`last_name`,`email_id`,`phone_no`,`username`,`password`,`imageurl`,
			`address` FROM `user_credential` WHERE `institution_id` = %s AND `user_role` = 'S1'""")
		cursor.execute(qry,institution_id)

		data = cursor.fetchall()

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Student Details",
                                "status": "success"
	                                },
	             "responseList": data}), status.HTTP_200_OK
