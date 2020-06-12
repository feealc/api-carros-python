import os
# import sys
import traceback
import sqlite3
from datetime import datetime
from handle_json_file import HandleJsonFile


class ManageDbCars:

    def __init__(self):
        self.db_name = os.path.join(os.getcwd(), '../', 'cars.db')
        self.table_name = 'cars'

        self.conn = None
        self.cursor = None

    def __str__(self):
        return f'ManageDbCars()'

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = self.__dict_factory
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def __dict_factory(self, cur, row):
        d = {}
        for idx, col in enumerate(cur.description):
            # print(f'__dict_factory() => idx [{idx}] col [{col}]')
            d[col[0]] = row[idx]
        return d

    def show_all_tables_and_columns(self):
        try:
            print('show_all_tables_and_columns()')

            self.cursor.execute('''
            SELECT name FROM sqlite_master WHERE type='table' ORDER BY name
            ''')

            all_tables = self.cursor.fetchall()

            for table in all_tables:
                print(f'Table: {table[0]}')
                # print(type(table))
                self.cursor.execute('PRAGMA table_info({})'.format(table[0]))
                colunas = [tupla[1] for tupla in self.cursor.fetchall()]
                print('Colunas:', colunas)
        except Exception:
            print('Erro')
            print(traceback.format_exc())

    def clear_cars_table(self, drop_create_table=False):
        if drop_create_table:
            self.drop_cars_table()
            self.create_cars_table()
        self.delete_all_cars_data()
        self.reset_auto_increment()

    def drop_cars_table(self):
        try:
            # print('drop_cars_table()')
            self.cursor.execute('''
            DROP TABLE cars;
            ''')
            self.conn.commit()
        except Exception as e:
            print('Erro ao dropar tabela')
            print(e)
            print(traceback.format_exc())

    def create_cars_table(self):
        try:
            # print('create_cars_table()')
            self.cursor.execute('''
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
            );
            ''')
            self.conn.commit()
        except Exception as e:
            print('Erro ao criar tabela')
            print(e)
            print(traceback.format_exc())

    def get_all_cars_data(self):
        try:
            print('get_all_cars_data()')
            self.cursor.execute('''
            SELECT * FROM cars;
            ''')

            for linha in self.cursor.fetchall():
                print(linha)
        except Exception as e:
            print('Erro')
            print(e)
            print(traceback.format_exc())

    def delete_all_cars_data(self):
        try:
            # print('delete_all_cars_data()')
            self.cursor.execute('''
            DELETE FROM cars;
            ''')
            self.conn.commit()
        except Exception as e:
            print('Erro ao apagar todos os carros')
            print(e)
            print(traceback.format_exc())

    def reset_auto_increment(self):
        try:
            # print('reset_auto_increment()')
            self.cursor.execute('''
            UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='cars';
            ''')
            self.conn.commit()
        except Exception as e:
            print('Erro ao resetar auto increment')
            print(e)
            print(traceback.format_exc())

    def insert_cars_data(self):
        try:
            test_data = HandleJsonFile.load()['test_data']
            today_str = datetime.now().strftime('%Y%m%d')

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
                self.cursor.execute(query, values_tuple)
                self.conn.commit()

        except Exception as e:
            print('Erro ao cadastrar carros')
            print(e)
            print(traceback.format_exc())

    def reset_db(self, connect_db=False):
        try:
            if connect_db:
                self.connect()

            if self.conn:
                self.clear_cars_table(drop_create_table=False)
                self.reset_auto_increment()
                self.insert_cars_data()
                # self.get_all_cars_data()

            if connect_db:
                self.close()
        except Exception as e:
            raise e

    def get_car(self, connect_db=False, car_id=None):
        # print('ManageDbCars => run_select()')
        if connect_db:
            self.connect()

        if car_id is None:
            return None

        if self.conn:
            query = f'SELECT * FROM cars WHERE id = {car_id};'
            # print(f'ManageDbCars => get_car() - query [{query}]')
            result = self.cursor.execute(query).fetchone()
            # print(result)

        if connect_db:
            self.close()

        return result

    def run_select(self, connect_db=False, query=None, values=None):
        # print('ManageDbCars => run_select()')
        if connect_db:
            self.connect()

        result = None

        if query is None:
            return result

        if self.conn:
            if not query.endswith(';'):
                query += ';'
            # print(f'ManageDbCars => run_select() - query [{query}]')
            if values is not None:
                result = self.cursor.execute(query, values).fetchall()
            else:
                result = self.cursor.execute(query).fetchall()

        if connect_db:
            self.close()

        return result

    def run_insert_update_delete(self, connect_db=False,
                                 query=None, values=None):
        # print('ManageDbCars => run_insert_update_delete()')
        if connect_db:
            self.connect()

        if query is None:
            return

        if self.conn:
            if not query.endswith(';'):
                query += ';'

            # print(f'ManageDbCars => run_insert_update_delete() - query
            # [{query}] values [{values}]')
            self.cursor.execute(query, values)
            self.conn.commit()

            return self.conn.total_changes

        if connect_db:
            self.close()


if __name__ == "__main__":
    cars = ManageDbCars()

    cars.connect()
    # cars.drop_cars_table()
    # cars.create_cars_table()
    # cars.delete_all_cars_data()
    # cars.reset_auto_increment()
    # cars.show_all_tables_and_columns()
    cars.clear_cars_table(drop_create_table=True)
    cars.insert_cars_data()

    cars.get_all_cars_data()

    cars.close()
