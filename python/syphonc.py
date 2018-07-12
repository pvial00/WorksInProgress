import sys, socket, getpass, select

host = sys.argv[1]
port = sys.argv[2]
key = "aweakkey12"
client_hello = "xB3s00"

def krypt(text, key):
	krypt_buffer = ""
	for x in reversed(range(0,len(text))):
		byte = text[x]
		primary_round = ord(byte)
		for y in range(0,len(key)):
			primary_round = primary_round ^ ord(key[y])
		primary_round = chr(primary_round)
		krypt_buffer = krypt_buffer + primary_round
	return krypt_buffer

def server_handshake(data):
        krypt_response = ""
        transit_key = ""
        for x in range(0,32):
                krypt_response = krypt_response + data[x]
        for x in range(32,42):
                transit_key =  transit_key + data[x]
        return krypt_response, transit_key

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket()
s.connect((host, port))
s.send(client_hello)
server_response = s.recv(42)
krypt_pkt = krypt(server_response, key)
krypt_pkt, transit_key = server_handshake(krypt_pkt)
auth_response = krypt(krypt_pkt, transit_key)
auth_response = auth_response + client_hello
krypto_response = krypt(auth_response, transit_key)
s.send(krypto_response)
login_prompt = s.recv(16)
login_prompt = krypt(login_prompt, transit_key)
sys.stdout.write(login_prompt)
login = raw_input()
login = krypt(login, transit_key)
s.send(login)
password_prompt = s.recv(16)
password_prompt = krypt(password_prompt, transit_key)
sys.stdout.write(password_prompt)
password = getpass.getpass("")
password = krypt(password, transit_key)
s.send(password)
auth_token = s.recv(2)

if len(auth_token) == 2:
	while True:
		cmand = raw_input("*#")
		if cmand == "\n":
			cmand = "dmesg"
		krypt_pkt = krypt(cmand, transit_key)
		s.send(krypt_pkt)
		if cmand == "exit": break
		while True:
			try:
				data_check = select.select([s], [], [], 2)
			except IOError as cer:
				pass
			if data_check[0]:
				try:
					cmand_out = s.recv(1024)
				except socket.error as recv_err:
					pass
			cmand_out = krypt(cmand_out, transit_key)
			sys.stdout.write(cmand_out)
			if not cmand_out: break
			if cmand_out == "": break
			if cmand_out == "\n": break
			cmand_out = ""
	s.close()
