import json
import uuid
from flask import request, jsonify
from app import app, db
from utils import json_response, JSON_MIME_TYPE, calculate_age, calculate_age_arr
from validation import validate_date_and_citizens_id, citizens_schema, patch_req_schema
from sqlalchemy.sql.expression import func
from jsonschema import validate, ValidationError, SchemaError
from models import Citizen, CitizenSchema
from numpy import zeros, percentile
from datetime import datetime
from sqlalchemy.orm import Session


@app.route("/imports", methods=["POST"])
def imports():
    if request.content_type != JSON_MIME_TYPE:
        error = json.dumps({'error': 'Invalid Content Type'})
        return json_response(error, 400)

    data = request.json

    try:
        validate(data, citizens_schema)
    except ValidationError as e:
        error = json.dumps({'error': 'JSON validation was not successfull'})
        print(e.message)
        return json_response(error, 400)
    except SchemaError:
        error = json.dumps({'error': 'Invalid JSON Schema'})
        return json_response(error, 400)

    try:
        validate_date_and_citizens_id(data)
    except ValueError as e:
        error = json.dumps({'error': f'{e}'})
        return json_response(error, 400)
    except KeyError:
        error = json.dumps({'error': 'Relatives array contains nonexistent citizen_id'})
        return json_response(error, 400)

    import_uuid = str(uuid.uuid4())

    # create object in database
    print(data['citizens'])
    for citizen in data["citizens"]:
        new_citizen = Citizen(citizen_id=citizen.get("citizen_id"), town=citizen.get("town"), street=citizen.get("street"),
                              building=citizen.get("building"), apartment=citizen.get("apartment"), name=citizen.get("name"),
                              birth_date=citizen.get("birth_date"), gender=citizen.get("gender"), relatives=citizen.get("relatives"),
                              import_id=import_uuid)
        db.session.add(new_citizen)
    db.session.commit()

    import_id = {
        "data": {
            "import-id": f'{import_uuid}'
        }
    }

    return json_response(json.dumps(import_id))


@app.route("/imports/<string:import_id>/citizens/<int:citizen_id>", methods=["PATCH"])
def modify(import_id, citizen_id):
    if request.content_type != JSON_MIME_TYPE:
        error = json.dumps({'error': 'Invalid Content Type'})
        return json_response(error, 400)

    data = request.json
    if not data:
        error = json.dumps({'error': 'Input JSON file is empty'})
        return json_response(error, 400)

    try:
        validate(data, patch_req_schema)
    except ValidationError:
        error = json.dumps({'error': 'JSON validation was not successfull'})
        return json_response(error, 400)
    except SchemaError:
        error = json.dumps({'error': 'Invalid JSON Schema'})
        return json_response(error, 400)

    citizens = Citizen.query.filter_by(import_id=import_id).all()
    updated_citizen = Citizen.query.filter_by(import_id=import_id, citizen_id=citizen_id).first()
    citizens_ids = []

    for elem in citizens:
            citizens_ids.append(elem.citizen_id)
    if not all(elem in citizens_ids for elem in data['relatives']):
        error = json.dumps({'error': 'Citizens for certain import_id do not have citizen_id from input JSON'})
        return json_response(error, 400)

    former_relatives = updated_citizen.relatives
    for key, value in data.items():
        setattr(updated_citizen, key, value)
    db.session.commit()
    new_relatives = updated_citizen.relatives

    missing_relatives = [item for item in former_relatives if item not in new_relatives]
    added_relatives = [item for item in new_relatives if item not in former_relatives]

    for item in missing_relatives:
        citizen = Citizen.query.filter_by(import_id=import_id, citizen_id=item).first()
        arr = list(citizen.relatives)
        if citizen_id in arr:
            arr.remove(citizen_id)
            setattr(citizen, 'relatives', arr)
            db.session.commit()

    for item in added_relatives:
        citizen = Citizen.query.filter_by(import_id=import_id, citizen_id=item).first()
        arr = list(citizen.relatives)
        if citizen_id not in arr:
            arr.append(citizen_id)
            setattr(citizen, 'relatives', arr)
            db.session.commit()

    citizen_schema = CitizenSchema()
    output = citizen_schema.dump(updated_citizen).data
    return json_response(jsonify({'data': output}), 200)


@app.route("/imports/<string:import_id>/citizens", methods=["GET"])
def citizens(import_id):
    certain_citizens = Citizen.query.filter_by(import_id=import_id).all()
    citizen_schema = CitizenSchema(many=True)
    output = citizen_schema.dump(certain_citizens).data
    return jsonify({'data': output})


@app.route("/imports/<string:import_id>/citizens/birthdays", methods=["GET"])
def birthdays(import_id):
    citizens = Citizen.query.filter_by(import_id=import_id).all()
    birthdays_dict = {}

    # for citizen in citizens:
    #     citizen_id = citizen.citizen_id
    #     # amount of presents certain citizen should buy(index of array = num of month)
    #     birthdays_dict[citizen_id] = zeros(12)
    #     for relative_id in citizen.relatives:
    #         relative_info = (list(filter(lambda person: person.citizen_id == relative_id, citizens)))[0]
    #         print(relative_info)
    #         relative_bthday = datetime.strptime(relative_info.birth_date, "%d.%m.%Y").month
    #         birthdays_dict[citizen_id][relative_bthday - 1] += 1

    for citizen in citizens:
        citizen_id = citizen.citizen_id
        # amount of presents certain citizen should buy(index of array = num of month)
        birthdays_dict[citizen_id] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
        for relative_id in citizen.relatives:
            relative_info = (list(filter(lambda person: person.citizen_id == relative_id, citizens)))[0]
            relative_bthday = datetime.strptime(relative_info.birth_date, "%d.%m.%Y").month
            birthdays_dict[citizen_id][(relative_bthday - 1)] += 1

    response = {
        'data': {
            '1': [],
            '2': [],
            '3': [],
            '4': [],
            '5': [],
            '6': [],
            '7': [],
            '8': [],
            '9': [],
            '10': [],
            '11': [],
            '12': []
        }
    }

    # for cit_id, presents_arr in birthdays_dict.items():
    #     for index, val in enumerate(presents_arr):
    #         if val != 0:
    #             response['data'][str(index + 1)].append({'citizen_id': f'{cit_id}', 'presents': val})
    #         continue

    for cit_id, presents_arr in birthdays_dict.items():
        for key, val in presents_arr.items():
            if val != 0:
                response['data'][str(key + 1)].append({'citizen_id': f'{cit_id}', 'presents': val})
            continue

    return json_response(json.dumps(response), 200)


@app.route("/imports/<string:import_id>/towns/stat/percentile/age", methods=["GET"])
def count_percentile(import_id):
    # Extract data from db in a structure like : [('City_1', ['brthday_1 for city', '..', ..], ('City_2', [....]), etc.]
    brth_days_grouped_by_town = db.session.query(Citizen.town, func.array_agg(Citizen.birth_date))   \
             .filter_by(import_id=import_id)   \
             .group_by(Citizen.town).all()
    test_dict = dict(brth_days_grouped_by_town)
    # result_dict = {}
    response = {
        'data': []
    }

    # for local_info in brth_days_grouped_by_town:
    #     ages = []
    #     for brth_day in local_info[1]:
    #         ages.append(calculate_age(datetime.strptime(brth_day, '%d.%m.%Y')))
    #     result_dict[local_info[0]] = ages
    # for key, value in result_dict.items():
    #     p50 = round(percentile(value, 50, interpolation='linear'), 2)
    #     p75 = round(percentile(value, 75, interpolation='linear'), 2)
    #     p99 = round(percentile(value, 99, interpolation='linear'), 2)
    #     response['data'].append({'town': f'{key}', 'p50': p50, 'p75': p75, 'p99': p99})

    # for town_info in brth_days_grouped_by_town:
    #     ages = []
    #     for brth_day in town_info[1]:
    #         ages.append(calculate_age(datetime.strptime(brth_day, '%d.%m.%Y')))
    #     p50 = round(percentile(ages, 50, interpolation='linear'), 2)
    #     p75 = round(percentile(ages, 75, interpolation='linear'), 2)
    #     p99 = round(percentile(ages, 99, interpolation='linear'), 2)
    #     response['data'].append({'town': f'{town_info[0]}', 'p50': p50, 'p75': p75, 'p99': p99})

    for key, value in test_dict.items():
        arr = calculate_age_arr(value)
        p50 = round(percentile(arr, 50, interpolation='linear'), 2)
        p75 = round(percentile(arr, 75, interpolation='linear'), 2)
        p99 = round(percentile(arr, 99, interpolation='linear'), 2)
        response['data'].append({'town': f'{key}', 'p50': p50, 'p75': p75, 'p99': p99})

    return json_response(json.dumps(response), 200)
































