import logging
import optparse
from legos import legos

__author__ = 'jinkerjiang'


def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)

    parser.add_option('--type',
                      dest='type',
                      action='store',
                      choices=['saveModelByPath', 'pubIdcModelByPath'],
                      help='mission type')

    parser.add_option('--filePath',
                      dest='filePath',
                      action='store',
                      help='file path')

    parser.add_option('--pid',
                      dest='pid',
                      action='store',
                      help='project id')

    return parser


def getModelInfo(filePath):
    isTpl = False
    text = open(filePath).read()

    try:
        text = text.decode('gb2312').encode('utf-8')
    except:
        pass

    name = legos.getModuleName(text)
    if not name:
        name = legos.getModuleNameFromTpl(text)
        isTpl = True

    return name, text, isTpl


def u(s, encoding):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, encoding)


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.info)
    options, args = _GetOptionsParser().parse_args()
    options_type = options.type

    # legos.saveByModelName('test.test11', '//0012', '59')
    # legos.createModule(pid='59', name='test.test8', title='jinkerTest', desc='desc', code='//code')
    name, code, isTpl = getModelInfo(options.filePath)
    if name:
        if options_type == 'saveModelByPath':
            pid = options.pid
            if not isTpl:
                if pid:
                    legos.createModule(pid=pid, name=name, title=name, desc='', code=code)
                else:
                    legos.saveByModelName(name=name, code=code, pid=pid)
            else:
                legos.saveTplByModelName(name=name, code=code, pid=pid)
        elif options_type == 'pubIdcModelByPath':
            legos.pubIdcByModuleName(name=name)
    else:
        logging.info("It's not a amd js")