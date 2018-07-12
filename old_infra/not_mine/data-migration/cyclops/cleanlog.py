#!/usr/bin/env python

import subprocess
import os, sys
import time, datetime
import argparse


def rmDuplicates(entries):
    results = []
    index = 0
    while index < len(entries):
        currentEntry = entries[index]
        results.append(entries[index])
        if index < len(entries) - 1:            
            if entries[index+1].startswith(currentEntry.split(',')[0]):
                index += 1
        index += 1
    return results




def main(argv):
    

    parser = argparse.ArgumentParser(description='Clean completion log')

    parser.add_argument('completion_logfile')
    args = parser.parse_args()

    logfile = args.completion_logfile

    cleanEntries = []
    with open(logfile) as log:
        for line in log.readlines():
            line = line.strip()
            if line.startswith('start:'):
                if line.find('start') == line.rfind('start'):
                    cleanEntries.append(line)
                else:
                    ampIndex = line.find('&')                    
                    cleanEntries.append(line[ampIndex+1:])
                

    

    print '\n'.join(rmDuplicates(cleanEntries))


if __name__ == '__main__':
   main(sys.argv[1:])
