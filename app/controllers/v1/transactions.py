import json
import traceback
from flask import jsonify
from flask import request

from app.controllers import api
from app.controllers import api_request
from app.libs.logger import Logger
from app.services.v1.transactions import TransactionService


@api.route('/v1/transaction/initiate', methods=['POST'])
@api_request.json
@api_request.required_body_params('customer_email', 'amount', 'phone', 'provider')
def initiate_transaction():
    # Get request data
    request_data = json.loads(request.data.decode('utf-8'))
    Logger.debug(__name__, "initiate_transaction", "00", "Received request to initiate transaction", request_data)

    transaction = TransactionService.initiate_payment(request_data)
    print("transaction | {}".format(transaction))
    if transaction.get('code') == "00":
        return jsonify(code="00", msg=transaction.get('msg'))
    else:
        return jsonify(code="01", msg=transaction.get('msg'))


@api.route('/v1/check/transaction/status', methods=['POST'])
def check_transaction_status():
    # Get webhook callback request data from paystack
    request_data = json.loads(request.data.decode('utf-8'))
    Logger.debug(__name__, "check_transaction_status", "00", "Received transaction status from paystack", request_data)
    response = TransactionService.check_transaction_status(request_data)
    if response.get('code') == "00":
        return jsonify(code="00", msg=response.get('msg'), data=response.get('data'))
    else:
        return jsonify(code="01", msg=response.get('msg'), data=response.get('data'))


@api.route('/v1/transactions', methods=['GET'])
def get_transactions():
    Logger.debug(__name__, "get_transactions", "00", "Received request to get transactions")
    params = request.args.to_dict()
    Logger.debug(__name__, "get_transactions", "00", "Param(s) received: %s" % params)
    minimal = False
    paginate = True

    if 'minimal' in params:
        minimal = params.pop('minimal').lower() == 'true'
    if 'paginate' in params:
        paginate = params.pop('paginate').lower() != 'false'

    transactions_list, nav = TransactionService.find_transactions(paginate=paginate, minimal=minimal, **params)
    print("transaction_list | {}".format(transactions_list))
    return jsonify(code="00", msg="Data retrieved successfully'", nav=nav, data=transactions_list)


@api.route('/v1/transactions/<transactions_id>', methods=['GET'])
def get_transaction(transactions_id):
    Logger.debug(__name__, "get_transaction", "00", "Received request to get transaction [%s]" % transactions_id)

    transaction_data = TransactionService.get_by_id(transactions_id)
    if transaction_data is None:
        Logger.warn(__name__, "get_application", "01", "Application [%s] does not exist" % transactions_id)
        return jsonify(code="02", msg="Transaction does not exist", data={})

    return jsonify(code="00", msg="Transaction Retrieved Successfully", data=transaction_data)
