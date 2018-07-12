#!/usr/bin/env python
 
 
import os, sys
import time, datetime
import argparse
import yaml
import mongo_client as mdb 
import pymongo
import traceback
 
import mongo_settings as settings
_logfileName = None
_lockfileName = None
 
 

 
class DeltaLog:
    '''Wraps the file used to record filesystem change records.

    @param logfilename  the file to which we will write change records
    '''

    def __init__(self, logfilename):       
       self.logfilename = logfilename       
 

    def writeChangeRecord(self, record):
        '''records a filesystem change log record

        @param record   a DeltaLogRecord instance
        '''
        with open(self.logfilename, 'a') as fsDeltaLog:
            fsDeltaLog.write('%s\n' % record)
 
 

 
class DeltaLogRecord:
    '''  Container for filesystem change data to be logged.
    '''


    def __init__(self, moduleName, path, date):
        self.moduleName = moduleName
        self.path = path
        self.date = date
 

    def __repr__(self):
        return '%s,%s,%s' % (self. moduleName, self.path, self.date)



    def data(self):
        '''Create a dictionary-style document for storing this record in MongoDB

        '''
        rec = {}
        rec['module_name'] = self.moduleName
        rec['path'] = self.path        
        rec['date'] = str(self.date)
        rec['sync_start'] = None
        rec['sync_end'] = None       
        rec['processed'] = False
        rec['deleted'] = False
        rec['worker_id'] = None
        
        return rec


 
class DeltaLogRecordParser:
    '''Turns a single-line text entry in a changelog file into a DeltaLogRecord instance

    '''

    def __init__(self):
        pass
 
 
    def parseLogEntry(self, entry):        
        '''Process a comma-delimited line from a filestystem
        change log record.

        '''
        fields = [f.strip() for f in entry.split(',')]
        moduleName = fields[0]
        path = fields[1]
        date = fields[2]
        return DeltaLogRecord(moduleName, path, date)
        
    

 
class FSDeltaGlobalSettings():
    '''Represents the globals section in the logfsdelta/syncfsdelta init file

    '''
    def __init__(self, rsyncOptions, logfileName, lockfileName, completionLogName, distributionPoolName=None):
      self.rsyncOptions = rsyncOptions
      self.lockfileName = lockfileName
      self.logfileName = logfileName
      self.completionLogName = completionLogName 
      self.distributionPoolName = distributionPoolName
 
   
 
class FSDeltaConfigModule():
    '''A named file synchronization context stored in our init file

    '''

    def __init__(self, name, **kwargs):
        self.name = name
        self.sourcePath = kwargs['source']
        self.destPath = kwargs['destination']

 
    def __repr__(self):
        return '(FSDeltaConfigModule "%s": src: %s, dest: %s)' % (self.name, self.sourcePath, self.destPath)
 


def createDistributionPoolInDatabase(name, segments, mongoDBInstance): 
    '''Create a data structure inside MongoDB that will support round-robin distribution
    (and consumption) of filesystem change data. Will fail if a pool 
    with this name exists in the DB.

    '''

    data = {'name': name, 'segments': segments, 'counter': 0}
    return mongoDBInstance.insert(data, settings.DB_NAME, settings.POOL_COLLECTION_NAME)



class DistributionPoolNotFoundError(Exception):
    def __init__(self, poolName):
        Exception.__init__(self, 'Distribution pool %s not found in database.' % poolName)



class DistributionPool():
    '''A stored list of arbitrary names plus a counter value, for round robin distribution.

    Remembers its place in the list of names ("segments") and returns consecutive segment names 
    on successive requests.
    '''

    def __init__(self, name, mongoDBInstance, dbName=settings.DB_NAME, collectionName=settings.POOL_COLLECTION_NAME):        
        self.name = name
        self.dbName = dbName
        self.collectionName = collectionName
        poolData = self.loadPoolData( mongoDBInstance)         
        self.segments = poolData['segments']       
        

    def loadPoolData(self, mongoDBInstance):
        '''Retrieve the application's segment pool from MongoDB.

        '''

        poolData = mongoDBInstance.findOne({'name': self.name }, self.dbName, self.collectionName)
        if not poolData:
            raise DistributionPoolNotFoundError(self.name)
        return poolData


    def getSegment(self, counter):        
        '''Return the segment ID represented by an unbounded integer value, using modulo 

        '''

        index = int(counter % len(self.segments))
        return self.segments[index]


    def nextSegment(self, mongoDBInstance):
        '''Return the next segment name in this pool's sequence, incrementing the internal counter.

        '''
        poolData = self.loadPoolData(mongoDBInstance) 
        updateData = { 'counter': poolData['counter'] + 1}        
        mongoDBInstance.update(poolData['_id'], updateData, self.dbName, self.collectionName)
        return self.getSegment(updateData['counter'])
        
        
        


class MongoDBChangeRecordStorage():
    def __init__(self, mongoInstance, dbName, collectionName, distributionPool=None):
        '''Encapsulates the write semantics for Mongo-based filesystem change record storage.

        '''
        self.dbName = dbName
        self.collectionName = collectionName
        self.mongoDBInstance = mongoInstance        
        self.distributionPool = distributionPool


    def writeChangeRecord(self, changeRecord):        
        '''Store a filesystem change record in the database.

        @param  changeRecord    a valid DeltaLogRecord instance
        '''
        objectData = changeRecord.data()      
        if self.distributionPool:
            objectData['segment'] = self.distributionPool.nextSegment(self.mongoDBInstance)

        newID = self.mongoDBInstance.insert(objectData, self.dbName, self.collectionName)            
        return newID

    
 
def readInitfile(initfileName):
    '''Load a YAML initfile by name, returning the dictionary of its contents

    '''
    config = None
    with open(initfileName, 'r') as f:
        config = yaml.load(f)
 
    return config
 
 
def getConfigModules(yamlConfig):
    '''Retrieve the dictionary of config modules from a loaded YAML init object

    '''
    configModules = {}
    for moduleName in yamlConfig['modules']:
        moduleData = yamlConfig['modules'][moduleName]
        configModules[moduleName] = FSDeltaConfigModule(moduleName, **moduleData)
 
    return configModules
 
 
def initializeDistributionPools(yamlConfig, mongoDBInstance):
    '''Make sure the declared pools exist in MongoDB
    
    '''
    
    for poolName in yamlConfig.get('distribution_pools'):
        segmentList = yamlConfig['distribution_pools'][poolName]['segments']
        createDistributionPoolInDatabase(poolName, segmentList, mongoDBInstance)

    



def loadAssignedDistributionPool(yamlConfig, mongoDBInstance):
    '''Load the distribution pool that has been assigned to a syncfsdelta application
    in its YAML init file

    '''
    globalConfig = getGlobalSettings(yamlConfig)    
    distPoolName = globalConfig.distributionPoolName
    pool = None
    if distPoolName:
        print 'loading distribution pool %s.' % distPoolName
        try:
            return DistributionPool(distPoolName, mongoDBInstance)
        except DistributionPoolNotFoundError, err:
            segmentList = yamlConfig['distribution_pools'][distPoolName]['segments']
            createDistributionPoolInDatabase(distPoolName, segmentList, mongoDBInstance)
            return DistributionPool(distPoolName, mongoDBInstance)

   




def getGlobalSettings(yamlConfig):
    '''Retrieve application-wide settings from a loaded YAML config object

    '''
    globals = yamlConfig['globals']
    settings = FSDeltaGlobalSettings(globals['rsync_options'], globals.get('logfile'), globals.get('lockfile'), globals.get('completion_log'), globals.get('distribution_pool'))
    return settings
 
 

def generateChangeRecord(path, fsDeltaConfigModule):
    '''Render a path containing filesystem deltas into a single-line filesystem
    change record

    '''
    changeRecord = '%s,%s,%s' % (fsDeltaConfigModule.name, path, datetime.datetime.now())
    return changeRecord      
 
 


def createMongoInstance(yamlConfig):
    '''Create a new MongoDB client wrapper from a YAML config object.

    '''
    mdbConfig = yamlConfig['mongodb_storage_config']
    hostArray = mdbConfig['hosts']   
    replicaset = mdbConfig.get('replicaset')
    
    mongoConfig = mdb.MongoClientConfig(hostArray, replicaset)
    mongoInstance = mdb.MongoInstance(mongoConfig)
    
    return mongoInstance
        




def logChangedFolder(folder, config_filename, module_name):
    '''Write a filesystem delta record to our storage media of choice
    (currently the filesystem and the database).


    @param folder               the directory whose contents changed
    @param config_filename      the full path of our YAML initfile
    @param module_name          the name of a source->target synchronization 
                                context, defined in the YAML file
    '''

    yamlConfig = readInitfile(config_filename)

    moduleTable = getConfigModules(yamlConfig)
    globalConfig = getGlobalSettings(yamlConfig)
    mongoInstance = createMongoInstance(yamlConfig)
   


    distPoolName = globalConfig.distributionPoolName
    distributionPool = None
    if distPoolName:
        distributionPool = loadAssignedDistributionPool(yamlConfig, mongoInstance)
        print 'will write change record using distribution pool %s.' % distPoolName


    mdbConfig = yamlConfig['mongodb_storage_config']
    dbName = settings.DB_NAME
    collectionName = settings.COLLECTION_NAME
    logRecorder = MongoDBChangeRecordStorage(mongoInstance, dbName, collectionName, distributionPool)

    targetModule = moduleTable.get(module_name)
    
    if not targetModule:
       raise Exception('Module "%s" not found in init file %s.' % (module_name, config_filename))

 
    if not folder.startswith(targetModule.sourcePath):
       raise Exception('Error: the location %s is not covered by module "%s" in initfile %s. (module path: %s)' % (folder, module_name, config_filename, targetModule.sourcePath))

 
    changeRecord = DeltaLogRecord(module_name, folder, datetime.datetime.now())
    
    newRecordID = logRecorder.writeChangeRecord(changeRecord)
    if not newRecordID:
        raise Exception('Error logging change record: %s' % changeRecord)
 
    return newRecordID



def main(argv):
    parser = argparse.ArgumentParser(description='Log filesystem changes from boinc ingest workflow')
 
    parser.add_argument('-i', metavar='initfile', nargs=1, required=True, help='YAML init file')
    parser.add_argument('-m', metavar='module', nargs=1, required=True, help='module name')
    parser.add_argument('path')
 
    args = parser.parse_args(argv)
 
    initfileName = args.i[0]
    filesystemChangeLocation = args.path
    targetModuleName = args.m[0]
    

    success = logChangedFolder(filesystemChangeLocation, initfileName, targetModuleName)
    if success:
        exit(0)
    else:
        print 'Error writing change record.'
        exit(1)
 
 
if __name__ == '__main__':
   main(sys.argv[1:])
