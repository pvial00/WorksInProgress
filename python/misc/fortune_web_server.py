import sys, socket, subprocess, os, datetime
import threading

def fortune_teller(c):
	output = subprocess.Popen('fortune', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	fortune = "HTTP/1.1 200 OK\n\n"
	fortune = fortune + output.stdout.read()
	c.send(fortune)
	c.close()

host = "0.0.0.0"
port = 34567
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
user = ""
status = 1

stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

while True:
	c, addr = s.accept()
	get = c.recv(1024)
	threading.Thread(target=fortune_teller, args=(c,)).start()
