import logging
import os
import re
import subprocess
import sys
from util import svn
from util import command
import distutils.version

__author__ = 'jinkerjiang'

_VERSION_REGEX = re.compile('"([0-9][.0-9]*)')

logging.basicConfig(format=(sys.argv[0] + ': %(message)s'),
                    level=logging.INFO)


def _GetJavaVersion():
    """Returns the string for the current version of Java installed."""
    proc = subprocess.Popen(['java', '-version'], stderr=subprocess.PIPE)
    unused_stdoutdata, stderrdata = proc.communicate()
    version_line = stderrdata.splitlines()[0]
    return _VERSION_REGEX.search(version_line).group(1)


def compile(input, output=None, flags=None):
    """Prepares command-line call to Closure Compiler.

    Args:
      source_paths: Source paths to build, in order.

    Returns:
      The compiled source, as a string, or None if compilation failed.
    """

    # User friendly version check.
    if not (distutils.version.LooseVersion(_GetJavaVersion()) >=
                distutils.version.LooseVersion('1.6')):
        logging.error('Requires Java 1.6 or higher. '
                      'Please visit http://www.java.com/getjava')
        return

    svn.try_lock(output)

    args = ['java', '-jar', os.path.dirname(__file__) + '/lib/yuicompressor-2.4.7.jar', input, '--line-break', '1000',
            '--charset', 'gb2312']

    if output:
        args += ['-o', output]

    if flags:
        args += flags

    command.run(' '.join(args), show_log=True)

    return output
