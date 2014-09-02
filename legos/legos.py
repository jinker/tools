#coding:utf-8
import httplib
import json
import logging
import optparse
import re
import urllib
from util import authUtil

__author__ = 'jinkerjiang'

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


def postLegos(body, url):
    logging.info("legos save module...")
    headers = {
        'Connection': 'keep-alive',
        'pragma': 'no-cache',
        'Origin': 'http://legos.cm.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'oaname=' + authUtil.getUserName()
    }
    conn = httplib.HTTPConnection("legos.cm.com")
    conn.request("POST", url, urllib.urlencode(body), headers)
    response = conn.getresponse()
    headers = response.getheaders()
    text = response.read()
    conn.close()
    return headers, text


def save(id, pid, name, title, desc, code, filename):
    url = "/legos4.php/package/save"
    body = {
        'id': id,
        'pid': pid,
        'title': title,
        'name': name,
        'filename': filename,
        'desc': desc,
        'code': code
    }
    headers, text = postLegos(body, url)
    res = False
    if (re.compile('http://legos\.cm\.com/legos4\.php/package\?id=\d+&pid=\d+&result=1')).match(headers['Location']):
        res = True
    logging.info("\tresult:" + str(res))
    return res


def createModule(pid, name, title='', desc='', code=''):
    return save('', pid, title, name, '', desc, code)


def saveByModelName(name, code):
    url = "/legos4.php/package/saveByModelName"
    body = {
        'modelName': name,
        'code': code
    }
    headers, text = postLegos(body, url)
    res = False
    try:
        info = json.loads(text)
        res = info['code'] == code
    except:
        pass
    logging.info("\tresult:" + str(res))
    return res


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.info)
    options, args = _GetOptionsParser().parse_args()
    options_type = options.type

    #    save(id='1896', pid='59', title='testName1', name='test.test2', filename='', desc='desc', code='//code1123143')
    saveByModelName('test.test2', '//1123456789')
