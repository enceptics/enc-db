from pathlib import Path
import os
import datetime
from decouple import config, Csv
import dj_database_url

import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'logfile.log'),
            'formatter': 'default',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}

SITE_DOMAIN = "enceptics.com"
SITE_NAME = "Enceptics"

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-7tgcv33&!i&av(!mc1$zlwa#@db5jb!-ir0lb%*=3$63tkc8)s'
DEBUG = True
ALLOWED_HOSTS = ['enceptics.com', '127.0.0.1', '127.0.0.1:8000']

# Paypal settings
PAYPAL_SANDBOX_CLIENT_ID = config('PAYPAL_SANDBOX_CLIENT_ID')
PAYPAL_SANDBOX_CLIENT_SECRET = config('PAYPAL_SANDBOX_CLIENT_SECRET')

# PESAPAL

PESAPAL_ENV = os.getenv("PESAPAL_ENV", "live")  # Default to "live" if not set
PESAPAL_IPN_URL = os.getenv("PESAPAL_IPN_URL", "https://enceptics.com/pesapal/ipn/")
PESAPAL_CALLBACK_URL = os.getenv("PESAPAL_CALLBACK_URL", "https://enceptics.com/pesapal/response/")
PESAPAL_CONSUMER_KEY = os.getenv("PESAPAL_CONSUMER_KEY", "")
PESAPAL_CONSUMER_SECRET = os.getenv("PESAPAL_CONSUMER_SECRET", "")


import os

PESAPAL_ENV = os.getenv("PESAPAL_ENV", "live")  # Default to "live" if not set

# Default domain
DOMAIN = os.getenv("DOMAIN", "enceptics.com")

# Dynamically set Pesapal URLs
PESAPAL_IPN_URL = os.getenv("PESAPAL_IPN_URL", f"https://{DOMAIN}/pesapal/ipn/")
PESAPAL_CALLBACK_URL = os.getenv("PESAPAL_CALLBACK_URL", f"https://{DOMAIN}/booking/response/")

PESAPAL_CONSUMER_KEY = os.getenv("PESAPAL_CONSUMER_KEY", "")
PESAPAL_CONSUMER_SECRET = os.getenv("PESAPAL_CONSUMER_SECRET", "")


# Google OAuth settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('GOOGLE_OAUTH2_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('GOOGLE_OAUTH2_CLIENT_SECRET')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    "authentication.apps.AuthenticationConfig",
    'blog_posts.apps.BlogPostsConfig',
    'accounts.apps.AccountsConfig',
    'destinations.apps.DestinationsConfig',
    'weather.apps.WeatherConfig',
    'mpesa_payment.apps.MpesaPaymentConfig',
    "rest_framework",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    'rest_framework_swagger',
    'corsheaders',
    'django_daraja',
    'social_django',
]


CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'https://enceptics.com',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'https://enceptics.com',
]

CORS_ORIGIN_ALLOW_ALL = False

SWAGGER_SETTINGS = {
    'LOGIN_URL': 'rest_framework:login',
    'LOGOUT_URL': 'rest_framework:logout',
}

SIGNALS_MODULE = 'authentication.signals'
AUTH_TOKEN_MODEL = 'authentication..CustomToken'
AUTH_USER_MODEL = 'accounts.User'
ROOT_URLCONF = 'enceptics.urls'
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATE_INPUT_FORMATS = ['%m/%d/%y %H:%M:%S',]
USE_L10N = False

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'enceptics.vacay@gmail.com'
EMAIL_HOST_PASSWORD = 'wdhgxruwhpmvgcrl'
ACCOUNT_EMAIL_REQUIRED = True
EMAIL_CONFIRM_REDIRECT_BASE_URL = "https://enceptics.com/email/confirm/"
PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = "https://enceptics.com/password-reset/confirm/"

# Ensure email is  as the username for allauth
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"  # Optional, based on your requirement
ACCOUNT_USERNAME_REQUIRED = False  # Disable the username requirement
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'email'  # Tell allauth to use email as the unique identifier

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Session engine and other session-related settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'blog_post_session'
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False

GOOGLE_CLIENT_ID='143693841827-i3di9q4b0kc497cc9sj7q9ng9fcakhl1.apps.googleusercontent.com'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'enceptics.wsgi.application'

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'authentication.serializers.CustomRegisterSerializer',
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ]
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': dj_database_url.config(
        # Replace this value with your local database's connection string.
        default='postgresql://postgres:postgres@localhost:5432/enceptics',
        conn_max_age=600
    )
}

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_EMAIL_VERIFICATION = 'none'

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = os.path.join(BASE_DIR, 'static'),
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
