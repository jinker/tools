import subprocess

__author__ = 'jinkerjiang'

def lock(path):
    try:
        process = subprocess.Popen(("svn lock " + path).split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
    except Exception:
        pass
    finally:
        pass


def isUnderVersionAndLocked(path):
    pass

lock('E:/workspace/bocai/static/v1.0/i/js/jczq/confirm/cp_jczq_confirm_compound.js')