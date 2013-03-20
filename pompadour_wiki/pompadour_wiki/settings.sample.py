# Django settings for pompadour_wiki project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import os
ROOT = os.getcwd()

ADMINS = (
    # ('Manager Name', 'Manager Email'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': '',       # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',         # Or path to database file if using sqlite3.
        'USER': '',         # Not used with sqlite3.
        'PASSWORD': '',     # Not used with sqlite3.
        'HOST': '',         # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',         # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr'

gettext = lambda s: s

LANGUAGES = (
    ('fr', gettext('French')),
    ('en', gettext('English')),
)

LOCALE_PATHS = (
    os.path.join(ROOT, 'locale'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT, 'media', 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'dajaxice.finders.DajaxiceFinder',
)

# Secret Key

try:
    from secret_key import SECRET_KEY

except ImportError:
    SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))
    generate_secret_key(os.path.join(SETTINGS_DIR, 'secret_key.py'))

    from secret_key import SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
     'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'pompadour_wiki.apps.utils.context_processors.pompadour',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'pompadour_wiki.apps.utils.middleware.UnsetAcceptLanguageHeaderMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'pompadour_wiki.apps.auth.backends.GoogleBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/accounts/logout/'

OPENID_SSO_SERVER_URL = 'https://www.google.com/accounts/o8/id'

from pompadour_wiki.views import login_failed
OPENID_RENDER_FAILURE = login_failed

WIKI_GIT_DIR = os.path.join(ROOT, 'gitwikis')   # Directory where wiki git repository is located
WIKI_INDEX = 'Home'                             # Index page, set it to None if you want to see all folder's pages

GOOGLE_ACCEPT_ALL = True                        # Accept all domains ?
# List of accepted Google App domain
GOOGLE_APP = (
    'example.com',
)

EMAIL_NOTIFY = True                         # Notify wikis updates via E-Mail ?
EMAIL_HOST = 'smtp.example.com'             # Hostname of the SMTP server
EMAIL_PORT = 25                             # Port of the SMTP server
EMAIL_HOST_USER = 'noreply@example.com'     # SMTP user
EMAIL_HOST_PASSWORD = 'noreply'             # Password for SMTP user

MARKITUP_FILTER = ('markdown.markdown', {
    'safe_mode': False,
    'extensions': ['meta', 'codehilite', 'toc'],
})

DAJAXICE_MEDIA_PREFIX = "dajaxice"
DAJAXICE_JSON2_JS_IMPORT = False

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'pompadour_wiki.wsgi.application'

PROJECT_APPS = (
    'django_openid_auth',
    'pompadour_wiki.apps.wiki',
    'pompadour_wiki.apps.tagging',
    'pompadour_wiki.apps.lock',
    'pompadour_wiki.apps.filemanager',
    'pompadour_wiki.apps.utils',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.markup',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.humanize',
    'dajaxice',
    'dajax',
) + PROJECT_APPS

ROOT_URLCONF = 'pompadour_wiki.urls'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'pompadour_cache',
    }
}