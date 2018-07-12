#!/bin/bash

while getopts h:a:b: option
do
	case "${option}"
	        in
	                h) hostname=${OPTARG};;
	                a) mac1=${OPTARG};;
	                b) mac2=${OPTARG};;
			?) echo "Usage: -h HOSTNAME -a -b Two MAC Addresses" && exit
										        esac
										done


cp -a -r /nfs/master /nfs/$hostname
ln -f -s $hostname $mac1
ln -f -s $hostname $mac2
rm /nfs/$hostname/etc/ssh/ssh_host_*
ssh-keygen -N '' -q -t dsa -f /nfs/$hostname/etc/ssh/ssh_host_dsa_key
ssh-keygen -N '' -q -t rsa -f /nfs/$hostname/etc/ssh/ssh_host_rsa_key
salt-key --gen-keys=$hostname
cp $hostname.pub /etc/salt/pki/master/minions/$hostname
cp $hostname.pem $hostname.pub /nfs/$hostname/etc/salt/pki/minion/
printf "127.0.0.1	localhost $hostname
10.21.0.2	salt
10.22.0.10	mfsmaster
" > /nfs/$hostname/etc/hosts
printf $hostname > /nfs/$hostname/etc/hostname

