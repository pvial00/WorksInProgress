import os, signal
import socket, random
import subprocess, threading, pam
from multiprocessing import Process
from time import sleep
import pwd

host = "0.0.0.0"
port = 6968
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
c = ""

keys = { 'xB3s00':'aweakkey12', 'G393s2':'anotherweak' }
user_ids = { 'xB3s00':'user1', 'Ge93s2':'bozo' }

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

def gen_serverok():
	server_ok = ""
	for s in range(0,2):
		rnd_char = chr(random.randint(0,127))
		server_ok = server_ok + rnd_char
	return server_ok
	

def shutdown_recv(rhost, rport):
	rs.close = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	rsclose.connect((rhost, rport))
	rsclose.close()

def shutdown_send(shost, sport):
	ssclose = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ssclose.connect((shost, sport))
	ssclose.close()

def shutdown_server(c, s):
	try:
		c.close()
	except AttributeError as aer:
		print aer
	s.close()
	exit(0)

def signal_handler(signal, frame):
	try:
		if send_thread.isAlive():
			shutdown_send(shost, sport)
	except NameError as ner:
		print ner
	try:
		if recv_thread.isAlive():
			shutdown_recv(rhost, rport)
	except NameError as ner:
		print ner
	shutdown_server(c, s)

def recv_server(rhost, rport, rpath):
	rpath = rpath.rstrip('\n')
	try:
		recv_file = open(rpath, "w")
	except IOError as rerr:
		print rerr
        rs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       	rs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       	rs.bind((rhost, rport))
       	rs.listen(1)
        rc, raddr = rs.accept()
        while True:
		rdata = rc.recv(8192)
		if not rdata: break
		recv_file.write(rdata)
	recv_file.close()
	rc.close()
	rs.close()

def send_server(shost, sport, spath):
	spath = spath.rstrip('\n')
	try:
		send_file = open(spath, "r")
	except IOError as serr:
		print serr
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       	ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       	ss.bind((shost, sport))
       	ss.listen(1)
        sc, saddr = ss.accept()
        for line in send_file.readlines():
			sc.send(line)
	send_file.close()
	sc.close()
	ss.close()

def server(s, c):
	key_id = ""
	while True:
		c, addr = s.accept()
		try:
			key_id = c.recv(64)
		except socket.error as init_error:
			print init_error
		if key_id in user_ids:
			key = keys[key_id]
			auth_challenge, transit_key = gen_challenge()
			auth_challenge = krypt(auth_challenge, transit_key)
			krypto_pkt = gen_krypto_pkt(auth_challenge, transit_key)
			krypto_pkt = krypt(krypto_pkt, key)
			c.send(krypto_pkt)
			krypto_auth_response = c.recv(108)
			auth_response = krypt(krypto_auth_response, transit_key)
			gatekey = auth_challenge + key_id
			if  auth_response != gatekey:
				continue
			else:
				login_prompt = "login: "
				password_prompt = "password: "
				login_prompt = krypt(login_prompt, transit_key)
				c.send(login_prompt)
				user = c.recv(64)
				user = krypt(user, transit_key)
				user = user.rstrip("\n")
				password_prompt = "password: "
				password_prompt = krypt(password_prompt, transit_key)
				c.send(password_prompt)
				password = c.recv(64)
				password = krypt(password, transit_key)
				password = password.rstrip("\n")
				p = pam.pam()
				if p.authenticate(user, password):
					server_ok = gen_serverok()
					c.send(server_ok)
					Process(target=client_handler, args=(c, user, transit_key,)).start()
				else:
					c.close()

def client_handler(c, user, transit_key):
	pw_stuff = pwd.getpwnam(user)
	uid = pw_stuff.pw_uid
	gid = pw_stuff.pw_gid
	home = pw_stuff.pw_dir
	os.setgid(gid)
	os.setuid(uid)
	os.chdir(home)
	while True:
		command = c.recv(128)
		rcmand = krypt(command, transit_key)
		if rcmand == "":
			break
		elif "syphonr" in rcmand:
			opts = rcmand.split(" ")
			try:
				rpath = opts.pop()
				rport = opts.pop()
				rhost = opts.pop()
			except IndexError as ier:
				print ier
			try:
				rport = int(rport)
			except ValueError as ver:
				print ver
			if 'rpath' in locals() and 'rport' in locals() and 'rhost' in locals():
				recv_thread = threading.Thread(target=recv_server, args=(rhost, rport, rpath,))	
				recv_thread.daemon = True
				recv_thread.start()
				c.send("Syphon receive server started successfully\n")
				rcmand = ""
		elif "syphons" in rcmand:
			opts = rcmand.split(" ")
			try:
				spath = opts.pop()
				sport = opts.pop()
				shost = opts.pop()
			except IndexError as ier:
				print ier
			try:
				sport = int(sport)
			except ValueError as ver:
				print ver
			if 'spath' in locals() and 'sport' in locals() and 'shost' in locals():
				send_thread = threading.Thread(target=send_server, args=(shost, sport, spath,))
				send_thread.daemon = True
				send_thread.start()
				c.send("Syphon send server started successfully\n")
				rcmand = ""
		elif rcmand == "exit":
			if 'spath' in locals() and 'sport' in locals() and 'shost' in locals():
				shutdown_send(ss, shost, sport)
			if 'rpath' in locals() and 'rport' in locals() and 'rhost' in locals():
				shutdown_recv(rs, rhost, rport)
				shutdown_server(c, s)
			exit(0)
		else:
			try:
				output = subprocess.check_output(rcmand, stderr=subprocess.STDOUT, shell=True)
			except subprocess.CalledProcessError:
				rcmand_error = "Command not found or error"
				rcmand_error = krypt(rcmand_error, transit_key)
				c.send(rcmand_error)
			else:
				krypted_output = krypt(output, transit_key)
               			c.send(krypted_output)
	c.close()

signal.signal(signal.SIGINT, signal_handler)

server(s, c)
