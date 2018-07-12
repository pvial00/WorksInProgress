import MySQLdb, MySQLdb.cursors
import datetime
import os
import os.path
from os.path import join
from shutil import copytree, ignore_patterns

if __name__ == "__main__":    
    log = open('copy.' + str(datetime.datetime.now().strftime('%Y-%m-%d')) + '.log', 'w', 0)
    log.write("[%s] Loading UUIDs from database...\n" % datetime.datetime.now())
    
    UUIDs = []
    try:
        db = MySQLdb.connect(host='db01.prod.pnap.ny.boinc', 
                               user='beyond', 
                               passwd="b3y0nd0", 
                               db="beyond", 
                               cursorclass = MySQLdb.cursors.SSDictCursor,
                               charset="utf8")
    
        cursor = db.cursor()
        cursor.execute("select * from album_album where created>'2014-03-01' and created<'2014-04-22'")
        
        for row in cursor:
            UUIDs.append(row.get('uuid'))

    finally:
        cursor.close()
        
    log.write( "[%s] Total UUIDs - %s\n" % (datetime.datetime.now(), len(UUIDs)))
    
    counter = 0
    missing_count = 0
    
    for uuid in UUIDs:
        counter += 1
        
        if counter % 100 == 0:
            log.write( "[%s] Processed - %d, Missing - %d\n" % (datetime.datetime.now(), counter, missing_count))        
        
        mfs_folder = join('/srv/media/media/albums',uuid[0:2],uuid[2:4],uuid[4:])
        nfs_folder = join('/srv/nfs2/media/albums',uuid[0:2],uuid[2:4],uuid[4:])
        
        if os.path.exists(mfs_folder) and not os.path.exists(nfs_folder):
            missing_count += 1
            copytree(mfs_folder, nfs_folder, ignore=ignore_patterns('*.mp3'))
    
    log.close()
    
        
        