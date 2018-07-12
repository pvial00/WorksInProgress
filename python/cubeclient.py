from pycube import Cube
import socket, threading, select, sys

host = "localhost"
port = 62666
key = "NEVERSAYNEVERAGAIN"

def recv_thread(s):
    sockets = []
    sockets.append(s)
    while sockets:
        readable, writable, errable = select.select(sockets, sockets, sockets)
        for r in readable:
            buf = r.recv(2048)
            buf = Cube(key).decrypt(buf)
            sys.stdout.write(buf+"\n")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
skey = s.recv(16)
tkey = Cube(key).decrypt(skey)
key = tkey
threading.Thread(target=recv_thread, args=(s,)).start()
while True:
    msg = raw_input()
    if msg == "EXIT":
	break
    ctext = Cube(key).encrypt(msg)
    s.send(ctext)
s.close()
