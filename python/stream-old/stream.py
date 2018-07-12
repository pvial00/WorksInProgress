import sys, socket, time
import threading

users = { 'user1':'abc123', 'bozo':'password' }
host = "0.0.0.0"
port = 31234
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
user = ""

global stream
global general
global tech
global logged_in_users
#logged_in_users = { 'admin':'admin' }
stream = "admin: Welcome to Stream Chat!\n"
tech = "admin: Welcome to Tech Chat!\n"
general = "admin: Welcome to General Chat!\n"

def validate_creds(user,passw):
	token = 0
	try:
		if passw == users[user]:
			token = 1
		else:
			token = 0
	except KeyError as ker:
		print ker
		
	return token

def get_recent(room):
	global stream
	global tech
	global general
	recent = ""
	if room == "1":
		stream_length = len(general.split('\n'))
		num_lines_to_display = 28
		if stream_length < 28:
			recent = general + "\n"

		elif stream_length >= 28:
			for line in reversed(range(0,num_lines_to_display)):
				position = stream_length - line
				recent = recent + general.split('\n')[position - 1] + "\n"
	elif room == "2":
		stream_length = len(tech.split('\n'))
		num_lines_to_display = 28
		if stream_length < 28:
			recent = tech + "\n"

		elif stream_length >= 28:
			for line in reversed(range(0,num_lines_to_display)):
				position = stream_length - line
				recent = recent + tech.split('\n')[position - 1] + "\n"
	elif room == "3":
		stream_length = len(stream.split('\n'))
		num_lines_to_display = 28
		if stream_length < 28:
			recent = stream + "\n"

		elif stream_length >= 28:
			for line in reversed(range(0,num_lines_to_display)):
				position = stream_length - line
				recent = recent + stream.split('\n')[position - 1] + "\n"
	return recent

def append_msg(user, msg, room):
	global stream
	global tech
	global general
	if room == "1":
		general = general + user + ": " + msg + "\n"
	elif room == "2":
		tech = tech + user + ": " + msg + "\n"
	elif room == "3":
		stream = stream + user + ": " + msg + "\n"
	

def client_stream(c, user, room):
	response = ""
	global stream
	global general
	global tech
	myroom = room
	while True:
		try:
			msg = c.recv(1024)
		except ValueError as ver:
			print ver
		msg = msg.rstrip("\r\n")
		if msg == "\r\n":
			continue
		elif msg == "\n":
			continue
		elif msg == "exit":
			break
		elif msg == "leave":
			main_menu(c, user)
		elif msg == "refresh":
			response = get_recent(myroom)
			response = response + "Post a msg: "
			c.send(response)
		else:
			if msg != "":
				append_msg(user, msg, myroom)
			response = get_recent(myroom)
			response = response + "Post a msg: "
			c.send(response)
	c.close()

def main_menu(c, user):
		banner = "Welcome to Stream Chat!\nType: \"refresh\" to refresh the chat stream\nType \"leave\" to leave a room\nType \"exit\" to logout completely\n"
		banner = banner + "Please select a room to join\nType \"1\" for General Chat\nType \"2\" for Tech Chat\nType \"3\" for Stream Chat\nEnter a room number to join: "
		try:
			c.send(banner)
			room = c.recv(2)
			room = room.rstrip('\r\n')
		except socket.error:
			print("Error: continuing")
		client_stream(c, user, room)
		
def server_menu(c):
		banner = "Welcome to Stream Chat!\nType: \"refresh\" to refresh the chat stream\nType \"leave\" to leave a room\nType \"exit\" to logout completely\n"
		banner = banner + "Please select a room to join\nType \"1\" for General Chat\nType \"2\" for Tech Chat\nType \"3\" for Stream Chat\nEnter a room number to join: "
		try:
			c.send(banner)
			room = c.recv(2)
			room = room.rstrip('\r\n')
		except socket.error:
			print("Error: continuing")

		client_handle = threading.Thread(target=client_stream, args=(c, user, room,)).start()
	
while True:
	c, addr = s.accept()
	loginprompt = "login: "
	try:
		c.send(loginprompt)
	except socket.error as login_error:
		print login_error
	user = c.recv(64)
	passwordprompt = "password: "
	try:
		c.send(passwordprompt)
	except socket.error:
		print("Error: continuing")

	passw = c.recv(64)
	user = user.rstrip('\r\n')
	passw = passw.rstrip('\r\n')
	token = validate_creds(user,passw)
	if token == 0:
		c.close()
		continue
	elif token == 1:
		server_menu(c)
