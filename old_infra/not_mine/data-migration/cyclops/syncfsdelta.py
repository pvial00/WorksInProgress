#!/usr/bin/env python



import os, sys
import socket
import argparse
import yaml
import logfsdelta
import logfsdelta_mdb
import datetime
import subprocess
import traceback
import logging
import atexit
import time


# global list of child processes
procs = []


#
# we kick off numerous child processes as part of the sync protocol, 
# so make sure we kill them all when we terminate
#
@atexit.register
def kill_subprocesses():
    for proc in procs:
        proc.kill()



def log_uncaught_exceptions(ex_cls, ex, tb):
      logging.critical(''.join(traceback.format_tb(tb)))
      logging.critical('{0}: {1}'.format(ex_cls, ex))


sys.excepthook = log_uncaught_exceptions




class OpLogEntry:
    '''Wraps the file-based sync completion log record

    '''
    
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
        '''Indicate the time we began syncing the current record

        '''

        self.startTime = str(startTime)


    def setEndTime(self, endTime):
        '''Indicate the time we finished syncing the current record

        '''
        self.endTime = str(endTime)


    def isComplete(self):
        '''Return false if the sync of this entry was interrupted

        '''
        return self.endTime != None
            
            
    def __repr__(self):
        if self.endTime:
            return 'start:%d,%s,%s,%s&end:%s' % (self.lineNumber, self.syncCommand, self.logDate, self.startTime, self.endTime)
        return 'start:%d,%s,%s,%s&' % (self.lineNumber, self.syncCommand, self.logDate, self.startTime)
                  



class OpLogParser:
      def __init__(self):
            pass

      def parseLogEntry(self, logText):
          '''Read a line from a filesystem delta log file and return a valid log entry object

          '''
          
          logText = logText.strip()

          # the start marker is written when sync begins, and is terminated with '&'          
          endMarkerIndex = logText.find('&')
          startMarker = logText[0:endMarkerIndex]
          startMarkerFields = startMarker.split('start:')[1].split(',')
          lineNumber = int(startMarkerFields[0])
          syncCommand = startMarkerFields[1]
          logDate = startMarkerFields[2]
          startTime = startMarkerFields[3]

          # end marker is everything from the '&' character to EOL
          endMarker = logText[endMarkerIndex:]

          endTime = None
          # endMarker will only have been written if the sync completed, otherwise we will assign
          # a null end time to this record
          #
          if ':' in endMarker:
              endTime = endMarker.split('end:')[1]            
          return OpLogEntry(lineNumber, syncCommand, logDate, startTime, endTime)
            


class FileLock():
    '''Wraps the lockfile mechanism used to prevent consecutive sync processes from stepping on each other

    '''
    def __init__(self, filename, timeout=0):
        self.filename = filename            
        self.locked = False
        self.timeout = 0
            

    def acquire(self):
        '''Create a lockfile and return True if no lockfile exists, otherwise return False

        '''
        if os.path.exists(self.filename):
            self.locked = False
        else:
            with open(self.filename, 'w') as lockfile:
                lockfile.write('lock acquired at %s by PID %s' % (datetime.datetime.now(), os.getpid()))
                self.locked = True
        return self.locked

      
    def release(self):
        '''Remove the lockfile and set our status to unlocked

        '''
        if not os.path.exists(self.filename):
            self.locked = False
            return                        

        os.remove(self.filename)
        self.locked = False
                       


class AutoSync():
    '''Performs the actual syncing from source to target filesystems based on delta log records

    '''
    def __init__(self, moduleTable, globalSettings):            
        self.modules = moduleTable
        self.globalSettings = globalSettings
        self.changeLogFilename = globalSettings.logfileName
        self.lock = FileLock(globalSettings.lockfileName)
        self.completionLogFilename = globalSettings.completionLogName
      

    def replayOplogEntry(self, entry): 
        '''Re-do a filesystem sync operation, typically an incomplete one

        '''
        print 'Rerunning completion log entry: %s' % (entry)
        syncCmdArray = entry.syncCommand.split(' ')
        p = subprocess.Popen(syncCmdArray)
        procs.append(p)
        p.wait()
        return p.returncode
            
            
    def readCompletionLog(self):
        '''Parse the data file that tells us which delta log records we have processed

        '''
        entries = []
        parser = OpLogParser()
        with open(self.completionLogFilename, 'r') as file:
            for line in file:
                entries.append(parser.parseLogEntry(line.strip()))
        return entries


    def replayCompletionLog(self):
        parser = OpLogParser()
        success = True
        logEntries = []

        # first, scan the completion log, whose last line should tell us where we are in
        # the delta log. 
        #
        with open(self.completionLogFilename, 'r+') as file:
            while True:
                line = file.readline().strip()
                if not line:
                    break
                entry = parser.parseLogEntry(line)
                if entry.isComplete():                            
                    logEntries.append(entry)
                else:
                    # replay entries with no end time

                    print '>>> entry is not complete: %s' % line
                    try:                                   
                        entry.setStartTime(datetime.datetime.now())
                        result = self.replayOplogEntry(entry)
                        if result == 0: # success            
                            entry.setEndTime(datetime.datetime.now())                                       
                        else:
                            print 'Error replaying completion log entry command %s'  % (entry.syncCommand)
                            success = False
                                   
                    except Exception, x:
                        print 'Exception replaying completion log entry command %s: %s' % (entry.syncCommand, x)
                        traceback.print_exc(file=sys.stdout)
                        success = False
                    finally:
                        logEntries.append(entry)

          # We will use the revised list of entries to rewrite the completion log
          #
        return logEntries
                        
                      
            
    def sync(self, **kwargs):    
            
        if not self.lock.acquire():
            # this means the lockfile is present; now make sure its parent proc 
            # is still alive
            lockPID = None
            with open(self.lock.filename, 'r') as lockfile:
                lockPID = lockfile.readline().split(' ')[-1] # process ID is the last token

            if os.path.exists('/proc/%s' % lockPID):  # parent is still running
                print 'lockfile %s present, exiting.' % self.lock.filename
                return
            else:       # parent must have died
                print 'lockfile %s present but parent process %s is no longer running; deleting orphan lockfile.' % (self.lock.filename, lockPID)
                os.remove(self.lock.filename)
                
        try:
            previewMode = kwargs.get('preview', False)
            completionLogEntries = []
            if not previewMode:
                    completionLogEntries.extend(self.replayCompletionLog())
                    self.rewriteCompletionLog(completionLogEntries)
                    print '>>> Finished replaying log.'
              
            lineCount = 0
            deltaLogEntries = None
            with open(self.changeLogFilename, 'r+') as logfile:
                    deltaLogEntries = logfile.readlines()
                    lineCount = len(deltaLogEntries)
    
            activeLineNumber = 1
            if len(completionLogEntries):
                    lastOperation = completionLogEntries[len(completionLogEntries) - 1]
                    activeLineNumber = lastOperation.lineNumber + 1
                  
            print '>>> Next changelog line number to process is %d.' % activeLineNumber
        
            parser = logfsdelta_mdb.DeltaLogRecordParser()
            # stop at the next-to-last line of the logfile
            for lineNumber in range(activeLineNumber, lineCount):  # stop at the penultimate line
                    print 'processing delta log, line number %d...' % (lineNumber)
                    currentEntry = deltaLogEntries[lineNumber - 1]
                    logRecord = parser.parseLogEntry(currentEntry)
                    print 'parsed log record # %d' % lineNumber
    
                    syncCommand = self.generateSyncCommand(logRecord)    
                                        
                    startTime = datetime.datetime.now()
                    
                    if previewMode:
                          print '>>> previewing sync cmd: %s\n' % syncCommand
                          continue
    
                    self.writeStartMarkerToCompletionLog(lineNumber, syncCommand, logRecord.date, startTime)
    
                    syncDest = syncCommand.split(' ')[-1]
                    if not os.path.exists(syncDest):
                          print '>>> sync target directory %s does not exist, creating...' % syncDest
                          p = subprocess.Popen(['mkdir', '-p', syncDest])
                          procs.append(p)
                          p.wait()
                          if not p.returncode == 0:
                                print '>>> error creating sync target directory %s' % syncDest
                                continue
                          
                    if self.runSyncCommand(syncCommand) == 0:                
                          endTime = datetime.datetime.now()
                          self.writeEndMarkerToCompletionLog(endTime)
                          print '>>> synchronized change record # %d.' % lineNumber
                    else:
                          print '>>> there was a problem running the sync command %s.' % syncCommand
                                    
        finally:
            self.lock.release()


    def writeStartMarkerToCompletionLog(self, changeLogLineNumber, syncCommand, dateStamp, startTime):
            newEntry = OpLogEntry(changeLogLineNumber, syncCommand, dateStamp, startTime)
            with open(self.completionLogFilename, 'a+') as completionLog:
                  completionLog.write(str(newEntry))



    def writeEndMarkerToCompletionLog(self, dateStamp):
            with open(self.completionLogFilename, 'a+') as completionLog:
                  completionLog.write('end:%s\n' % dateStamp)
            


    def runSyncCommand(self, commandString):
            print '>>> running sync command: %s' % commandString
            syncCmdArray = commandString.split(' ')
            p = subprocess.Popen(syncCmdArray)
            p.wait()
            print '>>> sync command returning result code %d.' % (p.returncode)
            return p.returncode            
            

            
    def generateSyncCommand(self, changeLogEntry):
            syncSource = changeLogEntry.path
            sourcePath = self.modules[changeLogEntry.moduleName].sourcePath
            targetPath = self.modules[changeLogEntry.moduleName].destPath
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



                
    def rewriteCompletionLog(self, opLogEntries):
            print '>>> Writing updated completion log...' 
            f = open(self.completionLogFilename, 'w+')
            f.truncate()
            for entry in opLogEntries:
                  f.write('%s\n' % str(entry))
            f.close()
                  
                  
              

                

def loadInitfile(filename):
    config = None
    with open(filename, 'r') as initfile:
        config = yaml.load(initfile)
            
    return config
 

def main(argv):
    parser = argparse.ArgumentParser(description='Sync change data between two locations')
    parser.add_argument('initfile')
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


    modules = logfsdelta_mdb.getConfigModules(yamlConfig)
    globalSettings = logfsdelta_mdb.getGlobalSettings(yamlConfig)

      

    previewMode = False
    if args.p is not None:
            previewMode = bool(args.p)            
            if previewMode: 
                  print '>>> running syncfsdelta in preview mode. Sync commands will be shown but not executed.'
    else:
            print '>>> running syncfsdelta in normal mode. Sync commands will be executed.'


    try:
            autosync = AutoSync(modules, globalSettings)
            autosync.sync(preview=previewMode)

    finally:
            timestamp = datetime.datetime.now()
            print '>>> syncfsdelta terminated at %s on host %s.' % (timestamp, host)


if __name__ == '__main__':
      main(sys.argv[1:])
      

