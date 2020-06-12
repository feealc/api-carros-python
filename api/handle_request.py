import os
import json
from datetime import datetime
from handle_json_file import HandleJsonFile


class HandleRequest:

    def __init__(self):
        # print('HandleRequest() init')
        self.__message_key = 'message'
        self.__st_key = 'status_code'
        self.json_data = HandleJsonFile.load()
        # print(self.json_data)

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
        if not car_id.isdigit():
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

    def build_reset_response(self):
        return self._get_default_fields('bd_reset')

    def build_car_created_response(self, car_id):
        ret_dict = self._get_default_fields('car_created')
        ret_dict['id'] = car_id
        return ret_dict, ret_dict['status_code']

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
                if field == 'marca' or field == 'modelo':
                    ret_dict = HandleJsonFile.load()['car_missing_field']
                    ret_dict['message'] = ret_dict['message'].replace('##', field)
                    ret_dict['error'] = True
                    return ret_dict
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
                    if field == 'marca' or field == 'modelo':
                        ret_dict = HandleJsonFile.load()['car_missing_field']
                        ret_dict['message'] = ret_dict['message'].replace('##', field)
                        ret_dict['error'] = True
                        return ret_dict
                    query += f'{field} = ?,'
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
