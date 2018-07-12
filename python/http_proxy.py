import socket
import httplib

host = "10.0.2.15"
port = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(10)
shutdown = 0

def main():
	cport = 80
	client = ""
	method = ""
	while shutdown != 1:
		throw = 0
		newpayload = ""
		c, addr = s.accept()
		payload = c.recv(1024)
		if len(payload) != 0:
			cnt = 0
			for line in payload.splitlines():
				print line
				if "CONNECT" in line:
					throw = 1
				if "GET" in line:
					getstring = line.split(" ")
					proto = getstring.pop()
					url = getstring.pop()
					if url == "":
						url = "/"
					method = getstring.pop()
				if "Host:" in line:
					if throw == 0:
						hostinfo = line.split(" ")
						client = hostinfo.pop()
						client = socket.gethostbyname(client)
		if throw == 0:
			http_conn = httplib.HTTPConnection(client)
			http_conn.request(method, url)
			response = http_conn.getresponse()
			cpayload = response.read()	
			c.send(cpayload)
		try:
			c.shutdown(1)
		except socket.error as ser:
			print "Socket error, continuing"
			continue
		c.close()

main()
