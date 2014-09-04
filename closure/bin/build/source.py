# Copyright 2009 The Closure Library Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Scans a source JS file for its provided and required namespaces.

Simple class to scan a JavaScript file and express its dependencies.
"""

__author__ = 'nnaze@google.com'

import re

_BASE_REGEX_STRING = '^\s*goog\.%s\(\s*[\'"](.+)[\'"]\s*\)'
_PROVIDE_REGEX = re.compile(_BASE_REGEX_STRING % 'provide')
_REQUIRES_REGEX = re.compile(_BASE_REGEX_STRING % 'require')
_PROVIDE_REGEX_LINE = re.compile('\n\s*goog\.provide\(\s*[\'"].+[\'"]\s*\);?')
_REQUIRES_REGEX_LINE = re.compile('\n\s*goog\.require\(\s*[\'"].+[\'"]\s*\);?')
_STRING_REGEX_LINE = re.compile('(\'.*?(?<!\\\)\'|".*?(?<!\\\)")')

# This line identifies base.js and should match the line in that file.
_GOOG_BASE_LINE = (
    'var goog = goog || {}; // Identifies this file as the Closure base.')

_REQUIRES_REGEX_SOY_OR_SOYDATA = re.compile('^\s*goog\.require\(\s*[\'"](soy|soydata)[\'"]\s*\)')
_REGEX_SOY_OR_SOYDATA = re.compile('(soy|soydata)\.[^(]+\(')

COMMENT_REGEXS = [
    re.compile('^\s*//'), #//
    re.compile('^\s*/?\*+\s*@(lends|class|param|return|augments|constructs|example)'), #/* @lends|class|param|return|augments|constructs|example
]

def isComment(line):
    for reg in COMMENT_REGEXS:
        if reg.match(line):
            return True
    return False

class Source(object):
    """Scans a JavaScript source for its provided and required namespaces."""

    # Matches a "/* ... */" comment.
    # Note: We can't definitively distinguish a "/*" in a string literal without a
    # state machine tokenizer. We'll assume that a line starting with whitespace
    # and "/*" is a comment.
    _COMMENT_REGEX = re.compile(
        r"""
        ^\s*   # Start of a new line and whitespace
        /\*    # Opening "/*"
        .*?    # Non greedy match of any characters (including newlines)
        \*/    # Closing "*/""",
        re.MULTILINE | re.DOTALL | re.VERBOSE)

    _COMMENT_INLINE_REGEX = re.compile("\/\/[^\n]*")

    def __init__(self, source):
        """Initialize a source.

        Args:
          source: str, The JavaScript source.
        """
        self.nameSpaces = []

        self.nameMap = {}

        self.provides = set()
        self.requires = set()

        self._source = source
        self._ScanSource()

    def __str__(self):
        return 'Source %s' % self._path

    def snakeCased(self, str):
        return str.replace(".", "_")

    def getNameMap(self):
        return self.nameMap

    def GetSource(self):
        """Get the source as a string."""
        return self._source

    @classmethod
    def _StripComments(cls, source):
        return cls._COMMENT_REGEX.sub('', source)

    def getNames(self):
        return self.nameSpaces

    def getCamelName(self, str):
        try:
            value = self.nameMap[str]
            if value:
                return value
        except Exception:
            pass

        return None

    def _ScanSource(self):
        """Fill in provides and requires by scanning the source."""

        source = self._StripComments(self.GetSource())

        source_lines = source.splitlines()
        for line in source_lines:
            match_group = ''
            match = _PROVIDE_REGEX.match(line)
            if match:
                match_group = match.group(1)
                self.provides.add(match.group(1))
            match = _REQUIRES_REGEX.match(line)
            if match:
                match_group = match.group(1)
                self.requires.add(match_group)

            if match_group:
                self.nameMap[match_group] = self.snakeCased(match_group)
                self.nameSpaces.append(match_group)

        # Closure's base file implicitly provides 'goog'.
        for line in source_lines:
            if line == _GOOG_BASE_LINE:
                if len(self.provides) or len(self.requires):
                    raise Exception(
                        'Base files should not provide or require namespaces.')
                self.provides.add('goog')


def GetFileContents(path):
    """Get a file's contents as a string.

    Args:
      path: str, Path to file.

    Returns:
      str, Contents of file.

    Raises:
      IOError: An error occurred opening or reading the file.

    """
    fileobj = open(path)
    try:
        return fileobj.read()
    finally:
        fileobj.close()


if __name__ == "__main__":
    print re.compile('\'.*?(?<!\\\)\'').sub('', open('E:/workspace/tools/closure/bin/build/test.js', 'r').read())
#    print re.compile('\'.+?(?<!(\\{1}))\'').sub("",
#        "output += '<li class=\'game ' + ((bettingGameData8._expired) ? 'expired' : '') + ' ' + ((bettingGameData8._selectedDs) ? 'on' : '') + '\' data-game-id=\'' + bettingGameData8._id + '\'><span class=\"no\">' + bettingGameData8._gameNo + '</span><span class=\"home-team\">' + bettingGameData8._homeTeam.name + '</span><span class=\"handicap\">' + ((bettingGameData8._handicap != null && bettingGameData8._handicap != 0) ? '(' + ((bettingGameData8._handicap > 0) ? '<span class=\'red bold\'>+' + bettingGameData8._handicap + '</span>' : '<span class=\'green bold\'>' + bettingGameData8._handicap + '</span>') + ')' : '') + '</span><span class=\"game-time\">' + soy.$$escapeHtml(cp.date.util.format(bettingGameData8._gameTime,'%h:%m',true)) + '</span><span class=\"visiting-team\">' + bettingGameData8._visitingTeam.name + '</span></li>';")
