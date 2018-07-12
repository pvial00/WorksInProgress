import socket
import sys, getopt
import select, signal
#import threading
#from time import sleep

server = 1
port = 6969
host = "0.0.0.0"
#stoprequest = threading.Event()
rt = ""


def usage():
	print "Server mode usage: knetcat -l <ip address> <port>"
	print "Client mode usage: knetcat <ip address> <port>"

def signal_handler(signal, frame):
	#stoprequest.set()
	#rt.join(stoprequest)
	sys.exit(0)

def serverrun(host, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((host, port))
	s.listen(5)
	if select.select([sys.stdin,],[],[],0.0)[0]:
		c, addr = s.accept()
		for line in sys.stdin.readlines():
			c.send(line)
	else:
		c, addr = s.accept()
		while True:
			data = c.recv(64)
			if not data: break
			sys.stdout.write(data)
	try:
		c.shutdown(1)
	except socket.error as ser:
		print "Socket error, continuing"
	c.close()

def recv_thread(s):
	while not stoprequest.isSet():
		data = s.recv(64)
		sys.stdout.write(data)
		sleep(0.4)

def clientrun(host, port):
	if select.select([sys.stdin,],[],[],0.0)[0]:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s = socket.socket()
		s.connect((host, port))
		for line in sys.stdin.readlines():
			s.send(line)
		s.shutdown(1)
		s.close()
	elif not sys.stdout.isatty():
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s = socket.socket()
		s.connect((host, port))
		while True:
			data = s.recv(64)
			if not data: break
			sys.stdout.write(data)
		s.shutdown(1)
		s.close()
	elif sys.stdout.isatty():
		buf = ""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s = socket.socket()
		s.connect((host, port))
		#rt = threading.Thread(target=recv_thread, args=(s,)).start()
		while True:
			buf = sys.stdin.readline()
			if buf != "":
				s.send(buf)
			while True:
				data = s.recv(1024)
				if not data: break
				
				sys.stdout.write(data)
		s.close()

def main():
	if server == 1:
		serverrun(host, port)
	elif server == 0:
		clientrun(host, port)

argv = sys.argv[1:]
try:
	opts, args = getopt.getopt(argv,"l:h:")
except getopt.GetoptError as geter:
	print geter

if not '-l' in sys.argv[1:]:
	server = 0
try: 
	for opt, arg in opts:
		if opt == '-l':
			server = 1
except NameError as ner:
	print ner
	
if '-h' in sys.argv[1:]:
	usage()
	exit(0)
	
if sys.argv[1:]:
	port = int(sys.argv.pop())
	host = sys.argv.pop()

signal.signal(signal.SIGINT, signal_handler)

main()
