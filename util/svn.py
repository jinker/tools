import subprocess

__author__ = 'jinkerjiang'


def lock(path):
    try:
        process = subprocess.Popen(("svn lock --force " + path).split(" "), stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.communicate()
    except Exception:
        pass
    finally:
        pass


def add(paths):
    try:
        process = subprocess.Popen(("svn add --force " + " ".join(paths)).split(" "), stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.communicate()
    except Exception:
        pass
    finally:
        pass


def isUnderVersionAndLocked(path):
    pass

if __name__ == '__main__':
    add([
        '/Users/jinkerjiang/workspace/lottery_proj/bocai/static/build/201411/cp_external_cpqq_recommended.201411141119.c.min.js'
    ])