from cm.model import CMObjectBase, CMStatusBase
from cm import datetime


class IncidentManager(CMObjectBase):
    def get(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'incident_id':
            by_sql = 'i.incident_id'
        elif by == 'date':
            by_sql = 'date, time'
        elif by == 'time':
            by_sql = 'time, incident_id'
        elif by == 'store_id':
            by_sql = 'i.store_id'
        elif by == 'description':
            by_sql = 'i.description'
        elif by == 'status':
            by_sql = 'status'
        else:
            by_sql = 'incident_id'

        sql = """select i.incident_id, 
              to_char(i.date_, '%s') as date, 
              to_char(i.time_, '%s') as time, 
              i.store_id, truncat(i.description) as description, 
              ins.description as status 
              from cm_incident i, cm_incident_status ins
              where i.status_id = ins.status_id 
              order by %s %s;
              """ % (datetime.PG_DATE_FMT, 
                     datetime.PG_TIME_FMT, by_sql, order_sql)
        return self._query(sql)

    def get_by_case(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'incident_id':
            by_sql = 'i.incident_id'
        elif by == 'date':
            by_sql = 'date, time'
        elif by == 'time':
            by_sql = 'time, incident_id'
        elif by == 'store_id':
            by_sql = 'i.store_id'
        elif by == 'description':
            by_sql = 'i.description'
        elif by == 'status':
            by_sql = 'status'
        else:
            by_sql = 'incident_id'

        sql = """select i.incident_id, 
              to_char(i.date_, '%s') as date, 
              to_char(i.time_, '%s') as time, 
              i.store_id, truncat(i.description) as description, 
              ins.description as status 
              from cm_incident i, cm_incident_status ins, 
              cm_case_incident ci
              where ci.case_id = %s
              and ci.incident_id = i.incident_id
              and i.status_id = ins.status_id 
              order by %s %s;
              """ % (datetime.PG_DATE_FMT, datetime.PG_TIME_FMT, 
                     '%s', by_sql, order_sql)
        return self._query(sql, kw.get('case_id'))
    
    def get_by_attachment(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'incident_id':
            by_sql = 'i.incident_id'
        elif by == 'description':
            by_sql = 'i.description'
        elif by == 'status':
            by_sql = 'status'
        else:
            by_sql = 'i.incident_id'

        sql = """select i.incident_id, truncat(i.description) as description,
              ins.description as status  
              from cm_incident i, cm_incident_status ins, 
              cm_incident_attachment ia
              where ia.attachment_id = %s
              and ia.incident_id = i.incident_id
              and i.status_id = ins.status_id
              order by %s %s;
              """ % ('%s', by_sql, order_sql)
        return self._query(sql, kw.get('attachment_id'))


class Incident(CMObjectBase):
    seq_name = 'cm_incident_id'

    def _set_defaults(self, kw):
        kw = CMObjectBase._set_defaults(self, kw)
        kw['description'] = kw.get('description', '')
        kw['who'] = kw.get('who', '')
        kw['narrative'] = kw.get('narrative', '')
        kw['outcome'] = kw.get('outcome', '')
        kw['service_request'] = kw.get('service_request', '')
        return kw
    
    def new(self, kw):
        kw = self._set_defaults(kw)
        kw['obj_type'] = 'incident'
        
        sql = """insert into cm_incident(obj_type_id, owner, create_datetime,
              modify_datetime, incident_id, description, who, date_, time_,
              store_id, narrative, outcome, service_request, status_id)
              select ot.obj_type_id, %(owner)s, %(datetime)s, %(datetime)s,
              %(incident_id)s, %(description)s, %(who)s, %(date)s, %(time)s,
              s.store_id, %(narrative)s, %(outcome)s, %(service_request)s, 
              ins.status_id
              from cm_obj_type ot, cm_store s, cm_incident_status ins
              where ot.description = %(obj_type)s
              and s.store_id = %(store_id)s
              and ins.description = %(status)s;"""
        self._query(sql, kw)
        
    def set(self, kw):
        kw = self._set_defaults(kw)
        
        if 'status' in kw.keys():
            kw['status_id'] = IncidentStatus().get_id(kw['status'])
            del kw['status']
        if 'time' in kw.keys():
            kw['time_'] = kw['time']
            del kw['time']
        if 'date' in kw.keys():
            kw['date_'] = kw['date']
            del kw['date']
        
        keys = kw.keys()
        f = [key + " = " + "%(" + key + ")s" for key in keys]
        sql = "update cm_incident set " + " , ".join(f) \
              + " where incident_id = %(incident_id)s;"
        self._query(sql, kw)

    def delete(self, kw):
        _id = kw.get('incident_id')
        sql = """
              delete from cm_item where incident_id = %(_id)s
              delete from cm_incident_attachment where incident_id = %(_id)s;
              delete from cm_case_incident where incident_id = %(_id)s;
              delete from cm_incident where incident_id = %(_id)s;
              """
        self._query(sql, vars())

    def get(self, kw):
        sql = """select i.obj_id, i.owner, i.incident_id,
        i.description, i.who, 
        to_char(i.date_, '%s') as date, 
        to_char(i.time_, '%s') as time, 
        i.store_id, s.location, i.narrative, i.outcome, 
        i.service_request, isa.description as status
        from cm_incident i, cm_incident_status isa, cm_store s
        where i.incident_id = %s
        and i.status_id = isa.status_id
        and i.store_id = s.store_id;
        """ % (datetime.PG_DATE_FMT, datetime.PG_TIME_FMT, '%s')
        return self._query(sql, kw.get('incident_id'))

    def get_attachments(self, kw):
        from cm.model.attachment import AttachmentManager
        return AttachmentManager().get_by_incident(kw)
        
    def get_items(self, kw):
        from cm.model.item import ItemManager
        return ItemManager().get_by_incident(kw)

    def get_cases(self, kw):
        from cm.model.case import CaseManager
        return CaseManager().get_by_incident(kw)

    def attach_to_case(self, kw):
        sql = """insert into cm_case_incident(incident_id, case_id)
              values(%(incident_id)s, %(case_id)s)
              """
        self._query(sql, kw)

    def attach_attachment(self, kw):
        from cm.model.attachment import Attachment
        return Attachment().attach_to_incident(kw)

    def detach_from_case(self, kw):
        sql = """delete from cm_case_incident
              where case_id = %(case_id)s
              and incident_id = %(incident_id)s;
              """
        self._query(sql, kw)



status_singleton = None # is a resultsets 

class IncidentStatus(CMStatusBase):
    def __init__(self):
        global status_singleton
        if status_singleton is None:
            sql = """select status_id, description 
                  from cm_incident_status order by status_id asc;
                  """
            status_singleton = self._query(sql)
        self._data = status_singleton
        
