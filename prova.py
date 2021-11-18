from __future__ import print_function
import codecs
import os
import sys
from clang.cindex import Config

# 2. set the lib name with full path
conf = Config()
Config.set_library_file('C:/Program Files/LLVM/bin/libclang.dll')
from clang.cindex import *


class SourceFile(object):
    def __init__(self, path):
        with codecs.open(path, 'r', 'utf-8') as file:
            self.file_content = file.read()

        index = Index.create()
        root_node = index.parse(path)

        # for included in root_node.get_includes():
            # print(included.include)

        self.print_declerations(root_node.cursor)

    def print_declerations(self, root, recurse=True):
        print(root.kind.name, root.spelling)
        if root.kind.is_declaration():
            node_def = root.get_definition()
            if node_def is not None:
                start_offset = node_def.extent.start.offset
                end_offset = node_def.extent.end.offset + 1
                print(self.file_content[start_offset:end_offset], '\n')

        if recurse:
            for child in root.get_children():
                self.print_declerations(child, False)


if __name__ == '__main__':
    path = 'C:/Users/User/PycharmProjects/TesiLucaCastricini/code_and_static_analyzer/data/MDEwOlJlcG9zaXRvcnkxMDc3MTAyNDc=/source/sohail-argsv-cpython-545a697/argsv.c'
    print('Translation unit:', path)
    source = SourceFile(path)
