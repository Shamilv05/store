import json
from flask import request, jsonify, Blueprint
from store.citizens.app import db
from store.citizens.utils import json_response, JSON_MIME_TYPE, calculate_age_arr
from store.citizens.validation import citizens_schema, patch_req_schema, json_validation
from sqlalchemy.sql.expression import func
from store.models import Citizen, CitizenSchema
from numpy import zeros, percentile
from datetime import datetime
from sqlalchemy import exc
from fastjsonschema import validate
from fastjsonschema.exceptions import JsonSchemaException

citizens = Blueprint('app', __name__)


@citizens.route("/imports", methods=["POST"])
def imports():
    if request.content_type != JSON_MIME_TYPE:
        error = json.dumps({'error': 'Invalid Content Type'})
        return json_response(error, 400)

    data = request.json

    try:
        validate(citizens_schema, data)
    except JsonSchemaException as e:
        error = json.dumps({'error': f'{e}'})
        return json_response(error, 400)

    try:
        json_validation(data)
    except ValueError as e:
        error = json.dumps({'error': f'{e}'})
        return json_response(error, 400)
    except KeyError:
        error = json.dumps({'error': 'Relatives array contains nonexistent citizen_id'})
        return json_response(error, 400)

    max_import_id_from_table = db.session.query(func.max(Citizen.import_id)).first()[0]
    if max_import_id_from_table:
        import_id = max_import_id_from_table + 1
    else:
        import_id = 1

    for item in data['citizens']:
        item.update({"import_id": import_id})

    try:
        db.session.bulk_insert_mappings(Citizen, data['citizens'])
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        error = json.dumps({'error': 'Cannot insert citizens into db'})
        return json_response(error, 400)

    import_id = {
        "data": {
            "import_id": import_id
        }
    }

    return json_response(json.dumps(import_id))


@citizens.route("/imports/<int:import_id>/citizens/<int:citizen_id>", methods=["PATCH"])
def modify(import_id, citizen_id):
    if request.content_type != JSON_MIME_TYPE:
        error = json.dumps({'error': 'Invalid Content Type'})
        return json_response(error, 400)

    data = request.json

    try:
        validate(patch_req_schema, data)
    except JsonSchemaException as e:
        error = json.dumps({'error': f'{e}'})
        return json_response(error, 400)

    citizen_to_update = Citizen.query.filter_by(import_id=import_id, citizen_id=citizen_id).first()

    if not citizen_to_update:
        error = json.dumps({'error': 'Incorrect import_id or citizen_id'})
        return json_response(error, 404)

    if 'birth_date' in data:
        try:
            if datetime.strptime(data["birth_date"], '%d.%m.%Y') > datetime.utcnow():
                error = json.dumps({'error': 'Birth date is not correct'})
                return json_response(error, 400)
        except ValueError as e:
            error = json.dumps({'error': f'{e}'})
            return json_response(error, 400)

    if 'relatives' in data:
        for c_id in data['relatives']:
            exists = db.session.query(Citizen).filter_by(import_id=import_id, citizen_id=c_id).scalar() is not None
            if not exists:
                error = json.dumps({'error': 'Citizen id from relatives array does not exists in db'})
                return json_response(error, 400)

        old_relatives = citizen_to_update.relatives
        new_relatives = data['relatives']

        no_longer_relatives = [item for item in old_relatives if item not in new_relatives]
        fresh_relatives = [item for item in new_relatives if item not in old_relatives]

        for item in no_longer_relatives:
            citizen = Citizen.query.filter_by(import_id=import_id, citizen_id=item).first()
            arr = list(citizen.relatives)
            if citizen_id in arr:
                arr.remove(citizen_id)
                setattr(citizen, 'relatives', arr)
                db.session.commit()

        for item in fresh_relatives:
            citizen = Citizen.query.filter_by(import_id=import_id, citizen_id=item).first()
            arr = list(citizen.relatives)
            if citizen_id not in arr:
                arr.append(citizen_id)
                setattr(citizen, 'relatives', arr)
                db.session.commit()

        for key, value in data.items():
            setattr(citizen_to_update, key, value)
        db.session.commit()

        citizen_schema = CitizenSchema()
        output = citizen_schema.dump(citizen_to_update).data
        return json_response(jsonify({'data': output}), 200)

    for key, value in data.items():
        setattr(citizen_to_update, key, value)
    db.session.commit()

    citizen_schema = CitizenSchema()
    output = citizen_schema.dump(citizen_to_update).data
    return json_response(jsonify({'data': output}), 200)


@citizens.route("/imports/<int:import_id>/citizens", methods=["GET"])
def citizens_info(import_id):
    certain_citizens = Citizen.query.filter_by(import_id=import_id).all()
    db.session.close()

    if not certain_citizens:
        error = json.dumps({'error': 'This import_id does not exist yet'})
        return json_response(error, 404)

    citizen_schema = CitizenSchema(many=True)
    output = citizen_schema.dump(certain_citizens).data
    return jsonify({'data': output})


@citizens.route("/imports/<string:import_id>/citizens/birthdays", methods=["GET"])
def birthdays(import_id):
    certain_citizens = Citizen.query.filter_by(import_id=import_id).all()

    if not certain_citizens:
        error = json.dumps({'error': 'This import_id does not exist yet'})
        return json_response(error, 404)

    db.session.close()
    birthdays_dict = {}

    for citizen in certain_citizens:
        citizen_id = citizen.citizen_id
        # amount of presents certain citizen should buy(index of array = num of month)
        birthdays_dict[citizen_id] = zeros(12)
        for relative_id in citizen.relatives:
            relative_info = (list(filter(lambda person: person.citizen_id == relative_id, certain_citizens)))[0]
            relative_brthday = datetime.strptime(relative_info.birth_date, "%d.%m.%Y").month
            birthdays_dict[citizen_id][relative_brthday - 1] += 1

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

    for cit_id, presents_arr in birthdays_dict.items():
        for index, val in enumerate(presents_arr):
            if val != 0:
                response['data'][str(index + 1)].append({'citizen_id': f'{cit_id}', 'presents': val})

    return json_response(json.dumps(response), 200)


@citizens.route("/imports/<string:import_id>/towns/stat/percentile/age", methods=["GET"])
def count_percentile(import_id):
    birth_days_grouped_by_town = db.session.query(Citizen.town, func.array_agg(Citizen.birth_date))   \
             .filter_by(import_id=import_id)   \
             .group_by(Citizen.town).all()
    db.session.close()

    if not birth_days_grouped_by_town:
        error = json.dumps({'error': 'This import_id does not exist yet'})
        return json_response(error, 404)

    test_dict = dict(birth_days_grouped_by_town)
    response = {
        'data': []
    }

    for key, value in test_dict.items():
        arr = calculate_age_arr(value)
        p50 = round(percentile(arr, 50, interpolation='linear'), 2)
        p75 = round(percentile(arr, 75, interpolation='linear'), 2)
        p99 = round(percentile(arr, 99, interpolation='linear'), 2)
        response['data'].append({'town': f'{key}', 'p50': p50, 'p75': p75, 'p99': p99})

    return json_response(json.dumps(response), 200)
































