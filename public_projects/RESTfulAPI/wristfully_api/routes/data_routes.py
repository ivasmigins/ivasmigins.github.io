from flask import Blueprint, request, jsonify
from wristfully_api.auth.decorators import api_key_or_login_required
from wristfully_api.utils.sanitization import *
from wristfully_api.utils.helpers import *
from wristfully_api.utils.queries import runSetQuerySafe

data_blueprint = Blueprint('data', __name__)

@data_blueprint.route('/add/steps', methods=['POST'])
@api_key_or_login_required
def add_steps_entry():
	data = request.get_json(silent=False, force=True)
	watch_id = get_current_watch_id()

	if not watch_id:
		return jsonify({'error': 'Authentication required'}), 401

	sanitiseInputNumber(watch_id)
	sanitiseInputNumber(data['amount'])
	sanitiseInputDate(data['date'])

	query = '''
		INSERT INTO steps (watch_id, date, steps)
		VALUES (?, ?, ?)
		ON DUPLICATE KEY UPDATE steps = VALUES(steps)
	'''
	params = (watch_id, data['date'], data['amount'])
	return runSetQuerySafe(query, params)

@data_blueprint.route('/add/falls', methods=['POST'])
@api_key_or_login_required
def add_falls_entry():
	data = request.get_json(silent=False, force=True)
	watch_id = get_current_watch_id()

	if not watch_id:
		return jsonify({'error': 'Authentication required'}), 401

	sanitiseInputNumber(watch_id)
	sanitiseInputDate(data['date'])
	sanitiseInputBool(data['stopped'])

	query = 'INSERT INTO falls (watch_id, date, stopped) VALUES (?, ?, ?)'
	params = (watch_id, data['date'], data['stopped'])
	return runSetQuerySafe(query, params)

@data_blueprint.route('/add/blood-oxygen', methods=['POST'])
@api_key_or_login_required
def add_blood_oxygen_entry():
	data = request.get_json(silent=False, force=True)
	watch_id = get_current_watch_id()

	if not watch_id:
		return jsonify({'error': 'Authentication required'}), 401

	sanitiseInputNumber(watch_id)
	sanitiseInputDate(data['date'])
	sanitisePercentage(data['percentage'])

	query = 'INSERT INTO blood_oxygen (watch_id, date, percentage) VALUES (?, ?, ?)'
	params = (watch_id, data['date'], data['percentage'])
	return runSetQuerySafe(query, params)

@data_blueprint.route('/add/heart-rate', methods=['POST'])
@api_key_or_login_required
def add_heart_rate_entry():
	data = request.get_json(silent=False, force=True)
	watch_id = get_current_watch_id()

	if not watch_id:
		return jsonify({'error': 'Authentication required'}), 401

	sanitiseInputNumber(watch_id)
	sanitiseInputDate(data['date'])
	sanitiseHeartRate(data['bpm'])

	query = 'INSERT INTO heart_rate (watch_id, date, bpm) VALUES (?, ?, ?)'
	params = (watch_id, data['date'], data['bpm'])
	return runSetQuerySafe(query, params)