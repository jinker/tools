#coding:utf-8
import httplib
import urllib

__author__ = 'jinkerjiang'

def addMissionTask():
    module = '315'
    body = {
        'EEnv': '16',
        'IsConst': '0',
        'Executer': ';jinkerjiang',
        'ExtExecuter': '',
        'Modules': module,
        'Desc': '',
        'Files': '315;/data/eos/dev/dist/bocai_home/html/tt_jq.js;;,315;/data/eos/dev/dist/bocai_home/html/tt_sf.js;;',
        'Subject': 'test',
        'BEnv': '15',
        'TapdId': '',
        'Attention': '',
        'PubType': ''
    }
    headers = {
        'Connection': 'keep-alive',
        'pragma': 'no-cache',
        'Origin': 'http://t.ecc.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'PHPSESSID=rmutaa7mokq8sn9unn9kf05ig7; PHPSESSID=rmutaa7mokq8sn9unn9kf05ig7'
    }
    conn = httplib.HTTPConnection("t.ecc.com")
    conn.request("POST", "/eos/api.ajax.php?act=addMissionTask", urllib.urlencode(body), headers)
    response = conn.getresponse()
    responseText = response.read()
    conn.close()
    return responseText

addMissionTask()
