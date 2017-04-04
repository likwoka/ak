'''
Copyright (c) Alex Li 2003.  All rights reserved.
'''

__version__ = '0.3'
__file__ = 'urlspider.py'


ROOT_NAMESPACE = 'cm.html'
APP_ROOT = '/cm'
IGNORE_NEW_URLS = ['/cm/login', '/cm/logout',
'/cm/attachment/download/', '/cm/test/', '/cm/test/en', '/cm/test/fr',
'/cm/test/session', '/cm/test/choose']
IGNORE_OLD_URLS = []


import os, getopt, sys, pprint, inspect, re
from quixote import enable_ptl
from types import *

from cm.user import Url, UrlManager


def _module_walk(namespace, cur_url, retval):
    '''
    namespace - a string representing the namespace
    cur_url - a string representing the current URL
    retval - a reference of a list containing the final URLs
    '''
    try:
        __import__(namespace)
    except ImportError:
        print 'E: Import Error when importing this module:', namespace
        return
    module = sys.modules[namespace]
    _class_instance_walk(module, cur_url, retval)


def _class_instance_walk(namespace, cur_url, retval):
    '''
    namespace - an instance (NOT A STRING) representing the namespace
    curl_url - a string representing the current URL
    retval - a reference of a list containing the final URLs
    '''
    _q_exports = getattr(namespace, '_q_exports', [])
    for name in _q_exports:
        
        instance = getattr(namespace, name, None)
        
        if isinstance(instance, NoneType):
            # Must be a url dir, so walk into it...
            _module_walk(_make_namespace(namespace.__name__, name), 
                         _make_url(cur_url, name), retval)
        elif isinstance(instance, FunctionType): 
            # Must be a leaf...
            _insert(_make_url(cur_url, name), retval)
        elif isinstance(instance, InstanceType):
            # Must be a url dir represented by 
            # a class instance, walk into it...
            _class_instance_walk(instance, _make_url(cur_url, name), retval)
        elif isinstance(instance, MethodType):
            # Must be a leaf...
            _insert(_make_url(cur_url, name), retval)
        elif isinstance(instance, ModuleType):
            _module_walk(instance.__name__, 
                         _make_url(cur_url, name), retval)
        else:
            print 'E: Unhandled namespace from ' \
                  '_class_instance_walk:', name, \
                  'type:', type(instance), \
                  'in the _q_exports at:', namespace

    if hasattr(namespace, '_q_index'):
        _insert(_make_url(cur_url, '/'), retval)

    if hasattr(namespace, '_q_lookup'):
        _q_lookup_walk(namespace._q_lookup, 
                       _make_url(cur_url, '_'), retval) 
        
        
def _q_lookup_walk(instance, cur_url, retval):
    '''
    instance - an instance of the function/method _q_lookup
    '''
    (lines, startat) = inspect.getsourcelines(instance.func_code)
    for line in lines:
        # If find the word 'return', get the 
        # thing in between return and (..)
        begin = 'return '
        end = '('
        begin_pos = line.find(begin)
        if begin_pos > 0: # this is a 'return' statement
            end_pos = line.find(end)
            if end_pos > 0: 
                # find a '(', this must be a class/function
                name = line[begin_pos+len(begin):end_pos].strip()
                _class_instance_walk(instance.func_globals.get(name), 
                                     cur_url, retval)
            else: 
                # no '(', probably a namespace...
                name = line[begin_pos+len(begin):].strip()
                _module_walk(name, cur_url, retval)
        
def _make_namespace(path1, path2):
    return '.'.join([path1, path2])

def _make_url(path1, path2):
    if path1[-1] == '/' and path2[0] == '/':
        return path1
    elif path1[-1] != '/' and path2[0] != '/':
        return path1 + '/' + path2
    elif path1[-1] == '/' or path2[0] == '/':
        return path1 + path2
    
def _insert(url, urllist):
    urllist.append(url)


class UrlSpider:
    def __init__(self, root_namespace, app_root, 
                 ignore_new=[], ignore_old=[]):
        self._urls_in_src = [] # we compare urls in src and db
        self._urls_in_db = []
        self._new_urls = [] # hold results of diff
        self._old_urls = [] # hold results of diff
        self._ign_new = ignore_new
        self._ign_old = ignore_old
        self._root_namespace = root_namespace
        self._app_root = app_root
        self._crawl()

    def _crawl(self):
        # 'crawl' the database for existing urls
        self._get_urls_in_db()
        list_db = self._urls_in_db
        
        # crawl the package code for new urls
        self._get_urls_in_src()
        list_src = self._urls_in_src
        
        # new urls are the ones in src but not in db
        dict_db = dict(zip(list_db, list_db))
        temp = [url for url in list_src if url not in dict_db]

        dign_new = dict(zip(self._ign_new, self._ign_new))
        self._new_urls = [url for url in temp if url not in dign_new]

        # old urls are the ones in db but not in src
        dict_src = dict(zip(list_src, list_src))
        temp = [url for url in list_db if url not in dict_src]

        dign_old = dict(zip(self._ign_old, self._ign_old))
        self._old_urls = [url for url in temp if url not in dign_old]
        
    def _get_urls_in_db(self):
        rs = UrlManager().get({'sort_by':'url'})
        for r in rs:
            self._urls_in_db.append(r.url)
        self._urls_in_db.sort()
       
    def _get_urls_in_src(self):
        urllist = []
        #side-effect on urllist
        _module_walk(self._root_namespace, self._app_root, urllist) 
        self._urls_in_src = urllist
        self._urls_in_src.sort()
                    
    def report(self):
        cnt_new = len(self._new_urls)
        cnt_old = len(self._old_urls)
        if cnt_new > 0:
            print 'There are %s new urls in the code.' % cnt_new
        else:
            print 'There are no new urls in the code.'

        if cnt_old > 0:
            print 'There are %s old urls in the database.' % cnt_old
        else:
            print 'There are no old urls in the database.'

        if cnt_new > 0:
            print '=' * 45
            print 'New URLs:'
            print pprint.pprint(self._new_urls)

        if cnt_old > 0:
            print '=' * 45
            print 'Old URLs:'
            print pprint.pprint(self._old_urls)
        
    def install_new_urls(self):
        url = Url()
        cnt = 0
        print 'Start installing new URLs...'
        for name in self._new_urls:
            url.new({'url':name, 'description':None})
            print 'Installed new URL:', name
            cnt += 1
        print '%s new URLs installed.' % cnt
        
    def remove_old_urls(self):
        url = Url()
        cnt = 0
        print 'Start removing old URLs...'
        for name in self._old_urls:
            url.delete({'url':name})
            print 'Removed old URL:', name
            cnt += 1
        print '%s old URLs deleted.' % cnt


class UsageError(Exception):
    def __init__(self, msg=''):
        self.msg = msg


usage = '''\nUsage: $python %(name)s [OPTION]

Crawl and maintain URLs stored in the table usr_url in the database.

Options:
    -r, --report            Report any new URLs in the source code but not
                            in the database, and any old urls in the 
                            database but not in the source code.
    -i, --install-new       Install all new URLs into the database.
    -d, --remove-old        Remove all old URLs and their role-url
                            relationships from the database.
    -h, --help              Display this message\n''' % {'name':__file__}


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hrid", ["help",
                                                          "report",
                                                          "install-new",
                                                          "remove-old"])
        except getopt.error, msg:
            raise UsageError(msg)

        if len(args) > 0:   # have arguments
            raise UsageError('E: Wrong number of argument.')

        if len(opts) == 0:  # empty... no options
            raise UsageError(usage)

        #LOGIC STARTS HERE       
        enable_ptl()
        
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                raise UsageError(usage)
            elif opt in ('-r', '--report'):
                UrlSpider(ROOT_NAMESPACE, APP_ROOT, 
                          IGNORE_NEW_URLS, IGNORE_OLD_URLS).report()
            elif opt in ('-i', '--install-new'):
                UrlSpider(ROOT_NAMESPACE, APP_ROOT,
                          IGNORE_NEW_URLS, IGNORE_OLD_URLS).install_new_urls()
            elif opt in ('-d', '--remove-old'):
                UrlSpider(ROOT_NAMESPACE, APP_ROOT,
                          IGNORE_NEW_URLS, IGNORE_OLD_URLS).remove_old_urls()

    except UsageError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, 'For help use --help.'
        return 2

    
if __name__ == '__main__':
    sys.exit(main())

