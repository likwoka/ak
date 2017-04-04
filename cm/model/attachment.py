from cm.model import CMObjectBase
from cm import datetime, filetype
from cm.config import ATTACHMENT_DIR
from quixote import upload
import os, stat, glob


class AttachmentManager(CMObjectBase):
    def get(self, kw):
        order_sql = self._get_sort_order(kw)
        
        by = kw.get('sort_by')
        if by == 'filename':
            by_sql = 'filename'
        elif by == 'filetype':
            by_sql = 'filetype'
        elif by == 'description':
            by_sql = 'description'
        elif by == 'size':
            by_sql = 'size_'
        elif by == 'date':
            by_sql = 'datetime'
        else:
            by_sql = 'filename'
            
        sql = """select attachment_id, filename, filetype, 
              truncat(description) as description, size_ as size, 
              to_char(modify_datetime, '%s') as datetime 
              from cm_attachment 
              order by %s %s;
              """ % (datetime.PG_DATETIME_FMT, by_sql, order_sql)
        return self._query(sql)

    def get_by_case(self, kw):
        order_sql = self._get_sort_order(kw)
        
        by = kw.get('sort_by')
        if by == 'filename':
            by_sql = 'filename'
        elif by == 'filetype':
            by_sql = 'filetype'
        elif by == 'description':
            by_sql = 'description'
        elif by == 'size':
            by_sql = 'size_'
        elif by == 'date':
            by_sql = 'datetime'
        else:
            by_sql = 'filename'
            
        sql = """select a.attachment_id, a.filename, a.filetype, 
              truncat(a.description) as description, 
              a.size_ as size, 
              to_char(modify_datetime, '%s') as datetime
              from cm_attachment a, cm_case_attachment ia
              where ia.case_id = %s
              and ia.attachment_id = a.attachment_id
              order by %s %s;
              """ % (datetime.PG_DATETIME_FMT, '%s', by_sql, order_sql)
        return self._query(sql, kw.get('case_id'))

    def get_by_incident(self, kw):
        order_sql = self._get_sort_order(kw)
        
        by = kw.get('sort_by')
        if by == 'filename':
            by_sql = 'filename'
        elif by == 'filetype':
            by_sql = 'filetype'
        elif by == 'description':
            by_sql = 'description'
        elif by == 'size':
            by_sql = 'size_'
        elif by == 'date':
            by_sql = 'datetime'
        else:
            by_sql = 'filename'
            
        sql = """select a.attachment_id, a.filename, a.filetype, 
              truncat(a.description) as description, 
              a.size_ as size, 
              to_char(modify_datetime, '%s') as datetime
              from cm_attachment a, cm_incident_attachment ia
              where ia.incident_id = %s
              and ia.attachment_id = a.attachment_id
              order by %s %s;
              """ % (datetime.PG_DATETIME_FMT, '%s', by_sql, order_sql)
        return self._query(sql, kw.get('incident_id'))
        

class Attachment(CMObjectBase):
    seq_name = 'cm_attachment_id'

    def has_uploaded(self, upload):
        size = os.stat(upload.tmp_filename)[stat.ST_SIZE]
        if not upload.base_filename or size == 0:
            return False
        return True

    def _set_defaults(self, kw):
        kw = CMObjectBase._set_defaults(self, kw)
        try:
            if 'description' in kw.keys():
                kw['description'] = kw.get('description', '')
        except KeyError:
            pass
        return kw
        
    def new(self, kw):
        kw2 = self._file_system_create(kw['attachment_id'], kw['upload'])
        kw.update(kw2)
        kw = self._set_defaults(kw)
        kw['obj_type'] = 'attachment'
        kw['datetime'] = datetime.now()
    
        sql = """insert into cm_attachment(obj_type_id, owner, attachment_id,
                 filename, filetype, description, size_, create_datetime,
                 modify_datetime)
                 select ot.obj_type_id, %(owner)s, %(attachment_id)s,
                 %(filename)s, %(filetype)s, %(description)s, 
                 %(size)s, %(datetime)s, %(datetime)s
                 from cm_obj_type ot
                 where ot.description = %(obj_type)s;"""
        self._query(sql, kw)

    def _file_system_create(self, attachment_id, upload):
        dir_name = os.path.join(ATTACHMENT_DIR, str(attachment_id))
        os.mkdir(dir_name)
        final_name = os.path.join(dir_name, upload.base_filename)
        os.rename(upload.tmp_filename, final_name) 
        
        kw = {}
        # file size in kB, min 1
        kw['size'] = os.stat(final_name)[stat.ST_SIZE]/1000 or 1
        kw['filename'] = upload.base_filename
        kw['filetype'] = filetype.guess_file_type(final_name)
        return kw

    def set(self, kw):
        if 'upload' in kw and isinstance(kw['upload'], upload.Upload):
            kw2 = self._file_system_replace(kw['attachment_id'], kw['upload'])
            kw.update(kw2)
            del kw['upload']
        kw = self._set_defaults(kw)
        
        keys = kw.keys()
        f = [str(key) + " = " + "%(" + str(key) + ")s" for key in keys]
        sql = "update cm_attachment set " + ", ".join(f) \
              + " where attachment_id = %(attachment_id)s;"
        self._query(sql, kw)

    def _file_system_replace(self, attachment_id, upload):
        dir_name = os.path.join(ATTACHMENT_DIR, str(attachment_id))
        
        #rm the old file first!!!
        rs = self.get({'attachment_id':attachment_id})
        for r in rs:
            old_file = r.filename
        old_file = os.path.join(dir_name, old_file)
        os.remove(old_file)
        
        #mv the new file to the final location
        final_name = os.path.join(dir_name, upload.base_filename)
        os.rename(upload.tmp_filename, final_name)         
        
        kw = {}
        #file size in kB, minimum 1kB
        kw['size_'] = os.stat(final_name)[stat.ST_SIZE]/1000 or 1 
        kw['filename'] = upload.base_filename
        kw['filetype'] = filetype.guess_file_type(final_name)
        return kw    
        
    def delete(self, kw):
        # delete the physical file first, then update database
        _id = kw.get('attachment_id')
        self._file_system_delete(_id)
        sql = """delete from cm_incident_attachment 
              where attachment_id = %(_id)s;
              delete from cm_case_attachment where attachment_id = %(_id)s;
              delete from cm_attachment where attachment_id = %(_id)s;
              """
        self._query(sql, vars())
       
    def _file_system_delete(self, attachment_id):
        path = os.path.join(ATTACHMENT_DIR, str(attachment_id))
        allfiles = os.path.join(path, '*')
        for f in glob.glob(allfiles):
            os.remove(f)
        os.rmdir(path)
        
    def get(self, kw):
        sql = """select obj_id, owner, 
              to_char(modify_datetime, '%s') as datetime, 
              attachment_id, filename, filetype, description, size_ as size
              from cm_attachment
              where attachment_id = %s;
              """ % (datetime.PG_DATETIME_FMT, '%s')
        return self._query(sql, kw.get('attachment_id'))

    def get_incidents(self, kw):
        from cm.model.incident import IncidentManager
        return IncidentManager().get_by_attachment(kw)
    
    def get_cases(self, kw):
        from cm.model.case import CaseManager
        return CaseManager().get_by_attachment(kw)
        
    def attach_to_case(self, kw):
        sql = """insert into cm_case_attachment(attachment_id, case_id)
              values(%(attachment_id)s, %(case_id)s)
              """
        self._query(sql, kw)

    def attach_to_incident(self, kw):
        sql = """insert into cm_incident_attachment(attachment_id, incident_id)
              values(%(attachment_id)s, %(incident_id)s)
              """
        self._query(sql, kw)

    def detach_from_case(self, kw):
        sql = """delete from cm_case_attachment
              where attachment_id = %(attachment_id)s
              and case_id = %(case_id)s;
              """
        self._query(sql, kw)

    def detach_from_incident(self, kw):
        sql = """delete from cm_incident_attachment
              where attachment_id = %(attachment_id)s
              and incident_id = %(incident_id)s;
              """
        self._query(sql, kw)

       
