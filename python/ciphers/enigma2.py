import collections, sys, random

etw_wheel_set = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
rotor1_set = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
rotor2_set = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
rotor3_set = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
reflector_set = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

default_ring_settings = "AAA"

#reflector = {'A':'Y', 'B':'R', 'C':'U', 'D':'H','E':'Q','F':'S','G':'L','H':'D','I':'P','J':'X','K':'N','L':'G','M':'O','N':'K','O':'M','P':'I','Q':'E','R':'B','S':'F','T':'Z','U':'C','V':'W','W':'V','X':'J','Y':'A','Z':'T' }

plugboard = {'A':'A', 'B':'B', 'C':'C', 'D':'D','E':'E','F':'F','G':'G','H':'H','I':'I','J':'J','K':'K','L':'L','M':'M','N':'N','O':'O','P':'P','Q':'Q','R':'R','S':'S','T':'T','U':'U','V':'V','W':'W','X':'X','Y':'Y','Z':'Z' }

def convert_settings(settings):
    setting_list = []
    for letter in settings:
        setting_list.append(letter)
    return setting_list

def ready_settings(etw_wheel_set, rotor1_set, rotor2_set, rotor3_set, reflector_set):
    global etw_wheel_main
    global etw_wheel1
    global etw_wheel2
    global etw_wheel3
    global etw_wheelr
    global rotor1_cfg
    global rotor2_cfg
    global rotor3_cfg
    global reflector_cfg
    etw_wheel_main = convert_settings(etw_wheel_set)
    etw_wheel1 = convert_settings(etw_wheel_set)
    etw_wheel2 = convert_settings(etw_wheel_set)
    etw_wheel3 = convert_settings(etw_wheel_set)
    etw_wheelr = convert_settings(etw_wheel_set)
    rotor1_cfg = convert_settings(rotor1_set)
    rotor2_cfg = convert_settings(rotor2_set)
    rotor3_cfg = convert_settings(rotor3_set)
    reflector_cfg = convert_settings(reflector_set)

def configure_plugboard(config):
    if config != "" or config != "\n":
        for pair in config.split():
            one = pair[0]
            two = pair[1]
            plugboard[one] = two
            plugboard[two] = one

def reflector(letter):
    pos = etw_wheelr.index(letter)
    sub = reflector_cfg.pop(pos)
    reflector_cfg.insert(pos,sub)
    return sub

def rotor_pos1(letter):
    pos = etw_wheel1.index(letter)
    sub = rotor1_cfg.pop(pos)
    rotor1_cfg.insert(pos,sub)
    return sub

def rotor_pos2(letter):
    shift = etw_wheel3.pop(0)
    etw_wheel3.append(shift)
    pos = etw_wheel3.index(letter)
    sub = rotor2_cfg.pop(pos)
    rotor2_cfg.insert(pos,sub)
    return sub

def rotor_pos1_rev(letter):
    pos = rotor1_cfg.index(letter)
    sub = etw_wheelr.pop(pos)
    etw_wheelr.insert(pos,sub)
    return sub

def rotor_pos2_rev(letter):
    pos = rotor2_cfg.index(letter)
    sub = etw_wheel_main.pop(pos)
    etw_wheel_main.insert(pos,sub)
    return sub

def rotor_pos3_rev(letter):
    pos = etw_wheel_main.index(letter)
    sub = etw_wheel3.pop(pos)
    etw_wheel3.insert(pos,sub)
    pos = rotor3_cfg.index(sub)
    sub = etw_wheel_main.pop(pos)
    etw_wheel_main.insert(pos,sub)
    return sub

def rotor_pos3(letter):
    shift = rotor3_cfg.pop(0)
    rotor3_cfg.append(shift)
    pos = etw_wheel_main.index(letter)
    sub = rotor3_cfg.pop(pos)
    rotor3_cfg.insert(pos,sub)
    #shift = rotor3_cfg.pop(0)
    #rotor3_cfg.append(shift)
    return sub

def program_ring_settings(ring_settings):
    r1_pos = etw_wheel_main.index(ring_settings[0])
    for x in range(r1_pos):
        shift = rotor1_cfg.pop(0)
        rotor1_cfg.append(shift)
        #shift = reflector_cfg.pop(0)
        #reflector_cfg.append(shift)
        shift = etw_wheelr.pop(0)
        etw_wheelr.append(shift)
    r2_pos = etw_wheel_main.index(ring_settings[1])
    for x in range(r2_pos):
        shift = rotor2_cfg.pop(0)
        rotor2_cfg.append(shift)
        shift = etw_wheel1.pop(0)
        etw_wheel1.append(shift)
    r3_pos = etw_wheel_main.index(ring_settings[2])
    for x in range(r3_pos):
        shift = rotor3_cfg.pop(0)
        rotor3_cfg.append(shift)
        shift = etw_wheel3.pop(0)
        etw_wheel3.append(shift)
        #shift = etw_wheel1.pop(0)
        #etw_wheel1.append(shift)
        #for x in range(pos):

    
ready_settings(etw_wheel_set, rotor1_set, rotor2_set, rotor3_set, reflector_set)

ring_settings = raw_input("Enter ring settings: ")
if ring_settings == "" or ring_settings == "\n":
    ring_settings = default_ring_settings
program_ring_settings(ring_settings)
print ring_settings

#plugboard_config = raw_input("Enter plugboard configuration: ")
data = raw_input("Enter text to cipher: ")
#configure_plugboard(plugboard_config)
cipher_text = ""

for ctr, letter in enumerate(data):
    ctr += 1
    sub = plugboard[letter]
    sub = rotor_pos3(sub)
    print rotor3_cfg
    #if ctr == 22 == 0 and ctr != 0 or ctr % 26 == 0 and ctr != 26:
    if ctr == 22 and ctr != 0 or ctr % 26 == 0 and ctr != 26:
        #shift = rotor3_cfg.pop(0)
        #rotor3_cfg.append(shift)
        shift = rotor2_cfg.pop(0)
        rotor2_cfg.append(shift)
        shift = rotor2_cfg.pop(0)
        rotor2_cfg.append(shift)
        shift = rotor1_cfg.pop(25)
        rotor1_cfg.insert(0,shift)
        #shift = rotor1_cfg.pop(0)
        #rotor1_cfg.append(shift)
        #shift = etw_wheel1.pop(0)
        #etw_wheel1.append(shift)
        #shift = etw_wheel2.pop(0)
        #etw_wheel2.append(shift)
        shift = etw_wheel3.pop(0)
        etw_wheel3.append(shift)
        print "counter: ", ctr
    print "3: ", sub
    sub = rotor_pos2(sub)
    print rotor2_cfg
    print "2: ", sub
    sub = rotor_pos1(sub)
    print "1: ", sub
    print rotor1_cfg
    #sub = reflector[sub]
    sub = reflector(sub)
    print "R: ", sub
    sub = rotor_pos1_rev(sub)
    print "1: ", sub
    sub = rotor_pos2_rev(sub)
    print "2: ", sub
    sub = rotor_pos3_rev(sub)
    print "3: ", sub
    sub = plugboard[sub]
    print "final sub: ", sub
    cipher_text += sub
    print ctr

print cipher_text
