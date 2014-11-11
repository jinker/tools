__author__ = 'jinkerjiang'

from tempfile import mkstemp
from shutil import move
from os import remove, close


def replace(file_path, replacements):
    # Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path, 'w')
    old_file = open(file_path)
    for line in old_file:
        for src, target in replacements.iteritems():
            line = line.replace(src, target)
        new_file.write(line)
    # close temp file
    new_file.close()
    close(fh)
    old_file.close()
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)