#coding:utf-8
from util import svn

__author__ = 'jinker'

import re
import sys
import logging
import optparse
import treescan
import datetime
import time
import os

BASE_BUILD_DIR = "/static/build"

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

BASE_REG_STRING_SCRIPT = ['(<script[^>]*src=[\'"])([^>]*%s)[^\'"]*([\'"][^>]*></script>)']
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
    "/static/cftcaipiao/v1.0": "/gtimg",
    "/static/v1.0": "/v1.0"
}

logging.basicConfig(format='%(message)s', level=logging.INFO)

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
    replacePatten = r'\1\2?t=' + versionStr + r'\3'

    fileObj = open(contentFilePath)
    content = fileObj.read()

    for fileRelPath in fileRelPaths:
        for regStr in regStrArr:
            reg = re.compile(regStr % fileRelPath)
            if reg.search(content):
                content = reg.sub(replacePatten, content)
                result = 1

    if result:
        svn.lock(contentFilePath)
        fileObjW = open(contentFilePath, "w")
        fileObjW.write(content)
        fileObjW.close()

    fileObj.close()

    return result


def updateVersionByPathsNew(contentFilePath, regStrArr, fileRelPaths, filePathNewVersion):
    result = 0
    replacePatten = r'\1' + 'http://888.gtimg.com' + filePathNewVersion + r'\3'

    fileObj = open(contentFilePath)
    content = fileObj.read()

    for fileRelPath in fileRelPaths:
        for regStr in regStrArr:
            reg = re.compile(regStr % fileRelPath)
            if reg.search(content):
                content = reg.sub(replacePatten, content)
                result = 1

    if result:
        svn.lock(contentFilePath)
        fileObjW = open(contentFilePath, "w")
        fileObjW.write(content)
        fileObjW.close()

    fileObj.close()

    return result


def getTimeStampAndRelativePath():
    fromtimestamp = datetime.datetime.fromtimestamp(time.time())
    return (fromtimestamp.strftime('%Y%m%d%H%M'), '/' + fromtimestamp.strftime('%Y%m'))


def update(filePath, roots, filePathExpired=None):
    #判断是否使用行的版本管理策略
    reg = re.compile("(.*" + BASE_BUILD_DIR + "/)(\d+)(/.+\.)(\d+)(\.c\.min\.js)$")
    reg_match = reg.match(filePath)
    if reg_match:
        filePathPattern = reg_match.group(1) + '\d+' + reg_match.group(3) + '\d+' + reg_match.group(5)

        fileType = os.path.splitext(filePath)[1]
        fileConfig = FileConfig.getConfig(fileType)

        if not fileConfig or not fileConfig.regStrSet:
            logging.warn("File type not supported yet : " + fileType)
            return

        filePaths = set()
        filePaths.add(filePathPattern)
        filePaths.add(filePathExpired)
        for dir in SOFT_LINKS_REL_DIR_MAP.keys():
            softLinkReg = re.compile("^" + dir)
            if softLinkReg.match(filePath):
                filePaths.add(softLinkReg.sub(SOFT_LINKS_REL_DIR_MAP.get(dir), filePath))
                break
            if softLinkReg.match(filePathExpired):
                filePaths.add(softLinkReg.sub(SOFT_LINKS_REL_DIR_MAP.get(dir), filePathExpired))
                break

        timestamp = getTimeStampAndRelativePath()[0]
        logging.info("The new version : " + timestamp)

        logging.info('Scanning paths...')
        paths = set()
        for path in roots:
            for js_path in treescan.ScanTree(path, fileConfig.fileSearchFilter):
                paths.add(js_path)
        logging.info('%s sources scanned.', len(paths))

        logging.info('Modifying version...')
        updatedFilePaths = set()
        for path in paths:
            if updateVersionByPathsNew(path, fileConfig.regStrSet, filePaths, filePath):
                updatedFilePaths.add(path)

        if updatedFilePaths:
            logging.info("The target html files is/are the follow(%s) :", len(updatedFilePaths))
            index = 0
            for path in updatedFilePaths:
                index += 1
                logging.info("\t" + str(index) + ".\t" + path)
        else:
            logging.info("No file updated.")

        return updatedFilePaths
    else:
        return updateOld(filePath, roots)


def updateOld(filePath, roots):
    paths = set()
    updatedFilePaths = set()

    fileType = os.path.splitext(filePath)[1]
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

    timestamp = getTimeStampAndRelativePath()[0]
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

    return updatedFilePaths


def getRelPath(minJs, root):
    return "/" + os.path.relpath(minJs, root).replace("\\", "/")


def main():
    options, args = _GetOptionsParser().parse_args()
    basePath = options.basePath
    roots = options.roots
    filePath = getRelPath(options.filePath, basePath)

    update(filePath, roots)

    sys.exit(0)

if __name__ == '__main__':
#    main()
    path = '/static/build/201407/cp_jczq_all.201407311647.c.min.js'
    reg = re.compile("(.*" + BASE_BUILD_DIR + "/)(\d+)(/.+\.)(\d+)(\.c\.min\.js)$")
    reg_match = reg.match(path)
    if reg_match:
        print reg_match.group(1) + '\d+' + reg_match.group(3) + '\d+' + reg_match.group(5)