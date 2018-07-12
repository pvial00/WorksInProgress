import libnacl.secret, libnacl.utils, libnacl.public, libnacl.sealed, sys

mode = sys.argv[1]
if mode != "gen":
    filename = sys.argv[2]

def gen_key():
    keypair = libnacl.public.SecretKey()
    keypair.save('rsa_keys')
    print "Keys generated"

def encrypt_file(filename, rsa_keys):
    infile = open(filename, "r")
    data = infile.read()
    infile.close()
    outfilename = filename + ".en"
    outfile = open(outfilename, "w")
    rsa_safe = libnacl.sealed.SealedBox(rsa_keys)
    key = libnacl.utils.salsa_key()
    nonce = libnacl.utils.rand_nonce()
    hidden_key = rsa_safe.encrypt(key)
    cipher_text = libnacl.crypto_secretbox(data, nonce, key)
    crypto_pkg = nonce + hidden_key + cipher_text
    outfile.write(crypto_pkg)
    outfile.close()

def decrypt_file(filename, rsa_keys):
    infile = open(filename, "r")
    data = infile.read()
    nonce = data[0:24]
    hidden_key = data[24:104]
    cipher_text = data[104:]
    infile.close()
    outfilename = filename.rstrip('.en')
    outfile = open(outfilename, "w")
    rsa_safe = libnacl.sealed.SealedBox(rsa_keys)
    key = rsa_safe.decrypt(hidden_key)
    plain_text = libnacl.crypto_secretbox_open(cipher_text, nonce, key)
    outfile.write(plain_text)
    outfile.close()

if mode == "encrypt":
    rsa_keys = libnacl.utils.load_key('rsa_keys')
    encrypt_file(filename, rsa_keys)
elif mode == "decrypt":
    rsa_keys = libnacl.utils.load_key('rsa_keys')
    decrypt_file(filename, rsa_keys)
elif mode == "gen":
    gen_key()
