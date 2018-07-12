from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from base64 import (b64encode, b64decode)
from time import sleep
import sys, socket, threading, select, libnacl.secret, libnacl.utils, libnacl.sealed

port = 64666

def rsa_encrypt(data, public_key):
    srv_safe = libnacl.sealed.SealedBox(public_key)
    cipher_text = srv_safe.encrypt(data)
    return cipher_text

def salsa_encrypt(data, safe):
    try:
        cipher_text = safe.encrypt(data)
    except (ValueError, libnacl.CryptError):
        cipher_text = ""
    return cipher_text

def salsa_decrypt(data, safe):
    try:
        plain_text = safe.decrypt(data)
    except (ValueError, libnacl.CryptError):
        plain_text = ""
    return plain_text

def auth_pkg(user, passw, session_key):
    pkg = user + ":" + passw + ":" + session_key
    print len(user), len(passw), len(session_key)
    return pkg

def gen_session_key():
    session_key = libnacl.utils.salsa_key()
    return session_key

def recv_thread(sock, safe):
    while sock:
        try:
            readable, writable, errable = select.select(sock, sock, sock)
        except socket.error as ser:
            break
        for r in readable:
            response = r.recv(2048)
            response = salsa_decrypt(response, safe)
            gui.write(response)
            
class StreamClient:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.passw = libnacl.crypto_hash(password)
        self.session_key = gen_session_key()
        self.safe = libnacl.secret.SecretBox(self.session_key)
        self.session_pkg = auth_pkg(self.user, self.passw, self.session_key)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_id = "StreamClient"
        self.stream = ""

    def send(self, data):
        buf = self.safe.encrypt(data)
        self.s.send(buf)

    def shutdown(self):
        self.s.close()

    def connect(self):
        try:
            self.s.connect((self.host, self.port))
        except socket.error as ser:
            print "Error: Unable to connect to server, try again."
            sys.exit(1)
        client_id = b64encode(self.client_id)
        try:
            self.s.send(client_id)
        except socket.error as ser:
            print "Error: Unable to connect to server, try again."
            sys.exit(1)

        server_key = self.s.recv(2048)
        server_key = b64decode(server_key)
        session_pkg = auth_pkg(self.user, self.passw, self.session_key)
        self.session_key = ""
        session_pkg = rsa_encrypt(self.session_pkg, server_key)
        self.s.send(session_pkg)
        sockets = []
        sockets.append(self.s)
        menu = self.s.recv(1024)
        if menu != "":
            self.online = True
            menu = salsa_decrypt(menu, self.safe)
            self.stream += menu
            threading.Thread(target=self.recv_thread, args=(sockets, self.safe)).start()
        else:
            self.online = False

    def recv_thread(self, sock, safe):
        while sock:
            try:
                readable, writable, errable = select.select(sock, sock, sock)
            except socket.error as ser:
                break
            for r in readable:
                response = r.recv(2048)
                response = salsa_decrypt(response, safe)
                self.stream += response

class Stream(App):

    def on_text(self, instance, value):
	self.input = value

    def set_key(self, instance, value):
	self.key = value

    def get_user(self, instance, value):
	self.user = value

    def get_pass(self, instance, value):
	self.password = value

    def get_server(self, instance, value):
	self.server = value

    def toascii(self, data):
        tmp = data.decode("utf-8")
        asciidata = tmp.encode("ascii")
        return asciidata

    def send(self, event):
        buffer = self.toascii(self.buffer)
        self.client.send(buffer)
        self.buffer = ""
        self.inputfield.text = ""

    def get_input(self, instance, value):
        self.buffer = value

    def refresh(self, event):
        self.chatwindow.text = self.client.stream

    def login(self, instance):
        user = self.toascii(self.user)
        password = self.toascii(self.password)
	self.client = StreamClient(self.server, 64666, user, password)
	self.client.connect()
	if self.client.online == True:
            self.layout.remove_widget(self.ttitle)
            self.layout.remove_widget(self.srvfield)
            self.layout.remove_widget(self.userfield)
            self.layout.remove_widget(self.passfield)
            self.layout.remove_widget(self.submitbtn)
            self.layout.remove_widget(self.refreshbtn)
	    self.inputfield = TextInput(size_hint=(.5,.5),height='20')
	    self.inputfield.bind(text=self.get_input)
	    self.sendbtn = Button(text='Send',size_hint=(.4,.4))
	    self.sendbtn.bind(on_release=self.send)
            self.layout.add_widget(self.inputfield)
            self.layout.add_widget(self.sendbtn)
            threading.Thread(target=self.recvthread).start()
            #self.layout.add_widget(self.refreshbtn)

    def build(self):
	self.layout = BoxLayout(orientation='vertical')
        self.chat = StringProperty()
        self.chat = ""
        blue = (0, 0, 1.5, 2.5)
	self.ttitle = Label(text='StreamChat Login', valign='top', halign='center', font_size='12sp',)
        self.chatwindow = Label(text=self.chat, valign='top', halign='center', font_size='12sp', max_lines=28)
	self.srvfield = TextInput(size_hint=(.5, .3), height='30')
	self.srvfield.bind(text=self.get_server)
	self.userfield = TextInput(size_hint=(.5, .3), height='30')
	self.userfield.bind(text=self.get_user)
	self.passfield = TextInput(password=True, size_hint=(.5, .3), height='30')
	self.passfield.bind(text=self.get_pass)
	self.submitbtn = Button(text='Login', background_color=blue,size_hint=(.8,.8))
	self.submitbtn.bind(on_release=self.login)
	self.refreshbtn = Button(text='Refresh', background_color=blue,size_hint=(.8, .8), valign='bottom')
	self.refreshbtn.bind(on_release=self.refresh)
	self.layout.add_widget(self.ttitle)
        self.layout.add_widget(self.chatwindow)
	self.layout.add_widget(self.srvfield)
        self.layout.add_widget(self.userfield)
	self.layout.add_widget(self.passfield)
	self.layout.add_widget(self.submitbtn)
	self.layout.add_widget(self.refreshbtn)
	return self.layout

    def recvthread(self):
        sock = []
        sock.append(self.client.s)
        while sock:
            try:
                readable, writable, errable = select.select(sock, sock, sock)
            except socket.error as ser:
                break
            for r in readable:
                response = r.recv(2048)
                response = salsa_decrypt(response, self.client.safe)
                self.chatwindow.text = response

if __name__ == '__main__':
    Stream().run()
