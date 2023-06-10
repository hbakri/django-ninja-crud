SECRET_KEY = "SECRET_KEY_FOR_TESTING"
INSTALLED_APPS = ["django.contrib.contenttypes", "examples", "ninja_crud"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
ROOT_URLCONF = "examples.urls"
