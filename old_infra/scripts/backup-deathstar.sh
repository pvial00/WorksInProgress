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
#OSSEC Config and Keys Backup
if [ `date +%d` != "01" ] 
then
   if [ `date +%A` = "Friday" ]
   then
	tar -cvzf //srv/backups/weekly/ossec-$(date +%Y%m%d).tgz /var/ossec/
   else
	tar -cvzf //srv/backups/daily/ossec-$(date +%Y%m%d).tgz /var/ossec/
   fi
else
	tar -cvzf //srv/backups/monthly/ossec-$(date +%Y%b%d).tgz /var/ossec/
fi
#Backup LDAP
if [ `date +%d` != "01" ] 
then
   if [ `date +%A` = "Friday" ]
   then
	tar -cvzf /srv/backups/weekly/ldapconfig-$(date +%Y%m%d).tgz /usr/local/etc/openldap/
	tar -cvzf /srv/backups/weekly/ldapdb-$(date +%Y%m%d).tgz /var/db/openldap-data/
   else
	tar -cvzf /srv/backups/daily/ldapconfig-$(date +%Y%m%d).tgz /usr/local/etc/openldap/
	tar -cvzf /srv/backups/daily/ldapdb-$(date +%Y%m%d).tgz /var/db/openldap-data/
   fi
else
	tar -cvzf /srv/backups/monthly/ldapconfig-$(date +%Y%b%d).tgz /usr/local/etc/openldap/
	tar -cvzf /srv/backups/monthly/ldapdb-$(date +%Y%b%d).tgz /var/db/openldap-data/
fi
#Backup OpenVPN
if [ `date +%d` != "01" ] 
then
   if [ `date +%A` = "Friday" ]
   then
	tar -cvzf /srv/backups/weekly/openvpn-$(date +%Y%m%d).tgz /etc/openvpn/
   else
	tar -cvzf /srv/backups/daily/openvpn-$(date +%Y%m%d).tgz /etc/openvpn/
   fi
else
	tar -cvzf /srv/backups/monthly/openvpn-$(date +%Y%b%d).tgz /etc/openvpn/
fi

#Set ENV
export PASSPHRASE=b3y0nd0
export AWS_ACCESS_KEY_ID=AKIAI2CLKWTCE5RBJZGA
export AWS_SECRET_ACCESS_KEY=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

# Delete any older than 4 days in Daily bucket
# Delete any older than 4 weeks in Weekly bucket
# Delete any older than 4 Months in Monthly bucket
# Delete any older than 4 Years in Yearly bucket
duplicity full --volsize 5000 --no-encryption /srv/backups/daily/ s3+http://DSBackup/Daily
if [ `date +%A` = "Friday" ]
   then
    duplicity full --volsize 5000 --no-encryption /srv/backups/weekly/ s3+http://DSBackup/Weekly
fi
if [ `date +%d` != "01" ]
   then
    echo "Not first of the month." > /srv/backups/nfsbackup.txt
   else
    duplicity full --volsize 5000 --no-encryption /srv/backups/monthly/ s3+http://DSBackup/Monthly
fi
#duplicity full --volsize 5000 --no-encryption /srv/backups/yearly/ s3+http://DSBackup/Yearly
duplicity remove-older-than 4D --force s3+http://DSBackup/Daily
duplicity remove-older-than 4W --force s3+http://DSBackup/Weekly
duplicity remove-older-than 4M --force s3+http://DSBackup/Monthly
duplicity remove-older-than 4Y --force s3+http://DSBackup/Yearly

#Clear ENV
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export PASSPHRASE=

find /srv/backups/daily/* -mtime +15 -exec rm {} \;
