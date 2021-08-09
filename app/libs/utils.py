# utils.py

import asyncio
import csv
import datetime
import hashlib
import io
import json
import ntpath
import os
import random
import re
# import requests
import string

from app.config import config

SYMBOLS = '!#$%&()*+,-:;<=>?@[]^_{|}~'
CHARS = string.ascii_uppercase + SYMBOLS + string.ascii_lowercase + string.digits
CHARS_WITHOUT_SYMBOLS = string.ascii_uppercase + string.ascii_lowercase + string.digits

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_WITH_MICROSECOND_FORMAT = '%Y%m%d%H%M%S%f'
MONGO_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class GeneratorUtils:
    @staticmethod
    def generate_string(length=16, symbols=False):
        if symbols:
            return ''.join(random.choice(CHARS) for _ in range(length))
        return ''.join(random.choice(CHARS_WITHOUT_SYMBOLS) for _ in range(length))


class DateUtils:
    @staticmethod
    def get_timestamp(date_obj=datetime.datetime.utcnow()):
        return int(date_obj.timestamp() * 1000000)

    @staticmethod
    def format_full_date(date_obj):
        return datetime.datetime.strftime(date_obj, DATETIME_WITH_MICROSECOND_FORMAT)

    @staticmethod
    def mongo_date_to_object(date_str):
        return datetime.datetime.strptime(date_str, MONGO_DATE_FORMAT)

    @staticmethod
    def format_datetime(date_obj):
        return datetime.datetime.strftime(date_obj, DATETIME_FORMAT)

    @staticmethod
    def parse_datetime(datetime_str):
        return datetime.datetime.strptime(datetime_str, DATETIME_FORMAT)
