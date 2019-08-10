import json
import uuid
from flask import request, jsonify
from store import app, db
from .utils import json_response, JSON_MIME_TYPE
from .validation import validate_date_and_citizens_id, validate_schema, validate_relatives
from jsonschema import ValidationError, SchemaError


@app.route("/imports", methods=["POST"])
def imports():
    if request.content_type != JSON_MIME_TYPE:
        error = json.dumps({'error': 'Invalid Content Type'})
        return json_response(error, 400)

    data = request.json

    try:
        validate_schema(data)
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

    import_id = {
        "data": {
            "import-id": f'{uuid.uuid4()}'
        }
    }

    return json_response(json.dumps(import_id))

