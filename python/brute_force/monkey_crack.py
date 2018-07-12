import collections, sys

mode = sys.argv[1]

start_char = 65

def brute_force():
    chars = [91] * 10
    for a in range(start_char,chars[0]):
        for b in range(start_char,chars[1]):
            for c in range(start_char,chars[2]):
                for d in range(start_char,chars[3]):
                    for e in range(start_char,chars[4]):
                        for f in range(start_char,chars[5]):
                            for g in range(start_char,chars[6]):
                                for w in range(start_char,chars[7]):
                                    for x in range(start_char,chars[8]):
                                        for y in range(start_char,chars[9]):
                                                key = chr(f) + chr(g) + chr(w) + chr(x) + chr(y)

		                                expanded_key = expand_key(key, cipher_text)
		                                plain_text = vigenere_decrypt(alphabets, cipher_text, expanded_key)
                                                print key, plain_text
def init_alphabets():
	alphabets = {}
	alphabets_rev = {}
	for z, x in enumerate(range(65,91)):
		alphabet = collections.deque()
		alphabet_dict = {}
		alphabet_dict_rev = {}
		for y in range(65,91):
			alphabet.append(chr(y))
		if z == 0:
			shift_factor = z
		else:
			shift_factor = z * -1
		alphabet.rotate(shift_factor)
		for y in range(65,91):
			letter = alphabet.popleft()
			alphabet_dict[chr(y)] = letter
			alphabet_dict_rev[letter] = chr(y)
		alphabets[chr(x)] = alphabet_dict
                alphabets_rev[chr(x)] = alphabet_dict_rev
	return alphabets, alphabets_rev

def expand_key(key, secret):
	expanded_key = []
	key_copy = []
	for x in range(0,len(key)):
		expanded_key.append(key[x])
		key_copy.append(key[x])
	for x in range(0,len(secret)):
		char = key_copy.pop(0)
		key_copy.append(char)
		expanded_key.append(char)
        expanded_key.reverse()
	return expanded_key

def vigenere_decrypt(alphabets, secret, key):
	cipher_text = ""
	for x in range(0,len(secret)):
		keyi = key.pop()
		key.insert(0, keyi)
		sub_dict = alphabets_rev[keyi]
		sub = sub_dict[secret[x]]
		cipher_text = cipher_text + sub
	return cipher_text

def vigenere_encrypt(alphabets, secret, key):
	cipher_text = ""
	for x in range(0,len(secret)):
		keyi = key.pop()
		key.insert(0, keyi)
		sub_dict = alphabets[keyi]
		sub = sub_dict[secret[x]]
		cipher_text = cipher_text + sub
	return cipher_text
	
def dictionary_attack():
    with open("words", "r") as infile:
	for word in infile:
		word = word.rstrip('\n')
		expanded_key = expand_key(word, cipher_text)
		plain_text = vigenere_decrypt(alphabets, cipher_text, expanded_key)
		print word, plain_text
		#print plain_text

alphabets, alphabets_rev = init_alphabets()
if mode == "brute":
    brute_force()
elif mode == "dict":
    dictionary_attack()
