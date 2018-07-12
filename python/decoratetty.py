import serial
import os
import time

ttydev = sys.argv[1]

ser = serial.Serial(ttydev)
print(ser.name)
stars = "*!%"
while 1:
	stars = stars + "*#!"
	input = ser.write(stars)
	print input,
	time.sleep(1)

ser.close()
