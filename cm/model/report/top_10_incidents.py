from cm.model import CMObjectBase


class Logic(CMObjectBase):
    def get(self, kw):
        order_sql = self._get_sort_order(kw, default='down')
        
        by = kw.get('sort_by')
        if by == 'incident_id':
            by_sql = 'i.incident_id'
        elif by == 'description':
            by_sql = 'description'
        elif by == 'status':
            by_sql = 'status'
        elif by == 'amount':
            by_sql = 'amount'
        else:
            by_sql = 'amount'
            
        sql = """
              select i.incident_id, 
              truncat(i.description) as description,
              ins.description as status, sq.amount
              from cm_incident i, cm_incident_status ins, 
              (select i.incident_id, sum(i.amount_value) as amount 
               from cm_item i, cm_item_status its
               where i.status_id = its.status_id
               and its.description = 'lost'
               group by i.incident_id) sq
              where sq.incident_id = i.incident_id
              and i.date_ between %s and %s
              and i.status_id = ins.status_id 
              order by %s %s
              limit 10;
              """ % ('%s', '%s', by_sql, order_sql)
        return self._query(sql, kw['start_date'], kw['end_date'])
