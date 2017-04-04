'''
The I18N/gettext support.  Use gettext extensively.

Usage:
    from cm.i18n import enable_i18n
    enable_i18n() # install the function _ 
                  # and N_ into the builtin namespace
    ...
    print _("Some text that can be translated")

Note:
1) To enable re-ordering of inserted texts in formatting strings
(which can easily happen if a sentence has to be re-ordered due to
grammatical changes), translatable formats should use named format specs:

    ... _('Index of %(classname)s') % {'classname': cn} ...

Also, this eases the job of translators since they have some context what
the dynamic portion of a message really means.

2) This module is meant to use with an app server that has request
handler in the model of serialized request per app server process
(NOT THREAD SAFE)
'''
from quixote.publish import get_session
from cm import config
import gettext


_trans = None

def enable_i18n():
    '''Enable the i18n translation module.  More specifically,
    calling this function will load(reload) all message catalogs.
    '''
    langs = config.IL_LANGS
    lang_dir = config.IL_LANG_DIR
    global _trans
    _trans = {}
    for lang in langs.items():
        try:
            _trans[lang[0]] = gettext.translation('akcm', 
                                                  localedir=lang_dir,
                                                  languages=[lang[0]])
        except:
            _trans[lang[0]] = gettext.NullTranslations()
    # Install default language, we will install the default language
    # again when handling a session without lang attribute in a http
    # request.
    _trans[config.IL_DEFAULT_LANG].install()


class LanguageManager:
    '''Use me to get a list of available languages,
    their codes and names, for example, for the 
    user preference UI.
    '''
    def __init__(self):
        self._dict = config.IL_LANGS
        self._list = self._dict.values()

    def get(self, lang_code):
        lang = self._dict.get(lang_code, None)
        return lang

    def get_all(self):
        return self._list

    def get_codes(self):
        return list(zip(*self._list)[0])

    def get_names(self):
        return list(zip(*self._list)[1])

    def get_encodings(self):
        return list(zip(*self._list)[2])

        
class Language:
    '''I represent a language available to the system.'''
    def __init__(self, lang_code=None):
        '''
        lang_code - 2 letter lowercase language code, use default if
                    not given.
        '''
        if lang_code is None:
            # use the default language; called when
            # no session is found, or when a session is
            # first created.
            lang_code = config.IL_DEFAULT_LANG
        langseq = LanguageManager().get(lang_code)
        self.code = lang_code
        self.name = langseq[1]
        self.encoding = langseq[2]


class LangInstance(Language):
    '''I am a Language Instance hold by a user Session.
    I represent the user's language preference.  The 
    diference between me and Language is that I can be
    installed into a user's session..
    '''  
    def install(self, unicode=0):
        '''Install this language, as indicated by 
        the user's preference, in handling the 
        current http request.
        
        unicode - the Message Id (key) is in unicode.'''
        global _trans
        _trans[self.code].install()


