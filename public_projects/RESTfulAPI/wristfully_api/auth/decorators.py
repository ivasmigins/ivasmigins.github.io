from functools import wraps
from flask import request, session, jsonify
from wristfully_api.utils.api_key import verify_api_key

def login_required(f):
	@wraps(f) # Keeps identity of function since im using this as a decorator
	def decorated_function(*args, **kwargs):
		if 'user_id' not in session and 'doctor_id' not in session:
			return jsonify({'error': 'Authentication required'}), 401
		return f(*args, **kwargs)
	return decorated_function

def api_key_or_login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		# Check for API key first
		api_key = request.headers.get('X-API-Key') # Used by WAS, conventional I think?
		if api_key:
			auth_info = verify_api_key(api_key)
			if auth_info:
				# Session data for this request
				request.authenticated_user = auth_info['username']
				if auth_info['type'] == 'watch':
					request.authenticated_watch_id = auth_info['watch_id']
				return f(*args, **kwargs)
		
		if 'user_id' not in session and 'doctor_id' not in session:
			return jsonify({'error': 'Authentication required'}), 401

		return f(*args, **kwargs)
	return decorated_function