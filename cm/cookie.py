from cm import config, error


class Cookie:
    '''I represent a HTTP cookie.  Subclass me by setting the
    class variable name, path, domain, secure, expire.
    '''
    name = None
    path = None
    domain = None
    secure = None
    expire_datetime = None

    def __init__(self):
        if self.name is None:
            raise AssertionError('Cookie has no name.  It needs a name.')
        
    def get(self, request):
        return request.get_cookie(self.name)

    def set(self, request, username):
        request.response.set_cookie(self.name, username,
                                    expire=self.expire_datetime,
                                    path=self.path,
                                    domain=self.domain,
                                    secure=self.secure)        

    def expire(self, request):
        request.response.expire_cookie(self.name, path=self.path)


class UserNameCookie(Cookie):
    """I represent the "username" cookie sent to 
    the users web client after the user has logged in.
    """
    name = 'username'
    path = config.COOKIE_PATH
    domain = None
    secure = config.IS_COOKIE_SSL_ONLY
    expire_datetime = None

