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

#Cron settings

CRONJOBS = [
    #the job is executed every day at 24
    ('0 0 * * *', 'AndroidRequests.cronTasks.clearEventsThatHaveBeenDecline'),
    ('*/2 * * * *', 'AndroidRequests.cronTasks.cleanActiveTokenTable')
]

MODELSDOC_APPS = ('AndroidRequests',)

# secure proxy SSL header and secure cookies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = False

# session expire at browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# wsgi scheme
os.environ['wsgi.url_scheme'] = 'https'

