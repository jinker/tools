import subprocess

__author__ = 'jinkerjiang'

def lock(path):
    try:
        subprocess.call(("svn lock " + path).split(" "), stdout=subprocess.PIPE)
    except Exception:
        pass
    finally:
        pass