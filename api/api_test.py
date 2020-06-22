import requests
import unittest
import json
from datetime import datetime
from handle_json_file import HandleJsonFile

# car_id = None
# RUN - python -m unittest -v api_test


class MyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.base_url = 'http://localhost:5000//api/v1/cars'
        self.headers = {'Content-Type': 'application/json'}
        self.car_id = 3

    # @classmethod
    # def setUpClass(cls) -> None:
    #     cls.car_id = 65

    @staticmethod
    def get_current_date_int():
        return int(datetime.now().strftime('%Y%m%d'))

    def fill_car_missing_fields(self, car=None, car_id=None, data_criacao=None,
                                data_alteracao=None, get_current_date=True):
        key_id = 'id'
        key_criacao = 'data_criacao'
        key_alteracao = 'data_alteracao'
        if car is not None:
            if car_id is None:
                car[key_id] = self.car_id
            else:
                car[key_id] = car_id

            if data_criacao is None:
                if get_current_date:
                    car[key_criacao] = self.get_current_date_int()
            else:
                car[key_criacao] = data_criacao

            if data_alteracao is None:
                if get_current_date:
                    car[key_alteracao] = self.get_current_date_int()
            else:
                car[key_alteracao] = data_alteracao

        return car

    def valid_response_simple(self, resp=None, code=None, expected_message=None):
        self.assertIsNotNone(resp, msg=f'Resp is none')
        resp_json = resp.json()

        self.assertIsNotNone(code, msg=f'Code is none')
        if code is not None:
            self.assertEqual(resp.status_code, code, msg=f'Código da resposta diferente do esperado')

        self.assertIsNotNone(expected_message, msg=f'Expected message is none')
        if expected_message is not None:
            self.assertEqual(len(resp_json), len(expected_message),
                             msg=f'Quantidade de campos da resposta diferente do esperado')
            for key, value in expected_message.items():
                self.assertEqual(resp_json[key], value, msg=f'Valor do campo {key} diferente do esperado')

    def valid_car_json(self, resp=None, expected_car=None):
        self.assertIsNotNone(resp)
        self.assertIsNotNone(expected_car)
        resp_json = resp.json()

        self.assertEqual(len(expected_car), len(resp_json), msg=f'Quantidade de campos diferente do esperado')
        for key, value in expected_car.items():
            self.assertTrue(key in resp_json, msg=f'{key} não existe na resposta')
            if key in resp_json:
                self.assertEqual(value, resp_json[key], msg=f'Valor do campo {key} diferente do esperado')

    def test_1_post_reset(self):
        reset_message = HandleJsonFile.load()['bd_reset']
        url = f'{self.base_url}/reset'
        resp = requests.post(url)
        self.valid_response_simple(resp=resp, code=200, expected_message=reset_message)

    def test_2_get_all(self):
        response_fields = HandleJsonFile.load()['response_fields']
        test_data = HandleJsonFile.load()['test_data']
        url = f'{self.base_url}/all'
        resp = requests.get(url)
        resp_json = resp.json()

        self.assertEqual(len(resp_json), 2)
        car_index = 0
        for resp_car in resp_json:
            car_data = test_data[car_index]
            car_data['data_criacao'] = self.get_current_date_int()
            car_data['data_alteracao'] = None
            for field in response_fields:
                self.assertTrue(field in resp_car)
                if field in resp_car:
                    self.assertEqual(resp_car[field], car_data[field])
            car_index += 1

    def test_2_get_all_order_by(self):
        field_sort = 'potencia'
        response_fields = HandleJsonFile.load()['response_fields']
        test_data = HandleJsonFile.load()['test_data']
        test_data_sorted = sorted(test_data, key=lambda k: k[field_sort])
        url = f'{self.base_url}/all'
        resp = requests.get(url, headers=self.headers, data=json.dumps({'order_by': field_sort}))
        resp_json = resp.json()

        self.assertEqual(len(resp_json), 2)
        car_index = 0
        for resp_car in resp_json:
            car_data = test_data_sorted[car_index]
            car_data['data_criacao'] = self.get_current_date_int()
            car_data['data_alteracao'] = None
            for field in response_fields:
                self.assertTrue(field in resp_car)
                if field in resp_car:
                    self.assertEqual(resp_car[field], car_data[field])
            car_index += 1

    def test_2_get_all_order_by_unknown_field(self):
        field_sort = 'campo1'
        expected_message = HandleJsonFile.load()['car_unknown_field']
        expected_message['unknown_fields'] = [field_sort]
        url = f'{self.base_url}/all'
        resp = requests.get(url, headers=self.headers, data=json.dumps({'order_by': field_sort}))

        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car(self):
        test_data_json = HandleJsonFile.load()['test_data_create']
        expected_message = HandleJsonFile.load()['car_created']
        expected_message['id'] = self.car_id
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=201, expected_message=expected_message)

    def test_3_post_create_car_body_invalid(self):
        expected_message = HandleJsonFile.load()['body_fields']
        url = f'{self.base_url}'
        resp = requests.post(url)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_body_invalid_with_header(self):
        expected_message = HandleJsonFile.load()['body_fields']
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_body_marca_missing(self):
        test_car_data = HandleJsonFile.load()['test_data_create']
        del test_car_data['marca']
        expected_message = HandleJsonFile.load()['car_missing_field']
        expected_message['message'] = expected_message['message'].replace('##', 'marca')
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_car_data))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_body_modelo_missing(self):
        test_car_data = HandleJsonFile.load()['test_data_create']
        del test_car_data['modelo']
        expected_message = HandleJsonFile.load()['car_missing_field']
        expected_message['message'] = expected_message['message'].replace('##', 'modelo')
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_car_data))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_body_unknown_fields(self):
        test_car_data = HandleJsonFile.load()['test_data_create_unknown_fields']
        unknown_fields = test_car_data['unknown_fields']
        del test_car_data['unknown_fields']
        expected_message = HandleJsonFile.load()['car_unknown_field']
        expected_message['unknown_fields'] = unknown_fields
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_car_data))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_anofabricacao_bigger(self):
        field = 'ano_fabricacao'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = 20185
        expected_message = HandleJsonFile.load()['check_request_fields']['field_len_bigger']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_anofabricacao_empty(self):
        field = 'ano_fabricacao'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_anofabricacao_not_numeric(self):
        field = 'ano_fabricacao'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = '20f16'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_anomodelo_bigger(self):
        field = 'ano_modelo'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = '02019'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_len_bigger']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_anomodelo_empty(self):
        field = 'ano_modelo'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_anomodelo_not_numeric(self):
        field = 'ano_modelo'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = 'a1991'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_combustivel_empty(self):
        field = 'combustivel'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_cor_empty(self):
        field = 'cor'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_fipecodigo_empty(self):
        field = 'fipe_codigo'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_lugares_empty(self):
        field = 'lugares'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_lugares_not_numeric(self):
        field = 'lugares'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = '2020 '
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_marca_empty(self):
        field = 'marca'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_modelo_empty(self):
        field = 'modelo'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_portas_empty(self):
        field = 'portas'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_portas_not_numeric(self):
        field = 'portas'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = '20a12b'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_potencia_empty(self):
        field = 'potencia'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_3_post_create_car_field_potencia_not_numeric(self):
        field = 'potencia'
        test_data_json = HandleJsonFile.load()['test_data_create']
        test_data_json[field] = '20a12b'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}'
        resp = requests.post(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_4_get_car_id(self):
        test_car = HandleJsonFile.load()['test_data_create']
        test_car = self.fill_car_missing_fields(car=test_car)
        test_car['data_alteracao'] = None
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.get(url)
        self.valid_car_json(resp=resp, expected_car=test_car)

    def test_4_get_car_id_invalid_id(self):
        expected_message = HandleJsonFile.load()['car_id_invalid']
        url = f'{self.base_url}/2s7ffs'
        resp = requests.get(url)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_4_get_car_id_not_found(self):
        expected_message = HandleJsonFile.load()['car_not_found']
        url = f'{self.base_url}/27031991'
        resp = requests.get(url)
        self.valid_response_simple(resp=resp, code=404, expected_message=expected_message)

    def test_5_put_update_car(self):
        test_car_update = HandleJsonFile.load()['test_data_update_put']
        test_car_update_put = test_car_update
        del test_car_update_put['potencia']
        expected_message = HandleJsonFile.load()['car_updated']
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_car_update_put))
        self.valid_response_simple(resp=resp, code=200, expected_message=expected_message)

        test_car_update = self.fill_car_missing_fields(car=test_car_update)
        test_car_update['potencia'] = None

        url = f'{self.base_url}/{self.car_id}'
        resp = requests.get(url)
        self.valid_car_json(resp=resp, expected_car=test_car_update)

    def test_5_put_update_car_body_invalid(self):
        expected_message = HandleJsonFile.load()['body_fields']
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_body_invalid_with_header(self):
        expected_message = HandleJsonFile.load()['body_fields']
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_body_marca_missing(self):
        test_car_update = HandleJsonFile.load()['test_data_update_put']
        del test_car_update['marca']
        expected_message = HandleJsonFile.load()['car_missing_field']
        expected_message['message'] = expected_message['message'].replace('##', 'marca')
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_car_update))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_body_modelo_missing(self):
        test_car_update = HandleJsonFile.load()['test_data_update_put']
        del test_car_update['modelo']
        expected_message = HandleJsonFile.load()['car_missing_field']
        expected_message['message'] = expected_message['message'].replace('##', 'modelo')
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_car_update))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_body_unknown_fields(self):
        test_car_data = HandleJsonFile.load()['test_data_update_put_unknown_fields']
        unknown_fields = test_car_data['unknown_fields']
        del test_car_data['unknown_fields']
        expected_message = HandleJsonFile.load()['car_unknown_field']
        expected_message['unknown_fields'] = unknown_fields
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_car_data))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_anofabricacao_bigger(self):
        field = 'ano_fabricacao'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = 12000
        expected_message = HandleJsonFile.load()['check_request_fields']['field_len_bigger']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_anofabricacao_empty(self):
        field = 'ano_fabricacao'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_anofabricacao_not_numeric(self):
        field = 'ano_fabricacao'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = 'kdhsa'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_anomodelo_bigger(self):
        field = 'ano_modelo'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = 325447
        expected_message = HandleJsonFile.load()['check_request_fields']['field_len_bigger']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_anomodelo_empty(self):
        field = 'ano_modelo'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_anomodelo_not_numeric(self):
        field = 'ano_modelo'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = '22wqjh'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_combustivel_empty(self):
        field = 'combustivel'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_cor_empty(self):
        field = 'cor'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_fipecodigo_empty(self):
        field = 'fipe_codigo'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_lugares_empty(self):
        field = 'lugares'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_lugares_not_numeric(self):
        field = 'lugares'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = 'rso12rma'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_marca_empty(self):
        field = 'marca'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_modelo_empty(self):
        field = 'modelo'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_portas_empty(self):
        field = 'portas'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_portas_not_numeric(self):
        field = 'portas'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = 'castle422'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_potencia_empty(self):
        field = 'potencia'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_field_potencia_not_numeric(self):
        field = 'potencia'
        test_data_json = HandleJsonFile.load()['test_data_update_put']
        test_data_json[field] = 'rso12rma'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_id_invalid_id(self):
        expected_message = HandleJsonFile.load()['car_id_invalid']
        url = f'{self.base_url}/f3'
        resp = requests.put(url)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_5_put_update_car_id_not_found(self):
        test_car_update = HandleJsonFile.load()['test_data_update_put']
        expected_message = HandleJsonFile.load()['car_not_found']
        url = f'{self.base_url}/123456'
        resp = requests.put(url, headers=self.headers, data=json.dumps(test_car_update))
        self.valid_response_simple(resp=resp, code=404, expected_message=expected_message)

    def test_6_patch_update_car(self):
        test_car_update_orig = HandleJsonFile.load()['test_data_update_put']
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.get(url)
        test_car_update_orig = self.fill_car_missing_fields(car=test_car_update_orig)
        self.valid_car_json(resp=resp, expected_car=test_car_update_orig)

        test_car_update_patch = HandleJsonFile.load()['test_data_update_patch']
        expected_message = HandleJsonFile.load()['car_updated']
        car_patch = {**test_car_update_orig, **test_car_update_patch}
        del car_patch['id']
        del car_patch['data_criacao']
        del car_patch['data_alteracao']

        resp = requests.patch(url, headers=self.headers, data=json.dumps(car_patch))
        self.valid_response_simple(resp=resp, code=200, expected_message=expected_message)

        car_patch = self.fill_car_missing_fields(car=car_patch)
        resp = requests.get(url)
        self.valid_car_json(resp=resp, expected_car=car_patch)

    def test_6_patch_update_car_body_invalid(self):
        expected_message = HandleJsonFile.load()['body_fields']
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_body_invalid_with_header(self):
        expected_message = HandleJsonFile.load()['body_fields']
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_body_unknown_fields(self):
        test_car_data = HandleJsonFile.load()['test_data_update_patch_unknown_fields']
        unknown_fields = test_car_data['unknown_fields']
        del test_car_data['unknown_fields']
        expected_message = HandleJsonFile.load()['car_unknown_field']
        expected_message['unknown_fields'] = unknown_fields
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_car_data))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_anofabricacao_bigger(self):
        field = 'ano_fabricacao'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = 9927421
        expected_message = HandleJsonFile.load()['check_request_fields']['field_len_bigger']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_anofabricacao_empty(self):
        field = 'ano_fabricacao'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_anofabricacao_not_numeric(self):
        field = 'ano_fabricacao'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = 'k ahsd2'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_anomodelo_bigger(self):
        field = 'ano_modelo'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = 523741
        expected_message = HandleJsonFile.load()['check_request_fields']['field_len_bigger']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_anomodelo_empty(self):
        field = 'ano_modelo'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_anomodelo_not_numeric(self):
        field = 'ano_modelo'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = 'kdhsa'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_combustivel_empty(self):
        field = 'combustivel'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_cor_empty(self):
        field = 'cor'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_fipecodigo_empty(self):
        field = 'fipe_codigo'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_lugares_empty(self):
        field = 'lugares'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_lugares_not_numeric(self):
        field = 'lugares'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = 'rso12rma'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_marca_empty(self):
        field = 'marca'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_modelo_empty(self):
        field = 'modelo'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_portas_empty(self):
        field = 'portas'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_portas_not_numeric(self):
        field = 'portas'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = 'valkyrie'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_potencia_empty(self):
        field = 'potencia'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = ''
        expected_message = HandleJsonFile.load()['check_request_fields']['field_empty']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_field_potencia_not_numeric(self):
        field = 'potencia'
        test_data_json = HandleJsonFile.load()['test_data_update_patch']
        test_data_json[field] = '20 20'
        expected_message = HandleJsonFile.load()['check_request_fields']['field_not_numeric']
        expected_message['message'] = expected_message['message'].replace('##', field)
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_data_json))
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_id_invalid_id(self):
        expected_message = HandleJsonFile.load()['car_id_invalid']
        url = f'{self.base_url}/brum1'
        resp = requests.patch(url)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_6_patch_update_car_id_not_found(self):
        test_car_update = HandleJsonFile.load()['test_data_update_patch']
        expected_message = HandleJsonFile.load()['car_not_found']
        url = f'{self.base_url}/852387326437575'
        resp = requests.patch(url, headers=self.headers, data=json.dumps(test_car_update))
        self.valid_response_simple(resp=resp, code=404, expected_message=expected_message)

    def test_7_delete_car(self):
        expected_message = HandleJsonFile.load()['car_deleted']
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.delete(url)
        self.valid_response_simple(resp=resp, code=200, expected_message=expected_message)

    def test_7_delete_car_id_invalid_id(self):
        expected_message = HandleJsonFile.load()['car_id_invalid']
        url = f'{self.base_url}/2castle'
        resp = requests.delete(url)
        self.valid_response_simple(resp=resp, code=400, expected_message=expected_message)

    def test_7_delete_car_id_not_found(self):
        expected_message = HandleJsonFile.load()['car_not_found']
        url = f'{self.base_url}/{self.car_id}'
        resp = requests.delete(url)
        self.valid_response_simple(resp=resp, code=404, expected_message=expected_message)


if __name__ == '__main__':
    # unittest.main(failfast=True, exit=True)
    unittest.main()
