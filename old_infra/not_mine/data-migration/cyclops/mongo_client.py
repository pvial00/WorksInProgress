#!/usr/bin/env python


import pymongo
from bson.objectid import ObjectId
import mongo_settings
import time



class DBOperationStatus():
    def __init__(self, statusDocument):
        self.statusData = statusDocument
        if not statusDocument:
            raise Exception('Attempted to initialize a status object with an empty status document.')


    def __repr__(self):
        return str(self.statusData)


    def didUpdateDB(self):
        return bool(self.statusData['updatedExisting'])


    def ok(self): 
        if self.statusData['ok'] == 1.0:
            return True

        return False


class MongoClientConfig(object):
    def __init__(self, hosts, replicaset):
        self.hosts = hosts
        self.replicaset = replicaset



class MongoInstance():
    def __init__(self, mongoClientConfig):
        self.config = mongoClientConfig        
        self._mdbClient = None


    def url(self):
        return ','.join(self.config.hosts)
        
        
    def _createClient(self):
        if not self._mdbClient:            
            self._mdbClient = pymongo.MongoReplicaSetClient(self.url(), replicaset=self.config.replicaset, connectTimeoutMS=mongo_settings.CONNECT_TIMEOUT_MS)
        return self._mdbClient


    client = property(_createClient)


    def _retryFindOne(self, objectData, dbName, collectionName):
        try:
            # if find_one() executes normally but couldn't find a record...
            return (True, self.client[dbName][collectionName].find_one(objectData))
        except pymongo.errors.AutoReconnect:
            # if we still can't reconnect... 
            return (False, None)


    def findOne(self, objectData, dbName, collectionName):
        try:
            collection = self.client[dbName][collectionName]
            obj = collection.find_one(objectData)
            return obj
        except pymongo.errors.AutoReconnect, err:
            print 'initial mongodb connect failed, reconnecting...'
            
            # We use a statusTuple instead of just checking the return value of find_one() 
            # because we need to distinguish between getting a null value 
            # because we couldn't find an object, and getting a null value because of a connection error
            #
            statusTuple = None
            for x in range(1, mongo_settings.MAX_FAILOVER_RETRIES):
                time.sleep(mongo_settings.FAILOVER_RETRY_INTERVAL_SECS)
                statusTuple = self._retryFindOne(objectData, dbName, collectionName)
                if statusTuple[0]:
                    break

            if not statusTuple[0]:
                raise Exception('could not connect to MongoDB instance for findOne operation after %d retries. Initial error essage: %s' 
                                % (mongo_settings.MAX_FAILOVER_RETRIES, err.message))
            return statusTuple[1]



    def _retryInsert(self, objectData, dbName, collectionName):
        try:
            return self.client[dbName][collectionName].insert(objectData)                     
        except pymongo.errors.AutoReconnect:
            return None



    def insert(self, objectData, dbName, collectionName):
        newID = None
        try:                           
            collection = self.client[dbName][collectionName]
            print 'inserting document %s into %s.%s...' % (objectData, dbName, collectionName)
            newID = collection.insert(objectData)            
            return newID
        except pymongo.errors.AutoReconnect, err:  
            print 'initial mongodb connect failed, reconnecting...'
            
            for x in range(1, mongo_settings.MAX_FAILOVER_RETRIES):
                time.sleep(mongo_settings.FAILOVER_RETRY_INTERVAL_SECS)
                newID = self._retryInsert(objectData, dbName, collectionName)
                if newID:
                    return newID
                                
            raise Exception('could not connect to MongoDB instance for insert operation after %d retries. Initial error essage: %s' % (mongo_settings.MAX_FAILOVER_RETRIES, err.message))
            

    def insertIfNotPresent(self, objectData, dbName, collectionName):                                        
        collection = self.client[dbName][collectionName]
        cursor = self.query(objectData, dbName, collectionName)
        if not cursor.count():
            print 'inserting document %s into %s.%s...' % (objectData, dbName, collectionName)
            self.insert(objectData, dbName, collectionName)

        


    def _retryUpdate(self, objectKey, objectData, dbName, collectionName):
        try:
            return self.client[dbName][collectionName].update({'_id': objectKey }, {'$set': objectData})                     
        except pymongo.errors.AutoReconnect:
            return None       
    

    def update(self, key, data, dbName, collectionName):
        updateStatus = None
        objectKey = ObjectId(key)

        try:          
            collection = self.client[dbName][collectionName]
            updateStatus = collection.update({'_id': objectKey }, {'$set': data})
            return DBOperationStatus(updateStatus)
        except pymongo.errors.AutoReconnect, err:
            print 'initial mongodb connect failed, reconnecting...'
            
            for x in range(1, mongo_settings.MAX_FAILOVER_RETRIES):
                time.sleep(mongo_settings.FAILOVER_RETRY_INTERVAL_SECS)
                updateStatus = self._retryUpdate(objectKey, data, dbName, collectionName)
                if updateStatus:
                    break
            if not updateStatus:                    
                raise Exception('Could not connect to mongoDB instance for update operation after %d retries. Initial error essage: %s' 
                                % (mongo_settings.MAX_FAILOVER_RETRIES, err.message))
            
            return DBOperationStatus(updateStatus)
             
 
    
    def _retryQuery(self, queryDict, dbName, collectionName):
        try:
            return self.client[dbName][collectionName].find(queryDict, timeout=False)                     
        except pymongo.errors.AutoReconnect:
            return None         



    def query(self, queryDict, dbName, collectionName):
        cursor = None
        try:
            collection = self.client[dbName][collectionName]
            cursor = collection.find(queryDict, timeout=False)
            return cursor
        except pymongo.errors.AutoReconnect, err:
            print 'initial mongodb connect failed, reconnecting...'
            
            for x in range(1, mongo_settings.MAX_FAILOVER_RETRIES):
                time.sleep(mongo_settings.FAILOVER_RETRY_INTERVAL_SECS)
                cursor = self._retryQuery(queryDict, dbName, collectionName)
                if cursor:
                    break

            if not cursor:      
                raise Exception('Could not connect to mongoDB instance for query operation after %d retries. Initial error essage: %s' 
                                % (mongo_settings.MAX_FAILOVER_RETRIES, err.message))
            return cursor



    
    
