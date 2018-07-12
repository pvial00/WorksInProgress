#!/usr/bin/env python

import sys, os
import argparse
import time
from stat import *

from gen_purge_list import *



def main(argv):
    parser = argparse.ArgumentParser(description='Verify date format of a named directory')
    parser.add_argument('-l', metavar='label', nargs=1, required=True, help='record label name')
    parser.add_argument('filename')

    args = parser.parse_args()

    filename = args.filename
    labelName = args.l[0]

    parentDir = contentFeedPaths.get(labelName)
    if not parentDir:
        print '>>> no content feed directory has been registered for the record label %s. Exiting.' % labelName
    
    fqFilename = os.path.join(parentDir, filename)
    st = os.stat(fqFilename)

    print "\n>>> examining file %s..." % fqFilename
    print ">>> file %s was last modified on: %s" % (filename, time.asctime(time.localtime(st[ST_MTIME])))
    
    if verifyFilenameFormat(filename, labelName):
        print '>>> filename %s matches the %s feed format.' % (filename, labelName)
        inferredDate = deriveDateFromFilename(filename, labelName)
        if inferredDate:
            print '>>> inferred date of this file is %s' % inferredDate
        else:
            print '>>> could not infer the date of this file from its name.'
    else:
        print '>>> filename %s does NOT match the %s feed format.' % (filename, labelName)
    

if __name__ == '__main__':
   main(sys.argv[1:])
