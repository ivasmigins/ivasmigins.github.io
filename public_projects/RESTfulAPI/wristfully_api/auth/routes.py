from flask import Blueprint, request, jsonify, session
from wristfully_api.auth.decorators import login_required

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/session', methods=['GET'])
def check_session(): # To check if user is logged in
	if 'user_id' in session:
		return jsonify(logged_in=True, user_type='user', user_id=session['user_id']), 200
	elif 'doctor_id' in session:
		return jsonify(logged_in=True, user_type='doctor', doctor_id=session['doctor_id']), 200
	else:
		return jsonify(logged_in=False), 200

@auth_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
	session.clear()
	return jsonify(message="Logged out"), 200