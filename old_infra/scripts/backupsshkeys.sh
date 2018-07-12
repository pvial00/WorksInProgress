#!/bin/bash
dirs=`ls`

for x in $dirs;
do
	tar -cvf $x.sshkey.tar /srv/users/$x/.ssh
done

