from cm.model import CMObjectBase, CMStatusBase


class ItemManager(CMObjectBase):
    def get_by_incident(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'item_id':
            by_sql = 'i.item_id'
        elif by == 'description':
            by_sql = 'i.description'
        elif by == 'quantity':
            by_sql = 'i.quantity'
        elif by == 'amount_value':
            by_sql = 'i.amount_value'
        elif by == 'status':
            by_sql = 'its.description'
        else:
            by_sql = 'i.item_id'

        sql = """select i.item_id, truncat(i.description) as description,
                 i.quantity, 
                 i.amount_value, its.description as status
                 from cm_item i, cm_item_status its
                 where i.incident_id = %s
                 and i.status_id = its.status_id
                 order by %s %s;""" % ('%s', by_sql, order_sql)
        return self._query(sql, kw.get('incident_id'))


class Item(CMObjectBase):
    seq_name = 'cm_item_id'
    
    def _set_defaults(self, kw):
        kw = CMObjectBase._set_defaults(self, kw)
        kw['description'] = kw.get('description', '')
        return kw
    
    def new(self, kw):
        kw = self._set_defaults(kw)
        kw['obj_type'] = 'item'

        sql = """insert into cm_item(obj_type_id, owner, create_datetime,
              modify_datetime, item_id, incident_id, description, quantity,
              amount_value, status_id)
              select ot.obj_type_id, %(owner)s, %(datetime)s, %(datetime)s,
              %(item_id)s, %(incident_id)s, %(description)s, %(quantity)s,
              %(amount_value)s, its.status_id
              from cm_obj_type ot, cm_item_status its
              where ot.description = %(obj_type)s
              and its.description = %(status)s;
              """
        self._query(sql, kw)
        
    def delete(self, kw):
        sql = """
              delete from cm_item where item_id = %(item_id)s;
              """
        self._query(sql, kw)

    def set(self, kw):
        if 'status' in kw.keys():
            kw['status_id'] = ItemStatus().get_id(kw['status'])
            del kw['status'] 

        keys = kw.keys()
        f = [key + ' = ' + '%(' + key + ')s' for key in keys]
        sql = 'update cm_item set ' + ' , '.join(f) \
              + ' where item_id = %(item_id)s;'
        self._query(sql, kw)

    def get(self, kw):
        sql = """select i.obj_id, i.owner, i.item_id, i.incident_id,
              i.description, i.quantity, i.amount_value, 
              its.description as status
              from cm_item i, cm_item_status its
              where i.item_id = %s
              and i.status_id = its.status_id;
              """
        return self._query(sql, kw.get('item_id'))
            
              

status_singleton = None # is a resultsets 

class ItemStatus(CMStatusBase):
    def __init__(self):
        global status_singleton
        if status_singleton is None:
            sql = """select status_id, description 
                  from cm_item_status order by status_id asc;
                  """
            status_singleton = self._query(sql)
        self._data = status_singleton



