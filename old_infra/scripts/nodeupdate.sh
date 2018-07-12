#!/bin/bash
/usr/local/bin/salt 'node*' cmd.run 'virsh list' > /root/nodelist.txt
mailx --to infra@boinc.com --subject="Virts Running Report `date +'%m-%d-%Y'`" < /root/nodelist.txt
