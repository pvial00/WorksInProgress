#!/usr/bin/env python


import os, sys
import argparse
import socket


def main(argv):
    parser = argparse.ArgumentParser(description='generate cron job entries for syncfsdelta satellite procs')

    parser.add_argument('label')
    args = parser.parse_args()

    label = args.label
    hostID = socket.gethostname().split('.')[0]



    scheduleField = '15      *     *     *     *    '
    commandField = '/srv/users/dtaylor/fspurge/fspurge.py -l %s 1>>/srv/users/dtaylor/fspurge/fspurge_%s_%s.log \
2>>/srv/users/dtaylor/fspurge/fspurge_%s_%s.err' % (label, label, hostID, label, hostID)


    print '%s%s\n' % (scheduleField, commandField)

    



if __name__== '__main__':
    main(sys.argv[1:])

