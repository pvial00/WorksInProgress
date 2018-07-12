#!/bin/bash
#BH 3/4/2013
#description:  this script pulls out the apk version, as defined in the androidmanifest, to name the latest apk filename before uploading to files.boinc.com
# 
cd /var/lib/jenkins/jobs/boinc_Android/workspace/Android/Player/bin
versionVal=`aapt d badging Player-release.apk | grep 'versionName=' | awk -F: 'match($0,"versionName="){ print substr($2,RSTART-8)}' | tr -d "'" | sed -e 's/versionName=/\n/g'`

apkName=`echo 'boinc-'$versionVal'.apk' | tr -d ' '`
echo 'Uploading '$apkName' to files.boinc.com...'
scp Player-release.apk root@docs.beyondoblivion.com:/srv/http/docs.beyondoblivion.com/html/$apkName
echo 'Done! '
echo 'Now replacing boinc-latest.apk with this version...'
scp Player-release.apk root@docs.beyondoblivion.com:/srv/http/docs.beyondoblivion.com/html/boinc-latest.apk
echo 'Done-Done!'
exit
