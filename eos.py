# coding:utf-8
import httplib
import logging
import optparse
import urllib

from util import inputUtil, authUtil, svn


__author__ = 'jinkerjiang'

MODULE_BOCAI_HOME = '315'
MODULE_vb2c_lottery = '166'

MODULE_PATH_PREFIX_MAP = {
    # /data/eos/dev/dist
    MODULE_BOCAI_HOME: '/bocai_home',
    MODULE_vb2c_lottery: '/vb2c_lottery'
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

    parser.add_option('--filePathAbs',
                      dest='filePathsAbs',
                      action='append',
                      help='file abs path')

    parser.add_option('--subject',
                      dest='subject',
                      action='store',
                      help='subject')

    parser.add_option('--begin',
                      dest='begin',
                      action='store',
                      default=1,
                      help='env begin')

    parser.add_option('--end',
                      dest='end',
                      action='store',
                      default=2,
                      help='env end')

    return parser


def add_eos_mission(module, file_relative_paths, subject, executors, middle_path=None, begin=1, end=2, filePathsAbs=[],
                    project_path=None):
    if filePathsAbs and len(filePathsAbs) > 0:
        svn.try_commit(filePathsAbs, cwd=project_path)

    if module:
        path_prefix = MODULE_PATH_PREFIX_MAP[module]
    else:
        path_prefix = ''
    full_paths = []

    if not middle_path:
        middle_path = ''
    for relPath in file_relative_paths:
        full_paths.append(path_prefix + middle_path + relPath)

    return do_eos_by_api(executors, full_paths, module, subject, begin, end)


def do_eos(executors, full_paths, module, subject, begin, end):
    files = []

    for path in full_paths:
        files.append(module + ';' + path + ';;')

    logging.info("EOS add mission task...")
    body = {
        'EEnv': '16',
        'IsConst': '0',
        'Executer': ';'.join(executors),
        'ExtExecuter': '',
        'Modules': module,
        'Desc': '',
        'Files': ','.join(files),
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
    response_text = response.read()
    conn.close()
    res = 'ok' == response_text
    logging.info("\tresult:" + str(res))
    return res


def do_eos_by_api(executors, full_paths, module, subject, begin=1, end=2):
    logging.info("EOS add mission task...")

    body = {
        'exeuser': ';'.join(executors),
        'files': ','.join(full_paths),
        'subject': subject,
        'benv': begin,
        'eenv': end,
        'isexec': 'true'
    }
    headers = {
        'Cookie': 'PHPSESSID=i6le63ru6umm55crtph0tba4i7;'
    }
    conn = httplib.HTTPConnection("vtools.oa.com", 80)
    conn.request("POST", "/dsrm.php/eos/addMission?" + urllib.urlencode(body), "", headers)
    response = conn.getresponse()
    response_text = response.read()
    conn.close()
    res = '发布任务创建成功，请登录Eos执行。' == response_text
    try:
        response_text = response_text.decode('utf-8').encode('gb2312')
    except Exception:
        pass
    logging.info(response_text)
    logging.info("\tresult:" + str(res))
    return res


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.info)
    options, args = _GetOptionsParser().parse_args()
    options_type = options.type
    begin = options.begin
    end = options.end

    filePaths = []
    subject = ''
    module = MODULE_BOCAI_HOME
    middlePath = ''

    filePathsAbs = options.filePathsAbs

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

    add_eos_mission(module=module, file_relative_paths=filePaths, subject=subject, executors=[authUtil.get_user_name()],
                    middle_path=middlePath, begin=begin, end=end, filePathsAbs=filePathsAbs)
