#!/bin/bash
cd /var/www/nconf/bin
if [ -f /srv/users/nrpe/addhost.tmp ]
	then
#	echo "Doesn't Exist!"
	/usr/bin/perl ./add_items_from_csv.pl -c host -f /srv/users/nrpe/addhost.tmp -d ","
#	/usr/bin/curl -silent -u icingaadmin:b3y0nd2010 http://nagios.prod.pnap.tx.boinc/nconf/generate_config.php
	rm /srv/users/nrpe/addhost.tmp
fi
