import sys, os
length = int(sys.argv[1])
l = 0
c = []
while True:
    if l == length:
        break
    sample = ord(os.urandom(1))
    if sample >= 0 and sample <= 25:
        unit = chr(sample + 65)
        l = l + 1
        c.append(unit)
    else:
        pass
print "".join(c)
