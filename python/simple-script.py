import time

for i in range(100):
        print "For Message", i

time.sleep(2)

while i != 200:
        x = 0
        print "While message ", i
        while x <= 50:
                print i, x
                x = x +1
        i = i + 1

if i == 200:
        print "Finished"
elif i != 200:
        print "Not finished"

call("date")
