import sys, socket

host = sys.argv[1]
port = int(sys.argv[2])
key = "notagoodpassword"
client_hello = "38eR@Salk*ieFVSle34lsSf90245dxFs"

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
server_response_code = s.recv(2)

if len(server_response_code) == 2:
	cmand = raw_input("*#")
	krypt_pkt = krypt(cmand, transit_key)
	s.send(krypt_pkt)
	krypt_response = s.recv(8192)
	cmand_out = krypt(krypt_response, transit_key)
	print cmand_out
	s.close()
