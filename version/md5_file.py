# coding=utf-8

__author__ = 'jinker'

from hashlib import md5


def md5_file(name):
    m = md5()
    a_file = open(name, 'rb')    #需要使用二进制格式读取文件内容
    m.update(a_file.read())
    a_file.close()
    return m.hexdigest()

if __name__ == '__main__':
    print md5_file('G:/workspace/bocai/build/lib/version/updater.py')