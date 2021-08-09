from flask import Blueprint, session
from flask import jsonify
from app.libs.decorators import ValidateApiRequest

api = Blueprint('api', __name__, url_prefix='/api')
api_request = ValidateApiRequest()

from app.controllers.v1 import transactions


@api.route('/', methods=['GET', 'POST'])
def api_base():
    return jsonify(code="00", msg="PAYMENT ENGINE ENTRY", data={})
