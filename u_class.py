import requests, json
from retry import retry


def get_token():
    '''Получаем токен из файла'''
    with open('token.txt') as token_vault:
        for token in token_vault:
            token_vault.readline()
    return token


class User:

    def __init__(self, user_input):
        self.id = self.check_if_closed(user_input)

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
        print('.')
        return response

    def check_if_closed(self, uid):
        '''Проверяем, что профиль доступен'''
        response = self.get_user_info_retry(uid)[0]
        if ('is_closed', True) in response.items():
            print(f"Страница пользователя с id{response['id']} закрыта")
        elif ('deactivated', 'deleted') in response.items():
            print(f"Страница пользователя с id{response['id']} удалена")
        elif ('deactivated', 'banned') in response.items():
            print(f"Страница пользователя с id{response['id']} заблокирована")
        elif ('is_closed', False) in response.items():
            return response['id']

    def get_user_info(self, uid):
        '''Получаем информацию о пользователе'''
        params = self.get_params().copy()
        params['user_ids'] = uid
        response = self.request('users.get', params=params)
        return response.json()

    @retry(KeyError, delay=1, backoff=2, tries=5)
    def get_user_info_retry(self, uid):
        self.get_user_info(uid)
        return self.get_user_info(uid)['response']

    def get_groups(self, uid):
        '''Получаем перечень групп, в которых состоит User'''
        params = self.get_params().copy()
        params['user_id'] = uid
        response = self.request('groups.get', params=params)
        return response.json()

    @retry(KeyError, delay=1, backoff=2, tries=5)
    def get_groups_retry(self, uid):
        self.get_groups(uid)
        return self.get_groups(uid)['response']['items']

    def get_groups_set(self, uid):
        '''Получаем множество групп пользователя'''
        groups_set = set()
        for group in self.get_groups_retry(uid):
            groups_set.add(group)
        return groups_set

    def get_friends(self):
        '''Получаем список ID друзей'''
        params = self.get_params().copy()
        params['user_id'] = self.id
        response = self.request('friends.get', params=params)
        return response.json()

    def get_available_friends(self):
        '''Формируем список друзей с открытым профилем'''
        available_friends = []
        for friend in self.get_friends()['response']['items']:
            available_friends.append(self.check_if_closed(friend))
        return available_friends

    def get_friends_groups_set(self):
        '''Получаем множество групп всех друзей'''
        friends_groups_set = set()
        for friend in self.get_available_friends():
            friends_groups_set.update(self.get_groups_set(friend))
        return friends_groups_set

    def get_groups_wo_friends(self):
        '''Множество групп, в которых нет друзей'''
        result = self.get_groups_set(self.id).difference(
            self.get_friends_groups_set())
        return result

    def get_groups_wo_friends_info(self):
        '''Получаем подробную информацию о группах из множества без друзей'''
        if len(self.get_groups_wo_friends()) == 0:
            pass
        else:
            params = self.get_params().copy()
            params['fields'] = 'members_count'
            params['group_ids'] = str(self.get_groups_wo_friends())[1:-2]
            response = self.request('groups.getById', params=params)
            return response.json()

    def format_groups_info(self):
        '''Убираем лишние поля из полученной информации о группах'''
        if len(self.get_groups_wo_friends()) == 0:
            pass
        else:
            groups_info = self.get_groups_wo_friends_info()
            for field in groups_info['response']:
                field.pop('is_closed')
                field.pop('photo_100')
                field.pop('photo_200')
                field.pop('photo_50')
                field.pop('screen_name')
                field.pop('type')
            return groups_info

    def get_results_json(self):
        '''Сохраняем информацию о группах в json'''
        if len(self.get_groups_wo_friends()) == 0:
            print('Групп без друзей нет :(')
        else:
            data = self.format_groups_info()
            with open('groups.json', 'w', encoding='utf-8-sig') as file:
                json.dump(data['response'], file, ensure_ascii=False, indent=4)
