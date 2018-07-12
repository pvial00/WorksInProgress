#!/usr/bin/env python

from __future__ import print_function
import os, sys, socket
import argparse
import yaml
import logfsdelta
from syncfsdelta import FileLock
import datetime
import subprocess
import threading, time
import re
import xml.etree.ElementTree as ET
from dateutil import parser as dateparser
from time import sleep
import atexit


procs = []

@atexit.register
def kill_subprocesses():
    for proc in procs:
        if proc.is_alive():
            proc.kill()




orchardRegex = r'[0-9]{8}_[0-9]{4}'

digitalpressureRegex = r'[0-9]{8}_[0-9]{7}'

emiRegex = r'[0-9]{17}'

ingroovesRegex = r'[0-9]{8}_[0-9]+'

iodaRegex = r'(beyondobliv)_[0-9]{4}_[0-9]{5}'
 
lacupulaRegex = r'(BNC)_[0-9]{14}_[0-9]{3}_[0-9]{3}_[0-9]{5}'

sonyRegex = r'[0-9]{17}'

wmgRegex = r'[0-9]{17}'

hungamaRegex = r'(HUND)_[0-9]{4}.[0-9]{2}.[0-9]{2}'

warnerRegex = r'[0-9]{17}'



feedItemRegexStrings = {}
feedItemRegexStrings['orchard'] = orchardRegex
feedItemRegexStrings['digitalpressure'] = digitalpressureRegex
feedItemRegexStrings['emi'] = emiRegex
feedItemRegexStrings['ingrooves'] = ingroovesRegex
feedItemRegexStrings['ioda'] = iodaRegex
feedItemRegexStrings['lacupula'] = lacupulaRegex
feedItemRegexStrings['sony'] = sonyRegex
feedItemRegexStrings['hungama'] = hungamaRegex
feedItemRegexStrings['wmg'] = wmgRegex
feedItemRegexStrings['warner'] = warnerRegex


contentFeedSourcePaths = {}
contentFeedSourcePaths['orchard'] = '/srv/originals/orchard/feed'
contentFeedSourcePaths['sony'] = '/srv/originals/sony/incoming'
contentFeedSourcePaths['ioda'] = '/srv/originals/ioda/'
contentFeedSourcePaths['digitalpressure'] = '/srv/originals/digitalpressure/new_releases'
contentFeedSourcePaths['emi'] = '/srv/originals/emi'
contentFeedSourcePaths['wmg'] = '/srv/originals/wmg/brandnew_releases'
contentFeedSourcePaths['ingrooves'] = '/srv/originals/ingrooves/incoming'
contentFeedSourcePaths['lacupula'] = '/srv/originals/lacupula/new_releases'
contentFeedSourcePaths['empire'] = '/srv/originals/empire/incoming'
contentFeedSourcePaths['umg'] = '/srv/originals/umg/feed_new'
contentFeedSourcePaths['hungama'] = '/srv/originals/hungama/incoming'
contentFeedSourcePaths['warner'] = '/srv/originals/warner/combined'
contentFeedSourcePaths['unisys'] = '/srv/originals/unisys/incoming'


contentFeedTargetPaths = {}
contentFeedTargetPaths['orchard'] = '/srv/nfs3/originals/orchard/feed'
contentFeedTargetPaths['sony'] = '/srv/nfs1/originals/sony/incoming'
contentFeedTargetPaths['ioda'] = '/srv/nfs1/originals/ioda/'
contentFeedTargetPaths['digitalpressure'] = '/srv/nfs1/originals/digitalpressure/new_releases'
contentFeedTargetPaths['emi'] = '/srv/nfs1/originals/emi'
contentFeedTargetPaths['wmg'] = '/srv/nfs1/originals/wmg/brandnew_releases'
contentFeedTargetPaths['ingrooves'] = '/srv/nfs1/originals/ingrooves/incoming'
contentFeedTargetPaths['lacupula'] = '/srv/nfs1/originals/lacupula/new_releases'
contentFeedTargetPaths['empire'] = '/srv/nfs1/originals/empire/incoming'
contentFeedTargetPaths['umg'] = '/srv/nfs1/originals/umg/feed_new'
contentFeedTargetPaths['hungama'] = '/srv/nfs1/originals/hungama/incoming'
contentFeedTargetPaths['warner'] = '/srv/nfs1/originals/warner/combined'
contentFeedSourcePaths['unisys'] = '/srv/nfs1/originals/unisys/incoming'


def verifyFilenameFormat(filename, labelName):
    result = False
    regexString = feedItemRegexStrings.get(labelName)
    if regexString:
        rx = re.compile(regexString)
        if rx.match(filename):
            result = True
    return result


def orchardDateFromFilename(filename):
    year = int(filename[0:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    return datetime.datetime(year = year, month=month, day=day)


def sonyDateFromFilename(filename):
    year = int(filename[0:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    return datetime.datetime(year = year, month=month, day=day)   


def emiDateFromFilename(filename):
    year = int(filename[0:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    return datetime.datetime(year = year, month=month, day=day)


def digitalpressureDateFromFilename(filename):
    year = int(filename[0:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    return datetime.datetime(year = year, month=month, day=day) 


def hungamaDateFromFilename(filename):
    year = int(filename[5:9])
    fields = filename.split('.')
    month = int(fields[1])
    day = int(fields[2])
    return datetime.datetime(year = year, month=month, day=day)


def ingroovesDateFromFilename(filename):
    year = int(filename[0:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    return datetime.datetime(year = year, month=month, day=day)


def lacupulaDateFromFilename(filename):
    year = int(filename[4:8])
    month = int(filename[8:10])
    day = int(filename[10:12])
    return datetime.datetime(year = year, month=month, day=day)


def warnerDateFromFilename(filename):
    year = int(filename[0:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    return datetime.datetime(year = year, month=month, day=day)     


def wmgDateFromFilename(filename):
    year = int(filename[0:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    return datetime.datetime(year = year, month=month, day=day)     


dateRoutines = {}
dateRoutines['orchard'] = orchardDateFromFilename
dateRoutines['sony'] = sonyDateFromFilename
dateRoutines['digitalpressure'] = digitalpressureDateFromFilename
dateRoutines['emi'] = emiDateFromFilename
dateRoutines['hungama'] = hungamaDateFromFilename
dateRoutines['ingrooves'] = ingroovesDateFromFilename
dateRoutines['lacupula'] = lacupulaDateFromFilename
dateRoutines['wmg'] = wmgDateFromFilename
dateRoutines['warner'] = warnerDateFromFilename



class UnsupportedLabelException(Exception):
    def __init__(self, labelName):
        Exception.__init__(self, 'No filename-date conversion routine registered for record label %s.' % labelName)



def deriveDateFromFilename(name, labelName):
    function = dateRoutines.get(labelName)
    if not function:
        raise UnsupportedLabelException(labelName)
   
    return function(name)




class ModuleServiceStatus():
    def __init__(self, isOK, **kwargs):
        self.isOK = isOK
        self.data = kwargs



class InvalidDateWindowException(Exception):
    def __init__(self, message):
        Exception.__init__(message)




class DateWindow():
    def __init__(self, startDate, endDate=None):
        if startDate > datetime.datetime.now():
            raise InvalidDateWindowException('start date cannot be in the future.')

        if endDate and startDate > endDate:
            raise InvalidDateWindowException('start date cannot be later than end date.')
        self.startDate = startDate
        self.endDate = endDate
        self.isOpenEnded = False
        if not self.endDate:
            self.isOpenEnded = True
            self.endDate = datetime.datetime.now()


    def covers(self, filename, recordLabelName):
        if not verifyFilenameFormat(filename, recordLabelName):
            print('>>> found invalid filename: %s. Skipping date logic.' % filename)
            return False

        fileDate = deriveDateFromFilename(filename, recordLabelName)
        if self.isOpenEnded:
            return fileDate >= self.startDate
        return fileDate >= self.startDate and fileDate <= self.endDate


    def __repr__(self):
        return 'from %s to %s' % (self.startDate, self.endDate) 


def compileUmgFileList(dateWindow):
    feedDirectory = contentFeedSourcePaths['umg']
    xmlDirectory = 'Delivery_Messages'

    xmlPath = os.path.join(feedDirectory, xmlDirectory)
    xmlFiles = [f for f in os.listdir(xmlPath) if f.startswith('delivery')]
    
    deliveries = []

    for xmlFilename in xmlFiles:
        tree = ET.parse(os.path.join(xmlPath, xmlFilename))
        root = tree.getroot()

        orderID = None
        orderDateString = None
        for child in root:        
            if child.tag == 'order_id':                
                orderID = child.text
                

            if child.tag == 'date':
                orderDateString = child.text

            if child.tag == 'asset_map':
                assetMap = child.text
 
        if orderID and orderDateString:
            orderDate = dateparser.parse(orderDateString)            
            if orderDate >= dateWindow.startDate:                
                deliveries.append(Delivery(orderID, orderDate, assetMap))    

    candidateFeedDirs = os.listdir(feedDirectory)
    results = []
    for delivery in deliveries:
        print('scanning delivery order ID # %s...' % delivery.orderID)
        for dir in candidateFeedDirs:
            print('scanning feed location %s...' % dir)
            if dir[15:] == delivery.orderID:
                print('match found.')
                results.append(dir)
            else:
                print('no match found.')

    return results
        

def compileFileList(dateWindow, recordLabelName):

    if recordLabelName == 'umg':
        return compileUmgFileList(dateWindow)

    feedPath = contentFeedSourcePaths.get(recordLabelName)
    if not feedPath:
        raise Exception('no content feed path registered for record label %s.' % recordLabelName)

    files = os.listdir(feedPath)
    results = [f for f in files if dateWindow.covers(f, recordLabelName)]
    results.sort()
    return results

    
    

class CompletionMonitor(threading.Thread):
    def __init__(self, completionService, completionCallback, **kwargs):
        threading.Thread.__init__(self)
        self.completionTestFunction =  getattr(__import__('cmonitor_plugins'), completionService)
        self.completionFunctionArgs = kwargs
        self.completionCallback = completionCallback


    def run(self):
        while True:
            time.sleep(1)
            if not self.completionTestFunction({}):
                print('completion function returned false, completion monitor sleeping...')
                continue
            break
        self.completionCallback()




class ContentSynchronizer():
    def __init__(self, recordLabelName, dateWindow, syncLogFilename, rsyncOptionArray=[], previewMode=False, regexFilter=None):        
        self.previewMode = previewMode              
        self.regexFilter = regexFilter
        self.recordLabelName = recordLabelName
        self.dateWindow = dateWindow
        self.rsyncOptions = ' '.join(rsyncOptionArray) 
        self.syncLogFilename = syncLogFilename
            
       
    def logSync(self, logfile, directory):
        print('pid %d synced %s feed dir %s with datestamp# %s' % (os.getpid(), self.recordLabelName, directory, deriveDateFromFilename(directory, self.recordLabelName)), file=logfile)
        logfile.flush()


    def generateRsyncCommand(self, filename):
        syncSource = os.path.join(contentFeedSourcePaths[self.recordLabelName], filename)
        syncTarget = contentFeedTargetPaths[self.recordLabelName]
        if not self.regexFilter:
            return 'rsync -v --progress %s %s %s' % (self.rsyncOptions, syncSource, syncTarget)

        return "rsync -v --progress -r --include=*/ --include=%s --exclude=* %s %s %s" % (self.regexFilter, self.rsyncOptions, syncSource, syncTarget)


    def run(self):  
        print('compiling list of feed subdirectories...')
        syncDirs = compileFileList(self.dateWindow, self.recordLabelName)
        
        if self.previewMode:
            for dir in syncDirs:
                print('showing sync command: %s' %  self.generateRsyncCommand(dir))

            return

        print('%d feed subdirectories found within date window %s.' % (len(syncDirs), self.dateWindow))

        with open(self.syncLogFilename, 'a') as logfile: 
            for dir in syncDirs:
                syncCmd = self.generateRsyncCommand(dir)
                                                  
                print('running sync command: %s' % syncCmd)

                commandArray = syncCmd.split(' ')                    
                p = subprocess.Popen(commandArray)
                procs.append(p)
                p.wait()
                print(p.communicate())
                sys.stdout.flush()
                syncCmdResult = p.returncode
                if syncCmdResult != 0:
                    print('Error. rsync returned %d.' % syncCmdResult)  
                    break
                    
                self.logSync(logfile, dir)
                


def getLastSyncDate(logfileName):
    with open(logfileName, 'r') as f:
        entries = f.readlines()
        lastDate =  entries[-1].split('#')[1].strip()
        return dateparser.parse(lastDate)


def startupMessage():
    return 'osync starting at %s on host %s...' % (datetime.datetime.now(), socket.gethostname())


def lockfileName(labelName):
    return 'osync_%s_%s.lock' % (labelName, socket.gethostname().split('.')[0])


def syncLogFilename(labelName):
    return 'osync_completed_%s.log' % labelName


def main(argv):
    parser = argparse.ArgumentParser(description = 'monitor content directory for changes')
    parser.add_argument('--label', metavar='record_label', nargs=1, required=True, help='record label name to sync')
    parser.add_argument('-p', action='store_true', required=False, help='preview (show but do no execute) sync commands')    
    parser.add_argument('--numdays', metavar='days_ago', nargs=1, required=False) 
    parser.add_argument('--logdir', metavar='log_dir', nargs=1, required=True)

    parser.add_argument('--nolock', action='store_true', required=False, help='do not obey locking semantics')

    parser.add_argument('-f', metavar='filter_regex', nargs=1, required=False)
    
    args = parser.parse_args()
    labelName = args.label[0]

    previewMode = bool(args.p)
    disableLocking = bool(args.nolock)

    print('disableLocking set to %s.' % disableLocking)
    
    filter = None
    if args.f:
        filter = args.f[0]
    
    print(startupMessage())
    print('preview mode set to %s.' % previewMode)

    
    logDirectory = args.logdir[0]
    
    
    lockFileFullPath = os.path.join(logDirectory, lockfileName(labelName))
    syncLogFullPath = os.path.join(logDirectory, syncLogFilename(labelName))

    print('lockfile: %s' % lockFileFullPath)
    print('sync log: %s' % syncLogFullPath)


    lock = FileLock(lockFileFullPath)
    

    if not disableLocking:
        if not lock.acquire():  
            print('lockfile %s present, exiting.' % lockFileFullPath)
            exit()
        else:
            print('lockfile %s created.' % lockFileFullPath)

    try:
        startDate = None
        currentDate = datetime.datetime.now()
        if args.numdays:
            startDate = currentDate - datetime.timedelta(days = int(args.numdays[0]))
       
        else:            
            print('No date range provided. osync will look for last completed sync record in %s...' % syncLogFullPath)
            if os.path.exists(syncLogFullPath):
                startDate = getLastSyncDate(syncLogFullPath)


        if not startDate:
            print('Error: no log present from previous sync. You must provide a start date.')
            lock.release()
            exit(1)
                                  
        window = DateWindow(startDate)
        cs = ContentSynchronizer(labelName, window, syncLogFullPath, ['-az'], previewMode, regexFilter=filter)         
        cs.run()
        
    except Exception, err:
        print("Error %s while starting thread" % err)
    finally:
        print('Releasing lock...')
        lock.release()


if __name__ == '__main__':
    main(sys.argv[1:])
