import sys, socket, signal
import getpass

key = "aweakkey12"
client_hello = "pvial"

def signal_handler(signal, frame):
	try:
		s.close()
	except socket.error as ser:
		print "Quitting"
	sys.exit(0)

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

host = sys.argv[1]
port = int(sys.argv[2])
signal.signal(signal.SIGINT, signal_handler)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.send(client_hello)
server_response = s.recv(42)
krypt_pkt = krypt(server_response, key)
krypt_pkt, transit_key = server_handshake(krypt_pkt)
auth_response = krypt(krypt_pkt, transit_key)
auth_response = auth_response + client_hello
krypto_response = krypt(auth_response, transit_key)
s.send(krypto_response)

password = ""
login_prompt = s.recv(16)
login_prompt = krypt(login_prompt, transit_key)
sys.stdout.write(login_prompt)
login = raw_input()
login = krypt(login, transit_key)
s.send(login)
password_prompt = s.recv(16)
password_prompt = krypt(password_prompt, transit_key)
sys.stdout.write(password_prompt)
password = getpass.getpass(password)
password = krypt(password, transit_key)
s.send(password)
menu = s.recv(2048)
menu = krypt(menu, transit_key)
sys.stdout.write(menu)
room = raw_input()
room = krypt(room, transit_key)
s.send(room)
while True:
	msg = s.recv(2048)
	msg = krypt(msg, transit_key)
	sys.stdout.write(msg)
	msg = raw_input()
	if msg == "exit":
		msg = krypt(msg, transit_key)
		s.send(msg)
		break
	msg = krypt(msg, transit_key)
	s.send(msg)
			
s.close()
