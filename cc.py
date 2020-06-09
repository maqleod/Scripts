#!/usr/bin/env python3

#IMPORTS - built-ins
import optparse
import os.path
import sys

# CONSTANTS
# basics
NAME = "cc"
VER = "0.0.1"
# args
DESC = "Simple utility to print number of chars in file, stdin or argument."
EPILOG = """
Version: %(ver)s
""" % {'ver': VER}

# ARGS
parser = optparse.OptionParser(description=DESC, epilog=EPILOG)
parser.add_option(
    '-V',
    '--version',
    help='print version and exit',
    dest="version",
    default=False,
    action="store_true")

options, args = parser.parse_args()  # set up argument parser

if options.version:  # no need to go further if this is all we want
    print(VER)
    sys.exit()


# MAIN
def main():  # main script wrapper function
    try:
        # if we have an argument, first check if its a path
        if os.path.isfile(sys.argv[1]):
            with open(sys.argv[1], 'r') as myfile:
                line = myfile.read()
        else:
            # if not a file, then just read all arguments
            line = " ".join(sys.argv[1:])
    except Exception:
        # if no argument, try stdin (pipe)
        try:
            line = ""
            for part in sys.stdin:
                line = line + part
        except Exception:
            #if that still fails, then well, we got nothin
            line = ""
    print(str(len(line)))
        
if __name__ == "__main__":
    main()
