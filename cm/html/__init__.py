from cm.html.aboutus import aboutus
from cm.html.home import home
from cm.html.login import login
from cm.html.logout import logout
from cm.html.help import help
from cm.html.admin import admin
from cm.html.search import search

from cm import config, error
from cm.user import User
from quixote.util import StaticDirectory

graph = StaticDirectory(config.GRAPH_DIR, use_cache=0)   

_q_exports = ["aboutus", "home", "login", "logout", "help",
              "case", "incident", "store", "attachment",
              "report", "feedback", "user", "admin", "mypreference",
              "role", "search", "graph"]


def _q_access(request):
    url = request.get_path()
    if url not in public_paths:
        if not User().is_logged_in(request):
            raise error.NotLoggedInError
        request.session.role.check_access(url)
        

def _q_index(request):
    return request.redirect("%shome" % config.APP_ROOT, permanent=1)
    

from cm.htmllib import base, Message
from cm.session import get_session_manager

public_paths = [config.LOGIN_URL, '%slogout' % config.APP_ROOT]

def _q_exception_handler(request, exc):
    global public_paths
    if isinstance(exc, error.NotLoggedInError):
        goto = make_goto(request)
        request.redirect(config.LOGIN_URL + goto)
    elif isinstance(exc, error.AccessNotAllowedError):
        return render_error(request, exc)
    elif isinstance(exc, error.SessionError):
        # revoke_session_cookie() is being called in
        # SessionError.format(), which will only be called
        # if the error is handled by the default
        # exception handler, not this one.
        m = get_session_manager()
        try:
            m.expire_session(request)   # Delete the session and cookie
                                        # This means 1 more sql, but can keep
                                        # session table from expanding quickly.
        except AttributeError:
            # when the request has no session, then
            # accessing request.session.id returns 
            # an attribute error (since None has no attributes)
            pass
        #m.revoke_session_cookie(request) # Delete the cookie only
        goto = make_goto(request)
        request.redirect(config.LOGIN_URL + goto)
    elif isinstance(exc, error.NotEnoughDataError):
        return render_error(request, exc)
    else: raise exc

def make_goto(request):
    url = request.get_url()
    qstr = request.get_environ('QUERY_STRING')
    if qstr != '': 
        qstr = '?' + qstr
    return '?goto=%s%s' % (url, qstr) 
    
def render_error(request, exc):
    m = Message()
    m.set_message(str(exc))
    return base.header(request)+m.render(request)+base.footer(request)

