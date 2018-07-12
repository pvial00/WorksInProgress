#!/bin/bash

# generate the nsupdate config
host=`hostname --fqdn`
domain=`hostname --fqdn | cut -d '.' -f 2,3,4,5`
myip=`ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`
printf "server cm.pnap.tx.boinc\nzone $domain\nupdate delete $host. A\nupdate add $host. 86400 A $myip\nsend\n" > /root/update.txt

# update bind
nsupdate -k /root/Kboinc.com.+157+39859.private -v /root/update.txt
