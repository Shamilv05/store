from jsonschema import validate, ValidationError, SchemaError
from datetime import datetime
from numpy import unique

# Schema for JSON, which we get in /imports API
citizens_schema = {
    'type': 'object',
    'properties': {
        'citizens': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'citizen_id': {
                        'type': 'integer',
                        'minimum': 0
                    },
                    'town': {
                        'type': 'string',
                        'minLength': 1
                    },
                    'street': {
                        'type': 'string',
                        'minLength': 1
                    },
                    'building': {
                        'type': 'string',
                        'minLength': 1
                    },
                    'apartment': {
                        'type': 'integer',
                        'minimum': 0
                    },
                    'name': {
                        'type': 'string',
                        'minLength': 1
                    },
                    'birth_date': {
                        'type': 'string'
                    },
                    'gender': {
                        'type': 'string',
                        'enum': ['male', 'female']
                    },
                    'relatives': {
                        'type': 'array',
                        'items': {
                            'type': 'integer'
                        }
                    }
                },
                'required': ['citizen_id', 'town', 'street', 'building', 'apartment', 'name', 'birth_date', 'gender', 'relatives']
            }
        }
    },
    'required': ['citizens']
}


def validate_schema(input_json):
    validate(input_json, citizens_schema)


def validate_relatives(input_json, citizens_id):
    relatives_dict = {}
    for citizen in input_json["citizens"]:
        relatives_dict[citizen["citizen_id"]] = citizen["relatives"]
    for citizen_id, relatives_ids in relatives_dict.items():
        for id_ in relatives_ids:
            if (citizen_id in relatives_dict[id_]) and (id_ in citizens_id):
                continue
            else:
                raise ValueError('Relatives array is not correct')


def validate_date_and_citizens_id(input_json):
    citizens_id = []
    for citizen in input_json["citizens"]:
        datetime.strptime(citizen["birth_date"], '%d.%m.%Y')
        citizens_id.append(citizen["citizen_id"])
    if unique(citizens_id).size != len(citizens_id):
        raise ValueError('Citizens ids are not unique')
    validate_relatives(input_json, citizens_id)



