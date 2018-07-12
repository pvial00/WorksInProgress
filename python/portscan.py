import sys
import socket

host = str(sys.argv[1])

print "Scanning host: ", host
openports = []
for port in range(1,65536):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = socket.socket()
        try:
                s.connect((host, port))
                print "Detected open TCP port:", port
                openports.append(port)
        except socket.error as er:
                s.close()
                #print "Closed port:", port
                s = None
                continue

print "Open TCP ports: ", openports
