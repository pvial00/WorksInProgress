#!/bin/bash
iptables -F FORWARD
clients="/etc/openvpn/clients/ipp.txt"
while read line
do
	email=`echo $line | cut -d ',' -f 1`
	ip=`echo $line | cut -d ',' -f 2`
	echo $email
	echo $ip

	routes="/etc/openvpn/clients/$email"
	while read route
	do
		myroute=`echo $route | cut -d "\"" -f 2`
		net=`echo $myroute | cut -d " " -f 2`
		mask=`echo $myroute | cut -d " " -f 3`
		echo $myroute
		iptables -A FORWARD -s $ip -d $net/$mask -p all -j ACCEPT
		iptables -A FORWARD -s $net/$mask -d $ip -p all -j ACCEPT
		
	done < $routes
	
done <$clients
iptables -A FORWARD -s 10.66.0.25 -d 0.0.0.0/0 -p all -j ACCEPT
iptables -A FORWARD -s 10.66.0.20 -d 0.0.0.0/0 -p all -j ACCEPT
iptables -A FORWARD -s 10.66.6.200 -d 0.0.0.0/0 -p all -j ACCEPT
iptables -A FORWARD -s 0.0.0.0/0 -d 10.66.0.25 -p all -j ACCEPT
iptables -A FORWARD -s 0.0.0.0/0 -d 10.66.0.20 -p all -j ACCEPT
iptables -A FORWARD -s 0.0.0.0/0 -d 10.66.6.200 -p all -j ACCEPT
iptables -A FORWARD -s 10.10.10.0/24 -d 0.0.0.0/0 -p all -j ACCEPT
iptables -A FORWARD -s 10.66.6.103/0 -d 172.31.65.0/24 -p all -j ACCEPT
iptables -A FORWARD -s 172.31.65.0/24 -d 10.66.6.103/0 -p all -j ACCEPT
iptables -A FORWARD -s 0.0.0.0/0 -d 10.10.10.0/24 -p all -j ACCEPT
iptables -A FORWARD -j DROP
