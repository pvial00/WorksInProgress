import socket, threading, select
import os, time

host = "0.0.0.0"
port = 80
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(10000)
offline = { }
lb_pool = []
master_pool = {'1':'10.9.9.1', '2':'10.9.9.2', '3':'10.9.9.3'}

def health_check():
	global offline
	global master_pool
	while True:
		if len(offline.keys()) > 0:
			for member in sorted(offline.keys()):
				respone = ""
				server = offline[str(member)]
				getstring = "GET /index.html HTTP/1.1\nhost: %s\n\n" % server
				sport = 80
				health_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				try:
					health_socket.connect((server, sport))
					health_socket.send(getstring)
					response = health_socket.recv(512)
				except socket.error as er:
					health_status = 0
				else:
					line = ""
					for line in response.splitlines():
						if "HTTP/1.1 200 OK" in line:
							health_status = 1
							master_pool[str(member)] = server
							del offline[str(member)]
						else:
							health_status = 0
						break
		num_members = len(master_pool.keys())
		for member in sorted(master_pool.keys()):
			response = ""
			server = master_pool[str(member)]
			getstring = "GET /index.html HTTP/1.1\nhost: %s\n\n" % server
			sport = 80
			health_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				health_socket.connect((server, sport))
				health_socket.send(getstring)
				response = health_socket.recv(512)
			except socket.error as er:
				health_status = 0
				del master_pool[str(member)]
				offline[member] = server
			else:
				line = ""
				for line in response.splitlines():
					if "HTTP/1.1 200 OK" in line:
						health_status = 1
					else:
						health_status = 0
						del master_pool[str(member)]
						offline[member] = server
					break
			time.sleep(2)
			health_socket.close()

def rotatepool():
	global master_pool
	global lb_pool
	client = "null"
	nodecount = len(lb_pool)
	master_pool_count = len(master_pool)
	if (nodecount == 0):
		for member in reversed(sorted(master_pool.keys())):
			lb_pool.append(master_pool[str(member)])
	if master_pool_count > 0:
		client = lb_pool.pop()
	return client

def main():
	while True:
		c, addr = s.accept()
		client_handle = threading.Thread(target=client_handler, args=(c,)).start()

def client_handler(c):
	os.setuid(33)
	global master_pool
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
	client = rotatepool()
	if client != "null":
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			client_socket.connect((client, cport))
			client_socket.send(newpayload)
		except socket.error as csock_err:
			c.send("Error: 500 No Server available")
			c.close()
		else:
			if len(payload) != 0:
				while True:
					try:
						data_check = select.select([client_socket], [], [], 2)
					except IOError as sel_err:
						pass
					if data_check[0]:
						try:
							cpayload = client_socket.recv(8192)
						except socket.error as recv_err:
							pass
					if not cpayload:
						break
					elif cpayload == "":
						break
			#if not cpayload: break
			#returnpayload = ""
			#if "Content-Length:"
			#       if "HTTP/1.1" in line:
					#line = line + "\r\nServer_ID: 66"
                        #               print line
                        #       if "<html>" in line:
                        #               line = "\r" + line
                        #       if returnpayload == "":
                        #               returnpayload = returnpayload + line
                        #       else:
                        #               returnpayload = returnpayload + "\r\n" + line

                        #returnpayload = returnpayload
					try:
						c.send(cpayload)
					except socket.error as send_err:
						pass
		
				c.close()
				client_socket.close()
	else:
		srv_unavailable = "HTTP 1.1 503 No Server Available\n"
		c.send(srv_unavailable)
		c.close()

health_thread = threading.Thread(target=health_check).start()
main()
