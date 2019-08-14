from flask import make_response
from datetime import datetime

JSON_MIME_TYPE = 'application/json'


def json_response(data='', status=201, headers=None):
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = JSON_MIME_TYPE

    return make_response(data, status, headers)


# pass birth_day in format of datetime to calculate age
def calculate_age(brth_day):
    today = datetime.utcnow()
    return today.year - brth_day.year - ((today.month, today.day) < (brth_day.month, brth_day.day))


def calculate_age_arr(brth_days):
    today = datetime.utcnow()
    new_arr = []
    for index, value in enumerate(brth_days):
        datetime_format = datetime.strptime(value, '%d.%m.%Y')
        brth_days[index] = today.year - datetime_format.year - ((today.month, today.day) < (datetime_format.month, datetime_format.day))
        # new_arr.append(today.year - elem.year - ((today.month, today.day) < (elem.month, elem.day)))
    return brth_days

