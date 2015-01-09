import logging
import os
import subprocess

__author__ = 'jinkerjiang'

logging.basicConfig(format='%(message)s', level=logging.INFO)


def lock(path, force=True):
    try:
        cmd = "svn lock"
        if force:
            cmd += ' --force'
        cmd += ' ' + path
        process = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        (output, err) = process.communicate()
        logging.info('svn lock: \n' + str(output) + '\n' + str(err))
        return True
    except Exception:
        return False


def add(paths):
    try:
        process = subprocess.Popen(("svn add --force " + " ".join(paths)).split(" "), stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        (output, err) = process.communicate()
        logging.info('svn add: \n' + str(output) + '\n' + str(err))
    except Exception:
        pass
    finally:
        pass


def commit(paths, msg='modify'):
    add(paths)

    try:
        process = subprocess.Popen(("svn changelist my-changelist " + " ".join(paths)).split(" "),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        (output, err) = process.communicate()
        logging.info('svn changelist: \n' + str(output) + '\n' + str(err))
    except Exception:
        pass
    finally:
        pass

    process = subprocess.Popen("svn commit -m \"" + msg + "\" --changelist my-changelist",
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)
    (output, err) = process.communicate()
    logging.info('svn commit: \n' + str(output) + '\n' + str(err))
    # try:
    # process = subprocess.Popen("svn commit -m '" + msg + "' --changelist my-changelist".split(" "),
    # stdout=subprocess.PIPE,
    # stderr=subprocess.PIPE)
    # process.communicate()
    # except Exception:
    # pass
    # finally:
    # pass


def isUnderVersionAndLocked(path):
    pass


if __name__ == '__main__':
    commit([
        '/Users/jinkerjiang/workspace/lottery_proj/bocai/static/build/201501/test1.txt'
    ])