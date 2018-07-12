import sys, time, random

infile = open(sys.argv[1], "r")
outfile = open(sys.argv[2], "w")
key = sys.argv[3]
data = infile.read()

start_time = time.time()

for x in reversed(range(0,len(data))):
	byte = data[x]
	primary_round = ord(byte)
	for y in range(0,len(key)):
		primary_round = primary_round ^ ord(key[y])
	crypt_text = chr(primary_round)
	outfile.write(crypt_text)
end_time = time.time() - start_time
print "Completed in %s seconds" % end_time
infile.close()
outfile.close()
