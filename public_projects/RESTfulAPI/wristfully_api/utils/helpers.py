from flask import Blueprint, request, jsonify, session
import mariadb
from wristfully_api.config import Config

def get_current_user(): # Get user from session or API key
	if hasattr(request, 'authenticated_user'):
		return request.authenticated_user
	elif 'user_id' in session:
		return session['user_id']
	return None

def get_current_watch_id(): # Get watch_id if auth by API key
	if hasattr(request, 'authenticated_watch_id'):
		return request.authenticated_watch_id
	return None

def get_user_accessible_watches(username):
	query = 'SELECT watch_id FROM watch_user WHERE username = ?'
	conn = mariadb.connect(**Config.DB_CONFIG)
	cur = conn.cursor()
	cur.execute(query, (username,))
	results = cur.fetchall()
	conn.close()
	return [row[0] for row in results]

def get_doctor_accessible_patients(doctor_id): 
	query = 'SELECT username FROM patients_doctor WHERE doctor_id = ?'
	conn = mariadb.connect(**Config.DB_CONFIG)
	cur = conn.cursor()
	cur.execute(query, (doctor_id,))
	results = cur.fetchall()
	conn.close()
	return [row[0] for row in results]

def get_patient_watches(username):
	query = 'SELECT watch_id FROM watch_user WHERE username = ?'
	conn = mariadb.connect(**Config.DB_CONFIG)
	cur = conn.cursor()
	cur.execute(query, (username,))
	results = cur.fetchall()
	conn.close()
	return [row[0] for row in results]

def user_can_access_watch(username, watch_id):
	accessible_watches = get_user_accessible_watches(username)
	return int(watch_id) in accessible_watches

def doctor_can_access_patient(doctor_id, username):
	accessible_patients = get_doctor_accessible_patients(doctor_id)
	return username in accessible_patients