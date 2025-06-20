from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

passh = PasswordHasher()

def hash_password(password: str):
	return passh.hash(password)

def check_password(password: str, hashed: str):
	try:
		return passh.verify(hashed, password)
	except VerifyMismatchError:
		return False
