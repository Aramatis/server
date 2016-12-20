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
    # 'cbwz-*ri$u=_v@xa5m(3)qujt8yur&id*j%ps3src9^l+doxx4'

# Google key to ask for google services
with open(os.path.join(os.path.dirname(__file__), 'keys/google_key.json')) as file:
    GOOGLE_KEY = json.load(file)['key']

# Define the user will receive email when server has an error
with open(os.path.join(os.path.dirname(__file__), 'keys/admins.json')) as file:
    adminsJson = json.load(file)['admins']
    # print jsonAdmins
    ADMINS = []
    for user in adminsJson:
        admin = (user['name'], user['email'])
        ADMINS.append(admin)

# Set email configuration to report errors
with open(os.path.join(os.path.dirname(__file__), 'keys/email_config.json')) as file:
    emailConfigJson = json.load(file)
    EMAIL_HOST = emailConfigJson["EMAIL_HOST"]
    EMAIL_PORT = emailConfigJson["EMAIL_PORT"]
    EMAIL_USE_TSL = emailConfigJson["EMAIL_USE_TLS"]

    EMAIL_HOST_USER = emailConfigJson["EMAIL_HOST_USER"]
    EMAIL_HOST_PASSWORD = emailConfigJson["EMAIL_HOST_PASSWORD"]
    SERVER_EMAIL = emailConfigJson["SERVER_EMAIL"]

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

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
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'filters': ['ignore_silk', 'ignore_devicepositionintime'],
            'class': 'logging.FileHandler',
            'filename': os.path.dirname(__file__) + "/logs/file.log",
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'AndroidRequests': {
            'handlers': ['file', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'routeplanner': {
            'handlers': ['file', 'mail_admins'],
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
        # Empty for localhost through domain sockets or           '127.0.0.1'
        # for localhost through TCP.
        'HOST': 'localhost',
        'PORT': '',
    }
    # for development purpuse use SQLite
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es-CL'

TIME_ZONE = 'Chile/Continental'  # -3
# TIME_ZONE = 'Cuba' # -4

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
    # the job is executed every day at 24
    ('0 0 * * *', 'AndroidRequests.cronTasks.clearEventsThatHaveBeenDecline'),

    # every 2 minutes
    ('*/2 * * * *', 'AndroidRequests.cronTasks.cleanActiveTokenTable'),
]
CRONTAB_LOCK_JOBS = True
CRONTAB_COMMAND_SUFFIX = '2>&1'

MODELSDOC_APPS = ('AndroidRequests',)

# secure proxy SSL header and secure cookies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = False

# session expire at browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# wsgi scheme
os.environ['wsgi.url_scheme'] = 'https'


## load AndroidRequestsBackups settings
from server.keys.android_requests_backups import ANDROID_REQUESTS_BACKUPS
from server.keys.android_requests_backups import android_requests_backups_update_jobs
CRONJOBS = android_requests_backups_update_jobs(CRONJOBS)
