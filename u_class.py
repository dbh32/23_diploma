import requests
import json
import time


def get_token():
    '''Получаем токен из файла'''
    with open('token.txt') as token_vault:
        for token in token_vault:
            token_vault.readline()
    return token


class User:

    def __init__(self, user_input):
        self.uid = self.get_id(user_input)

    def get_params(self):
        '''Параметры для обращения к vk api'''
        return {
            'access_token': get_token(),
            'v': '5.89',
        }

    def request(self, method, params):
        '''Обращаемся к vk api'''
        response = requests.get(
            'https://api.vk.com/method/' + method, params=params
        )
        time.sleep(0.34)
        print('.')
        return response

    def get_id(self, user_input):
        '''
        Проверяем ввод: screen_name или id
        Если screen_name, то получаем id
        '''
        if user_input.isdigit():
            return int(user_input)
        else:
            return self.get_id_from_sn(user_input)

    def get_id_from_sn(self, user_input):
        '''Получаем id по screen_name'''
        params = self.get_params().copy()
        params['screen_name'] = user_input
        response = self.request('utils.resolveScreenName', params=params)
        return response.json()['response']['object_id']

    def get_user_cred(self):
        '''Получаем информацию о пользователе'''
        params = self.get_params().copy()
        params['user_ids'] = self.uid
        response = self.request('users.get', params=params)
        return response.json()

    def get_groups(self):
        '''Получаем список групп, в которых состоит User'''
        params = self.get_params().copy()
        params['user_id'] = self.uid
        response = self.request('groups.get', params=params)
        return response.json()

    def get_group_members(self, group_id):
        '''Получаем список членов групп, в которых состоит User с фильтром по друзьям'''
        params = self.get_params().copy()
        params['group_id'] = group_id
        params['filter'] = 'friends'
        response = self.request('groups.getMembers', params=params)
        return response.json()

    def get_solo_groups(self):
        '''
        Сохраняем id групп, в которых нет друзей User-а, в файл
        Запускаем дальнейшее выполнение программы
        '''
        for group in self.get_groups()['response']['items']:
            if self.get_group_members(group)['response']['count'] == 0:
                with open('groups.txt', 'a') as doc:
                    doc.write(str(group))
                    doc.write(',')
            self.save_groups_json()

    def get_group_info(self):
        '''Получаем подробную информацию о сохраненных в файл группах'''
        params = self.get_params().copy()
        params['fields'] = 'members_count'
        with open('groups.txt') as groups_list:
            params['group_ids'] = groups_list.readline()
        response = self.request('groups.getById', params=params)
        return response.json()

    def format_groups_info(self):
        '''Убираем лишние поля из полученной информации о группах'''
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
        '''Сохраняем информацию о группах в json'''
        data = self.format_groups_info()
        with open('groups.json', 'w', encoding='utf-8-sig') as file:
            json.dump(data['response'], file, ensure_ascii=False, indent=4)

    def check_is_closed(self):
        '''
        Проверяем закрыт ли профиль
        Если открыт, то запускаем выполнение программы
        '''
        if self.get_user_cred()['response'][0]['is_closed']:
            print('К сожалению, профиль пользователя закрыт :(')
            print()
        else:
            self.get_solo_groups()
