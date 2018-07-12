from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from json import dumps
from flask.ext.jsonpify import jsonify
from pycube256 import CubeRandom
from ciphersuitez import Vigenere
from ciphersuitez import Affine
from ciphersuitez import Atbash
from ciphersuitez import Baconian
from ciphersuitez import BaconBits
from ciphersuitez import Caesar
import os

app = Flask(__name__)
api = Api(app)

class CryptoNum(Resource):
    def get(self):
        return CubeRandom().randint()

class Choice(Resource):
    def get(self, num):
        items = { '1': 'apples', '2': 'oranges'}
        return items[num]

class ViCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Vigenere().encrypt(args['text'], args['key'])

class ViDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Vigenere().decrypt(args['text'], args['key'])

class AffineCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Affine().encrypt(args['text'])

class AffineDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Affine().decrypt(args['text'])

class AtbashCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Atbash().encrypt(args['text'])

class AtbashDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Atbash().decrypt(args['text'])

class BaconCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Baconian().encrypt(args['text'])

class BaconDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Baconian().decrypt(args['text'])

class BaconbitsCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return BaconBits().encrypt(args['text'])

class BaconbitsDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return BaconBits().decrypt(args['text'])

class CaesarCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Caesar().encrypt(args['text'])

class CaesarDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Caesar().decrypt(args['text'])


api.add_resource(CryptoNum, '/random')
api.add_resource(ViCrypt, '/vigenere')
api.add_resource(ViDeCrypt, '/vigenere/decrypt')
api.add_resource(AffineCrypt, '/affine')
api.add_resource(AffineDeCrypt, '/affine/decrypt')
api.add_resource(AtbashCrypt, '/atbash')
api.add_resource(AtbashDeCrypt, '/atbash/decrypt')
api.add_resource(BaconCrypt, '/baconian')
api.add_resource(BaconDeCrypt, '/baconian/decrypt')
api.add_resource(BaconbitsCrypt, '/baconbits')
api.add_resource(BaconbitsDeCrypt, '/baconbits/decrypt')
api.add_resource(CaesarCrypt, '/caesar')
api.add_resource(CaesarDeCrypt, '/caesar/decrypt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000')
