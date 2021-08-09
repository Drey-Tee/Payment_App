import os
import sys

from app.config.base import BaseConfig
from app.config.production import ProductionConfig

env = os.environ.get('APP_ENV', 'DEFAULT')

if env == 'production':
    config = ProductionConfig
elif env in ('DEFAULT', 'dev'):
    config = BaseConfig
else:
    print("Unknown application environment: {0}".format(env))
    sys.exit(4)