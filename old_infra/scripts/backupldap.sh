tar -cvzf /tmp/ldapconfig$(date +%Y%m%d).tgz /usr/local/etc/openldap/
tar -cvzf /tmp/ldapdb$(date +%Y%m%d).tgz /var/db/openldap-data/
s3cmd put /tmp/ldap*.tgz s3://boinc-ldap/
#s3cmd put /tmp/ldapdb$(date +%Y%m%d).tgz s3://boinc-ldap/
rm /tmp/ldap*
