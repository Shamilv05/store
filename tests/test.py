# before running these tests, you should have created psql db, because setUp cycle was missed on purpose

import unittest
import json

from store.citizens.app import create_app, db, ma


class TestUser(unittest.TestCase):

    def setUp(self):
        self.test_app = create_app()
        db.init_app(self.test_app)
        ma.init_app(self.test_app)
        self.client = self.test_app.test_client()

    def tearDown(self):
        db.session.remove()

    def test_ok(self):

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

        response = self.client.post('/imports', data=json.dumps(input_), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.get_data(as_text=True))
        import_id_ = json_response['data']['import_id']

        response = self.client.get(f'/imports/{import_id_}/citizens')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data(as_text=True))['data'], input_["citizens"])

        response = self.client.patch(f'/imports/{import_id_}/citizens/1', data=json.dumps(patch_input),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data(as_text=True))['data']['town'], 'New York')

        response = self.client.get(f'/imports/{import_id_}/citizens/birthdays')
        self.assertEqual(response.status_code, 200)

    def test_post_bad(self):
        empty_town = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "",
                    "street": "Griffin",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        space_before_town = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": " Moscow",
                    "street": "Griffin",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        space_after_town = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Moscow ",
                    "street": "Griffin",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        incorrect_birth_date = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Moscow",
                    "street": "Griffin",
                    "birth_date": "29.02.2019",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        future_date_for_brth = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Moscow",
                    "street": "Griffin",
                    "birth_date": "29.05.2021",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        space_before_brth = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Moscow",
                    "street": "Griffin",
                    "birth_date": " 29.05.2017",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        space_after_brth = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Moscow",
                    "street": "Griffin",
                    "birth_date": "29.05.2017 ",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        wrong_gender = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Moscow",
                    "street": "Griffin",
                    "birth_date": "29.05.2017",
                    "gender": "woman",
                    "relatives": []
                }
            ]
        }

        space_before_gender = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Moscow",
                    "street": "Griffin",
                    "birth_date": "29.05.2018",
                    "gender": " female",
                    "relatives": []
                }
            ]
        }

        response = self.client.post('/imports', data=json.dumps(empty_town), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/imports', data=json.dumps(space_before_town), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/imports', data=json.dumps(space_after_town), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/imports', data=json.dumps(incorrect_birth_date), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/imports', data=json.dumps(future_date_for_brth), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/imports', data=json.dumps(space_before_brth), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/imports', data=json.dumps(space_after_brth), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/imports', data=json.dumps(wrong_gender), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/imports', data=json.dumps(space_before_gender), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_relatives(self):
        relatives_arr_ok = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Ross",
                    "street": "Griffin",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [2, 3]
                },
                {
                    "citizen_id": 2,
                    "apartment": 5,
                    "building": "Milk",
                    "name": "Nathan",
                    "town": "Waters",
                    "street": "Cox",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [1, 3, 4]
                },
                {
                    "citizen_id": 3,
                    "apartment": 36,
                    "building": "Milk",
                    "name": "Jim",
                    "town": "Burch",
                    "street": "Hughes",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [1, 2]
                },
                {
                    "citizen_id": 4,
                    "apartment": 19,
                    "building": "Milk",
                    "name": "Valerie",
                    "town": "Barefoot",
                    "street": "Nolan",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [2]
                }
            ]
        }

        response = self.client.post('/imports', data=json.dumps(relatives_arr_ok), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        relatives_arr_bad = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Ross",
                    "street": "Griffin",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [2, 3]
                },
                {
                    "citizen_id": 2,
                    "apartment": 5,
                    "building": "Milk",
                    "name": "Nathan",
                    "town": "Waters",
                    "street": "Cox",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": []
                },
                {
                    "citizen_id": 3,
                    "apartment": 36,
                    "building": "Milk",
                    "name": "Jim",
                    "town": "Burch",
                    "street": "Hughes",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": []
                },
                {
                    "citizen_id": 4,
                    "apartment": 19,
                    "building": "Milk",
                    "name": "Valerie",
                    "town": "Barefoot",
                    "street": "Nolan",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        response = self.client.post('/imports', data=json.dumps(relatives_arr_bad), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        relatives_with_bad_cit_id = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Regina",
                    "town": "Ross",
                    "street": "Griffin",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [2, 3]
                },
                {
                    "citizen_id": 2,
                    "apartment": 5,
                    "building": "Milk",
                    "name": "Nathan",
                    "town": "Waters",
                    "street": "Cox",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [1]
                },
                {
                    "citizen_id": 3,
                    "apartment": 36,
                    "building": "Milk",
                    "name": "Jim",
                    "town": "Burch",
                    "street": "Hughes",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [1, 10]
                },
                {
                    "citizen_id": 4,
                    "apartment": 19,
                    "building": "Milk",
                    "name": "Valerie",
                    "town": "Barefoot",
                    "street": "Nolan",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": []
                }
            ]
        }

        response = self.client.post('/imports', data=json.dumps(relatives_with_bad_cit_id),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_patch(self):
        relatives = {
            "citizens": [
                {
                    "citizen_id": 1,
                    "apartment": 37,
                    "building": "Milk",
                    "name": "Иван",
                    "town": "Ross",
                    "street": "Griffin",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [2, 3]
                },
                {
                    "citizen_id": 2,
                    "apartment": 5,
                    "building": "Milk",
                    "name": "Сергей",
                    "town": "Waters",
                    "street": "Cox",
                    "birth_date": "23.07.2016",
                    "gender": "male",
                    "relatives": [1]
                },
                {
                    "citizen_id": 3,
                    "apartment": 36,
                    "building": "Milk",
                    "name": "Анна",
                    "town": "Burch",
                    "street": "Hughes",
                    "birth_date": "23.07.2016",
                    "gender": "female",
                    "relatives": [1]
                }
            ]
        }

        patch_input = {
            "relatives": []
        }

        response = self.client.post('/imports', data=json.dumps(relatives),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.get_data(as_text=True))
        import_id_ = json_response['data']['import_id']

        response = self.client.patch(f'/imports/{import_id_}/citizens/3', data=json.dumps(patch_input),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data(as_text=True))['data']['relatives'], [])

        get_citizens = self.client.get(f'/imports/{import_id_}/citizens')
        self.assertEqual(get_citizens.status_code, 200)
        for citizen in json.loads(get_citizens.get_data(as_text=True))['data']:
            if citizen['citizen_id'] == 1:
                self.assertEqual(citizen['relatives'], [2])
            elif citizen['citizen_id'] == 2:
                self.assertEqual(citizen['relatives'], [1])

        patch_bad_bday_v1 = {
            "birth_day": " 23.07.1998"
        }

        patch_bad_bday_v2 = {
            "birth_day": "23.07.2020"
        }

        patch_bad_bday_v3 = {
            "birth_day": "33.07.1998"
        }

        response = self.client.patch(f'/imports/{import_id_}/citizens/3', data=json.dumps(patch_bad_bday_v1),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(f'/imports/{import_id_}/citizens/3', data=json.dumps(patch_bad_bday_v2),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(f'/imports/{import_id_}/citizens/3', data=json.dumps(patch_bad_bday_v3),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)

        patch_bad_name_v1 = {
            "name": " Игорь"
        }

        patch_bad_name_v2 = {
            "name": "Игорь "
        }

        patch_bad_name_v3 = {
            "name": " "
        }

        response = self.client.patch(f'/imports/{import_id_}/citizens/3', data=json.dumps(patch_bad_name_v1),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(f'/imports/{import_id_}/citizens/3', data=json.dumps(patch_bad_name_v2),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(f'/imports/{import_id_}/citizens/3', data=json.dumps(patch_bad_name_v3),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)







