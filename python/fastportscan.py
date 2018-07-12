import sys
import socket
import time
from multiprocessing import Process

host = str(sys.argv[1])
threads = 32
ports = 65536

starttime = time.time()
openports = []

def dividepools(threads):
        a = 1
        chunk = ports / threads
        z = chunk * 2
        for thread in range(1,threads):
                Process(target=scanpool, args=(a,z)).start()
                a = z + 1
                z = z + chunk

def scanpool(a, z):
        for port in range(a,z):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)
		if port == 65535:
			endtime = time.time() - starttime
			print "Finished in %s seconds." % endtime	
                try:
			s.settimeout(0.5)
                        s.connect((host, port))
                        print "Detected open TCP port:", port
                        openports.append(port)
                except socket.error as er:
                        s.close()
                        #print "Closed port:", port
                        s = None
                        continue

dividepools(threads)
