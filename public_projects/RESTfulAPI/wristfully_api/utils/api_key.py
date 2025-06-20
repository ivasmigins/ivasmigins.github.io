import mariadb
from wristfully_api.config import Config

def verify_api_key(api_key): # Returns username and watch_id of that API Key
	conn = mariadb.connect(**Config.DB_CONFIG)
	cur = conn.cursor()

	query = '''
		SELECT wu.username, w.watch_id 
		FROM watch w 
		LEFT JOIN watch_user wu ON w.watch_id = wu.watch_id 
		WHERE w.api_key = ?
	'''
	cur.execute(query, (api_key,))
	result = cur.fetchone()
	conn.close()

	if result:
		return {'username': result[0], 'watch_id': result[1], 'type': 'watch'}
	
	return None