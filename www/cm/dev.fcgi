#!/usr/bin/python2.2

from quixote import enable_ptl
from quixote.publish import SessionPublisher
from quixote.session import SessionManager
from cm.session import AKSession, PostgresMapping
from cm.i18n import enable_i18n

enable_ptl()
enable_i18n()
session_mgr = SessionManager(session_class=AKSession,
                             session_mapping=PostgresMapping())
pub = SessionPublisher('cm.html', session_mgr=session_mgr)
pub.read_config('dev_quixote.conf') # for dev
pub.setup_logs()
pub.publish_cgi()




