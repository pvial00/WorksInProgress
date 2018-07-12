#!/bin/bash
#Back up bind config Datestamped
tar -cvzf /tmp/ossec-$(date +%Y%m%d).tgz /var/ossec/
s3cmd put /tmp/ossec-$(date +%Y%m%d).tgz s3://boinc-ossec/
rm /tmp/ossec-$(date +%Y%m%d).tgz
