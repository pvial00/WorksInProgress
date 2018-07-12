#!/bin/bash
#BH 4/26/13 apiserverPublish.sh:  scp this script to api instance for a git-fetch from the latest master branch
#set -x
echo "Deploying latest code on "$2" instance(s)" 
echo "sleeping for "$1" seconds (in case github needs some buffer time before the fetch)"
sleep $1
for i in `echo $2`
do
server="$i"
echo "remoting into "$server
scp ~/remotePublisher.sh beyond@`echo $server`:/home/beyond/
ssh -t -t -v beyond@`echo $server` exec `echo /home/beyond/remotePublisher.sh $2 $3`
done
exit
