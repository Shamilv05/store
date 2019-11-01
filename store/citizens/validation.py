from datetime import datetime
from numpy import unique

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
                        'minimum': 0,
                        'maximum': 2147483647
                    },
                    'town': {
                        'type': 'string',
                        'pattern': '^[^\s]+(\s+[^\s]+)*$',
                        'maxLength': 256
                    },
                    'street': {
                        'type': 'string',
                        'pattern': '^[^\s]+(\s+[^\s]+)*$',
                        'maxLength': 256
                    },
                    'building': {
                        'type': 'string',
                        'pattern': '^[^\s]+(\s+[^\s]+)*$',
                        'maxLength': 256
                    },
                    'apartment': {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 2147483647
                    },
                    'name': {
                        'type': 'string',
                        'pattern': '^[^\s]+(\s+[^\s]+)*$',
                        'maxLength': 256
                    },
                    'birth_date': {
                        'type': 'string',
                        'pattern': '^([0-2][0-9]|(3)[0-1])(.)(((0)[0-9])|((1)[0-2]))(.)\d{4}$',
                        'maxLength': 10
                    },
                    'gender': {
                        'type': 'string',
                        'enum': ['male', 'female']
                    },
                    'relatives': {
                        'type': 'array',
                        'items': {
                            'type': 'integer',
                            'minimum': 0,
                            'maximum': 2147483647
                        },
                        "uniqueItems": True
                    }
                },
                'required': ['citizen_id', 'town', 'street', 'building', 'apartment',
                             'name', 'birth_date', 'gender', 'relatives'],
                'additionalProperties': False
            }
        }
    },
    'required': ['citizens'],
    'additionalProperties': False
}


# Schema for PATCH request
patch_req_schema = {
    'type': 'object',
    'properties': {
        'town': {
            'type': 'string',
            'pattern': '^[^\s]+(\s+[^\s]+)*$',
            'maxLength': 256
        },
        'street': {
            'type': 'string',
            'pattern': '^[^\s]+(\s+[^\s]+)*$',
            'maxLength': 256
        },
        'building': {
            'type': 'string',
            'pattern': '^[^\s]+(\s+[^\s]+)*$',
            'maxLength': 256
        },
        'apartment': {
            'type': 'integer',
            'minimum': 0,
            'maximum': 2147483647
        },
        'name': {
            'type': 'string',
            'pattern': '^[^\s]+(\s+[^\s]+)*$',
            'maxLength': 256
        },
        'birth_date': {
            'type': 'string',
            'pattern': '^([0-2][0-9]|(3)[0-1])(.)(((0)[0-9])|((1)[0-2]))(.)\d{4}$',
            'maxLength': 10
        },
        'gender': {
            'type': 'string',
            'enum': ['male', 'female']
        },
        'relatives': {
            'type': 'array',
            'items': {
                'type': 'integer',
                'minimum': 0,
                'maximum': 2147483647
            },
            "uniqueItems": True
        },
    },
    'additionalProperties': False,
    'minProperties': 1
}


def json_validation(input_json):
    relatives_dict = {}
    citizens_id = []
    for citizen in input_json["citizens"]:
        relatives_dict[citizen["citizen_id"]] = citizen["relatives"]

        if datetime.strptime(citizen["birth_date"], '%d.%m.%Y') > datetime.utcnow():
            raise ValueError('Birth date is not correct')

        citizens_id.append(citizen["citizen_id"])

    if unique(citizens_id).size != len(citizens_id):
        raise ValueError('Citizens ids are not unique')

    for citizen_id, relatives_ids in relatives_dict.items():
        for id_ in relatives_ids:
            if (citizen_id in relatives_dict[id_]) and (id_ in citizens_id):
                continue
            else:
                raise ValueError('Relatives array is not correct')
