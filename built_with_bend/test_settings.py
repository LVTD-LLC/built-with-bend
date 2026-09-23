from .settings import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
SECURE_SSL_REDIRECT = False
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
