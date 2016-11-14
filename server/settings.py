"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open(os.path.join(os.path.dirname(__file__), 'keys/secret_key.txt')) as file:
    SECRET_KEY = file.read().strip()
    #'cbwz-*ri$u=_v@xa5m(3)qujt8yur&id*j%ps3src9^l+doxx4'

# Google key to ask for google services
with open(os.path.join(os.path.dirname(__file__), 'keys/google_key.json')) as file:
    GOOGLE_KEY = json.load(file)['key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

"""
'54.94.231.101' => public prod server ip
'200.9.100.91'  => public dev server ip
'172.17.77.240' => private dev server ip
"""
ALLOWED_HOSTS = ['54.94.231.101', '200.9.100.91', '172.17.77.240']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'AndroidRequests',
    'MapLocationOfUsers',
    'modelsdoc',
    'DataDictionary',
    'PredictorDTPM',
    'routeplanner',
    'AndroidRequestsBackups',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'

# Logging
def ignore_silk(record):
    """ return False if exist the word silk in the message """
    if "silk" in record.getMessage():
        return False
    return True

def ignore_devicepositionintime(record):
    """ return False if exist the word devicepositionintime in the message """
    if "devicepositionintime" in record.getMessage():
        return False
    return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'filters': {
        'ignore_silk': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': ignore_silk,
        },
        'ignore_devicepositionintime': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': ignore_devicepositionintime,
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'filters': [ 'ignore_silk', 'ignore_devicepositionintime' ],
            'class': 'logging.FileHandler',
            'filename': os.path.dirname(__file__) + "/logs/file.log",
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'AndroidRequests': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'routeplanner': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases


DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': 'ghostinspector',
       'USER': 'inspector',
       'PASSWORD': '1ghost2inspector',
       'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
       'PORT': '',
    }
    # for development purpuse use SQLite
    #'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #}
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es-CL'

TIME_ZONE = 'Chile/Continental' # -3
#TIME_ZONE = 'Cuba' # -4

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
MEDIA_IMAGE = os.path.join(MEDIA_ROOT, "reported_images/")


# cron settings
CRONJOBS = [
    #the job is executed every day at 24
    ('0 0 * * *', 'AndroidRequests.cronTasks.clearEventsThatHaveBeenDecline'),

    # every 2 minutes
    ('*/2 * * * *', 'AndroidRequests.cronTasks.cleanActiveTokenTable'),
    

    ## Android Requests Backups schedule
    # daily complete backup at 3:30am
    # ('*/5 * * * *', 'AndroidRequestsBackups.jobs.complete_dump',  '> /tmp/vizbkpapp_complete_dump_log.txt'),
    ('30  3 * * *', 'AndroidRequestsBackups.jobs.complete_dump', '> /tmp/vizbkpapp_complete_dump_log.txt'),
    
    # partial backups every 5 minutes
    ('*/5 * * * *', 'AndroidRequestsBackups.jobs.partial_dump',  '> /tmp/vizbkpapp_partial_dump_log.txt'),

    # USE THIS ONLY FOR TESTING ON TRANSAPP HEADQUARTERS
    # check for complete updates every 5 minutes
    # ('*/5 * * * *', 'AndroidRequestsBackups.jobs.complete_loaddata', '> /tmp/vizbkpapp_complete_loaddata_log.txt'),
    
    # check for partial updates every 2 minutes
    # '*/1 * * * *', 'AndroidRequestsBackups.jobs.partial_loaddata',  '> /tmp/vizbkpapp_partial_loaddata_log.txt'),
]
CRONTAB_LOCK_JOBS = True


MODELSDOC_APPS = ('AndroidRequests',)

# secure proxy SSL header and secure cookies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = False

# session expire at browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# wsgi scheme
os.environ['wsgi.url_scheme'] = 'https'



## ----------------------------------------------------------------------------
## VIZ_BACKUP_APP
## see also: AndroidRequestsBackups/REAME.md

# from where to lookup for images on host
VIZ_BKP_APP_IMGS_FLDR       = "media/reported_images"

# where to put backups on remote. (full path!)
# this folder will be created on the VIZ_BKP_APP_REMOTE_USER home
VIZ_BKP_APP_REMOTE_BKP_FLDR = "/home/transapp/bkps"

# database on host and remote must have the same name
VIZ_BKP_APP_HOST_DATABASE   = "ghostinspector"

# send updates for the last 5 minutes
VIZ_BKP_APP_TIME            = "5"

# where to store temporal bkp files on host
VIZ_BKP_APP_TMP_BKP_FLDR    = "/tmp/backup_viz"

# remote credentials
# - private key: used to access the remote
# - remote host: IP of the remote host
# - remote user: username for the remote host
VIZ_BKP_APP_PRIVATE_KEY     = "/home/server/.ssh/id_rsa"
VIZ_BKP_APP_REMOTE_HOST     = "104.236.183.105"
VIZ_BKP_APP_REMOTE_USER     = "transapp"

## (uncomment for testing)
# VIZ_BKP_APP_REMOTE_BKP_FLDR = "/home/mpavez/bkps"
# VIZ_BKP_APP_PRIVATE_KEY     = "/home/sebastian/.ssh/sebastian.id_rsa"
# VIZ_BKP_APP_REMOTE_HOST     = "172.17.57.17"
# VIZ_BKP_APP_REMOTE_USER     = "mpavez"

## ----------------------------------------------------------------------------
