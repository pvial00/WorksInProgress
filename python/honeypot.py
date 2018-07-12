import sys, socket, time, os
import threading

users = { 'admin':'admin', 'bozo':'password' }
host = "0.0.0.0"
port = 23
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
user = ""
status = 1

def validate_creds(user,passw):
	if passw == users[user]:
		token = 1
	else:
		token = 0
	return token

def logc(cmand, addr):
        newl = "\n"
        file = open('logfile', 'a')
        stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cmand = "Command from " + str(addr) + " logged at %s: " % stamp + cmand + newl
        file.write(cmand)
        file.close
        return

def command_processor(cmand):
	if cmand == "ls":
		response = "bin   dev   initrd.img   lib64   mnt   root   snap   sys var\nboot  etc  initrd.img.old  lost+found  opt  run  srv  tmp  vmlinuz\nhome  lib  media  proc  sbin  swap  usr  vmlinuz.old\n#"
	elif "pwd" in cmand:
		response = "/\n#"
	elif "whoami" in cmand:
		response = "root\n#"
	elif cmand == "uname -a\n#":
		response = "Linux thrash 6.6.6-1016-Azure #25-RedHat SMP Thu Apr 20 11:34:35 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux\n#"
	elif "cd" in cmand:
		response = "#"
	else:
		response = "Error: File or command not found\n#"
	return response
		
def thepot(c, addr):
	os.setuid(13)
	os.setuid(13)
	#os.chroot("/tmp/pot")
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
	elif token == 1:
		c.send("#")
		while True:
			msg = c.recv(1024)
			#logc(msg, addr)
			msg = msg.rstrip("\r\n")
			if msg == "exit": break
			response = command_processor(msg)
			c.send(response)
	c.close()
		
while True:
	c, addr = s.accept()
	threading.Thread(target=thepot, args=(c,addr)).start()
