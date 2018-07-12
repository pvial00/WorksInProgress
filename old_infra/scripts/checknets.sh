#!/bin/bash
myip=
while IFS=$': \t' read -a line ;do
    [ -z "${line%inet}" ] && ip=${line[${#line[1]}>4?1:2]} &&
        [ "${ip#127.0.0.1}" ] && myip=$ip
  done< <(LANG=C /sbin/ifconfig)
echo "Coming from $myip"

result=0
nets=8

if ping -c 1 74.201.250.66; then
	((result++))
else
	echo "Unable to reach NY Cisco edge router"
fi

if ping -c 1 10.21.0.254; then
	((result++))
else
	echo "Unable to reach NY Juniper core switch"
fi

if ping -c 1 10.21.0.2; then
	((result++))
else
	echo "Unable to reach NY CM and Service VLAN"
fi

if ping -c 1 10.22.0.10; then
	((result++))
else
	echo "Unable to reach NY Moose Master and Storage VLAN"
fi

if ping -c 1 10.23.0.60; then
	((result++))
else
	echo "Unable to reach NY IPMI VLAN"
fi

if ping -c 1 10.66.0.1; then
	((result++))
else
	echo "Unable to reach TX Cisco Edge Router"
fi

if ping -c 1 10.66.0.4; then
	((result++))
else
	echo "Unable to reach TX Turboiron Core Switch"
fi

#if ping -c 1 10.65.0.252; then
#	((result++))
#else
#	echo "Unable to reach TX Turboiron Core Switch Agile router gateway"
#fi

if ping -c 1 172.31.65.1; then
	((result++))
else
	echo "Unable to reach TX Agile VLAN Salt Master"
fi

if [ $result != $nets ]; then
	newresult=$(echo "$nets - $result"|bc)
	echo "$newresult networks were unable to be reached"
else
	echo ""
	echo "SUCCESS:  ALL NETWORKS AVAILABLE"
fi
