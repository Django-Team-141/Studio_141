from .base import *  # noqa: F401,F403

SECRET_KEY = env("SECRET_KEY")
DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])