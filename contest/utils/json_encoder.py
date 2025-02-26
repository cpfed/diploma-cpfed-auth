import json
import datetime

from phonenumbers import PhoneNumber

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PhoneNumber):
            return str(o)
        if isinstance(o, datetime.date):
            return str(o)
        return super().default(o)

