#!/usr/bin/env python



import os, sys
import socket
import argparse
import yaml
import logfsdelta_mdb as logmdb
from syncfsdelta import OpLogParser, OpLogEntry
import mongo_settings as settings


import datetime
import subprocess
import traceback
import logging
import atexit
from osync import DateWindow


########################################################################
#
# this script scans syncfsdelta completion logs and updates 
# the corresponding records in mongodb. It is desgined to bring our
# database up to date in cases where we have synced delta logs without
# updating mongo.
#
#
########################################################################


previewMode = False



def syncCompletionLogEntryToDB(opLogEntry, mongoInstance, yamlConfig, segment=None):
    
    recordID = None
    queryData = {}
    if segment:
        queryData['segment'] = segment
    queryData['processed'] = False
    queryData['path'] = opLogEntry.syncCommand.split(' ')[2]

    db = settings.DB_NAME
    collection = settings.COLLECTION_NAME

    cursor = mongoInstance.query(queryData, db, collection)
    if cursor.count() > 1:
        raise Exception('duplicate sync record found in database for path %s.' % (queryData['path']))

    if cursor.count() < 1:
        print 'no sync record found in database for path %s.' % (queryData['path'])
        return

    for record in cursor:       
        recordID = record['_id']
    
    updateData = { 'sync_start': opLogEntry.startTime, 'sync_end': opLogEntry.endTime, 'processed': True }

    if previewMode:
        print 'previewing DB update with record ID %s and data %s...' % (recordID, updateData)
    else:
        print 'updating DB record %s with data %s...' % (recordID, updateData)
        updatedDoc = mongoInstance.update(recordID, updateData, db, collection)
        if not updatedDoc:
            print 'error syncing completion log to DB record %s.' % recordID
        
        


def main(argv):
    
    parser = argparse.ArgumentParser(description='update mongodb with data from completed sync jobs')

    parser.add_argument('-p', action='store_true', required=False, help='preview mode (scan logs but do not update database)') 
    parser.add_argument('--initfile', metavar='initfile', required=True, nargs=1, help='syncfsdelta YAML init file')
    parser.add_argument('--segment', metavar='segment', required=False, nargs=1, help='segment name')
   
    
    args = parser.parse_args(argv)

    yamlConfig = logmdb.readInitfile(args.initfile[0])
    
    segment = None
    if args.segment:
        segment = args.segment[0]
    previewMode = bool(args.p)
    completionLogFilename = yamlConfig['globals']['completion_log']

    mongoInstance = logmdb.createMongoInstance(yamlConfig)
    

    print 'reading completion logs from %s...' % completionLogFilename
    print 'preview mode is %s.' % previewMode


    parser = OpLogParser()

    
    with open(completionLogFilename, 'r') as log:

        print 'processing completion log file %s...' % (completionLogFilename)
        lineNumber = 1
        for line in log:
            completionLogEntry = parser.parseLogEntry(line)            
            syncCompletionLogEntryToDB(completionLogEntry, mongoInstance, yamlConfig, segment)
            
            lineNumber = lineNumber+1
            if lineNumber % 500 == 0:
                print 'processed line %d in completion log %s.' % (lineNumber, completionLogFilename)
            sys.stdout.flush()
            
    

if __name__ == '__main__':
   main(sys.argv[1:])
