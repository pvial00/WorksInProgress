ps -e | grep FL | awk '{ print $1 }' | xargs kill -9

