import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(path):
    if not path.exists():
        return

    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file(BASE_DIR / '.env')
load_env_file(BASE_DIR.parent / '.env')

SECRET_KEY = 'django-insecure-!ne2&5mi0k)=^%1jtlxq47#ctxf7f5ga^cusj0fzv1ys(#9pep'

DEBUG = True
HANDLER404 = 'cars.views.page_not_found'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cars',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'users.middleware.LoginRequiredSiteMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'autoworld.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

WSGI_APPLICATION = 'autoworld.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
DEFAULT_USER_IMAGE = MEDIA_URL + 'users/default.svg'

AUTHENTICATION_BACKENDS = [
    'users.backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'cars:index'
LOGOUT_REDIRECT_URL = 'users:login'

EMAIL_BACKEND = os.environ.get(
    'DJANGO_EMAIL_BACKEND',
    os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
)
EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST', os.environ.get('EMAIL_HOST', 'smtp.yandex.ru'))
EMAIL_PORT = int(os.environ.get('DJANGO_EMAIL_PORT', os.environ.get('EMAIL_PORT', '465')))
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_HOST_USER', os.environ.get('EMAIL_HOST_USER', ''))
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD', os.environ.get('EMAIL_HOST_PASSWORD', ''))
EMAIL_USE_TLS = os.environ.get('DJANGO_EMAIL_USE_TLS', os.environ.get('EMAIL_USE_TLS', '0')) == '1'
EMAIL_USE_SSL = os.environ.get('DJANGO_EMAIL_USE_SSL', os.environ.get('EMAIL_USE_SSL', '1')) == '1'

DEFAULT_FROM_EMAIL = os.environ.get('DJANGO_DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'webmaster@localhost')
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER
