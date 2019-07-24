import os
import requests
import json
import time
from pprint import pprint


class User:

    def __init__(self, token):
        self.token = token

    def get_params(self):
        # Параметры для обращения к VK API
        return {
            'access_token': self.token,
            'v': '5.54',
        }

    def request(self, method, params):
        # Обращение к VK API
        response = requests.get(
            'https://api.vk.com/method/' + method, params=params
        )
        time.sleep(0.34)
        print('.')
        return response

    def get_groups(self):
        # Список групп, в которых состоит User
        params = self.get_params().copy()
        response = self.request('groups.get', params=params)
        return response.json()

    def get_group_members(self, group_id):
        # Список членов групп, в которых состоит User с фильтром по друзьям
        params = self.get_params().copy()
        params['group_id'] = group_id
        params['filter'] = 'friends'
        response = self.request('groups.getMembers', params=params)
        return response.json()

    def get_solo_groups(self):
        # Сохраняем ID групп в файл, в которых нет друзей пользователя
        for group in self.get_groups()['response']['items']:
            if self.get_group_members(group)['response']['count'] == 0:
                with open('groups.txt', 'a') as doc:
                    doc.write(str(group))
                    doc.write(',')
        return doc

    def get_group_info(self):
        # Получаем требуемую информацию о сохраненных в файл группах
        params = self.get_params().copy()
        params['fields'] = 'members_count'
        with open('groups.txt') as groups_list:
            params['group_ids'] = groups_list.readline()
        response = self.request('groups.getById', params=params)
        return response.json()

    def format_groups_info(self):
        # Убираем лишние поля из информации о группах
        groups_info = self.get_group_info()
        for field in groups_info['response']:
            field.pop('is_closed')
            field.pop('photo_100')
            field.pop('photo_200')
            field.pop('photo_50')
            field.pop('screen_name')
            field.pop('type')
        return groups_info

    def save_groups_json(self):
        # Сохраняем информацию в json
        data = self.format_groups_info()
        with open('groups.json', 'w', encoding='utf-8-sig') as file:
            json.dump(data['response'], file, ensure_ascii=False, indent=4)

    def get_results(self):
        # Последовательное выполнение для получения итогового результата
        self.get_solo_groups()
        self.get_group_info()
        self.format_groups_info()
        self.save_groups_json()


def get_token():
    # Получаем токен из файла
    with open('token.txt') as token_vault:
        for token in token_vault:
            token_vault.readline()
    return token


def main():
    eugen = User(get_token())
    eugen.get_results()
    os.remove('groups.txt')
    print('done!')


if __name__ == '__main__':
    main()
