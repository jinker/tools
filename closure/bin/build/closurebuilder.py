#!/usr/bin/env python
#
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

"""Utility for Closure Library dependency calculation.

ClosureBuilder scans source files to build dependency info.  From the
dependencies, the script can produce a manifest in dependency order,
a concatenated script, or compiled output from the Closure Compiler.

Paths to files can be expressed as individual arguments to the tool (intended
for use with find and xargs).  As a convenience, --root can be used to specify
all JS files below a directory.

usage: %prog [options] [file1.js file2.js ...]
"""
import re

__author__ = 'nnaze@google.com (Nathan Naze)'

import logging
import optparse
import os
import sys
import posixpath

import depstree
import jscompiler
import source
import treescan


def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)
    parser.add_option('-i',
        '--input',
        dest='inputs',
        action='append',
        default=[],
        help='One or more input files to calculate dependencies '
             'for.  The namespaces in this file will be combined with '
             'those given with the -n flag to form the set of '
             'namespaces to find dependencies for.')
    parser.add_option('-n',
        '--namespace',
        dest='namespaces',
        action='append',
        default=[],
        help='One or more namespaces to calculate dependencies '
             'for.  These namespaces will be combined with those given '
             'with the -i flag to form the set of namespaces to find '
             'dependencies for.  A Closure namespace is a '
             'dot-delimited path expression declared with a call to '
             'goog.provide() (e.g. "goog.array" or "foo.bar").')
    parser.add_option('--root',
        dest='roots',
        action='append',
        default=[],
        help='The paths that should be traversed to build the '
             'dependencies.')
    parser.add_option('-o',
        '--output_mode',
        dest='output_mode',
        type='choice',
        action='store',
        choices=['list', 'script', 'compiled', 'calcdepsIndependent', 'calcAndOrganizeDepsIndependent', 'genModuleJsEntryPoint'],
        default='list',
        help='The type of output to generate from this script. '
             'Options are "list" for a list of filenames, "script" '
             'for a single script containing the contents of all the '
             'files, or "compiled" to produce compiled output with '
             'the Closure Compiler.  Default is "list".')
    parser.add_option('-c',
        '--compiler_jar',
        dest='compiler_jar',
        action='store',
        help='The location of the Closure compiler .jar file.')
    parser.add_option('-f',
        '--compiler_flags',
        dest='compiler_flags',
        default=[],
        action='append',
        help='Additional flags to pass to the Closure compiler. '
             'To pass multiple flags, --compiler_flags has to be '
             'specified multiple times.')
    parser.add_option('--output_file',
        dest='output_file',
        action='store',
        help=('If specified, write output to this path instead of '
              'writing to standard output.'))
    parser.add_option('--root_with_prefix',
        dest='root_with_prefix',
        default=[],
        action='store',
        help='A root directory to scan for JS source files, plus '
             'a prefix (if either contains a space, surround with '
             'quotes).  Paths in generated deps file will be relative '
             'to the root, but preceded by the prefix.')
    parser.add_option('--output_dir',
        dest='output_dir',
        action='store',
        help=('dir of output file'))

    parser.add_option('--modulejs',
        dest='modulejs',
        action='store',
        help=('path of modulejs'))

    return parser


def _GetInputByPath(path, sources):
    """Get the source identified by a path.

    Args:
      path: str, A path to a file that identifies a source.
      sources: An iterable collection of source objects.

    Returns:
      The source from sources identified by path, if found.  Converts to
      absolute paths for comparison.
    """
    for js_source in sources:
        # Convert both to absolute paths for comparison.
        if os.path.abspath(path) == os.path.abspath(js_source.GetPath()):
            return js_source


def _GetClosureBaseFile(sources):
    """Given a set of sources, returns the one base.js file.

    Note that if zero or two or more base.js files are found, an error message
    will be written and the program will be exited.

    Args:
      sources: An iterable of _PathSource objects.

    Returns:
      The _PathSource representing the base Closure file.
    """
    base_files = [
    js_source for js_source in sources if _IsClosureBaseFile(js_source)]

    if not base_files:
        logging.error('No Closure base.js file found.')
        sys.exit(1)
    if len(base_files) > 1:
        logging.error('More than one Closure base.js files found at these paths:')
        for base_file in base_files:
            logging.error(base_file.GetPath())
        sys.exit(1)
    return base_files[0]


def _IsClosureBaseFile(js_source):
    """Returns true if the given _PathSource is the Closure base.js source."""
    return (os.path.basename(js_source.GetPath()) == 'base.js' and
            js_source.provides == set(['goog']))


def _GetDepsLine(path, js_source):
    """Get a deps.js file string for a source."""

    provides = sorted(js_source.provides)
    requires = sorted(js_source.requires)

    return 'goog.addDependency(\'%s\', %s, %s);\n' % (path, provides, requires)


def _GetModuleJsLine(path, js_source):
    """Get a entrypoint.js file string for a source."""

    provides = sorted(js_source.provides)

    return ',\n'.join(['"%s": "%s"' % (path, provide) for provide in provides])


def _GetPair(s):
    """Return a string as a shell-parsed tuple.  Two values expected."""
    try:
        # shlex uses '\' as an escape character, so they must be escaped.
        #s = s.replace('\\', '\\\\')
        first, second = s.split('||')
        return (first, second)
    except:
        raise Exception('Unable to parse input line as a pair: %s' % s)


class _PathSource(source.Source):
    """Source file subclass that remembers its file path."""

    def __init__(self, path):
        """Initialize a source.

        Args:
          path: str, Path to a JavaScript file.  The source string will be read
            from this file.
        """
        super(_PathSource, self).__init__(source.GetFileContents(path))

        self._path = path

    def GetPath(self):
        """Returns the path."""
        return self._path

    def GetFlatName(self, moduleName):
    #        return moduleName.replace(".", "$$$")
        return ''

    def writeRequires(self, requiresAll):
        sourceRemoveComment = self._source
        #remove old requires
        sourceRemoveComment = source._REQUIRES_REGEX_LINE.sub('', sourceRemoveComment)
        sourceRemoveComment = source._PROVIDE_REGEX_LINE.sub('', sourceRemoveComment)
        sourceRemoveComment = source.Source._StripComments(sourceRemoveComment)
        sourceRemoveComment = source.Source._COMMENT_INLINE_REGEX.sub('', sourceRemoveComment)
        sourceRemoveComment = source._STRING_REGEX_LINE.sub('', sourceRemoveComment)

        requiresDirect = set()
        for moduleName in requiresAll:
            if re.search(r'(?<![\w\d\_\-\$@])' + moduleName.replace(".", "\.") + r"(?![\w\d\_\-\$@])",
                sourceRemoveComment):
                sourceRemoveComment = sourceRemoveComment.replace(moduleName, self.GetFlatName(moduleName))
                requiresDirect.add(moduleName)

        requiresDirect.update(self.requires)
        for provide in self.provides:
            try:
                requiresDirect.remove(provide)
            except Exception:
                pass
        requiresDirect = sorted(requiresDirect)

        #update requires
        self.requires = requiresDirect

        requireStatement = 'goog.require("%s");'
        requireStatements = ''
        for require in requiresDirect:
            requireStatements += (requireStatement % require) + "\n"

        requireStatements += "\n"

        sourceNew = source._REQUIRES_REGEX_LINE.sub('', self._source)

        #((\n?\s*goog\.provide\(\s*[\'"].*[\'"]\s*\);?\n*)+)
        re_provide = re.compile('((\n?\s*goog\.provide\(\s*[\'"].*[\'"]\s*\);?\n*)+)')
        if requiresDirect:
            sourceNew = re_provide.sub(r'\1\n' + requireStatements, sourceNew)
        out = open(self._path, "w")
        out.write(sourceNew)


def writeDepsFile(deps, input_namespaces, options):
    out = open(options.output_dir + "/" + input_namespaces.pop() + ".deps.js", 'w')
    out.write('// This file was autogenerated by %s.\n' % sys.argv[0])
    out.write('// Please do not edit.\n')
    rootWithPrefix, prefix = _GetPair(options.root_with_prefix)
    out.writelines(
        [_GetDepsLine(js_source.GetPath().replace(rootWithPrefix, prefix).replace(os.sep, posixpath.sep), js_source)
         for js_source in deps])


def main():
    logging.basicConfig(format=(sys.argv[0] + ': %(message)s'),
        level=logging.INFO)
    options, args = _GetOptionsParser().parse_args()

    # Make our output pipe.
    if options.output_file:
        out = open(options.output_file, 'w')
    else:
        out = sys.stdout

    sources = set()

    logging.info('Scanning paths...')
    for path in options.roots:
        for js_path in treescan.ScanTreeForJsFiles(path):
            sources.add(_PathSource(js_path))

    # Add scripts specified on the command line.
    for js_path in args:
        sources.add(_PathSource(js_path))

    logging.info('%s sources scanned.', len(sources))

    # Though deps output doesn't need to query the tree, we still build it
    # to validate dependencies.
    logging.info('Building dependency tree..')
    tree = depstree.DepsTree(sources)

    input_namespaces = set()
    inputs = options.inputs or []
    for input_path in inputs:
        js_input = _GetInputByPath(input_path, sources)
        if not js_input:
            logging.error('No source matched input %s', input_path)
            sys.exit(1)
        input_namespaces.update(js_input.provides)

    input_namespaces.update(options.namespaces)

    if not input_namespaces:
        logging.error('No namespaces found. At least one namespace must be '
                      'specified with the --namespace or --input flags.')
        sys.exit(2)

    # The Closure Library base file must go first.
    base = _GetClosureBaseFile(sources)
    deps = [base] + tree.GetDependencies(input_namespaces)

    output_mode = options.output_mode
    if output_mode == 'list':
        out.writelines([js_source.GetPath() + '\n' for js_source in deps])
    elif output_mode == 'calcdepsIndependent':
        writeDepsFile(deps, input_namespaces, options)
    elif output_mode == 'calcAndOrganizeDepsIndependent':
        #exclude closure module
        depsExcludeClosure = []
        providesExcludeClosure = set()
        for dep in deps:
            if not "closure" in dep.GetPath():
                depsExcludeClosure.append(dep)
                providesExcludeClosure.update(dep.provides)

        providesExcludeClosure = sorted(providesExcludeClosure, reverse=True)
        for dep in depsExcludeClosure:
            dep.writeRequires(providesExcludeClosure)

        writeDepsFile(deps, input_namespaces, options)
    elif output_mode == 'genModuleJsEntryPoint':
        #genernate modulejs entrypoint file
        entryModule = input_namespaces.pop()
        entrypoint_js = entryModule + ".entrypoint.js"
        out = open(options.output_dir + "/" + entrypoint_js
            , 'w')
        out.write('// This file was autogenerated by %s.\n' % sys.argv[0])
        out.write('// Please do not edit.\n')
        out.write('_moduleConfig = {alias: {\n')
        rootWithPrefix, prefix = _GetPair(options.root_with_prefix)

        out.write(',\n'.join([_GetModuleJsLine(js_source.GetPath().replace(rootWithPrefix, prefix).replace(os.sep, posixpath.sep), js_source)
                              for js_source in deps]))

        out.write('}};\n')
        out.write(open(options.modulejs, "r").read())
        out.write("\n")
        out.write('_mytouchConfig = {"index": ["%s", "init"], "containerId": "businessContent"};setTimeout(function () {modulejs(["%s"], function (m) {});}, 10);' % (entryModule, entryModule))

        logging.info('The entrypoint url is:\nhttp://888.gtimg.com/static/v1.0/i/js/entrypoint/' + entrypoint_js)
        logging.info('Success.')
    elif output_mode == 'script':
        out.writelines([js_source.GetSource() for js_source in deps])
    elif output_mode == 'compiled':
        # Make sure a .jar is specified.
        if not options.compiler_jar:
            logging.error('--compiler_jar flag must be specified if --output is '
                          '"compiled"')
            sys.exit(2)

        compiled_source = jscompiler.Compile(
            options.compiler_jar,
            [js_source.GetPath() for js_source in deps],
            options.compiler_flags)

        if compiled_source is None:
            logging.error('JavaScript compilation failed.')
            sys.exit(1)
        else:
            logging.info('JavaScript compilation succeeded.')
            out.write(compiled_source)

    else:
        logging.error('Invalid value for --output flag.')
        sys.exit(2)


if __name__ == '__main__':
    main()