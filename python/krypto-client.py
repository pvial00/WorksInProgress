from Crypto.Cipher import AES
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket()
host = "127.0.0.1"
port = 1200
key = 'abcdefghijklmnop'
true = 0

file = open('out', 'w')
krypto = ""
s.connect((host, port))
for x in range(0,16694):
        #krypto = s.recv(267118)
        krypto = s.recv(16)
        obj = AES.new(key, AES.MODE_CBC, '01AB 34ABEDEFTXe')
        plain = obj.decrypt(krypto)
        file.write(plain)
        print plain,
file.close()

