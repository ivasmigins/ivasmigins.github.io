from flask import Flask
from flask_cors import CORS
from wristfully_api.config import Config
from wristfully_api.auth.routes import auth_blueprint
from wristfully_api.routes.user_routes import user_blueprint
from wristfully_api.routes.doctor_routes import doctor_blueprint
from wristfully_api.routes.watch_routes import watch_blueprint
from wristfully_api.routes.data_routes import data_blueprint

def create_app():
	app = Flask(__name__)
	app.config.from_object(Config)
	CORS(app, supports_credentials=True)

	app.register_blueprint(auth_blueprint)
	app.register_blueprint(user_blueprint)
	app.register_blueprint(doctor_blueprint)
	app.register_blueprint(watch_blueprint)
	app.register_blueprint(data_blueprint)

	@app.route("/", methods=["GET"])
	def index():
		return "Wristfully Co. API"

	return app

if __name__ == '__main__':
	create_app().run(host='0.0.0.0', port=5000)
