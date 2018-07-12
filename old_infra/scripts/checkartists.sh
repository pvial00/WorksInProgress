#!/bin/bash

while read line
do
    mysql -pb3y0nd0 -e "select * from artist_artist where name like '$line'" beyond

done <artists2
