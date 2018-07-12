import sys, socket
import getpass

host = sys.argv[1]
port = int(sys.argv[2])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

password = ""
login_prompt = s.recv(16)
sys.stdout.write(login_prompt)
login = raw_input()
s.send(login)
password_prompt = s.recv(16)
sys.stdout.write(password_prompt)
password = getpass.getpass(password)
s.send(password)
while True:
	msg = s.recv(2048)
	sys.stdout.write(msg)
	msg = raw_input()
	s.send(msg)
	if msg == "exit": break
			
s.close()
