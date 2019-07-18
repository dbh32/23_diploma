import os
import requests

# from pprint import pprint

TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'


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
        return response

    def get_groups(self):
        # Список групп, в которых состоит User
        params = self.get_params()
        response = self.request('groups.get', params=params)
        return response.json()

    def get_group_members(self, group_id):
        # Список членов групп, в которых состоит User с фильтром по друзьям
        params = self.get_params().copy()
        params['group_id'] = group_id
        params['filter'] = 'friends'
        response = self.request('groups.getMembers', params=params)
        return response.json()

    # def get_friends(self):
    #     # Список друзей User
    #     params = self.get_params()
    #     response = self.request('friends.get', params=params)
    #     return response.json()


# def get_friends_ids(user):
#     # Сохраняем ID друзей в документ
#     for response in user.get_friends()['response']['items']:
#         with open('friends.txt', 'a') as document:
#             document.write(str(response))
#             document.write('\n')


def get_solo_groups(user):
    # Получаем ID групп, в которых нет друзей пользователя

    def get_group_ids(user):
        # Сохраняем ID груп в документ
        for response in user.get_groups()['response']['items']:
            with open('groups.txt', 'a') as doc:
                doc.write(str(response))
                doc.write('\n')

    def get_groups_ids_list():
        # Получаем список из ID групп
        ids_list = []
        with open('groups.txt') as groups:
            for line in groups:
                line = line.lower().split()
                ids_list.append(line)
        return ids_list

    get_group_ids(user)
    for group in get_groups_ids_list():
        group = str(group[0])
        if user.get_group_members(group)['response']['count'] != 0:
            pass
        else:
            print(group)


Eugen = User(TOKEN)
get_solo_groups(Eugen)
# os.remove('friends.txt')
os.remove('groups.txt')
