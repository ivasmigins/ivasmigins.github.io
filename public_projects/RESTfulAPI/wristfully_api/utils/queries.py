from flask import request, session, jsonify
from wristfully_api.config import Config
import mariadb

def runGetQuerySafe(query, params=()):
	try:
		conn = mariadb.connect(**Config.DB_CONFIG)
		cur = conn.cursor()
		cur.execute(query, params)
		message_rows = cur.fetchall()
		message_columns = [column[0] for column in cur.description]
		message_data = [dict(zip(message_columns, row)) for row in message_rows]
		conn.close()
		return jsonify(message_data)
	except mariadb.Error as e:
		print("MariaDB Error (GET):", e)
		return jsonify(isError=True, message=str(e), statusCode=500), 500

def runSetQuerySafe(query, params=()):
	try:
		conn = mariadb.connect(**Config.DB_CONFIG)
		cur = conn.cursor()
		cur.execute(query, params)
		conn.commit()
		conn.close()
		return jsonify(isError=False, message="Success", statusCode=200), 200
	except mariadb.Error as e:
		print("MariaDB Error (SET):", e)
		return jsonify(isError=True, message=str(e), statusCode=500), 500

def runSetGetQuerySafe(set_query, set_params, get_query, get_params):
	try:
		conn = mariadb.connect(**Config.DB_CONFIG)
		cur = conn.cursor()
		cur.execute(set_query, set_params)
		conn.commit()
		cur.execute(get_query, get_params)
		message_rows = cur.fetchall()
		message_columns = [column[0] for column in cur.description]
		message_data = [dict(zip(message_columns, row)) for row in message_rows]
		conn.close()
		return jsonify(message_data)
	except mariadb.Error as e:
		print("MariaDB Error (SET/GET):", e)
		return jsonify(isError=True, message=str(e), statusCode=500), 500