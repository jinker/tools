#coding:utf-8
import jsbeautifier
import optparse
import os
import re
from closure2amd import source

__author__ = 'jinker'

_BASE_REGEX_STRING = re.compile('^\s*goog\.addDependency\(\s*[\'"](.+)[\'"]\s*,\s*\[[\'"]([^,]+)[\'"]\]')
_REGEX_GOOG = re.compile('/closure/')

def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)

    parser.add_option('--filePath',
        dest='filePath',
        action='store',
        help='js or css file path')

    return parser

#_moduleConfig={
#    alias:{
#        "module1":"http://www.demo.com/js/modules.js",
#        "module2":"http://www.demo.com/js/modules.js",
#        "module3":"http://www.demo2.com/js/xxx.js"
#    }
#};

def toEntryPoint(pathJs):
    firstLine = True
    newContents = ""
    contents = source.GetFileContents(pathJs)
    source_lines = contents.splitlines()

    for line in source_lines:
        if _REGEX_GOOG.search(line):
            continue

        match = _BASE_REGEX_STRING.match(line)
        if match:
            if not firstLine:
                newContents += ",\n"
            else:
                newContents += '\n_moduleConfig={alias:{'
            newContents += '"' + match.group(2) + '":"' + getAmdFilePath(match.group(1)) + '"'
            firstLine = False
        else:
            newContents += "\n" + line

    newContents += '\n}};'


    #输出
    out = open(getEntryPointFilePath(pathJs), 'w')
    beautifier_options = jsbeautifier.BeautifierOptions()
    beautifier_options.indent_with_tabs = True
    out.write(jsbeautifier.beautify(newContents, beautifier_options))


def getEntryPointFilePath(path):
#    return 'E:/workspace/bocai_100/build/entrypoint/' + os.path.splitext(os.path.basename(path))[0] + '.entrypoint.js'
    return os.path.dirname(path) + "/" + os.path.splitext(os.path.basename(path))[0] + ".entrypoint.js"


def getAmdFilePath(path):
    pathRes = os.path.dirname(path) + "/" + os.path.splitext(os.path.basename(path))[0] + ".amd.js"
    pathRes = pathRes.replace("/static", "")
    return pathRes

if __name__ == "__main__":
#    options, args = _GetOptionsParser().parse_args()
#    filePath = options.filePath
#    toEntryPoint(filePath)
    #
    #    toEntryPoint(filePath)
    #    match = _BASE_REGEX_STRING.match("goog.addDependency('../../../../static/v1.0/i/js/jc/view/tpl/jc.goog.js', ['goog.cp.tpl.jc.view'], ['soy', 'soydata']);")
    #    print match.group(1), "----", match.group(2)

    toEntryPoint('J:/workspace/tools/closure2amd/test/cp.jczq.all.deps.js')