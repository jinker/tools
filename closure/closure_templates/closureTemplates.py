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


def process(inputs, outputPathFormat=None):
    """Prepares command-line call to Closure Compiler.

    Args:
      input: Source paths to build, in order.
    """

    # User friendly version check.
    if not (distutils.version.LooseVersion(_GetJavaVersion()) >=
            distutils.version.LooseVersion('1.6')):
        logging.error('Requires Java 1.6 or higher. '
                      'Please visit http://www.java.com/getjava')
        return

    if not outputPathFormat:
        outputPathFormat = '{INPUT_DIRECTORY}/{INPUT_FILE_NAME_NO_EXT}.js'

    outputPaths = []
    for input in inputs:
        output_path = getOutputPath(input, outputPathFormat)
        outputPaths.append(output_path)
        svn.lock(output_path)

    args = [
        'java',
        '-jar', os.path.dirname(__file__) + '/SoyToJsSrcCompiler.jar',
        '--srcs', ','.join(inputs),
        '--outputPathFormat', outputPathFormat,
        '--shouldProvideRequireSoyNamespaces'
    ]

    logging.info('Compiling with the following command: %s', ' '.join(args))

    proc = subprocess.Popen(args, stdout=subprocess.PIPE)

    logging.info('Compiling result: %s', '\n'.join(outputPaths))


def getOutputPath(path, outputFormat):
    prefix = os.path.splitext(path)[1]
    dir = os.path.dirname(path)
    fileName = os.path.basename(path)
    fileNameNoExt = os.path.splitext(fileName)[0]
    #{INPUT_PREFIX}, {INPUT_DIRECTORY}, {INPUT_FILE_NAME}, {INPUT_FILE_NAME_NO_EXT}
    outputPath = path.replace('{INPUT_PREFIX}', prefix)
    outputPath = outputPath.replace('{INPUT_DIRECTORY}', dir)
    outputPath = outputPath.replace('{INPUT_FILE_NAME}', fileName)
    outputPath = outputPath.replace('{INPUT_FILE_NAME_NO_EXT}', fileNameNoExt)
    return outputPath

