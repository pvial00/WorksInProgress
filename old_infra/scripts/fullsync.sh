#!/bin/bash
myhome=`pwd`
host=`hostname --short`
dirs=`cat $myhome/$host.conf`
d=`date +%Y%m%d`

for i in $dirs;
do
	env HOME="$myhome" unison -logfile $myhome/$i/$host-$i-$d.log $myhome/$i/media$i.prf &
done
exit
