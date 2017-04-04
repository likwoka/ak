from cm.model import CMObjectBase
from cm import datetime


class DailyLogManager(CMObjectBase):
    def get(self, kw):
        order_sql = self._get_sort_order(kw)
        
        by = kw.get('sort_by')
        if by == 'daily_log_id':
            by_sql = 'daily_log_id'
        elif by == 'date':
            by_sql = 'date'
        elif by == 'description':
            by_sql = 'description'
        else:
            by_sql = 'daily_log_id'

        sql = """select daily_log_id, to_char(date_, '%s') as date, 
              truncat(description) as description
              from cm_daily_log
              where case_id = %s
              order by %s %s;
              """ % (datetime.PG_DATE_FMT, '%s', by_sql, order_sql)
        return self._query(sql, kw.get('case_id'))


class DailyLog(CMObjectBase):
    seq_name = 'cm_daily_log_id'

    def new(self, kw):
        kw['obj_type'] = 'case'

        sql = """insert into cm_daily_log(obj_type_id, owner, create_datetime,
              modify_datetime, daily_log_id, case_id, date_, description)
              select ot.obj_type_id, %(owner)s, %(datetime)s, %(datetime)s,
              %(daily_log_id)s, %(case_id)s, %(date)s, %(description)s
              from cm_obj_type ot
              where ot.description = %(obj_type)s;
              """
        self._query(sql, kw)


    def set(self, kw):
        if 'date' in kw.keys():
            kw['date_'] = kw['date']
            del kw['date']
            
        keys = kw.keys()
        f = [key + " = " + "%(" + key + ")s" for key in keys]
        
        sql = "update cm_daily_log set " + " , ".join(f) \
              + " where daily_log_id = %(daily_log_id)s;"
        self._query(sql, kw)
       
       
    def delete(self, kw):
        sql = "delete from cm_daily_log where daily_log_id = %s;"
        self._query(sql, kw.get('daily_log_id'))


    def get(self, kw):
        sql = """select obj_id, owner, daily_log_id, 
              case_id, to_char(date_, '%s') as date, description
              from cm_daily_log
              where daily_log_id = %s;
              """ % (datetime.PG_DATE_FMT, '%s')
        return self._query(sql, kw.get('daily_log_id'))

    
