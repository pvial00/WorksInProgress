#!/bin/bash
#BH 4/26/13 remotePublisher.sh: script is scp'd and exec remotely on each api instance
set -x
echo "cd-time baby"
cd /opt/beyond/code
echo "now git fetch..."
git config --global user.email "tech@boinc.com"
git config --global user.name "Jenkins Boinc"
##copy settings file
if [[ "$1" == *partner* ]]
then
        git reset --hard origin/develop
        git fetch git@github.com:BoincMusic/apiserver.git develop
        git pull git@github.com:BoincMusic/apiserver.git develop
        cp /opt/beyond/code/externals/local_drmsettings_partner.py /opt/beyond/code/externals/local_drmsettings.py
        cp /opt/beyond/code/api/beyond/local_cache_settings_partner.py /opt/beyond/code/api/beyond/local_cache_settings.py
        cp /opt/beyond/code/api/beyond/local_settings_partner.py /opt/beyond/code/api/beyond/local_settings.py
elif [[ "$1" == *prod* ]]
then
        git reset --hard origin/master
        git fetch git@github.com:BoincMusic/apiserver.git master
        git pull git@github.com:BoincMusic/apiserver.git master
        cp /opt/beyond/code/externals/local_drmsettings_prod.py /opt/beyond/code/externals/local_drmsettings.py
        cp /opt/beyond/code/api/beyond/local_cache_settings_prod.py /opt/beyond/code/api/beyond/local_cache_settings.py
        cp /opt/beyond/code/api/beyond/local_settings_prod.py /opt/beyond/code/api/beyond/local_settings.py
        #sudo pip install -r /opt/beyond/code/api/requirements.txt --download-cache /tmp/
elif [[ "$1" == *qa* ]]
then
        git reset --hard origin/master
        git fetch git@github.com:BoincMusic/apiserver.git master
        git pull git@github.com:BoincMusic/apiserver.git master
        cp /opt/beyond/code/externals/local_drmsettings_dev.py /opt/beyond/code/externals/local_drmsettings.py
        cp /opt/beyond/code/api/beyond/local_cache_settings_dev.py /opt/beyond/code/api/beyond/local_cache_settings.py
        cp /opt/beyond/code/api/beyond/local_settings_dev.py /opt/beyond/code/api/beyond/local_settings.py
        #sudo pip install -r /opt/beyond/code/api/requirements.txt --download-cache /tmp/
else
        git reset --hard origin/develop
        git fetch git@github.com:BoincMusic/apiserver.git develop
        git pull git@github.com:BoincMusic/apiserver.git develop
        cp /opt/beyond/code/externals/local_drmsettings_dev.py /opt/beyond/code/externals/local_drmsettings.py
        cp /opt/beyond/code/api/beyond/local_cache_settings_dev.py /opt/beyond/code/api/beyond/local_cache_settings.py
        cp /opt/beyond/code/api/beyond/local_settings_dev.py /opt/beyond/code/api/beyond/local_settings.py
        #sudo pip install -r /opt/beyond/code/api/requirements.txt --download-cache /tmp/
fi
echo "installing new requirements (if any)..."
if [ -n "$2" ]
then
        for i in `echo $i2`
        do
        sudo pip2 install $i
        done
        echo "requirements up to date."
fi
echo "restart the wsgi"
#~/restart_uwsgi.sh
#sudo kill -HUP `cat /var/run/uwsgi/api.pid`
#sudo /etc/rc.d/api restart
echo "mercy-flush the cache!"
echo "flush_all" | netcat 127.0.0.1 11211 &
exit 0
