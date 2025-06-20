from flask import Blueprint, request, jsonify, session
from wristfully_api.utils.sanitization import sanitiseInputNumber
import mariadb
from wristfully_api.config import Config
import secrets

watch_blueprint = Blueprint('watch', __name__)

@watch_blueprint.route('/register/watch', methods=['POST'])
def register_watch(): # Adds the watch to the database and gives it an unique API Key 
	data = request.get_json(silent=False, force=True)
	sanitiseInputNumber(data['version'])

	conn = mariadb.connect(**Config.DB_CONFIG)
	cur = conn.cursor()

	for _ in range(10): # 10 attempts max
		api_key = secrets.token_urlsafe(5)

		try:
			cur.execute('INSERT INTO watch (version, api_key) VALUES (?, ?)', 
						(data['version'], api_key))
			conn.commit()
			watch_id = cur.lastrowid
			conn.close()
			return jsonify(watch_id=watch_id, api_key=api_key), 200
		except mariadb.IntegrityError: # Retry
			continue

	conn.close()
	return jsonify({'error': 'Failed to generate unique API key after multiple attempts'}), 500

