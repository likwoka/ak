'''
Copyright (c) Alex Li 2003.  All rights reserved.
'''

__version__ = '0.1'
__file__ = 'rmcompile.py'


import os, getopt, sys


EXTLIST = ['.ptlc', '.pyc']


def remove(extlist, dirname, files):
    for file in files:
        (name, ext) = os.path.splitext(file)
        if ext in extlist:
            os.remove(os.path.join(dirname, file))


class UsageError(Exception):
    def __init__(self, msg=''):
        self.msg = msg


usage = '''\nUsage: $python %s [OPTION] dir

Remove all .pyc and .ptlc files in the directory recursively.

Options:
    -h, --help              display this message\n''' % __file__


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise UsageError(msg)
        
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                raise UsageError(usage)
        
        if len(args) != 1:
            raise UsageError('E: Wrong number of argument.')
        
        #LOGIC STARTS HERE
        global EXTLIST
        dir = args[0]
        os.path.walk(dir, remove, EXTLIST)

    except UsageError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, 'For help use --help.'
        return 2

    
if __name__ == '__main__':
    sys.exit(main())

