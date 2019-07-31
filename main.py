import os
import time
import u_class


def clear_json():
    '''Удаляем файл, если существует'''
    try:
        os.remove('groups.json')
    except:
        pass


def main():
    start = time.time()
    clear_json()
    command = input('Введите screen_name или id пользователя: ')
    user = u_class.User(command)
    if user.id:
        user.get_results_json()
        finish = time.time()
        exec_time = finish - start
        print("Готово! Заняло " + str(exec_time) + " секунд.")
    else:
        print('Нельзя выполнить для не открытой страницы :(')


if __name__ == '__main__':
    main()
