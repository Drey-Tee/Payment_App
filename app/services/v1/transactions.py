import datetime
import json
import re
import traceback
import requests
from flask import jsonify
from mongoengine.queryset.visitor import Q

from app.config import config
from app.libs.logger import Logger
from app.libs.utils import GeneratorUtils
from app.models.transactions import Transactions, Status, Currency


class TransactionService:
    """
    Class contains functions and attributes for transaction service
    """

    @staticmethod
    def initiate_payment(data):
        try:
            transaction_data = Transactions()
            transaction_data.customer_email = data['customer_email'].strip()
            transaction_data.amount = data['amount'] * 100
            transaction_data.currency = Currency.GHS.value
            transaction_data.status = Status.INITIATED.value
            transaction_data.reference = GeneratorUtils.generate_string()
            transaction_data.mobile_money['phone'] = data['phone'].strip()
            transaction_data.mobile_money['provider'] = data['provider'].strip()  # mtn, vod, tigo

            transaction_data.save()

            Logger.info(__name__, "initiate_payment", "00", "Payment request saved successfully",
                        transaction_data.to_dict())

            transaction_data = transaction_data.to_dict()
            result = TransactionService.request_payment(transaction_data)

        except KeyError as kex:
            Logger.error(__name__, "initiate_payment", "02", "KeyError: {}".format(str(kex)), traceback.format_exc())
            result = {'code': "02", 'msg': 'Payment could not be initiated'}

        except Exception as ex:
            Logger.error(__name__, "initiate_payment", "02", "Exception occurred: {}".format(str(ex)),
                         traceback.format_exc())
            result = {'code': "02", 'msg': 'Payment could not be initiated'}

        return result

    @staticmethod
    def request_payment(transaction_data):

        if transaction_data is not None:
            request = {
                "amount": transaction_data.get('amount'),
                "email": transaction_data.get('customer_email'),
                "currency": transaction_data.get('currency'),
                "reference": transaction_data.get('reference'),
                "mobile_money": {
                    "phone": transaction_data.get('mobile_money').get('phone'),
                    "provider": transaction_data.get('mobile_money').get('provider')
                }
            }

            Logger.debug(__name__, "request_payment", "00", "Request to initiate transaction on paystack api",
                         request)
            headers = {
                'Authorization': 'Bearer {0}'.format(config.PAYSTACK_SECRET_KEY),
                'content-type': 'application/json'
            }

            try:
                response = requests.post(config.API_URL + '/charge', data=json.dumps(request), headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('status'):
                        return {'code': "00", 'msg': 'Payment initiated successfully'}
                    else:
                        Logger.warn(__name__, "request_payment", "01",
                                    "Paystack response status | Reason:  %s" % (response.json()))
                        result_data = TransactionService.update_transaction_status(transaction_data.get('reference'),
                                                                                   Status.FAILED.value)
                        if result_data is None:
                            return {'code': "01", 'msg': 'Transaction not found'}

                        return {'code': "01", 'msg': 'Payment could not be initiated'}

                else:
                    Logger.warn(__name__, "request_payment", "01",
                                "Paystack response status | Reason:  %s" % (response.json()))
                    result_data = TransactionService.update_transaction_status(transaction_data.get('reference'),
                                                                               Status.FAILED.value)
                    if result_data is None:
                        return {'code': "01", 'msg': 'Transaction not found'}

                    return {'code': "01", 'msg': 'Payment could not be initiated'}

            except requests.exceptions.HTTPError as error:
                Logger.error(__name__, "initiate_payment", "02", "Exception occurred: {}".format(str(error)),
                             traceback.format_exc())
                return {'code': "02", 'msg': 'Payment could not be initiated'}
            except requests.exceptions.ConnectionError as error:
                Logger.error(__name__, "initiate_payment", "02", "Exception occurred: {}".format(str(error)),
                             traceback.format_exc())
                return {'code': "02", 'msg': 'Payment could not be initiated'}
            except requests.exceptions.Timeout as error:
                Logger.error(__name__, "initiate_payment", "02", "Exception occurred: {}".format(str(error)),
                             traceback.format_exc())
                return {'code': "02", 'msg': 'Payment could not be initiated'}
            except requests.exceptions.RequestException as error:
                Logger.error(__name__, "initiate_payment", "02", "Exception occurred: {}".format(str(error)),
                             traceback.format_exc())
                return {'code': "02", 'msg': 'Payment could not be initiated'}

    @staticmethod
    def update_transaction_status(reference, status):
        try:

            transaction_data = Transactions.objects(reference=reference).first()

            if transaction_data is None:
                Logger.warn(__name__, "update_transaction_status", "01", "Transaction [{}] not found".format(reference))
                transaction_data = None

            transaction_data.status = status
            transaction_data.updated_at = datetime.datetime.utcnow()

            transaction_data.save()
            transaction_data = transaction_data.to_dict()

        except KeyError as kex:
            Logger.error(__name__, "update_transaction_status", "02", "KeyError: {}".format(str(kex)),
                         traceback.format_exc())
            raise kex
        except Exception as ex:
            Logger.error(__name__, "update_transaction_status", "02", "Exception occurred: {}".format(str(ex)),
                         traceback.format_exc())
            raise ex
        return transaction_data

    @staticmethod
    def check_transaction_status(data):
        try:
            if data.get('data').get('status') == 'success':
                result_data = TransactionService.update_transaction_status(data.get('data').get('reference'),
                                                                           Status.SUCCESS.value)

                if result_data is None:
                    return {'code': "01", 'msg': 'Transaction not found'}

                return {'code': "00", 'msg': 'Transaction status updated successfully | reference : {}'.format(
                    data.get('data').get('reference')), 'data': result_data}

            elif data.get('data').get('status') == 'failed':
                result_data = TransactionService.update_transaction_status(data.get('data').get('reference'),
                                                                           Status.FAILED.value)
                if result_data is None:
                    return {'code': "01", 'msg': 'Transaction not found'}

                return {'code': "00", 'msg': 'Transaction status updated successfully | reference : {}'.format(
                    data.get('data').get('reference')), 'data': result_data}

            elif data.get('data').get('status') == 'pending':
                result_data = TransactionService.update_transaction_status(data.get('data').get('reference'),
                                                                           Status.PENDING.value)
                if result_data is None:
                    return {'code': "01", 'msg': 'Transaction not found'}

                return {'code': "00", 'msg': 'Transaction status updated successfully | reference : {}'.format(
                    data.get('data').get('reference')), 'data': result_data}

        except Exception as ex:
            Logger.warn(__name__, "check_transaction_status", "02",
                        "Transaction status could not be updated | Reason:  %s" % (str(ex)))
            return {'code': "01", 'msg': 'Transaction status could not be updated', 'data': []}

    @staticmethod
    def find_transactions(order_by='-initiated_at', paginate=True, minimal=True, **filter_parameters):
        try:

            query = {}
            for field, value in filter_parameters.items():
                if field.split('__')[0] in Transactions._fields and value != '':
                    query[field] = value

            if 'size' not in filter_parameters:
                filter_parameters['size'] = config.DEFAULT_LIMIT
            if 'page' not in filter_parameters:
                filter_parameters['page'] = config.DEFAULT_PAGE

            # print("query | {0}".format(query))

            Logger.debug(__name__, "find_transactions", "00", "Filter query: %s" % str(query))

            if filter_parameters.get('start_date') and not filter_parameters.get('end_date'):
                transactions_data = Transactions.objects(
                    initiated_at__gte=datetime.datetime.strptime(filter_parameters['start_date'], '%Y-%m-%d')) \
                    .filter(**query).order_by(order_by)
            elif not filter_parameters.get('start_date') and filter_parameters.get('end_date'):
                transactions_data = Transactions.objects(
                    initiated_at__lt=datetime.datetime.strptime(filter_parameters['end_date'],
                                                                "%Y-%m-%d") + datetime.timedelta(days=1)
                ).filter(**query).order_by(order_by)
            elif filter_parameters.get('start_date') and filter_parameters.get('end_date'):
                transactions_data = Transactions.objects(
                    initiated_at__gte=datetime.datetime.strptime(filter_parameters['start_date'], '%Y-%m-%d'),
                    initiated_at__lt=datetime.datetime.strptime(filter_parameters['end_date'],
                                                                '%Y-%m-%d') + datetime.timedelta(days=1)
                ).filter(**query).order_by(order_by)
            else:
                transactions_data = Transactions.objects.filter(**query).order_by(order_by)

            # Paginate, if pagination requested
            transactions_list = []
            nav = None
            if paginate:
                transactions_data = transactions_data.paginate(int(filter_parameters['page']),
                                                               int(filter_parameters['size']))
                nav = {
                    'current_page': int(filter_parameters['page']),
                    'next_page': transactions_data.next_num,
                    'prev_page': transactions_data.prev_num,
                    'total_pages': transactions_data.pages,
                    'total_records': transactions_data.total,
                    'size': int(filter_parameters['size'])
                }

                for transactions in transactions_data.items:
                    trans_data = transactions.to_dict(minimal=minimal)
                    trans_data['amount'] = trans_data['amount'] / 100
                    transactions_list.append(trans_data)
            else:
                for transactions in transactions_data:
                    trans_data = transactions.to_dict(minimal=minimal)
                    trans_data['amount'] = trans_data['amount'] / 100
                    transactions_list.append(trans_data)
            return transactions_list, nav
        except Exception as ex:
            Logger.error(__name__, "find_transactions", "02", "Error while finding transactions",
                         traceback.format_exc())
            raise ex

    @staticmethod
    def get_by_id(uid, minimal=False):

        try:
            transaction_data = Transactions.objects(id=uid).first()
            if transaction_data is not None:
                transaction_data = transaction_data.to_dict(minimal=minimal)
                transaction_data['amount'] = transaction_data['amount'] / 100
        except Exception as ex:
            transaction_data = None
            Logger.error(__name__, "get_by_id", "02", "Exception occurred: {}".format(ex), traceback.format_exc())

        return transaction_data
