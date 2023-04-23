from flask_restful import Resource
from flask import jsonify
from parser_games import parser
import sqlite3


class Add_domen(Resource):
    def post(self):
        args = parser.parse_args()
        entities = (args['steam_return_to'], args['steam_realm'])
        con = sqlite3.connect('db/domen.db')
        cur = con.cursor()
        cur.execute(
            """INSERT INTO add_for_domen(return_to, realm) VALUES(?, ?)""",
            entities)
        con.commit()
        return jsonify({'success': 'OK'})

