#!/bin/bash
#Back up bind config Datestamped
if [ `date +%d` != "01" ]
then
   if [ `date +%A` = "Friday" ]
   then
    tar -cvzf /srv/backups/weekly/bind-$(date +%Y%m%d).tgz /etc/bind/
   else
    tar -cvzf /srv/backups/daily/bind-$(date +%Y%m%d).tgz /etc/bind/
   fi
else
    tar -cvzf /srv/backups/monthly/bind-$(date +%Y%b%d).tgz /etc/bind/
fi
#DHCP Config Backup
if [ `date +%d` != "01" ]
then
   if [ `date +%A` = "Friday" ]
   then
    tar -cvzf /srv/backups/weekly/dhcpconf-$(date +%Y%m%d).tgz /etc/dhcp/dhcpd.conf
   else
    tar -cvzf /srv/backups/daily/dhcpconf-$(date +%Y%m%d).tgz /etc/dhcp/dhcpd.conf
   fi
else
    tar -cvzf /srv/backups/monthly/dhcpdconf-$(date +%Y%b%d).tgz /etc/dhcp/dhcpd.conf
fi
#Salt
if [ `date +%d` != "01" ]
then
   if [ `date +%A` = "Friday" ]
   then
    tar -cvzf /srv/backups/weekly/salt-$(date +%Y%m%d).tgz /etc/salt/
   else
    tar -cvzf /srv/backups/daily/salt-$(date +%Y%m%d).tgz /etc/salt/
   fi
else
    tar -cvzf /srv/backups/monthly/salt-$(date +%Y%b%d).tgz /etc/salt/
fi
#Salt States
if [ `date +%d` != "01" ]
then
   if [ `date +%A` = "Friday" ]
   then
    tar -cvzf /srv/backups/weekly/salt-srv-$(date +%Y%m%d).tgz /srv/salt/
   else
    tar -cvzf /srv/backups/daily/salt-srv-$(date +%Y%m%d).tgz /srv/salt/
   fi
else
    tar -cvzf /srv/backups/monthly/salt-srv-$(date +%Y%b%d).tgz /srv/salt/
fi
#Set ENV
export PASSPHRASE=b3y0nd0
export AWS_ACCESS_KEY_ID=AKIAI2CLKWTCE5RBJZGA
export AWS_SECRET_ACCESS_KEY=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

# Delete any older than 4 days in Daily bucket
# Delete any older than 4 weeks in Weekly bucket
# Delete any older than 4 Months in Monthly bucket
# Delete any older than 4 Years in Yearly bucket
duplicity full --volsize 5000 --no-encryption /srv/backups/daily/ s3+http://CMBackups/Daily
if [ `date +%A` = "Friday" ]
   then
    duplicity full --volsize 5000 --no-encryption /srv/backups/weekly/ s3+http://CMBackups/Weekly
fi
if [ `date +%d` != "01" ]
   then
    echo "Not first of the month." > /srv/backups/nfsbackup.txt
   else
    duplicity full --volsize 5000 --no-encryption /srv/backups/monthly/ s3+http://CMBackups/Monthly
fi
#duplicity full --volsize 5000 --no-encryption /srv/backups/yearly/ s3+http://CMBackups/Yearly
duplicity remove-older-than 4D --force s3+http://CMBackups/Daily
duplicity remove-older-than 4W --force s3+http://CMBackups/Weekly
duplicity remove-older-than 4M --force s3+http://CMBackups/Monthly
duplicity remove-older-than 4Y --force s3+http://CMBackups/Yearly

#Clear ENV
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export PASSPHRASE=

find /srv/backups/daily/* -mtime +15 -exec rm {} \;
