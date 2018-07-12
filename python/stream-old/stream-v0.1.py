import sys, socket, time
import threading

users = { 'user1':'abc123', 'bozo':'password' }
host = "0.0.0.0"
port = 1234
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
user = ""
status = 1

stream = ""

def validate_creds(user,passw):
	if passw == users[user]:
		token = 1
	else:
		token = 0
	return token

def logc(cmand):
        newl = "\n"
        file = open('logfile', 'a')
        stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cmand = "Command logged at %s: " % stamp + cmand + newl
        file.write(cmand)
        file.close
        return
	
while True:
	c, addr = s.accept()
	loginprompt = "login: "
	c.send(loginprompt)
	user = c.recv(64)
	passwordprompt = "password: "
	c.send(passwordprompt)
	passw = c.recv(64)
	user = user.rstrip('\r\n')
	passw = passw.rstrip('\r\n')
	token = validate_creds(user,passw)
	if token == 0:
		c.close()
		continue
	elif token == 1:
		c.send("Post a msg: ")
		while True:
			msg = c.recv(1024)
			msg = msg.rstrip("\r\n")
			if msg == "exit": break
			stream = stream + user + ": " + msg + "\n"
			response = stream + "Post a msg : "
			c.send(response)
			
	c.close()
		
