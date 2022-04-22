from flask_restful import reqparse, abort, Resource
from flask import jsonify as jf
from utils import get_user
from utils import db


class InventoryResource(Resource):
    def get(self, token):
        user = get_user(token)
        if not user:
            return jf(['err', 'Токен не найден.'])
        cr = db.cursor()
        inres = cr.execute(f'''SELECT item, amount FROM Inventories WHERE userid = (SELECT id FROM Users
            WHERE nickname = "{user}") ORDER BY slot''').fetchall()
        return jf(inres)

    def post(self, token):
        cr = db.cursor()
        args = parser.parse_args()
        user = get_user(token)
        uid = cr.execute(f'SELECT id FROM Users WHERE nickname = "{user}"').fetchone()[0]
        for i in args['moved']:
            first = cr.execute(f'SELECT id, item, amount FROM Inventories WHERE slot = {i[0]} AND userid = {uid}').fetchone()
            second = cr.execute(f'SELECT id, item, amount FROM Inventories WHERE slot = {i[1]} AND userid = {uid}').fetchone()
            cr.execute(f'UPDATE Inventories SET item = {first[1]}, amount = {first[2]} WHERE id = {second[0]}')
            cr.execute(f'UPDATE Inventories SET item = {second[1]}, amount = {second[2]} WHERE id = {first[0]}')
        return jf(['ok'])


parser = reqparse.RequestParser()
parser.add_argument('moved', type=list, location='json')