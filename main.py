import os
import time
import u_class


def clear_json():
    '''Удаляем файл, если существует'''
    try:
        os.remove('groups.json')
    except:
        pass


def clear_txt():
    '''Удаляем временный файл'''
    try:
        os.remove('groups.txt')
    except:
        pass


def main():
    start = time.time()

    clear_json()
    command = input('Введите screen_name или id пользователя: ')
    user = u_class.User(command)
    user.check_is_closed()
    clear_txt()

    finish = time.time()
    exec_time = finish - start
    print("Готово! Заняло " + str(exec_time) + " секунд.")


if __name__ == '__main__':
    main()
