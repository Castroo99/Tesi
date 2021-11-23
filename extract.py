from __future__ import print_function
import os
import sys
from clang.cindex import Config
import re

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
find_bug2 = "code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnk0MDM5NTEyNg=="


def method_definitions(cursor):
    for i in cursor.get_children():
        if i.kind != CursorKind.FUNCTION_DECL:
            continue
        if not i.is_definition():
            continue
        yield i


def extract_definition(cursor, origin_filename):
    filename = cursor.location.file.name
    if filename == origin_filename:
        with open(filename, 'r', encoding="latin1") as fh:
            contents = fh.read()
        return contents[cursor.extent.start.offset: cursor.extent.end.offset]
    else:
        return None


# Cerca i bug sul file bugs.txt
def extract_bugs(path):
    with open(path, "r", encoding="latin1") as a_file:
        line_number = 0
        null = []
        dead = []
        uninitialized = []
        for line in a_file:
            line_number += 1
            if "NULL_DEREFERENCE" in line:
                null.append((line_number, line.rstrip()))
            if "DEAD_STORE" in line:
                dead.append((line_number, line.rstrip()))
            if "UNINITIALIZED_VALUE" in line:
                uninitialized.append((line_number, line.rstrip()))
        # print(null)
        # print(dead)
        # print(uninitialized)
        # print(result, result.group(1), p[0])
        return null, dead, uninitialized


os.makedirs("extracted_func", 0o777, True)
i = 0
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        # Trovo i bug nel file bugs.txt
        if file.endswith("bugs.txt"):
            null_deference, dead_store, uninitialized_value = extract_bugs(os.path.join(subdir, file))
            # print(null_deference, dead_store, uninitialized_value)
        # Prendo le funzioni dal file .c
        if file.endswith(".c"):
            print(file)
            with open(os.path.join(subdir, file), "r", encoding="latin1") as a_file:
                idx = Index.create()
                args = '-x c --std=c11'.split()
                tu = idx.parse(os.path.join(subdir, file), args=args)
                # print(tu.spelling)
                # print(os.path.join(subdir))
                defns = method_definitions(tu.cursor)
                prova = open(os.path.join("extracted_func", str(i)), "w", encoding="latin1")
                i += 1
                # funcs = open(os.path.join(subdir, "funcs.txt"), "w")
                # funcs.write("Percorso: " + subdir + "\n\n\n")
                for defn in defns:
                    function = extract_definition(defn, tu.spelling)
                    if function is not None:
                        a = 0
                        # print(function)
                        # funcs.write("Percorso funzione: " + tu.spelling + "\n\n" + function + "\n\n")
                        prova.write("Percorso funzione: " + tu.spelling + "\n\n" + function + "\n\n")
                    # print()
                null_2 = []
                dead_2 = []
                uninitialized_2 = []
                for e in null_deference:
                    if e[1].find("/" + file + ":") != -1:
                        result = re.search(':(.*):', e[1])
                        line = result.group(1).split(":")
                        null_2.append((1, line[0], file))
                for e in dead_store:
                    if e[1].find("/" + file + ":") != -1:
                        result = re.search(':(.*):', e[1])
                        line = result.group(1).split(":")
                        dead_2.append((1, line[0], file))
                for e in uninitialized_value:
                    if e[1].find("/" + file + ":") != -1:
                        result = re.search(':(.*):', e[1])
                        line = result.group(1).split(":")
                        uninitialized_2.append((1, line[0], file))
                # print(null_2)
                # print("#############################")
                # print(dead_2)
                # print("-----------------------------")
                if null_2:
                    for error in null_2:
                        # funcs.write("NULL_DEREFERENCE: " + str(error[0]) + " riga: " + str(error[1]) + "\n")
                        prova.write("NULL_DEREFERENCE: " + str(error[0]) + " riga: " + str(error[1]) + "\n")
                if dead_2:
                    for error in dead_2:
                        # funcs.write("DEAD_STORE: " + str(error[0]) + " riga: " + str(error[1]) + "\n")
                        prova.write("DEAD_STORE: " + str(error[0]) + " riga: " + str(error[1]) + "\n")
                if uninitialized_2:
                    for error in uninitialized_2:
                        # funcs.write("UNINITIALIZED_VALUE: " + str(error[0]) + " riga: " + str(error[1]) + "\n")
                        prova.write("UNINITIALIZED_VALUE: " + str(error[0]) + " riga: " + str(error[1]) + "\n")
                # funcs.write("\n\n#######################################################\n\n"
                #            "NULL_DEFERENCE------DEAD_STORE------UNINITIALIZED_VALUE\n")
                # funcs.write("     " + str(1) + "                  " +
                 #           str(1) + "                  " + str(1) + "\n\n")
                prova.close()
                # funcs.close()
