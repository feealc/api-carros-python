import os
import json


class HandleJsonFile:

    @staticmethod
    def load():
        try:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            file_name = os.path.join(current_dir, '../', 'project.json')

            with open(file_name, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f'Erro ao carregar arquivo json')
            raise e


if __name__ == '__main__':
    print(HandleJsonFile.load())
