from dh import DHE

dh = DHE()
g, p, secret = dh.gen()
a = dh._step1(g, p, secret)
b = dh._step2(dh.decode(a), p, secret)
print len(b)
print b

