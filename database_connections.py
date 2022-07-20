import pymysql


def connect_recess():
	connection = pymysql.connect(host='recess.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='recess_admin',
	                             password='hiHFy1FFJ9L1VDjmDo11',
	                             db='user_credential',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection


def study_break():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='study_break',
									charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection

def connect_logindb():
	connection = pymysql.connect(host='career-modular-db.cjghxwo955mp.us-east-2.rds.amazonaws.com',
								user='career_admin',
								password='blIXOZEU8I1l2JhvKotk',
								db='creamson_logindb',
								charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection

def connect_lab_lang1():
	connection = pymysql.connect(host='career-modular-db.cjghxwo955mp.us-east-2.rds.amazonaws.com',
								user='career_admin',
								password='blIXOZEU8I1l2JhvKotk',
								db='creamson_lab_lang1',
								charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection