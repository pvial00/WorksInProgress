#!/bin/bash
slowtime="0.500"
while read line; do
        rt=`echo $line | cut -d ' ' -f 15`
        ts=`echo $line | cut -d ' ' -f 4`
        call=`echo $line | cut -d ' ' -f 8`
        if (( $(echo "$rt > $slowtime" | bc -l) )); then
                echo $rt $ts $call
        fi
done < $1
