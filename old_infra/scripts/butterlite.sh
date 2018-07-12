#!/bin/bash
#
#
home=/home/vm
vmpath=/mnt/vmtmp

if [[ $# -eq 0 ]] ; then
	echo "Usage: -n HOSTNAME -h HYPERVISOR -c CPUs -m RAM in MB"
        exit 1
fi

while getopts n:h:c:m:p:e:o:d:v: option
do
        case "${option}"
        in
                n) fqdn=${OPTARG};;
                h) hyper=${OPTARG};;
                c) cpu=${OPTARG};;
                m) mem=${OPTARG};;
	        p) cl=${OPTARG};;
	        e) encode=$OPTARG;;
                o) original=${OPTARG};;
	        d) destination=${OPTARG};;
	        v) vmname=$OPTARG;;
		?) echo "Usage: -n HOSTNAME -h HYPERVISOR -c CPUs -m RAM in MB" && exit
        esac
done

if [ -n "$original" ] && [ -n "$destination" ] && [ -n "$vmname" ]; then
saltdom=".pnap.ny.boinc"
scpdom=".stor.pnap.ny.boinc"

##check if vm running on original
ovmexists=$(salt $original$saltdom cmd.run 'virsh list' | grep $vmname | awk '{print $2}')
if [[ "$ovmexists" == "" ]];
   then
    echo "ERROR: $vmname is not running on host $original"
    exit 0
   else
    echo "$vmname is running on $original"
fi

##check if vm running on destination
dvmexists=$(salt $destination$saltdom cmd.run 'virsh list' | grep $vmname | awk '{print $2}')
if [[ "$dvmexists" != "" ]];
   then
    echo "ERROR: $vmname already running on host $destination"
   exit 0
   else
    echo "$vmname is not running on $destination"
#copy vm original -> dest
   origdirexists=$(salt $original$saltdom file.directory_exists "/srv/vm/tmp/$vmname" | grep False | awk '{ print $1}')
if [[ "$origdirexists" == "False" ]]; then
   echo "Copying from $original:/mnt/local/vm/$vmname to /srv/vm/tmp/"
   salt $original$saltdom cmd.run "cp -r /mnt/local/vm/$vmname /srv/vm/tmp/"
fi
   destdirexists=$(salt $destination$saltdom file.directory_exists "/mnt/local/vm/$vmname" | grep False | awk '{ print $1}')
if [[ "$destdirexists" == "False" ]]; then
   echo "Copying from /srv/vm/tmp/$vmname to $destination:/mnt/local/vm/"
   salt $destination$saltdom cmd.run "cp -r /srv/vm/tmp/$vmname /mnt/local/vm/"
fi
   echo "Copied from $original local storage to $destination local storage"
fi
#validate scp on dest side
dvmexists=$(salt $destination$saltdom cmd.run 'ls -al /mnt/local/vm/' | grep $vmname | awk '{print $9}')
if [[ "$dvmexists" == "" ]];
   then
    echo "Error: $vmname has not been copied to host $destination"
   exit 0
   else
    echo "$vmname now exists on $destination's Local Storage"
#live migrate
  echo "Bringing $vmname online"
   sshexists=$(salt $destination$saltdom file.directory_exists "/root/.ssh" | grep False | awk '{ print $1}')
if [[ "$sshexists" == "False" ]]; then
  salt $destination$saltdom cmd.run "ssh-keygen -f /root/.ssh/id_rsa -t rsa -N ''"
fi
  salt $destination$saltdom cmd.run "cp -f /srv/users/tempssh/* /root/.ssh/"
  salt $original$saltdom cmd.run "cp -f /srv/users/tempssh/* /root/.ssh/"
  salt $original$saltdom cmd.run "rm /root/.ssh/known_hosts"
  salt $original$saltdom cmd.run "ssh-keyscan -H $destination$scpdom >> /root/.ssh/known_hosts"
  salt $destination$saltdom cmd.run "echo $destination$scpdom > /etc/hostname;service hostname restart"
  salt $original$saltdom cmd.run "virsh migrate --live $vmname qemu+ssh://$destination$scpdom/system"
sleep 5
fi

#validate not running on original
ovmexists=$(salt $original$saltdom cmd.run 'virsh list' | grep $vmname | awk '{print $2}')
if [[ "$ovmexists" == "" ]];
   then
    echo "$vmname is not running on host $original"
   else
    echo "Still Running on $original"
fi

#validate access to running destination
dvmexists=$(salt $destination$saltdom cmd.run 'virsh list' | grep $vmname | awk '{print $2}')
if [[ "$dvmexists" == "" ]];
   then
    echo "Error: $dvmexists is not running on host $destination"
    exit 0
   else
    echo "$vmname is running on $destination. Cleaning up."
    salt $original$saltdom cmd.run "rm -rf /mnt/local/vm/$vmname"
    salt $original$saltdom cmd.run "rm -rf /srv/vm/tmp/$vmname"
    salt $original$saltdom cmd.run "rm /root/.ssh/authorized_keys"
    salt $destination$saltdom cmd.run "rm /root/.ssh/authorized_keys"

#echo success
echo "$vmname has been live migrated from $original to $destination and is running"
fi
exit 0

fi

if [ -z "$fqdn" ] && [ -z "$hyper" ] && [ -z "$cpu" ] && [ -z "$mem" ] && [ -z "$cl" ]; then
	echo "Not all arguments were given."
	exit
fi

if [ -n "$cl" ]; then
	rm /srv/vm/instances/$cl.xml
	rm -fR $home/$cl/
	rm /etc/salt/pki/master/minions/$cl.pub
	#salt 'node*' cmd.run "virsh shutdown $cl"
	echo "$cl cleaned"
	exit
fi

host=$(echo $fqdn | cut -d '.' -f 1)
hdom=$(echo $fqdn | cut -d '.' -f 1,2)

memkb=$(($mem * 1024))

origdirexists=$(salt '$hyper' file.directory_exists "/mnt/local/vm/"|grep False|awk '{ print $1}')
if [[ "$origdirexists" == "False" ]]; then
	echo "/mnt/local/vm doesn't exist on $hyper"
	exit 1
fi

if [ ! -d /srv/vm/instances ]; then
	echo "/srv/vm/instances doesn't exist"
	exit 1
fi

if [ ! -f $home/master/master.raw ]; then
	echo "Master VM is missing"
	exit 1
fi

if [ ! -f $home/minion_master.pub ]; then
	echo "$home/minion_master.pub is missing"
	exit 1
fi

if [ -f $home/$fqdn/$fqdn.raw ]; then
	echo "$home/fqdn/$fqdn.raw already exists"
	exit 1
fi

if [ -f /etc/salt/pki/master/minions/$fqdn.pub ]; then
	echo "Salt keys already exist"
	exit 1
fi

if [ -f /etc/salt/pki/master/minions/$fqdn.pub ]; then
	echo "Salt keys already exist"
	exit 1
fi

chkloop=`mount | grep loop4 | cut -d ' ' -f 1`
if [ ! -z $chkloop ]; then
	echo "/dev/loop4 is busy"
	exit 1
fi


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
	mkdir $home/$fqdn
	cp $home/master/master.raw $home/$fqdn/$fqdn.raw
	letr="G"
	if [ -n "$encode" ]; then
		qemu-img create -f raw $home/$fqdn/vdb.raw $encode$letr
		#mkfs.ext4 /home/kzander/$fqdn/vdb.raw
		srvdata="    <disk type='file' device='disk'>
		      <driver name='qemu' cache='writeback' io='native'/>
		            <source file='/mnt/local/vm/$fqdn/vdb.raw'/>
			          <target dev='vdb' bus='virtio'/>
				      </disk>"

	fi
	losetup -o 32256 /dev/loop4 $home/$fqdn/$fqdn.raw
	mount /dev/loop4 $vmpath
	printf "127.0.0.1 localhost\n127.0.1.1 $fqdn $host\n10.21.0.2 salt\n10.22.0.10 mfsmaster\n" > $vmpath/etc/hosts
	printf $fqdn > $vmpath/etc/hostname
	mkdir -p $vmpath/etc/salt/pki/minion
	salt-key --gen-keys=$fqdn
	cp $fqdn.pem $vmpath/etc/salt/pki/minion/minion.pem
	cp $fqdn.pub $vmpath/etc/salt/pki/minion/minion.pub
	cp $fqdn.pub /etc/salt/pki/master/minions/
	cp minion_master.pub $vmpath/etc/salt/pki/minion/
	cp $vmpath/etc/salt/pki/minion/* $vmpath/etc/salt/pki/
	rm $vmpath/etc/ssh/ssh_host_*
	ssh-keygen -N '' -q -t dsa -f $vmpath/etc/ssh/ssh_host_dsa_key
	ssh-keygen -N '' -q -t rsa -f $vmpath/etc/ssh/ssh_host_rsa_key
	newiffile=`awk -v var="$fqdn" '/hostname/ { print "hostname " var; next} 1' $vmpath/etc/network/interfaces`
	echo "$newiffile" > $vmpath/etc/network/interfaces


	printf "option rfc3442-classless-static-routes code 121 = array of unsigned integer 8;\n\ninterface \"eth0\" { \nsend host-name \"$hdom\";\n\n}\nrequest subnet-mask, broadcast-address, time-offset, routers, domain-name, domain-name-servers, domain-search, host-name, netbios-name-servers, netbios-scope, inteface-mtu, rfc3442-classless-static-routes, ntp-servers" > $vmpath/etc/dhcp/dhclient.conf
	umount /dev/loop4
	losetup -d /dev/loop4
	else
		echo "Missing arguments" && exit
fi
newmac=`$home/genmac.pl`
newmac2=`$home/genmac.pl`

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
      <source file='/mnt/local/vm/$fqdn/$fqdn.raw'/>
      <target dev='hda' bus='virtio'/>
    </disk>
    $srvdata
    <interface type='bridge'>
      <source bridge='virt_service'/>
      <mac address='$newmac'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <interface type='bridge'>
      <source bridge='storage'/>
      <mac address='$newmac2'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
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
scp -r $home/$fqdn/ gozer@$hyper:/mnt/local/vm/

if [ -f $home/$fqdn/vdb.raw ]
then
	scp $home/$fqdn/vdb.raw gozer@$hyper:/mnt/local/vm/$fqdn/
fi

hyperhost=`printf $hyper | cut -d '.' -f 1`
hyperdom=".pnap.ny.boinc"
hyperfqdn=$hyperhost$hyperdom
salt $hyperfqdn cmd.run "'virsh create /srv/vm/instances/$fqdn.xml'"
rm -fR $home/$fqdn*
echo "*** DONE ***"

