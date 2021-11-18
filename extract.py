from __future__ import print_function
import os
import sys
from clang.cindex import Config

# 2. set the lib name with full path
conf = Config()
Config.set_library_file('C:/Program Files/LLVM/bin/libclang.dll')
from clang.cindex import *

sys.path.extend(['.', '..'])

# Root directory
rootdir = 'code_and_static_analyzer/data'
# Cartella di prova script
folder = "code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnk0MDA0OTU4"
# Cartella che causava un crash
folder_crash = "code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnkxNTUyNjAxMg==/source/prife-ptp-gadget-cf1f803"
# Cartella dove sono presenti bug
find_bug = "code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnkxMDc3MTAyNDc="


def method_definitions(cursor):
    for i in cursor.get_children():
        if i.kind != CursorKind.FUNCTION_DECL:
            continue
        if not i.is_definition():
            continue
        yield i


def extract_definition(cursor):
    filename = cursor.location.file.name
    with open(filename, 'r') as fh:
        contents = fh.read()
        # print(contents)
    return contents[cursor.extent.start.offset: cursor.extent.end.offset]


# Cerca i bug sul file bugs.txt
def extract_bugs(path):
    with open(path, "r", encoding="latin1") as a_file:
        file = a_file.read()
        null_deference = file.find("NULL_DEREFERENCE")
        dead_store = file.find("DEAD_STORE")
        uninitialized_value = file.find("UNINITIALIZED_VALUE")
        if null_deference != -1:
            null_deference = 1
        else:
            null_deference = 0
        if dead_store != -1:
            dead_store = 1
        else:
            dead_store = 0
        if uninitialized_value != -1:
            uninitialized_value = 1
        else:
            uninitialized_value = 0
        return null_deference, dead_store, uninitialized_value


for subdir, dirs, files in os.walk(folder):
    for file in files:
        # Trovo i bug nel file bugs.txt
        if file.endswith("bugs.txt"):
            null_deference, dead_store, uninitialized_value = extract_bugs(os.path.join(subdir, file))
            print(null_deference, dead_store, uninitialized_value)
        # Prendo le funzioni dal file .c
        if file.endswith(".c"):
            with open(os.path.join(subdir, file), "r", encoding="latin1") as a_file:
                for line in a_file:
                    stripped_line = line.strip()
                idx = Index.create()
                args = '-x c --std=c11'.split()
                tu = idx.parse(os.path.join(subdir, file), args=args)
                # print(tu.spelling)
                # print(os.path.join(subdir))
                defns = method_definitions(tu.cursor)
                funcs = open(os.path.join(subdir, "funcs.txt"), "w")
                funcs.write("Percorso:" + tu.spelling + "\n\n\n")
                for defn in defns:
                    print(extract_definition(defn))
                    funcs.write(extract_definition(defn))
                    # print()
                funcs.write("\n\n#######################################################\n\n"
                            "NULL_DEFERENCE------DEAD_STORE------UNINITIALIZED_VALUE\n"
                            "     " + str(null_deference) + "                  " +
                            str(dead_store) + "                  " + str(uninitialized_value))
                funcs.close()
