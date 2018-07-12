import sys, time, random, getopt
from getpass import getpass

def gen_session_key(session_key_length):
	session_key = ""
	for key in range(0,session_key_length):
		session_key = session_key + chr(random.randint(0,127))
	return session_key

def enkrypt(text, key):
	crypt_text = ""
	for x in range(0,len(text)):
		byte = text[x]
		primary_round = ord(byte)
		for y in range(0,len(key)):
			primary_round = primary_round ^ ord(key[y])
			primary_round = primary_round >> 4
		crypt_text = crypt_text + chr(primary_round)
	return crypt_text

def dekrypt(text, key):
	plain_text = ""
	for x in range(0,len(text)):
		byte = text[x]
		primary_round = ord(byte)
		for y in range(0,len(key)):
			primary_round = primary_round << 4
			primary_round = primary_round ^ ord(key[y])
		plaint_text = plain_text + chr(primary_round)
	return plain_text

def krypto_pack(plain_text, key):
	session_key = gen_session_key(session_key_length)
	krypt_pkt = enkrypt(plain_text, session_key)
	krypt_pkt = session_key + krypt_pkt
	krypt_pkt = enkrypt(krypt_pkt, key)
	return krypt_pkt

def krypto_unpack(cipher_text, key):
	plain_text = ""
	session_key = ""
	second_stage = ""
	first_stage = dekrypt(cipher_text, key)
	first_stage_len = len(cipher_text)
	for x in range(0,session_key_length):
		session_key = session_key + first_stage[x]
	for x in range(session_key_length,first_stage_len):
		second_stage = second_stage + first_stage[x]
	plain_text = dekrypt(second_stage, session_key)
	return plain_text

argv = sys.argv[1:]
try:
        opts, args = getopt.getopt(argv, "h:", ['encrypt', 'decrypt', 'infile=', 'outfile=', 'key=','genkey'])
except getopt.GetoptError as geter:
        print geter

try:
        for opt, arg in opts:
                if '--encrypt' in opt:
			mode = 0
                elif '--decrypt' in opt:
                        mode = 1
                elif '--infile' in opt:
                        in_file = arg
                elif '--outfile' in opt:
                        out_file = arg
                elif '--key' in opt:
                        key = arg
except NameError as ner:
	print ner

try:
	infile = open(in_file, "r")
except NameError as ner:
	print "Unable to open infile"
	sys.exit(0)

try:
	outfile = open(out_file, "w")
except NameError as ner:
	print "Unable to open outfile"
	sys.exit(0)

try:
	key
except NameError:
	key = getpass("key: ")

data = infile.read()
session_key_length =  16 # 16 for 128 bit, 32 for 256 bit, 128 for 1024 bit, 256 for 2048

start_time = time.time()
if mode == 0:
	cipher_text = krypto_pack(data, key)
	outfile.write(cipher_text)
elif mode == 1:
	plain_text = krypto_unpack(data, key)
	outfile.write(plain_text)

end_time = time.time() - start_time
print "Completed in %s seconds" % end_time
infile.close()
outfile.close()
