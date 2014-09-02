import json
import os
import re

__author__ = 'jinkerjiang'

dir = re.sub('\\\\', '/', os.path.normpath(os.path.abspath(__file__)))
dir = re.sub(r'/[^/]*$', '', dir)
settings = json.loads(open(dir + '/../setting.json').read())


def getUserName():
    return settings['userName']