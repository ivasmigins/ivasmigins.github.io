from flask import Blueprint, request, jsonify, session
from wristfully_api.auth.decorators import login_required
from wristfully_api.utils.sanitization import *
from wristfully_api.utils.helpers import *
from wristfully_api.utils.queries import runSetGetQuerySafe, runGetQuerySafe
import mariadb
from wristfully_api.config import Config
from wristfully_api.auth.hash_utils import check_password, hash_password

doctor_blueprint = Blueprint('doctor', __name__)

@doctor_blueprint.route('/register/doctor', methods=['POST'])
def register_doctor():
	data = request.get_json(silent=False, force=True)
	
	sanitiseInput(data['password'])
	sanitiseInput(data['firstname'])
	sanitiseInput(data['lastname'])
	
	hashed_password = hash_password(data['password'])
	set_query = 'INSERT INTO doctors (password, firstname, lastname) VALUES (?, ?, ?)'
	get_query = 'SELECT doctor_id FROM doctors ORDER BY doctor_id DESC LIMIT 1'
	return runSetGetQuerySafe(set_query, (hashed_password, data['firstname'], data['lastname']), get_query, ())

@doctor_blueprint.route('/login/doctor', methods=['POST'])
def login_doctor():
	data = request.get_json(silent=False, force=True)
	
	sanitiseInputNumber(data['doctor_id'])
	sanitiseInput(data['password'])
	
	query = 'SELECT * FROM doctors WHERE doctor_id = ?'
	
	try:
		user_data = runGetQuerySafe(query, (data['doctor_id'],)).get_json(silent=False, force=True)
	except:
		return jsonify(login=False, message="Invalid credentials"), 401
	
	if not user_data:
		return jsonify(login=False, message="Invalid credentials"), 401
	
	if check_password(data['password'], user_data[0]['password']):
		# Create session
		session['doctor_id'] = data['doctor_id']
		session['user_type'] = 'doctor'
		session.permanent = True
		
		return jsonify(login=True, message="Login successful"), 200
	
	return jsonify(login=False, message="Invalid credentials"), 401

@doctor_blueprint.route('/setuserdoctor', methods=['POST'])
@login_required
def set_doctor_user():
	if 'doctor_id' not in session:
		return jsonify({'error': 'Doctor access required'}), 403

	data = request.get_json(silent=False, force=True)
	sanitiseInput(data['username'])
	doctor_id = session['doctor_id']

	# user exists?
	query_check = 'SELECT 1 FROM users WHERE username = ?'
	conn = mariadb.connect(**Config.DB_CONFIG)
	cur = conn.cursor()
	cur.execute(query_check, (data['username'],))
	if not cur.fetchone():
		conn.close()
		return jsonify({'error': 'User not found'}), 404

	query_insert = 'INSERT INTO patients_doctor (username, doctor_id) VALUES (?, ?)'
	try:
		cur.execute(query_insert, (data['username'], doctor_id))
		conn.commit()
		conn.close()
		return jsonify(message="Patient assigned to doctor"), 200
	except mariadb.IntegrityError:
		conn.close()
		return jsonify({'error': 'User is already assigned to this doctor'}), 400

@doctor_blueprint.route('/patient/<username>/stats/<type>', methods=['GET'])
@doctor_blueprint.route('/patient/<username>/stats/<type>/<int:limit>', methods=['GET'])
@login_required
def get_patient_stats(username, type, limit=100):
	if 'doctor_id' not in session:
		return jsonify({'error': 'Doctor access required'}), 403
	
	doctor_id = session['doctor_id']
	if not doctor_can_access_patient(doctor_id, username):
		return jsonify({'error': 'Access denied to this patient'}), 403
	
	sanitiseInput(type)
	sanitiseInput(username)
	sanitiseInputNumber(limit)
	
	patient_watches = get_patient_watches(username)
	if not patient_watches:
		return jsonify([])
	
	placeholders = ','.join(['?' for _ in patient_watches])
	query = f'SELECT * FROM {type} WHERE watch_id IN ({placeholders}) ORDER BY date DESC LIMIT ?'
	params = patient_watches + [limit]
	
	return runGetQuerySafe(query, params)

@doctor_blueprint.route('/my-patients', methods=['GET'])
@login_required
def get_my_patients():
	if 'doctor_id' not in session:
		return jsonify({'error': 'Doctor access required'}), 403
	
	doctor_id = session['doctor_id']
	query = 'SELECT username FROM patients_doctor WHERE doctor_id = ?'
	return runGetQuerySafe(query, (doctor_id,))