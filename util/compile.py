'''
Byte-compile all .ptl, .py files.   

Run this script before starting a quixote process
allow all files to be compiled before being served,
sparing the process of compiling and thus serve
the first request for each resource (a lot) faster.
'''

import compileall, sys, getopt
from quixote import ptl_compile


def compile_ptl(dir):
    ptl_compile.compile_dir(dir, maxlevels=30)


def compile_py(dir):
    compileall.compile_dir(dir, maxlevels=30)


class UsageError(Exception):
    def __init__(self, msg=''):
        self.msg = msg


usage = '''\nUsage: $python compile.py [OPTION] dir

Byte-compile all .py and .ptl files to .pyc and .ptlc files
in the directory recursively.

Options:
    -h, --help              display this message\n'''


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
        DIR = args[0]
        compile_ptl(DIR)
        compile_py(DIR)

    except UsageError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, 'For help use --help.'
        return 2

    
if __name__ == '__main__':
    sys.exit(main())

