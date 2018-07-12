import sys

def create_archive(name):
    archive_fd = open(name, "w")
    return archive_fd

def file_count(archive_name):
    with open(archive_name, "r") as archive:
        archive_data = archive.read()
        count = archive_data.count(chr(3))
    return count

def archive_files(file_list, archive_fd):
    tag = chr(4)
    for filename in file_list:
        in_fd = open(filename, "r")
        content = in_fd.read()
        in_fd.close()
        archive_fd.write(filename+chr(3)+content+tag)
    archive_fd.close()

def extract_files(archive_name):
    in_fd = open(archive_name, "r")
    exit_signal = False
    #with (open(archive_name, "r") as in_fd):
    while True:
        filename = ""
        while True:
            byte = in_fd.read(1)
            if byte == chr(3):
                break
            elif byte == "":
                exit_signal = True
                break
            filename += byte
        if exit_signal == True:
            break
        print filename
        out_fd = open(filename, "w")
        content = ""
        while True:
            byte = in_fd.read(1)
            if byte == chr(4):
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
