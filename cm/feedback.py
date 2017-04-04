from cm.db import Connection
from cm.base import ObjectBase, StatusBase
from cm import datetime, config


_conn = None

def open_connection(self):
    '''A mixin method for returning a globally single
    connection object.'''
    global _conn
    if _conn is None:
        _conn = Connection(config.FB_DB_DATABASE,
                           config.FB_DB_HOST,
                           config.FB_DB_USER,
                           config.FB_DB_PASSWORD,
                           config.FB_DB_MAXCONN,
                           config.FB_DB_MINCONN)
    return _conn


class FeedbackManager(ObjectBase):
    _get_connection = open_connection

    def get_suggestions(self, kw):
        order_sql = self._get_sort_order(kw)
        by = kw.get('sort_by')
        if by == 'feedback_id':
            by_sql = 'f.feedback_id'
        elif by == 'status':
            by_sql = 'status'
        elif by == 'submitted_by':
            by_sql = 'submitted_by'
        elif by == 'assigned_to':
            by_sql = 'assigned_to'
        elif by == 'datetime':
            by_sql = 'datetime'
        else:
            by_sql = 'f.feedback_id'
            
        sql = """select f.feedback_id, s.description as status, 
              f.submitted_by_user, f.assigned_to_user,
              to_char(f.datetime, '%s') as datetime, 
              truncat(f.description) as description 
              from fb_feedback f, fb_feedback_type t, fb_feedback_status s 
              where f.status_id = s.status_id
              and f.type_id = t.type_id 
              and t.description = '%s' order by %s %s;
              """ % (datetime.PG_DATETIME_FMT, 'suggestion', 
                     by_sql, order_sql)
        return self._query(sql)

    def get_bugs(self, kw):
        order_sql = self._get_sort_order(kw)
        by = kw.get('sort_by')
        if by == 'feedback_id':
            by_sql = 'f.feedback_id'
        elif by == 'status':
            by_sql = 'status'
        elif by == 'submitted_by':
            by_sql = 'submitted_by'
        elif by == 'assigned_to':
            by_sql = 'assigned_to'
        elif by == 'datetime':
            by_sql = 'datetime'
        else:
            by_sql = 'f.feedback_id'
            
        sql = """select f.feedback_id, s.description as status, 
              f.submitted_by_user, f.assigned_to_user,
              to_char(f.datetime, '%s') as datetime, 
              truncat(f.description) as description 
              from fb_feedback f, fb_feedback_type t, fb_feedback_status s 
              where f.status_id = s.status_id
              and f.type_id = t.type_id 
              and t.description = '%s' order by %s %s;
              """ % (datetime.PG_DATETIME_FMT, 'bug', 
                     by_sql, order_sql)
        return self._query(sql)


class Feedback(ObjectBase):
    seq_name = 'fb_feedback_id'
    _get_connection = open_connection
    
    def new(self, kw):
        kw['status'] = 'open'
        sql = """insert into fb_feedback(feedback_id, status_id, type_id, 
              submitted_by_user, url, datetime, description) 
              select %(feedback_id)s, s.status_id, t.type_id, 
              %(submitted_by_user)s, %(url)s, %(datetime)s, %(description)s
              from fb_feedback_type t, fb_feedback_status s
              where t.description = %(type)s
              and s.description = %(status)s;
              """
        self._query(sql, kw)

    def set(self, kw):
        if 'status' in kw.keys():
            kw['status_id'] = FeedbackStatus().get_id(kw['status'])
            del kw['status']
        if 'type' in kw.keys():
            kw['type_id'] = FeedbackType().get_id(kw['type'])
            del kw['type']
        
        keys = kw.keys()
        f = [key + " = " + "%(" + key + ")s" for key in keys]
        sql = "update fb_feedback set " + " , ".join(f) \
              + " where feedback_id = %(feedback_id)s;"
        self._query(sql, kw)
 
    def delete(self, kw):
        sql = 'delete from fb_feedback where feedback_id = %s;'
        self._query(sql, kw.get('feedback_id'))

    def get(self, kw):
        sql = """select f.feedback_id, s.description as status, 
              t.description as type, f.submitted_by_user,
              f.assigned_to_user,
              f.url as url, 
              to_char(f.datetime, '%s') as datetime, 
              f.description as description 
              from fb_feedback f, fb_feedback_type t, fb_feedback_status s 
              where f.feedback_id = %s
              and f.status_id = s.status_id
              and f.type_id = t.type_id;
              """ % (datetime.PG_DATETIME_FMT, '%s')
        return self._query(sql, kw.get('feedback_id'))



status_singleton = None # is a resultsets 

class FeedbackStatus(StatusBase):
    _get_connection = open_connection
    
    def __init__(self):
        global status_singleton
        if status_singleton is None:
            sql = """select status_id, description 
                  from fb_feedback_status order by status_id asc;
                  """
            status_singleton = self._query(sql)
        self._data = status_singleton 
        

type_singleton = None

class FeedbackType(StatusBase):
    _get_connection = open_connection
    
    def __init__(self):
        global type_singleton
        if type_singleton is None:
            sql = """select type_id, description 
                  from fb_feedback_type order by type_id asc;
                  """
            type_singleton = self._query(sql)
        self._data = type_singleton 

