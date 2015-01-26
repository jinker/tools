import optparse
import os
from version import updater
import version
from yui import yui


def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)
    parser.add_option('-i',
                      '--input',
                      dest='input',
                      action='store',
                      help='input file path')
    parser.add_option('--root',
                      dest='root',
                      action='store',
                      help='root dir')

    parser.add_option('--update_build_version',
                      dest='update_build_version',
                      action='store',
                      help='update_build_version')

    return parser


def main():
    options, args = _GetOptionsParser().parse_args()
    input = options.input
    root = options.root
    update_build_version = options.update_build_version == 'True'

    path_splitext = os.path.splitext(input)

    file_name_no_suffix = os.path.splitext(os.path.basename(input))[0]
    timestamp, build_path = version.updater.get_build_version(input, update_build_version)
    dir = root.replace("\\", "/") + version.updater.BASE_BUILD_DIR + build_path + "/"
    build_path = dir + file_name_no_suffix + "." + timestamp + ".min" + path_splitext[1]

    build_path_expired = path_splitext[0] + ".min" + path_splitext[1]

    build_path = yui.compile(input, build_path)

    if build_path and os.path.exists(build_path):
        version.updater.update(version.updater.get_rel_path(build_path, root), [root],
                               version.updater.get_rel_path(build_path_expired, root))


if __name__ == "__main__":
    main()