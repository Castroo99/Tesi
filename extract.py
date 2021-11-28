from __future__ import print_function
import os
import sys
from clang.cindex import Config
import re
import csv

# 2. set the lib name with full path
conf = Config()
Config.set_library_file('C:/Program Files/LLVM/bin/libclang.dll')
from clang.cindex import *

sys.path.extend(['.', '..'])

# Root directory
rootdir = 'code_and_static_analyzer/data/'
# Cartella di prova script
folder = "code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnk0MDA0OTU4"
# Cartella che causava un crash
folder_crash = "code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnkxNTUyNjAxMg==/source/prife-ptp-gadget-cf1f803"
# Cartella dove sono presenti bug
find_bug = "code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnkxMDc3MTAyNDc="
find_bug2 = "code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnk0MDM5NTEyNg=="
error = "code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnk1NDI4MDc3OA=="


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
        lines = [cursor.extent.start.line, cursor.extent.end.line]
        return lines, cursor.spelling, contents[cursor.extent.start.offset: cursor.extent.end.offset]
    else:
        return None, None, None


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
        return null, dead, uninitialized


os.makedirs("extracted_func", 0o777, True)
bugs = open("bugs.csv", "w", newline="", encoding="utf-8")
header = ["Percorso", "NULL_DEREFERENCE", "DEAD_STORE", "UNINITIALIZED_VALUE"]
writer = csv.writer(bugs)
writer.writerow(header)

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        # Trovo i bug nel file bugs.txt
        if file.endswith("bugs.txt"):
            null_deference, dead_store, uninitialized_value = extract_bugs(os.path.join(subdir, file))
        # Prendo le funzioni dal file .c
        if file.endswith(".c"):
            with open(os.path.join(subdir, file), "r", encoding="latin1") as a_file:
                idx = Index.create()
                args = '-x c --std=c11'.split()
                tu = idx.parse(os.path.join(subdir, file), args=args)

                defns = method_definitions(tu.cursor)

                null_2 = []
                dead_2 = []
                uninitialized_2 = []
                for e in null_deference:
                    if e[1].find(file + ":") != -1:
                        result = re.search(':(.*):', e[1])
                        line = result.group(1).split(":")
                        null_2.append((1, line[0], file))
                for e in dead_store:
                    if e[1].find(file + ":") != -1:
                        result = re.search(':(.*):', e[1])
                        line = result.group(1).split(":")
                        dead_2.append((1, line[0], file))
                for e in uninitialized_value:
                    if e[1].find(file + ":") != -1:
                        result = re.search(':(.*):', e[1])
                        line = result.group(1).split(":")
                        uninitialized_2.append((1, line[0], file))

                for defn in defns:
                    function_lines, function_name, function_descr = extract_definition(defn, tu.spelling)
                    if function_name is not None:
                        function_path = str(tu.spelling).split("/")
                        final_path = function_path[2].replace("\\", "-")
                        function_dataset = open(
                            os.path.join("extracted_func", final_path + "-" + function_name + ".txt"),
                            "w", encoding="latin1")
                        function_dataset.write(function_descr)
                        function_dataset.close()
                        # Dava errore: src_pl_plpgsql_src_pl_comp.c-plpgsql_build_variable
                        row = [tu.spelling + "-" + function_name]
                        if null_2:
                            cnt = 0
                            for error in null_2:
                                cnt += 1
                                if function_lines[0] < int(error[1]) < function_lines[1]:
                                    row.append(1)
                                    break
                                if cnt == len(null_2):
                                    row.append(0)
                        else:
                            row.append(0)
                        if dead_2:
                            cnt = 0
                            for error in dead_2:
                                cnt += 1
                                if function_lines[0] < int(error[1]) < function_lines[1]:
                                    row.append(1)
                                    break
                                if cnt == len(dead_2):
                                    row.append(0)
                        else:
                            row.append(0)
                        if uninitialized_2:
                            cnt = 0
                            for error in uninitialized_2:
                                cnt += 1
                                if function_lines[0] < int(error[1]) < function_lines[1]:
                                    row.append(1)
                                    break
                                if cnt == len(uninitialized_2):
                                    row.append(0)
                        else:
                            row.append(0)
                        # print(row)
                        writer.writerow(row)
bugs.close()
