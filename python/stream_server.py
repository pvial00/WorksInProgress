from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random
from binascii import hexlify
from binascii import unhexlify
from base64 import b64encode
from base64 import b64decode
import sys, socket, threading, select, os
import nacl.secret
import nacl.utils

host = "0.0.0.0"
port = 64666
univeral_id = "StreamClient"
stream_contents = "admin: Welcome to Stream Chat!\n"
tech_contents = "admin: Welcome to Tech Chat!\n"
general_contents = "admin: Welcome to General Chat!\n"
dbfile = "stream.db"
passkey = "5%9Bd@3gUi$5KPqS7$TBm9201A35%bB#"
stream_users_online = {}
online_sockets = {}
invites = {}
debug = False

def gen_server_keypair():
    random_gen = Random.new().read
    key = RSA.generate(2048, random_gen)
    private_key = key.exportKey()
    public_key = key.publickey().exportKey()
    return private_key, public_key

def gen_session_key():
    session_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    return session_key

class Room:
    def __init__(self, name, contents, private, reservations):
        master_key = gen_session_key()
        self.safe = nacl.secret.SecretBox(master_key)
        master_key = ""
        self.name = name
        self.contents = contents
        self.contents = self.safe.encrypt(self.contents)
        self.users_online = {}
        self.sockets = {}
        self.private = private
        self.reservations = reservations
        if len(self.reservations) == 2 and self.private == True:
            self.max_users = 2
        else:
            self.max_users = 0

    def write(self, user, msg):
        contents = self.safe.decrypt(self.contents)
        entry = user + ": " + msg
        contents += entry
        contents = trim_room(contents)
        self.contents = self.safe.encrypt(contents)
        for write_user, write_user_obj in self.users_online.iteritems():
            write_socket = self.sockets[write_user_obj.name]
            payload = write_user_obj.safe.encrypt(contents)
            write_socket.send(payload)

    def read(self):
        contents = self.safe.decrypt(self.contents)
        return contents

    def join(self, user, socket):
        if user.name in self.reservations and self.private == True:
            self.users_online[user.name] = user
            self.sockets[user.name] = socket
            self.write("admin", user.name+" has joined the room")
            if debug == True:
                print self.name, self.users_online
                print self.name, self.sockets
        elif self.private == False:
            self.users_online[user.name] = user
            self.sockets[user.name] = socket
            self.write("admin", user.name+" has joined the room")
            if debug == True:
                print self.name, self.users_online
                print self.name, self.sockets
                print StreamServer.private_rooms

    def leave(self, user):
        del self.users_online[user]
        del self.sockets[user]
        self.write("admin", user+" has left the room")
        if debug == True:
            print self.name, self.users_online
            print self.name, self.sockets
            print StreamServer.private_rooms
        if self.private == True and len(self.reservations) == 2 and len(self.users_online) == 0:
            for pos in range(0,len(StreamServer.private_rooms)):
                check = StreamServer.private_rooms.pop(pos)
                if check.name != self.name:
                    StreamServer.private_rooms.insert(pos,check)

class User:
    def __init__(self, name, session_key):
        self.name = name
        self.safe = nacl.secret.SecretBox(session_key)

def rsa_decrypt(data, private_key):
    key_obj = RSA.importKey(private_key)
    cipher = PKCS1_OAEP.new(key_obj)
    plain_text = cipher.decrypt(data)
    return plain_text

def rsa_encrypt(data, public_key):
    key_obj = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(key_obj)
    cipher_text = cipher.encrypt(data)
    return cipher_text

def process_auth_pkg(auth_pkg):
    elements = auth_pkg.split(':')
    user = elements.pop(0)
    passw = elements.pop(0)
    session_key = elements.pop(0)
    return user, passw, session_key

def validate_creds(user,passw):
    token = 0
    passfile = open(dbfile, "r")
    contents = passfile.read()
    passfile.close()
    passbox = nacl.secret.SecretBox(passkey)
    contents = passbox.decrypt(contents)
    entries = contents.split("\n")
    for entry in entries:
        if user in entry:
            auth_items = entry.split(":")
            if passw == auth_items.pop(1):
                token = 1
    return token

def trim_room(contents):
    recent = ""
    num_lines = 50
    stream_length = len(contents.split('\n'))
    if stream_length >= num_lines:
        for line in reversed(range(0,num_lines)):
                position = stream_length - line
                recent += contents.split('\n')[position - 1] + "\n"
    else:
        recent = contents + "\n"
    return recent

def get_roomchat(user, room, socket):
    if room == 1:
        contents = StreamServer.general.read()
        if user not  in StreamServer.general.users_online:
            StreamServer.general.join(user, socket)
    elif room == 2:
        contents = StreamServer.tech.read()
        if user not  in StreamServer.tech.users_online:
            StreamServer.tech.join(user, socket)
    elif room == 3:
        contents = StreamServer.stream.read()
        if user not  in StreamServer.stream.users_online:
            StreamServer.stream.join(user, socket)
    elif room > 10:
        for speakeasy in StreamServer.private_rooms:
            if speakeasy.name == StreamServer.rooms[room]:
                contents = speakeasy.read()
                if user not in speakeasy.users_online:
                    speakeasy.join(user, socket)
    return contents

def leave_room(user, room):
    if room == 1:
        if user in StreamServer.general.users_online:
            StreamServer.general.leave(user)
    elif room == 2:
        if user in StreamServer.tech.users_online:
            StreamServer.tech.leave(user)
    elif room == 3:
        if user in StreamServer.stream.users_online:
            StreamServer.stream.leave(user)
    elif room > 10:
        for speakeasy in StreamServer.private_rooms:
            if user in speakeasy.users_online:
                speakeasy.leave(user)

def append_msg(user, msg, room):
    if room == 1:
        StreamServer.general.write(user, msg)
    elif room == 2:
        StreamServer.tech.write(user, msg)
    elif room == 3:
        StreamServer.stream.write(user, msg)
    elif room > 10:
        for speakeasy in StreamServer.private_rooms:
            if speakeasy.name == StreamServer.rooms[room]:
                speakeasy.write(user, msg)

def main_menu():
    banner = "W31c0m3 t0 StR34m Chat!\nType: \"refresh\" to refresh chat stream\nType \"exit\" to logout\n"
    banner += "Please select a room to join\nType \"1\" for General Chat\nType \"2\" for Tech Chat\nType \"3\" for Stream Chat\nType \"9\" for Private Chats\nEnter a room number to join: "
    return banner

def main_menu_handler(c, user):
    banner = main_menu()
    banner = user.safe.encrypt(banner)
    c.send(banner)
    room = c.recv(1024)
    room = user.safe.decrypt(room)
    room = room.strip('\r\n')
    if room == "exit" or room == "leave":
        if user.name in stream_users_online:
            del stream_users_online[user.name]
        del online_sockets[user.name]
        print "hit"
    else:
        room = int(room)
        if room == 9:
            private_stream(c, user)
        else:
            client_stream(c, user, room)

def gen_roomid():
    room_id = 0
    while room_id <= 10:
        room_id = ord(os.urandom(1))
    return room_id

def private_stream(sock1, user1):
    menu = "Choose a user to invite\n"
    for u, i in stream_users_online.iteritems():
        if u != user1.name:
            menu += u + "\n"
    menu = user1.safe.encrypt(menu)
    sock1.send(menu)
    puser = sock1.recv(64)
    puser = user1.safe.decrypt(puser)
    user2 = stream_users_online[puser]
    sock2 = online_sockets[user2.name]
    invite_msg = user1.name + " has invited you to a private room. Type accept to accept\n"
    room_num = gen_roomid()
    content = "Speakeasy " + str(room_num) + "\n"
    reservations = []
    reservations.append(user1.name)
    reservations.append(user2.name)
    private_room = Room(room_num, content, True, reservations)
    StreamServer.private_rooms.append(private_room)
    StreamServer.rooms[room_num] = room_num
    invites[user2.name] = room_num
    sock2.send(user2.safe.encrypt(invite_msg))
    client_stream(sock1, user1, room_num)
    
def client_stream(c, user, room):
    response = ""
    room_recent = get_roomchat(user, room, c)
    room_recent = user.safe.encrypt(room_recent)
    c.send(room_recent)
    while True:
        try:
            msg = c.recv(2048)
        except ValueError as ver:
            print ver
        msg = user.safe.decrypt(msg)
        msg = msg.rstrip("\r\n")
        if msg == "\r\n":
            continue
        elif msg == "\n":
            continue
        elif msg == "exit":
            leave_room(user.name, room)
            if user.name in stream_users_online:
                del stream_users_online[user.name]
            del online_sockets[user.name]
            break
        elif msg == "leave":
            leave_room(user.name, room)
            main_menu_handler(c, user)
        elif msg == "accept":
            if user.name in invites:
                room = invites[user.name]
                response = get_roomchat(user, room, c)
                response = user.safe.encrypt(response)
                c.send(response)
        elif msg == "refresh":
            response = get_roomchat(user, room, c)
            response = user.safe.encrypt(response)
            c.send(response)
        else:
            if msg != "":
                append_msg(user.name, msg, room)
    c.close()

def auth_handler(c):
    client_id = c.recv(16)
    client_id = b64decode(client_id)
    if client_id == univeral_id:
        c.send(b64encode(StreamServer.public_key))
        session_pkg = c.recv(256)
        session_pkg = rsa_decrypt(session_pkg, StreamServer.safe.decrypt(StreamServer.private_key))
        username, passw, session_key = process_auth_pkg(session_pkg)
        if validate_creds(username,passw) == 1 and username not in stream_users_online and len(session_key) == 32:
            user = User(username, session_key)
            stream_users_online[username] = user
            online_sockets[username] = c
            main_menu_handler(c,user)
        else:
            c.close()
    else:
        c.close()

class Server:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
    key = gen_session_key()
    safe = nacl.secret.SecretBox(key)
    key = ""
    private_rooms = []
    rooms = { 1:'general', 2:'tech', 3:'stream' }
    privatekey, public_key = gen_server_keypair()
    private_key = safe.encrypt(privatekey)
    stream = Room("stream", stream_contents, False, [])
    tech = Room("tech", tech_contents, False, [])
    general = Room("general", general_contents, False, [])

    def listen(self, num):
        self.s.listen(num)
        while True:
            c, addr = self.s.accept()
            threading.Thread(target=auth_handler, args=(c,)).start()
        
StreamServer = Server(host, port)
StreamServer.listen(5)
