#!/bin/bash

user=""

while true
do
cnt=0
pids=`ps -ef | grep $user | awk '{ print $2 }'`

	for pid in $pids
	do
		if [ "$cnt" -ge 6 ]; then
			kill -9 $pid 2> /dev/null
		fi
		let cnt+=1
	done
	sleep 1
done
