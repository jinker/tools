# coding:utf-8
import httplib
import json
import logging
import re
import urllib
from util import authUtil

__author__ = 'jinkerjiang'

logging.basicConfig(format='%(message)s', level=logging.INFO)


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
    return headers, text, response


def save(id, pid, name, title, desc, code, filename):
    try:
        code = code.decode('gb2312').encode('utf-8')
    except:
        pass
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
    headers, text, response = postLegos(body, url)
    headerLocation = response.getheader('Location')
    res = False
    if headerLocation and (re.compile('http://legos\.cm\.com/legos4\.php/package\?id=\d+&pid=\d+&result=1')).match(
            headerLocation):
        res = True
    logging.info("\tresult:" + str(res))
    return res


def createModule(pid, name, title='', desc='', code=''):
    return save(id='', pid=pid, name=name, title=title, desc=desc, code=code, filename='')


def saveByModelName(name, code, pid=None, compressionType=None):
    try:
        code = code.decode('gb2312').encode('utf-8')
    except:
        pass
    logging.info('model name : ' + name)
    url = "/legos4.php/package/saveByModelName"
    body = {
        'modelName': name,
        'code': code
    }
    if pid:
        body['pid'] = pid

    if not compressionType:
        compressionType = 'option1'

    body['compressiontype'] = compressionType

    headers, text, response = postLegos(body, url)
    res = False
    try:
        info = json.loads(text)
        if pid:
            res = info['pid'] == pid
        else:
            res = (info['code']).encode('utf-8') == code
    except:
        pass
    logging.info('response : ' + text)
    logging.info("\tresult:" + str(res))
    return res


def getModuleName(fileContent):
    try:
        fileContent = fileContent.decode('gb2312').encode('utf-8')
    except:
        pass
    reg = re.compile('define\([\'"]([\w\d\._-]+)[\'"]')
    content_splitlines = fileContent.splitlines()
    for line in content_splitlines:
        match = reg.match(line)
        if match:
            break
    if match:
        return match.group(1)
    return None


def pubIdcByModuleName(name):
    logging.info('model name : ' + name)
    url = "/legos4.php/package/pubIdcByModelName"
    body = {
        'modelName': name
    }

    headers, text, response = postLegos(body, url)
    res = False
    try:
        info = json.loads(text)
        res = info['name'] == name
    except:
        pass
    logging.info("\tresult:" + str(res))
    return res
