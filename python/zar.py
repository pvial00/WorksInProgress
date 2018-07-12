import sys, time

def create_archive(name):
    archive_fd = open(name, "w")
    return archive_fd

def file_count(archive_name):
    with open(archive_name, "r") as archive:
        archive_data = archive.read()
        count = archive_data.count(chr(3))
    return count

def archive_files(file_list, archive_fd):
    eof_header = chr(7) * 512
    for filename in file_list:
        print "+" + filename
        in_fd = open(filename, "r")
        content = in_fd.read()
        in_fd.close()
        file_header = chr(3)
        archive_fd.write(filename+file_header+content+eof_header)
    archive_fd.close()

def extract_files(archive_name):
    in_fd = open(archive_name, "r")
    file_end = False
    exit_signal = False
    while True:
        file_end = False
        filename = ""
        while True:
            byte = in_fd.read(1)
            if byte == chr(3):
                byte = ""
                break
            elif byte == "":
                exit_signal = True
                break
            filename += byte
        if exit_signal == True:
            break
        print "-" + filename
        out_fd = open(filename, "w")
        content = ""
        eof_count = 0
        file_end = False
        while True:
            content = ""
            eof_buf = ""
            byte = in_fd.read(1)
            if byte == chr(7):
                while True:
                    eof_buf += byte
                    eof_count += 1
                    print eof_count
                    print eof_buf
                    #time.sleep(1)
                    if eof_count == 512:
                        file_end = True
                        break
                    byte = in_fd.read(1)
                    if byte != chr(7):
                        eof_count = 0
                        eof_buf += byte
                        byte = eof_buf
                        break
            if file_end == True:
                break
            content += byte
            out_fd.write(content)
    out_fd.close()

file_list = sys.argv[1:]
file_list.reverse()
mode = file_list.pop()
archive_name = file_list.pop()
file_list.reverse()

if mode == "-c":
    archive_fd = create_archive(archive_name)
    archive_files(file_list, archive_fd)
elif mode == "-x":
    extract_files(archive_name)
elif mode == "-l":
    print "l"

#archive_name = "zarchival"
#archive_fd = create_archive(archive_name)

#archive_files(file_list, archive_fd)

#archive_name += ".zar"
#count = file_count(archive_name)
#print count

#extract_files(archive_name)
