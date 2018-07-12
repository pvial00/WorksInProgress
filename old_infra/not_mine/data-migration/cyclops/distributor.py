#!/usr/bin/env python


import os, sys, socket
import argparse
import yaml
import logfsdelta
import datetime
import subprocess
import threading, time



# distributor.py




class ChangeLogSegment():
    def __init__(self, name, parentFilename):
        if not parentFilename.endswith('.log'):
            raise Exception('parent log file must have a .log extension.')
        
        tokens = parentFilename.split('.')
        self.filename = '%s_%s.%s' % (tokens[0], name, tokens[1])
        

    def __repr__(self):
        return self.filename


class ChangeRecordDistributor():
    def __init__(self, changeLogFilename, offsetLogFilename, segmentArray):
        self.segments = segmentArray
        self.changeLogFilename = changeLogFilename
        self.offsetLogFilename = offsetLogFilename
        self.active = False
        


    def readChunk(self, changeLogFile, recordsPerChunk, recordsRemaining):
        print 'reading %d records max from logfile %s; %d records remaining.' % (recordsPerChunk, changeLogFile, recordsRemaining)
        data = []
        
        for i in xrange(min(recordsPerChunk, recordsRemaining)):
            line = changeLogFile.readline()
            if line:                
                data.append(line.strip())

        return data


    def previewWritingChunkToSegment(self, chunk, changeLogSegment):
        print 'the following records would be written to satellite file %s:' % (changeLogSegment.filename)
        for data in chunk:
            print data


    def writeChunkToSegment(self, chunk, changeLogSegment):
        with open(changeLogSegment.filename, 'a+') as segmentFile:
            for data in chunk:
                segmentFile.write('%s\n' % data)



    def writeOffsetLog(self, offset):   
        with open(self.offsetLogFilename, 'a+') as offsetFile:
            offsetRecord = 'offset into change log file: %d' % offset
            offsetFile.write('%s\n' % offsetRecord)


    def run(self, **kwargs):
        previewMode = kwargs.get('preview_mode', False)

        self.active = True
    
        currentChangeLogLineNumber = 0
            
        # read offset from our own log
        with open(self.offsetLogFilename) as offsetLog:
            offsetRecords = offsetLog.readlines()
            if len(offsetRecords):
                if len(offsetRecords[-1].strip()) > 0:
                    print 'last offset record: %s' % offsetRecords[-1].strip()
                    currentRecord = offsetRecords[-1].strip()
                    currentChangeLogLineNumber = int(currentRecord.split(' ')[-1])
                else:
                    print 'no records in offset log!'
                    exit()
               
        
        print('current change log line: %d' % currentChangeLogLineNumber)


        wcOutput = subprocess.Popen(['wc', '-l', self.changeLogFilename], stdout=subprocess.PIPE).communicate()
        print wcOutput
        numLinesInChangeLog = int(wcOutput[0].strip().split(' ')[0])

        print '%d lines total in change log.' % numLinesInChangeLog

        numNewChangeLogRecords = 0
        if numLinesInChangeLog > currentChangeLogLineNumber:
            numNewChangeLogRecords = numLinesInChangeLog - currentChangeLogLineNumber

        print('there are %d new lines to distribute in the change log.' % numNewChangeLogRecords) 
        
        with open(self.changeLogFilename) as changeLog:
            # skip records in the change log file till we reach the start of the new records
            for i in xrange(currentChangeLogLineNumber):
                changeLog.readline()

            recordsRead = 0
            if numNewChangeLogRecords < len(self.segments):
                recordsPerSegment = numNewChangeLogRecords
            else:
                recordsPerSegment = numNewChangeLogRecords / len(self.segments)

            segmentIndex = 0
            while recordsRead < numNewChangeLogRecords:                
                chunk = self.readChunk(changeLog, recordsPerSegment, numNewChangeLogRecords-recordsRead)                
                recordsRead += len(chunk)
                print('%d records in chunk.' % len(chunk))
                currentSegment = self.segments[segmentIndex % len(self.segments)]
                if previewMode:
                    self.previewWritingChunkToSegment(chunk, currentSegment)
                else:
                    self.writeChunkToSegment(chunk, currentSegment)
                segmentIndex += 1
                

        print('read %s records from changelog.' % recordsRead)        
        currentChangeLogLineNumber += recordsRead        

        if previewMode:
            print 'new change log line offset is %d.' % currentChangeLogLineNumber
        else:
            self.writeOffsetLog(currentChangeLogLineNumber)
        

                                    
def main(argv):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('initfile')
    parser.add_argument('-p', action='store_true', required=False, help='preview (show but do no execute) distribution of change log records')
    args = parser.parse_args()

    initfileName = args.initfile
    previewMode = bool(args.p)

    if previewMode:
        print 'distributor will run in preview mode. No files will be updated.'
        
    segments = []
    changeLogFilename = None
    offsetLogFilename = None
    with open(initfileName) as initfile:
        config  = yaml.load(initfile)
        changeLogFilename = config['source_file']
        for segment in config['segments']:
            segments.append(ChangeLogSegment(segment, changeLogFilename))
        offsetLogFilename = config['offset_file']

    print('%d segments specified in initfile.' % len(segments))
    print('\n'.join([str(s) for s in segments]))

    dist = ChangeRecordDistributor(changeLogFilename, offsetLogFilename, segments)
    dist.run(preview_mode = previewMode)

    
        



if __name__ == '__main__':
   main(sys.argv[1:])

