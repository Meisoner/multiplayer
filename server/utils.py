from random import randrange as rr
from sqlite3 import connect as cn


users = dict()
destinations = dict()
lettera = ord('a')
db = cn('gamedata.db', check_same_thread=False)


# Функция для создания случайных токенов доступа
def get_token():
    res = ''
    for i in range(rr(30, 40)):
        if rr(3):
            res += str(rr(10))
        else:
            res += chr(lettera + rr(26))
    return res


# Функция для получения пользователя по токену
def get_user(token):
    if token not in users.keys():
        return ''
    elif users[token] == '-':
        return ''
    else:
        return users[token]