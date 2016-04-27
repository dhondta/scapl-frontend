"""
Django settings for frontend project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.contrib import messages
from django.utils.text import slugify
from ..admin import ADMIN_REORDER

PROJECT_NAME = 'SCAPL'
PROJECT_AUTHORS = 'Alex & Hussein'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Celery settings
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
#BROKER_URL = 'amqp://scapl:scapl@localhost:5672/vScapl'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'amqp'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
ROUTING_KEYS = {
    'default': 'default',
    'search': 'se.task',
    'automation': 'as.task',
}
RESULT_REFRESH_DELAY = 300  # seconds
ASYNC_TASK_EXPIRATION = 10  # 24 * 3600

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# TODO: Dev key ; change it for production version
SECRET_KEY = 'vm-ucdk*adk1$47^ri1!&8sp)ms%u^$26v)zhq6l$r@s_&ur%8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
DENIED_HOSTS = []
SITE_ID = 1

# SCAPL application definition
SCAPL_INSTALLED_APPS = (
    'apps.common',
    'apps.profiles',
    'apps.scheme',
    'apps.wizard',
)

# Application definition
INSTALLED_APPS = (
    # style applications
    'bootstrap3',
    'bootstrap_themes',
    'django_admin_bootstrapped',
    # extra applications (core)
    'admin_reorder',
    'adminsortable2',
    'compressor',
    'django_libs',
    'django_summernote',
    'expirables',
    'form_utils',
    'overextends',
    'smuggler',
    # native applications
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # TODO: Enable 'storages' for production version
    #    'storages',
    #'celery_haystack',
    #'queued_search',
    # add-on applications (optional)
    'django_extensions',
    'simple_history',
    'admin_honeypot',
    # SCAPL project,
    'frontend',
) + SCAPL_INSTALLED_APPS
# Useful list of additional apps: https://github.com/rosarior/awesome-django#admin-interface
# TODO: convert admin site to django-admin2 or bootstrap3-django-admin
# TODO: add model translation using django-modeltranslation or django-rosetta
# TODO: optimize JS and CSS transfer with django-pipeline
# TODO: consider using django-feedback for adding a feedback feature where needed
# TODO: consider using django-analytical
# TODO: consider using django-blog-zinnia or puput for blog part
# TODO: consider adding a project dashboard using django-dashing
# TODO: consider using django-imagekit for managing avatar processing
# TODO: consider using django-autocomplete-light or django-searchable-select for select's
# TODO: consider using ? for Search field
# TODO: optimize security with django-security and django-sslify
# TODO: consider simplifying settings.py with django-environ or django-split-settings
# TODO: consider using django-taggit for tagging assets (e.g. APL tasks)
# TODO: consider integrating BPMN workflows sketching with django-viewflow (for the Automation System)
# TODO: consider using django-defender for protection against brute-force login attempts
# TODO: consider using django-badgify for managing user badges

# Login URL settings
LOGIN_URL = LOGOUT_URL = ADMIN_LOGOUT_URL = LOGIN_REDIRECT_URL = '/'

# Backends for using the customized user model and for automatically creating a superuser
AUTHENTICATION_BACKENDS = (
    'frontend.backends.GenericUserBackend',
    'frontend.backends.SuperUserCreationBackend',
)

MIDDLEWARE_CLASSES = (
#    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
    'simple_history.middleware.HistoryRequestMiddleware',
#    'django.middleware.cache.FetchFromCacheMiddleware',
#    'frontend.middleware.RemoteAddrMiddleware',
#    'frontend.middleware.FilterIPMiddleware',
    'frontend.middleware.StripWhitespaceMiddleware',
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
"""
Copy the static files to the public accessible folder using manage.py

# --link    Create a symbolic link to each file instead of copying.
# --noinput Do NOT prompt the user for input of any kind.
#
python manage.py collectstatic -link --noinput
"""
# web accessible folders
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'static/').replace('\\', '/'),
    # location of application, should not be public web accessible
)
# URL prefix for static files.
STATIC_ROOT = STATIC_URL = '/static/'
# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    #'compressor.parser.BeautifulSoupParser',
    #'compressor.parser.LxmlParser',
    #'compressor.parser.Html5LibParser',
    #'compressor.filters.jsmin.SlimItFilter',
    #'compressor.filters.cssmin.CSSCompressorFilter',
)

# URL prefix for media files (must be different from STATIC_URL).
MEDIA_URL = '/media/'
# TODO: Enable FTP for production version
# Web accessible folder (must be different from STATIC_ROOT)
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'media/').replace('\\', '/')
# DEFAULT_FILE_STORAGE = 'storages.backends.ftp.FTPStorage'
AVATARS_LOCATION = 'avatars/'    # for user profiles
PACKAGES_LOCATION = 'packages/'  # for APL packages
REPORTS_LOCATION = 'reports/'    # for APL generated reports

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
        'DIRS': [
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'templates').replace('\\', '/'),
        ],
        'OPTIONS': {
            'context_processors': [
                'frontend.context_processors.project_info',
                'frontend.context_processors.async_task_parameters',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.common.processors.tooltips',
            ],
            'builtins': [
                'overextends.templatetags.overextends_tags'
            ],
            'libraries': {
                'common_tags': 'apps.common.tags',
            },
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

# Set to False because of incompatibility with adminsortable (normally, no longer required with adminsortable2
# CSRF_COOKIE_HTTPONLY = False

# Specific SCAPL config
AUTH_USER_MODEL = 'profiles.ScaplUser'
DI_ID_DIGITS = 5
DL_ID_DIGITS = 3
DS_ID_DIGITS = 2
APL_ID_DIGITS = 3
MAX_RECENT_TASKS = 5

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
SMUGGLER_FIXTURE_DIR = './data/'
SMUGGLER_EXCLUDE_LIST = [
    'contenttypes.contenttype',
    'auth.permission',
    'admin.logentry',
    'sessions.session'
]

# Particular language settings
getText = lambda x: x
LANGUAGES = (
    ('en', getText('EN')),
    ('fr', getText('FR')),
    ('nl', getText('NL')),
)

# Admin bootstrapped configuration
DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info info',
    messages.SUCCESS: 'alert-success success',
    messages.WARNING: 'alert-warning warning',
    messages.ERROR: 'alert-danger danger',
    messages.INFO: 'alert-info info',
    100: 'alert-success success',
}

# In order to get the list of available themes, go to a Python shell and type:
#   from bootstrap_themes import list_themes
#   list_themes()
DEFAULT_BOOTSTRAP_THEME = 'default'

# Custom message storage to avoid duplicate messages
MESSAGE_STORAGE = 'apps.common.storage.CustomMessageStorage'
MESSAGES_TOAST_MAPPING = {
    messages.DEBUG: 'Notice',
    messages.SUCCESS: 'Success',
    messages.WARNING: 'Warning',
    messages.ERROR: 'Error',
    messages.INFO: 'Notice',
    100: 'Welcome',
}


# Summernote settings
def upload_attachment(self, fn):
    filename, extension = os.path.splitext(fn)
    return '{}/{}_{}{}'.format('uploads', str(self), slugify(filename), extension)

SUMMERNOTE_CONFIG = {
    'iframe': False,
    'airMode': False,
    'styleWithTags': True,
    'disableDragAndDrop': True,
    'direction': 'ltr',
    'width': '100%',
    'height': '300',
    'tabsize': 2,
    'lang': 'en-US',
    'lang_matches': {
        'en': 'en-US',
        'fr': 'fr-FR',
        'nl': 'nl-NL',
    },
    'toolbar': [
        ['action', ['undo', 'redo']],
        ['style', ['style']],
        ['font', ['bold', 'italic', 'underline', 'superscript', 'subscript', 'strikethrough', 'clear']],
        ['font', ['fontname', 'fontsize', 'color']],
        ['constants', ['constants']],
        ['para', ['ul', 'ol', 'paragraph', 'height']],
        ['insert', ['table', 'link', 'picture', 'hr']],
        ['highlight', ['highlight']],
        ['view', ['fullscreen', 'codeview']],
        ['help', ['help']]
    ],
    'attachment_require_authentication': False,
    'attachment_filesize_limit': 1024 * 1024,
    'attachment_storage_class': None,
    'attachment_upload_to': upload_attachment,
    'disable_upload': False,
    'prettifyHtml': False,
}
# Note: JS and CSS are manually imported in the relevant templates

# TODO: Enable JS and CSS compression for production version
# COMPRESS_ENABLED = True
# COMPRESS_OFFLINE = True
# COMPRESS_CSS_FILTERS = [
#     'compressor.filters.cleancss.CleanCSSFilter',
#     'compressor.filters.css_default.CssAbsoluteFilter',
#     'compressor.filters.cssmin.CSSCompressorFilter',
#     'compressor.filters.yui.YUICSSFilter',
# ]
# COMPRESS_JS_FILTERS = [
#     'compressor.filters.jsmin.JSMinFilter',
#     'compressor.filters.yui.YUIJSFilter',
# ]
# COMPRESS_YUI_BINARY = os.path.join(STATICFILES_DIRS[0], 'base', 'yuicompressor.jar').replace('\\', '/')
