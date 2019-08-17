# before running these tests, you should have created psql db, because setUp cycle was missed on purpose

import unittest
import json

from app import app, db
from models import Citizen


class TestUser(unittest.TestCase):

    def test_ok(self):
        self.test_app = app.test_client()

        input_ = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "town": "Москва",
                    "street": "Первомайска",
                    "building": "34/5к1",
                    "apartment": 221,
                    "name": "Вагабов Шамиль Абдуллахович",
                    "birth_date": "23.07.1998",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        patch_input = {
            "town": "New York"
        }

        response = self.test_app.post('/imports', data=json.dumps(input_), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.get_data(as_text=True))
        import_id_ = json_response['data']['import_id']

        response = self.test_app.get(f'/imports/{import_id_}/citizens')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data(as_text=True))['data'], input_["citizens"])

        response = self.test_app.patch(f'/imports/{import_id_}/citizens/1', data=json.dumps(patch_input),
                                       content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data(as_text=True))['data']['town'], 'New York')

        response = self.test_app.get(f'/imports/{import_id_}/citizens/birthdays')
        self.assertEqual(response.status_code, 200)





