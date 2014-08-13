import optparse
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
    parser.add_option('--output_file',
        dest='output_file',
        action='store',
        help=('output file path'))
    parser.add_option('--root',
        dest='root',
        action='store',
        help='root dir')

    return parser


def main():
    options, args = _GetOptionsParser().parse_args()
    output = options.output_file
    input = options.input
    options_root = options.root
    yui_compile = yui.Compile(input, output)
    if yui_compile:
        version.updater.update(output, options_root)

if __name__ == "__main__":
    main()