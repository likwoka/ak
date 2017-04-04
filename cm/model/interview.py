from cm.model import CMObjectBase
from cm import datetime


class InterviewManager(CMObjectBase):
    def get(self, kw):
        order_sql = self._get_sort_order(kw)
        
        by = kw.get('sort_by')
        if by == 'interview_id':
            by_sql = 'interview_id'
        elif by == 'date':
            by_sql = 'date, time'
        elif by == 'time':
            by_sql = 'time, interview_id'
        elif by == 'interviewer':
            by_sql = 'interviewer'
        elif by == 'interviewee':
            by_sql = 'interviewee'
        elif by == 'description':
            by_sql = 'description'
        else:
            by_sql = 'interview_id'

        sql = """select interview_id, to_char(date_, '%s') as date, 
              to_char(time_, '%s') as time,
              interviewer, interviewee, truncat(description) as description
              from cm_interview
              where case_id = %s
              order by %s %s;
              """ % (datetime.PG_DATE_FMT, datetime.PG_TIME_FMT, '%s', 
                     by_sql, order_sql)
        return self._query(sql, kw.get('case_id'))


class Interview(CMObjectBase):
    seq_name = 'cm_interview_id'

    def new(self, kw):
        kw = self._set_defaults(kw)
        kw['obj_type'] = 'interview'

        sql = """insert into cm_interview(obj_type_id, owner, create_datetime,
              modify_datetime, interview_id, case_id, date_, time_, interviewer,
              interviewee, description)
              select ot.obj_type_id, %(owner)s, %(datetime)s, %(datetime)s,
              %(interview_id)s, %(case_id)s, %(date)s, %(time)s, 
              %(interviewer)s, %(interviewee)s, %(description)s
              from cm_obj_type ot
              where ot.description = %(obj_type)s;"""
        self._query(sql, kw)

    def set(self, kw):
        kw = self._set_defaults(kw)
        if 'date' in kw.keys():
            kw['date_'] = kw['date']
            del kw['date']
        if 'time' in kw.keys():
            kw['time_'] = kw['time']
            del kw['time']
            
        keys = kw.keys()
        f = [key + " = " + "%(" + key + ")s" for key in keys]
        
        sql = "update cm_interview set " + " , ".join(f) \
              + " where interview_id = %(interview_id)s;"
        self._query(sql, kw)

    def delete(self, kw):
        sql = "delete from cm_interview where interview_id = %s;"
        self._query(sql, kw.get('interview_id'))

    def get(self, kw):
        sql = """select obj_id, owner, interview_id, case_id,
              to_char(date_, '%s') as date,
              to_char(time_, '%s') as time,
              interviewer, interviewee, description
              from cm_interview
              where interview_id = %s
              """ % (datetime.PG_DATE_FMT, datetime.PG_TIME_FMT, '%s')
        return self._query(sql, kw.get('interview_id'))
              
       
