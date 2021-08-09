from flask import Flask
from app.config import config
from flask import jsonify
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from app.config import config

from app.controllers import api

application = Flask(__name__)
CORS(application)

# Set app db config
application.config['MONGODB_DB'] = config.MONGODB_DB
application.config['MONGODB_HOST'] = config.MONGODB_HOST
application.config['MONGODB_PORT'] = config.MONGODB_PORT
application.config['MONGODB_USERNAME'] = config.MONGODB_USERNAME
application.config['MONGODB_PASSWORD'] = config.MONGODB_PASSWORD
application.secret_key = config.SECRET_KEY

db = MongoEngine(application)

# Register blueprint(s)
application.register_blueprint(api)


@application.errorhandler(404)
def not_found(error):
    return jsonify(code="404", msg="Resource not found"), 404


@application.errorhandler(405)
def method_not_allowed(error):
    return jsonify(code="405", msg="Method not allowed"), 405


if __name__ == '__main__':
    application.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
