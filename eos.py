#coding:utf-8
import httplib
import json
import logging
import optparse
import os
import re
import urllib
from util import inputUtil

__author__ = 'jinkerjiang'

MODULE_BOCAI_HOME = '315'

MODULE_PATH_PREFIX_MAP = {
    MODULE_BOCAI_HOME: '/data/eos/dev/dist/bocai_home'
}

logging.basicConfig(format='%(message)s', level=logging.INFO)


def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)

    parser.add_option('--type',
        dest='type',
        action='store',
        choices=['pathFromCmd', 'pathFromInput', 'pathFromInputPhp'],
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


def addMissionTask(module, fileRelativePaths, subject, executors, middlePath=None):
    logging.info("EOS add mission task...")
    pathPrefix = MODULE_PATH_PREFIX_MAP[module]
    fullPaths = []

    if not middlePath:
        middlePath = ''
    for relPath in fileRelativePaths:
        fullPaths.append(module + ';' + pathPrefix + middlePath + relPath + ';;')
    body = {
        'EEnv': '16',
        'IsConst': '0',
        'Executer': ';'.join(executors),
        'ExtExecuter': '',
        'Modules': module,
        'Desc': '',
        'Files': ','.join(fullPaths),
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

#addMissionTask(module=MODULE_BOCAI_HOME, fileRelativePaths=['/tt_jq.js', '/tt_sf.js'], subject='test', executors=['jinkerjiang'], middlePath='/html1')

if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.info)
    options, args = _GetOptionsParser().parse_args()
    options_type = options.type

    fileRelativePaths = []
    subject = ''
    if options_type == 'pathFromCmd':
        fileRelativePaths = options.fileRelativePaths
        subject = options.subject
        middlePath = '/html'
    elif options_type == 'pathFromInput':
        logging.info("Please input file relative path(multiple split by semicolon): \n")
        fileRelPathsRaw = inputUtil.raw_input_multi_line()

        fileRelativePaths = []
        for fileRelPath in fileRelPathsRaw:
            fileRelativePaths.append(fileRelPath.replace("\\", "/"))


        #fileRelativePaths = raw_input("Please input file relative path(multiple split by semicolon): \n").replace("\\", "/").split(";")

        subject = raw_input("Please input subject: \n").replace("\\", "/")
        middlePath = '/html'
    elif options_type == 'pathFromInputPhp':
        logging.info("Please input file relative path(multiple split by semicolon): \n")
        fileRelPathsRaw = inputUtil.raw_input_multi_line()

        fileRelativePaths = []
        for fileRelPath in fileRelPathsRaw:
            fileRelativePaths.append(fileRelPath.replace("\\", "/"))


        #fileRelativePaths = raw_input("Please input file relative path(multiple split by semicolon): \n").replace("\\", "/").split(";")

        subject = raw_input("Please input subject: \n").replace("\\", "/")
        middlePath = '/web_app'

    dir = re.sub('\\\\', '/', os.path.normpath(os.path.abspath(__file__)))
    dir = re.sub(r'/[^/]*$', '', dir)
    settings = json.loads(open(dir + '/setting.json').read())
    addMissionTask(module=MODULE_BOCAI_HOME, fileRelativePaths=fileRelativePaths, subject=subject, executors=[settings['userName']], middlePath=middlePath)
