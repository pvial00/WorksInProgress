from pycube import Cube
import socket, threading, select, sys, random

key = "NEVERSAYNEVERAGAIN"
host = "0.0.0.0"
port = 62666

def recv_thread(s):
    sockets = []
    sockets.append(s)
    while sockets:
        readable, writable, errable = select.select(sockets, sockets, sockets)
        for r in readable:
            buf = r.recv(2048)
            sys.stdout.write(Cube(key).decrypt(buf)+"\n")

def gen_key(length):
    key = ""
    for x in range(0,length):
        char = chr(random.randint(65,90))
        key += char
    return key
        
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
c, addr = s.accept()
tkey = gen_key(16)
skey = Cube(key).encrypt(tkey)
c.send(skey)
key = tkey
threading.Thread(target=recv_thread, args=(c,)).start()
while True:
    msg = raw_input()
    if msg == "EXIT":
        break
    ctext = Cube(key).encrypt(msg)
    c.send(ctext)
s.close()
