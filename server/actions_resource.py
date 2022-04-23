from flask_restful import reqparse, abort, Resource
from flask import jsonify as jf
from utils import get_user
from utils import destinations, db


class ActionsResource(Resource):
    def post(self):
        cr = db.cursor()
        args = parser.parse_args()
        user = get_user(args['token'])
        dat = cr.execute(f'SELECT id, x, y FROM Users WHERE nickname = "{user}"').fetchone()
        uid = dat[0]
        pos = [dat[1], dat[2]]
        posx = pos[0]
        for i in args['actions']:
            if i[0] == 0:
                if i[1] == 0:
                    pos[0] -= 1
                elif i[1] == 1:
                    pos[0] += 1
                elif i[1] == 2:
                    pos[1] += 1
                elif i[1] == 3:
                    pos[1] -= 1
            cr.execute('INSERT INTO Actions(player, action, data) VALUES(?, ?, ?)', (uid, i[0], i[1]))
        cr.execute(f'UPDATE Users SET x = {pos[0]}, y = {pos[1]} WHERE nickname = "{user}"')
        destinations[user] = posx > pos[0]
        return jf(pos)


# def updpos(token, ax, ay):
#     cr = db.cursor()
#     try:
#         x, y = int(ax), int(ay)
#     except Exception:
#         return jf(['err', 'Недопустимое значение.'])
#     user = get_user(token)
#     if not user:
#         return jf(['err', 'Токен не найден.'])
# #    check = cr.execute(f'SELECT * FROM Map WHERE x = {x} AND y = {y}').fetchone()
# #    if check:
# #        removetoken(token)
# #        cr.execute(f'UPDATE Users SET banned = 1 WHERE nickname = "{user}"')
# #    else:
#     posx = cr.execute(f'SELECT x, y FROM Users WHERE nickname = "{user}"').fetchone()[0]
#     destinations[user] = posx > x
#
#     return jf(['ok'])


parser = reqparse.RequestParser()
parser.add_argument('token', required=True)
parser.add_argument('actions', type=list, location='json')