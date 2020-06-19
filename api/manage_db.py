import os
# import sys
import traceback
import sqlite3
from datetime import datetime
from handle_json_file import HandleJsonFile


class Cars:

    @staticmethod
    def show_all_tables_and_columns():
        try:
            print('show_all_tables_and_columns()')
            cars_db = ManageDatabase()

            result = cars_db.run_query(query=f'SELECT name FROM sqlite_master WHERE type="table" ORDER BY name',
                                       select=True)

            for table in result:
                table_name = table['name']
                if table_name == 'cars':
                    print(f'Table: {table_name}')
                    result2 = cars_db.run_query(query=f'PRAGMA table_info({table_name})', select=True)
                    colunas = [i['name'] for i in result2]
                    print('Colunas:', colunas)
        except Exception as e:
            print('Erro ao mostrar todas as tabelas e campos')
            print(traceback.format_exc())
            print(e)

    @staticmethod
    def clear_cars_table(drop_create_table=False):
        if drop_create_table:
            Cars.drop_cars_table()
            Cars.create_cars_table()
        Cars.delete_all_cars_data()
        Cars.reset_auto_increment()

    @staticmethod
    def reset_db():
        try:
            Cars.clear_cars_table(drop_create_table=False)
            Cars.insert_cars_data()
            # Cars.get_all_cars_data()

        except Exception as e:
            raise e

    @staticmethod
    def drop_cars_table():
        try:
            # print('drop_cars_table()')
            cars_db = ManageDatabase()
            cars_db.run_query(query=f'DROP TABLE cars')

        except Exception as e:
            print('Erro ao dropar tabela')
            # print(traceback.format_exc())
            print(e)

    @staticmethod
    def create_cars_table():
        try:
            # print('create_cars_table()')
            query = '''
            CREATE TABLE cars (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    marca TEXT NOT NULL,
                    modelo TEXT NOT NULL,
                    cor TEXT,
                    ano_fabricacao INTEGER,
                    ano_modelo INTEGER,
                    combustivel TEXT,
                    potencia INTEGER,
                    portas INTEGER,
                    lugares INTEGER,
                    fipe_codigo TEXT,
                    data_criacao INTEGER NOT NULL,
                    data_alteracao INTEGER
            );'''
            cars_db = ManageDatabase()
            cars_db.run_query(query=query)
        except Exception as e:
            print('Erro ao criar tabela')
            # print(traceback.format_exc())
            print(e)

    @staticmethod
    def get_all_cars_data():
        try:
            # print('get_all_cars_data()')
            cars_db = ManageDatabase()
            q_result = cars_db.run_query(query=f'SELECT * FROM cars', select=True)

            for linha in q_result:
                print(linha)
        except Exception as e:
            print('Erro ao consultar todos os carros')
            # print(traceback.format_exc())
            print(e)

    @staticmethod
    def delete_all_cars_data():
        try:
            # print('delete_all_cars_data()')
            cars_db = ManageDatabase()
            cars_db.run_query(query=f'DELETE FROM cars')
        except Exception as e:
            print('Erro ao apagar todos os carros')
            # print(traceback.format_exc())
            print(e)

    @staticmethod
    def reset_auto_increment():
        try:
            # print('reset_auto_increment()')
            cars_db = ManageDatabase()
            cars_db.run_query(query=f'UPDATE SQLITE_SEQUENCE SET SEQ = 0 WHERE NAME = "cars"')
        except Exception as e:
            print('Erro ao resetar auto increment')
            # print(traceback.format_exc())
            print(e)

    @staticmethod
    def insert_cars_data():
        try:
            # print('insert_cars_data()')
            test_data = HandleJsonFile.load()['test_data']
            today_str = datetime.now().strftime('%Y%m%d')
            cars_db = ManageDatabase()

            for data in test_data:
                query_fields = ''
                query_values = ''
                values_list = []
                for key, value in data.items():
                    query_fields += key + ','
                    query_values += '?,'
                    values_list.append(value)
                query_fields += 'data_criacao'
                query_values += '?'
                values_list.append(today_str)
                values_tuple = tuple(values_list)
                query = f'INSERT INTO cars ({query_fields}) VALUES ({query_values})'
                cars_db.run_query(query=query, values=values_tuple)

        except Exception as e:
            print('Erro ao cadastrar carros')
            # print(traceback.format_exc())
            print(e)

    @staticmethod
    def get_car(car_id=None):
        if car_id is None:
            return None

        cars_db = ManageDatabase()
        query = f'SELECT * FROM cars WHERE id = {car_id}'
        result = cars_db.run_query(query=query, select=True, fetch_one=True)

        return result

    @staticmethod
    def run_query(select=False, query=None, values=None, fetch_one=False):
        cars_db = ManageDatabase()
        if select:
            return cars_db.run_query(query=query, select=select, values=values, fetch_one=fetch_one)
        else:
            cars_db.run_query(query=query, select=select, values=values, fetch_one=fetch_one)


class ManageDatabase:

    def __init__(self):
        self.db_name = os.path.join(os.getcwd(), '../', 'cars.db')
        self.conn = None
        self.cursor = None
        self.__connet()

    @staticmethod
    def __dict_factory(cur, row):
        d = {}
        for idx, col in enumerate(cur.description):
            # print(f'__dict_factory() => idx [{idx}] col [{col}]')
            d[col[0]] = row[idx]
        return d

    def __connet(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = ManageDatabase.__dict_factory
        self.cursor = self.conn.cursor()

    def __close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def run_query(self, select=False, query=None, values=None, fetch_one=False):
        self.__connet()
        q_result = None

        if query is None:
            return q_result

        if not query.endswith(';'):
            query += ';'

        if select:
            if values is not None:
                if fetch_one:
                    q_result = self.cursor.execute(query, values).fetchone()
                else:
                    q_result = self.cursor.execute(query, values).fetchall()
            else:
                if fetch_one:
                    q_result = self.cursor.execute(query).fetchone()
                else:
                    q_result = self.cursor.execute(query).fetchall()
        else:
            if values is not None:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            self.conn.commit()

        self.__close()

        if select:
            return q_result


if __name__ == "__main__":
    # db = ManageDatabase()

    # Cars.show_all_tables_and_columns()
    Cars.reset_db()
    # Cars.drop_cars_table()
    # Cars.create_cars_table()

    print(Cars.get_car(2))
