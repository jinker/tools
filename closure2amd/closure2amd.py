# coding:utf-8
import jsbeautifier
import optparse
import os
from closure.bin.build import source
import treescan

__author__ = 'jinker'


def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)

    parser.add_option('--filePath',
                      dest='filePath',
                      action='store',
                      help='js or css file path')

    return parser


def getAmdCodeBySource(s):
    textRes = ''
    modelName = None
    if s.provides:
        modelName = s.provides.copy().pop()
        textOri = s.GetSource()
        name_map = s.getNameMap()
        names = s.getNames()
        names = sorted(names, reverse=True)
        source_lines = textOri.splitlines()
        #转换
        for line in source_lines:
            matchProvide = source._PROVIDE_REGEX.match(line)
            matchRequire = source._REQUIRES_REGEX.match(line)
            matchSoy = source._REQUIRES_REGEX_SOY_OR_SOYDATA.match(line)
            if matchSoy:
                continue
            elif matchProvide:
                provide = matchProvide.group(1)
                textRes += u'\n//本文件由closure模块转换而来，请不要直接编辑，如果决定取消对应的closure模块，方可编辑'.encode("gb2312")
                textRes += '\ndefine("' + provide + '", function (require, exports) {'
                textRes += '\nvar _cacheThisModule_;\n'
                textRes += '\nvar ' + s.getCamelName(provide) + ' = {};'
            elif matchRequire:
                require = matchRequire.group(1)
                if require != 'cp.$':
                    camel_name = s.getCamelName(require)
                    textRes += '\nvar ' + camel_name + ' = require("' + require + '");'
                else:
                    textRes += '\nvar $ = require("{jquery}");'
                    textRes += '\nvar jQuery = $;'
                    textRes += '\nvar cp_$ = $;'
            else:
                if not source.isComment(line):
                    for name in names:
                        line = line.replace(name, name_map[name])
                line = source._REGEX_SOY_OR_SOYDATA.sub('(', line)
                textRes += "\n" + line

        textRes += "\nreturn " + name_map[modelName] + ';'
        textRes += "\n});"

        beautifier_options = jsbeautifier.BeautifierOptions()
        beautifier_options.indent_with_tabs = True
        textRes = jsbeautifier.beautify(textRes, beautifier_options)
    return textRes, modelName


def getAmdCode(pathJs):
    s = source.Source(source.GetFileContents(pathJs))
    return getAmdCodeBySource(s)


def toAmd(pathJs):
    textRes, modelName = getAmdCode(pathJs)

    if textRes:
        #输出
        out = open(getAmdFilePath(pathJs), 'w')
        out.write(textRes)
        return True
    else:
        return False


def getAmdFilePath(path):
    return os.path.dirname(path) + "/" + os.path.splitext(os.path.basename(path))[0] + ".amd.js"


def main():
    #    for pathJs in treescan.ScanTreeForJsFiles("E:/workspace/tools/closure2amd/test"):
    #        toAmd(pathJs)

    options, args = _GetOptionsParser().parse_args()
    filePath = options.filePath

    print "processing..."

    count = 0
    if os.path.isdir(filePath):
        for pathJs in treescan.ScanTreeForJsFiles(filePath):
            if toAmd(pathJs):
                count += 1
    else:
        toAmd(filePath)
        count += 1

    print "closure modules transfer to amd module : " + str(count)