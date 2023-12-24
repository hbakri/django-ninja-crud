SECRET_KEY = "SECRET_KEY_FOR_TESTING"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "tests.test_app",
    "examples",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "tests.test_urls"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "ninja_crud": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
