#!/bin/bash -x
#
# deploy.sh 
#
# deploy the version that can be found in /srv/build/<project>/<project>-<stage>-<branch>-<classifier>-<buildnum>.tar.gz
# apiserver-qa-develop-7-default.tar.gz
if [ $# -lt 5 ] ; then
   echo "usage: deploy.sh <project> <stage> <branch> <classifier> <buildnum>"
   exit 0
fi
echo "DEPLOY --------------------------->"
BUILD_DIR=/srv/builds
BASE_DEPLOY_DIR=/opt/beyond
DEPLOY_DIR=$BASE_DEPLOY_DIR/deploy
PROJECT=$1
STAGE=$2
BRANCH=$3
CLASSIFIER=$4
BUILDNUM=$5

## this is a pain in the balls but apiserver has historically been deployed as "code" dont' want to rock the boat too much
case "$PROJECT" in
	'apiserver')
		CODE="code"
		;;
	*)
		CODE=$PROJECT
		;;
esac

## where we are ultimately linking to
CODE_DIR=$BASE_DEPLOY_DIR/$CODE
echo "CODE_DIR: $CODE_DIR"

## the thing that has the code we want to deploy
ARCHIVE=$BUILD_DIR/$PROJECT/$PROJECT-$STAGE-$BRANCH-$BUILDNUM-$CLASSIFIER.tar.gz

## where we unzip to
UNTARLOC=$DEPLOY_DIR/$PROJECT/$PROJECT-$STAGE-$BRANCH-$BUILDNUM-$CLASSIFIER

if [ ! -f $ARCHIVE ] ; then
  echo "$ARCHIVE does not exist"
  exit 1
fi

if [ ! -d $DEPLOY_DIR/$PROJECT ] ; then
  echo "Deployment directory $DEPLOY_DIR/$PROJECT does not exist"
  exit 1
fi

echo "unarchiving $ARCHIVE to $UNTARLOC"
mkdir $UNTARLOC
tar zxf $ARCHIVE -C $UNTARLOC
if [ $? -ne 0 ]; then
   echo "error unarchiving"
   exit 1
fi
echo "linking new code"
if [ -h $CODE_DIR ] ; then
   ## get the old one and delete it
   OLDDEPL=`ls -l $CODE_DIR | awk '{print $11}'|sed -e "s|/$CODE|/|"`
   echo "also deleting $OLDDEPL"
   rm -rf $OLDDEPL || exit $? 
   rm $CODE_DIR || exit $?
fi

ln -s $UNTARLOC/code $CODE_DIR || exit $?
sudo /bin/chown -R www-data:www-data $CODE_DIR
echo "<------------------------ DEPLOY DONE"
exit 0

