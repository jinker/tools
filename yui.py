import optparse
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

    return parser


def main():
    options, args = _GetOptionsParser().parse_args()
    yui.Compile(options.input, options.output_file)

if __name__ == "__main__":
    main()