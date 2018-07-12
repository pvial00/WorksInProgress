#!/bin/bash
cd /var/www/nconf/bin
if [ -f /srv/users/nrpe/addhost.tmp ]
	then
#	echo "Doesn't Exist!"
	/usr/bin/perl ./add_items_from_csv.pl -c host -f /srv/users/nrpe/addhost.tmp -d ","
	rm /srv/users/nrpe/addhost.tmp
fi
