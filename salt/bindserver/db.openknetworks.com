;
; BIND data file for local loopback interface
;
$TTL	604800
@	IN	SOA	openknetworks.com. root.openknetworks.com. (
			      7		; Serial
			 604800		; Refresh
			  86400		; Retry
			2419200		; Expire
			 604800 )	; Negative Cache TTL
;
@	IN	NS	openknetworks.com.
@	IN	A	192.168.1.103
;@	IN	AAAA	::1
www	IN	A	192.168.1.103
mail	IN	A	192.168.1.103

