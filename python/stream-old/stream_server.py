import sys, socket, time
import threading, random

users = { 'user1':'abc123', 'bozo':'password' }
keys = { 'user1':'aweakkey12', 'bozo':'anotherweak' }
host = "0.0.0.0"
port = 64666
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

def krypt(text, key):
	krypt_buffer = ""
	for x in reversed(range(0,len(text))):
		byte = text[x]
		primary_round = ord(byte)
		for y in range(0,len(key)):
			primary_round = primary_round ^ ord(key[y])
		primary_round = chr(primary_round)
		krypt_buffer = krypt_buffer + primary_round
	return krypt_buffer

def gen_challenge():
	auth_challenge = ""
	transit_key = ""
	challenge_length = 32
	transit_key_length = 10
	for n in range(0,challenge_length):
		rnd_char = chr(random.randint(0,127))
		auth_challenge = auth_challenge + rnd_char
	for n in range(0,transit_key_length):
		transit_key = transit_key + chr(random.randint(0,127))
	return auth_challenge, transit_key

def gen_krypto_pkt(auth_challenge, transit_key):
	krypt_pkt = krypt(auth_challenge, transit_key)
	krypt_pkt = krypt_pkt + transit_key
	return krypt_pkt

def validate_key_index(key_index):
	if key_index in keys:
		first_stage_key = keys[key_index]
		first_stage_key_index = key_index
		first_stage_token = 1
	else:
		first_stage_token = 0
		first_stage_key = "null"
		first_stage_key_index = "null"
	return first_stage_token, first_stage_key, first_stage_key_index

def client_stream(c, user, room, transit_key):
	response = ""
	global stream
	global general
	global tech
	myroom = room
	response = get_recent(myroom)
	response = response + "Post a msg: "
	response = krypt(response, transit_key)
	c.send(response)
	while True:
		try:
			msg = c.recv(1024)
		except ValueError as ver:
			print ver
		msg = krypt(msg, transit_key)
		msg = msg.rstrip("\r\n")
		if msg == "\r\n":
			continue
		elif msg == "\n":
			continue
		elif msg == "exit":
			break
		elif msg == "leave":
			main_menu(c, user, transit_key)
		elif msg == "refresh":
			response = get_recent(myroom)
			response = response + "Post a msg: "
			response = krypt(response, transit_key)
			c.send(response)
		else:
			if msg != "":
				append_msg(user, msg, myroom)
			response = get_recent(myroom)
			response = response + "Post a msg: "
			response = krypt(response, transit_key)
			c.send(response)
	c.close()

def main_menu(c, user, transit_key):
		banner = "Welcome to Stream Chat!\nType: \"refresh\" to refresh the chat stream\nType \"exit\" to logout\n"
		banner = banner + "Please select a room to join\nType \"1\" for General Chat\nType \"2\" for Tech Chat\nType \"3\" for Stream Chat\nEnter a room number to join: "
		banner = krypt(banner, transit_key)
		try:
			c.send(banner)
			room = c.recv(2)
		except socket.error:
			print("Error: continuing")
		room = krypt(room, transit_key)
		room = room.rstrip('\r\n')
		client_stream(c, user, room, transit_key)
		
def server_menu(c, transit_key):
		banner = "Welcome to Stream Chat!\nType: \"refresh\" to refresh the chat stream\nType \"exit\" to logout\n"
		banner = banner + "Please select a room to join\nType \"1\" for General Chat\nType \"2\" for Tech Chat\nType \"3\" for Stream Chat\nEnter a room number to join: "
		banner = krypt(banner, transit_key)
		try:
			c.send(banner)
			room = c.recv(2)
		except socket.error:
			print("Error: continuing")
		room = krypt(room, transit_key)
		room = room.rstrip('\r\n')

		client_handle = threading.Thread(target=client_stream, args=(c, user, room, transit_key,)).start()
	
while True:
	c, addr = s.accept()
	first_stage_token = 0
	first_stage_user_index = c.recv(32)
	first_stage_token, first_stage_key, first_stage_key_index = validate_key_index(first_stage_user_index)
	if first_stage_token == 1:
		auth_challenge, transit_key = gen_challenge()
		auth_challenge = krypt(auth_challenge, transit_key)
		krypto_pkt = gen_krypto_pkt(auth_challenge, transit_key)
		krypto_pkt = krypt(krypto_pkt, first_stage_key)
		c.send(krypto_pkt)
		krypto_auth_response = c.recv(108)
		auth_response = krypt(krypto_auth_response, transit_key)
		gatekey = auth_challenge + first_stage_key_index
		if auth_response == gatekey:
			login_prompt = "login: "
			login_prompt = krypt(login_prompt, transit_key)
			try:
				c.send(login_prompt)
			except socket.error as login_error:
				print login_error
			user = c.recv(64)
			user = krypt(user, transit_key)
			password_prompt = "password: "
			password_prompt = krypt(password_prompt, transit_key)
			try:
				c.send(password_prompt)
			except socket.error:
				print("Error: continuing")

			passw = c.recv(64)
			passw = krypt(passw, transit_key)
			user = user.rstrip('\r\n')
			passw = passw.rstrip('\r\n')
			token = validate_creds(user,passw)
			if token == 0:
				c.close()
				continue
			elif token == 1:
				server_menu(c, transit_key)
