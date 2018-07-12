import MySQLdb, MySQLdb.cursors
import datetime
import os
import os.path
from os.path import join
from shutil import copytree, ignore_patterns
from pymongo import MongoClient
import time
from Queue import Queue
from threading import Thread

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception, e:
                print e
            finally:
                self.tasks.task_done()

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


class DoTheNeedful(object):        
    def process_UDID(self, log=None, total=None, index=None, src=None, dest=None):
        if os.path.exists(src):
            if not os.path.exists(dest):
                copytree(src, dest, ignore=ignore_patterns('*.mp3'))
            else:
                os.system("cp -rf %s %s" % (src, dest))

        log.write( "[%s of %s] %s to %s\n" % (index, total, src,dest))    
    
    def please(self):
        log = open('played_copy.' + str(datetime.datetime.now().strftime('%Y-%m-%d')) + '.log', 'w', 0)
        client = MongoClient('mongorep-playcount-01.prod.pnap.ny.boinc', 27017)
        db = client.playcount
        collection = db.month_plays
        
        log.write("[%s] Loading played albums from playcount database...\n" % datetime.datetime.now())
        
        results = db.month_plays.distinct("album_id")
            
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
            
            format_strings = ','.join(['%s'] * len(results))
            cursor.execute("select uuid from album_album where id in (%s)" % format_strings, tuple(results))
            
            for row in cursor:
                UUIDs.append(row.get('uuid'))
    
        finally:
            cursor.close()
        
         
        log.write( "[%s] Total UUIDs - %s\n" % (datetime.datetime.now(), len(UUIDs)))
        
        pool = ThreadPool(10)
        
        total = len(UUIDs)
        counter = 0
        
        for uuid in UUIDs:
            counter += 1
            
            #if counter % 100 == 0:
            #    log.write( "[%s] Processed - %d" % (datetime.datetime.now(), counter))        
            
            mfs_folder = join('/srv/media/media/albums',uuid[0:2],uuid[2:4],uuid[4:])
            nfs_folder = join('/srv/nfs2/media/albums',uuid[0:2],uuid[2:4],uuid[4:])
            
            
            pool.add_task(self.process_UDID, index=counter, total=total, log=log, src=mfs_folder, dest=nfs_folder)
            
        pool.wait_completion()
        
        log.write( "DONE! \n")
        
        log.close()
        
        
if __name__ == "__main__":
    DoTheNeedful().please()     