#!/bin/bash

service zabbix-server stop
ps -e | grep zabbix_server | awk '{ print $1 }' | xargs kill -9
service mysql stop
sleep 10
service mysql start
sleep 10
mysql --password=zabbix zabbix < /root/truncate.sql
sleep 10
service zabbix-server start
