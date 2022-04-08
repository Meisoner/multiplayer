from flask import Flask, jsonify as jf
from random import randrange as rr
from sqlite3 import connect as cn
from hashlib import sha256 as hsh
from time import sleep
from threading import Thread
import os
from generator import generator as gen


app = Flask(__name__)
db = cn('gamedata.db', check_same_thread=False)
users = dict()
lettera = ord('a')


def init():
    cr = db.cursor()
    cr.execute('''CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY AUTOINCREMENT, hash STRING,
        nickname STRING, x INTEGER DEFAULT 0, y INTEGER DEFAULT 6, banned INTEGER DEFAULT 0, hp INTEGER DEFAULT 10)''')
    cr.execute('CREATE TABLE IF NOT EXISTS Map(block INTEGER, x INTEGER, y INTEGER)')
    q = '''CREATE TABLE IF NOT EXISTS Inventories(id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER references Users(id), slot INTEGER, item INTEGER DEFAULT 0, amount INTEGER DEFAULT 0)'''
    cr.execute(q)


def get_token():
    res = ''
    for i in range(rr(30, 40)):
        if rr(3):
            res += str(rr(10))
        else:
            res += chr(lettera + rr(26))
    return res


def get_user(token):
    if token not in users.keys():
        return ''
    elif users[token] == '-':
        return ''
    else:
        return users[token]


@app.route('/register/<psw>/<nickname>')
def register(psw, nickname):
    cr = db.cursor()
    exists = list(cr.execute('SELECT id FROM Users WHERE nickname = "' + nickname + '"'))
    if exists:
        return jf(['err', 'Такой пользователь уже существует.'])
    hs = hsh((nickname + ':' + psw).encode()).hexdigest()
    cr.execute(f'INSERT INTO Users(hash, nickname) VALUES("{hs}", "{nickname}")')
    uid = cr.execute(f'SELECT id FROM Users WHERE nickname = "{nickname}"').fetchone()[0]
    for i in range(20):
        cr.execute(f'INSERT INTO Inventories(userid, slot) VALUES(?, ?)', (uid, i))
    return jf(['ok'])


@app.route('/token/<psw>/<nickname>')
def login(psw, nickname):
    cr = db.cursor()
    hs = hsh((nickname + ':' + psw).encode()).hexdigest()
    user = list(cr.execute(f'SELECT * FROM Users WHERE hash = "{hs}" AND nickname = "{nickname}"'))
    token = get_token()
    if not user:
        return jf(['err', 'Такого пользователя не существует.'])
    elif user[0][5]:
        return jf(['err', 'Аккаунт данного пользователя заблокирован.'])
    else:
        users[token] = nickname
        print(users)
        return jf(['ok', token])


@app.route('/get_blocks/<token>')
def blocks(token):
    cr = db.cursor()
    user = get_user(token)
    if not user:
        return jf(['err', 'Токен не найден.'])
    pos = cr.execute(f'SELECT x, y FROM Users WHERE nickname = "{user}"').fetchone()
    res = []
    protres = []
    for x in range(pos[0] - 30, pos[0] + 30):
        bls = cr.execute('SELECT * FROM Map WHERE x = ' + str(x)).fetchall()
        if not bls:
            hg = max(get_height(x - 1), get_height(x + 1))
            if not hg:
                hg = 5
            if not rr(10):
                if rr(2) or hg < 4:
                    d = 1
                else:
                    d = -1
                if rr(4):
                    hg += d
                else:
                    hg += 2 * d
            for y in range(hg + 1):
                if rr(10):
                    block = 0
                elif rr(4):
                    block = 1
                else:
                    block = 2
                cr.execute('INSERT INTO Map(block, x, y) VALUES(?, ?, ?)', (block, x, y))
                if y == 0:
                    protres += [[block, x, 0]]
                else:
                    res += [[block, x, y]]
        else:
            for i in bls:
                if i[2] == 0:
                    protres += [[i[0], x, 0]]
                else:
                    res += [[i[0], x, i[2]]]
    return jf([res, protres])


@app.route('/get_pos/<token>')
def gpos(token):
    cr = db.cursor()
    user = get_user(token)
    if not user:
        return jf(['err', 'Токен не найден.'])
    pos = cr.execute(f'SELECT x, y FROM Users WHERE nickname = "{user}"').fetchone()
    return jf(pos)


@app.route('/update_pos/<token>/<ax>/<ay>')
def updpos(token, ax, ay):
    cr = db.cursor()
    try:
        x, y = int(ax), int(ay)
    except Exception:
        return jf(['err', 'Недопустимое значение.'])
    user = get_user(token)
    if not user:
        return jf(['err', 'Токен не найден.'])
#    check = cr.execute(f'SELECT * FROM Map WHERE x = {x} AND y = {y}').fetchone()
#    if check:
#        removetoken(token)
#        cr.execute(f'UPDATE Users SET banned = 1 WHERE nickname = "{user}"')
#    else:
    cr.execute(f'UPDATE Users SET x = {x}, y = {y} WHERE nickname = "{user}"')
    return jf(['ok'])


@app.route('/break/<token>/<ax>/<ay>')
def removeblock(token, ax, ay):
    cr = db.cursor()
    try:
        x, y = int(ax), int(ay)
    except Exception:
        return jf(['err', 'Недопустимое значение.'])
    user = get_user(token)
    if not user:
        return jf(['err', 'Токен не найден.'])
    userid = cr.execute(f'SELECT id FROM Users WHERE nickname = "{user}"').fetchone()[0]
    if y == 0:
        return jf(['err', 'Невозможно уничтожить нижнюю границу мира.'])
    item = cr.execute(f'SELECT block FROM Map WHERE x = {x} AND y = {y}').fetchone()[0]
    cr.execute(f'DELETE FROM Map WHERE x = {x} AND y = {y}')
    query = cr.execute(f'SELECT Slot FROM Inventories WHERE item = {item} AND userid = {userid} AND amount > 0')
    invslot = query.fetchone()
    if not invslot:
        invslot = cr.execute(f'SELECT Slot From Inventories WHERE amount = 0 AND userid = {userid}').fetchone()
    cr.execute(f'''UPDATE Inventories SET amount = amount + 1, item = {item}
               WHERE slot = {invslot[0]} AND userid = {userid}''')
    return jf(['ok'])


@app.route('/place/<token>/<int:blid>/<ax>/<ay>')
def addblock(token, blid, ax, ay):
    cr = db.cursor()
    try:
        x, y = int(ax), int(ay)
    except Exception:
        return jf(['err', 'Недопустимое значение.'])
    user = get_user(token)
    if not user:
        return jf(['err', 'Токен не найден.'])
    already = cr.execute(f'SELECT block FROM Map WHERE x = {x} AND y = {y}').fetchone()
    if already:
        return jf(['err', 'Эти координаты уже заняты.'])
    userid = cr.execute(f'SELECT id FROM Users WHERE nickname = "{user}"').fetchone()[0]
    check = cr.execute(f'SELECT slot FROM Inventories WHERE userid = ? AND amount > 0 AND item = ?',
                       (userid, blid)).fetchone()
    if check:
        cr.execute(f'UPDATE Inventories SET amount = amount - 1 WHERE slot = {check[0]} AND userid = {userid}')
        cr.execute(f'INSERT INTO Map(block, x, y) VALUES({blid}, {x}, {y})')
        return jf(['ok'])
    return jf(['err', 'В инвентаре игрока нет этого блока.'])


@app.route('/get_inv/<token>')
def inv(token):
    user = get_user(token)
    if not user:
        return jf(['err', 'Токен не найден.'])
    cr = db.cursor()
    inres = cr.execute(f'''SELECT item, amount FROM Inventories WHERE userid = (SELECT id FROM Users
        WHERE nickname = "{user}")''').fetchall()
    return jf(inres)


@app.route('/exit/<token>')
def removetoken(token):
    if token in users.keys():
        users[token] = '-'
    return jf(['ok'])


@app.route('/game_status')
def status():
    return '"Working"'


@app.route('/off')
def off():
    os._exit(0)


def get_height(x):
    cr = db.cursor()
    res = cr.execute('SELECT y FROM Map WHERE x = ' + str(x) + ' ORDER BY y DESC').fetchone()
    if res:
        return res[0]
    return 0


def committer():
    while True:
        sleep(2)
        db.commit()


if __name__ == '__main__':
    init()
    cmt = Thread(target=committer)
    cmt.setDaemon(True)
    cmt.start()
    app.run()