
for i in `awk -F ' ' '{ if ( $1 ~ /[0-9{1,3}].[0-9{1,3}].[0-9{1,3}].[0-9{1,3}]/ ) print $1 }' /proc/net/arp` ;
do
    arp -d $i
done
