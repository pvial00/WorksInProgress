#!/usr/bin/env python


import os, sys
import socket
import argparse
import shutil
import datetime
from gen_purge_list import compileContentPurgeList


approvedHosts = ['encode14.ingest.pnap.ny.boinc']


def getDatestamp():
    return datetime.datetime.now()


def main(argv):

    print('fspurge started at %s with process ID %d.' % (getDatestamp(), os.getpid()))
    
    hostname = socket.gethostname()
    if hostname not in approvedHosts:
        print 'fspurge is not authorized to run on host %s. \nRun fspurge on one of the following hosts: %s.' \
                % (hostname, approvedHosts)
        exit(1)

    
    parser = argparse.ArgumentParser(description='Purge record label content')
    parser.add_argument('-l', metavar='label', nargs=1, required=True, help='record label name')
    parser.add_argument('-p', action='store_true', required=False, help='preview (show files to be deleted, but do not delete)')
    parser.add_argument('--verify', action='store_true', required=False)
    args = parser.parse_args()

    labelName = args.l[0]
    previewMode = bool(args.p)
    numDays = 90


    print('compiling %s purge list using %d day window...' % (labelName, numDays))
    filesToPurge = compileContentPurgeList(numDays, labelName)
    numFilesToPurge = len(filesToPurge)
   
    if previewMode:
        print('fspurge running in preview mode, showing content from label %s older than %d days...' % (labelName, numDays))
    else:
        print('fspurge preparing to delete content from label %s older than %d days...' % (labelName, numDays))
        print 'fspurge will delete the following directories:'
    
    
    for f in filesToPurge:
        print f

    if not len(filesToPurge):
        print 'No files to purge for label %s. Exiting.' % labelName
        exit()
        
    if args.verify:
        existingFiles = []
        for f in filesToPurge:
            if os.path.exists(f):
                existingFiles.append(f)

        print 'verification: %d directories out of %d marked for purging actually exist on the target volume.' % (len(existingFiles), len(filesToPurge))


    if previewMode:
        exit()


    numFilesPurged = 0
    
    for f in filesToPurge:
        try:
            shutil.rmtree(f)
            print('deleted %s\n' % f)                
            numFilesPurged += 1                                 
        except Exception, x:
            print('error deleting dir: %s\n' % x)
            continue
        finally:    
            print('purged %d of %d selected dirs.\n' % (numFilesPurged, numFilesToPurge))
    
    
    
    


if __name__ == '__main__':
   main(sys.argv[1:])
