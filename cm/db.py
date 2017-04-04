from __future__ import generators
import psycopg as dbapi
from psycopg import Binary


class Connection:
    '''I wrap a dbapi database connection.
    I provide the query method, which all database
    operation should be used.  The query operations
    return results in ResultSets.  The instance is 
    a pool of connections, and each one
    is a autocommit connection (commit on cursor.closed()).
    '''
    def __init__(self, database, host, user, password, maxconn, minconn):
        dsn = 'dbname=%s host=%s user=%s password=%s' % (
              database, host, user, password)
        self._conn = dbapi.connect(dsn, 
                                   maxconn=maxconn, 
                                   minconn=minconn, 
                                   serialize=0)
        self._conn.autocommit(1)

    def query(self, sql, *args):
        '''Returns ResultSets.  Note that for insert/update/delete
        sql (query not supposed to return anything), the Resulsets
        would be empty [].
        '''
        cursor = self._conn.cursor()
        cursor.commit()
        if len(args) == 1 and type(args[0]) == dict:
            args = args[0]
        
        #LOGSQL
        #from cm.debug import logsql
        #logsql(sql, args, dml_only=True)
        
        cursor.execute(sql, args)
        return ResultSets(cursor)

    def get_cursor(self):
        '''Returns a cursor.  Use the returned cursor to do transactions,
        or any lower level operations.
        '''
        cursor = self._conn.cursor()
        cursor.commit()
        cursor.autocommit(0)
        return Cursor(cursor)
    

class Cursor:
    '''This is a wrapper class for the cursor class, which is a
    C extension in psycopg.  This allows us the use of logsql() 
    inside executeXXX() calls and the callproc() call.
    '''
    def __init__(self, realcursor):
        self._cursor = realcursor

    def execute(self, sql, args):
        #LOGSQL
        #from cm.debug import logsql
        #logsql(sql, args, dml_only=True)
        
        self._cursor.execute(sql, args)

    def executemany(self, sql, seq_of_args):
        # LOGSQL
        #from cm.debug import logsql
        #for args in seq_of_args:
        #    logsql(sql, args, dml_only=True)
        
        self._cursor.executemany(sql, seq_of_args)

    def callproc(self, procname, args):
        # LOGSQL
        #from cm.debug import logsql
        #logsql(procname, args, dml_only=True)
        
        self._cursor.callproc(procname, args)    
    
    def rollback(self):
        self._cursor.rollback()

    def fetchone(self):
        return self._cursor.fetchone()
    
    def fetchmany(self, size=None):
        if size is None:
            size = self._cursor.arraysize
        return self._cursor(self, size=size)
    
    def fetchall(self):
        return self._cursor.fetchall()
    
    def commit(self):
        self._cursor.commit()
        

class ResultSets:
    '''I wrap a cursor into a (enhanced) list of
    resultset for convienent usage.
    
    Usage:
    resultsets = ResultSets(cursor)
    for rs in resultsets:
        #prefer, prefer, not prefer
        print rs.store_id, row[0], row['store_id']
    '''
    def __init__(self, cursor):
        if cursor.description is None:
            # this happens when after insert/update/delete,
            # or the cursor hasn't been executed.
            self._data = []
        else:
            self._data = cursor.fetchall() #XXX
        self._cursor = cursor
        self.rowcount = cursor.rowcount
        self.description = cursor.description

    def __iter__(self):
        results = iter(self._data) #XXX
        try:
            r = RowWrapper(self.description)
        except AttributeError:
            raise StopIteration #cursor is None... nothing to iterate
        for result in results:
            r.set_data(result)
            yield r #XXX
    
    def __len__(self):
        return len(self._data)
    
    def __str__(self):
        return str(self._data)

    def __contains__(self, item):
        return self._data.__contains__(item)
    
    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getslice__(self, i, j):
        rs = ResultSets(self._cursor)
        rs._data = self._data[i:j]
        return rs

    def __setslice__(self, i, j, sequence):
        self._data.__setslice__(i, j, sequence)

    def __delslice__(self, i, j):
        self._data.__delslice__(i, j)

    def __repr__(self):
        return str(self._data)



class RowWrapper:
    '''I wrap a row of a database query result.  I give
    3 ways of getting the data, see usage below.
    
    Usage:
    #prefer, prefer, not prefer
    print rs.location, row[1], row['location']     
    for item in rs:
        print item  #this prints rs[0], rs[1]...etc accordingly
    '''
    def __init__(self, cursor_description):
        data = []
        for col in cursor_description:
            data.append(col[0])
        self._key = data
        self._color = None

    def set_data(self, aList):
        self._data = aList

    def __getattr__(self, name):
        return self._data[self._key.index(name)]      

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, index_or_name):
        if type(index_or_name) is IntType: # is an int
            return self._data[index_or_name]
        else: # is a string
            return self._data[self._key.index(index_or_name)]

    def __contains__(self, item):
        if item in self._key:
            return True
        return False

    def keys(self):
        return self._key

    def values(self):
        return self._data
        
    def items(self):
        return zip(self._key, self._data)

    
