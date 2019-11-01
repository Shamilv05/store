from flask import make_response
from datetime import datetime

JSON_MIME_TYPE = 'application/json'


def json_response(data='', status=201, headers=None):
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = JSON_MIME_TYPE

    return make_response(data, status, headers)


def calculate_age_arr(brth_days):
    today = datetime.utcnow()
    for index, value in enumerate(brth_days):
        datetime_format = datetime.strptime(value, '%d.%m.%Y')
        brth_days[index] = today.year - datetime_format.year - ((today.month, today.day) < (datetime_format.month, datetime_format.day))
    return brth_days
