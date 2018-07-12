import subprocess
import sys


port = str(sys.argv[1])
netstat = subprocess.Popen(["netstat", "-an"], stdout=subprocess.PIPE).communicate()[0]

print len(netstat)

for x in netstat.splitlines():
        check  = x.find(port)
        if check != -1:
                print x
