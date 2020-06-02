import os
import json
from datetime import datetime


class HandleRequest():

    def __init__(self):
        # print('HandleRequest() init')
        self.__message_key = 'message'
        self.__st_key = 'status_code'
        self.__load_json_file()
        # print(self.json_data)

    def __load_json_file(self):
        file_name = os.path.join(os.getcwd(), '../', 'project.json')
        with open(file_name, 'r', encoding='utf-8') as f:
            self.json_data = json.load(f)

    def _get_default_fields(self, key):
        return_dict = {}
        if key in self.json_data:
            fields = self.json_data[key]
            if self.__message_key in fields:
                return_dict[self.__message_key] = fields[self.__message_key]
            if self.__st_key in fields:
                return_dict[self.__st_key] = fields[self.__st_key]

        return return_dict

    def valid_car_id(self, car_id):
        json_key = 'car_id_invalid'
        ret_dict = None
        try:
            int(car_id)
        except Exception:
            ret_dict = self._get_default_fields(json_key)

        return ret_dict

    def valid_car_found(self, car):
        json_key = 'car_not_found'
        ret_dict = None

        if car is None:
            ret_dict = self._get_default_fields(json_key)

        return ret_dict

    def valid_body_fields(self, body):
        json_key = 'body_fields'
        ret_dict = None

        if body is None:
            ret_dict = self._get_default_fields(json_key)

        return ret_dict

    def build_car_created_response(self, car_id):
        ret_dict = self._get_default_fields('car_created')
        ret_dict['id'] = car_id
        return ret_dict

    def build_car_updated_response(self):
        return self._get_default_fields('car_updated')

    def build_car_deleted_response(self):
        return self._get_default_fields('car_deleted')

    def parse_request_insert(self, body):
        fields = self.json_data['request_fields']
        ret_dict = None

        query_main = 'INSERT INTO cars ('
        query_values = 'VALUES ('
        values_list = []

        for field in fields:
            query_main += field + ','
            query_values += '?,'
            if field in body:
                values_list.append(body[field])
            else:
                values_list.append(None)

        query_main += 'data_criacao)'
        query_values += '?)'
        query = query_main + ' ' + query_values
        values_list.append(datetime.now().strftime('%Y%m%d'))
        values_tuple = tuple(values_list)

        # print(query)
        # print(values_tuple)
        ret_dict = {
            'query': query,
            'values': values_tuple
        }
        return ret_dict

    def parse_request_update(self, body, car_id, put_method=False):
        fields = self.json_data['request_fields']
        ret_dict = None

        query = 'UPDATE cars SET '
        values_list = []

        for field in fields:
            if field in body:
                query += f'{field} = ?,'
                values_list.append(body[field])
            else:
                if put_method:
                    query += f'{field} = ?,'
                    # TODO: se for o campo MARCA ou MODELO, responder campo ausente
                    values_list.append(None)

        query += 'data_alteracao = ? WHERE id = ?;'
        values_list.append(datetime.now().strftime('%Y%m%d'))
        values_list.append(car_id)
        values_tuple = tuple(values_list)

        # print(query)
        # print(values_tuple)
        ret_dict = {
            'query': query,
            'values': values_tuple
        }
        return ret_dict
