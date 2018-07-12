from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random
from binascii import hexlify
from binascii import unhexlify
from base64 import b64encode
from base64 import b64decode
from getpass import getpass
import sys, socket, threading, select, nacl.secret, nacl.utils, hashlib

server = "localhost"
port = 64666
client_id = "StreamClient"

def rsa_encrypt(data, public_key):
    key_obj = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(key_obj)
    cipher_text = cipher.encrypt(data)
    return cipher_text

def auth_pkg(user, passw, session_key):
    return user + ":" + passw + ":" + session_key

def gen_session_key():
    session_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    return session_key

def recv_thread(sock, box):
    while sock:
        try:
            readable, writable, errable = select.select(sock, sock, sock)
        except socket.error as ser:
            break
        for r in readable:
            room_chat = r.recv(2048)
            room_chat = box.decrypt(room_chat)
            sys.stdout.write(room_chat+"\n")
            
user = raw_input("login:")
password = getpass("password:")
passw = hashlib.sha256(password).hexdigest()
session_key = gen_session_key()
box = nacl.secret.SecretBox(session_key)
session_pkg = auth_pkg(user, passw, session_key)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((server, port))
except socket.error as ser:
    print "Error: Unable to connect to server, try again."
client_id = b64encode(client_id)
s.send(client_id)
server_key = s.recv(2048)
server_key = b64decode(server_key)
session_pkg = rsa_encrypt(session_pkg, server_key)
s.send(session_pkg)
menu = s.recv(1024)
if menu != "":
    mmenu = box.decrypt(menu)
    print mmenu
    myroom = raw_input()
    myroom = box.encrypt(myroom)
    s.send(myroom)
    room_chat = s.recv(2048)
    room_chat = box.decrypt(room_chat)
    print room_chat
    sockets = []
    sockets.append(s)
    threading.Thread(target=recv_thread, args=(sockets, box)).start()
    while True:
        msg = raw_input()
        if msg == "exit":
            msg = box.encrypt(msg)
            s.send(msg)
            break
        msg = box.encrypt(msg)
        s.send(msg)

s.close()
