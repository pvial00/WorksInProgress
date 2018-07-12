#!/bin/bash
# BH 6/28/2013
#
# uploadBinaries.sh
#
# Description: uploads boinc apk to files.boinc.com and updates release history html page
# Prereq: stage, historyFile and apkName vars all need to be set from originating Jenkins job
#

echo 'Uploading '$apkName' to files.boinc.com...'
scp Player-release.apk root@docs.beyondoblivion.com:/srv/http/docs.beyondoblivion.com/html/apps/builds/$stage/$apkName
echo 'Done! '
echo 'Now replacing boinc-*-latest.apk with this version...'
scp Player-release.apk root@docs.beyondoblivion.com:/srv/http/docs.beyondoblivion.com/html/apps/builds/$stage/boinc-$stage-latest.apk
echo 'Done-Done!'

echo 'updating release history html...'

cd /var/lib/jenkins/jobs
mkdir tempAndroid
cd tempAndroid
git clone git@github.com:BoincMusic/files.boinc.com.git
cd files.boinc.com/apps/

export timest="$(date +%m\\\/%d\\\/%y\\\ %H\\\:%M\\\:%S)"

grep -rl "<\!-- anchor -->" $historyFile | xargs sed -i 's/<\!-- anchor -->/<\!-- anchor -->\n<div id=\"leftcol\"><a href=\"builds\/'$stage'\/'$apkName'\">'$apkName'<\/a><\/div><div id=\"rightcol\">'"$timest"'<\/div><hr width=\"400\">/g'

scp "$historyFile" root@docs.beyondoblivion.com:/srv/http/docs.beyondoblivion.com/html/apps/"$historyFile"
git add -u
git commit -m "updating history file via jenkins ".$BUILD_NUMBER
git push origin master
cd /var/lib/jenkins/jobs
rm -rf tempAndroid
