from flask import Flask, jsonify as jf
from random import randrange as rr
from sqlite3 import connect as cn
from hashlib import sha256 as hsh
from time import sleep
from threading import Thread
import os
from generator import generator as gen
from utils import users, get_user, get_token, destinations, db
from flask_restful import Api
import actions_resource


app = Flask(__name__)
api = Api(app)
save = dict()
userids = dict()
api.add_resource(actions_resource.ActionsResource, '/action')


def init():
    cr = db.cursor()
    cr.execute('''CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY AUTOINCREMENT, hash STRING,
        nickname STRING, x INTEGER DEFAULT 0, y INTEGER DEFAULT 6, banned INTEGER DEFAULT 0, hp INTEGER DEFAULT 10)''')
    cr.execute('CREATE TABLE IF NOT EXISTS Map(block INTEGER, x INTEGER, y INTEGER)')
    cr.execute('''CREATE TABLE IF NOT EXISTS Actions(id INTEGER PRIMARY KEY AUTOINCREMENT,
        player INTEGER references Users(id), action INTEGER, tm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data STRING, seen STRING DEFAULT "| ")''')
    q = '''CREATE TABLE IF NOT EXISTS Inventories(id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER references Users(id), slot INTEGER, item INTEGER DEFAULT 0, amount INTEGER DEFAULT 0)'''
    cr.execute(q)
    for i in range(3):
        set_height(i - 1, 5)


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
        destinations[nickname] = False
        userids[nickname] = rr(10 ** 10)
        return jf(['ok', token])


@app.route('/get_blocks/<token>')
def blocks(token):
    global save
    cr = db.cursor()
    user = get_user(token)
    if not user:
        return jf(['err', 'Токен не найден.'])
    pos = cr.execute(f'SELECT x, y FROM Users WHERE nickname = "{user}"').fetchone()
    res = []
    protres = []
    if destinations[user]:
        rng = range(pos[0] + 29, pos[0] - 30, -1)
    else:
        rng = range(pos[0] - 30, pos[0] + 30)
    for x in rng:
        bls = cr.execute('SELECT * FROM Map WHERE x = ' + str(x)).fetchall()
        check = cr.execute('SELECT * FROM Map WHERE y = 0 AND x = ' + str(x)).fetchone()
        if not check:
            if x in save.keys():
                hg = save[x]
            else:
                hg = max(get_height(x - 1), get_height(x + 1))
                rev = destinations[user]
                if not hg:
                    hg = 5
                if not rr(10):
                    if not rr(3) or hg < 4:
                        d = 1
                    else:
                        d = -1
                    if hg > 10:
                        hg -= 2
                    else:
                        if rr(4):
                            hg += d
                        else:
                            hg += 2 * d
                if not rr(40):
                    d = gen(x, hg, rev)
                    for j in d[1]:
                        set_height(j, hg)
                    for q in d[0]:
                        cr.execute(q)
            for y in range(hg + 1):
                if rr(10):
                    block = 0
                elif rr(4):
                    block = 1
                else:
                    block = 2
                try:
                    cr.execute('INSERT INTO Map(block, x, y) VALUES(?, ?, ?)', (block, x, y))
                except Exception:
                    pass
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
    item = cr.execute(f'SELECT block FROM Map WHERE x = {x} AND y = {y}').fetchone()
    if not item:
        return jf(['err'])
    cr.execute(f'DELETE FROM Map WHERE x = {x} AND y = {y}')
    query = cr.execute(f'SELECT Slot FROM Inventories WHERE item = {item[0]} AND userid = {userid} AND amount > 0')
    invslot = query.fetchone()
    if not invslot:
        invslot = cr.execute(f'SELECT Slot From Inventories WHERE amount = 0 AND userid = {userid}').fetchone()
    cr.execute(f'''UPDATE Inventories SET amount = amount + 1, item = {item[0]}
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


@app.route('/players/<token>')
def getothers(token):
    user = get_user(token)
    if not user:
        return jf(['err', 'Токен не найден.'])
    cr = db.cursor()
    uid, x = cr.execute(f'SELECT id, x FROM Users WHERE nickname = "{user}"').fetchone()
    players = cr.execute('SELECT * FROM Users WHERE x >= ? AND x <= ?', (x - 30, x + 30)).fetchall()
    res = []
    for p in players:
        name = p[2]
        if name in users.values() and name != user:
            otherid = cr.execute('SELECT id FROM Users WHERE nickname = "' + name + '"').fetchone()[0]
            acts = cr.execute('''SELECT Action FROM Actions WHERE player = ?
                AND datetime(tm) > datetime("now", "-5 second")
                AND seen NOT LIKE "% ''' + str(uid) + ''' %"''',
                (otherid,)).fetchall()
            cr.execute('''UPDATE Actions SET seen = seen || ? WHERE player = ?
                AND datetime(tm) > datetime("now", "-5 second")
                AND seen NOT LIKE "% ''' + str(uid) + ''' %"''',
                (str(uid) + ' ', otherid)).fetchall()
            res += [dict()]
            res[-1]['id'] = userids[name]
            res[-1]['name'] = name
            res[-1]['pos'] = [p[3], p[4]]
            res[-1]['hp'] = p[6]
            res[-1]['acts'] = acts
    return jf(res)



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


def set_height(x, h):
    global save
    save[x] = h


def committer():
    while True:
        sleep(2)
        print(destinations)
        db.commit()


if __name__ == '__main__':
    init()
    cmt = Thread(target=committer)
    cmt.setDaemon(True)
    cmt.start()
    app.run()