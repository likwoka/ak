from cm.base import ObjectBase, StatusBase
from cm.db import Connection
from cm import config, datetime


_conn = None

def open_connection(self):
    '''A mixin method for returning a globally single
    connection object.'''
    global _conn
    if _conn is None:
        _conn = Connection(config.CM_DB_DATABASE,
                           config.CM_DB_HOST,
                           config.CM_DB_USER,
                           config.CM_DB_PASSWORD,
                           config.CM_DB_MAXCONN,
                           config.CM_DB_MINCONN)
    return _conn
   
class CMObjectBase(ObjectBase):
    _get_connection = open_connection

    def _set_defaults(self, kw):
        '''Sets the default values for certain 'always there' columns.
        This method is usually called in a update/insert operation.
        Returns the modified keyword dictionary.
        '''
        kw['modify_datetime'] = kw.get('modify_datetime', datetime.now())
        return kw

class CMStatusBase(StatusBase):
    _get_connection = open_connection


