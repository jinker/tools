#coding:utf-8
import json
import logging
import optparse
import os
import re
import urllib
from urllib2 import HTTPError
import urllib2
from pip._vendor import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

__author__ = 'jinker'

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC


def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)

    parser.add_option('--orderId',
        dest='orderIds',
        action='store',
        help='web base path')

    return parser


class OrderPublisher1():
    def __init__(self):
        self.exceptionCount = 0
        self.MAX_EXCEPTION = 6

        #        self.driver = webdriver.Remote("http://%s:%s/wd/hub" % ('127.0.0.1', '4444'), DesiredCapabilities.HTMLUNIT)

        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, userName, passWord):
        self.driver.get("http://pub.bocaiwawa.com/index.shtml")
        self.wait.until(EC.presence_of_element_located((By.ID, 'username')))
        self.clearAndSendKeys("#username", userName)
        self.clearAndSendKeys("#password", passWord)
        self.clickInSafe("input[name=subcribe]")

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
            logging.info("alert:" + unicode(alert.text, "gb2312"))
            alert.accept()
        except Exception, e:
            logging.debug(e)

    def trySubmitOrder(self, id):
        logging.info("submitting...")
        self.checkOrderState(id)

        if self.isPresent("#lin_cancel_order"):
            self.cancelOrder(id)
            self.resetOrder(id)
            self.submitOrder(id)
        elif self.isPresent("#lin_reset_order"):
            self.resetOrder(id)
            self.submitOrder(id)
        elif self.isPresent("#btn_submit_form"):
            self.submitOrder(id)
        else:
            logging.info("Order " + id + " has been deployment or deleted")

    def isPresent(self, cssSelector):
        try:
            if self.driver.find_element_by_css_selector(cssSelector):
                return True
            else:
                return False
        except NoSuchElementException:
            return False

    def checkOrderState(self, id):
        self.acceptAlert()
        self.driver.get("http://pub.bocaiwawa.com/test_list.php?id=" + id)
        self.preventPop()

    def cancelOrder(self, id):
        self.checkOrderState(id)
        self.clickInSafe("#lin_cancel_order")

    def resetOrder(self, id):
        self.checkOrderState(id)
        self.clickInSafe("#lin_reset_order")

    def submitOrder(self, id):
        self.checkOrderState(id)

        propEls = self.driver.find_elements_by_css_selector("#form1 [type=hidden]")
        data = {}
        for ipt in propEls:
            try:
                data[ipt.get_attribute('name')] = ipt.get_attribute('value')
            except Exception:
                pass
                #response = self.requestSubmit(data, self.getCookies(self.driver))
        response = self.post('http://pub.bocaiwawa.com/receive.php', data, self.getCookies(self.driver))
        if (not u"返回" in unicode(response, 'gb2312')):
            self.submitOrder(id)
            return
        logging.info("order sub success : " + id)

    #        self.submit_old(id)

    def post(self, url, data, cookies):
        req = urllib2.Request(url)
        data = urllib.urlencode(data)
        #enable cookie
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

        cookieStr = ''
        for key, value in cookies.items():
            cookieStr += "%s=%s; " % (key, value)

        opener.addheaders.append(('Cookie', cookieStr))
        response = opener.open(req, data)
        return response.read()

    def requestSubmit(self, data, cookies):
        try:
            post = requests.post('http://pub.bocaiwawa.com/receive.php', data=data, cookies=cookies)
        except Exception, e:
            print e
            return self.requestSubmit(data, cookies)
        post.encoding = 'gb2312'
        return post.content

    def submit_old(self, id):
        self.clickInSafe("#btn_submit_form")
        try:
            self.clickInSafe('a[href="test_file.php"]')
            logging.info("order sub success : " + id)
        except Exception, e:
            self.submitOrder(id)

    def getCookies(self, driver):
        cookiesResult = {}

        cookies = driver.get_cookies()
        for cookie in cookies:
            cookiesResult[cookie['name']] = cookie['value']

        return cookiesResult

    def getHeaders(self):
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Cookie': 'pgv_pvid=8168912156; bc_agent=1300000297; PHPSESSID=fda4def2ddc0bdcd2cc6a795d4b588ab',
            'Host': 'pub.bocaiwawa.com',
            'Referer': 'http://pub.bocaiwawa.com/test_list.php?id=62802',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0'
        }

    def clickInSafe(self, cssSelector):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, cssSelector)))
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
                        self.trySubmitOrder(id)
                    except Exception, e:
                        print e
                        logging.info("order sub failed : " + id)
                        continue
        finally:
            try:
                self.driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    options, args = _GetOptionsParser().parse_args()
    logging.info("Please input order id(s) (multi ids should be separated by space): ")
    orderIds = raw_input().split(" ")
    OrderPublisher1().run(orderIds)