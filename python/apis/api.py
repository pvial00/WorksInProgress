from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from json import dumps
from flask.ext.jsonpify import jsonify
from pycube256 import CubeRandom
from KlassiKrypto import Vigenere
from KlassiKrypto import Affine
from KlassiKrypto import Atbash
from KlassiKrypto import Baconian
from KlassiKrypto import BaconBits
from KlassiKrypto import Caesar
from KlassiKrypto import Polybius
from KlassiKrypto import Bifid
from KlassiKrypto import Trifid
from KlassiKrypto import Nihilist
from KlassiKrypto import VIC
from KlassiKrypto import Chaocipher
from pycube90 import Cube as Cube90
from pycube256 import Cube
import base64
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

class ChaoCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Chaocipher().encrypt(args['text'])

class ChaoDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Chaocipher().decrypt(args['text'])

class BifidDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Bifid().decrypt(args['text'])

class BifidCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Bifid().encrypt(args['text'])

class TrifidCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Trifid(args['key']).encrypt(args['text'])

class TrifidDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Trifid(args['key']).decrypt(args['text'])

class NiCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Nihilist(args['key']).encrypt(args['text'])

class NiDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Nihilist(args['key']).decrypt(args['text'])

class VICCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return VIC(args['key']).encrypt(args['text'])

class VICDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return VIC(args['key']).decrypt(args['text'])

class ViCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Vigenere(args['key']).encrypt(args['text'])

class ViDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Vigenere(args['key']).decrypt(args['text'])

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
        parser.add_argument('rot', type=int, required=False)
        args = parser.parse_args()
        if args['rot']:
            rot = args['rot']
        else:
            rot = 3
        return Caesar(rot).encrypt(args['text'])

class CaesarDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str, required=True)
        parser.add_argument('rot', type=int, required=False)
        args = parser.parse_args()
        if args['rot']:
            rot = args['rot']
        else:
            rot = 3
        return Caesar(rot).decrypt(args['text'])

class Cube90Crypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Cube90(args['key']).encrypt(args['text'])

class Cube90DeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Cube90(args['key']).decrypt(args['text'])

class CubeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return base64.b64encode(Cube(args['key']).encrypt(args['text']))

class CubeDeCrypt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', type=str, required=True)
        parser.add_argument('text', type=str, required=True)
        args = parser.parse_args()
        return Cube(args['key']).decrypt(base64.b64decode(args['text']))

api.add_resource(CryptoNum, '/random')
api.add_resource(ChaoCrypt, '/chaocipher')
api.add_resource(ChaoDeCrypt, '/chaocipher/decrypt')
api.add_resource(TrifidCrypt, '/trifid')
api.add_resource(TrifidDeCrypt, '/trifid/decrypt')
api.add_resource(BifidCrypt, '/bifid')
api.add_resource(BifidDeCrypt, '/bifid/decrypt')
api.add_resource(NiCrypt, '/nihilist')
api.add_resource(NiDeCrypt, '/nihilist/decrypt')
api.add_resource(VICCrypt, '/vic')
api.add_resource(VICDeCrypt, '/vic/decrypt')
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
api.add_resource(Cube90Crypt, '/cube90')
api.add_resource(Cube90DeCrypt, '/cube90/decrypt')
api.add_resource(CubeCrypt, '/cube')
api.add_resource(CubeDeCrypt, '/cube/decrypt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000')
