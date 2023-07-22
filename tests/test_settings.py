SECRET_KEY = "SECRET_KEY_FOR_TESTING"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "tests.test_app",
    "example",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
ROOT_URLCONF = "tests.test_urls"

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
