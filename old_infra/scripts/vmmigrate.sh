#!/bin/bash
while getopts o:d:v: option
do
        case "${option}"
        in
                o) original=${OPTARG};;
                d) destination=${OPTARG};;
                v) vmname=${OPTARG};;
		?) echo "Usage: -o original -d destination -v vm-name" && exit
        esac
done

saltdom=".pnap.ny.boinc"
scpdom=".stor.pnap.ny.boinc"

##check if vm running on original
ovmexists=$(salt $original$saltdom cmd.run 'virsh list' |grep $vmname|awk '{print $2}')
if [[ "$ovmexists" == "" ]];
   then
    echo "ERROR: $vmname is not running on host $original"
    exit 0
   else
    echo "$vmname is running on $original"
fi

##check if vm running on destination
dvmexists=$(salt $destination$saltdom cmd.run 'virsh list' |grep $vmname|awk '{print $2}')
if [[ "$dvmexists" != "" ]];
   then
    echo "ERROR: $vmname already running on host $destination"
   exit 0
   else
    echo "$vmname is not running on $destination"
#copy vm original -> dest
   origdirexists=$(salt $original$saltdom file.directory_exists "/srv/vm/tmp/$vmname"|grep False|awk '{ print $1}')
if [[ "$origdirexists" == "False" ]]; then
   echo "Copying from $original:/mnt/local/vm/$vmname to /srv/vm/tmp/"
   salt $original$saltdom cmd.run "cp -r /mnt/local/vm/$vmname /srv/vm/tmp/"
fi
   destdirexists=$(salt $destination$saltdom file.directory_exists "/mnt/local/vm/$vmname"|grep False|awk '{ print $1}')
if [[ "$destdirexists" == "False" ]]; then
   echo "Copying from /srv/vm/tmp/$vmname to $destination:/mnt/local/vm/"
   salt $destination$saltdom cmd.run "cp -r /srv/vm/tmp/$vmname /mnt/local/vm/"
fi
   echo "Copied from $original local storage to $destination local storage"
fi
#validate scp on dest side
dvmexists=$(salt $destination$saltdom cmd.run 'ls -al /mnt/local/vm/' |grep $vmname|awk '{print $9}')
if [[ "$dvmexists" == "" ]];
   then
    echo "Error: $vmname has not been copied to host $destination"
   exit 0
   else
    echo "$vmname now exists on $destination's Local Storage"
#live migrate
  echo "Bringing $vmname online"
   sshexists=$(salt $destination$saltdom file.directory_exists "/root/.ssh"|grep False|awk '{ print $1}')
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
ovmexists=$(salt $original$saltdom cmd.run 'virsh list' |grep $vmname|awk '{print $2}')
if [[ "$ovmexists" == "" ]];
   then
    echo "$vmname is not running on host $original"
   else
    echo "Still Running on $original"
fi

#validate access to running destination
dvmexists=$(salt $destination$saltdom cmd.run 'virsh list' |grep $vmname|awk '{print $2}')
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
