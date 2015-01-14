import logging
import subprocess

__author__ = 'jinkerjiang'

logging.basicConfig(format='%(message)s', level=logging.INFO)


def run(cmd_str, cwd=None, show_log=False):
    if show_log:
        logging.info(cmd_str)
    process = subprocess.Popen(cmd_str.split(" "),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=cwd)
    (output, err) = process.communicate()
    if show_log:
        if output:
            logging.info(str(output))
        if err:
            logging.info(str(err))
    return output