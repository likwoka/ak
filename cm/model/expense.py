from cm.model import CMObjectBase


class ExpenseManager(CMObjectBase):
    def get(self, kw):
        order_sql = self._get_sort_order(kw)
        
        by = kw.get('sort_by')
        if by == 'description':
            by_sql = 'description'
        elif by == 'amount':
            by_sql = 'amount'
        else:
            by_sql = 'expense_id'

        sql = """select expense_id, 
              truncat(description) as description, amount
              from cm_expense
              where case_id = %s
              order by %s %s;
              """ % ('%s', by_sql, order_sql)
        return self._query(sql, kw.get('case_id'))


class Expense(CMObjectBase):
    seq_name = 'cm_expense_id'
    
    def new(self, kw):
        kw['obj_type'] = 'expense'
        
        sql = """insert into cm_expense(obj_type_id, owner, create_datetime,
              modify_datetime, expense_id, case_id, description, amount)
              select ot.obj_type_id, %(owner)s, %(datetime)s, %(datetime)s,
              %(expense_id)s, %(case_id)s, %(description)s, %(amount)s
              from cm_obj_type ot
              where ot.description = %(obj_type)s;
              """
        self._query(sql, kw)

    def set(self, kw):
        keys = kw.keys()
        f = [key + " = " + "%(" + key + ")s" for key in keys]
        
        sql = "update cm_expense set " + " , ".join(f) \
              + " where expense_id = %(expense_id)s;"
        self._query(sql, kw)
 
    def delete(self, kw):
        sql = "delete from cm_expense where expense_id = %s;"
        self._query(sql, kw.get('expense_id'))

    def get(self, kw):
        sql = """select obj_id, owner, expense_id,
              case_id, description, amount
              from cm_expense
              where expense_id = %s;
              """
        return self._query(sql, kw.get('expense_id'))


