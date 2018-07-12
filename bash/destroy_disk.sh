#!/bin/bash
# ./destroy_disk.sh /dev/sda

device=$1
dd if=/dev/zero of=$device bs=1024k &
