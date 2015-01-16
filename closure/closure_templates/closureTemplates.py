import logging
import os
import re
import subprocess
import distutils.version
import sys

from util import svn
from util import fileUtil


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


def compileTemplate(inputs, outputPathFormat):
    outputPaths = []
    for input in inputs:
        output_path = getOutputPath(input, outputPathFormat)
        outputPaths.append(output_path)
        svn.try_lock(output_path)
    args = [
        'java',
        '-jar', os.path.dirname(__file__) + '/SoyToJsSrcCompiler.jar',
        '--srcs', ','.join(inputs),
        '--outputPathFormat', outputPathFormat,
        '--shouldProvideRequireSoyNamespaces'
    ]
    logging.info('Compiling with the following command: %s', ' '.join(args))
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    stdoutdata, unused_stderrdata = proc.communicate()

    return outputPaths


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

    outputPathFormats = []
    if not outputPathFormat:
        outputPathFormats.append('{INPUT_DIRECTORY}/{INPUT_FILE_NAME_NO_EXT}.js')
        outputPathFormats.append('{INPUT_DIRECTORY}/{INPUT_FILE_NAME_NO_EXT}.goog.js')
    else:
        outputPathFormats.append(outputPathFormat)

    outputPaths = []
    for outputPathFormat in outputPathFormats:
        paths = compileTemplate(inputs, outputPathFormat)
        if '.goog.' in outputPathFormat:
            for path in paths:
                fileUtil.replace(path, {
                    'cp.tpl': 'goog.cp.tpl',
                    "goog.require('soy');": '',
                    "goog.require('soydata');": ''
                })

        outputPaths = outputPaths + paths

    for outputPath in outputPaths:
        logging.info('Compiling result: %s', outputPath)


def getOutputPath(path, outputFormat):
    prefix = os.path.splitext(path)[1]
    dir = os.path.dirname(path)
    fileName = os.path.basename(path)
    fileNameNoExt = os.path.splitext(fileName)[0]
    # {INPUT_PREFIX}, {INPUT_DIRECTORY}, {INPUT_FILE_NAME}, {INPUT_FILE_NAME_NO_EXT}
    outputFormat = outputFormat.replace('{INPUT_PREFIX}', prefix)
    outputFormat = outputFormat.replace('{INPUT_DIRECTORY}', dir)
    outputFormat = outputFormat.replace('{INPUT_FILE_NAME}', fileName)
    outputFormat = outputFormat.replace('{INPUT_FILE_NAME_NO_EXT}', fileNameNoExt)
    return outputFormat

