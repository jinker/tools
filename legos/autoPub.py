import optparse
import re
from pub import *

__author__ = 'jinker'

_BASE_REGEX_STRING = '^\s*define\s*\(\s*[\'"](.+)[\'"]\s*,'
_BASE_REGEX_STRING_TPL = '<script\s*type=[\'"]text\/template[\'"]\s*id=[\'"](.+)[\'"]>'

def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)

    parser.add_option('--basePath',
        dest='basePath',
        action='store',
        help='web base path')

    parser.add_option('--filePath',
        dest='filePath',
        action='store',
        help='js or css file path')

    return parser

if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    options, args = _GetOptionsParser().parse_args()

    filePath = options.filePath

    moduleIds = set()
    moduleIdsTpl = set()
    source = open(filePath, 'r')
    for line in source:
        if re.match(_BASE_REGEX_STRING, line):
            moduleId = re.search(_BASE_REGEX_STRING, line).group(1)
            moduleIds.add(moduleId)
        elif re.match(_BASE_REGEX_STRING_TPL, line):
            moduleId = "tpl_" + re.search(_BASE_REGEX_STRING_TPL, line).group(1)
            moduleIdsTpl.add(moduleId)

    if moduleIds:
        Pub().run(moduleIds)

    if moduleIdsTpl:
        PubTpl().run(moduleIdsTpl)
