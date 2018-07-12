import sys
import socket

host = str(sys.argv[1])

def knock(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = socket.socket()
        try:
                s.connect((host, port))
                msg = "Detected open TCP port:"
                openports.append(port)
        except socket.error as er:
                s.close()
                #print "Closed port:", port
                msg = []
                s = None
                #continue
        return msg, port

print "Scanning common ports on host: ", host
openports = []
commonports = (21, 22, 25, 80, 110, 143, 993, 995, 445, 554)
for port in commonports:
        knock(host,port)

print "Open TCP ports: ", openports

openports = []

print "Scanning range 1-1000 ports on host: ", host

for port in range(1,1000):
        knock(host,port)

print "Open TCP ports: ", openports
