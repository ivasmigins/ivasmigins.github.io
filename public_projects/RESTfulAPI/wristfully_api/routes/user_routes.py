from flask import Blueprint, request, jsonify, session
from wristfully_api.auth.decorators import login_required
from wristfully_api.utils.sanitization import *
from wristfully_api.utils.helpers import *
from wristfully_api.utils.queries import runGetQuerySafe, runSetQuerySafe
from wristfully_api.auth.hash_utils import check_password, hash_password

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/register/user', methods=['POST'])
def register_user():
	data = request.get_json(silent=False, force=True)
	
	sanitiseInput(data['username'])
	sanitiseInput(data['password'])
	sanitiseInput(data['firstname'])
	sanitiseInput(data['lastname'])
	sanitiseInputDate(data['birthdate'])
	
	hashed_password = hash_password(data['password'])
	query = 'INSERT INTO users (username, password, firstname, lastname, birthdate) VALUES (?, ?, ?, ?, ?)'
	params = (data['username'], hashed_password, data['firstname'], data['lastname'], data['birthdate'])
	
	return runSetQuerySafe(query, params)

@user_blueprint.route('/login', methods=['POST'])
def login_user():
	data = request.get_json(silent=False, force=True)
	
	sanitiseInput(data['username'])
	sanitiseInput(data['password'])
	
	# Parameterized query to prevent SQL injection
	query = 'SELECT * FROM users WHERE username = ?'
	
	try:
		user_data = runGetQuerySafe(query, (data['username'],)).get_json(silent=False, force=True)
	except:
		return jsonify(login=False, message="Invalid credentials"), 401
	
	if not user_data:
		return jsonify(login=False, message="Invalid credentials"), 401
	
	if check_password(data['password'], user_data[0]['password']):
		# Create session
		session['user_id'] = data['username']
		session['user_type'] = 'user'
		session.permanent = True
		
		return jsonify(login=True, message="Login successful"), 200
	
	return jsonify(login=False, message="Invalid credentials"), 401
	
@user_blueprint.route('/setwatchuser', methods=['POST'])
@login_required
def set_watch_user(): # User assigns watch to themselves
	data = request.get_json(silent=False, force=True)

	if 'user_id' in session:
		username = session['user_id']
		if data['username'] != username:
			return jsonify({'error': 'Can only assign watches to yourself'}), 403
	else:
		return jsonify({'error': 'Authentication required'}), 401
	
	sanitiseInput(data['username'])
	sanitiseInputNumber(data['watch_id'])
	
	query = 'INSERT INTO watch_user (username, watch_id) VALUES (?, ?)'
	params = (data['username'], data['watch_id'])
	
	return runSetQuerySafe(query, params)

@user_blueprint.route('/me/watches', methods=['GET'])
@login_required
def get_my_watches():
	if 'user_id' not in session:
		return jsonify({'error': 'User access required'}), 403
	
	username = session['user_id']
	query = 'SELECT * FROM watch_user WHERE username = ?'
	return runGetQuerySafe(query, (username,))

@user_blueprint.route('/me/stats/<type>', methods=['GET'])
@user_blueprint.route('/me/stats/<type>/<int:limit>', methods=['GET'])
@login_required
def get_my_stats(type, limit=100):
	if 'user_id' not in session:
		return jsonify({'error': 'User access required'}), 403
	
	username = session['user_id']
	sanitiseInput(type)
	sanitiseInputNumber(limit)

	accessible_watches = get_user_accessible_watches(username)
	if not accessible_watches:
		return jsonify([])
	
	# Create placeholders for IN clause
	placeholders = ','.join(['?' for _ in accessible_watches])
	query = f'SELECT * FROM {type} WHERE watch_id IN ({placeholders}) ORDER BY date DESC LIMIT ?'
	params = accessible_watches + [limit]
	
	return runGetQuerySafe(query, params)

@user_blueprint.route('/user/<user_name>/exists', methods=['GET'])
def get_user_username_taken(user_name):
	sanitiseInput(user_name)
	return find_username_taken("users", user_name)
