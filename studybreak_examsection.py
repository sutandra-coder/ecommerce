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

exam_section = Blueprint('exam_api', __name__)
api = Api(exam_section,  title='StudyBreak API',description='StudyBreak API')
name_space = api.namespace('StudyBreak',description='StudyBreak')


createexam = api.model('createexam', {
	"name":fields.String(),
	"type":fields.String(),
	"module_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"fullmarks":fields.Integer(),
	"duration":fields.Integer(),
	"topic_id":fields.Integer(),
	"subtopic_id":fields.Integer()
	})

examsection = api.model('examsection', {
	"exam_id":fields.Integer(),
	"name":fields.String(),
	"sectiontype":fields.String(),
	"duration":fields.Integer(),
	"marks":fields.Integer(),
	"sequence":fields.Integer(),
	"warning_time":fields.Float()
	})

addtopic = api.model('addtopic', {
	"topic_name":fields.String(),
	"teacher_id":fields.Integer()
	})

addsubtopic = api.model('addsubtopic', {
	"topic_id":fields.Integer(),
	"subtopic_name":fields.String()
	})

questionset = api.model('questionset', {
	"teacher_id":fields.Integer(),
	"set_name":fields.String(),
	"display_name":fields.String()
	})

instructions = api.model('instructions', {
	"instructions":fields.String(),
	"instruction_filepath":fields.String(),
	"instruction_filename":fields.String(),
	"instruction_filetype":fields.String()
	})

instructiondtls = api.model('instructiondtls', {
	"exam_id":fields.Integer(),
	"instructions": fields.List(fields.Nested(instructions))
	})

add_options = api.model('options',{
	"Option":fields.String(),
	"Content_file_path":fields.String(),
	"Content_FileName":fields.String(),
	"File_Type":fields.String()
	})

add_resource = api.model('resource',{
	"resource_type":fields.String(),
	"description":fields.String(),
	"sequence":fields.Integer()
	})

add_que = api.model('questions', {
	"question_type":fields.String(),
	"exam_id":fields.Integer(),
	"section_id":fields.Integer(),
	"set_id":fields.Integer(),
	"marks":fields.Float(),
	"negative_marks":fields.Float(),
	"unanswered_marks":fields.Float(),
	"difficulty_level":fields.String(),
	"solution":fields.String(),
	"option_available":fields.String(),
	"calculator_available":fields.String(),
	"teacher_id":fields.Integer(),
	"option_flag":fields.String(),
	"answer":fields.String(),
	"answer_text_without_option":fields.String(),
	"topic_id":fields.Integer(),
	"subtopic_id":fields.Integer(),
	"resources": fields.List(fields.Nested(add_resource)),
	"options": fields.List(fields.Nested(add_options))
	})

settingsdata = api.model('settingsdata', {
	"exam_id":fields.Integer(),
	"section_id":fields.Integer(),
	"topicset_level":fields.String(),
	"topic_id":fields.Integer(),
	"subtopicset_level":fields.String(),
	"subtopic_id":fields.Integer(),
	"calculatorset_level":fields.String(),
	"calculator_available":fields.String(),
	"marksset_level":fields.String(),
	"marks":fields.Float(),
	"negative_marksset_level":fields.String(),
	"negative_marks":fields.Float(),
	"unanswered_marks_set_level":fields.String(),
	"unanswered_marks":fields.Float(),
	"difficulty_set_level":fields.String(),
	"difficulty_level":fields.String(),
	"paper_attempts":fields.Integer(),
	"pause_paper":fields.String(),
	"navigable_section":fields.String(),
	"submit":fields.String()
	})

difflevel = api.model('difflevel', {
	"difficulty_level":fields.String()
})

update_resource = api.model('update_resource',{
	"resource_id":fields.Integer(),
	"question_id":fields.Integer(),
	"set_id":fields.Integer(),
	"resource_type":fields.String(),
	"description":fields.String(),
	"sequence":fields.Integer()
	})

update_que = api.model('update_que', {
	"resources": fields.List(fields.Nested(update_resource)),
	})

update_option_model = api.model('update_option_model',{
	"Option_ID":fields.Integer(),
	"Option":fields.String(),
	"Option_Sequence_ID":fields.Integer(),
	"Content_file_path":fields.String(),
	"Content_FileName":fields.String(),
	"File_Type":fields.String()
	})

update_instruction_model = api.model('update_instruction_model',{
	"instruction_id":fields.Integer(),
	"instructions":fields.String(),
	"instruction_sequence_id":fields.Integer(),
	"instruction_filepath":fields.String(),
	"instruction_filename":fields.String(),
	"instruction_filetype":fields.String()
	})

final_submit_model = api.model('final_submit_model',{
	"exam_id":fields.Integer(),
	"start_date":fields.String(),
	"end_date":fields.String(),
	"start_time":fields.String(),
	"end_time":fields.String(),
	"group_ids":fields.List(fields.Integer()),
	"student_ids":fields.List(fields.Integer()),
	"submit":fields.String(),
	"paper_pause":fields.String(),
	"exam_link":fields.String(),
	"unattemped_theshold":fields.Integer(),
	"last_update_id":fields.Integer()
	})

update_set_model = api.model('update_set_model',{
	"set_id":fields.Integer(),
	"set_name":fields.String(),
	"display_name":fields.String()
	})

update_question_model = api.model('update_question_model',{
	"quetion_type":fields.String(),
	"marks":fields.String(),
	"negative_marks":fields.String(),
	"unanswered_marks":fields.String(),
	"difficulty_level":fields.String(),
	"solution":fields.String(),
	"answer_text_without_option":fields.String(),
	"option_available":fields.String(),
	"calculator_available":fields.String(),
})

BASE_URL = "http://ec2-18-191-151-105.us-east-2.compute.amazonaws.com/flaskapp/"


@name_space.route("/updateSet")
class updateSet(Resource):
	@api.expect(update_set_model)
	def put(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		set_id = details['set_id']
		set_name = details.get('set_name')
		display_name = details.get('display_name')

		if set_name:
			cursor.execute("""UPDATE `question_set` SET `set_name`=%s WHERE `set_id`=%s""",(set_name,set_id))

		if display_name:
			cursor.execute("""UPDATE `question_set` SET `display_name`=%s WHERE `set_id`=%s""",(display_name,set_id))

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Set Updated",
                                "status": "success",
	                                },
	             "responseList": details}), status.HTTP_200_OK


#----------------------------------------------------#
@name_space.route("/CreateExam")
class CreateExam(Resource):
	@api.expect(createexam)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		name = details.get('name')
		examtype = details.get('type')
		module_id = details.get('module_id')
		teacher_id = details.get('teacher_id')
		fullmarks = details.get('fullmarks')
		duration = details.get('duration')
		topic_id = details.get('topic_id')
		subtopic_id = details.get('subtopic_id')

		exam_query = ("""INSERT INTO `exam_master`(`type`,`name`,module_id,
			`teacher_id`,`fullmarks`,`duration`,topic_id,subtopic_id)
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
		exam_data = (examtype,name,module_id,teacher_id,fullmarks,duration,
			topic_id,subtopic_id)
		examdata = cursor.execute(exam_query,exam_data)

		if examdata:
			exam_id = cursor.lastrowid
			details['exam_id'] = exam_id
			msg = "Added"
		else:
			msg = "Not Added"
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Exam Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#			
@name_space.route("/ExamDtlsByTeacherId/<int:teacher_id>")	
class ExamDtlsByTeacherId(Resource):
	def get(self,teacher_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT exam_id,type,name,em.`module_id`,
        	module_name,teacher_id,fullmarks,duration,topic_id,
        	subtopic_id,em.`last_update_ts` FROM `exam_master` em inner join 
			`module_master` mm on em.`module_id`=mm.`module_id` WHERE 
			`teacher_id`=%s  ORDER BY `exam_id` DESC""",(teacher_id))

		examdtls = cursor.fetchall()
		for i in range(len(examdtls)):

			if examdtls:
				examdtls[i]['last_update_ts'] = examdtls[i]['last_update_ts'].isoformat()
			else:
				examdtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Exam Details",
		    		"status": "success"
		    	},
		    	"responseList":examdtls}), status.HTTP_200_OK

#----------------------------------------------------#
@name_space.route("/CreateExamSection")
class CreateExamSection(Resource):
	@api.expect(examsection)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details.get('exam_id')
		name = details.get('name')
		sectiontype = details.get('sectiontype')
		duration = details.get('duration')
		sequence = details.get('sequence')
		marks = details.get('marks')
		warning_time = details.get('warning_time')

		section_query = ("""INSERT INTO `exam_section_master`(`exam_id`,
			`name`, `sequence`, `marks`,`section_type`,duration,`warning_time`) 
			VALUES(%s,%s,%s,%s,%s,%s,%s)""")
		section_data = (exam_id,name,sequence,marks,sectiontype,duration,warning_time)
		sectiondata = cursor.execute(section_query,section_data)

		if sectiondata:
			section_id = cursor.lastrowid
			details['section_id'] = section_id

			msg = "Added"
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Exam Section Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK
			
#--------------------------------------------------------#
@name_space.route("/ExamSectionDtlsByExamId/<int:exam_id>")	
class ExamSectionDtlsByExamId(Resource):
	def get(self,exam_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `section_id`,esm.`exam_id`,esm.`name`,`sequence`,`marks`,`section_type`,esm.`duration`,`warning_time`,
			esm.`last_update_ts`,fullmarks as exam_marks FROM `exam_section_master` esm INNER join `exam_master` em on esm.`exam_id`=em.`exam_id`
			where esm.`exam_id`=%s""",(exam_id))

		sectiondtls = cursor.fetchall()
		for i in range(len(sectiondtls)):

			if sectiondtls:
				sectiondtls[i]['last_update_ts'] = sectiondtls[i]['last_update_ts'].isoformat()
				cursor.execute("""SELECT SUM(`marks`)as total_quemarks FROM `question` where `section_id`=%s""",(sectiondtls[i]['section_id']))

				quemarksdtls = cursor.fetchone()
				if quemarksdtls['total_quemarks'] == None:
					sectiondtls[i]['total_quemarks'] = 0
				else:
					sectiondtls[i]['total_quemarks'] = quemarksdtls['total_quemarks']
			else:
				sectiondtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Exam Section Details",
		    		"status": "success"
		    	},
		    	"responseList":sectiondtls}), status.HTTP_200_OK

		
#------------------------------------------------------#
@name_space.route("/AddTopic")
class AddTopic(Resource):
	@api.expect(addtopic)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		topic_name = details.get('topic_name')
		teacher_id = details.get('teacher_id')

		cursor.execute("""SELECT * FROM `topic` WHERE UPPER(TRIM(`topic_name`))=%s""",(topic_name.strip().upper()))
		chktopic = cursor.fetchone()

		if chktopic == None:
			topic_query = ("""INSERT INTO `topic`(`topic_name`,last_update_id) 
				VALUES(%s,%s)""")
			
			topicdata = cursor.execute(topic_query,(topic_name,teacher_id))

			if topicdata:
				topic_id = cursor.lastrowid
				details['topic_id'] = topic_id

				msg = "Added"
			else:

				msg = "Not added"
		else:
			msg = "Already exists"
			details['topic_id'] = chktopic['topic_id']

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Topic Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#			
@name_space.route("/TopicListByTeacherId/<int:teacher_id>")	
class TopicListByTeacherId(Resource):
	def get(self,teacher_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `topic` WHERE 
			`last_update_id`=%s""",(teacher_id))

		topicdtls = cursor.fetchall()
		for i in range(len(topicdtls)):

			if topicdtls:
				topicdtls[i]['last_update_ts'] = topicdtls[i]['last_update_ts'].isoformat()
			else:
				topicdtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Exam Details",
		    		"status": "success"
		    	},
		    	"responseList":topicdtls}), status.HTTP_200_OK

#------------------------------------------------------#
@name_space.route("/AddSubTopic")
class AddSubTopic(Resource):
	@api.expect(addsubtopic)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		topic_id = details.get('topic_id')
		subtopic_name = details.get('subtopic_name')
		
		cursor.execute("""SELECT * FROM `subtopic` WHERE UPPER(TRIM(`subtopic_name`))=%s and topic_id=%s""",(subtopic_name.strip().upper(),topic_id))
		chksubtopic = cursor.fetchone()

		if chksubtopic == None:
			subtopic_query = ("""INSERT INTO `subtopic`(`topic_id`,
				`subtopic_name`) VALUES(%s,%s)""")
			
			subtopicdata = cursor.execute(subtopic_query,(topic_id,subtopic_name))

			if subtopicdata:
				topic_id = cursor.lastrowid
				details['subtopic_id'] = topic_id

				msg = "Added"
			else:
				msg = "Not added"

		else:
			msg = "Already exists"
			details['subtopic_id'] = chksubtopic['subtopic_id']

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Subtopic Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK
		
#--------------------------------------------------------#			
@name_space.route("/SubtopicListByTopicId/<int:topic_id>")	
class SubtopicListByTopicId(Resource):
	def get(self,topic_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `subtopic` WHERE 
			`topic_id`=%s""",(topic_id))

		subtopicdtls = cursor.fetchall()
		for i in range(len(subtopicdtls)):

			if subtopicdtls:
				subtopicdtls[i]['last_update_ts'] = subtopicdtls[i]['last_update_ts'].isoformat()
			else:
				subtopicdtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Subtopic Details",
		    		"status": "success"
		    	},
		    	"responseList":subtopicdtls}), status.HTTP_200_OK

#------------------------------------------------------#
@name_space.route("/CreateQuestionSet")
class CreateQuestionSet(Resource):
	@api.expect(questionset)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		teacher_id = details.get('teacher_id')
		set_name = details.get('set_name')
		display_name = details.get('display_name')
			
		set_query = ("""INSERT INTO `question_set`(`set_name`,`display_name`,
			`last_update_id`) VALUES(%s,%s,%s)""")
		
		setdata = cursor.execute(set_query,(set_name,display_name,teacher_id))

		if setdata:
			set_id = cursor.lastrowid
			details['set_id'] = set_id

			connection.commit()
			cursor.close()

			return ({"attributes": {
									"status_desc": "Question Set Details",
	                                "status": "success"
		                            },
		             "responseList": details}), status.HTTP_200_OK
		else:

			return ({"attributes": {"status_desc": "Question Set Details",
	                                "status": "success"
		                                },
		             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#			
@name_space.route("/QuestionSetListByTeacherId/<int:teacher_id>")	
class QuestionSetListByTeacherId(Resource):
	def get(self,teacher_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `question_set` WHERE 
			`last_update_id`=%s""",(teacher_id))

		setdtls = cursor.fetchall()
		for i in range(len(setdtls)):

			if setdtls:
				setdtls[i]['last_update_ts'] = setdtls[i]['last_update_ts'].isoformat()
			else:
				setdtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Question Set Details",
		    		"status": "success"
		    	},
		    	"responseList":setdtls}), status.HTTP_200_OK

#------------------------------------------------------#
@name_space.route("/AddInstructions")
class AddInstructions(Resource):
	@api.expect(instructiondtls)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details['exam_id']
		instruction_sequence_id = 1
		instructiondtls = details['instructions']
		for ins in range(len(instructiondtls)):
			instruction = instructiondtls[ins]['instructions']
			instruction_filepath = instructiondtls[ins]['instruction_filepath']
			instruction_filename = instructiondtls[ins]['instruction_filename']
			instruction_filetype = instructiondtls[ins]['instruction_filetype']

			instrtn_query = ("""INSERT INTO `exam_instruction`(`exam_id`,instructions,
				instruction_sequence_id,instruction_filepath,
				instruction_filename,instruction_filetype) 
				VALUES(%s,%s,%s,%s,%s,%s)""")
			
			instrtndata = cursor.execute(instrtn_query,(exam_id,instruction,instruction_sequence_id,
				instruction_filepath,instruction_filename,instruction_filetype))
			instruction_sequence_id += 1
			if instrtndata:
				msg = "Added"

			else:
				msg = "Not Added"
		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Instructions Details",
                                "status": "success",
                                "msg": msg
	                            },
	             "responseList": details}), status.HTTP_200_OK
			
#--------------------------------------------------------#			
@name_space.route("/ExamInsructionsByExamId/<int:exam_id>")	
class ExamInsructionsByExamId(Resource):
	def get(self,exam_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `exam_instruction` WHERE 
			`exam_id`=%s""",(exam_id))

		instdtls = cursor.fetchall()
		
		for i in range(len(instdtls)):
			instdtls[i]['last_update_ts'] = instdtls[i]['last_update_ts'].isoformat()
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Instructions Details",
		    		"status": "success"
		    	},
		    	"responseList":instdtls}), status.HTTP_200_OK

#------------------------------------------------------#
@name_space.route("/AddQuestions")
class AddQuestions(Resource):
	@api.expect(add_que)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		question_type = details.get('question_type')
		exam_id = details.get('exam_id')
		section_id = details.get('section_id')
		set_id = details.get('set_id')
		marks = details.get('marks')
		negative_marks = details.get('negative_marks')
		unanswered_marks = details.get('unanswered_marks')
		difficulty_level = details.get('difficulty_level')
		solution = details.get('solution')
		option_available = details.get('option_available')
		calculator_available = details.get('calculator_available')
		teacher_id = details.get('teacher_id')
		option_flag = details.get('option_flag')
		answer = details.get('answer')
		topic_id = details.get('topic_id')
		subtopic_id = details.get('subtopic_id')
		answer_text_without_option = details.get('answer_text_without_option','')
		
		if set_id != 0:
			ques_query = ("""INSERT INTO `question`(`quetion_type`,
				`exam_id`,`section_id`,`set_id`,`marks`,`negative_marks`,unanswered_marks,
				`difficulty_level`,`solution`,`option_available`,`calculator_available`,
				`topic_id`,`subtopic_id`,`answer_text_without_option`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			
			quedata = cursor.execute(ques_query,(question_type,exam_id,
				section_id,set_id,marks,negative_marks,unanswered_marks,difficulty_level,
				solution,option_available,calculator_available,topic_id,subtopic_id,answer_text_without_option))

			question_id = cursor.lastrowid
			details['question_id'] = question_id

			resourcesdtls = details['resources']
			for re in range(len(resourcesdtls)):
				resource_type = resourcesdtls[re]['resource_type']
				description = resourcesdtls[re]['description']
				sequence = resourcesdtls[re]['sequence']
						
				setres_query = ("""INSERT INTO `questionset_resource_mapping`(`question_id`,
					`set_id`,`resource_type`,`description`,`sequence`) 
					VALUES(%s,%s,%s,%s,%s)""")
				
				setresdata = cursor.execute(setres_query,(question_id,set_id,
					resource_type,description,sequence))

			optionsdtls = details['options']
			Option_Sequence_ID = 1
			for op in range(len(optionsdtls)):
				option = optionsdtls[op]['Option']
				Content_file_path = optionsdtls[op]['Content_file_path']
				Content_FileName = optionsdtls[op]['Content_FileName']
				File_Type = optionsdtls[op]['File_Type']

				opt_query = ("""INSERT INTO `options`(`Question_ID`,
					`Option`,Option_Sequence_ID,Content_file_path,
					Content_FileName,File_Type) VALUES(%s,%s,%s,%s,%s,%s)""")
			
				optdata = cursor.execute(opt_query,(question_id,option,
					Option_Sequence_ID,Content_file_path,
					Content_FileName,File_Type))
				Option_Sequence_ID += 1

			if option_flag == 'y':
				cursor.execute("""SELECT `Option_ID` FROM `options` 
					WHERE `Option`=%s""",(answer))
				ansopt_id = cursor.fetchone()

				if ansopt_id:
					ansoptid = ansopt_id['Option_ID']
					ans_query = ("""INSERT INTO `answer`(`Question_ID`,
						`Option_ID`) VALUES(%s,%s)""")
				
					ansdata = cursor.execute(ans_query,(question_id,ansoptid))

					if ansdata:
						connection.commit()
						cursor.close()
						return ({"attributes": {
											"status_desc": "Question Details",
			                                "status": "success"
				                            },
				             "responseList": "Question Added"}), status.HTTP_200_OK
			elif answer != "":
				answerpath = answer.split('Image/',1)
				
				filepath = answerpath[0]+ 'Image/'
				filename = answerpath[1]
				filetype = filename.split('.',1)
				
				if filetype[1] == 'jpg' or filetype[1] == 'jpeg' or filetype[1] == 'png':
					ftype = 'Image'
					
				elif filetype == 'txt':
					ftype = 'text'
					
				else:
					ftype = 'video'
					
				cursor.execute("""SELECT `Option_ID` FROM `options` 
					WHERE `Content_file_path`=%s and Content_FileName=%s 
					and File_Type=%s and Question_ID=%s""",(filepath,
						filename,ftype,question_id))
				ansopt_id = cursor.fetchone()

				if ansopt_id:
					ansoptid = ansopt_id['Option_ID']
					ans_query = ("""INSERT INTO `answer`(`Question_ID`,
						`Option_ID`) VALUES(%s,%s)""")
				
					ansdata = cursor.execute(ans_query,(question_id,ansoptid))

					if ansdata:
						connection.commit()
						cursor.close()
						return ({"attributes": {
											"status_desc": "Question Details",
			                                "status": "success"
				                            },
				             "responseList": "Question Added"}), status.HTTP_200_OK

		else:
			ques_query = ("""INSERT INTO `question`(`quetion_type`,
				`exam_id`,`section_id`,`set_id`,`marks`,`negative_marks`,
				`difficulty_level`,`solution`,`option_available`,`calculator_available`,
				`topic_id`,`subtopic_id`,`answer_text_without_option`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			
			quedata = cursor.execute(ques_query,(question_type,exam_id,
				section_id,set_id,marks,negative_marks,difficulty_level,
				solution,option_available,calculator_available,topic_id,subtopic_id,answer_text_without_option))

			question_id = cursor.lastrowid
			details['question_id'] = question_id

			resourcesdtls = details['resources']
			for re in range(len(resourcesdtls)):
				resource_type = resourcesdtls[re]['resource_type']
				description = resourcesdtls[re]['description']
				sequence = resourcesdtls[re]['sequence']

				setres_query = ("""INSERT INTO `question_resource_mapping`(`question_id`,
					`resource_type`,`description`,`sequence`) VALUES(%s,%s,
					%s,%s)""")
				
				setresdata = cursor.execute(setres_query,(question_id,
					resource_type,description,sequence))

			optionsdtls = details['options']
			Option_Sequence_ID = 1
			for op in range(len(optionsdtls)):
				option = optionsdtls[op]['Option']
				Content_file_path = optionsdtls[op]['Content_file_path']
				Content_FileName = optionsdtls[op]['Content_FileName']
				File_Type = optionsdtls[op]['File_Type']

				opt_query = ("""INSERT INTO `options`(`Question_ID`,
					`Option`,Option_Sequence_ID,Content_file_path,
					Content_FileName,File_Type) VALUES(%s,%s,%s,%s,%s,%s)""")
			
				optdata = cursor.execute(opt_query,(question_id,option,
					Option_Sequence_ID,Content_file_path,
					Content_FileName,File_Type))
				Option_Sequence_ID += 1


			if option_flag == 'y':
				cursor.execute("""SELECT `Option_ID` FROM `options` 
					WHERE `Option`=%s""",(answer))
				ansopt_id = cursor.fetchone()

				if ansopt_id:
					ansoptid = ansopt_id['Option_ID']
					ans_query = ("""INSERT INTO `answer`(`Question_ID`,
						`Option_ID`) VALUES(%s,%s)""")
				
					ansdata = cursor.execute(ans_query,(question_id,ansoptid))

					if ansdata:
						connection.commit()
						cursor.close()
						return ({"attributes": {
											"status_desc": "Question Details",
			                                "status": "success"
				                            },
				             "responseList": "Question Added"}), status.HTTP_200_OK
			elif answer != "":
				answerpath = answer.split('Image/',1)
				filepath = answerpath[0]+ 'Image/'
				
				filename = answerpath[1] 
				
				filetype = filename.split('.',1)
				
				if filetype[1] == 'jpg' or filetype[1] == 'jpeg' or filetype[1] == 'png':
					ftype = 'Image'
					
				elif filetype == 'txt':
					ftype = 'text'
					
				else:
					ftype = 'video'
					
				cursor.execute("""SELECT `Option_ID` FROM `options` 
					WHERE `Content_file_path`=%s and Content_FileName=%s 
					and File_Type=%s and Question_ID=%s""",(filepath,
						filename,ftype,question_id))
				ansopt_id = cursor.fetchone()

				if ansopt_id:
					ansoptid = ansopt_id['Option_ID']
					ans_query = ("""INSERT INTO `answer`(`Question_ID`,
						`Option_ID`) VALUES(%s,%s)""")
				
					ansdata = cursor.execute(ans_query,(question_id,ansoptid))

					if ansdata:
						connection.commit()
						cursor.close()
						return ({"attributes": {
											"status_desc": "Question Details",
			                                "status": "success"
				                            },
				             "responseList": "Question Added"}), status.HTTP_200_OK
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Question Details",
		    		"status": "success"
		    	},
		    	"responseList":"Question Added"}), status.HTTP_200_OK

#------------------------------------------------------#		
@name_space.route("/getAllModule")	
class getAllModule(Resource):
	def get(self):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `module_master`""")

		moduledtls = cursor.fetchall()
		
		for i in range(len(moduledtls)):
			moduledtls[i]['last_update_ts'] = moduledtls[i]['last_update_ts'].isoformat()
						
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Modules Details",
		    		"status": "success"
		    	},
		    	"responseList":moduledtls}), status.HTTP_200_OK

#--------------------------------------------------------#			  		
@name_space.route("/PreviewSectionByExamId/<int:exam_id>")	
class PreviewSectionByExamId(Resource):
	def get(self,exam_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT exam_id,type,name,module_name,
			em.`last_update_ts` FROM `exam_master` em inner join 
			`module_master` mm on em.`module_id`=mm.`module_id` WHERE 
			`exam_id`=%s""",(exam_id))

		examdtls = cursor.fetchone()
		
		if examdtls:
			examdtls['last_update_ts'] = examdtls['last_update_ts'].isoformat()
			
			cursor.execute("""SELECT section_id,name,section_type,duration 
				FROM `exam_section_master` WHERE `exam_id`=%s""",(exam_id))

			sectiondtls = cursor.fetchall()
			if sectiondtls ==():
				cursor.execute("""SELECT `question_id`,set_id FROM `question` 
					where `exam_id`=%s""",(exam_id))

				setdtls = cursor.fetchall()
				if setdtls == ():
					examdtls['question'] = []

				else:
					for chksid in range(len(setdtls)):
						
						if setdtls != () and setdtls[chksid]['set_id'] == 0:
							cursor.execute("""SELECT `question_id`,quetion_type,set_id,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								`solution` FROM `question` where `exam_id`=%s ORDER BY `question_id`""",(exam_id))

							questiondtls = cursor.fetchall()
							if questiondtls == ():
								examdtls['question'] = []
							else:
								for i in range(len(questiondtls)):
									examdtls['question'] = questiondtls

									cursor.execute("""SELECT `question_resource_id`,`resource_type`,
										`description`,sequence as 'que_sequence' FROM `question_resource_mapping` 
										WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
									questionlist = cursor.fetchall()
									if questionlist == ():
										questiondtls[i]['queresource'] = []
										
									else:
										questiondtls[i]['queresource'] = questionlist
									
									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls:
										questiondtls[i]['option'] = optdtls

									else:
										questiondtls[i]['option'] = []

									cursor.execute("""SELECT q.`question_id`,
										op.`Option_ID`,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join answer a on q.`question_id`=a.`Question_ID`
										inner join options op on a.`Option_ID`=op.`Option_ID` where
										a.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									answerdtls = cursor.fetchone()
									if answerdtls:
										questiondtls[i]['answer'] = answerdtls

									else:
										questiondtls[i]['answer'] = None

						else:
							cursor.execute("""SELECT `question_id`,quetion_type,`set_id`,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								`solution` FROM `question` where `exam_id`=%s ORDER BY `question_id`""",(exam_id))
							questiondtls = cursor.fetchall()

							if questiondtls == ():
								examdtls['question'] = []
							else:
								for i in range(len(questiondtls)):
									examdtls['question'] = questiondtls

									cursor.execute("""SELECT `set_resource_id`,`resource_type`,
										`description`,sequence as 'que_sequence' FROM `questionset_resource_mapping` 
										WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
									questionlist = cursor.fetchall()
									if questionlist == ():
										questiondtls[i]['queresource'] = []
										
									else:
										questiondtls[i]['queresource'] = questionlist

									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls:
										questiondtls[i]['option'] = optdtls

									else:
										questiondtls[i]['option'] = []

									cursor.execute("""SELECT q.`question_id`,
										op.`Option_ID`,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join answer a on q.`question_id`=a.`Question_ID`
										inner join options op on a.`Option_ID`=op.`Option_ID` where
										a.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									answerdtls = cursor.fetchone()
									if answerdtls:
										questiondtls[i]['answer'] = answerdtls

									else:
										questiondtls[i]['answer'] = None

			else:
				for secid in range(len(sectiondtls)):
					
					cursor.execute("""SELECT `question_id`,set_id FROM `question` 
						where `section_id`=%s and `exam_id`=%s""",
						(sectiondtls[secid]['section_id'],exam_id))

					setdtls = cursor.fetchall()
					
					if setdtls == ():
						sectiondtls[secid]['question'] = []
						examdtls['section'] = sectiondtls

					else:
						for chksid in range(len(setdtls)):
							
							if setdtls != () and setdtls[chksid]['set_id'] == 0:
								
								cursor.execute("""SELECT `question_id`,quetion_type,set_id,marks,negative_marks, 
									difficulty_level,option_available,calculator_available,
									`solution` FROM `question` where `section_id`=%s and `exam_id`=%s ORDER BY `question_id`""",
									(sectiondtls[secid]['section_id'],exam_id))

								questiondtls = cursor.fetchall()
								
								queList = []
								if questiondtls == ():
									sectiondtls[secid]['question'] = []
									examdtls['section'] = sectiondtls
								else:
									for i in range(len(questiondtls)):
										sectiondtls[secid]['question'] = questiondtls
										examdtls['section'] = sectiondtls

										cursor.execute("""SELECT `question_resource_id`,`resource_type`,
											`description`,sequence as 'que_sequence' FROM `question_resource_mapping` 
											WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
										questionlist = cursor.fetchall()
										
										if questionlist == ():
											questiondtls[i]['queresource'] = []
											
										else:
											questiondtls[i]['queresource'] = questionlist
										
										cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
											Content_FileName,File_Type FROM `question` q
											inner join options op on q.`question_id`=op.`Question_ID` where
											q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
										optdtls = cursor.fetchall()
										if optdtls:
											questiondtls[i]['option'] = optdtls

										else:
											questiondtls[i]['option'] = []

										cursor.execute("""SELECT q.`question_id`,
											op.`Option_ID`,`Option`,Content_file_path,
											Content_FileName,File_Type FROM `question` q
											inner join answer a on q.`question_id`=a.`Question_ID`
											inner join options op on a.`Option_ID`=op.`Option_ID` where
											a.`Question_ID`=%s""",(questiondtls[i]['question_id']))
										answerdtls = cursor.fetchone()
										if answerdtls:
											questiondtls[i]['answer'] = answerdtls

										else:
											questiondtls[i]['answer'] = None

							else:
							
								cursor.execute("""SELECT `question_id`,quetion_type,`set_id`,marks,negative_marks, 
									difficulty_level,option_available,calculator_available,
									`solution` FROM `question` where `section_id`=%s and `exam_id`=%s ORDER BY `question_id`""",
									(sectiondtls[secid]['section_id'],exam_id))

								questiondtls = cursor.fetchall()
								# print(questiondtls)
								if questiondtls == ():
									sectiondtls[secid]['question'] = []
									examdtls['section'] = sectiondtls
								else:
									for i in range(len(questiondtls)):
										sectiondtls[secid]['question'] = questiondtls
										examdtls['section'] = sectiondtls

										cursor.execute("""SELECT `set_resource_id`,`resource_type`,
											`description`,sequence as 'que_sequence' FROM `questionset_resource_mapping` 
											WHERE `question_id`=%s""",(questiondtls[i]['question_id']))
										questionlist = cursor.fetchall()
										
										if questionlist == ():
											questiondtls[i]['queresource'] = []
											
										else:
											questiondtls[i]['queresource'] = questionlist

										cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
											Content_FileName,File_Type FROM `question` q
											inner join options op on q.`question_id`=op.`Question_ID` where
											q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
										optdtls = cursor.fetchall()
										if optdtls:
											questiondtls[i]['option'] = optdtls

										else:
											questiondtls[i]['option'] = []

										cursor.execute("""SELECT q.`question_id`,
											op.`Option_ID`,`Option`,Content_file_path,
											Content_FileName,File_Type FROM `question` q
											inner join answer a on q.`question_id`=a.`Question_ID`
											inner join options op on a.`Option_ID`=op.`Option_ID` where
											a.`Question_ID`=%s""",(questiondtls[i]['question_id']))
										answerdtls = cursor.fetchone()
										if answerdtls:
											questiondtls[i]['answer'] = answerdtls

										else:
											questiondtls[i]['answer'] = None
						# f
		else:
			examdtls = []
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Preview Details",
		    		"status": "success"
		    	},
		    	"responseList":examdtls}), status.HTTP_200_OK

	
#----------------------------------------------------#
@name_space.route("/ExamSectionSettings")
class ExamSectionSettings(Resource):
	@api.expect(settingsdata)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details.get('exam_id')
		section_id = details.get('section_id')
		topicset_level = details.get('topicset_level')
		topic_id = details.get('topic_id')
		subtopicset_level = details.get('subtopicset_level')
		subtopic_id = details.get('subtopic_id')
		calculatorset_level = details.get('calculatorset_level')
		calculator_available = details.get('calculator_available')
		marksset_level = details.get('marksset_level')
		marks = details.get('marks')
		negative_marksset_level = details.get('negative_marksset_level')
		negative_marks = details.get('negative_marks')
		unanswered_marks_set_level = details.get('unanswered_marks_set_level')
		unanswered_marks = details.get('unanswered_marks')
		difficulty_set_level = details.get('difficulty_set_level')
		difficulty_level = details.get('difficulty_level')
		paper_attempts = details.get('paper_attempts')
		pause_paper = details.get('pause_paper')
		navigable_section = details.get('navigable_section')
		submit = details.get('submit')

		if section_id == 0:
			cursor.execute("""SELECT `settings_id`,`exam_id`,`section_id`,`topicset_level`,`topic_id`,
				`subtopicset_level`,`subtopic_id`,`calculatorset_level`,`calculator_available`,
				`marksset_level`,`marks`,`negative_marksset_level`,`negative_marks`,`unanswered_marks_set_level`,
				`unanswered_marks`,`difficulty_set_level`,`difficulty_level`,`paper_attempts`,`pause_paper`,
				`navigable_section`,`submit` FROM `exam_section_settings` WHERE `exam_id`=%s""",(exam_id))

			settingsdtls = cursor.fetchone()

			if settingsdtls == None:
				settings_query = ("""INSERT INTO `exam_section_settings`(`exam_id`,`section_id`,
					`topicset_level`,`topic_id`,`subtopicset_level`,`subtopic_id`,`calculatorset_level`,
					`calculator_available`,`marksset_level`,`marks`,`negative_marksset_level`,`negative_marks`,`unanswered_marks_set_level`,
					`unanswered_marks`,`difficulty_set_level`,`difficulty_level`,`paper_attempts`,`pause_paper`,`navigable_section`,`submit`)
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				settings_data = (exam_id,section_id,topicset_level,topic_id,subtopicset_level,subtopic_id,calculatorset_level,calculator_available,
					marksset_level,marks,negative_marksset_level,negative_marks,unanswered_marks_set_level,unanswered_marks,difficulty_set_level,
					difficulty_level,paper_attempts,pause_paper,navigable_section,submit)
				settingsdata = cursor.execute(settings_query,settings_data)

				if settingsdata:
					settings_id = cursor.lastrowid
					details['settings_id'] = settings_id
					msg = "Set"
				else:
					msg = "Not Set"
			else:
				details['settings_id'] = settingsdtls['settings_id']
				
				msg = "Already Set"

		else:
			cursor.execute("""SELECT `settings_id`,`exam_id`,`section_id`,`topicset_level`,`topic_id`,
				`subtopicset_level`,`subtopic_id`,`calculatorset_level`,`calculator_available`,
				`marksset_level`,`marks`,`negative_marksset_level`,`negative_marks`,`unanswered_marks_set_level`,
				`unanswered_marks`,`difficulty_set_level`,`difficulty_level`,`paper_attempts`,`pause_paper`,
				`navigable_section`,`submit` FROM `exam_section_settings` WHERE `exam_id`=%s and section_id=%s""",(exam_id,section_id))

			settingsdtls = cursor.fetchone()

			if settingsdtls == None:
				settings_query = ("""INSERT INTO `exam_section_settings`(`exam_id`,`section_id`,
					`topicset_level`,`topic_id`,`subtopicset_level`,`subtopic_id`,`calculatorset_level`,
					`calculator_available`,`marksset_level`,`marks`,`negative_marksset_level`,`negative_marks`,`unanswered_marks_set_level`,
					`unanswered_marks`,`difficulty_set_level`,`difficulty_level`,`paper_attempts`,`pause_paper`,`navigable_section`,`submit`)
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
				settings_data = (exam_id,section_id,topicset_level,topic_id,subtopicset_level,subtopic_id,calculatorset_level,calculator_available,
					marksset_level,marks,negative_marksset_level,negative_marks,unanswered_marks_set_level,unanswered_marks,difficulty_set_level,
					difficulty_level,paper_attempts,pause_paper,navigable_section,submit)
				settingsdata = cursor.execute(settings_query,settings_data)

				if settingsdata:
					settings_id = cursor.lastrowid
					details['settings_id'] = settings_id
					msg = "Set"
				else:
					msg = "Not Set"

			else:
				details['settings_id'] = settingsdtls['settings_id']
				
				msg = "Already Set"


		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Exam Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

#--------------------------------------------------------#			
@name_space.route("/ExamSettingsDtlsByExamId/<int:exam_id>")	
class ExamSettingsDtlsByExamId(Resource):
	def get(self,exam_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `exam_section_settings` WHERE `exam_id`=%s""",(exam_id))

		settingsdtls = cursor.fetchone()
		if settingsdtls:
			settingsdtls['addition_last_update_ts'] = settingsdtls['addition_last_update_ts'].isoformat()
			settingsdtls['last_update_ts'] = settingsdtls['last_update_ts'].isoformat()
		else:
			settingsdtls = {}
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Settings Details",
		    		"status": "success"
		    	},
		    	"responseList":settingsdtls}), status.HTTP_200_OK

#----------------------------------------------------#
@name_space.route("/ExamSettingsDtlsByExamIdSectionId/<int:exam_id>/<int:section_id>")	
class ExamSettingsDtlsByExamIdSectionId(Resource):
	def get(self,exam_id,section_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `exam_section_settings` WHERE `exam_id`=%s and section_id=%s""",(exam_id,section_id))

		settingsdtls = cursor.fetchone()
		if settingsdtls:
			settingsdtls['addition_last_update_ts'] = settingsdtls['addition_last_update_ts'].isoformat()
			settingsdtls['last_update_ts'] = settingsdtls['last_update_ts'].isoformat()
		else:
			settingsdtls = {}
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Settings Details",
		    		"status": "success"
		    	},
		    	"responseList":settingsdtls}), status.HTTP_200_OK

#----------------------------------------------------#
@name_space.route("/TopicNameByTopicId/<int:topic_id>")	
class TopicNameByTopicId(Resource):
	def get(self,topic_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT topic_name FROM `topic` WHERE `topic_id`=%s""",(topic_id))

		topicdtls = cursor.fetchone()
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Topic Details",
		    		"status": "success"
		    	},
		    	"responseList":topicdtls}), status.HTTP_200_OK

#----------------------------------------------------#
@name_space.route("/SubTopicNameBySubTopicId/<int:subtopic_id>")	
class SubTopicNameBySubTopicId(Resource):
	def get(self,subtopic_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT subtopic_name FROM `subtopic` WHERE `subtopic_id`=%s""",(subtopic_id))

		subtopicdtls = cursor.fetchone()
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Subtopic Details",
		    		"status": "success"
		    	},
		    	"responseList":subtopicdtls}), status.HTTP_200_OK

#----------------------------------------------------#
#----------------------------------------------------#
@name_space.route("/AddDifficultyLevel")
class AddDifficultyLevel(Resource):
	@api.expect(difflevel)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		difficulty_level = details.get('difficulty_level')

		cursor.execute("""SELECT * FROM `difficulty_level` WHERE UPPER(TRIM(`difficulty_level`))=%s""",(difficulty_level.strip().upper()))
		chklvl = cursor.fetchone()

		if chklvl != None:
			msg = "Already exists"
			details['difficulty_level_id'] = chklvl['difficulty_level_id']
			
			return ({"attributes": {"status_desc": "Exam Difficulty Level Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK

		diff_query = ("""INSERT INTO `difficulty_level`(`difficulty_level`) 
			VALUES(%s)""")
		diff_data = (difficulty_level)
		diffdata = cursor.execute(diff_query,diff_data)

		if diffdata:
			difficulty_level_id = cursor.lastrowid
			details['difficulty_level_id'] = difficulty_level_id

			msg = "Added"
		else:
			msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Exam Difficulty Level Details",
                                "status": "success",
                                "msg": msg
	                                },
	             "responseList": details}), status.HTTP_200_OK
			
#-----------------------------------------------------------------------------#
@name_space.route("/ExamDifficultyLevel")	
class ExamDifficultyLevel(Resource):
	def get(self):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT * FROM `difficulty_level`""")

		diffdtls = cursor.fetchall()
		for i in range(len(diffdtls)):

			if diffdtls:
				diffdtls[i]['last_update_ts'] = diffdtls[i]['last_update_ts'].isoformat()
			else:
				diffdtls = []
				
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    		"status_desc": "Exam Difficulty Level Details",
		    		"status": "success"
		    	},
		    	"responseList":diffdtls}), status.HTTP_200_OK
		
#------------------------------------------------------------------------#
update_exam_model = api.model('update_exam_model', {
	"exam_id":fields.Integer(),
	"module_id":fields.Integer(),
	"name":fields.String(),
	"fullmarks":fields.Integer(),
	"duration":fields.Integer(),
	"type":fields.String()
	})

update_exam_section_model = api.model('update_exam_section_model',{
	"section_id":fields.Integer(),
	"name":fields.String(),
	"section_type":fields.String(),
	"duration":fields.Integer(),
	"marks":fields.Integer(),
	"sequence":fields.Integer(),
	"warning_time":fields.Float()
	})

@name_space.route("/UpdateExam")
class UpdateExam(Resource):
	@api.expect(update_exam_model)
	def put(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		name=details.get('name');
		fullmarks=details.get("fullmarks")
		duration=details.get("duration")
		exam_id=details.get("exam_id")
		exam_type=details.get("type")
		module_id=details.get("module_id")

		if name:
			update_name_query=("""UPDATE `exam_master` SET `name`=%s WHERE `exam_id`=%s""")
			update_name_data=(name,exam_id)
			cursor.execute(update_name_query,update_name_data)

		if fullmarks:
			update_marks_query=("""UPDATE `exam_master` SET `fullmarks`=%s WHERE `exam_id`=%s""")
			update_marks_data=(fullmarks,exam_id)
			cursor.execute(update_marks_query,update_marks_data)
		if duration:
			update_duration_query=("""UPDATE `exam_master` SET `duration`=%s WHERE `exam_id`=%s""")
			update_duration_data=(duration,exam_id)
			cursor.execute(update_duration_query,update_duration_data)

		if exam_type:
			update_type_query=("""UPDATE `exam_master` SET `type`=%s WHERE `exam_id`=%s""")
			update_type_data=(exam_type,exam_id)
			cursor.execute(update_type_query,update_type_data)

		if module_id:
			update_type_query=("""UPDATE `exam_master` SET `module_id`=%s WHERE `exam_id`=%s""")
			update_type_data=(module_id,exam_id)
			cursor.execute(update_type_query,update_type_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Update Exam Details",
	    				"status": "success"
	    				},
	    				"responseList":"Updated successfully"}), status.HTTP_200_OK

#----------------------------------------------------------------------------------------------#

@name_space.route("/UpdateExamSection")
class UpdateExamSection(Resource):
	@api.expect(update_exam_section_model)
	def put(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		section_id=details.get("section_id")
		name=details.get("name")
		section_type=details.get("section_type")
		duration=details.get("duration")
		marks=details.get("marks")
		sequence=details.get("sequence")
		warning_time=details.get("warning_time")

		if name:
			update_name_query=("""UPDATE `exam_section_master` SET `name`=%s WHERE `section_id`=%s""")
			update_name_data=(name,section_id)
			cursor.execute(update_name_query,update_name_data)

		if section_type:
			update_section_query=("""UPDATE `exam_section_master` SET `section_type`=%s WHERE `section_id`=%s""")
			update_section_data=(section_type,section_id)
			cursor.execute(update_section_query,update_section_data)

		if duration:
			update_duration_query=("""UPDATE `exam_section_master` SET `duration`=%s WHERE `section_id`=%s""")
			update_duration_data=(duration,section_id)
			cursor.execute(update_duration_query,update_duration_data)

		if marks:
			update_marks_query=("""UPDATE `exam_section_master` SET `marks`=%s WHERE `section_id`=%s""")
			update_marks_data=(marks,section_id)
			cursor.execute(update_marks_query,update_marks_data)

		if sequence:
			update_sequence_query=("""UPDATE `exam_section_master` SET `sequence`=%s WHERE `section_id`=%s""")
			update_sequence_data=(sequence,section_id)
			cursor.execute(update_sequence_query,update_sequence_data)

		if warning_time:
			update_warning_time_query=("""UPDATE `exam_section_master` SET `warning_time`=%s WHERE `section_id`=%s""")
			update_warning_time_data=(warning_time,section_id)
			cursor.execute(update_warning_time_query,update_warning_time_data)

		connection.commit()
		cursor.close()
		
		return ({"attributes": {
	    				"status_desc": "Update Exam Section Details",
	    				"status": "success"
	    				},
	    				"responseList":"Updated successfully"}), status.HTTP_200_OK

#----------------------------------------------------------------------------------------------#


@name_space.route("/UpdateQuestionResourceSection")
class UpdateQuestionResourceSection(Resource):
	@api.expect(update_que)
	def put(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		resourcesdtls = details['resources']
		for re in range(len(resourcesdtls)):
			resource_id=resourcesdtls[re]['resource_id']
			question_id=resourcesdtls[re]['question_id']
			set_id=resourcesdtls[re]['set_id']
			resource_type = resourcesdtls[re]['resource_type']
			description = resourcesdtls[re]['description']
			sequence = resourcesdtls[re]['sequence']
			if resource_id==0:
				if set_id!=0:
					insert_set_query = ("""INSERT INTO `questionset_resource_mapping`(`question_id`,
					`set_id`,`resource_type`,`description`,`sequence`) 
					VALUES(%s,%s,%s,%s,%s)""")
					insertsetdata = cursor.execute(insert_set_query,(question_id,set_id,resource_type,description,sequence))
				else:
					insert_question_query = ("""INSERT INTO `question_resource_mapping`(`question_id`,`resource_type`,`description`,`sequence`) VALUES(%s,%s,%s,%s)""")
					insertquestiondata = cursor.execute(insert_question_query,(question_id,resource_type,description,sequence))
			else:
				if set_id!=0:
					update_set_query=("""UPDATE `questionset_resource_mapping` SET `resource_type` =%s,`description`=%s,`sequence`=%s WHERE `set_resource_id`=%s""")
					update_set_data=(resource_type,description,sequence,resource_id)
					cursor.execute(update_set_query,update_set_data)
				else:
					update_question_query=("""UPDATE `question_resource_mapping` SET `resource_type` =%s,`description`=%s,`sequence`=%s WHERE `question_resource_id`=%s""")
					update_question_data=(resource_type,description,sequence,resource_id)
					cursor.execute(update_question_query,update_question_data)

		connection.commit()
		cursor.close()
		return ({"attributes": {
	    			"status_desc": "Update Question Resource Details",
	    			"status": "success"
	    			},
	    			"responseList":details}), status.HTTP_200_OK

#----------------------------------------------------------------------------------------------#


@name_space.route("/update_option")
class update_option(Resource):
	@api.expect(update_option_model)
	def put(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		Option_ID=details["Option_ID"]
		Option=details["Option"]
		Option_Sequence_ID=details["Option_Sequence_ID"]
		Content_file_path=details["Content_file_path"]
		Content_FileName=details["Content_FileName"]
		File_Type=details["File_Type"]

		update_set_query=("""UPDATE `options` SET `Option` =%s,`Option_Sequence_ID`=%s,`Content_file_path`=%s, `Content_FileName`=%s, `File_Type`=%s WHERE `Option_ID`=%s""")
		update_set_data=(Option,Option_Sequence_ID,Content_file_path,Content_FileName,File_Type,Option_ID)
		cursor.execute(update_set_query,update_set_data)


		connection.commit()
		cursor.close()
		return ({"attributes": {
	    			"status_desc": "Update Option Details",
	    			"status": "success"
	    			},
	    			"responseList":details}), status.HTTP_200_OK

#----------------------------------------------------------------------------------------------#


@name_space.route("/UpdateinstructionSection")
class UpdateinstructionSection(Resource):
	@api.expect(update_instruction_model)
	def put(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		instruction_id=details.get("instruction_id")
		instructions = details.get("instructions")
		instruction_sequence_id=details.get("instruction_sequence_id")
		instruction_filepath=details.get("instruction_filepath")
		instruction_filename=details.get("instruction_filename")
		instruction_filetype=details.get("instruction_filetype")

		if instructions:
			update_instruction_query=("""UPDATE `exam_instruction` SET `instructions`=%s WHERE `instruction_id`=%s""")
			update_instruction_data=(instructions,instruction_id)
			cursor.execute(update_instruction_query,update_instruction_data)

		if instruction_sequence_id:
			update_sequence_query=("""UPDATE `exam_instruction` SET `instruction_sequence_id`=%s WHERE `instruction_id`=%s""")
			update_sequence_data=(instruction_sequence_id,instruction_id)
			cursor.execute(update_sequence_query,update_sequence_data)

		if instruction_filepath:
			update_filepath_query=("""UPDATE `exam_instruction` SET `instruction_filepath`=%s WHERE `instruction_id`=%s""")
			update_filepath_data=(instruction_filepath,instruction_id)
			cursor.execute(update_filepath_query,update_filepath_data)

		if instruction_filename:
			update_filename_query=("""UPDATE `exam_instruction` SET `instruction_filename`=%s WHERE `instruction_id`=%s""")
			update_filename_data=(instruction_filename,instruction_id)
			cursor.execute(update_filename_query,update_filename_data)

		if instruction_filetype:
			update_filetype_query=("""UPDATE `exam_instruction` SET `instruction_filetype`=%s WHERE `instruction_id`=%s""")
			update_filetype_data=(instruction_filetype,instruction_id)
			cursor.execute(update_filetype_query,update_filetype_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Update Instruction Details",
	    				"status": "success"
	    				},
	    				"responseList":"Updated successfully"}), status.HTTP_200_OK
#----------------------------------------------------------------------------------------------#

update_instructions = api.model('instructions', {
	"instruction_id":fields.Integer(),
	"exam_id":fields.Integer(),
	"instruction_sequence_id":fields.Integer(),
	"instructions":fields.String(),
	"instruction_filepath":fields.String(),
	"instruction_filename":fields.String(),
	"instruction_filetype":fields.String()
	})

update_instructiondtls = api.model('update_instructions', {
	"instructions": fields.List(fields.Nested(instructions))
	})

@name_space.route("/UpdateinstructionSectionV2")
class UpdateinstructionSectionV2(Resource):
	@api.expect(update_instructiondtls)
	def put(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		instructiondtls = details['instructions']

		for ins in instructiondtls:
			instruction_id = ins['instruction_id']
			exam_id= ins['exam_id']
			instruction_sequence_id = ins['instruction_sequence_id']
			instruction = ins['instructions']
			instruction_filepath = ins['instruction_filepath']
			instruction_filename = ins['instruction_filename']
			instruction_filetype = ins['instruction_filetype']

			if instruction_id == 0:
				instrtn_query = ("""INSERT INTO `exam_instruction`(`exam_id`,instructions,
					instruction_sequence_id,instruction_filepath,
					instruction_filename,instruction_filetype) 
					VALUES(%s,%s,%s,%s,%s,%s)""")

				instrtndata = cursor.execute(instrtn_query,(exam_id,instruction,instruction_sequence_id,
					instruction_filepath,instruction_filename,instruction_filetype))
			else:
				updateqry = ("""UPDATE `exam_instruction` SET `instructions` = %s,`instruction_sequence_id`= %s,`instruction_filepath`= %s,
					`instruction_filename`= %s,`instruction_filetype`= %s WHERE `instruction_id` =%s""")
				updatedata = (instruction,instruction_sequence_id,instruction_filepath,instruction_filename,instruction_filetype,instruction_id)
				cursor.execute(updateqry,updatedata)
			
		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Instructions Details",
                                "status": "success",
	                            },
	             "responseList": details}), status.HTTP_200_OK

@name_space.route("/removeExamInstruction/<int:instruction_id>")
class removeExamInstruction(Resource):
	def delete(self, instruction_id):
		connection = study_break()
		cursor = connection.cursor()
		
		delqry = ("""DELETE FROM `exam_instruction` WHERE `instruction_id` = %s """)
		delData = (instruction_id)
		
		cursor.execute(delqry,delData)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Exam Instructions",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK


@name_space.route("/PreviewSectionByExamIdV2/<int:exam_id>")	
class PreviewSectionByExamIdV2(Resource):
	def get(self,exam_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT exam_id,type,name,module_name,
			em.`last_update_ts` FROM `exam_master` em inner join 
			`module_master` mm on em.`module_id`=mm.`module_id` WHERE 
			`exam_id`=%s""",(exam_id))

		examdtls = cursor.fetchone()

		if examdtls:
			examdtls['last_update_ts'] = examdtls['last_update_ts'].isoformat()
			
			cursor.execute("""SELECT section_id,name,section_type,duration,sequence 
				FROM `exam_section_master` WHERE `exam_id`=%s ORDER BY sequence""",(exam_id))

			sectiondtls = cursor.fetchall()

			if sectiondtls:
				for sec in sectiondtls:
					cursor.execute("""SELECT `question_id`,quetion_type,`question`.`set_id`,qs.`set_name`,qs.`display_name`,marks,negative_marks, 
						difficulty_level,option_available,calculator_available,`unanswered_marks`,
						`solution`,t.`topic_name`,st.`subtopic_name`,`answer_text_without_option` FROM `question` inner join `question_set` qs on `question`.`set_id` = qs.`set_id` inner join `topic` t on `question`.`topic_id`=t.`topic_id`
						inner join `subtopic` st on `question`.`subtopic_id`=st.`subtopic_id` where `section_id`=%s and `exam_id`=%s""",
						(sec['section_id'],exam_id))
					questions = cursor.fetchall()
					if questions:
						questionsDict = dict()
						for que in questions:
							if que['set_id'] == 0:
								resourseqry = ("""SELECT `question_resource_id` as 'resource_id',`resource_type`,
									`description`,sequence as 'que_sequence' FROM `question_resource_mapping` 
									WHERE `question_id`=%s""")
							else:
								resourseqry = ("""SELECT `set_resource_id` as 'resource_id',`resource_type`,
									`description`,sequence as 'que_sequence' FROM `questionset_resource_mapping` 
									WHERE `question_id`=%s""")
							cursor.execute(resourseqry,(que['question_id']))
							queresource = cursor.fetchall()
							if queresource:
								que['queresource'] = queresource
							else:
								que['queresource'] = []

							cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
								Content_FileName,File_Type FROM `question` q inner join 
								options op on q.`question_id`=op.`Question_ID` where 
								q.`Question_ID`=%s""",(que['question_id']))
							optdtls = cursor.fetchall()
							if optdtls:
								que['option'] = optdtls
							else:
								que['option'] = []

							cursor.execute("""SELECT q.`question_id`, op.`Option_ID`,
								`Option`,Content_file_path, Content_FileName,File_Type 
								FROM `question` q inner join answer a on q.`question_id`= 
								a.`Question_ID` inner join options op on a.`Option_ID`=op.`Option_ID` 
								where a.`Question_ID`=%s""",(que['question_id']))
							answerdtls = cursor.fetchone()
							if answerdtls:
								que['answer'] = answerdtls
							else:
								que['answer'] = {}
							key = que['set_id']
							if key == 0:
								key = key - que['question_id']
							temp = questionsDict.get(key,list())
							temp.append(que)
							questionsDict[key] = temp

						sec['question'] = list(questionsDict.values())
					else:
						sec['question'] = []

				examdtls['section'] = sectiondtls


			else:
				examdtls['section'] = []
		else:
			pass

		connection.commit()
		cursor.close()
		return ({"attributes": {
			"status_desc": "Preview Details",
			"status": "success"},
			"responseList":examdtls}), status.HTTP_200_OK

@name_space.route("/finalSubmit")
class finalSubmit(Resource):
	@api.expect(final_submit_model)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		exam_id = details.get('exam_id')
		start_date = details.get('start_date')
		end_date = details.get('end_date')
		start_time = details.get('start_time')
		end_time = details.get('end_time')
		submit = details.get('submit')
		paper_pause = details.get('paper_pause')
		exam_link = details.get('exam_link')
		student_ids = details.get('student_ids')
		group_ids = details.get('group_ids')
		exam_status = "assigned"
		last_update_id = details.get('last_update_id')
		unattemped_theshold = details.get('unattemped_theshold',0)

		if exam_link:
			cursor.execute("""UPDATE `exam_master` SET `exam_link`=%s WHERE `exam_id` = %s""",(exam_link,exam_id))

		cursor.execute("""SELECT `settings_id` FROM `exam_section_settings` WHERE `exam_id`=%s AND `section_id`=0""",(exam_id))
		settingDtls = cursor.fetchone()
		if settingDtls:
			cursor.execute("""UPDATE `exam_section_settings` SET `pause_paper`=%s,`submit`=%s,`threshold_unattempted`=%s WHERE `settings_id` = %s""",(paper_pause,submit,unattemped_theshold,settingDtls['settings_id']))

		student_qry = ("""INSERT INTO `student_exam_mapping`(`exam_id`,`student_id`,`exam_status`,`start_date`,`end_date`,`start_time`,`end_time`,
			`last_update_id`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")

		for student_id in student_ids:
			cursor.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `exam_id`=%s AND `student_id`=%s""",(exam_id,student_id))
			already_exist = cursor.fetchone()
			if not already_exist:
				cursor.execute(student_qry,(exam_id,student_id,exam_status,start_date,end_date,start_time,end_time,last_update_id))

		for group_id in group_ids:
			cursor.execute("""SELECT `student_id` FROM `group_student_mapping` WHERE `group_id`=%s""",(group_id))
			group_students = cursor.fetchall()
			for student_id in group_students:
				cursor.execute("""SELECT `mapping_id` FROM `student_exam_mapping` WHERE `exam_id`=%s AND `student_id`=%s""",(exam_id,student_id['student_id']))
				already_exist = cursor.fetchone()
				if not already_exist:
					cursor.execute(student_qry,(exam_id,student_id['student_id'],exam_status,start_date,end_date,start_time,end_time,last_update_id))

		connection.commit()
		cursor.close()

		return ({"attributes": {
			"status_desc": "Final Submit",
			"status": "success"},
			"responseList":""}), status.HTTP_200_OK

@name_space.route("/deleteQuestion/<int:question_id>")
class deleteQuestion(Resource):
	def delete(self, question_id):
		connection = study_break()
		cursor = connection.cursor()
		
		# delete question from question table
		cursor.execute("""DELETE FROM `question` WHERE `question_id` = %s""",(question_id))

		# delete question resourse from question_resource_mapping
		cursor.execute("""DELETE FROM `question_resource_mapping` WHERE `question_id` = %s""",(question_id))

		# delete question resourse from questionset_resource_mapping
		cursor.execute("""DELETE FROM `questionset_resource_mapping` WHERE `question_id` = %s""",(question_id))

		# delete all options associated with this question.
		cursor.execute("""DELETE FROM `options` WHERE `Question_ID` = %s""",(question_id))

		# delete answer of this question
		cursor.execute("""DELETE FROM `answer` WHERE `Question_ID` = %s""",(question_id))

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Exam Question",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

@name_space.route("/deleteSection/<int:section_id>/<int:exam_id>")
class deleteSection(Resource):
	def delete(self,section_id,exam_id):

		connection = study_break()
		cursor = connection.cursor()

		cursor.execute("""SELECT `question_id` FROM `question` WHERE `section_id` = %s""",(section_id))
		questions = cursor.fetchall()

		for x in questions:
			delete_que_url = BASE_URL + "exam_section/StudyBreak/deleteQuestion/"+str(x['question_id'])
			delRes = requests.delete(delete_que_url).json()
		
		cursor.execute("""DELETE FROM `exam_section_master` WHERE `section_id` = %s""",(section_id))

		cursor.execute("""SELECT * FROM `exam_section_master` WHERE `exam_id`=%s order by sequence asc""",(exam_id))
		exam_sections = cursor.fetchall()

		i = 1
		for key,data in enumerate(exam_sections):
			print(i)
			update_query = ("""UPDATE `exam_section_master` SET `sequence` = %s
					WHERE `section_id` = %s""")
			update_data = (i,data['section_id'])
			cursor.execute(update_query,update_data)
			i +=1
		
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Remove Exam Section",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
		

@name_space.route("/deleteSet/<int:set_id>")
class deleteSet(Resource):
	def delete(self, set_id):

		if set_id == 0:
			return ({"attributes": {"status_desc": "Remove Exam Set",
								"status": "success"},
				"responseList": 'Set id should be non-zero'}), status.HTTP_200_OK

		connection = study_break()
		cursor = connection.cursor()
		
		# fetch all questions of this set
		cursor.execute("""SELECT `question_id` FROM `question` WHERE `set_id`=%s""",(set_id))
		questions = cursor.fetchall()

		# delete set from set table
		cursor.execute("""DELETE FROM `question_set` WHERE `set_id` = %s""",(set_id))

		# delete question from question table
		cursor.execute("""DELETE FROM `question` WHERE `set_id` = %s""",(set_id))

		# delete question resourse from questionset_resource_mapping
		cursor.execute("""DELETE FROM `questionset_resource_mapping` WHERE `set_id` = %s""",(set_id))

		for x in questions:
			question_id = x['question_id']
			# delete all options associated with this question.
			cursor.execute("""DELETE FROM `options` WHERE `Question_ID` = %s""",(question_id))

			# delete answer of this question
			cursor.execute("""DELETE FROM `answer` WHERE `Question_ID` = %s""",(question_id))

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Exam Set",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK


#----------------------Delete-Exam---------------------#
@name_space.route("/deleteExam/<int:exam_id>")
class deleteExam(Resource):
	def delete(self,exam_id):

		connection = study_break()
		cursor = connection.cursor()

		cursor.execute("""SELECT `section_id` FROM `exam_section_master` WHERE `exam_id` = %s""",(exam_id))
		sections = cursor.fetchall()

		for x in sections:
			delete_que_url = BASE_URL + "exam_section/StudyBreak/deleteSection/"+str(x['section_id'])+"/"+str(exam_id)
			delRes = requests.delete(delete_que_url).json()

		cursor.execute("""DELETE FROM `exam_master` WHERE `exam_id` = %s""",(exam_id))

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Remove Exam",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK
#----------------------Delete-Exam---------------------#

#----------------------Update-Question--------------------------------#

@name_space.route("/UpdateQuestion/<int:question_id>")
class UpdateQuestion(Resource):
	@api.expect(update_question_model)
	def put(self,question_id):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()

		if details and "quetion_type" in details:
			quetion_type = details['quetion_type']
			update_query = ("""UPDATE `question` SET `quetion_type` = %s
						WHERE `question_id` = %s """)
			update_data = (quetion_type,question_id)
			cursor.execute(update_query,update_data)

		if details and "marks" in details:
			marks = details['marks']
			update_query = ("""UPDATE `question` SET `marks` = %s
						WHERE `question_id` = %s """)
			update_data = (marks,question_id)
			cursor.execute(update_query,update_data)

		if details and "negative_marks" in details:
			negative_marks = details['negative_marks']
			update_query = ("""UPDATE `question` SET `negative_marks` = %s
						WHERE `question_id` = %s """)
			update_data = (negative_marks,question_id)
			cursor.execute(update_query,update_data)

		if details and "unanswered_marks" in details:
			unanswered_marks = details['unanswered_marks']
			update_query = ("""UPDATE `question` SET `unanswered_marks` = %s
						WHERE `question_id` = %s """)
			update_data = (unanswered_marks,question_id)
			cursor.execute(update_query,update_data)

		if details and "difficulty_level" in details:
			difficulty_level = details['difficulty_level']
			update_query = ("""UPDATE `question` SET `difficulty_level` = %s
						WHERE `question_id` = %s """)
			update_data = (difficulty_level,question_id)
			cursor.execute(update_query,update_data)

		if details and "solution" in details:
			solution = details['solution']
			update_query = ("""UPDATE `question` SET `solution` = %s
						WHERE `question_id` = %s """)
			update_data = (solution,question_id)
			cursor.execute(update_query,update_data)

		if details and "answer_text_without_option" in details:
			answer_text_without_option = details['answer_text_without_option']
			update_query = ("""UPDATE `question` SET `answer_text_without_option` = %s
						WHERE `question_id` = %s """)
			update_data = (answer_text_without_option,question_id)
			cursor.execute(update_query,update_data)

		if details and "option_available" in details:
			option_available = details['option_available']
			update_query = ("""UPDATE `question` SET `option_available` = %s
						WHERE `question_id` = %s """)
			update_data = (option_available,question_id)
			cursor.execute(update_query,update_data)

		if details and "calculator_available" in details:
			calculator_available = details['calculator_available']
			update_query = ("""UPDATE `question` SET `calculator_available` = %s
						WHERE `question_id` = %s """)
			update_data = (calculator_available,question_id)
			cursor.execute(update_query,update_data)

		

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Update Question Details",
	    				"status": "success"
	    		},
	    		"responseList":"Updated successfully"}), status.HTTP_200_OK

#----------------------Update-Question--------------------------------#

