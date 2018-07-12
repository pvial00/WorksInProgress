from twofish import Twofish
import hashlib, sys, os, time
from binascii import hexlify
from getpass import getpass

salt = b'0101010169696969'
mode = sys.argv[1]
infile = sys.argv[2]
outfile = sys.argv[3]
try:
	key = sys.argv[4]
except NameError as ker:
	key = getpass("Enter key: ")
	if len(key) < 8:
		print "Error: Key length must be at least 8 characters long"
		sys.exit(1)

def hash_key(key, salt):
	sub_key = hashlib.pbkdf2_hmac('sha256', key, salt, 100000, 8)
	return sub_key

def twofish_encrypt(data, key):
	Tcipher = Twofish(key)
	cipher_text = Tcipher.encrypt(data)
	return cipher_text

def twofish_decrypt(data, key):
	Tcipher = Twofish(key)
	plain_text = Tcipher.decrypt(data)
	return plain_text

def pkcs7_pad(block):
	pad_char = chr(4)
	for p in range(0,(16 - len(block))):
		block += pad_char
	return block

def pkcs7_unpad(block):
	pad_char = chr(4)
	pad_block = ""
	pad_count = block.count(pad_char)
	for p in range(0,(16 - pad_count)):
		pad_block += block[p]
	return pad_block

def cbc_mode(block, last_block):
    cbc_block = ""
    for x in range(0,len(block)):
            byte = ord(block[x]) ^ ord(last_block[x])
            cbc_block += chr(byte)
    return cbc_block


try:
	in_fd = open(infile, "r")
except IOError as ier:
	print "Error: Could not open input file"
	sys.exit(1)

try:
	out_fd = open(outfile, "w")
except IOError as oer:
	print "Error: Could not open output file"
	sys.exit(1)
byte_count = 0
start_time = time.time()
sub_key = hexlify(hash_key(key, salt))
last_block_q = ['6969696969696969']
if mode == "encrypt":
	while True:
		Pblock = in_fd.read(16)
		byte_count += len(Pblock)
		if Pblock == "":
			break
		elif len(Pblock) < 16:
			Pblock = pkcs7_pad(Pblock)
                last_block = last_block_q.pop()
                cbc_block = cbc_mode(Pblock, last_block)
		cipher_text = twofish_encrypt(cbc_block, sub_key)
                last_block_q.append(cipher_text)
		out_fd.write(cipher_text)

elif mode == "decrypt":
	while True:
		Cblock = in_fd.read(16)
		byte_count += len(Cblock)
		if Cblock == "":
			break
                last_block = last_block_q.pop()
                last_block_q.append(Cblock)
		plain_text = twofish_decrypt(Cblock, sub_key)
                cbc_block = cbc_mode(plain_text, last_block)
		plain_text = pkcs7_unpad(cbc_block)
		out_fd.write(plain_text)

total_time = time.time() - start_time
print "ZanderFish: " + str(byte_count) + " bytes processed in " + str(total_time) + " seconds."
in_fd.close()
out_fd.close()
