import sys
from binascii import hexlify

input_file = sys.argv[1]
iv = 5
hash = []
in_fd = open(input_file, "r")

data = in_fd.read()

def init_hash(hash, iv):
	for x in range(0,16):
		hash.append(iv)
	return hash

def hash_round(data, hash):
	for x in range(0,len(data)):
		hash_byte = hash.pop()
		hash_byte = hash_byte ^ ord(data[x])
		hash.insert(0,hash_byte)
	return hash

def hash_final_round(hash):
	for h in range(0,len(hash)):
		hash_final = hash[:]
		hash_byte = hash.pop()
		hash.insert(0,hash_byte)
		for i in range(0,len(hash_final)):
			hash_final_byte = hash_final.pop()
			if hash_final_byte != hash_byte:
				final_byte = hash_byte ^ hash_final_byte
		hash.insert(0,final_byte)
	return hash

def convert_hash_to_hex(hash):
	hex_hash = ""
	for i in range(0,len(hash)):
		hash_byte = hash.pop()
		hash_byte = hexlify(chr(hash_byte))
		hex_hash = hex_hash + hash_byte
	return hex_hash

init_hash(hash, iv)
hash = hash_round(data, hash)
hash_final = hash_final_round(hash)
hex_hash = convert_hash_to_hex(hash_final)
print input_file, hex_hash
in_fd.close()
