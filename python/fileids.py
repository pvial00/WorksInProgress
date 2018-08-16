import subprocess
import os
#import md5

database = "file.db"
mainpath = "/Users/pvial/work"

def builddb():
	allfiles = subprocess.Popen(["find", mainpath, "-type", "f"], stdout=subprocess.PIPE).communicate()[0]
	f = open(database, 'w')
	print "Building hash database..."
	for file in allfiles.split():
		mout = md5file(file)
		f.write(mout)
	f.close()

def md5file(file):
	mout = subprocess.Popen(["md5sum", file], stdout=subprocess.PIPE).communicate()[0]
	return mout
	

def watchdb(database):
	f = open(database, 'r')
	print "Comparing hashes..."
	for line in f.readlines():
		hash, file = line.split()
		mout = md5file(file)
		thash = mout.split()
		if hash != thash[0]:
			print "Alert! %s file changed" % file
	f.close()
	
if os.path.exists(database) == False:
	builddb()
watchdb(database)
