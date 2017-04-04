from cm.model import CMObjectBase, CMStatusBase
from cm import datetime


class CaseManager(CMObjectBase):
    def get(self, kw):
        order_sql = self._get_sort_order(kw)
        
        by = kw.get('sort_by')
        if by == 'case_id':
            by_sql = 'c.case_id'
        elif by == 'description':
            by_sql = 'c.description'
        elif by == 'status':
            by_sql = 'status'
        else:
            by_sql = 'c.case_id'
        
        sql = """select c.case_id, truncat(c.description) as description, 
                 cs.description as status
                 from cm_case c, cm_case_status cs
                 where c.status_id = cs.status_id
                 order by %s %s;""" % (by_sql, order_sql)
        return self._query(sql)

    def get_by_incident(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'case_id':
            by_sql = 'c.case_id'
        elif by == 'description':
            by_sql = 'c.description'
        elif by == 'status':
            by_sql = 'status'
        else:
            by_sql = 'c.case_id'

        sql = """select c.case_id, 
              truncat(c.description) as description,
              cs.description as status  
              from cm_case c, cm_case_status cs, cm_case_incident ci
              where ci.incident_id = %s
              and ci.case_id = c.case_id
              and c.status_id = cs.status_id
              order by %s %s;
              """ % ('%s', by_sql, order_sql)
        return self._query(sql, kw.get('incident_id'))


    def get_by_attachment(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'case_id':
            by_sql = 'c.case_id'
        elif by == 'description':
            by_sql = 'c.description'
        elif by == 'status':
            by_sql = 'status'
        else:
            by_sql = 'c.case_id'

        sql = """select c.case_id, truncat(c.description) as description,
              cs.description as status  
              from cm_case c, cm_case_status cs, cm_case_attachment ca
              where ca.attachment_id = %s
              and ca.case_id = c.case_id
              and c.status_id = cs.status_id
              order by %s %s;
              """ % ('%s', by_sql, order_sql)
        return self._query(sql, kw.get('attachment_id'))
       

class Case(CMObjectBase):
    seq_name = 'cm_case_id'
        
    def _set_defaults(self, kw):
        kw = CMObjectBase._set_defaults(self, kw)
        kw['description'] = kw.get('description', '')
        kw['investigation'] = kw.get('investigation', '')
        kw['evidence'] = kw.get('evidence', '')
        kw['narrative'] = kw.get('narrative', '')
        return kw


    def new(self, kw):
        kw = self._set_defaults(kw)
        kw['obj_type'] = 'case'
        
        sql = """insert into cm_case(obj_type_id, owner, create_datetime,
              modify_datetime, case_id, description, hours_expended, 
              status_id, investigation, evidence, narrative)
              select ot.obj_type_id, %(owner)s, %(datetime)s, %(datetime)s, 
              %(case_id)s, %(description)s, %(hours_expended)s, cs.status_id,
              %(investigation)s, %(evidence)s, %(narrative)
              from cm_obj_type ot, cm_case_status cs
              where ot.description = %(obj_type)s
              and cs.description = %(status)s;"""
        self._query(sql, kw)

    def set(self, kw):
        kw = self._set_defaults(kw)
        
        if 'status' in kw.keys():
            kw['status_id'] = CaseStatus().get_id(kw['status'])
            del kw['status']
        
        keys = kw.keys()
        f = [key + " = " + "%(" + key + ")s" for key in keys]
        
        sql = "update cm_case set " + " , ".join(f) \
              + " where case_id = %(case_id)s;"
        self._query(sql, kw)

    def delete(self, kw):
        _id = kw.get('case_id')
        sql = """
              delete from cm_expense where case_id = %(_id)s;
              delete from cm_daily_log where case_id = %(_id)s;
              delete from cm_interview where case_id = %(_id)s;
              delete from cm_case_incident where case_id = %(_id)s;
              delete from cm_case_attachment where case_id = %(_id)s;
              delete from cm_case where case_id = %(_id)s;
              """
        self._query(sql, kw.get('case_id'))
       
    def get(self, kw):
        sql = """select c.obj_id, c.owner, c.case_id,
              c.description, c.hours_expended, cs.description as status,
              c.investigation, c.evidence, c.narrative
              from cm_case c, cm_case_status cs
              where c.case_id = %s
              and c.status_id = cs.status_id;
              """
        return self._query(sql, kw.get('case_id'))
       
    
    def get_attachments(self, kw):
        from cm.model.attachment import AttachmentManager
        return AttachmentManager().get_by_case(kw)

    def get_incidents(self, kw):
        from cm.model.incident import IncidentManager
        return IncidentManager().get_by_case(kw)

    def get_expenses(self, kw):
        from cm.model.expense import ExpenseManager
        return ExpenseManager().get(kw)

    def get_interviews(self, kw):
        from cm.model.interview import InterviewManager
        return InterviewManager().get(kw)

    def get_daily_logs(self, kw):
        from cm.model.dailylog import DailyLogManager
        return DailyLogManager().get(kw)
    
    def attach_attachment(self, kw):
        from cm.model.attachment import Attachment
        return Attachment().attach_to_case(kw)

    def attach_incident(self, kw):
        from cm.model.incident import Incident
        return Incident().attach_to_case(kw)



status_singleton = None # is a resultsets 

class CaseStatus(CMStatusBase):
    def __init__(self):
        global status_singleton
        if status_singleton is None:
            sql = """select status_id, description 
                  from cm_case_status order by status_id asc;
                  """
            status_singleton = self._query(sql)
        self._data = status_singleton
        
