import os
import traceback
import logging
from flask import Flask, request, jsonify
from manage_db import ManageDbCars
from handle_request import HandleRequest


FILE_BD = os.path.join(os.getcwd(), '../', 'cars.db')

app = Flask(__name__)


def send_message(fields=None, **kwargs):
    key_message = 'message'
    key_status_code = 'status_code'

    if fields is not None:
        if key_message not in fields:
            fields[key_message] = 'Internal error'
        if key_status_code not in fields:
            fields[key_status_code] = 500
        if 'error' in fields:
            del fields['error']
    else:
        fields = {
            key_message: 'Internal error',
            key_status_code: 500
        }

    for key, value in kwargs.items():
        fields[key] = value

    return jsonify(fields), fields['status_code']


@app.route('/api/v1/cars/reset', methods=['POST'])
def api_reset():
    try:
        req = HandleRequest()
        cars = ManageDbCars()
        cars.reset_db(connect_db=True)

        return req.build_reset_response()
    except Exception as e:
        print('Erro no reset banco de dados')
        print(traceback.format_exc())
        print(e)
        return send_message()


@app.route('/api/v1/cars/all', methods=['GET'])
def api_all():
    try:
        c = ManageDbCars()
        all_cars = c.run_select(connect_db=True,
                                query='SELECT * FROM cars ORDER BY id')

        return jsonify(all_cars)
    except Exception:
        print('Erro ao consultar todos os carros')
        print(traceback.format_exc())
        return send_message()


@app.route('/api/v1/cars/<car_id>', methods=['GET'])
def api_id_get(car_id):
    try:
        req = HandleRequest()
        result = req.valid_car_id(car_id)
        if result is not None:
            return send_message(result)

        c = ManageDbCars()
        car = c.get_car(connect_db=True, car_id=car_id)

        result = req.valid_car_found(car)
        if result is not None:
            return send_message(result)

        return jsonify(car)
    except Exception as e:
        print('Erro ao consultar carro')
        print(traceback.format_exc())
        print(e)
        return send_message()


@app.route('/api/v1/cars', methods=['POST'])
def api_create():
    try:
        req = HandleRequest()
        body = request.get_json(silent=True)
        result = req.valid_body_fields(body)
        if result is not None:
            return send_message(result)

        result = req.parse_request_insert(body)
        if 'error' in result:
            return send_message(result)
        query = result['query']
        values = result['values']

        c = ManageDbCars()
        c.run_insert_update_delete(connect_db=True, query=query, values=values)

        line = c.run_select(connect_db=True, query='SELECT max(id) FROM cars')
        id_new = line[0]['max(id)']

        return req.build_car_created_response(id_new)
    except Exception as e:
        print('Erro ao cadastrar carro')
        print(traceback.format_exc())
        print(e)
        return send_message()


@app.route('/api/v1/cars/<car_id>', methods=['PUT', 'PATCH'])
def api_id_put_patch(car_id):
    try:
        req = HandleRequest()
        result = req.valid_car_id(car_id)
        if result is not None:
            return send_message(result)

        body = request.get_json(silent=True)
        result = req.valid_body_fields(body)
        if result is not None:
            return send_message(result)

        flag_put = request.method == 'PUT'
        result = req.parse_request_update(body, car_id, put_method=flag_put)
        if 'error' in result:
            return send_message(result)
        query = result['query']
        values = result['values']

        c = ManageDbCars()

        car = c.get_car(connect_db=True, car_id=car_id)
        result = req.valid_car_found(car)
        if result is not None:
            return send_message(result)

        result = c.run_insert_update_delete(connect_db=True,
                                            query=query, values=values)

        if result != 1:
            raise Exception()

        return req.build_car_updated_response()
    except Exception as e:
        print('Erro ao atualizar carro')
        print(traceback.format_exc())
        print(e)
        return send_message()


@app.route('/api/v1/cars/<car_id>', methods=['DELETE'])
def api_id_delete(car_id):
    try:
        req = HandleRequest()
        result = req.valid_car_id(car_id)
        if result is not None:
            return send_message(result)

        c = ManageDbCars()
        car = c.get_car(connect_db=True, car_id=car_id)
        result = req.valid_car_found(car)
        if result is not None:
            return send_message(result)

        query = f'DELETE FROM cars WHERE id = ?'
        result = c.run_insert_update_delete(connect_db=True,
                                            query=query, values=(car_id,))
        if result != 1:
            raise Exception()

        return req.build_car_deleted_response()
    except Exception as e:
        print('Erro ao apagar carro')
        print(traceback.format_exc())
        print(e)
        return send_message()


# print(f'FILE_BD [{FILE_BD}]')
if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(asctime)s %(levelname)8s > %(message)s')
    app.run(debug=True)
    # app.run()
