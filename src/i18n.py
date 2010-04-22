import os, sys
import locale
import gettext

APP_NAME = "mussorgsky"

APP_DIR = os.path.join (sys.prefix,
                        'share')

LOCALE_DIR = os.path.join(APP_DIR, 'locale')

DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
DEFAULT_LANGUAGES += ['en_US']

# Init i18n stuff
lc, encoding = locale.getdefaultlocale()

if lc:
    languages = [lc]

# DEBUG: to test translation without installation
#languages = ["es_ES"]
#mo_location = os.path.realpath(os.path.dirname(sys.argv[1]))
#print languages

languages += DEFAULT_LANGUAGES
mo_location = LOCALE_DIR

#print "Loading translations from: ", mo_location

gettext.install (True)
gettext.bindtextdomain (APP_NAME,
                        mo_location)
gettext.textdomain (APP_NAME)
language = gettext.translation (APP_NAME,
                                mo_location,
                                languages = languages,
                                fallback = True)
