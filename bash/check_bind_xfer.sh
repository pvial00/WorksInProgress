#!/bin/bash
errors=`grep "xfer" /var/log/named/named.log | grep error `
host=`hostname --fqdn`

if [ -n "$errors" ];
then
	echo $errors | mail -s "$host: bind xfer errors" infra@boinc.com 
fi

