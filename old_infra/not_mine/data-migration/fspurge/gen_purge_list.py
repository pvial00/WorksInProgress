#!/usr/bin/env python

import re
import os, sys
import datetime 
import argparse
import xml.etree.ElementTree as ET
from dateutil import parser as dateparser


orchardRegex = r'[0-9]{8}_[0-9]{4}'

digitalpressureRegex = r'[0-9]{8}_[0-9]{7}'

emiRegex = r'[0-9]{17}'

ingroovesRegex = r'[0-9]{8}_[0-9]+'

iodaRegex = r'(beyondobliv)_[0-9]{4}_[0-9]{5}'
 
lacupulaRegex = r'(BNC)_[0-9]{14}_[0-9]{3}_[0-9]{3}_[0-9]{5}'

sonyRegex = r'[0-9]{17}'

wmgRegex = r'[0-9]{17}'

hungamaRegex = r'(HUND)_[0-9]{4}.[0-9]{2}.[0-9]{2}.[0-9]{2}.[0-9]{2}'

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

contentFeedPaths = {}
contentFeedPaths['orchard'] = '/srv/nfs3/originals/orchard/feed'
contentFeedPaths['sony'] = '/srv/nfs1/originals/sony/incoming'
contentFeedPaths['ioda'] = '/srv/nfs1/originals/ioda/'
contentFeedPaths['digitalpressure'] = '/srv/nfs1/originals/digitalpressure/new_releases'
contentFeedPaths['emi'] = '/srv/nfs1/originals/emi'
contentFeedPaths['wmg'] = '/srv/nfs1/originals/wmg/brandnew_releases'
contentFeedPaths['ingrooves'] = '/srv/nfs1/originals/ingrooves/incoming'
contentFeedPaths['lacupula'] = '/srv/nfs1/originals/lacupula/new_releases'
contentFeedPaths['empire'] = '/srv/nfs1/originals/empire/incoming'
contentFeedPaths['umg'] = '/srv/nfs1/originals/umg/feed_new'
contentFeedPaths['hungama'] = '/srv/nfs1/originals/hungama/incoming'
contentFeedPaths['warner'] = '/srv/nfs1/originals/warner/combined'

# contentFeedPaths['lacentral'] = '/srv/nfs1/originals/lacentral' #-- no content
# contentFeedPaths['saregama'] = '/srv/originals/saregama/incoming' #-- no content


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
dateRoutines['ingrooves'] = ingroovesDateFromFilename
dateRoutines['lacupula'] = lacupulaDateFromFilename
dateRoutines['wmg'] = wmgDateFromFilename
dateRoutines['warner'] = warnerDateFromFilename

def deriveDateFromFilename(name, labelName):
    function = dateRoutines.get(labelName)
    if not function:
        return None
   
    return function(name)



class Delivery():
    def __init__(self, orderID, date, assetMap):
        self.orderID = orderID
        self.date = date
        self.assetMap = assetMap

    
    def __repr__(self):
        return 'media delivery# %s on %s' % (self.orderID, self.date)

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def compileUmgPurgeList(numDays):

    currentDate = datetime.datetime.now()
    cutoffDate = currentDate - datetime.timedelta(days = numDays)

    feedDirectory = contentFeedPaths['umg']
    xmlDirectory = 'Delivery_Messages'

    xmlPath = os.path.join(feedDirectory, xmlDirectory)
    xmlFiles = [f for f in os.listdir(xmlPath) if f.startswith('delivery')]
    
    orderIDs = []
    for xmlFilename in xmlFiles:        
        lastModifiedDate = modification_date(os.path.join(xmlPath, xmlFilename))
        if lastModifiedDate < cutoffDate:      
            orderID = xmlFilename.split('delivery_')[-1][0:-4]
            orderIDs.append(orderID)
        
    print '%d deliveries found with order dates outside the %d-day window.' % (len(orderIDs), numDays)

    candidateFeedDirs = os.listdir(feedDirectory)
    results = []
    for id in orderIDs:
        print('scanning delivery order ID # %s...' % id)
        for dir in candidateFeedDirs:            
            if dir.split('_')[1] == id:
                print('match found: %s' % dir)
                results.append(os.path.join(feedDirectory, dir))            

    return results




def compileContentPurgeList(numDays, labelName):
   
    purgeList = []

    if labelName == 'umg':
        return compileUmgPurgeList(numDays)


    feedDir = contentFeedPaths.get(labelName)
    if not feedDir:
        print '>>> no content feed directory registered to label %s.' % labelName
        return purgeList

    filenames = os.listdir(feedDir)
    currentDate = datetime.datetime.now()
    cutoffDate = currentDate - datetime.timedelta(days = numDays)

    for name in filenames:
        fqFilename = os.path.join(feedDir, name)
        if not os.path.isdir(fqFilename):
            continue
       
        if not verifyFilenameFormat(name, labelName):
            continue

        fileDate = deriveDateFromFilename(name, labelName)
        
        if fileDate:            
            if fileDate < cutoffDate:
                purgeList.append(fqFilename)
        else:
            print '>>> no date parsing routine registered to label %s.' % labelName
    return purgeList



def main(argv):
    parser = argparse.ArgumentParser(description='Generate list of files to purge, by label')
    parser.add_argument('label_name')
    args = parser.parse_args()


    labelName = args.label_name

    filesToDelete = compileContentPurgeList(90, labelName)
    print '%d targets found under label %s outside the 90-day window.' % (len(filesToDelete), labelName)

    for f in filesToDelete:
        print f



if __name__ == '__main__':
    main(sys.argv[1:])



