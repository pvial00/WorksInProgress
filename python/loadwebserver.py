import pycurl
from StringIO import StringIO
from multiprocessing import Process

def hitit():
	for x in range(0,100):
    		buf = StringIO()
    		c = pycurl.Curl()
    		c.setopt(c.URL, 'http://10.0.2.15:8080/')
    		c.setopt(c.WRITEDATA, buf)
    		try:
    			c.perform()
    		except pycurl.error as er:
			print "ERROR: Unable to reach server"
			continue
    		c.close()
    		body = buf.getvalue()
    		print body
    		if body == 0:
			print "ERROR: 0 bytes back"
		exit()

concurrency=50

for x in range(1,concurrency):
	Process(target=hitit).start()

