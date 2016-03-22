"""
Django settings for frontend project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import djcelery  # Django-Celery integration

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

djcelery.setup_loader()

#BROKER_URL = "amqp://frontend:frontend@192.168.1.10:5672//"
#CELERY_RESULT_BACKEND = "celery"
#CELERY SETTINGS
BROKER_URL='amqp://scapl:scapl@localhost:5672/vScapl'
CELERY_ACCEPT_CONTENT=['json']
CELERY_TASK_SERIALIZER='json'
CELERY_RESULT_SERIALIZER='json'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
#Enable the celery-haystack signal processor in the settings
#HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vm-ucdk*adk1$47^ri1!&8sp)ms%u^$26v)zhq6l$r@s_&ur%8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = (
    'bootstrap3',
    'django_admin_bootstrapped',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'smuggler',
    'adminsortable2',
    'bootstrap_themes',
    # TODO: Enable 'storages' for production version
    #    'storages',
    'frontend.apps.CeleryAppConfig',
    'frontend.apps.CommonAppConfig',
    'frontend.apps.ProfilesAppConfig',
    'frontend.apps.SchemeAppConfig',
    'frontend.apps.WizardAppConfig',
    #'celery_haystack',
    #'queued_search',
)

# Particular application customized authentication settings
COMMON_APP = 'common'
PROFILE_APP = 'profiles'
SCHEME_APP = 'scheme'
AUTH_ABSTRACT_USER_MODEL = '%s.GenericUser' % COMMON_APP
AUTH_USER_MODEL = '%s.ScaplUser' % PROFILE_APP
AUTH_ROLE_MODEL = '%s.ScaplRole' % PROFILE_APP
AUTH_ADMIN_MODEL = '%s.Administrator' % SCHEME_APP
SCHEME_SOURCE = 'apps.%s.views.get_scheme' % SCHEME_APP

# Backends for using the customized user model and for automatically creating a superuser
AUTHENTICATION_BACKENDS = (
    'frontend.backends.GenericUserBackend',
    'frontend.backends.SuperUserCreationBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'frontend.urls'

WSGI_APPLICATION = 'frontend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'scapl.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''},
    'celery': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'celery.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

"""copy the static files to the public accessible folder using manage.py

# --link    Create a symbolic link to each file instead of copying.
# --noinput Do NOT prompt the user for input of any kind.
#
python manage.py collectstatic -link --noinput
"""
# web accessible folder
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'static/').replace('\\', '/'),
    # location of application, should not be public web accessible
)
# URL prefix for static files.
# STATIC_URL = os.path.join(os.path.dirname(__file__),os.pardir,os.pardir,os.pardir, 'static/').replace('\\', '/')
STATIC_URL = '/static/'
# web accessible folder
STATIC_ROOT = '/var/www/scapl-frontend/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# For handling automatic admin creation
ADMIN_EMAIL = 'admin@localhost'
ADMIN_PASSWORD = u'bcrypt_sha256$$2a$12$Gt54zH8Vta8mft0m4QRuzO0o6aqGlt298/NF6q3qF41HBGH/9ypBe'  # admin

# For managing passowrd hashing algorithm
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',

]

# TODO: Enable for production version
# Password validation
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#         'OPTIONS': {'min_length': 8,}
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# customized context processing
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'templates').replace('\\', '/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.static',
                'django.core.context_processors.request',
            ],
            'libraries': {
                'common_tags': 'apps.common.tags',
            },
        },
    },
]

# Set to False because of incompatibility with adminsortable (normally, no longer required with adminsortable2
# CSRF_COOKIE_HTTPONLY = False

# Specific SCAPL config
DI_ID_DIGITS = 5
DL_ID_DIGITS = 3
DS_ID_DIGITS = 2
RL_ID_DIGITS = 2

# TODO: Enable FTP for production version
# File storage (for APL packages)
MEDIA_ROOT = MEDIA_URL = '/packages/'
# DEFAULT_FILE_STORAGE = 'storages.backends.ftp.FTPStorage'

# TODO: Enable Memcache for production version
# Cache management
# https://docs.djangoproject.com/en/1.9/topics/cache/#memcached
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
#         'LOCATION': '/tmp/memcached.sock',
#     }
# }

# Smuggler configuration
SMUGGLER_FIXTURE_DIR = '/data/'
# SMUGGLER_EXCLUDE_LIST = []

getText = lambda x: x
LANGUAGES = (
    ('en', getText('EN')),
    ('fr', getText('FR')),
    ('nl', getText('NL')),
)
