import socket

host = "10.0.2.15"
port = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(10)
shutdown = 0

def main():
	cport = 80
	client = ""
	while shutdown != 1:
		newpayload = ""
		c, addr = s.accept()
		payload = c.recv(1024)
		print payload
		if len(payload) != 0:
			cnt = 0
			for line in payload.splitlines():
				if "Host:" in line:
					hostinfo = line.split(" ")
					client = hostinfo.pop()
					client = socket.gethostbyname(client)
				if "User-Agent:" in line:
					line = "User-Agent: hax0r"
				if newpayload == "":
					newpayload = newpayload + line
				else:
					newpayload = newpayload + "\r\n" + line
		newpayload = newpayload + "\r\n"
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((client, cport))
		client_socket.send(newpayload)
		if len(payload) != 0:
			cpayload = client_socket.recv(16384)
			c.send(cpayload)
		try:
			c.shutdown(1)
		except socket.error as ser:
			print "Socket error, continuing"
			continue
		c.close()
		client_socket.shutdown(1)
		client_socket.close()

main()
