from cm.base import ObjectBase, StatusBase
from cm.db import Connection
from cm import config, error, cookie, i18n
import re, sha, time, binascii, urlparse


_password_generator = None

def get_password_generator():
    global _password_generator
    if _password_generator is None:
        _password_generator = PasswordGenerator()
    return _password_generator


class PasswordGenerator:
    '''Instance attributes:
    hash : any
    '''
    default_seed = 'iFfyAA3niLGN7ncn7vx2w' # some random secret data

    def __init__(self, seed=default_seed):
        self.hash = sha.new(seed)
        self.hash.update(str(time.time()))

    def generate(self, seed='', length=8):
        '''Generate a password.  Some effort is made to make it random.

        seed: if supplied the str() of this argument is used to update the
              generator state before generating the password.

        length: the maximum length of the password to return.
        '''
        try:
            # Try to use /dev/urandom.
            self.hash.update(open('/dev/urandom', 'rb').read(length))
        except IOError:
            # No source of random data.  This method will now only
            # generate passwords that look random if seed is kept secret.
            self.hash.update(str(time.time()))
        self.hash.update(str(seed))
        return binascii.b2a_base64(self.hash.digest())[:length]


def hash_password(password):
    '''Apply a one way hash function to a password 
    and return the result.
    '''
    return sha.new(password).hexdigest()


_conn = None

def open_connection(self):
    '''A mixin method for returning a globally single
    connection object.'''
    global _conn
    if _conn is None:
        _conn = Connection(config.USR_DB_DATABASE,
                           config.USR_DB_HOST,
                           config.USR_DB_USER,
                           config.USR_DB_PASSWORD,
                           config.USR_DB_MAXCONN,
                           config.USR_DB_MINCONN)
    return _conn


class UserManager(ObjectBase):
    _get_connection = open_connection
    
    def get(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'username':
            by_sql = 'username'
        elif by == 'name':
            by_sql = 'name'
        elif by == 'email':
            by_sql = 'email'
        elif by == 'role':
            by_sql = 'role'
        elif by == 'status':
            by_sql = 'status'
        elif by == 'description':
            by_sql = 'description'
        else:
            by_sql = 'username'
            
        sql = '''select u.username, u.name, u.email, u.description, 
              r.name as role, s.description as status
              from usr_user u, usr_role r, usr_user_status s
              where u.role_id = r.role_id
              and u.status_id = s.status_id
              order by %s %s;
              ''' % (by_sql, order_sql)
        return self._query(sql)


class User(ObjectBase):
    _get_connection = open_connection
    
    def new(self, kw):
        kw['status_id'] = UserStatus().get_id(kw['status'])
        kw['role_id'] = UserRole().get_id(kw['role'])
        
        sql = """insert into usr_user(username, name, email, 
              description, role_id, lang_code, status_id)
              values(%(username)s, %(name)s, %(email)s, 
              %(description)s, %(role_id)s, %(lang_code)s, 
              %(status_id)s);
              """
        self._query(sql, kw)

    def set(self, kw):
        if 'status' in kw.keys():
            kw['status_id'] = UserStatus().get_id(kw['status'])
            del kw['status']
        if 'role' in kw.keys():
            kw['role_id'] = UserRole().get_id(kw['role'])
            del kw['role']
        if 'password' in kw.keys():
            del kw['password'] # use set_password instead
            
        keys = kw.keys()
        f = [key + " = " + "%(" + key + ")s" for key in keys]
        sql = "update usr_user set " + " , ".join(f) \
              + " where username = %(username)s;"
        self._query(sql, kw)

    def set_password(self, kw):
        if kw['new_password1'] == kw['new_password2']:
            new_password = hash_password(kw['new_password1'])
            sql = """update usr_user set password = %s
                  where username = %s;
                  """
            self._query(sql, new_password, kw['username'])
        else:
            raise 'Your new password entries did not match.'
        
    def change_password(self, kw):
        if self.authenticate(kw['username'], kw['old_password']):
            self.set_password(kw['username'], 
                              kw['new_password1'], kw['new_password2'])
        else:
            raise 'Wrong password.'

    def delete(self, kw):
        sql = 'delete from usr_user where username = %(username)s;'
        self._query(sql, kw)

    def get(self, kw):
        sql = '''select u.username, u.name, u.email, u.description,
              r.name as role, u.lang_code, s.description as status
              from usr_user u, usr_user_status s, usr_role r
              where u.username = %s
              and u.role_id = r.role_id
              and u.status_id = s.status_id;
              '''
        return self._query(sql, kw.get('username'))

    def authenticate(self, username, password):
        '''Return True if the username and password match,
        otherwise return False.
        '''
        password = hash_password(password)
        status_id = UserStatus().get_id('active')
        sql = '''select r.username 
              from usr_user r
              where r.username = %(username)s
              and r.password = %(password)s
              and r.status_id = %(status_id)s;
              '''
        rs = self._query(sql, vars())

        for r in rs:
            if r.username == username: return True
        return False
    
    login = authenticate 

    def register(self, request, username):
        '''Register a user to the session manager.  This usually
        happens after the user has logged in/authenticated 
        successfully.

        2 HTTP cookies are issued when registering:
        cookie 1: contains the session_id assigned by the 
        server when user access a page
        that has stored things into it.
        It should expire at end of session (browser exit).
        
        cookie 2: named username, contains the username of the
        user who logs in (and successfully authenticate).  It
        should expire at end of session.
        '''
        # 2 sql queries in total, need optimization
        rs = self.get({'username':username})
        for r in rs:
            role_name = r.role
            lang_code = r.lang_code
        request.session.set_role(role_name)
        request.session.set_lang(lang_code)
        request.session.set_user(username)
        cookie.UserNameCookie().set(request, username)

    def is_logged_in(self, request):
        '''Return True if the user has logged in,
        return False otherwise.
        
        User has logged in if the username in
        the server-side session is the same as
        the username in the username cookie from
        the user.
        Therefore, we check:
        1) if the session_id provided by the user
        is correct (find a match on the server side)
        2) if that session id is not just a guess
        (make sure the username match)
        '''
        user = request.session.user
        if user is None:
            return False
        elif user == cookie.UserNameCookie().get(request):
            return True
        else:
            return False

    def logout(self, request):
        '''Remove/unregister the user session from the 
        session manager.  This usually happens when
        the user logout of the application.
        '''
        # remove the session on the server side
        from cm.session import get_session_manager
        get_session_manager().expire_session(request)
        # expire the cookie on the client side
        cookie.UserNameCookie().expire(request)


_user_status = None

class UserStatus(StatusBase):
    '''Contains valid user statuses (name and id) for user.'''
    _get_connection = open_connection

    def __init__(self):
        global _user_status
        if _user_status is None:
            sql = '''select status_id, description
                  from usr_user_status order by status_id asc;
                  '''
            _user_status = self._query(sql)
        self._data = _user_status 


_user_role = None

class UserRole(StatusBase):
    '''Contains valid user roles (name and id) for user.'''
    _get_connection = open_connection

    def __init__(self):
        global _user_role
        if _user_role is None:
            sql = '''select role_id, name
                  from usr_role order by role_id asc;
                  '''
            _user_role = self._query(sql)
        self._data = _user_role


class RoleManager(ObjectBase):
    _get_connection = open_connection

    def get(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'name':
            by_sql = 'name'
        elif by == 'description':
            by_sql = 'description'
        else:
            by_sql = 'name'
            
        sql = '''select r.role_id, r.name, r.description
              from usr_role r
              order by %s %s;
              ''' % (by_sql, order_sql)
        return self._query(sql)
    
    
class Role(ObjectBase):
    seq_name = 'usr_role_id'
    _get_connection = open_connection

    def new(self, kw):
        kw['role_id'] = self.get_id() 
        sql = '''insert into usr_role(role_id, name, description)
              values(%(role_id)s, %(name)s, %(description)s);
              '''
        self._query(sql, kw)
        
    def set(self, kw):
        if 'name' in kw:
            role_name = kw['name']
            del kw['name'] 
        
        keys = kw.keys()
        kw['role_name'] = role_name
        
        f = [key + ' = ' + '%(' + key + ')s' for key in keys]
        
        sql = 'update usr_role set ' + ' , '.join(f) \
              + ' where name = %(role_name)s;'
        self._query(sql, kw)
        
    def set_urls(self, kw):
        denylist = [(k,) for (k, v) in kw.iteritems() if v == 1]
        
        cursor = self._get_connection().get_cursor()
        try:
            sql = 'select role_id from usr_role where name = %s;'
            cursor.execute(sql, [kw.get('name')])
            role_id = cursor.fetchone()[0]
            
            sql = '''delete from usr_role_url
                  where role_id = %s;'''
            cursor.execute(sql, [role_id])
            
            sql = '''insert into usr_role_url(role_id, url_id, is_allow)
                  values (%s, %s, %s)
                  ''' % (role_id, '%s', 0)
            cursor.executemany(sql, denylist)
        except:
            cursor.rollback()
            raise
        cursor.commit()
    
    def delete(self, kw):
        cursor = self._get_connection().get_cursor()
        try: 
            sql = 'select role_id from usr_role where name = %s;'
            cursor.execute(sql, [kw.get('name')])
            role_id = cursor.fetchone()[0]
            
            sql = '''delete from usr_role_url
                  where role_id = %s;'''
            cursor.execute(sql, [role_id])
            
            sql = 'delete from usr_role where name = %s;'
            cursor.execute(sql, [kw.get('name')])
        except:
            cursor.rollback()
            raise
        cursor.commit()
        
    def get(self, kw):
        sql = '''select role_id, name, description
              from usr_role
              where name = %s;
              '''
        return self._query(sql, kw.get('name'))
        
    def get_urls(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'url_id':
            by_sql = 'url_id'
        elif by == 'url':
            by_sql = 'url'
        elif by == 'description':
            by_sql = 'description'
        elif by == 'deny':
            by_sql = 'deny %s, url' % order_sql
        else:
            by_sql = 'url_id'

        sql = '''select u.url_id, u.url, u.description, t.url_id as deny
              from usr_url u left outer join 
              (select u.url_id
               from usr_role r, usr_url u, usr_role_url ru
               where r.name = %s
               and r.role_id = ru.role_id
               and ru.url_id = u.url_id) t
              on u.url_id = t.url_id
              order by %s %s;
              ''' % ('%s', by_sql, order_sql)
        return self._query(sql, kw.get('name'))     

    def get_deny_urls(self, name):
        cursor = self._get_connection().get_cursor()
        sql = '''select u.url
              from usr_role r, usr_url u, usr_role_url ru
              where r.name = %s
              and r.role_id = ru.role_id
              and ru.url_id = u.url_id
              order by url asc;
              '''
        cursor.execute(sql, [name])
        # transform a list of tuple to a list of string
        return [item[0] for item in cursor.fetchall()] 


class RoleInstance:
    '''A class for providing an instance for the logged
    in users to store in their session.  Therefore we
    want it to be lightweight and contain as little code
    as possible (because we pickle the instance).
    '''
    def __init__(self, name):
        self.name = name
        self.deny_urls = Role().get_deny_urls(name)

    def check_access(self, url):
        '''Being called at the beginning of each page.'''
        if self.deny(url):
            raise error.AccessNotAllowedError

    def deny(self, url, base=None):
        '''Being called when rendering links.'''
        full = urlparse.urljoin(base, str(url))  
        url_com = urlparse.urlparse(full)[2].split('/')
        
        for durl in self.deny_urls:
            durl_com = durl.split('/')
            if len(url_com) == len(durl_com):
                if reduce(self._sum, map(self._same, url_com, durl_com)):
                    return True
        return False
    
    def _sum(self, x, y):
        return x and y
    
    def _same(self, com, dcom):
        if com == dcom or dcom == '_':
            return True
        return False


class UrlManager(ObjectBase):
    _get_connection = open_connection

    def get(self, kw):
        order_sql = self._get_sort_order(kw)

        by = kw.get('sort_by')
        if by == 'url_id':
            by_sql = 'url_id'
        elif by == 'url':
            by_sql = 'url'
        elif by == 'description':
            by_sql = 'description'
        else:
            by_sql = 'url'
            
        sql = '''select url_id, url, description
              from usr_url
              order by %s %s;
              ''' % (by_sql, order_sql)
        return self._query(sql)


class Url(ObjectBase):
    seq_name = 'usr_url_id'
    _get_connection = open_connection

    def new(self, kw):
        kw['url_id'] = self.get_id() 
        sql = '''insert into usr_url(url_id, url, description)
              values(%(url_id)s, %(url)s, %(description)s);
              '''
        self._query(sql, kw)
        
    def set(self, kw):
        if 'url' in kw:
            url_name = kw['url']
            del kw['url'] 
        
        keys = kw.keys()
        kw['url_name'] = role_name
        
        f = [key + ' = ' + '%(' + key + ')s' for key in keys]
        
        sql = 'update usr_url set ' + ' , '.join(f) \
              + ' where url = %(url_name)s;'
        self._query(sql, kw)
        
    def delete(self, kw): 
        cursor = self._get_connection().get_cursor()
        try:
            sql = 'select url_id from usr_url where url = %s;'
            cursor.execute(sql, [kw.get('url')])
            role_id = cursor.fetchone()[0]
            
            sql = '''delete from usr_role_url
                  where role_id = %s;'''
            cursor.execute(sql, [role_id])
            
            sql = 'delete from usr_url where url = %s;'
            cursor.execute(sql, [kw.get('url')])
        except:
            cursor.rollback()
            raise
        cursor.commit()
        
    def get(self, kw):
        sql = '''select url_id, url, description
              from usr_url
              where url = %s;
              '''
        return self._query(sql, kw.get('url'))


