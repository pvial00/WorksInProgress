#!/bin/bash
# BH 7/16/2013
# 
# description: revs manifest versionName and versionCode for given android workspace
#
# params: $WORKSPACE directory from jenkins
#
cd $1
versionName=`cat ./Android/Player/AndroidManifest.xml | grep 'versionName=' | awk -F: 'match($0,"versionName="){ print substr($2,RSTART-0)}' | tr -d "'" | sed -e 's/versionName=/\n/g' | sed -e 's/^"//' -e 's/"$//'`
buildNumber=`cat ./Android/Player/AndroidManifest.xml | grep 'versionName=' | awk -F: 'match($0,"versionName="){ print substr($2,RSTART-0)}' | tr -d "'" | sed -e 's/versionName=/\n/g' | sed -e 's/^"//' -e 's/"$//' | cut -d'.' -f 4`
preBuildNumber=`cat ./Android/Player/AndroidManifest.xml | grep 'versionName=' | awk -F: 'match($0,"versionName="){ print substr($2,RSTART-0)}' | tr -d "'" | sed -e 's/versionName=/\n/g' | sed -e 's/^"//' -e 's/"$//' | cut -c 1-5`
versionCode=`cat ./Android/Player/AndroidManifest.xml | grep 'versionCode=' | awk -F: 'match($0,"versionCode="){ print substr($2,RSTART-0)}' | tr -d "'" | sed -e 's/versionCode=/\n/g' | sed -e 's/^"//' -e 's/"$//'`
buildCount=`cat /var/lib/jenkins/scripts/buildcount.txt`
newCount=`expr $buildCount + 1`
newVersionName="$preBuildNumber".`expr $buildNumber + $newCount`
newVersionCode=`expr $versionCode + $newCount`
sed -i 's/'"$buildCount"'/'"$newCount"'/' /var/lib/jenkins/scripts/buildcount.txt
sed -i 's/'"$versionName"'/'"$newVersionName"'/' ./Android/Player/AndroidManifest.xml
sed -i 's/'"$versionCode"'/'"$newVersionCode"'/' ./Android/Player/AndroidManifest.xml
echo "version changed to "$newVersionName ", code="$newVersionCode
