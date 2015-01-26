# coding:utf-8
# !/usr/bin/env python
#
# Copyright 2009 The Closure Library Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
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
import time
import logging
import optparse
import os
import sys
import posixpath

from closure2amd import closure2amd
import eos
from legos import legos
import version.updater
import depstree
import jscompiler
import source
import treescan
from util import svn, authUtil


__author__ = 'nnaze@google.com (Nathan Naze)'


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
                      choices=['list', 'script', 'compiled', 'compiledSimple', 'compiledSimpleByModule',
                               'calcdepsIndependent',
                               'calcdepsIndependentDetail', 'calcAndOrganizeDepsIndependent',
                               'genModuleJsEntryPoint', 'compiledByModule', 'findEntriesByModule',
                               'findModulesByModule',
                               'calcdepsIndependentByModule', 'convertToLegosByEntrypoint', 'convertToLegos',
                               'pubDeps2Eos'],
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

    parser.add_option('--host',
                      dest='host',
                      action='store',
                      help=('host of modulejs'))

    parser.add_option('--eos',
                      dest='eos',
                      default=False,
                      action='store',
                      help=('if execute eos'))

    parser.add_option('--update_build_version',
                      dest='update_build_version',
                      default=True,
                      action='store',
                      help=('update_build_version'))

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
        logging.warning('No Closure base.js file found.')
        return None
        # sys.exit(1)
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
    path = path.replace('../../../../static/v1.0/', '../../../../v1.0/')

    provides = sorted(js_source.provides)
    requires = sorted(js_source.requires)

    return 'goog.addDependency(\'%s\', %s, %s);\n' % (path, provides, requires)


def _GetModuleJsLine(path, js_source):
    """Get a entrypoint.js file string for a source."""

    provides = sorted(js_source.provides)

    path = os.path.dirname(path) + "/" + os.path.splitext(os.path.basename(path))[0] + ".amd.js"

    return ',\n'.join(['"%s": "%s"' % (provide, path) for provide in provides])


def _GetPair(s):
    """Return a string as a shell-parsed tuple.  Two values expected."""
    try:
        # shlex uses '\' as an escape character, so they must be escaped.
        # s = s.replace('\\', '\\\\')
        first, second = s.split('*')
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
        # return moduleName.replace(".", "$$$")
        return ''

    def writeRequires(self, requiresAll):
        sourceRemoveComment = self._source
        # remove old requires
        sourceRemoveComment = source._REQUIRES_REGEX_LINE.sub('', sourceRemoveComment)
        sourceRemoveComment = source._PROVIDE_REGEX_LINE.sub('', sourceRemoveComment)
        sourceRemoveComment = source.Source._StripComments(sourceRemoveComment)
        sourceRemoveComment = source.Source._COMMENT_INLINE_REGEX.sub('', sourceRemoveComment)
        sourceRemoveComment = source._STRING_REGEX_LINE.sub('', sourceRemoveComment)

        requiresDirect = set()
        for moduleName in requiresAll:
            if re.search(r'(?<![\w\d\_\-@])' + (moduleName.replace(".", "\.")).replace("$", "\$") + r"(?![\w\d\_\-@])",
                         sourceRemoveComment):
                sourceRemoveComment = sourceRemoveComment.replace(moduleName, self.GetFlatName(moduleName))
                requiresDirect.add(moduleName)

        requiresDirect.update(self.requires)
        for provide in self.provides:
            try:
                requiresDirect.remove(provide)
            except Exception:
                pass

                # requiresDirect.difference(self.requires)
        if requiresDirect.difference(self.requires):
            requiresDirect = sorted(requiresDirect)
            # update requires
            self.requires = requiresDirect

            requireStatement = 'goog.require("%s");'
            requireStatements = ''
            for require in requiresDirect:
                requireStatements += (requireStatement % require) + "\n"

            requireStatements += "\n"

            sourceNew = source._REQUIRES_REGEX_LINE.sub('', self._source)

            re_provide = re.compile('((\n?\s*goog\.provide\(\s*[\'"].*[\'"]\s*\);?\n*)+)')
            if requiresDirect:
                sourceNew = re_provide.sub(r'\1' + requireStatements, sourceNew)

            if sourceNew != self._source:
                self._source = sourceNew
                svn.try_lock(self._path)
                out = open(self._path, "w")
                out.write(sourceNew)


def write_deps_file(deps, input_namespaces, outputDir, root_with_prefix):
    try:
        os.makedirs(outputDir)
    except:
        pass
    deps_path = outputDir + "/" + input_namespaces.copy().pop() + ".deps.js"
    svn.try_lock(deps_path)
    out = open(deps_path, 'w')
    out.write('// This file was autogenerated by %s.\n' % sys.argv[0])
    out.write('// Please do not edit.\n')
    root_with_prefix, prefix = _GetPair(root_with_prefix)
    out.writelines(
        [_GetDepsLine(js_source.GetPath().replace(root_with_prefix, prefix).replace(os.sep, posixpath.sep), js_source)
         for js_source in deps])
    logging.info('The deps file : ' + deps_path)


def calcAndOrganizeDepsIndependent(deps, input_namespaces, output_dir, root_with_prefix, sources):
    # exclude closure module
    depsExcludeClosure = []
    providesExcludeClosure = set()
    for source in sources:
        if not "closure" in source.GetPath():
            providesExcludeClosure.update(source.provides)
    for source in deps:
        if not "closure" in source.GetPath():
            depsExcludeClosure.append(source)
    providesExcludeClosure = sorted(providesExcludeClosure, reverse=True)
    for source in depsExcludeClosure:
        source.writeRequires(providesExcludeClosure)
    write_deps_file(deps, input_namespaces, output_dir, root_with_prefix)


def genModuleJsEntryPoint(deps, input_namespaces, modulejs, output_dir, root_with_prefix, host):
    # genernate modulejs entrypoint file
    entryModule = input_namespaces.pop()
    entrypoint_js = entryModule + ".entrypoint.js"

    template = open(os.path.dirname(__file__) + '/../../../modulejs/template4entrypoint.js', "r").read()

    template = template.replace("/*host*/", host)
    rootWithPrefix, prefix = _GetPair(root_with_prefix)
    template = template.replace("/*urlMap*/", ',\n'.join(
        [_GetModuleJsLine(js_source.GetPath().replace(rootWithPrefix, prefix).replace(os.sep, posixpath.sep), js_source)
         for js_source in deps if not 'closure' in js_source.GetPath()]))
    template = template.replace("/*moduleJs*/", open(modulejs, "r").read())
    template = template.replace("/*entryPointModule*/", entryModule)

    dir_entrypoint_js = output_dir + "/" + entrypoint_js
    svn.try_lock(dir_entrypoint_js)
    out = open(dir_entrypoint_js, 'w')
    out.write(template)

    logging.info('The entrypoint url is:\nhttp://888.gtimg.com/static/v1.0/i/js/entrypoint/' + entrypoint_js)
    logging.info('Success.')


def compile(compiler_jar_path, deps, inputs, compiler_flags, root, update_build_version=True):
    input = list(inputs)[0]
    # Make sure a .jar is specified.
    if not compiler_jar_path:
        logging.error('--compiler_jar flag must be specified if --output is '
                      '"compiled"')
        return None
    compiled_source = jscompiler.Compile(
        compiler_jar_path,
        deps,
        compiler_flags)
    if compiled_source is None:
        logging.error('JavaScript compilation failed.')
        return None
    else:
        logging.info('JavaScript compilation succeeded.')

        file_name_no_suffix = os.path.splitext(os.path.basename(input))[0]

        min_js = os.path.dirname(input) + "/" + file_name_no_suffix + ".c.min.js"

        timestamp, build_path = version.updater.get_build_version(input, update_build_version)
        dir = root.replace("\\", "/") + version.updater.BASE_BUILD_DIR + build_path + "/"
        min_js_new = dir + file_name_no_suffix + "." + timestamp + ".c.min.js"

        if not os.path.exists(dir):
            os.makedirs(dir)

        svn.try_lock(min_js_new)
        out = open(min_js_new, "w")
        out.write(compiled_source)
        logging.info('min js : ' + min_js_new)

        return min_js_new, min_js


def getSources(options_roots, args):
    sources = set()
    logging.info('Scanning paths...')
    for path in options_roots:
        for js_path in treescan.ScanTreeForJsFiles(path):
            sources.add(_PathSource(js_path))

    # Add scripts specified on the command line.
    for js_path in args:
        sources.add(_PathSource(js_path))
    logging.info('%s sources scanned.', len(sources))
    return sources


def compileSimple(compiler_jar_path, deps, inputs, compiler_flags, roots, exeEos, update_build_version):
    minJs, minJsExpired = compile(compiler_jar_path, deps, inputs, compiler_flags, roots[0],
                                  update_build_version=update_build_version)
    if minJs:
        out = open(minJs, "r")
        content = out.read()
        content = re.sub('var COMPILED=false;[\s\S]*goog\.scope=function\(fn\)\{fn\.call\(goog\.global\)\};', '',
                         content)
        # 将"goog.require(...);"移除
        content = re.sub('goog\.require\([^)]*\);', '', content)
        # 将"goog.provide(...);"替换成"CP.util.namespace(...);"
        content = re.sub('goog\.provide', 'CP.util.namespace', content)
        # 避免CP命名覆盖问题
        content = re.sub('var CP=\{(\w+):(\{[^}]*\})\}', 'var CP=CP||{};CP.\1={}', content)

        svn.try_lock(minJs)
        out = open(minJs, "w")
        out.write(content)

        minJsExpired = version.updater.get_rel_path(minJsExpired, roots[0])
        htmlPaths = version.updater.update(version.updater.get_rel_path(minJs, roots[0]), roots, minJsExpired)
        htmlRealPaths = []

        paths = [minJs]
        for path in htmlPaths:
            htmlRealPaths.append(path)
            paths.append(path)

        if exeEos:
            add_eos_mission(paths, minJs, roots[0])

    return (minJs, htmlRealPaths)


def isEntryPointModule(namespace, source_map):
    for path in source_map.keys():
        for require in source_map[path].requires:
            if require == namespace:
                return False
    return True


def getEntryPointSourceMap(source_map):
    paths = sorted(source_map.keys())
    source_map_noGoog = {}  # 非closure库模块
    for path in paths:
        js_source = source_map[path]
        if js_source.provides:
            namespace = js_source.provides.copy().pop()
            if (not (re.compile("^goog").match(namespace) or re.compile("^cp\.tpl").match(namespace))):
                source_map_noGoog[path] = js_source
    source_map_entryPoint = {}  # 入口模块
    for path in source_map_noGoog.keys():
        js_source = source_map_noGoog[path]
        if isEntryPointModule(js_source.provides.copy().pop(), source_map_noGoog):
            source_map_entryPoint[path] = js_source
    return source_map_entryPoint


def convertToLegos(dep):
    modelName = dep.provides.copy().pop()
    if ((re.compile('goog\.cp')).match(modelName) or not (re.compile('goog')).match(modelName)) and not (
            re.compile('^soy')).match(modelName):
        amdCode, modelName = closure2amd.getAmdCodeBySource(dep)
        createRes = legos.createModule(pid='100', name=modelName, title=modelName, desc='', code=amdCode)
        if not createRes:
            legos.saveByModelName(name=modelName, code=amdCode, compressionType='option1')


def main():
    logging.basicConfig(format=(sys.argv[0] + ': %(message)s'),
                        level=logging.INFO)
    options, args = _GetOptionsParser().parse_args()

    output_file = options.output_file
    roots = options.roots
    inputs = options.inputs
    namespaces = options.namespaces
    output_mode = options.output_mode
    output_dir = options.output_dir
    root_with_prefix = options.root_with_prefix
    compiler_jar_path = options.compiler_jar
    compiler_flags = options.compiler_flags
    update_build_version = options.update_build_version == 'True'

    # Make our output pipe.
    if output_file:
        svn.try_lock(output_file)
        out = open(output_file, 'w')
    else:
        out = sys.stdout

    sources = getSources(roots, args)

    # Though deps output doesn't need to query the tree, we still build it
    # to validate dependencies.
    logging.info('Building dependency tree..')
    tree = depstree.DepsTree(sources)

    input_namespaces = set()
    inputs = inputs or []
    for input_path in inputs:
        js_input = _GetInputByPath(input_path, sources)
        if not js_input:
            logging.error('No source matched input %s', input_path)
            sys.exit(1)
        input_namespaces.update(js_input.provides)

    input_namespaces.update(namespaces)

    if not input_namespaces:
        logging.error('No namespaces found. At least one namespace must be '
                      'specified with the --namespace or --input flags.')
        sys.exit(2)

    deps = tree.GetDependencies(input_namespaces)

    # The Closure Library base file must go first.
    base = _GetClosureBaseFile(sources)
    if base:
        deps = [base] + deps

    if output_mode == 'list':
        out.writelines([js_source.GetPath() + '\n' for js_source in deps])
    elif output_mode == 'calcdepsIndependent':
        write_deps_file(deps, input_namespaces, output_dir, root_with_prefix)
    elif output_mode == 'calcdepsIndependentDetail':
        for dep in deps:
            print dep.provides.copy().pop(), '\t', dep.GetPath(), '\t', len(dep.GetSource())
    elif output_mode == 'calcAndOrganizeDepsIndependent':
        calcAndOrganizeDepsIndependent(deps, input_namespaces, output_dir, root_with_prefix, sources)
    elif output_mode == 'genModuleJsEntryPoint':
        modulejs = options.modulejs
        genModuleJsEntryPoint(deps, input_namespaces, modulejs, output_dir, root_with_prefix, options.host)
    elif output_mode == 'script':
        out.writelines([js_source.GetSource() for js_source in deps])
    elif output_mode == 'compiled':
        min_js, min_js_expired = compile(compiler_jar_path, deps, inputs, compiler_flags, roots[0],
                                         update_build_version=update_build_version)

        if min_js:
            min_js_expired = version.updater.get_rel_path(min_js_expired, roots[0])
            html_paths = version.updater.update(version.updater.get_rel_path(min_js, roots[0]), roots, min_js_expired)

            paths = [min_js]
            for path in html_paths:
                paths.append(path)

            if options.eos:
                add_eos_mission(paths, min_js, roots[0])
        else:
            sys.exit(1)
    elif output_mode == 'compiledByModule':
        namespace_target = input_namespaces.copy().pop()
        sources = tree.GetLeafSourcesByNameSpace(namespace_target)

        paths = []
        for dep in sources:
            namespace = dep.provides.copy().pop()
            if not re.compile("^test").match(namespace):
                min_js, min_js_expired = compile(compiler_jar_path, [base] + tree.GetDependencies(namespace),
                                                 [dep.GetPath()], compiler_flags, roots[0],
                                                 update_build_version=update_build_version)

                if min_js:
                    min_js_expired = version.updater.get_rel_path(min_js_expired, roots[0])
                    html_paths = version.updater.update(version.updater.get_rel_path(min_js, roots[0]), roots, min_js_expired)

                    paths.append(min_js)
                    for path in html_paths:
                        paths.append(path)

        if options.eos:
            add_eos_mission(paths, namespace_target, roots[0])
    elif output_mode == 'compiledSimple':
        compileSimple(compiler_jar_path, deps, inputs, compiler_flags, roots, options.eos,
                      update_build_version=update_build_version)
    elif output_mode == 'compiledSimpleByModule':
        namespace_target = input_namespaces.copy().pop()
        sources = tree.GetLeafSourcesByNameSpace(namespace_target)

        paths = []
        for dep in sources:
            namespace = dep.provides.copy().pop()
            if not re.compile("^test").match(namespace):
                min_js, html_paths = compileSimple(compiler_jar_path, [base] + tree.GetDependencies(namespace),
                                                   [dep.GetPath()], compiler_flags, roots, False,
                                                   update_build_version=update_build_version)

                if min_js:
                    paths.append(min_js)
                    for path in html_paths:
                        paths.append(path)

        if options.eos:
            add_eos_mission(paths, namespace_target, roots[0])
    elif output_mode == 'findEntriesByModule':
        sources = tree.GetLeafSourcesByNameSpace(input_namespaces.copy().pop())

        print 'length:', str(len(sources))
        for dep in sources:
            print dep.provides.copy().pop(), '\t', dep.GetPath()
    elif output_mode == 'findModulesByModule':
        sources = tree.GetDirectSourcesByNameSpace(input_namespaces.copy().pop())

        for dep in sources:
            print dep.provides.copy().pop(), '\t', dep.GetPath()
    elif output_mode == 'calcdepsIndependentByModule':
        sources = tree.GetLeafSourcesByNameSpace(input_namespaces.copy().pop())

        for dep in sources:
            write_deps_file([base] + tree.GetDependencies(dep.provides.copy().pop()), dep.provides, output_dir,
                            root_with_prefix)
    elif output_mode == 'convertToLegosByEntrypoint':
        for dep in deps:
            convertToLegos(dep)
    elif output_mode == 'convertToLegos':
        convertToLegos(_PathSource(inputs[0]))
    elif output_mode == 'pubDeps2Eos':
        abs_paths = []
        for dep in deps:
            path = dep.GetPath()
            abs_paths.append(path)

        add_eos_mission(abs_paths, 'deps for : ' + input_namespaces.copy().pop(), roots[0], False)
    else:
        logging.error('Invalid value for --output flag.')
    sys.exit(2)


def add_eos_mission(file_paths, subject, project_path, wait=True):
    rel_paths = []
    for path in file_paths:
        rel_paths.append(version.updater.get_rel_path(path, project_path))

    if wait:
        time.sleep(len(file_paths) * 5)
    eos.add_eos_mission(module=eos.MODULE_BOCAI_HOME, file_relative_paths=rel_paths, subject=subject,
                        executors=[authUtil.get_user_name()], middle_path='/html', filePathsAbs=file_paths,
                        project_path=project_path)
