#!/usr/bin/env python


import os, sys
import subprocess
import argparse
import time


def bounceInterface(interfaceName, pauseTime=0):
   downCmd = 'ifconfig %s down' % (interfaceName)
   upCmd = 'ifconfig %s up' % (interfaceName)
   
   cmdArray = downCmd.split(' ')
   p = subprocess.Popen(cmdArray)
   p.wait()

   print 'interface %s down. Waiting %d seconds...' % (interfaceName, pauseTime)
   
   time.sleep(pauseTime)

   print 'bringing interface %s back up.' % interfaceName
   
   cmdArray = upCmd.split(' ')
   p = subprocess.Popen(cmdArray)
   p.wait()
   

   



def main(argv):
    parser = argparse.ArgumentParser('Bring the specified interface down, then up')

    parser.add_argument('-p', metavar='pause_time', nargs=1, required=False, help='# of seconds to pause before bringing interface up')
    
    parser.add_argument('interface')
    args = parser.parse_args(argv)

    pauseTime = 0
    if args.p:
       pauseTime = int(args.p[0])
    
    bounceInterface(args.interface, pauseTime)



if __name__ == '__main__':
   main(sys.argv[1:])
