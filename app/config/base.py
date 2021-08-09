import os


class BaseConfig(object):
    # Enabling development environment
    DEBUG = False

    # Application PORT
    PORT = 8000

    # Application Host
    HOST = '0.0.0.0'

    # External APIS
    API_URL = "https://api.paystack.co"
    PAYSTACK_SECRET_KEY = 'sk_test_c9c638528f2d47e7814065b6990dbd3373728a4e'


    # Pagination
    DEFAULT_PAGE = 1
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 10

    # Logging Configuration
    EVENT_LOG_PATH = 'logs/access.log'
    ERROR_LOG_PATH = 'logs/error.log'

    # MongoDb Config
    MONGODB_DB = os.environ.get('payment_db', 'payment_db')
    MONGODB_HOST = os.environ.get('payment_db_host', 'localhost')
    MONGODB_PORT = int(os.environ.get('payment_db_port', 27017))  # int(os.environ.get('CRM_DB_PORT', 27017))
    MONGODB_USERNAME = ""
    MONGODB_PASSWORD = ""

    # SECRET_KEY
    SECRET_KEY = '&*#$@%fgfgf555hh'



