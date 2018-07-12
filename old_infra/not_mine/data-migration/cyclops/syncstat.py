#!/usr/bin/env python


import os, sys, socket
import argparse
import commands
import yaml
import datetime

import osync
import logfsdelta_mdb as logmdb
import mongo_client
import mongo_settings as settings

from dateutil import parser as dateparser


########################################################################
#
# syncstat runs throughput stats on recently synchronized directories
# and uploads them to a designated mongodb instance.
#
########################################################################








class ThroughputMeasurement():
    def __init__(self, recordID, bytesTransferred, timeInSeconds):
        self.recordID = recordID
        self.bytesTransferred = bytesTransferred
        self.transferTime = timeInSeconds

    def megabytesPerSecond(self):
        mb = self.bytesTransferred / 1024
        return mb / self.transferTime

    def __repr__(self):
        return 'Record %s: %d bytes transferred in %d seconds' % (self.recordID, self.bytesTransferred, self.transferTime)




def getDeltaRecordsInDateRange(yamlConfig, mongoInstance, dateWindow, verbose=False):
    
    records = []
    queryDict = {}
    dateSubquery = { '$gte': str(dateWindow.startDate), '$lte': str(dateWindow.endDate) }                  
    queryDict['date'] = dateSubquery
    queryDict['processed'] = True

    db = settings.DB_NAME
    collection = settings.COLLECTION_NAME
    if verbose:
        print 'querying change log DB with query: %s...' % queryDict
    cursor = mongoInstance.query(queryDict, db, collection)
    for record in cursor:
        records.append(record)

    return records



def getStatsForDeltaRecords(yamlConfig, mongoInstance, deltaRecordList):
    
    db = settings.DB_NAME
    collection = settings.COLLECTION_NAME
    
    stats = []
    for record in deltaRecordList:                   
        recordID = str(record['_id'])
        path = record['path']
        duCmd = 'du -s %s' % (path)
        size = int(commands.getoutput(duCmd).split()[0])
        startTimeString = record['sync_start']
        endTimeString = record['sync_end']
        if startTimeString and endTimeString:
            
            endTime = dateparser.parse(endTimeString)
            startTime = dateparser.parse(startTimeString)
            transferTime = (endTime - startTime).total_seconds()
            stats.append(ThroughputMeasurement(recordID, size, transferTime))
            
    return stats    
    


def updateDBWithThroughputStats(yamlConfig, mongoInstance, stats):

    db = settings.DB_NAME
    collection = settings.COLLECTION_NAME
    updateCount = 0

    print '%d stats to update.' % len(stats)
    print 'verbose mode is %s.' % verbose

    for measurement in stats:
        if verbose:
            print 'updating deltalog DB record %s...' % measurement.recordID
        if mongoInstance.update(measurement.recordID, 
                                  { 'bytes_transferred' : measurement.bytesTransferred, 
                                   'transfer_time' : measurement.transferTime,
                                    'mbytes_sec': measurement.megabytesPerSecond() },
                                    db, collection):
            updateCount = updateCount + 1
            if verbose:
                print '%d of %d stats saved to DB.' % (updateCount, len(stats))
            
        else:
            print 'error updating record %s.' % measurement.recordID 

    print 'throughput stats updated.'
        

def startupMessage():
    return 'syncstat starting at %s on host %s...' % (datetime.datetime.now(), socket.gethostname())



def terminationMessage():
    return 'syncstat terminating at %s on host %s...' % (datetime.datetime.now(), socket.gethostname())



def main(argv):
    parser = argparse.ArgumentParser(description = 'Collect throughput stats on recent sync operations')

    parser.add_argument('--mode', metavar='mode', nargs=1, required=True, help='single (one record at a time) or batch mode')
    parser.add_argument('--logid', metavar='logID', nargs=1, required=False, help='target directory for single-record mode')
    parser.add_argument('-t', action='store_true', required=False, help='tell mode (collect stats but do not update database)') 
    parser.add_argument('-v', action='store_true', required=False, help='verbose mode')
    parser.add_argument('--minutes', metavar='minutes', nargs=1, required=False, help='collect stats on records synced N minutes ago or less')
    parser.add_argument('initfile')


    print startupMessage()

    args = parser.parse_args(argv)

    runMode = args.mode[0]
    verbose = bool(args.v)
    yamlConfig = logmdb.readInitfile(args.initfile)
    mongoInstance = logmdb.createMongoInstance(yamlConfig)

    print 'verbose mode is %s.' % verbose

    logRecords = []
    if runMode == 'single':
        if not args.dir:
            print 'If single-record mode is selected, you must specify a directory.'
            exit(1)
        
        logRecords.append(getDeltaRecord(args.logid[0]))
        
    elif runMode == 'batch': 
        if not args.minutes:
            print 'If batch mode is selected, you must specify a time window in minutes.'
            exit(1)

        currentDate = datetime.datetime.now()
        queryStartTime = currentDate - datetime.timedelta(minutes = int(args.minutes[0]))
        dateWindow = osync.DateWindow(queryStartTime)

        logRecords.extend(getDeltaRecordsInDateRange(yamlConfig, mongoInstance, dateWindow))
    else:
        print 'unsupported mode specified. Please select either "single" or "batch".'
        exit(1)
    
    
    if verbose:
        print '%d log records found.' % len(logRecords)
        for r in logRecords: 
            print r
            print '\n'

    stats = getStatsForDeltaRecords(yamlConfig, mongoInstance, logRecords)

    if verbose:
        for s in stats:
            print s
            print '\n'

    updateDBWithThroughputStats(yamlConfig, mongoInstance, stats)
    
    print terminationMessage()
    
        
if __name__=='__main__':
   main(sys.argv[1:])
