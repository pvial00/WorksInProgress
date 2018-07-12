#!/usr/bin/env python



import os, sys
import socket
import argparse
import yaml

import logfsdelta_mdb as logmdb
from syncfsdelta import OpLogParser, OpLogEntry

import mongo_client as mclient
import mongo_settings as settings



completeRecordQueryDoc = { 'sync_start': {'$ne': None }, 'sync_end': {'$ne': None }, 'processed': True }
syncingRecordQueryDoc = { 'sync_start': {'$ne': None }, 'sync_end': None, 'worker_id': {'$ne': None } }
unprocessedRecordQueryDoc = { 'processed': False  }
markedRecordQueryDoc =  { 'worker_id': {'$ne': None } }
anyRecordQueryDoc = {}



def statFunction(queryDoc, mongoInstance, db, collection, segmentName=None):

    resultSet = []
    if segmentName:
        queryDoc['segment'] = segmentName

    cursor = mongoInstance.query(queryDoc, db, collection)
    
    for record in cursor:
        resultSet.append(record)

    cursor.close()
    return resultSet



def main(argv):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--segment', metavar='segment', nargs=1, required=False)
    parser.add_argument('--status', metavar='status', nargs=1, required=True)    
    parser.add_argument('initfile')


    args = parser.parse_args(argv)


    initfile = args.initfile
    segmentName = None
    if args.segment:
        segmentName = args.segment[0]
    status = args.status[0]

    yamlConfig = logmdb.readInitfile(args.initfile)
    mongoInstance = logmdb.createMongoInstance(yamlConfig)
    db = settings.DB_NAME
    collection = settings.COLLECTION_NAME

    queryMap = {'complete': completeRecordQueryDoc,
                'syncing': syncingRecordQueryDoc, 
                'unprocessed': unprocessedRecordQueryDoc, 
                'marked': markedRecordQueryDoc, 
                'any': anyRecordQueryDoc }


    statQuery = queryMap.get(status)
    if statQuery or status == 'any':
        results = statFunction(statQuery, mongoInstance, db, collection, segmentName)
        if not segmentName:
            segmentTag = 'any segment'
        else:
            segmentTag = 'segment %s' % segmentName
        print 'Found %d records with status "%s" assigned to %s in the database.' % (len(results), status, segmentTag)
    else:
        print 'Unrecognized status type "%s". Valid status types are: \n%s' % (status, '\n'.join(queryMap.keys()))
    


   
    


if __name__ == '__main__':
    main(sys.argv[1:])
