#!/bin/bash

host=$1
wget -q http://$host/ws/ConfigurationToken.xml
sed -e 's/.$//g' ConfigurationToken.xml > certfile
grep -A 18 X509Certificate certfile > regcert
sed 's/<X509Certificate>/-----BEGIN CERTIFICATE-----/' regcert > regcert2
sed 's/<\/X509Certificate>/-----END CERTIFICATE-----/' regcert2 > regcertfinal
sed 's/^.*-----BEGIN CERTIFICATE-----/-----BEGIN CERTIFICATE-----/' regcertfinal > rf
sed 's/-----END CERTIFICATE-----.*/-----END CERTIFICATE-----/' rf > rf2
sed 's/-----BEGIN CERTIFICATE-----/-----BEGIN CERTIFICATE-----\n/' rf2 > rf3
sed 's/-----END CERTIFICATE-----.*/\n&/' rf3 > rf4
validcheck=`openssl x509 -text -in rf4 | grep "Not After" | cut -d ':' -f 2,3,4 | cut -d ' ' -f 5`
validdate="2032"
if [ "$validcheck" = "$validdate" ];then
        echo "OK: Certificate Valid"
	rm ConfigurationToken.xml
	rm regcert* rf*
	exit 0
else
	echo "Critical: Certificate NOT Valid"
	rm ConfigurationToken.xml
	rm regcert* rf*
	exit 2
fi

