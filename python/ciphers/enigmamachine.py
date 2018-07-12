class Rotor:
    def __init__(self, alphabet, notch):
        self.alphabet = list(alphabet)
        self.notch = notch
        self.position = 0
        self.counter = 0
        self.notchcounter = 0

class Wiring:
    def __init__(self, rotor1, rotor2, rotor3):
        self.rotor1 = Rotor(rotor1[0], rotor1[1])
        self.rotor2 = Rotor(rotor2[0], rotor2[1])
        self.rotor3 = Rotor(rotor3[0], rotor3[1])

    def rotor1_input(self, char):
        self.step(1)
        p = ((ord(char) - 65) + self.rotor1.position) % 26
        r = (p - self.rotor2.position) % 26
        #print chr(p + 65)
        sub = chr((((ord(self.rotor1.alphabet[r]) - 65) - self.rotor1.position) % 26) + 65)
        sub = self.rotor1.alphabet[r]
        sub = chr((((ord(sub) - 65) - self.rotor1.position) % 26) + 65)
        #print self.rotor1.alphabet
        return sub

    def rotor1_output(self, char):
        b = chr((((ord(char) - 65) + self.rotor1.position) % 26) + 65)
        sub = chr((self.rotor1.alphabet.index(b)+ 65))
        return sub

    def rotor2_input(self, char):
        self.step(2)
        p = ((ord(char) - 65) - self.rotor3.position) % 26
        #print p
        #print chr(p + 65)
        s = (p + self.rotor2.position) % 26
        sub = self.rotor2.alphabet[s]
        #print self.rotor2.alphabet
        return sub

    def rotor2_output(self, char):
        r = chr((((ord(char) - 65) + self.rotor2.position) % 26) + 65)
        p = chr((((ord(r) - 65) - self.rotor1.position) % 26) + 65)
        #print p
        sub = chr((self.rotor2.alphabet.index(p) + 65))
        #sub = chr(((self.rotor2.alphabet.index(p) + (self.rotor2.position)) % 26) + 65)
        return sub
    
    def rotor3_input(self, char):
        self.step(3)
        pos = ((ord(char) - 65) + self.rotor3.position) % 26
        p = (pos - self.rotor2.position) % 26
        sub = self.rotor3.alphabet[pos]
        #print self.rotor3.alphabet
        return sub

    def rotor3_output(self, char):
        #print chr(self.rotor3.position + 65)
        sub = chr((((ord(char) - 65) + self.rotor3.position) % 26) + 65)
        sub = chr((((ord(sub) - 65) - self.rotor2.position) % 26) + 65)
        #print sub
        sub = chr(self.rotor3.alphabet.index(sub) + 65)
        sub = chr((((ord(sub) - 65) - self.rotor3.position) % 26) + 65)
        #print sub
        #print self.rotor3.alphabet
        return sub

    def step(self, num):
        if num == 3:
            self.rotor3.position = (self.rotor3.position + 1) % 26
            self.rotor3.counter += 1
        if num == 2:
            for notch in self.rotor3.notch:
                if self.rotor3.position + 65 == (ord(notch) + 1):
                    self.rotor2.position = (self.rotor2.position + 1) % 26
            for notch in self.rotor2.notch:
                if self.rotor2.position + 65 == (ord(self.rotor2.notch)) and self.rotor2.notchcounter == 1:
                    self.rotor1.position = (self.rotor1.position + 1) % 26
                    self.rotor2.position = (self.rotor2.position + 1) % 26
                    self.rotor2.notchcounter += 1
                if self.rotor2.position + 65 == (ord(self.rotor2.notch)) and (self.rotor2.notchcounter == 2 or self.rotor2.notchcounter > 26):
                    self.rotor2.notchcounter = 0
                if self.rotor2.position + 65 == (ord(self.rotor2.notch)) and (self.rotor2.notchcounter == 0 or self.rotor2.notchcounter > 26):
                    self.rotor2.notchcounter = 1

    def program_wiring(self, setting):
        for x in range((ord(setting[0]) - 65)):
            self.rotor1.position = (self.rotor1.position + 1) % 26
        for x in range((ord(setting[1]) - 65)):
            self.rotor2.position = (self.rotor2.position + 1) % 26
        for x in range((ord(setting[2]) - 65)):
            self.rotor3.position = (self.rotor3.position + 1) % 26

    def program(self, setting):
        for x in range((ord(setting[0]) - 65)):
            #self.rotor1.alphabet.append(self.rotor1.alphabet.pop(0))
            self.rotor1.position = (self.rotor1.position + 1) % 26
        for x in range((ord(setting[1]) - 65)):
            self.rotor2.position = (self.rotor2.position + 1) % 26
            #self.rotor2.alphabet.append(self.rotor2.alphabet.pop(0))
        for x in range((ord(setting[2]) - 65)):
            self.rotor3.position = (self.rotor3.position + 1) % 26
            #self.rotor3.alphabet.append(self.rotor3.alphabet.pop(0))

class Plugboard:
    wiring = {'A':'A', 'B':'B', 'C':'C', 'D':'D','E':'E','F':'F','G':'G','H':'H','I':'I','J':'J','K':'K','L':'L','M':'M','N':'N','O':'O','P':'P','Q':'Q','R':'R','S':'S','T':'T','U':'U','V':'V','W':'W','X':'X','Y':'Y','Z':'Z' }
    def __init__(self, config):
        if config != "" or config != "\n":
            for pair in config.split():
                one = pair[0]
                two = pair[1]
                self.wiring[one] = two
                self.wiring[two] = one

    def input(self, char):
        return self.wiring[char]

class Reflector:
    def __init__(self, config):
        self.alphabet = list(config)

    def input(self, char):
        return self.alphabet[(ord(char) - 65)]

class Enigma:
    def __init__(self, rotor1, rotor2, rotor3, reflector, plugboard=""):
        self.rotor1 = rotor1
        self.rotor2 = rotor2
        self.rotor3 = rotor3
        self.reflector = reflector
        self.plugboard = plugboard

    def input(self, data, ringsetting="AAA", setting="AAA"):
        buf = []
        wiring = Wiring(self.rotor1, self.rotor2, self.rotor3)
        reflector = Reflector(self.reflector)
        plugboard = Plugboard(self.plugboard)
        wiring.program_wiring(ringsetting.upper())
        #wiring.program(setting)
        msg = "".join(data.split())
        for letter in msg.upper():
            #print "Input ", letter
            sub = plugboard.input(letter)
            #print "plug ", sub
            sub = wiring.rotor3_input(sub)
            #print "s3", sub
            sub = wiring.rotor2_input(sub)
            #print "s2", sub
            sub = wiring.rotor1_input(sub)
            #print "s1", sub
            sub = reflector.input(sub)
            #print "ref ", sub
            sub = wiring.rotor1_output(sub)
            ##print "s1r ", sub
            sub = wiring.rotor2_output(sub)
            #print "s2r ", sub
            sub = wiring.rotor3_output(sub)
            #print "s3r ", sub
            sub = plugboard.input(sub)
            #print "plugr", sub
            buf.append(sub)
        return "".join(buf)
