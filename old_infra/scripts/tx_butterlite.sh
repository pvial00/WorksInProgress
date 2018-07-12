#!/bin/bash
#
#
vmpath=/mnt/vmtmp

while getopts n:h:c:m:e: option
do
        case "${option}"
        in
                n) fqdn=${OPTARG};;
                h) hyper=${OPTARG};;
                c) cpu=${OPTARG};;
                m) mem=${OPTARG};;
	        e) encode=$OPTARG;;
		?) echo "Usage: -n HOSTNAME -h HYPERVISOR -c CPUs -m RAM in MB" && exit
        esac
done
host=$(echo $fqdn | cut -d '.' -f 1)
hdom=$(echo $fqdn | cut -d '.' -f 1,2)

memkb=$(($mem * 1024))

#mac=`cat /home/kzander/mac.index`
#macfive=$(echo $mac | cut -d ':' -f 5)
#maclast=$(echo $mac | cut -d ':' -f 6)
#macfront=$(echo $mac | cut -d ':' -f 1,2,3,4)
#decmacfive=$(echo "ibase=16; $macfive"|bc)
#decmac=$(echo "ibase=16; $maclast"|bc)

#if [ $decmac -eq '255' ]; then
#        macinc='00'
#        if [ $decmacfive -eq '255' ]; then
#                macincfive='00'
#        else
#                incoutfive=`expr $decmacfive + 1 `
#                macincfive=$(echo "obase=16; $incoutfive"|bc)
#                macinccfive=$(printf %02d $macincfive)
#                echo "$macfront:$macinccfive:$macinc" > /home/kzander/mac.index
#        fi
#else
#        incout=`expr $decmac + 1 `
#        macinc=$(echo "obase=16; $incout"|bc)
#        macincc=$(printf %02d $macinc)
#        macinccfive=$macfive
#        echo "$macfront:$macinccfive:$macincc" > /home/kzander/mac.index
#fi


#newmac=`cat /home/kzander/mac.index`

domain=`echo "$fqdn" | cut -d '.' -f 2,3,4,5`

if [ -n "$fqdn" ] && [ -n "$hyper" ] && [ -n "$cpu" ] && [ -n "$mem" ]; then
	mkdir /srv/vm/home/$fqdn
	cp /srv/vm/provision/master/master.raw /srv/vm/home/$fqdn/$fqdn.raw
	if [ -n "$encode" ]; then
		qemu-img create -f raw /srv/vm/home/$fqdn/vdb.raw 15G
		#mkfs.ext4 /home/kzander/$fqdn/vdb.raw
		srvdata="    <disk type='file' device='disk'>
		      <driver name='qemu' cache='writeback' io='native'/>
		            <source file='/srv/vm/home/vm/$fqdn/vdb.raw'/>
			          <target dev='vdb' bus='virtio'/>
				      </disk>"

	fi
	losetup -o 32256 /dev/loop4 /srv/vm/home/$fqdn/$fqdn.raw
	mount /dev/loop4 $vmpath
	printf "127.0.0.1 localhost\n127.0.1.1 $fqdn $host\n10.21.0.2 salt\n10.22.0.10 mfsmaster\n10.21.69.9 db-01_prod.storage\n10.21.69.18 solr_prod\n10.21.69.6 solr-master-01_prod\nmq-vip.la.bo" > $vmpath/etc/hosts
	printf $fqdn > $vmpath/etc/hostname
	#mkdir -p $vmpath/etc/salt/pki/minion
	#salt-key --gen-keys=$fqdn
	#cp $fqdn.pem $vmpath/etc/salt/pki/minion/minion.pem
	#cp $fqdn.pub $vmpath/etc/salt/pki/minion/minion.pub
	#cp $fqdn.pub /etc/salt/pki/master/minions/
	#cp minion_master.pub $vmpath/etc/salt/pki/minion/
	#cp $vmpath/etc/salt/pki/minion/* $vmpath/etc/salt/pki/
	rm $vmpath/etc/ssh/ssh_host_*
	ssh-keygen -N '' -q -t dsa -f $vmpath/etc/ssh/ssh_host_dsa_key
	ssh-keygen -N '' -q -t rsa -f $vmpath/etc/ssh/ssh_host_rsa_key


	printf "option rfc3442-classless-static-routes code 121 = array of unsigned integer 8;\nsend host-name \"$hdom\";\n\nrequest subnet-mask, broadcast-address, time-offset, routers, domain-name, domain-name-servers, domain-search, host-name, netbios-name-servers, netbios-scope, inteface-mtu, rfc3442-classless-static-routes, ntp-servers" > $vmpath/etc/dhcp/dhclient.conf
	umount /dev/loop4
	losetup -d /dev/loop4
	else
		echo "Missing arguments" && exit
fi
newmac=`/srv/vm/provision/genmac.pl`
#newmac2=`/srv/vm/provision/genmac.pl`

printf "<domain type='kvm'>
  <name>$fqdn</name>
  <memory>$memkb</memory>
  <currentMemory>$memkb</currentMemory>
  <vcpu>$cpu</vcpu>
  <os>
    <type>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
  </features>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <emulator>/usr/bin/kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' cache='writeback' io='native'/>
      <source file='/srv/vm/home/$fqdn/$fqdn.raw'/>
      <target dev='hda' bus='virtio'/>
    </disk>
    $srvdata
    <interface type='bridge'>
      <source bridge='br0'/>
      <mac address='$newmac'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <input type='mouse' bus='ps2'/>
    <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
      <listen type='address' address='0.0.0.0'/>
    </graphics>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </memballoon>
    <serial type='pty'>
            <target port='0'/>
    </serial>
    <console type='pty'>
            <target type='serial' port='0' />
    </console>

  </devices>
</domain>" > $fqdn.xml
echo "*** Libvirt config generated***"
cp $fqdn.xml /srv/vm/instances/
#scp -r /home/kzander/$fqdn/ gozer@$hyper:/mnt/local/vm/

#if [ -f /home/kzander/$fqdn/vdb.raw ]
#then
#	scp /home/kzander/$fqdn/vdb.raw gozer@$hyper:/mnt/local/vm/$fqdn/
#fi

hyperhost=`printf $hyper | cut -d '.' -f 1`
hyperdom=".pnap.ny.boinc"
hyperfqdn=$hyperhost$hyperdom
virsh create /srv/vm/instances/$fqdn.xml
#salt $hyperfqdn cmd.run "'virsh create /srv/vm/instances/$fqdn.xml'"
echo "*** DONE ***"
