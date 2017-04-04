from cm.model import CMObjectBase


class StoreManager(CMObjectBase):
    def get(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'store_id':
            by_sql = 'store_id'
        elif by =='location':
            by_sql = 'location'
        else:
            by_sql = 'store_id'
           
        sql = """select store_id, location from cm_store order by %s %s;
              """ % (by_sql, order_sql)
        return self._query(sql)
    

class Store(CMObjectBase):
    def _set_defaults(self, kw):
        kw = CMObjectBase._set_defaults(self, kw)
        kw['security'] = kw.get('security', '')
        kw['key_holder_access'] = kw.get('key_holder_access', '')
        kw['protection_system'] = kw.get('protection_system', '')
        return kw
        
    def new(self, kw):
        kw = self._set_defaults(kw)
        kw['obj_type'] = 'store'
        
        sql = """insert into cm_store(obj_type_id, owner, store_id,
              location, security, key_holder_access, protection_system)
              select ot.obj_type_id, %(owner)s, %(store_id)s,
              %(location)s, %(security)s, %(key_holder_access)s, 
              %(protection_system)s
              from cm_obj_type ot
              where ot.description = %(obj_type)s;"""
        self._query(sql, kw)

    def set(self, kw):
        kw = self._set_defaults(kw)
        keys = kw.keys()
        f = [key + " = " + "%(" + key + ")s" for key in keys]
        sql = "update cm_store set " + " , ".join(f) \
              + " where store_id = %(store_id)s;"
        self._query(sql, kw)

    def delete(self, kw):
        sql = "delete from cm_store where store_id = %s;"
        self._query(sql, kw.get('store_id'))
        
        
    def get(self, kw):
        sql = """select obj_id, owner, store_id, location, 
              security, key_holder_access, protection_system
              from cm_store
              where store_id = %s;
              """
        return self._query(sql, kw.get('store_id'))

    def get_incidents(self, kw):
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

        sql = """select i.incident_id, 
              truncat(i.description) as description, 
              ins.description as status  
              from cm_incident i, cm_incident_status ins
              where i.store_id = %s
              and i.status_id = ins.status_id
              order by %s %s;
              """ % ('%s', by_sql, order_sql)
        return self._query(sql, kw.get('store_id'))

    
        
