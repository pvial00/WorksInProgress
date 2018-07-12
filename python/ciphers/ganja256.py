import sys
from binascii import hexlify

iv = 5

try:
    input_file = sys.argv[1]
except IndexError as ier:
    print "Error: Input file argument missing"
    sys.exit(1)

def init_hash(hash, iv):
	for x in range(0,16):
		hash.append(iv)
	return hash

def hash_round(data, hash):
	for x in range(0,len(data)):
		hash_byte = hash.pop(0)
		hash_byte = hash_byte ^ ord(data[x])
		hash.append(hash_byte)
	return hash

def hash_final_round(hash):
	for h in range(0,len(hash)):
		hash_final = hash[:]
		hash_byte = hash.pop(0)
                #hash.insert(0,hash_byte)
                for i in range(0,len(hash_final)):
			hash_final_byte = hash_final.pop(0)
			if hash_final_byte != hash_byte:
				final_byte = hash_byte ^ hash_final_byte
		hash.append(final_byte)
	return hash

def convert_hash_to_hex(hash):
	hex_hash = ""
	for i in range(0,len(hash)):
		hash_byte = hash.pop()
		hash_byte = hexlify(chr(hash_byte))
		hex_hash = hex_hash + hash_byte
	return hex_hash

def key_hash(hash, key):
    keyed_hash = []
    keys = []
    for x in range(len(key)):
            keys.append(key[x])
    for x in range(len(hash)):
        byte = hash.pop(0)
        key_byte = keys.pop(0)
        byte = byte ^ ord(key_byte)
        keys.append(key_byte)
        keyed_hash.append(byte)
    return keyed_hash

def truncate_hash(hash):
    short_hash = ""
    for x in range(len(hash) / 2,len(hash)):
        short_hash += hash[x]
    return short_hash

def ganja_hash(data, key):
    hash = []
    init_hash(hash, iv)
    hash = hash_round(data, hash)
    keyed_hash = key_hash(hash, key)
    hash_final = hash_final_round(keyed_hash)
    hex_hash = convert_hash_to_hex(hash_final)
    return hex_hash

def readfile(filename):
    try:
        in_fd = open(filename, "r")
    except IOError as ioer:
        print "Error: Could not open input file."
        sys.exit(1)
    data = in_fd.read()
    in_fd.close()
    return data

data = readfile(input_file)
hex_hash = ganja_hash(data, input_file)
print input_file, hex_hash
