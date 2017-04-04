# Most likely to be changed...
APP_ROOT = '/cm/' 
RES_ROOT = '/resource/' 
GRAPH_ROOT = '/cm/graph/' #This correspond to code in cm.html.__init__.py
ATTACHMENT_DIR = '/home/staging/ak/data/attachment/'
GRAPH_DIR = '/home/staging/ak/data/graph'   
IL_LANG_DIR = '/home/staging/ak/i18n/'

#For timing out sessions (only for SessionReaper)
REAP_SESSIONS_EVERY = 1800.0 # 30 mins

SESSION_TIMEOUT = 14400.0 # 4 hours
IS_COOKIE_SSL_ONLY = 0

COOKIE_PATH = APP_ROOT
LOGIN_URL = '%slogin' % APP_ROOT

GRAPH_EXPIRY = 48 # hrs
REAP_GRAPHS_EVERY = 24 # hrs

WEBPAGE_TITLE = 'AKONE'
WEBPAGE_CHARSET = 'iso-8859-1'
LOGO = '<p class="logotext">DEMO</p>'

# Language of IL (I18n/L10n)
IL_LANGS = {'en': ('en', 'English', 'iso-8859-1'),
            'fr': ('fr', 'francais', 'iso-8859-1')}
IL_DEFAULT_LANG = 'en' # default will be used if user's 
                       # language setting is not valid

# 1.For display  2.python's mxDateTime format  3.Postregresql format
DATE_FORMAT = ('YYYY-MM-DD', '%Y-%m-%d', 'YYYY-MM-DD')
TIME_FORMAT = ('HH:MM', '%H:%M', 'HH24:MM')
DATETIME_FORMAT = ('YYYY-MM-DD HH:MM', '%Y-%m-%d %H:%M', 'YYYY-MM-DD HH24:MI')

# case management - cm module
CM_DB_HOST = "localhost"
CM_DB_DATABASE = "akcm_sampleclient"
CM_DB_USER = "akadmin"
CM_DB_PASSWORD = "testaccount"
CM_DB_MAXCONN = 10
CM_DB_MINCONN = 5

# feedback - fb module
FB_DB_HOST = "localhost"
FB_DB_DATABASE = "akcm_sampleclient"
FB_DB_USER = "akadmin"
FB_DB_PASSWORD = "testaccount"
FB_FEEDBACK_URL = '%sfeedback/create' % APP_ROOT
FB_DB_MAXCONN = 5
FB_DB_MINCONN = 5

# user management - usr module
USR_DB_HOST = 'localhost'
USR_DB_DATABASE = 'akcm_sampleclient'
USR_DB_USER = 'akadmin'
USR_DB_PASSWORD = 'testaccount'
USR_DB_MAXCONN = 10
USR_DB_MINCONN = 5

# session management - ses module
SES_DB_HOST = 'localhost'
SES_DB_DATABASE = 'akcm_sampleclient'
SES_DB_USER = 'akadmin'
SES_DB_PASSWORD = 'testaccount'
SES_DB_MAXCONN = 10
SES_DB_MINCONN = 5


