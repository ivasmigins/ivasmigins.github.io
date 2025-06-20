import secrets
from datetime import timedelta

class Config:
	SECRET_KEY = secrets.token_hex(32)
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SAMESITE = 'Lax'
	PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
	SESSION_COOKIE_SECURE = True
	DB_CONFIG = {
		'host': '127.0.0.1',
		'port': 3306,
		'user': 'root',
		'password': '',
		'database': 'wristfullydb'
	}
