class X2:
    def __init__(self, key):
        k = ""
        for byte in key:
            k += str(ord(byte))
        self.key = int(k)

    def encrypt(self, data):
        buf = ""
        for byte in data:
            buf += "1" + str('%03d' % ord(byte))
        c = str(int(buf) * self.key)
        return c

    def decrypt(self, data):
        c = str(int(data) / self.key)
        s = 0
        e = 4
        p = ""
        for x in range(len(c) / 4):
            p += chr(int(c[(s + 1):e]))
            s += 4
            e += 4
        return p
