import logging
import os
from time import time

from util import command


__author__ = 'jinkerjiang'

logging.basicConfig(format='%(message)s', level=logging.INFO)


def lock(path, force=True, show_log=True):
    if os.path.exists(path):
        cmd_str = "svn lock"
        if force:
            cmd_str += ' --force'
        cmd_str += ' ' + path
        command.run(cmd_str, show_log=show_log)
    return True


def add(paths, show_log=False):
    command.run("svn add --force " + " ".join(paths), show_log=show_log)


def commit(paths, msg, show_log=False, cwd=None):
    changelist = "my-changelist-" + str(time())
    command.run("svn changelist " + changelist + " " + " ".join(paths), show_log=show_log)
    cmd_str = "svn commit"
    if msg:
        cmd_str += " -m \"" + msg + "\""
    cmd_str += " --changelist " + changelist
    if not cwd:
        cwd = os.path.dirname(list(paths)[0])
    command.run(cmd_str, cwd=cwd, show_log=show_log)


def status(path, show_log=False):
    status_str = (command.run("svn status -v " + path, show_log=show_log))[:8]
    return status_str


def is_modified(path, show_log=False):
    status_str = status(path, show_log=show_log)
    if status_str[0] == 'M':
        return True
    return False


def is_added(path, show_log=False):
    status_str = status(path, show_log=show_log)[0]
    if status_str and status_str != '?':
        return True
    return False


def is_locked(path, show_log=False):
    status_str = status(path, show_log=show_log)
    if status_str[2] == 'K':
        return True
    return False


def need_commit(path, show_log=False):
    status_str = status(path, show_log=show_log)
    if status_str[0] == ' ':
        return False
    return True


def try_commit(paths, msg='modify', cwd=None):
    add_paths = []
    for path in paths:
        if not is_added(path, show_log=True):
            add_paths.append(path)

    if add_paths:
        add(add_paths, show_log=True)

    commit_paths = []
    for path in paths:
        if need_commit(path):
            commit_paths.append(path)
    if commit_paths:
        commit(commit_paths, msg, show_log=True, cwd=cwd)


if __name__ == '__main__':
    p = '/Users/jinkerjiang/workspace/lottery_proj/bocai/static/v1.0/i/lib/util.js'
    # status(path)

    is_modified(p)