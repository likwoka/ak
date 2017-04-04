'''
A long running process which removes expired sessions.
'''
import sys, time, getopt


class UsageError(Exception):
    def __init__(self, msg=''):
        self.msg = msg


usage = '''\nUsage: $python graphreaper.py [OPTION]

A long running process which removes expired graphs.

Options:
    -o  --oneshot       remove expired graphs now and then exit.
    -h, --help          display this message\n'''


def main(argv=None):
    
    is_oneshot = False
    
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'ho', ['help', 'oneshot'])
        except getopt.error, msg:
            raise UsageError(msg)
        
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                raise UsageError(usage)
            if opt in ('-o', '--oneshot'):
                is_oneshot = True
        
    except UsageError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, 'For help use --help.'
        return 2
    
    #LOGIC STARTS HERE
    try:
        from cm.config import REAP_GRAPHS_EVERY, GRAPH_EXPIRY
        from cm.plot import reap_dead_graphs
    except ImportError, err:
        print >> sys.stderr, 'Apparently your cm package cannot be found' \
                 ' on the python path.'
        return 2
    
    sleep_increment = 10.0
    run_every = REAP_GRAPHS_EVERY

    if not is_oneshot:
        print >> sys.stdout, 'Press <Control-C> to exit.'
    while True:
        try:
            reap_dead_graphs()

            if is_oneshot: return 1
                
            for i in xrange(0, run_every, sleep_increment):
                remainder = run_every - i
                if remainder < i:
                    time.sleep(remainder)
                else:
                    time.sleep(sleep_increment)
        except KeyboardInterrupt:
            print >> sys.stdout, 'Exiting.'
            break


if __name__ == '__main__':
    sys.exit(main())


