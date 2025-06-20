from flask import Blueprint, request, jsonify, session
from wristfully_api.auth.decorators import login_required
from wristfully_api.utils.sanitization import *
from wristfully_api.utils.helpers import *
from datetime import datetime
import mariadb
from wristfully_api.config import Config

def find_username_taken(type, user_name):
	query = f'SELECT * FROM {type} WHERE username = ?'
	
	conn = mariadb.connect(**Config.DB_CONFIG)
	cur = conn.cursor()
	
	cur.execute(query, (user_name,))
	found = cur.fetchone() is not None
	
	conn.close()
	return jsonify(taken=found), 200

def sanitiseInput(input):
	if '%' in input:
		raise Exception("Invalid character in input.")

def sanitiseInputNumber(input):
	if not isinstance(input, (int, float, complex)):
		raise Exception("Passed something that's not a number as an input. Instead, it was a " + type(input).__name__ + " .")

def sanitiseInputDate(input):
	accepted_formats = ["%Y-%m-%d",	"%Y-%m-%dT%H:%M:%S"]
	for	fmt in accepted_formats:
		try:
			parsed_date = datetime.strptime(input, fmt)
			break # Good
		except ValueError:
			parsed_date	= None
	if parsed_date is None:
		raise Exception("Invalid date format!")

def sanitiseInputBool(input):
	if (input < 0 or input > 1): 
		raise Exception("Object passed is not a bool! Instead, it's \"" + str(input) + "\".")

def sanitisePercentage(input):
	if (input < 0 or input > 100): 
		raise Exception("Percentage " + str(input) + "% outside of valid range")

def sanitiseHeartRate(input):
	if (input < 20): 
		raise Exception("Heartrate outside of logical boundaries! Heartrate reported as " + str(input) + ".")

def stringToNumber(input):
	return int(input)

def numberToString(input):
	return str(input)