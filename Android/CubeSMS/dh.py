import random, os
from Crypto.Util import number
from Crypto.Random import random
from pycube256 import CubeKDF
from base64 import b64encode, b64decode
import socket

class DHE:
    def __init__(self, keylen=16,socket=None, psize=1024, iterations=10):
        self.keylen = keylen
        if socket != None:
            self.sock = socket
        self.prime_size = psize
        self.iterations = iterations

    def encode(self, num):
        b = number.long_to_bytes(num)
        e = b64encode(b)
        return e

    def decode(self, b64):
        b = b64decode(b64)
        l = number.bytes_to_long(b)
        return l

    def gen_prime(self):
        return number.getStrongPrime(self.prime_size)

    def gen(self):
        g = self.gen_prime()
        p = self.gen_prime()
        secret = random.StrongRandom().randrange(0, (p - 1))
        return self.encode(g), self.encode(p), self.encode(secret)

    def _step1(self, g, p, secret):
        step1 = pow(self.decode(g), self.decode(secret), self.decode(p))
        return self.encode(step1)

    def _step2(self, step1, p, secret):
        key = number.long_to_bytes(pow(self.decode(step1), self.decode(secret), self.decode(p)))
        return CubeKDF().genkey(key, length=self.keylen)
