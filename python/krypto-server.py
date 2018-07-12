import socket
from Crypto.Cipher import AES

host = "127.0.0.1"
port = 1200
file = open("book")
buf = file.read()
buflen = len(buf)
blocks = buflen / 16

key='abcdefghijklmnop'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind((socket.gethostname(), 1200))
s.bind((host, port))
s.listen(5)

def kryptblock(block):
        obj = AES.new(key, AES.MODE_CBC, '01AB 34ABEDEFTXe')
        krypto = obj.encrypt(block)
        return krypto

def sendkrypto(krypto):
        c.send(krypto)
        return

def getblock():
        block = file.read(16)
        return block

a = 0
x = 0
while 1:
        c, addr = s.accept()
        for x in range(a,blocks):
           file.seek(a)
           block = getblock()
           krypto = kryptblock(block)
           sendkrypto(krypto)
           a = a + 16
        c.send(krypto)
        c.close()
