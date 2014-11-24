# coding:utf-8
import httplib
import logging
import optparse
import urllib
from util import inputUtil, authUtil

__author__ = 'jinkerjiang'

MODULE_BOCAI_HOME = '315'
MODULE_vb2c_lottery = '166'

MODULE_PATH_PREFIX_MAP = {
    MODULE_BOCAI_HOME: '/data/eos/dev/dist/bocai_home',
    MODULE_vb2c_lottery: '/data/eos/dev/dist/vb2c_lottery'
}

logging.basicConfig(format='%(message)s', level=logging.INFO)


def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)

    parser.add_option('--type',
                      dest='type',
                      action='store',
                      choices=['pathFromCmd', 'pathFromInput', 'pathFromCmdPhp', 'pathFromInputPhp', 'fullPath'],
                      default='pathFromInput',
                      help='mission type')

    parser.add_option('--fileRelativePath',
                      dest='fileRelativePaths',
                      action='append',
                      help='file relative path')

    parser.add_option('--subject',
                      dest='subject',
                      action='store',
                      help='subject')

    return parser


def addMissionTask(module, fileRelativePaths, subject, executors, middlePath=None, begin=1, end=2):
    if module:
        pathPrefix = MODULE_PATH_PREFIX_MAP[module]
    else:
        pathPrefix = ''
    fullPaths = []

    if not middlePath:
        middlePath = ''
    for relPath in fileRelativePaths:
        fullPaths.append(pathPrefix + middlePath + relPath)

    return doEosByApi(executors, fullPaths, module, subject, begin, end)


def doEos(executors, fullPaths, module, subject, begin, end):
    Files = []

    for path in fullPaths:
        Files.append(module + ';' + path + ';;')

    logging.info("EOS add mission task...")
    body = {
        'EEnv': '16',
        'IsConst': '0',
        'Executer': ';'.join(executors),
        'ExtExecuter': '',
        'Modules': module,
        'Desc': '',
        'Files': ','.join(Files),
        'Subject': subject,
        'BEnv': '15',
        'TapdId': '',
        'Attention': '',
        'PubType': ''
    }
    headers = {
        'Connection': 'keep-alive',
        'pragma': 'no-cache',
        'Origin': 'http://t.ecc.com',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    conn = httplib.HTTPConnection("t.ecc.com")
    conn.request("POST", "/eos/api.ajax.php?act=addMissionTask", urllib.urlencode(body), headers)
    response = conn.getresponse()
    responseText = response.read()
    conn.close()
    res = 'ok' == responseText
    logging.info("\tresult:" + str(res))
    return res


def doEosByApi(executors, fullPaths, module, subject, begin=1, end=2):
    logging.info("EOS add mission task...")

    body = {
        'exeuser': ';'.join(executors),
        'files': ','.join(fullPaths),
        'subject': subject,
        'benv': begin,
        'eenv': end,
        'isexec': 'true'
    }
    headers = {
        'Cookie': 'PHPSESSID=1gd1sri6c3rq880uj9oc0j8u31;'
    }
    conn = httplib.HTTPConnection("vtools.oa.com", 80)
    conn.request("POST", "/dsrm.php/eos/addMission?" + urllib.urlencode(body), "", headers)
    response = conn.getresponse()
    responseText = response.read()
    conn.close()
    res = '发布任务创建成功，请登录Eos执行。' == responseText
    try:
        responseText = responseText.decode('utf-8').encode('gb2312')
    except Exception:
        pass
    logging.info(responseText)
    logging.info("\tresult:" + str(res))
    return res


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.info)
    options, args = _GetOptionsParser().parse_args()
    options_type = options.type

    filePaths = []
    subject = ''
    module = MODULE_BOCAI_HOME
    middlePath = ''

    if options_type == 'pathFromCmd':
        filePaths = options.fileRelativePaths
        subject = options.subject
        middlePath = '/html'
    elif options_type == 'pathFromInput':
        logging.info("Please input file relative path(multiple split by semicolon): \n")
        fileRelPathsRaw = inputUtil.raw_input_multi_line()

        filePaths = []
        for fileRelPath in fileRelPathsRaw:
            filePaths.append(fileRelPath.replace("\\", "/"))

        subject = raw_input("Please input subject: \n").replace("\\", "/")
        middlePath = '/html'
    elif options_type == 'pathFromCmdPhp':
        filePaths = options.fileRelativePaths
        subject = options.subject
        middlePath = '/web_app'
    elif options_type == 'pathFromInputPhp':
        logging.info("Please input file relative path(multiple split by semicolon): \n")
        fileRelPathsRaw = inputUtil.raw_input_multi_line()

        filePaths = []
        for fileRelPath in fileRelPathsRaw:
            filePaths.append(fileRelPath.replace("\\", "/"))

        subject = raw_input("Please input subject: \n").replace("\\", "/")
        middlePath = '/web_app'
    else:
        logging.info("Please input file relative path(multiple split by semicolon): \n")
        filePathsRaw = inputUtil.raw_input_multi_line()
        subject = raw_input("Please input subject: \n").replace("\\", "/")
        module = raw_input("Please input module: \n")

        for fileRelPath in filePathsRaw:
            filePaths.append(fileRelPath.replace("\\", "/"))

    addMissionTask(module=module, fileRelativePaths=filePaths, subject=subject, executors=[authUtil.getUserName()],
                   middlePath=middlePath)
