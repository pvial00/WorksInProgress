import sys

mode = sys.argv[1]
input_file = sys.argv[2]
output_file = sys.argv[3]

def caesar_encrypt(text):
	cipher_text = ""
	for x in range(0,len(text)):
		byte = ord(text[x])
		byte = byte - 3
		cipher_text = cipher_text + chr(byte)
	return cipher_text

def caesar_decrypt(text):
	plain_text = ""
	for x in range(0,len(text)):
		byte = ord(text[x])
		byte = byte + 3
		plain_text = plain_text + chr(byte)
	return plain_text

input_filef = open(input_file, "r")
output_filef = open(output_file, "w")

if mode == "encrypt":
	plain_text = input_filef.read()
	cipher_text = caesar_encrypt(plain_text)
	output_filef.write(cipher_text)
elif mode == "decrypt":
	cipher_text = input_filef.read()
	plain_text = caesar_decrypt(cipher_text)
	output_filef.write(plain_text)

input_filef.close()
output_filef.close()
