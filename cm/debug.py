from quixote.publish import Publisher
from cm.cookie import UserNameCookie
from cm.user import RoleInstance
import time, inspect
from types import *


SQLLOG = '/home/staging/ak/log/sampledata.log'


class Dummy:
    def expire_session(self, request): pass
    def set_user(self, name):
        self.user = name


class DebugPublisher(Publisher):
    '''I allow user to bypass security check by
    assigning user ('alex_test') to a session.  
    Hence it always appear that there is a session,
    but in fact there is none.
    '''
    def start_request(self, request):
        session = Dummy()
        session.set_user('alex')
        session.role = RoleInstance('developer')
        request.session = session
        UserNameCookie().set(request, 'alex')

    session_mgr = Dummy()


def dprint(*args):
    '''Provides a better debug print method than print.
    Time, source file, and line number are stated.
    '''
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    f = inspect.getouterframes(inspect.currentframe())[1] 
    print '<-- [%s] %s, line %s' % (t, f[1], f[2])
    for arg in args:
        print arg,
    print '\n-->'


_sqllog = -1 # -1 means not initialized

def _open_sqllog():
    '''A factory function which returns the sqllog file object.'''
    global _sqllog
    if _sqllog == -1:
        try:
            _sqllog = file(SQLLOG, 'a+')
        except IOError:
            _sqllog = None
    return _sqllog
        
        
def logsql(sql, args, dml_only=False):
    '''Log the sql, with parameters filled in, to the sqllog (or debug log).
    This way, a sample database can be generated from the GUI, with
    sql saved to a file for regenerating the database from a script.
    
    dml_only -- if True, then only log DML query (insert, delete, update)
                This is useful when you want to only log all sql for
                creating a database sample
    '''
    if dml_only:
        if sql[0:23] == 'delete from ses_session' or \
            sql[0:23] == 'insert into ses_session'or \
            sql[0:6] == 'select':
                # the sql is about session, or returning data,
                # therefore don't log anything
                return 
    
    sqllog = _open_sqllog()
    print >> sqllog, '-' * 45, '[%s]' % time.strftime('%Y-%m-%d %H:%M:%S')
    
    if len(args) == 0: # A empty dict {}
        print >> sqllog, sql
    else:
        if isinstance(args, (ListType, TupleType)):
            args2 = []
            for arg in args:
                if isinstance(arg, StringTypes): #normal and unicode types
                    args2.append("'%s'" % arg)
                else:
                    args2.append(arg)

            print >> sqllog, sql % tuple(args2)
        elif isinstance(args, DictType):
            args2 = {}
            for k, v in args.iteritems():
                if isinstance(v, StringTypes):
                    args2[k] = "'%s'" % v
                else:
                    args2[k] = v
            print >> sqllog, sql % args2
    
    print >> sqllog, '-' * 45
    sqllog.flush()
        

