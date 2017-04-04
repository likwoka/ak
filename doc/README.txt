2003 08 20

Requirement (for running the system)
===========
-web server	... Apache
-RDMBS 		... Postgresql
-Python		... Python
-Python Lib	... Quixote
-Python Lib	... psycopg
-Python Lib	... mxtools (mxDateTime)
-Python Lib	... FixedPoint


Installation
============
For apache and Postgresql, please refer to  their respective
installation documents.
For Python Libs, simply use 'setup.py install'
For AK system, please see Directory Structure below.


Configuration
=============
-Apache: see /etc/apache/
-Postgresql: see /etc/postgresql
Mainly access control parameters
-Python: /etc/pythonX.X/site.py ... Basically sys.path entries
-AK system: see /ak/py/cm/config.py


Directory Structure
===================
Below is the recommended directory structure:

ak
    web   - contains all html and web resource files
    py    - contains the application code (python package)
    util  - contains tools/scripts for maintaining the application
    doc   - contains doc regarding this application
    data  - contains uploaded files, stored attachments, 
	    backend relational database instance
    log   - contains app server (Quixote) logs

Of course, in real life, akcm may just be one of the services
running on an existing machine (instead of a dedicated server),
so in that case you can:
1) put the content of web into any web root (ex: /var/www)
2) put the content of py into python's site-package 
(ex: /usr/local/lib/python2.2/site-packages)
3) put the content of doc into system's doc location  (ex: /usr/share/doc)   
4) put the content of util into system's script location (ex: /usr/local/bin)
5) put the content of db into system's database location (ex: /var/lib)


Currently:
ak == dev
web == akone.dyndns.org, which contains py
db == postgres

This should be fixed before release, because
1) client won't be name akone.dyndns.org
2) backend database can be any RDBMS, not neccessarily Postgresql
3) dev is too general, ak is the shorthand of the whole 
application 'framework'


File and Directory Permissions
==============================
1) web, py - need rx permissions for web-server (www-data)
2) log, data - need rwx permission for web-server (www-data)


Optimization
============
Optimization ideas:
- tune postgresql's parameter
- use pipe instead of tcp for database connection
(assumption: database is on the same machine as app server)
- tune apache's parameter
- don't use mod_rewrite (?)
- run python with optimzation flag on (-OO)
- compile all py/ptl files before hand (speed up the first
response of each file)
- use scgi instead of fcgi (currently Linux only; not on
Windows)
- upgrade from python2.2 to python2.3
- upgrade postgresql


Logging
=======
- quixote log: access.log, error.log, debug.log in log


Backup
======
Data backup:
- backup data using ex: tar, cpio
- backup db using database specific tools
- backup config files (in python)
- backup code


Upgrade
=======
TODO


