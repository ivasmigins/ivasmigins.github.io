# Wristfully API

Flask-based RESTful API which uses HTTPOnly Cookies

## ⚙️ Requirements

- Python
- MariaDB
- Flask
- Flask-cors
- Python-dontenv
- Argon2-cffi
- [Postman](https://www.postman.com/) (For testing)

## Setup

### Create virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### Install the required libraries
```
pip install flask flask-cors mariadb python-dotenv argon2-cffi
```

### Run mariadb database
```
mariadb -u root -p < db.sql
```

### Run flask
```
flask run
```

## Behind the creation

### Resources used:
- https://www.merge.dev/blog/api-response-codes
- [Password Hashing](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Http only cookies](https://owasp.org/www-community/HttpOnly)
- https://aws.amazon.com/what-is/restful-api/
- https://auth0.com/blog/developing-restful-apis-with-python-and-flask/
