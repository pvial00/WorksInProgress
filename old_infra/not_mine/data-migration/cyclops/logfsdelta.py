#!/usr/bin/env python
 
 
import os, sys
import time, datetime
import argparse
import yaml
import logfsdelta_mdb as logmdb
import traceback
 


def writeChangeRecord(changeRecord, logfileName, lockfileName):
    log = logmdb.DeltaLog(logfileName)
    try:
        log.writeChangeRecord(changeRecord)    
        return True
    except Exception, err:
        print '%s while attempting to update change log. %s' % (type(err).__name__, err.message)
        print traceback.format_exc()
        return False

 

def logChangedFolder(folder, config_filename, module_name):
    yamlConfig = logmdb.readInitfile(config_filename)
    

    moduleTable = logmdb.getConfigModules(yamlConfig)
    globalConfig = logmdb.getGlobalSettings(yamlConfig)
    
    targetModule = moduleTable.get(module_name)
    
    if not targetModule:
       raise Exception('Module "%s" not found in init file %s.' % (module_name, config_filename))
 
    if not folder.startswith(targetModule.sourcePath):
       raise Exception('The location %s is not covered by module "%s" in initfile %s. (module path: %s)' % (folder, module_name, config_filename, targetModule.sourcePath))
       
 
    changeRecord = logmdb.generateChangeRecord(folder, targetModule)
    print changeRecord
    
    # write filesystem-based log
    writeChangeRecord(changeRecord, globalConfig.logfileName, globalConfig.lockfileName)

    # write mongo-based log
    logmdb.logChangedFolder(folder, config_filename, module_name)

    
 

def main(argv):
    parser = argparse.ArgumentParser(description='Log filesystem changes from boinc ingest workflow')
 
    parser.add_argument('-i', metavar='initfile', nargs=1, required=True, help='YAML init file')
    parser.add_argument('-m', metavar='module', nargs=1, required=True, help='module name')
    parser.add_argument('path')
 
    args = parser.parse_args(argv)
 
    initfileName = args.i[0]
    filesystemChangeLocation = args.path
    targetModuleName = args.m[0]
    

    success = logChangedFolder(filesystemChangeLocation, initfileName, targetModuleName)
    if success:
        exit(0)
    else:
        print 'Error writing change record.'
        exit(1)
 
 
if __name__ == '__main__':
   main(sys.argv[1:])
