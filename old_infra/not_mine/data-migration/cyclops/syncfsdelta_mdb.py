#!/usr/bin/env python



import os, sys
import socket
import argparse
import yaml
from logfsdelta_mdb import *
from syncfsdelta import FileLock
import datetime
import subprocess
import traceback
import logging
import atexit
from osync import DateWindow


procs = []

@atexit.register
def kill_subprocesses():
    for proc in procs:
        proc.kill()



def log_uncaught_exceptions(ex_cls, ex, tb):
      logging.critical(''.join(traceback.format_tb(tb)))
      logging.critical('{0}: {1}'.format(ex_cls, ex))



sys.excepthook = log_uncaught_exceptions


def currentDatestamp():
    return str(datetime.datetime.now())


def getWorkerID():
    return '%s:%s' % (socket.gethostname(), os.getpid())


class ChangeLogReader:
      def __init__(self, mongoDBInstance, moduleTable, globalConfigSettings, segmentName=None):                    
          self.mongoInstance = mongoDBInstance
          self.modules = moduleTable
          self.globalSettings = globalConfigSettings
          self.segmentName = segmentName  
          self.chunkSize = 32 # TODO: remove this magic number
          

      def runSyncCommand(self, commandString):
            print '>>> running sync command: %s' % commandString
            syncCmdArray = commandString.split(' ')
            p = subprocess.Popen(syncCmdArray)
            procs.append(p)
            p.wait()
            print '>>> sync command returning result code %d.' % (p.returncode)
            return p.returncode            
            
            
      def generateSyncCommand(self, changeLogDBRecord):
            syncSource = changeLogDBRecord['path']
            moduleName = changeLogDBRecord['module_name']
            sourcePath = self.modules[moduleName].sourcePath
            targetPath = self.modules[moduleName].destPath
            pathFragment = syncSource.split(sourcePath)[1].lstrip('/')
            syncDest = os.path.dirname(os.path.join(targetPath, pathFragment))

            commandString = 'rsync %s %s %s' % (self.globalSettings.rsyncOptions, syncSource, syncDest)
            return commandString


      def findNFSPath(self, changeLogEntry):
            targetPath = self.modules[changeLogEntry.moduleName].destPath
            sourcePath = self.modules[changeLogEntry.moduleName].sourcePath
            syncSource = changeLogEntry.path
            pathFragment = syncSource.split(sourcePath)[1].lstrip('/')
            return os.path.join(targetPath, pathFragment)




      def resyncIncomplete(self, db, collection, shouldExecuteSync=False):
          queryDict = { 'sync_start': { '$ne': None }, 'worker_id': None, 'processed': False, 'deleted': False }
          if self.segmentName:
              queryDict['segment'] = self.segmentName

          workingSet = self.markRecordsActive(queryDict, -1, db, collection)
          
          count = 0
          for record in workingSet:
              recordID = record['_id']
              print 'reprocessing delta log record ID %s...' % recordID
              syncCmd = self.generateSyncCommand(record)
              print 'generated sync command %s' % syncCmd

              if shouldExecuteSync:                  
                  # perform the sync
                  if self.syncSingleRecord(record, db, collection):                  
                      print 'sync command successful.'
                      # mark this record as complete (unset the worker ID and set the sync end time)
                      if self.markSingleRecordComplete(recordID, db, collection):
                          count = count + 1
                  else:
                      print 'sync command failed.'
                      self.markSingleRecordInactive(recordID, db, collection) # just unset the worker ID
          print 'reprocessed %d delta log records.' % count


      def generateDateSubquery(self, dateWindow):
          print 'processing records inside date window %s...' % dateWindow
          dateSubquery = {}
          startDate = str(dateWindow.startDate)
          endDate = str(dateWindow.endDate)

          dateWindow = {}
            
          if not startDate:
              dateSubquery = { '$lte': endDate }
          elif not endDate:
              dateSubquery = { '$gte': startDate }
          else:
              dateSubquery = { '$gte': startDate, '$lte': endDate }

          return dateSubquery


      def markRecordsActive(self, queryDict, readingFrameSize, db, collection):
          print 'querying change log DB with query: %s...' % queryDict
          cursor = self.mongoInstance.query(queryDict, db, collection)
          if readingFrameSize > 0: # -1 means no limit
              cursor.limit(readingFrameSize)
          try:
              workerID = getWorkerID()
              workingSet = []
              for record in cursor:
                  markStatus = self.mongoInstance.update(record['_id'], { 'worker_id' : workerID }, db, collection)
                  if markStatus.didUpdateDB():
                      workingSet.append(record)
                  else:
                      sys.stderr.write('error marking record %s as in-progress: %s. Skipping...\n' % (record['_id'], markStatus))
                      sys.stderr.flush()
                      continue
              return workingSet
          
          finally:
              cursor.close()


      def markSingleRecordComplete(self, recordID, db, collection):
          success = True
          updateInfo = {}
          updateInfo['sync_end'] = currentDatestamp()
          updateInfo['processed'] = True      
          updateInfo['worker_id'] = None
          updateStatus = self.mongoInstance.update(recordID, updateInfo, db, collection)

          if not updateStatus.didUpdateDB() :
              sys.stderr.write('error marking record %s as complete: %s.\n' % (recordID, updateStatus))
              sys.stderr.flush()
              success = False
              
          return success


      def markSingleRecordInactive(self, recordID, db, collection):
          success = True
          updateInfo = {}            
          updateInfo['worker_id'] = None
          updateStatus = self.mongoInstance.update(recordID, updateInfo, db, collection)

          if not updateStatus.didUpdateDB() :
              sys.stderr.write('error marking record %s as inactive: %s.\n' % (recordID, updateStatus))
              sys.stderr.flush()
              success = False
              
          return success          

              
      def syncSingleRecord(self, changeLogRecord, db, collection):
          recordID = changeLogRecord['_id']
          updateInfo = {}
          updateInfo['sync_start'] = currentDatestamp()
          updateStatus = self.mongoInstance.update(changeLogRecord['_id'], updateInfo, db, collection)
          if not updateStatus.didUpdateDB() :
              sys.stderr.write('error updating start time for record %s:  %s.\n' % (record['_id'], updateStatus))
              sys.stderr.flush()
              return False

          success = True    
          print 'syncing...'
          
          syncCmd = self.generateSyncCommand(changeLogRecord)
          resultCode = self.runSyncCommand(syncCmd)
          
          if not resultCode:
              print 'sync command successful.'
          else:
               success = False

          return success
                  


      def syncChangeRecords(self,                                                                         
                        shouldExecuteSync = False,
                        dateWindow = None,
                        replayLimit = -1):

          numRecordsRead = 0          

          queryDict = { 'processed': False, 'deleted': False, 'sync_start': None, 'worker_id': None }
          if self.segmentName:
              queryDict['segment'] = self.segmentName
          if dateWindow:                      
              queryDict['date'] = self.generateDateSubquery(dateWindow)
      
          db = settings.DB_NAME
          collection = settings.COLLECTION_NAME

          if shouldExecuteSync:
              print 'reprocessing incomplete entries...'
              self.resyncIncomplete(db, collection, shouldExecuteSync)
          
          count = 0
          previewCount = 0

          while True:
              # mark a chunk of records as active (so other procs don't try to sync them too)
              
              activeRecords = self.markRecordsActive(queryDict, 32, db, collection) # TODO: remove this magic number
              print 'marked %d records as active.' % len(activeRecords)
              if not len(activeRecords):
                  break
                  
              for record in activeRecords:
                  recordID = record['_id']
                  print 'processing delta log record: \n%s' % record
                      
                  if shouldExecuteSync:
                      syncResult = self.syncSingleRecord(record, db, collection)
                      if syncResult:
                          count = count + 1
                          self.markSingleRecordComplete(recordID, db, collection)
                      else:
                          print 'error syncing change log record %s.' % record['_id']
                          self.markSingleRecordInactive(recordID, db, collection)
                  else:
                      cmd = self.generateSyncCommand(record)
                      print 'previewing sync command for record %s: %s' % (record['_id'], cmd)
                      previewCount = previewCount + 1
                      self.markSingleRecordInactive(recordID, db, collection)
                  
                      
          if shouldExecuteSync:
              print 'processed %d delta log records.' % count
          else:
              print 'previewed %d delta sync commands.' % previewCount
          
         
      



class OpLogEntry:
      def __init__(self, changeLogLineNumber, syncCommand, logDate, startTime, endTime=None):
            self.lineNumber = int(changeLogLineNumber)
            self.syncCommand = syncCommand
            self.logDate = logDate
            self.startTime = startTime
            if endTime and not len(endTime):
                  self.endTime = None
            else:
                  self.endTime = endTime

      def setStartTime(self, startTime):
            self.startTime = str(startTime)

      def setEndTime(self, endTime):
            self.endTime = str(endTime)

      def isComplete(self):
            return self.endTime != None
            
            
      def __repr__(self):
            if self.endTime:
                  return 'start:%d,%s,%s,%s&end:%s' % (self.lineNumber, self.syncCommand, self.logDate, self.startTime, self.endTime)
            return 'start:%d,%s,%s,%s&' % (self.lineNumber, self.syncCommand, self.logDate, self.startTime)
                  



class OpLogParser:
      def __init__(self):
            pass

      def parseLogEntry(self, logText):
            print '>>> Parsing completion log entry: %s' % logText
            logText = logText.strip()
            endMarkerIndex = logText.find('&')
            startMarker = logText[0:endMarkerIndex]
            startMarkerFields = startMarker.split('start:')[1].split(',')
            lineNumber = int(startMarkerFields[0])
            syncCommand = startMarkerFields[1]
            logDate = startMarkerFields[2]
            startTime = startMarkerFields[3]

            endMarker = logText[endMarkerIndex:]
            endTime = None
            if ':' in endMarker:
                  endTime = endMarker.split('end:')[1]            
            return OpLogEntry(lineNumber, syncCommand, logDate, startTime, endTime)
            

class FileLock():
      def __init__(self, filename, timeout=0):
            self.filename = filename            
            self.locked = False
            self.timeout = 0
            

      def acquire(self):
            if os.path.exists(self.filename):
                  self.locked = False
            else:
                  with open(self.filename, 'w') as lockfile:
                        lockfile.write('lock acquired at %s by PID %s' % (datetime.datetime.now(), os.getpid()))
                        self.locked = True
            return self.locked

      
      def release(self):
            if not os.path.exists(self.filename):
                  self.locked = False
                  return                        

            os.remove(self.filename)
            self.locked = False
              

                

def loadInitfile(filename):
      config = None
      with open(filename, 'r') as initfile:
            config = yaml.load(initfile)
            
      return config
 

def main(argv):
      parser = argparse.ArgumentParser(description='Sync change data between two locations, using mongoDB source')
      parser.add_argument('initfile')
      parser.add_argument('--segment', metavar='segment', nargs=1, required=True, help='distribution pool segment')
      parser.add_argument('-p', action='store_true', required=False, help='preview (show but do no execute) sync commands')

      args = parser.parse_args(argv)

      timestamp = datetime.datetime.now()
      host = socket.gethostname()

      print '>>> syncfsdelta started at %s on host %s.' % (timestamp, host)

      initFilename = args.initfile
      yamlConfig = loadInitfile(initFilename)

      if bool(yamlConfig['globals'].get('disabled')) == True:
            print 'detected disabled flag in syncfsdelta init file. Exiting.'
            exit()


      modules = getConfigModules(yamlConfig)
      globalSettings = getGlobalSettings(yamlConfig)

      
      previewMode = False
      if args.p is not None:
            previewMode = bool(args.p)            
            if previewMode: 
                  print '>>> running syncfsdelta in preview mode. Sync commands will be shown but not executed.'
      else:
            print '>>> running syncfsdelta in normal mode. Sync commands will be executed.'


      segment = args.segment[0]
      mongoInstance = createMongoInstance(yamlConfig)
      try:
          shouldRunSync = not previewMode
          clr = ChangeLogReader(mongoInstance, modules, globalSettings, segment)
          clr.syncChangeRecords(shouldRunSync, None, -1)
      except Exception, err:
          print 'Error syncing change log records: %s'  % err
          print traceback.format_exc()
      finally:
            timestamp = datetime.datetime.now()
            print '>>> syncfsdelta terminated at %s on host %s.' % (timestamp, host)


if __name__ == '__main__':
      main(sys.argv[1:])
      

