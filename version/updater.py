__author__ = 'jinker'

import fileinput
import re
import sys
import logging
import optparse
import treescan
import datetime
import time
import os


class FileConfig(object):
    _SUFFIX_MAP = {}

    @classmethod
    def getConfig(cls, fileSuffix):
        try:
            config = cls._SUFFIX_MAP[fileSuffix]
        except KeyError:
            config = {}
        return config

    def __init__(self, fileSuffix, fileSearchFilter, regStrSet ):
        self.fileSuffix = fileSuffix
        self.fileSearchFilter = fileSearchFilter
        self.regStrSet = regStrSet
        self._SUFFIX_MAP[fileSuffix] = self

BASE_REG_STRING_SCRIPT = ['(<script[^>]*src=[\'"][^>]*%s)[^\'"]*([\'"][^>]*></script>)']
BASE_REG_STRING_CSS = ['(<link[^>]*href=[\'"][^>]*%s)[^\'">]*([\'"][^>]*/?>)']
BASE_REG_STR_IMG = [
    '(background:[^}]*url\([\'"]?[^\)]*%s)[^\)\'"]*([\'"]?\))', # background:url()
    '(background-image:[\s]*[^;]*%s)[^;)]*([^;];)', # background-image:url() || background-image:
    '(<img[^>]*src=[\'"][^>]*%s)[^\'">]*([\'"][^>]*/?>)'  # <img src="" />
]

FILE_CONFIGS = [
    FileConfig(".js", treescan.HTML_FILE_REGEX, BASE_REG_STRING_SCRIPT),
    FileConfig(".css", treescan.HTML_FILE_REGEX, BASE_REG_STRING_CSS),
    FileConfig(".png", treescan.HTML_AND_CSS_FILE_REGEX, BASE_REG_STR_IMG),
    FileConfig(".jpg", treescan.HTML_AND_CSS_FILE_REGEX, BASE_REG_STR_IMG),
    FileConfig(".gif", treescan.HTML_AND_CSS_FILE_REGEX, BASE_REG_STR_IMG),
]

#
SOFT_LINKS_REL_DIR_MAP = {
    "static/cftcaipiao/v1.0": "gtimg",
    "static/v1.0": "/v1.0"
}

def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)

    parser.add_option('--basePath',
        dest='basePath',
        action='store',
        help='web base path')

    parser.add_option('--root',
        dest='roots',
        action='append',
        default=[],
        help='The paths that should be traversed to build the '
             'dependencies.')

    parser.add_option('--filePath',
        dest='filePath',
        action='store',
        help='js or css file path')

    return parser


def updateVersionByPaths(contentFilePath, regStrArr, fileRelPaths, versionStr):
    """Update version

    Args:
      contentFilePath       : str, Path to file.
      regStrArr             : set, reg pattern set
      fileRelPaths          : set
      versionStr            : str

    Returns:
      int, if found, 0 : not found, 1: found

    """
    result = 0
    replacePatten = r'\1?t=' + versionStr + r'\2'

    fileObj = open(contentFilePath)
    content = fileObj.read()

    for fileRelPath in fileRelPaths:
        for regStr in regStrArr:
            reg = re.compile(regStr % fileRelPath)
            if reg.search(content):
                content = reg.sub(replacePatten, content)
                result = 1

    if result:
        fileObjW = open(contentFilePath, "w")
        fileObjW.write(content)
        fileObjW.close()

    fileObj.close()

    return result


def main():
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    options, args = _GetOptionsParser().parse_args()

    paths = set()
    updatedFilePaths = set()

    basePath = options.basePath
    roots = options.roots
    filePath = os.path.relpath(options.filePath, basePath).replace("\\", "/")
    fileType = os.path.splitext(options.filePath)[1]

    fileConfig = FileConfig.getConfig(fileType)

    if not fileConfig or not fileConfig.regStrSet:
        logging.warn("File type not supported yet : " + fileType)
        return

    filePaths = set()
    filePaths.add(filePath)
    for dir in SOFT_LINKS_REL_DIR_MAP.keys():
        softLinkReg = re.compile("^" + dir)
        if softLinkReg.match(filePath):
            filePaths.add(softLinkReg.sub(SOFT_LINKS_REL_DIR_MAP.get(dir), filePath))
            break

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M')
    logging.info("The new version : " + timestamp)

    logging.info('Scanning paths...')
    for path in roots:
        for js_path in treescan.ScanTree(path, fileConfig.fileSearchFilter):
            paths.add(js_path)
    logging.info('%s sources scanned.', len(paths))

    logging.info('Modifying version...')
    for path in paths:
        if updateVersionByPaths(path, fileConfig.regStrSet, filePaths, timestamp):
            updatedFilePaths.add(path)

    if updatedFilePaths:
        logging.info("The target html files is/are the follow(%s) :", len(updatedFilePaths))
        index = 0
        for path in updatedFilePaths:
            index += 1
            logging.info("\t" + str(index) + ".\t" + path)
    else:
        logging.info("No file updated.")

    sys.exit(0)

if __name__ == '__main__':
    main()