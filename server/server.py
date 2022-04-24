from utils import users, get_user, get_token, destinations, db
from flask_restful import Api
import actions_resource
import inventories_resource
from flask import jsonify as jf
import os
from random import randrange as rr
from hashlib import sha256 as hsh
from time import sleep
from threading import Thread
from generator import generator as gen
from flask import Flask, render_template, redirect
from forms.loginform import LoginForm, GoinForm
from flask_login import LoginManager
from data import db_session
from data.users import User


app = Flask(__name__)
api = Api(app)
save = dict()
userids = dict()
api.add_resource(actions_resource.ActionsResource, '/action')
api.add_resource(inventories_resource.InventoryResource, '/get_inv/<token>')
lettera = ord('a')
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secretkey:p'
with open('crafts.txt') as file:
    crafts = dict()
    for i in file.read().split('\n'):
        data = [int(j) for j in i.split()]
        material = data[0]
        crafts[material] = dict()
        crafts[material][-1] = data[1]
        for j in range(len(data) // 2 - 1):
            crafts[material][data[j * 2 + 2]] = data[j * 2 + 3]
print('loaded', len(crafts), 'crafts:', str(crafts).replace('-1', 'amount'))


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


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/end")
def end():
    return render_template("end.html")


@app.route('/regi', methods=['GET', 'POST'])
def reg():
    form = LoginForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nickname=form.nickname.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        cr = db.cursor()
        uid = cr.execute(f'SELECT id FROM Users WHERE nickname = "{form.nickname.data}"').fetchone()[0]
        for i in range(20):
            cr.execute(f'INSERT INTO Inventories(userid, slot) VALUES(?, ?)', (uid, i))
        return redirect('/end')
    return render_template('register.html', title='Регистрация', form=form)
    # if form.validate_on_submit():
    #     return os.system('python client/game.py')


@app.route('/go_in', methods=['GET', 'POST'])
def go_in():
    form = GoinForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return redirect('/end')
    return render_template('login.html', title='Вход', form=form)
    # if form.validate_on_submit():
    #     return os.system('python client/game.py')


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
    print(hs)
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


@app.route('/crafts')
def getcrafts():
    return jf(crafts)


@app.route('/craft/<token>/<int:item>')
def craft(token, item):
    user = get_user(token)
    if not user:
        return jf(['err', 'Токен не найден.'])
    if item not in crafts.keys():
        return jf(['err', 'Эта вещь несоздаваема.'])
    cr = db.cursor()
    userid = cr.execute(f'SELECT id FROM Users WHERE nickname = "{user}"').fetchone()[0]
    data = []
    for i in crafts[item].keys():
        if i != -1:
            check = cr.execute(f'''SELECT slot FROM Inventories WHERE userid = {userid} AND amount >= {crafts[item][i]}
                AND item = {i}''').fetchone()
            if not check:
                return jf(['err', 'Недостаточно ресурсов.'])
            data += [(check[0], crafts[item][i])]
    for i in data:
        cr.execute(f'UPDATE Inventories SET amount = amount - {i[1]} WHERE slot = {i[0]}')
    query = cr.execute(f'SELECT Slot FROM Inventories WHERE item = {item} AND userid = {userid} AND amount > 0')
    invslot = query.fetchone()
    if not invslot:
        invslot = cr.execute(f'SELECT Slot From Inventories WHERE amount = 0 AND userid = {userid}').fetchone()
    cr.execute(f'''UPDATE Inventories SET amount = amount + {crafts[item][-1]}, item = {item}
                   WHERE slot = {invslot[0]} AND userid = {userid}''')
    return jf(['Успешно!'])


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
            cond = f''' WHERE player = {otherid} AND datetime(tm) > datetime("now", "-5 second")
                AND Action < 4 AND seen NOT LIKE "% {str(uid)} %"'''
            ids = ', '.join([str(i[0]) for i in cr.execute('SELECT id FROM Actions' + cond).fetchall()])
            acts = cr.execute('SELECT action, data FROM Actions WHERE id IN (' + ids + ')').fetchall()
            cr.execute('UPDATE Actions SET seen = seen || "' + str(uid) + ' "' + 'WHERE id IN (' + ids + ')').fetchall()
            res += [dict()]
            res[-1]['id'] = userids[name]
            res[-1]['name'] = name
            res[-1]['pos'] = [p[3], p[4]]
            res[-1]['hp'] = p[6]
            res[-1]['acts'] = acts
    return jf(res)


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
    clean = 0
    while True:
        sleep(2)
        clean = (clean + 1) % 10
        if not clean:
            cr = db.cursor()
            cr.execute('DELETE FROM Actions WHERE (action = 1 OR action = 2) AND datetime(tm) < datetime("now", "-10 second")')
        # print(destinations)
        db.commit()


if __name__ == '__main__':
    init()
    db_session.global_init("gamedata.db")
    cmt = Thread(target=committer)
    cmt.setDaemon(True)
    cmt.start()
    app.run()
