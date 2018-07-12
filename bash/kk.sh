#!/bin/bash
# KryptoMagik - KlassiKrypto api script
# pvial@kryptomagik.com

# Constants
hostname="kryptomagik.com"
ciphers=( "Atbash" "Affine" "Baconian" "BaconBits" "Polybius" "Bifid" "Trifid" "Caesar" "Beale" "Chaocipher" "Vigenere" "Nihilist" "VIC" )
services=( "Random" )
funcs=( "list" )
cipher=$1
algorithm=`echo $cipher | tr '[:upper:]' '[:lower:]'`
mode=$2
text=$3
key=$4
tmpfile="tmp.json"
usage () {
	echo "Usage: kk.sh <algorithm> <encrypt/decrypt> <text> <optional key>"
}
list () {
	echo "Supported Ciphers"
	echo "-----------------"
	for c in "${ciphers[@]}"
	do
		echo $c
	done
}
if [ -z $cipher ]; then
	usage
	exit
fi

# Dependency check
if [ -f /usr/bin/which ]; then
    ccheck=`which curl`
    if [ -z $ccheck ]; then
	echo "Error: Curl program not found"
	exit
    fi
fi
# Is cipher or service
func=0
found=0
service=0
for f in "${funcs[@]}"
do
	if [ "$f" == "$cipher" ]; then
		func=1
	fi
done
if [ $func == 1 ]; then
	list
	exit
fi
for a in "${ciphers[@]}"
do
	if [ "$a" == "$cipher" ]; then
		found=1
	fi
done
if [ $found == 0 ]; then
	for a in "${services[@]}"
	do
		if [ "$a" == "$cipher" ]; then
			service=1
		fi
	done
	if [ $service == 0 ]; then
	    echo "Error: Algorithm not supported"
	    exit
	fi
fi
if [ $service == 1 ]; then
	command=`curl -s https://$hostname/api/$algorithm`
	echo $command
	exit
fi
# If theres no text waiting ask for it
if [ -z "$text" ]; then
	printf "Enter text: "
	read text
	printf "Enter key: "
	read key
fi
# If key is not set don't use it
if [ -z "$key" ]; then
	r="{ \"text\":\"$text\" }"
else
	r="{ \"key\":\"$key\",\"text\":\"$text\"}"
fi
echo $r > $tmpfile
if [ "$mode" == "encrypt" ]; then
	# Encrypt the data
 	command=`curl -s -d @$tmpfile -H "Content-Type: application/json" -X POST https://$hostname/api/$algorithm`
	t="${command%\"}"
	t2="${t#\"}"
	echo $t2
elif [ "$mode" == "decrypt" ]; then
	# Decrypt the data
 	command=`curl -s -d @$tmpfile -H "Content-Type: application/json" -X POST https://$hostname/api/$algorithm/decrypt`
	t="${command%\"}"
	t2="${t#\"}"
	echo $t2
fi
rm $tmpfile
