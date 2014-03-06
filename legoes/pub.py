#coding:utf-8
__author__ = 'jinker'

import json
import logging
import optparse
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC

from pip._vendor import requests

logging.basicConfig(format='%(message)s', level=logging.INFO)

def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)

    parser.add_option('--orderId',
        dest='orderIds',
        action='store',
        help='web base path')

    return parser


class Pub():
    def __init__(self):
        self.exceptionCount = 0
        self.MAX_EXCEPTION = 6

        #        server_url = "http://%s:%s/wd/hub" % ('127.0.0.1', '4444')
        #        self.driver = webdriver.Remote(server_url, DesiredCapabilities.HTMLUNIT)

        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, userName, passWord):
        driver = self.driver
        driver.get("http://legos.cm.com/legos4.php/project/my")
        self.wait.until(EC.presence_of_element_located((By.ID, 'txtLoginName')))
        self.clearAndSendKeys("#txtLoginName", userName)
        self.clearAndSendKeys("#txtPassword", passWord)
        self.clickInSafe("#rbtnEx")
        self.clickInSafe("#ibnLogin")

    def clearAndSendKeys(self, cssSelector, keys):
        el = self.driver.find_element_by_css_selector(cssSelector)
        el.clear()
        el.send_keys(keys)

    def preventPop(self):
        self.driver.execute_script(
            "window.confirm = function(msg) { return true; };window.alert = function(msg) { return true; };")

    def acceptAlert(self):
        try:
            alert = self.driver.switch_to_alert()
            logging.info("alert:" + alert.text)
            alert.accept()
        except Exception, e:
            logging.debug(e)

    def tryDeploy(self, id):
        logging.info("deploying...")

        #my project page
        self.clickInSafe(".btn")

        self.toModulePage(id)

        self.deploy(id)

    def toModulePage(self, id):
        self.driver.find_element_by_partial_link_text(id + "--").click()

    def deploy(self, id):
        #load source code
        self.clickInSafe("#addCode")
        #save code
        self.clickInSafe("[type=submit]")
        #deploy
        id_ = self.driver.find_element_by_css_selector('[name=id]').get_attribute("value")
        url = "http://legos.cm.com/legos4.php/package/pubidc?id=" + id_
        cookies = self.getCookies(self.driver)
        response = json.loads(requests.get(url, cookies=cookies).text)
        response = json.loads(requests.get(url, cookies=cookies).text)
        if response['code'] == 0:
            logging.info('deploy success : ' + id)
        else:
            logging.info('deploy fail : ' + id)

    def getCookies(self, driver):
        cookiesResult = {}

        cookies = driver.get_cookies()
        for cookie in cookies:
            cookiesResult[cookie['name']] = cookie['value']

        return cookiesResult

    def clickInSafe(self, cssSelector):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, cssSelector)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssSelector)))
        el = self.driver.find_element_by_css_selector(cssSelector)
        el.click()
        return el

    def run(self, ids):
        try:
            dir = re.sub('\\\\', '/', os.path.normpath(os.path.abspath(__file__)))
            dir = re.sub(r'/[^/]*$', '', dir)
            settings = json.loads(open(dir + '/setting.json').read())
            self.login(settings['userName'], settings['password'])
            for id in ids:
                if id:
                    try:
                        self.tryDeploy(id)
                    except Exception, e:
                        logging.info("deploy fail : " + id)
                        continue
        finally:
            self.driver.quit()
            pass


class PubTpl(Pub):
    def toModulePage(self, id):
        self.driver.find_element_by_link_text(u"模版包管理").click()
        Pub.toModulePage(self, id)

_BASE_REGEX_STRING_TPL_ID = '^tpl_.*'

def deploy(moduleIdsOri):
    moduleIds = set()
    moduleIdsTpl = set()

    for id in moduleIdsOri:
        if re.match(_BASE_REGEX_STRING_TPL_ID, id):
            moduleIdsTpl.add(id)
        else:
            moduleIds.add(id)

    if moduleIds:
        Pub().run(moduleIds)

    if moduleIdsTpl:
        PubTpl().run(moduleIdsTpl)

if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.info)
    options, args = _GetOptionsParser().parse_args()
    moduleIds = raw_input("Please input order module ids(multiple id split by space): \n").split(" ")
    deploy(moduleIds)