import subprocess

__author__ = 'jinkerjiang'

def lock(path):
    try:
        process = subprocess.Popen(("svn lock --force " + path).split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
    except Exception:
        pass
    finally:
        pass


def isUnderVersionAndLocked(path):
    pass