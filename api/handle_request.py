from datetime import datetime
from handle_json_file import HandleJsonFile


class HandleRequest:

    @staticmethod
    def valid_car_id(car_id):
        ret_dict = None
        if not car_id.isdigit():
            ret_dict = HandleJsonFile.load()['car_id_invalid']

        return ret_dict

    @staticmethod
    def valid_car_found(car):
        ret_dict = None

        if car is None:
            ret_dict = HandleJsonFile.load()['car_not_found']

        return ret_dict

    @staticmethod
    def valid_body_fields(body):
        ret_dict = None

        if body is None:
            ret_dict = HandleJsonFile.load()['body_fields']

        return ret_dict

    @staticmethod
    def valid_request_fields(body, accept_date_fields=False):
        request_fields = HandleJsonFile.load()['request_fields']
        if accept_date_fields:
            request_fields = HandleJsonFile.load()['response_fields']
        unknown_fields = []
        ret_dict = None

        for field in body:
            if field not in request_fields:
                unknown_fields.append(field)

        if len(unknown_fields) > 0:
            ret_dict = HandleJsonFile.load()['car_unknown_field']
            ret_dict['unknown_fields'] = unknown_fields

        return ret_dict

    @staticmethod
    def build_reset_response():
        return HandleJsonFile.load()['bd_reset']

    @staticmethod
    def build_car_created_response(car_id):
        ret_dict = HandleJsonFile.load()['car_created']
        ret_dict['id'] = car_id
        return ret_dict, ret_dict['status_code']

    @staticmethod
    def build_car_updated_response():
        return HandleJsonFile.load()['car_updated']

    @staticmethod
    def build_car_deleted_response():
        return HandleJsonFile.load()['car_deleted']

    @staticmethod
    def build_dummy_response():
        return HandleJsonFile.load()['dummy_responde']

    @staticmethod
    def parse_request_insert(body):
        fields = HandleJsonFile.load()['request_fields']

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

        ret_dict = {
            'query': query,
            'values': values_tuple
        }
        return ret_dict

    @staticmethod
    def parse_request_update(body, car_id, put_method=False):
        fields = HandleJsonFile.load()['request_fields']

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

        ret_dict = {
            'query': query,
            'values': values_tuple
        }
        return ret_dict
