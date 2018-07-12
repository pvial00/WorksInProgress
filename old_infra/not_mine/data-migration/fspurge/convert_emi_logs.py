#!/usr/bin/env python


import os, sys



def main():
    f = open('emi_purge_log.txt')
    outfile = open('emi_purge_list.txt', 'w')

    for line in f:
        tokens = line.split('/')
        if tokens:
            outputLine = tokens[len(tokens) -1]
            outfile.write(outputLine)
        

    f.close()
    outfile.close() 


if __name__ == '__main__':
    main()
