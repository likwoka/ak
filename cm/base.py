def query(self, sql, *args):
    '''Mixin method for the XXXBase class.
    conn should be a cm.db.Connection instance.'''
    conn = self._get_connection()
    return conn.query(sql, *args)

def get_connection(self):
    '''Mixin method for the XXXBase class.
    Returns a cm.db.Connection instance.'''
    raise 'No implementation.'


class ObjectBase:
    '''I am the basis of the model class.'''
    seq_name = None # The name of the autoincrement id column in the table.

    def _set_defaults(self, kw):
        '''Sets the default values for certain 'always there' columns.
        This method is usually called in a update/insert operation.
        Returns the modified keyword dictionary.
        '''
        return kw

    def get_id(self):
        '''Returns an ID (unique identifier) for the object instance.'''
        if self.seq_name is None:
            raise 'There is no autoincrement column.'
        else:
            sql = """select nextval('%s');""" % self.seq_name
            rs = self._query(sql)
            for r in rs:
                _id = r.nextval
            return _id

    def _get_sort_order(self, kw, default=None):
        '''Returns the sort order according to key:value parsed in.
        This method is usually called in a get/select operation. 
        '''
        order = kw.get('sort_order')
        if order == 'up':
            order_sql = 'asc'
        elif order == 'down':
            order_sql = 'desc'
        else:
            if default is None:
                order_sql = 'asc'
            elif default == 'up':
                order_sql = 'asc'
            elif default == 'down':
                order_sql = 'desc'
            else:
                order_sql = 'asc'
        return order_sql
    
    _query = query
    _get_connection = get_connection
       

class StatusBase:
    '''I am the basis of the 'type'/'status' listing
    class.
    '''
    def ids(self):
        '''Returns a list of ID.'''
        return [i for (i, s) in self._data]

    def descs(self):
        '''Returns a list of Description.'''
        return [s for (i, s) in self._data]    
   
    def get_id(self, desc):
        '''Given a description, returns the related ID.'''
        ret = [i for (i, s) in self._data if desc == s]
        if ret is not None:
            return ret[0]
        else:
            raise 'No such desc <%s>.' % desc

    _query = query
    _get_connection = get_connection

