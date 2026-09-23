"""Directory-specific configuration, adapted from the hosted Djass scaffold."""

from pathlib import Path
from urllib.parse import urlsplit

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
if env.bool("DJANGO_READ_DOT_ENV", default=True):
    environ.Env.read_env(BASE_DIR / ".env")
ENVIRONMENT = env("ENVIRONMENT", default="dev")
DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY")
SITE_URL = env("SITE_URL", default="http://localhost:8000").rstrip("/")
ALLOWED_HOSTS = list(
    dict.fromkeys(
        [urlsplit(SITE_URL).hostname, "localhost", "127.0.0.1"]
        + env.list("EXTRA_ALLOWED_HOSTS", default=[])
    )
)
CSRF_TRUSTED_ORIGINS = [SITE_URL]
DEPLOYMENT_REVISION = env("DEPLOYMENT_REVISION", default="development")
# Enabled only when deployed behind CapRover's overwriting X-Real-IP proxy.
TRUST_CAPROVER_PROXY = env.bool("TRUST_CAPROVER_PROXY", default=False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if ENVIRONMENT == "prod" else None
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=ENVIRONMENT == "prod")
SESSION_COOKIE_SECURE = ENVIRONMENT == "prod"
CSRF_COOKIE_SECURE = ENVIRONMENT == "prod"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 8 * 60 * 60
SECURE_HSTS_SECONDS = 31536000 if ENVIRONMENT == "prod" else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
X_FRAME_OPTIONS = "DENY"
DATA_UPLOAD_MAX_MEMORY_SIZE = 65536
DATA_UPLOAD_MAX_NUMBER_FIELDS = 40
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "apps.directory",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "built_with_bend.urls"
WSGI_APPLICATION = "built_with_bend.wsgi.application"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "frontend/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
DATABASES["default"]["CONN_MAX_AGE"] = 60
if ENVIRONMENT == "prod" and DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ValueError("Production requires a PostgreSQL DATABASE_URL.")
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [BASE_DIR / "frontend/static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
