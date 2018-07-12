import socket, threading, select
import os, time

host = "0.0.0.0"
port = 80
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(10000)
global node
node = 1

def rotatepool(pool):
	global node
	nodecount = len(pool.keys())
	client = "null"
	for member in sorted(pool.keys()):
		if node == int(member):
			client = pool[str(member)]
	if node != nodecount:
		node = node + 1
	else:
		node = 1
	return client, node

def main():
	while True:
		pool = {'1':'127.0.0.1', '2':'127.0.0.2', '3':'127.0.0.3'}
		c, addr = s.accept()
		client_handle = threading.Thread(target=client_handler, args=(c,pool)).start()

def client_handler(c, pool):
	os.setuid(33)
	global node
	newpayload = ""
	cport = 80
	payload = c.recv(1024)
	if len(payload) != 0:
		cnt = 0
		for line in payload.splitlines():
			if "User-Agent:" in line:
				line = "User-Agent: hax0r"
			if newpayload == "":
				newpayload = newpayload + line
			else:
				newpayload = newpayload + "\r\n" + line
	newpayload = newpayload + "\r\n"
	client, node = rotatepool(pool)
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((client, cport))
	client_socket.send(newpayload)
	if len(payload) != 0:
		while True:
			data_check = select.select([client_socket], [], [], 2)
			if data_check[0]:
				cpayload = client_socket.recv(8192)
			if not cpayload:
				break
			elif cpayload == "":
				break
			c.send(cpayload)
		
	c.close()
	client_socket.close()

main()
