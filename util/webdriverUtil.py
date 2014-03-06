__author__ = 'jinker'

def getCookies(driver):
    cookiesResult = {}

    cookies = driver.get_cookies()
    for cookie in cookies:
        cookiesResult[cookie['name']] = cookie['value']

    return cookiesResult