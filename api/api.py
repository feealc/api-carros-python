import os
# import traceback
# import logging
from flask import Flask, request, jsonify
from manage_db import Cars
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
        Cars.reset_db()

        return HandleRequest.build_reset_response()
    except Exception as e:
        print('Erro no reset do banco de dados')
        # print(traceback.format_exc())
        print(e)
        return send_message()


@app.route('/api/v1/cars/all', methods=['GET'])
def api_all():
    try:
        body = request.get_json(silent=True)
        order_by_field = None
        if body is not None:
            if 'order_by' in body:
                body_fake = {body['order_by']: None}
                result = HandleRequest.valid_request_fields(body_fake, accept_date_fields=True)
                if result is not None:
                    return send_message(result)
                order_by_field = body['order_by']

        if order_by_field is None:
            order_by_field = 'id'

        all_cars = Cars.run_query(query=f'SELECT * FROM cars ORDER BY {order_by_field}', select=True)

        return jsonify(all_cars)
    except Exception as e:
        print('Erro ao consultar todos os carros')
        # print(traceback.format_exc())
        print(e)

        return send_message()


@app.route('/api/v1/cars/<car_id>', methods=['GET'])
def api_id_get(car_id):
    try:
        result = HandleRequest.valid_car_id(car_id)
        if result is not None:
            return send_message(result)

        car = Cars.get_car(car_id=car_id)

        result = HandleRequest.valid_car_found(car)
        if result is not None:
            return send_message(result)

        return jsonify(car)
    except Exception as e:
        print('Erro ao consultar carro')
        # print(traceback.format_exc())
        print(e)
        return send_message()


@app.route('/api/v1/cars', methods=['POST'])
def api_create():
    try:
        body = request.get_json(silent=True)
        result = HandleRequest.valid_body_fields(body)
        if result is not None:
            return send_message(result)

        result = HandleRequest.valid_request_fields(body)
        if result is not None:
            return send_message(result)

        result = HandleRequest.parse_request_insert(body)
        if 'error' in result:
            return send_message(result)
        query = result['query']
        values = result['values']

        Cars.run_query(query=query, values=values)

        line = Cars.run_query(query='SELECT max(id) FROM cars', select=True)
        id_new = line[0]['max(id)']

        return HandleRequest.build_car_created_response(id_new)
    except Exception as e:
        print('Erro ao cadastrar carro')
        # print(traceback.format_exc())
        print(e)
        return send_message()


@app.route('/api/v1/cars/<car_id>', methods=['PUT', 'PATCH'])
def api_id_put_patch(car_id):
    try:
        result = HandleRequest.valid_car_id(car_id)
        if result is not None:
            return send_message(result)

        body = request.get_json(silent=True)
        result = HandleRequest.valid_body_fields(body)
        if result is not None:
            return send_message(result)

        result = HandleRequest.valid_request_fields(body)
        if result is not None:
            return send_message(result)

        flag_put = request.method == 'PUT'
        result = HandleRequest.parse_request_update(body, car_id, put_method=flag_put)
        if 'error' in result:
            return send_message(result)
        query = result['query']
        values = result['values']

        car = Cars.get_car(car_id=car_id)
        result = HandleRequest.valid_car_found(car)
        if result is not None:
            return send_message(result)

        Cars.run_query(query=query, values=values)

        return HandleRequest.build_car_updated_response()
    except Exception as e:
        print('Erro ao atualizar carro')
        # print(traceback.format_exc())
        print(e)
        return send_message()


@app.route('/api/v1/cars/<car_id>', methods=['DELETE'])
def api_id_delete(car_id):
    try:
        result = HandleRequest.valid_car_id(car_id)
        if result is not None:
            return send_message(result)

        car = Cars.get_car(car_id=car_id)
        result = HandleRequest.valid_car_found(car)
        if result is not None:
            return send_message(result)

        Cars.run_query(query=f'DELETE FROM cars WHERE id = {car_id}')

        return HandleRequest.build_car_deleted_response()
    except Exception as e:
        print('Erro ao apagar carro')
        # print(traceback.format_exc())
        print(e)
        return send_message()


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(asctime)s %(levelname)8s > %(message)s')
    app.run(debug=True)
    # app.run()
