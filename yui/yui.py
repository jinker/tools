import logging
import os
import re
import subprocess
from util import svn
import distutils.version

__author__ = 'jinkerjiang'

_VERSION_REGEX = re.compile('"([0-9][.0-9]*)')


def _GetJavaVersion():
    """Returns the string for the current version of Java installed."""
    proc = subprocess.Popen(['java', '-version'], stderr=subprocess.PIPE)
    unused_stdoutdata, stderrdata = proc.communicate()
    version_line = stderrdata.splitlines()[0]
    return _VERSION_REGEX.search(version_line).group(1)


def Compile(input, output=None, flags=None):
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

    if not output:
        path_splitext = os.path.splitext(input)
        output = path_splitext[0] + ".min" + path_splitext[1]

    svn.lock(output)

    args = ['java', '-jar', os.path.dirname(__file__) + '/lib/yuicompressor-2.4.7.jar', input, '--charset', 'gb2312', '-o', output]

    if flags:
        args += flags

    logging.info('Compiling with the following command: %s', ' '.join(args))

    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    stdoutdata, unused_stderrdata = proc.communicate()

    logging.info('Compiling result: %s', output)

    if proc.returncode != 0:
        return

    return stdoutdata