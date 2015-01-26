# coding:utf-8
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

    def __init__(self, fileSuffix, fileSearchFilter, regStrSet):
        self.fileSuffix = fileSuffix
        self.fileSearchFilter = fileSearchFilter
        self.regStrSet = regStrSet
        self._SUFFIX_MAP[fileSuffix] = self


BASE_REG_STRING_SCRIPT = ['(<script[^>]*src=[\'"])([^>]*%s)[^\'"]*([\'"][^>]*></script>)']
BASE_REG_STRING_CSS = ['(<link[^>]*href=[\'"])([^>]*%s)[^\'">]*([\'"][^>]*/?>)']
BASE_REG_STR_IMG = [
    '(background:[^}]*url\([\'"]?[^\)]*%s)[^\)\'"]*([\'"]?\))',  # background:url()
    '(background-image:[\s]*[^;]*%s)[^;)]*([^;];)',  # background-image:url() || background-image:
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
        svn.try_lock(contentFilePath)
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
        svn.try_lock(contentFilePath)
        fileObjW = open(contentFilePath, "w")
        fileObjW.write(content)
        fileObjW.close()

    fileObj.close()

    return result


def get_time_stamp_and_relative_path():
    from_time_stamp = datetime.datetime.fromtimestamp(time.time())
    return (from_time_stamp.strftime('%Y%m%d%H%M'), '/' + from_time_stamp.strftime('%Y%m'))


def update(file_path, roots, file_path_expired=None):
    # 判断是否使用行的版本管理策略
    reg = re.compile("(.*" + BASE_BUILD_DIR + "/)(\d+)(/.+\.)(\d+)(\.?\w?\.min\.\w+)$")
    reg_match = reg.match(file_path)
    if reg_match:
        file_path_pattern = reg_match.group(1) + '\d+' + reg_match.group(3) + '\d+' + reg_match.group(5)

        file_type = os.path.splitext(file_path)[1]
        file_config = FileConfig.getConfig(file_type)

        if not file_config or not file_config.regStrSet:
            logging.warn("File type not supported yet : " + file_type)
            return

        filePaths = set()
        filePaths.add(file_path_pattern)
        filePaths.add(file_path_expired)
        for dir in SOFT_LINKS_REL_DIR_MAP.keys():
            softLinkReg = re.compile("^" + dir)
            if softLinkReg.match(file_path):
                filePaths.add(softLinkReg.sub(SOFT_LINKS_REL_DIR_MAP.get(dir), file_path))
                break
            if softLinkReg.match(file_path_expired):
                filePaths.add(softLinkReg.sub(SOFT_LINKS_REL_DIR_MAP.get(dir), file_path_expired))
                break

        logging.info("The version : " + reg_match.group(4))

        logging.info('Scanning paths...')
        paths = set()
        for path in roots:
            for js_path in treescan.ScanTree(path, file_config.fileSearchFilter):
                paths.add(js_path)
        logging.info('%s sources scanned.', len(paths))

        logging.info('Modifying version...')
        updatedFilePaths = set()
        for path in paths:
            if updateVersionByPathsNew(path, file_config.regStrSet, filePaths, file_path):
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
        return update_old(file_path, roots)


def update_old(filePath, roots):
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

    timestamp = get_time_stamp_and_relative_path()[0]
    logging.info("The version : " + timestamp)

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


def get_rel_path(min_js, root):
    return "/" + os.path.relpath(min_js, root).replace("\\", "/")


def get_build_version(entry_point_file, update_build_version):
    if update_build_version:
        timestamp, build_path = get_time_stamp_and_relative_path()
        save_version_to_file(entry_point_file, timestamp)
    else:
        timestamp = get_version_from_file(entry_point_file)
        if not timestamp:
            timestamp, build_path = get_time_stamp_and_relative_path()
            save_version_to_file(entry_point_file, timestamp)
        else:
            build_path = '/' + timestamp[:6]

    return timestamp, build_path


def save_version_to_file(entry_point_file, version):
    svn.try_lock(entry_point_file)

    file_io = open(entry_point_file, 'r')
    content = file_io.read()
    file_io.close()

    re_compile = re.compile('([\s\S]*)//buildVersion=(.+)')
    compile_match = re_compile.match(content)

    version_str = '//buildVersion=' + version

    if compile_match:
        content = re_compile.sub(r'\1' + version_str, content)
    else:
        content = version_str + '\n' + content

    file_io = open(entry_point_file, 'w')
    file_io.write(content)
    file_io.close()


def get_version_from_file(entry_point_file):
    file_io = open(entry_point_file, 'r')
    content = file_io.read()
    re_compile = re.compile('//buildVersion=(.+)')
    compile_match = re_compile.match(content)
    if compile_match:
        return compile_match.group(1)
    return None


def main():
    options, args = _GetOptionsParser().parse_args()
    basePath = options.basePath
    roots = options.roots
    filePath = get_rel_path(options.filePath, basePath)

    update(filePath, roots)

    sys.exit(0)


if __name__ == '__main__':
    # main()
    path = '/static/build/201407/cp_jczq_all.201407311647.c.min.js'
    reg = re.compile("(.*" + BASE_BUILD_DIR + "/)(\d+)(/.+\.)(\d+)(\.c\.min\.js)$")
    reg_match = reg.match(path)
    if reg_match:
        print reg_match.group(1) + '\d+' + reg_match.group(3) + '\d+' + reg_match.group(5)