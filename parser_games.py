from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('steam_return_to', required=True)
parser.add_argument('steam_realm', required=True)

