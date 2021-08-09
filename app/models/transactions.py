import datetime
import enum
from application import db
from app.libs.utils import DateUtils


class Status(enum.Enum):
    INITIATED = 'INITIATED'
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'

    @staticmethod
    def values():
        return [s.value for s in Status]


class Currency(enum.Enum):
    GHS = 'GHS'
    USD = 'USD'

    @staticmethod
    def values():
        return [c.value for c in Currency]


class Transactions(db.Document):
    customer_email = db.EmailField(required=True)
    reference = db.StringField(required=True)
    currency = db.StringField(required=True, default=Currency.GHS.value, choices=Currency.values())
    amount = db.IntField(required=True)
    mobile_money = db.DictField(required=True)
    status = db.StringField(required=True, default=Status.INITIATED.value, choices=Status.values())
    initiated_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = db.DateTimeField(null=True, default=None, onupdate=datetime.datetime.utcnow)

    meta = {
        'strict': False,
        'indexes': [
            'reference',
            'customer_email',
            'status',
        ]
    }

    def __repr__(self):
        return '<Transactions %r>' % self.id

    def to_dict(self, minimal=False):
        dict_obj = {}

        for column, value in self._fields.items():
            if column in ('updated_at', 'initiated_at'):
                dict_obj[column] = DateUtils.format_datetime(getattr(self, column)) if getattr(self,
                                                                                               column) is not None else None
            elif column in ('amount'):
                dict_obj[column] = int(getattr(self, column)) if getattr(self, column) is not None else None
            else:
                dict_obj[column] = getattr(self, column)

        if 'id' in dict_obj:
            dict_obj['id'] = str(dict_obj['id'])

        return dict_obj
