import os
import os.path
from os.path import join
import time
from datetime import datetime, timedelta

if __name__ == "__main__":
    root_folder = '/srv/originals/cdbaby/incoming/'

    counter = 0

    for root, dirs, files in os.walk(root_folder):
        if 'CDB_201404' in root or 'CDB_201403' in root or root==root_folder: 
            continue
        if counter > 1000:
            print '%s - batch done' % datetime.now()
            time.sleep(2)
            counter = 0
        else:
            counter += 1

        two_months_ago = datetime.now() - timedelta(days=60)
        dirtime = datetime.fromtimestamp(os.path.getctime(root))

        if dirtime < two_months_ago:
            for name in files:
                f = join(root,name)
                if f.endswith('.mp3') or f.endswith('.jpg'):
                    os.remove(f)