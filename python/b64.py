import sys, base64

mode = sys.argv[1]
infile = sys.argv[2]
outfile = sys.argv[3]
fd = open(infile, "r")
data = fd.read()
fd.close()

fd = open(outfile, "w")
if mode == "encode":
    fd.write(base64.b64encode(data))
elif mode == "decode":
    fd.write(base64.b64decode(data))
fd.close()
