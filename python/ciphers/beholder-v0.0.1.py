import random, sys
import collections

try:
    mode = sys.argv[1]
except IndexError as ier:
    print "Error: Did you forget (encrypt/decrypt)?"
    sys.exit(0)
shiftbox_A = [37, 59, 62, 15, 33, 76, 63, 21, 83, 77, 31, 61, 21, 8, 60, 16, 11, 17, 58, 2, 90, 43, 18, 8, 52, 59, 75, 7, 9, 27, 23, 30, 70, 82, 74, 30, 31, 58, 79, 68, 60, 81, 69, 8, 62, 65, 75, 6, 43, 57, 88, 70, 23, 3, 76, 18, 2, 55, 19, 40, 85, 42, 72, 2, 61, 48, 85, 6, 62, 17, 16, 36, 77, 49, 24, 0, 8, 28, 58, 12, 0, 69, 79, 84, 78, 77, 83, 6, 74, 83, 9, 21, 49, 14, 11, 67, 88, 0, 4, 81, 59, 47, 14, 6, 59, 69, 12, 20, 16, 83, 35, 57, 80, 19, 90, 61, 24, 91, 14, 9, 69, 17, 30, 16, 82, 36, 9, 70, 9, 44, 78, 38, 30, 89, 37, 36, 50, 63, 26, 16, 46, 83, 64, 31, 2, 88, 46, 60, 60, 29, 24, 57, 32, 85, 47, 67, 74, 68, 67, 15, 85, 56, 25, 6, 6, 63, 54, 12, 30, 75, 36, 27, 40, 41, 57, 36, 45, 50, 66, 47, 51, 74, 35, 45, 79, 36, 62, 76, 44, 66, 30, 56, 81, 63, 43, 0, 90, 49, 57, 85, 28, 14, 62, 78, 4, 73, 0, 3, 4, 63, 68, 24, 34, 62, 62, 88, 12, 32, 2, 73, 16, 36, 53, 73, 5, 54, 64, 40, 48, 29, 62, 27, 89, 14, 68, 68, 19, 28, 42, 23, 91, 7, 80, 23, 85, 24, 47, 69, 68, 45]
shiftbox_B = [36, 61, 4, 80, 3, 35, 69, 88, 11, 87, 31, 76, 43, 19, 45, 47, 34, 28, 77, 38, 86, 3, 6, 15, 59, 64, 89, 62, 43, 35, 0, 88, 60, 71, 38, 68, 22, 21, 33, 56, 42, 12, 6, 23, 10, 22, 4, 23, 65, 24, 55, 83, 56, 91, 76, 73, 23, 33, 53, 29, 66, 38, 30, 54, 60, 76, 8, 49, 66, 6, 71, 34, 27, 41, 49, 15, 5, 36, 58, 71, 11, 27, 47, 36, 46, 59, 39, 42, 19, 74, 31, 89, 84, 69, 71, 55, 20, 47, 10, 61, 61, 38, 41, 86, 69, 19, 31, 81, 24, 32, 34, 61, 78, 48, 67, 19, 15, 50, 58, 4, 74, 33, 23, 53, 54, 4, 2, 53, 49, 71, 74, 23, 12, 30, 15, 3, 10, 51, 13, 29, 65, 2, 88, 51, 75, 27, 55, 77, 79, 56, 79, 34, 86, 11, 80, 26, 25, 31, 59, 43, 59, 3, 78, 50, 45, 26, 45, 54, 42, 50, 85, 59, 15, 34, 7, 5, 24, 9, 66, 28, 28, 21, 0, 1, 90, 57, 24, 81, 21, 85, 5, 41, 32, 81, 83, 73, 89, 62, 34, 41, 58, 74, 2, 90, 45, 17, 14, 1, 71, 65, 28, 8, 83, 8, 2, 80, 0, 63, 72, 67, 24, 50, 4, 27, 74, 25, 14, 69, 73, 15, 2, 0, 52, 89, 38, 33, 3, 54, 60, 35, 16, 91, 43, 67, 57, 13, 80, 11, 50, 38]

def encipher_char(data):
	newdata = ""
	init = []
	sub_box = []
        primer = collections.deque()
	sub_primer = collections.deque()
        for x in range(32,123):
                primer.append(chr(x))
		sub_primer.append(chr(x))
        shift_value_A = shiftbox_A.pop()
        shift_value_B = shiftbox_B.pop()
        #sub_primer = alpha_matrix(shift_value_B)
        sub_primer.rotate(shift_value_A)
        sub_primer.rotate(shift_value_B)
	#print primer, sub_primer
	for x in range(0,91):
		init.append(primer.popleft())
		sub_box.append(sub_primer.popleft())

	for x in range(0,len(data)):
            try:
		pos = init.index(data[x])
            except ValueError as ver:
                print "Error on char: " + data[x]
	    sub_pos = sub_box.index(data[x])
	    sub = sub_box.pop(pos)
	    sub_box.insert(pos, sub)	
		#print pos, sub_pos
		#print sub
       	    newdata = newdata + sub
	return newdata

def decipher_char(data):
	newdata = ""
	init = []
	sub_box = []
        primer = collections.deque()
	sub_primer = collections.deque()
        for x in range(32,123):
                primer.append(chr(x))
		sub_primer.append(chr(x))
        shift_value_A = shiftbox_A.pop()
        shift_value_B = shiftbox_B.pop()
        #sub_primer = alpha_matrix(shift_value_B)
        sub_primer.rotate(-shift_value_A)
        sub_primer.rotate(-shift_value_B)
	for x in range(0,91):
		init.append(primer.popleft())
		sub_box.append(sub_primer.popleft())

	for x in range(0,len(data)):
            try:
		pos = init.index(data[x])
            except ValueError as ver:
                print "Error on char: " + data[x]
	    sub_pos = sub_box.index(data[x])
	    sub = 0
	    sub = sub_box.pop(pos)
	    sub_box.insert(pos, sub)	
		#print pos, sub_pos
		#print sub
	    newdata = newdata + sub
	return newdata

def random_shiftbox(length):
    shiftbox = []
    for x in range(0,length):
        value = random.randint(0,91)
        shiftbox.append(value)
    return shiftbox

def alpha_matrix(matrix_number):
    index = matrix_number / 91
    index_step = matrix_number % 91
    if index < 1:
        index = 1
    alphabet = collections.deque()
    master_alpha = collections.deque()
    for letter in range(32,123):
        alphabet.append(chr(letter))
        master_alpha.append(chr(letter))
    for x in range(0,index):
        alphabet.rotate(-1)
        for z in range(0,90):
            letter = alphabet.popleft()
            alphabet.append(letter)
    for y in range(0,index_step):
        letter = alphabet.popleft()
        alphabet.append(letter)
    alphabet_dict = {}
    for letter in master_alpha:
        alphabet_dict[letter] = alphabet.popleft()
    return alphabet_dict

#matrix = alpha_matrix(128)
#print matrix
#sys.exit(0)

if mode == "gen":
    box_value = int(sys.argv[2])

    shiftbox = random_shiftbox(box_value)
    print shiftbox
    sys.exit(0)

data = raw_input("Enter text to cipher: ")

if mode == "encrypt":
    cipher_text = ""
    for char in data:
        cryptdata = encipher_char(char)
        cipher_text += cryptdata
    print cipher_text
elif mode == "decrypt":
    plain_text = ""
    for char in data:
        clear = decipher_char(char)
        plain_text += clear
    print plain_text
