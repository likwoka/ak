from cm.db import Connection, Binary
from cm import config, i18n, user

import cPickle as pickle
from time import time

from quixote import get_session_manager # for export
from quixote.session import Session
from quixote.errors import SessionError 


_conn = None

def open_connection():
    '''Returns a globally single connection instance.'''
    global _conn
    if _conn is None:
        _conn = Connection(config.SES_DB_DATABASE,
                           config.SES_DB_HOST,
                           config.SES_DB_USER,
                           config.SES_DB_PASSWORD,
                           config.SES_DB_MAXCONN,
                           config.SES_DB_MINCONN)
    return _conn


class PostgresMapping:
    '''I am the relational database mapping.'''
    
    COMPLETE = 0
    SESSION_START = 1
    SESSION_END = 99999
    
    def __init__(self, connection=None):
        if connection is not None:
            self._conn = connection
        else:
            self._conn = open_connection()
    
    def keys(self):
        '''keys() -> [string]
        
        Returns a list of session IDs.
        '''
        sql = '''select distinct session_id from ses_session 
              order by session_id asc'''
        return [r.session_id for r in self._conn.query(sql)]
        
    def values(self):
        '''values() -> [Session]

        Return the list of sessions in this session manager.
        '''
        sql = '''select session_id, value_, order_ 
              from ses_session
              order by session_id asc, order_ asc;'''
        rs = self._conn.query(sql)
        result = []
        for r in rs:
            try:
                if r.order_ == self.COMPLETE: 
                    # a complete session
                    p = r.value_
                    result.append(pickle.loads(p))
                elif r.order_ == self.SESSION_END: 
                    # end of a chopped session
                    p += r.value_
                    result.append(pickle.loads(p))
                elif r.order_ == self.SESSION_START: 
                    # start of a chopped session
                    p = r.value_
                else: 
                    # body of a chopped session
                    p += r.value_
            except pickle.UnpicklingError:
                # an invalid pickle
                result.append(None) 
        return result

    def items(self):
        '''items() -> [(string, Session)]
        
        Return the list of (session_id, session) pairs
        '''
        sql = '''select session_id, value_, order_ 
              from ses_session
              order by session_id asc, order_ asc;'''
        rs = self._conn.query(sql)
        result = []
        for r in rs:
            try:
                if r.order_ == self.COMPLETE: 
                    # a complete session
                    p = r.value_
                    result.append((r.session_id, pickle.loads(p)))
                elif r.order_ == self.SESSION_END: 
                    # end of a chopped session
                    p += r.value_
                    result.append((r.session_id, pickle.loads(p)))
                elif r.order_ == self.SESSION_START: 
                    # start of a chopped session
                    p = r.value_
                else: 
                    # body of a chopped session
                    p += r.value_
            except pickle.UnpicklingError:
                # an invalid pickle
                result.append(None)
        return result
        
    def __getitem__(self, session_id):
        '''__getitem__(session_id : string) -> Session

        Return the session object identified by 'session_id'.  Raise KeyError
        if no such session.
        '''
        sql = '''select value_ from ses_session 
              where session_id = %s
              order by order_ asc;'''
        rs = self._conn.query(sql, session_id)
        p = ''
        for r in rs:
            p += r.value_
        try: 
            session = pickle.loads(p)
        except EOFError: # no such session
            raise KeyError(session_id)
        except pickle.UnpicklingError:
            session = None #XXX
        return session
        
    def get(self, session_id, default=None):
        '''get(session_id : string, default : any = None) -> Session

        Return the session object identified by 'session_id', 
        or None if no such session.
        '''
        try:
            return self[session_id]
        except KeyError:
            return default
    
    def has_key(self, session_id):
        '''has_key(session_id : string) -> boolean

        Return true if a session identified by 'session_id' exists.
        '''
        sql = '''select session_id from ses_session
              where session_id = %s;'''
        rs = self._conn.query(sql, session_id)
        if rs.rowcount > 0:
            return True
        return False
    
    def __setitem__(self, session_id, session):
        '''__setitem__(session_id : string, session : Session)

        Store 'session' under 'session_id'.
        '''
        # We get a dbapi cursor because we want a transaction.
        # The pickling may raise an error which cause the
        # transaction to abort, else we commit the transaction
        # at the end.
        p = pickle.dumps(session, True) # Binary format 

        cursor = self._conn.get_cursor() 
        # Delete the existing session.
        try:
            sql = '''delete from ses_session where session_id = %s;'''
            cursor.execute(sql, (session_id,))
            
            # Then insert the updated session.
            sql = '''insert into ses_session(session_id, value_, order_)
                  values(%s, %s, %s);'''
            length = len(p)   
            order = self.COMPLETE
            if length <= 4000:
                cursor.execute(sql, (session_id, Binary(p), order))
            else:
                for start in range(0, length, 4000):
                    order += 1
                    end = start + 3999
                    if end > length:
                        end = length
                        order = self.SESSION_END
                    cursor.execute(sql, (session_id, p[start:end], order))
        except:
            cursor.rollback()
            raise
        cursor.commit()
        
    def __delitem__(self, session_id):
        '''_delitem__(session_id : string)

        Remove the session object identified by 'session_id'.  
        Raise KeyError if no such session.
        '''
        sql = '''delete from ses_session
              where session_id = %s;'''
        rs = self._conn.query(sql, session_id)
        if rs.rowcount <= 0:
            raise KeyError(session_id, 'No such session %s' % session_id)


#---------------------------------------------------------------------------
class TimeoutSession(Session):
    '''Provides Timeout capability.'''
    timeout_period = config.SESSION_TIMEOUT
    resolution = 1 # for calculation of last access time

    def __init__(self, request, id):
        Session.__init__(self, request, id)
        self.last_access_time = time()

    def set_last_access_time(self, time):
        self.last_access_time = time
        self._dirty = True

    def start_request(self, request):
        '''start_request(request : HTTPRequest)

        Called near the beginning of each request: after the HTTPRequest
        object has been built and this Session object has been fetched
        or built, but before we traverse the URL or call the callable
        object found by URL traversal.
        '''
        now = time()
        if now - self.last_access_time > self.timeout_period:
            raise SessionError(session_id=self.id)
        
        if now - self.last_access_time > self.resolution:
            self.set_last_access_time(now)
        
        Session.start_request(self, request)


class AKSession(TimeoutSession):
    '''I provide custom session attributes and the timeout capability.'''

    def __init__(self, request, id):
        TimeoutSession.__init__(self, request, id)
        self._dirty = False
        self.role = None #set at user.register()
        self.response_status_code = None #set at every finish request
        #use default language; real language set at user.register()
        self.lang = i18n.LangInstance() 

    def set_user(self, user):
        '''Set the username (a String).'''
        self.user = user
        self._dirty = True
        
    def set_role(self, role):
        '''Set the role (a String).'''
        self.role = user.RoleInstance(role)
        self._dirty = True

    def set_lang(self, lang_code=None):
        '''Set the language (a String).'''
        self.lang = i18n.LangInstance(lang_code)
        self._dirty = True
        
    def is_dirty(self):
        '''
        Returns True if this session needs to be updated 
        (written out) to the session mapping (for persistence).
        '''        
        # We record the access time, which changes every
        # time the user send a request, but we ignore redirect (302)
        # which usually is triggered by a previous user request, and
        # errors (4XX, 5XX).
        if self.response_status_code < 300 or self._dirty:
            self._dirty = False
            return True
        return False
   
    def start_request(self, request):
        '''start_request(request : HTTPRequest)

        Called near the beginning of each request: after the HTTPRequest
        object has been built and this Session object has been fetched
        or built, but before we traverse the URL or call the callable
        object found by URL traversal.
        '''
        self.lang.install() # use the language in this session
        TimeoutSession.start_request(self, request)
        
    def finish_request(self, request):
        '''finish_request(request : HTTPRequest)

        Called near the end of each request: after a callable object has
        been found and (successfully) called.  Not called if there were
        any errors processing the request.
        '''
        #set response status code (200, 302, 404..etc)
        self.response_status_code = request.response.status_code


def reap_dead_sessions(timeout_period, session_mapping):
    '''Deletes expired sessions.  I should be run by
    either a separate daemon program, or periodically
    by a thread.
    
    timeout_period - a session is expired if it 
                     is inactive for this many seconds.
    session_mapping - an instance of a session mapping or 
                      a session manager.
    '''
    p = session_mapping
    items = p.items()
    for session_id, session in items:
        if session.get_access_age() > timeout_period:
            try:
                del p[session_id]
            except KeyError:
                # may be it is deleted in the
                # mean time, so just ignore the
                # error
                pass

