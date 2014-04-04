import subprocess

__author__ = 'jinkerjiang'

def lock(path):
    subprocess.call(("svn lock " + path).split(" "), stdout=subprocess.PIPE)