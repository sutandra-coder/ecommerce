from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from database_connections import study_break
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import requests
import calendar
import json
from threading import Thread
import time
import os   

app = Flask(__name__)
cors = CORS(app)

student_exam_section = Blueprint('student_exam_section_api', __name__)
api = Api(student_exam_section,  title='StudyBreak API',description='StudyBreak API')
name_space = api.namespace('StudyBreak',description='StudyBreak')

student_exam_mapping =  api.model('student_exam_mapping', {
	"exam_id":fields.Integer(),
	"student_id":fields.Integer(),
	"exam_status":fields.String()
	})

stu_exam_section = api.model('stu_exam_section', {
	"exam_id":fields.Integer(),
	"section_id":fields.Integer(),
	"student_id":fields.Integer(),
	"section_status":fields.String(),
	"section_duration":fields.Float()
	})

stu_que_section = api.model('stu_que_section', {
	"exam_id":fields.Integer(),
	"section_id":fields.Integer(),
	"student_id":fields.Integer(),
	"question_id":fields.Integer(),
	"option_id":fields.Integer(),
	"answer":fields.String(),
	"question_status":fields.String(),
	"question_duration":fields.Float(),
	"mark_status":fields.Integer()
	})

exam_status_model = api.model('exam_status_model', {
	"exam_id":fields.Integer(),
	"student_id":fields.Integer()
})

#------------------------------------------------------#			
@name_space.route("/SectionWiseQuestionsBySectionIdExamId/<int:exam_id>/<int:section_id>",
	doc={'params':{'start':'questionId','limit':'limit','page':'pageno'}})	
class SectionWiseQuestionsBySectionId(Resource):
	def get(self,exam_id,section_id):
		connection = study_break()
		cursor = connection.cursor()
		
		start=int(request.args.get('start', 0))
		limit=int(request.args.get('limit', 1))
		page=int(request.args.get('page', 1))

		previous_url = ''
		next_url = ''

		cursor.execute("""SELECT count(`question_id`)as count FROM 
			`question` WHERE `section_id`=%s""",(section_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		
		cur_count = int(page) * int(limit)
		
		
		if start == 0:
			previous_url = ''

			cursor.execute("""SELECT section_id,name,section_type,duration 
				FROM `exam_section_master` WHERE `section_id`=%s""",(section_id))

			sectiondtls = cursor.fetchone()
			if sectiondtls == None:
				sectiondtls = []
				
			else:
				cursor.execute("""SELECT `question_id`,set_id FROM `question` 
					where `section_id`=%s and `exam_id`=%s""",
					(section_id,exam_id))

				setdtls = cursor.fetchall()
				
				if setdtls == ():
					sectiondtls['question'] = []

				else:
					for chksid in range(len(setdtls)):
						
						if setdtls != () and setdtls[chksid]['set_id'] == 0:
							
							cursor.execute("""SELECT q.`question_id`,quetion_type,set_id,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								question_resource_id,resource_type,description,q.`solution`,
								sequence as 'que_sequence' FROM `question` q
								inner join question_resource_mapping qrm on q.`question_id`=qrm.`question_id`
								where q.`section_id`=%s and q.`exam_id`=%s order by q.`question_id` ASC limit %s""",
								(section_id,exam_id,limit))

							questiondtls = cursor.fetchall()
							
							if questiondtls == ():
								sectiondtls['question'] = []
								
							else:
								for i in range(len(questiondtls)):
									sectiondtls['question'] = questiondtls
									
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
										questiondtls[i]['answer'] = {}

						else:
							cursor.execute("""SELECT q.`question_id`,quetion_type,q.`set_id`,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								set_resource_id,resource_type,description,q.`solution`,
								sequence as 'que_sequence' FROM `question` q
								inner join questionset_resource_mapping qrm on q.`set_id`=qrm.`set_id`
								where q.`section_id`=%s and q.`exam_id`=%s order by q.`question_id` ASC limit %s""",
								(section_id,exam_id,limit))

							questiondtls = cursor.fetchall()

							if questiondtls == ():
								sectiondtls['question'] = []
								
							else:
								for i in range(len(questiondtls)):
									sectiondtls['question'] = questiondtls

									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls != ():
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
										questiondtls[i]['answer'] = {}

		else:
			cursor.execute("""SELECT section_id,name,section_type,duration 
				FROM `exam_section_master` WHERE `section_id`=%s""",(section_id))

			sectiondtls = cursor.fetchone()
			if sectiondtls == None:
				sectiondtls = []
				
			else:
				cursor.execute("""SELECT `question_id`,set_id FROM `question` 
					where `section_id`=%s and `exam_id`=%s""",
					(section_id,exam_id))

				setdtls = cursor.fetchall()
				
				if setdtls == ():
					sectiondtls['question'] = []

				else:
					for chksid in range(len(setdtls)):
						
						if setdtls != () and setdtls[chksid]['set_id'] == 0:
							
							cursor.execute("""SELECT q.`question_id`,quetion_type,set_id,marks,negative_marks, 
								difficulty_level,option_available,calculator_available,
								question_resource_id,resource_type,description,q.`solution`,
								sequence as 'que_sequence' FROM `question` q
								inner join question_resource_mapping qrm on q.`question_id`=qrm.`question_id`
								where q.`question_id`>%s and q.`section_id`=%s and q.`exam_id`=%s order by q.`question_id` ASC limit %s""",
								(start,section_id,exam_id,limit))

							questiondtls = cursor.fetchall()
							
							if questiondtls == ():
								sectiondtls['question'] = []
								
							else:
								for i in range(len(questiondtls)):
									sectiondtls['question'] = questiondtls
									
									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls != ():
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
										questiondtls[i]['answer'] = {}

						else:
							cursor.execute("""SELECT q.`question_id`,quetion_type,q.`set_id`,marks,negative_marks,
								difficulty_level,option_available,calculator_available,
								set_resource_id,resource_type,description,q.`solution`,
								sequence as 'que_sequence' FROM `question` q
								inner join questionset_resource_mapping qrm on q.`set_id`=qrm.`set_id`
								where q.`question_id`>%s and q.`section_id`=%s and q.`exam_id`=%s order by q.`question_id` ASC limit %s""",
								(start,section_id,exam_id,limit))

							questiondtls = cursor.fetchall()

							if questiondtls == ():
								sectiondtls['question'] = []
								
							else:
								for i in range(len(questiondtls)):
									sectiondtls['question'] = questiondtls

									cursor.execute("""SELECT q.`question_id`,Option_ID,`Option`,Content_file_path,
										Content_FileName,File_Type FROM `question` q
										inner join options op on q.`question_id`=op.`Question_ID` where
										q.`Question_ID`=%s""",(questiondtls[i]['question_id']))
									optdtls = cursor.fetchall()
									if optdtls != ():
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
										questiondtls[i]['answer'] = {}

		page_next = page + 1
		if cur_count < total_count:
			next_url = '?start={}&limit={}&page={}'.format(questiondtls[-1].get('question_id'),limit,page_next)
		else:
			next_url = ''
				
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Wise Questions Details",
	                            "status": "success",
	                            "total":total_count,
								'previous':previous_url,
								'next':next_url
								},
	             "responseList": sectiondtls}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/StudentExamMapping")
class StudentExamMapping(Resource):
	@api.expect(student_exam_mapping)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details['exam_id']
		student_id = details['student_id']
		exam_status = details['exam_status']

		cursor.execute("""SELECT `mapping_id`,`exam_status`,`paper_attempts` FROM 
			`student_exam_mapping` WHERE `exam_id`=%s and `student_id`=%s""",
			(exam_id,student_id))
		exammapdata = cursor.fetchone()

		if exammapdata != None:
			paper_attempts = exammapdata['paper_attempts']+1
			update_status = ("""UPDATE `student_exam_mapping` SET `exam_status`= %s,`paper_attempts`=%s 
				WHERE `exam_id`=%s and `student_id`=%s""")
			updatedata = cursor.execute(update_status,(exam_status,paper_attempts,exam_id,student_id))
			if updatedata:
				msg = "Updated"
				exam_mapping_id = exammapdata['mapping_id']
				details['exam_mapping_id'] = exam_mapping_id

			else:
				msg = "Not Updated"
		else:
			map_query = ("""INSERT INTO `student_exam_mapping`(`exam_id`,
				`student_id`,`exam_status`,`paper_attempts`) 
				VALUES(%s,%s,%s,%s)""")
			
			mapdata = cursor.execute(map_query,(exam_id,student_id,
				exam_status,1))
			
			if mapdata:
				msg = "Added"
				exam_mapping_id = cursor.lastrowid
				details['exam_mapping_id'] = exam_mapping_id

			else:
				msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Student Exam Details",
                                "status": "success",
                                "msg": msg
	                            },
	             "responseList": details}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/StudentExamSectionMapping")
class StudentExamSectionMapping(Resource):
	@api.expect(stu_exam_section)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details['exam_id']
		section_id = details['section_id']
		student_id = details['student_id']
		section_status = details['section_status']
		section_duration = details['section_duration']

		cursor.execute("""SELECT `section_mapping_id`,`section_status` FROM 
			`student_examsection_mapping` WHERE `exam_id`=%s and 
			`section_id`=%s and `student_id`=%s""",(exam_id,section_id,student_id))
		secmapdata = cursor.fetchone()

		if secmapdata != None:
			update_status = ("""UPDATE `student_examsection_mapping` SET `section_status`=%s,
				`section_duration`=%s WHERE `exam_id`=%s and 
				`section_id`=%s and `student_id`=%s""")
			updatedata = cursor.execute(update_status,(section_status,section_duration,exam_id,section_id,student_id))
			if updatedata:
				msg = "Updated"
				section_mapping_id = secmapdata['section_mapping_id']
				details['section_mapping_id'] = section_mapping_id

			else:
				msg = "Not Updated"
		else:
			map_query = ("""INSERT INTO `student_examsection_mapping`(`exam_id`,
				`section_id`,`student_id`,`section_status`,`section_duration`) 
				VALUES(%s,%s,%s,%s,%s)""")
			
			mapdata = cursor.execute(map_query,(exam_id,section_id,student_id,
				section_status,section_duration))
			
			if mapdata:
				msg = "Added"
				section_mapping_id = cursor.lastrowid
				details['section_mapping_id'] = section_mapping_id

			else:
				msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Student Exam Section Details",
                                "status": "success",
                                "msg": msg
	                            },
	             "responseList": details}), status.HTTP_200_OK

#----------------------------------------------------------#
@name_space.route("/StudentQuestionMapping")
class StudentQuestionMapping(Resource):
	@api.expect(stu_que_section)
	def post(self):
		connection = study_break()
		cursor = connection.cursor()
		details = request.get_json()
		
		exam_id = details['exam_id']
		section_id = details['section_id']
		student_id = details['student_id']
		question_id = details['question_id']
		option_id = details['option_id']
		answer = details['answer']
		question_status = details['question_status']
		question_duration = details['question_duration']
		mark_status = details.get('mark_status',0)
		
		cursor.execute("""SELECT `mapping_id`,`question_status`,`mark_status` FROM 
			`student_question_mapping` WHERE `exam_id`=%s 
			and `section_id`=%s and `question_id`=%s and 
			`student_id`=%s""",(exam_id,section_id,question_id,student_id))
		quemapdata = cursor.fetchone()

		if quemapdata != None:
			update_status = ("""UPDATE `student_question_mapping` SET `option_id`=%s,
				`answer`=%s,`question_status`=%s,`question_duration`=%s,`mark_status`=%s WHERE 
				`exam_id`=%s and `section_id`=%s and `question_id`=%s 
				and `student_id`=%s""")
			updatedata = cursor.execute(update_status,(option_id,answer,question_status,
				question_duration,mark_status,exam_id,section_id,question_id,student_id))
			if updatedata:
				msg = "Updated"
				question_mapping_id = quemapdata['mapping_id']
				details['question_mapping_id'] = question_mapping_id

			else:
				msg = "Not Updated"
		else:
			map_query = ("""INSERT INTO `student_question_mapping`(`exam_id`,
				`section_id`,`student_id`,`question_id`,`option_id`,`answer`,`question_status`,
				`question_duration`,`mark_status`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			
			mapdata = cursor.execute(map_query,(exam_id,section_id,student_id,
				question_id,option_id,answer,question_status,question_duration,mark_status))
			
			if mapdata:
				msg = "Added"
				question_mapping_id = cursor.lastrowid
				details['question_mapping_id'] = question_mapping_id

			else:
				msg = "Not Added"

		connection.commit()
		cursor.close()

		return ({"attributes": {
								"status_desc": "Student Question Mapping Details",
                                "status": "success",
                                "msg": msg
	                            },
	             "responseList": details}), status.HTTP_200_OK


#-----------------------------------------------------#
@name_space.route("/SectionWiseStudentQuestionStatusByStudentIdSectionIdExamId/<int:exam_id>/<int:section_id>/<int:student_id>")	
class SectionWiseStudentQuestionStatusByStudentIdSectionIdExamId(Resource):
	def get(self,exam_id,section_id,student_id):
		connection = study_break()
		cursor = connection.cursor()
		queDtls = {}
		studentsectionDtls = []

		cursor.execute("""SELECT count(`question_id`)as count FROM 
			`question` WHERE `section_id`=%s and `exam_id`=%s""",
			(section_id,exam_id))

		countDtls = cursor.fetchone()
		total_count = countDtls.get('count')
		
		cursor.execute("""SELECT `question_id`,`quetion_type` FROM `question` WHERE 
			`exam_id`=%s and `section_id`=%s""",(exam_id,section_id))

		examdtls = cursor.fetchall()
		if examdtls != ():
			for qid in range(len(examdtls)):
				cursor.execute("""SELECT`question_id`,question_duration  FROM `student_question_mapping` sqm 
				 	WHERE `student_id`=%s and `exam_id`=%s and `section_id`=%s""",
					(student_id,exam_id,section_id))

				studentdtls = cursor.fetchone()
				if studentdtls == None:
					queDtls['section_id'] = section_id
					queDtls['section_status'] = "notvisited"
					queDtls['section_duration'] = 0.001
					queDtls['student_id'] = student_id
					queDtls['question_id'] = examdtls[qid]['question_id']
					queDtls['quetion_type'] = examdtls[qid]['quetion_type']
					queDtls['question_status'] = "notvisited"
					queDtls['mark_status'] = 0
					queDtls['question_duration'] = ""
					queDtls['exam_id'] = exam_id
					
					studentsectionDtls.append(queDtls.copy())
				else:
					
					cursor.execute("""SELECT distinct(sqm.`question_id`),`question_status`,`mark_status`,
						question_duration,sqm.`exam_id`,sqm.`section_id`,sqm.`student_id`,
						`section_status`, `section_duration` FROM `student_question_mapping` sqm 
						Left join `student_examsection_mapping` ssm on 
						sqm.`section_id`=ssm.`section_id` WHERE 
						sqm.`student_id`=%s and sqm.`question_id`=%s 
						and sqm.`exam_id`=%s and sqm.`section_id`=%s""",
						(student_id,examdtls[qid]['question_id'],exam_id,section_id))

					sectiondtls = cursor.fetchone()

					if sectiondtls != None:
						sectiondtls['section_status'] = "visited"
						sectiondtls['section_duration'] = sectiondtls['section_duration']
						studentsectionDtls.append(sectiondtls)
						
					else:
						queDtls['section_id'] = section_id
						queDtls['section_status'] = "visited"
						queDtls['section_duration'] = 0.001
						queDtls['student_id'] = student_id
						queDtls['question_id'] = examdtls[qid]['question_id']
						queDtls['quetion_type'] = examdtls[qid]['quetion_type']
						queDtls['question_status'] = "notanswered"
						queDtls['mark_status'] = 0
						queDtls['question_duration'] = 0.001
						queDtls['exam_id'] = exam_id
						
						studentsectionDtls.append(queDtls.copy())	
					
		else:
			studentsectionDtls = []
		statusCount = dict()
		for x in studentsectionDtls:
			mark_status = "not_marked"
			if x['mark_status'] == 1:
				mark_status = "marked"
			elif x['mark_status'] == 2:
				mark_status = "marked_for_review"
			statusCount[mark_status] = statusCount.get(mark_status,0)+1
			statusCount[x['question_status']] = statusCount.get(x['question_status'],0)+1

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Wise Student Questions Details",
	                            "status": "success",
	                            "total":total_count,
	                            "status_count":statusCount
								},
	             "responseList": studentsectionDtls}), status.HTTP_200_OK

#----------------------------------------------------#
@name_space.route("/StudentExamSectionStatusByStudentIdExamId/<int:exam_id>/<int:student_id>")	
class StudentExamSectionStatusByStudentIdExamId(Resource):
	def get(self,exam_id,student_id):
		connection = study_break()
		cursor = connection.cursor()
		secList = []
		secDtls = {}

		cursor.execute("""SELECT count(`section_id`)as count FROM 
			`exam_section_master` WHERE `exam_id`=%s""",(exam_id))

		seccountDtls = cursor.fetchone()
		total_count = seccountDtls.get('count')
		
		cursor.execute("""SELECT count(`section_id`)as count FROM 
			`student_examsection_mapping` WHERE `exam_id`=%s and 
			`student_id`=%s and `section_status`='completed'""",
			(exam_id,student_id))

		secStatusDtls = cursor.fetchone()
		
		if secStatusDtls:
			Status_count = secStatusDtls.get('count')
		else:
			Status_count = 0
		
		cursor.execute("""SELECT `section_id`,`name` FROM 
			`exam_section_master` WHERE `exam_id`=%s""",(exam_id))
		sectionmasterDtls = cursor.fetchall()

		if sectionmasterDtls != ():
			for smid in range(len(sectionmasterDtls)):

				cursor.execute("""SELECT `section_status`,
					`section_duration`,`section_marks` FROM 
					`student_examsection_mapping` WHERE `student_id`=%s 
					and `section_id`=%s and `exam_id`=%s""",
					(student_id,sectionmasterDtls[smid]['section_id'],exam_id))

				sectionDtls = cursor.fetchone()
				
				if sectionDtls:
					if sectionDtls['section_marks'] == None:
						sectionDtls['section_marks'] = 0
					else:
						sectionDtls['section_marks'] = sectionDtls['section_marks']
					
					if sectionDtls['section_duration'] == None:
						sectionDtls['section_duration'] = 0.001
					else:
						sectionDtls['section_duration'] = sectionDtls['section_duration']

					sectionDtls['section_id'] = sectionmasterDtls[smid]['section_id']
					sectionDtls['name'] = sectionmasterDtls[smid]['name']
					secList.append(sectionDtls)
				else:
					secDtls['section_status'] = "notcompleted"
					secDtls['section_marks'] = 0
					
					secDtls['section_duration'] = 0.001
					
					secDtls['section_id'] = sectionmasterDtls[smid]['section_id']
					secDtls['name'] = sectionmasterDtls[smid]['name']
					
					secList.append(secDtls.copy())
				
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Section Wise Student Questions Details",
	                            "status": "success",
	                            "totalSection":total_count,
             					"totalCompletedSection":Status_count
					             
	                            },
	             "responseList": secList }), status.HTTP_200_OK

#--------------------------------------------------------------#
@name_space.route("/ExamListByStudentId/<int:student_id>")	
class ExamListByStudentId(Resource):
	def get(self,student_id):
		connection = study_break()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `exam_id`,`type`,`name`,`module_id`,
			`teacher_id`,`fullmarks`,`duration`,`topic_id`,`subtopic_id` 
			FROM `exam_master`""")
		allExamsData = cursor.fetchall()

		total_count = 0
		examdtls = []
		for x in allExamsData:
			cursor.execute("""SELECT `paper_attempts` FROM `student_exam_mapping` WHERE `exam_id`=%s and `student_id`=%s""",(x['exam_id'],student_id))
			paper_attemptsdtls = cursor.fetchone();
			spaper_attempts = 0
			if paper_attemptsdtls:
				spaper_attempts = paper_attemptsdtls.get('paper_attempts')
			cursor.execute("""SELECT `paper_attempts`,`pause_paper`,`navigable_section`,`submit`,`threshold_unattempted` FROM `exam_section_settings` WHERE `exam_id` = %s AND `section_id`=0""",(x['exam_id']))
			paper_attemptsdtls = cursor.fetchone();
			mpaper_attempts = 1
			if paper_attemptsdtls:
				mpaper_attempts = paper_attemptsdtls.get('paper_attempts')
				x['pause_paper'] = paper_attemptsdtls.get('pause_paper')
				x['navigable_section'] = paper_attemptsdtls.get('navigable_section')
				x['submit'] = paper_attemptsdtls.get('submit')
				x['threshold_unattempted'] = paper_attemptsdtls.get('threshold_unattempted')
			else:
				x['pause_paper'] = 'n'
				x['navigable_section'] = 'n'
				x['submit'] = 'after completion'
				x['threshold_unattempted'] = 0
			if mpaper_attempts>spaper_attempts:
				x['paper_attempts_left'] = mpaper_attempts-spaper_attempts
				examdtls.append(x)
				
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Student Wise Exam List Details",
	                            "status": "success",
	                            "total":total_count
								},
	             "responseList": examdtls}), status.HTTP_200_OK

#----------------------------------------------------------#

#----------------------------------------------------------#
@name_space.route("/getStatusOfExam")
class getStatusOfExam(Resource):
	@api.expect(exam_status_model)
	def post(self): 

		connection = study_break()
		cursor = connection.cursor()

		details = request.get_json()


		get_student_question_mapping_query = ("""SELECT `exam_id`,`student_id`,`question_duration`,`section_id`,`question_id`
					FROM `student_question_mapping` WHERE `exam_id` = %s and `student_id` = %s""")
		student_question_mapping_data = (details['exam_id'],details['student_id'])
		count_student_question_mapping = cursor.execute(get_student_question_mapping_query,student_question_mapping_data)

		if count_student_question_mapping > 0:
			student_question_data = cursor.fetchall()
			for key,data in enumerate(student_question_data):			
				student_question_data[key]['exam_id'] = data['exam_id']
				student_question_data[key]['student_id'] = data['student_id']
				student_question_data[key]['exam_pause_status'] = "yes"
				student_question_data[key]['exam_timer_count'] = data['question_duration'] * 60
				student_question_data[key]['exam_start_section_id'] = data['section_id']
				student_question_data[key]['exam_start_question_id'] = data['question_id']


			return ({"attributes": {"status_desc": "Student Exam Status",
	                            "status": "success"
								},
	             "responseList": student_question_data}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Student Exam Status",
	                            "status": "success"
								},
	             "responseList": {}}), status.HTTP_200_OK

#----------------------------------------------------------#
