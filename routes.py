import json
import uuid
from flask import request, jsonify
from app import app, db
from utils import json_response, JSON_MIME_TYPE
from validation import validate_date_and_citizens_id, citizens_schema, patch_req_schema
from jsonschema import validate, ValidationError, SchemaError
from models import Citizen, CitizenSchema


@app.route("/imports", methods=["POST"])
def imports():
    if request.content_type != JSON_MIME_TYPE:
        error = json.dumps({'error': 'Invalid Content Type'})
        return json_response(error, 400)

    data = request.json

    try:
        validate(data, citizens_schema)
    except ValidationError:
        error = json.dumps({'error': 'JSON validation was not successfull'})
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
    for citizen in data["citizens"]:
        new_citizen = Citizen(citizen_id=citizen["citizen_id"], town=citizen["town"], street=citizen["street"],
                              building=citizen["building"], apartment=citizen["apartment"], name=citizen["name"],
                              birth_date=citizen["birth_date"], gender=citizen["gender"], relatives=citizen["relatives"],
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
    citizen = Citizen.query.filter_by(import_id=import_id, citizen_id=citizen_id).first()
    citizens_ids = []

    for elem in citizens:
            citizens_ids.append(elem.citizen_id)
    if not all(elem in citizens_ids for elem in data['relatives']):
        error = json.dumps({'error': 'Citizens for certain import_id do not have citizen_id from input JSON'})
        return json_response(error, 400)

    former_relatives = citizen.relatives
    for key, value in data.items():
        setattr(citizen, key, value)
    db.session.commit()
    new_relatives = citizen.relatives

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
    output = citizen_schema.dump(citizen).data
    return json_response(jsonify({'data': output}), 200)


@app.route("/imports/<string:import_id>/citizens", methods=["GET"])
def citizens(import_id):
    certain_citizens = Citizen.query.filter_by(import_id=import_id).all()
    citizen_schema = CitizenSchema(many=True)
    output = citizen_schema.dump(certain_citizens).data
    return jsonify({'data': output})

































