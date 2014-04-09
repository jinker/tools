import optparse
from closure.closure_templates import closureTemplates

def _GetOptionsParser():
    """Get the options parser."""

    parser = optparse.OptionParser(__doc__)
    parser.add_option('-i',
        '--input',
        dest='input',
        action='store',
        help='input file path')
    parser.add_option('--outputFileFormat',
        dest='outputFileFormat',
        action='store',
        help='output file file format')

    return parser


def main():
    options, args = _GetOptionsParser().parse_args()
    outputPathFormat = options.outputFileFormat
    closureTemplates.process([options.input], outputPathFormat)

if __name__ == "__main__":
    main()