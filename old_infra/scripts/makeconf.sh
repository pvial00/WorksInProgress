#!/bin/bash
max=255
for((i=0;i<=max;i++))
do
	num=`printf "%.2X" $((0x$hex+i))`
	mkdir .unison/$num
	printf "root=/srv/media/media/albums/$num/\nroot=/srv/nfs2/media/albums/$num/\nauto=true\nbatch=true\nowner=true\ngroup=true\nprefer=newer\nnodeletion=/srv/media/media/albums/$num/\nnodeletion=/srv/nfs2/media/albums/$num/\nsilent=true\ntimes=true\n" > .unison/$num/media$num.prf
done
